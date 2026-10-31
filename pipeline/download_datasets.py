"""Download every dataset listed in CONTEXT.md section 6 into data/raw/ (git-ignored).

Run on the EC2 box:  cd ~/soymate-next && uv run python pipeline/download_datasets.py [name ...]
With no arguments it downloads everything. Re-running skips what is already complete.
Radio_lentille is gated on HuggingFace: export HF_TOKEN (after accepting the terms) to include it.
Writes data/raw/MANIFEST.json (file names, sizes, source URLs, licences) for the provenance table.
"""
import json
import os
import sys
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
UA = {"User-Agent": "Mozilla/5.0 (soymate dataset downloader)"}
MENDELEY = "https://data.mendeley.com/public-api/datasets"
MANIFEST: dict = {}


def fetch(url: str, dest: Path, expected_size: int | None = None) -> Path:
    """Stream url to dest; skip if dest already has the expected size."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and (expected_size is None or dest.stat().st_size == expected_size):
        return dest
    # Unique temp name: some Mendeley datasets list two files with the same path, fetched in parallel.
    tmp = dest.with_name(f"{dest.name}.{os.getpid()}.{threading.get_ident()}.part")
    with requests.get(url, headers=UA, stream=True, timeout=120, allow_redirects=True) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    os.replace(tmp, dest)
    return dest


def unzip(path: Path, to: Path) -> None:
    marker = to / ".unzipped"
    if marker.exists():
        return
    to.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as z:
        z.extractall(to)
    marker.touch()


def record(name: str, **info) -> None:
    MANIFEST[name] = info
    print(f"[done] {name}", flush=True)


def mendeley_zips(name: str, dataset: str, version: int, licence: str) -> None:
    files = requests.get(f"{MENDELEY}/{dataset}/files", params={"folder_id": "root", "version": version},
                         headers=UA, timeout=60).json()
    out = RAW / name
    for f in files:
        cd = f["content_details"]
        z = fetch(cd["download_url"], out / f["filename"], cd["size"])
        unzip(z, out / Path(f["filename"]).stem)
    record(name, source=f"https://data.mendeley.com/datasets/{dataset}/{version}", licence=licence,
           files=[{"name": f["filename"], "bytes": f["size"]} for f in files])


def mendeley_tree(name: str, dataset: str, version: int, licence: str, keep=lambda path: True,
                  note: str = "") -> None:
    """Loose files of a Mendeley dataset, saved under their real folder path; keep(path) filters them."""
    # The API only lists files for the latest version, so check it is still the one we expect.
    meta = requests.get(f"{MENDELEY}/{dataset}", headers=UA, timeout=60).json()
    if meta["version"] != version:
        raise RuntimeError(f"{dataset}: latest version is {meta['version']}, expected {version}")
    folders = {f["id"]: f for f in requests.get(f"{MENDELEY}/{dataset}/folders/{version}",
                                                headers=UA, timeout=60).json()}

    def folder_path(fid: str | None) -> Path:
        parts = []
        while fid in folders:
            parts.append(folders[fid]["name"])
            fid = folders[fid].get("parent_id")
        return Path(*reversed(parts))

    out = RAW / name
    jobs = []
    for f in meta["files"]:
        rel = folder_path(f.get("folder_id")) / f["filename"]
        if keep(rel.as_posix()):
            jobs.append((f["content_details"]["download_url"], out / rel, f["size"]))
    with ThreadPoolExecutor(16) as ex:
        list(ex.map(lambda j: fetch(*j), jobs))
    record(name, source=f"https://data.mendeley.com/datasets/{dataset}/{version}", licence=licence,
           n_files=len(jobs), bytes=sum(j[2] for j in jobs), **({"note": note} if note else {}))


def mendeley_seeds_5classes() -> None:
    """Soybean Seeds (v6vzvfszj6 v6): ~5,500 single-seed JPEGs in class folders, plus 5 multi-seed originals."""
    mendeley_tree("soybean_seeds_5classes", "v6vzvfszj6", 6, "CC BY 4.0",
                  note="Class folders: Intact, Spotted, Immature, Broken, Skin-damaged soybeans. "
                       "'Part of the original soybean images' = 5 multi-seed photos (segmentation test).")


def ghana_soybean() -> None:
    """Ghana seed varieties (t94nzy4ptz v2): only the soybean part, without the 14k single-seed crops.

    Keeps the 105 group phone photos (~150 seeds each) and the per-photo _crop_metadata.csv (one box per seed).
    Labels are variety only: use for segmentation/count and as a sound-seed false-positive test.
    """
    mendeley_tree("ghana_soybean", "t94nzy4ptz", 2, "CC BY 4.0",
                  keep=lambda p: p.startswith("seed_data/Soyabean/")
                  and ("/group_capture/" in p or p.endswith("_crop_metadata.csv")),
                  note="Varieties Afayak, FarmerSaved, Favor, Jenguma. FarmerSaved may contain unlabelled defects.")


def harvest_soybean() -> None:
    """Mechanical-harvest soybean (hwdtghttp7 v2): 800 images + VOC masks (intact, crushed, impurity).

    Skips the 336 MB VOC2007.rar, which duplicates the loose files. Only 40 originals, each augmented
    20 times: split by the 4-digit id prefix, never with the shipped train/val/test lists.
    """
    mendeley_tree("harvest_soybean", "hwdtghttp7", 2, "CC BY 4.0", keep=lambda p: not p.endswith(".rar"),
                  note="Split by the 4-digit id prefix (40 originals x 20 augmentations); shipped splits leak.")


def indonesia_soybean() -> None:
    """Indonesian soybean varieties (c733bjz4m3 v3): the 3 'Scanned_*' zips (multi-seed flatbed scans, ~294 MB).

    The 'Segmented_*' zips (~680 MB of single-seed crops) are skipped; add them only if a sound-class
    test from this setup is needed.
    """
    files = requests.get(f"{MENDELEY}/c733bjz4m3/files", params={"folder_id": "root", "version": 3},
                         headers=UA, timeout=60).json()
    out = RAW / "indonesia_soybean"
    kept = [f for f in files if f["filename"].startswith("Scanned_")]
    for f in kept:
        cd = f["content_details"]
        z = fetch(cd["download_url"], out / f["filename"], cd["size"])
        unzip(z, out / Path(f["filename"]).stem)
    record("indonesia_soybean", source="https://data.mendeley.com/datasets/c733bjz4m3/3", licence="CC BY 4.0",
           files=[{"name": f["filename"], "bytes": f["size"]} for f in kept],
           note="Variety labels only (Anjasmoro, Dega I, Grobogan). Segmented_* zips not downloaded.")


def figshare(name: str, article: int, licence: str) -> None:
    meta = requests.get(f"https://api.figshare.com/v2/articles/{article}", headers=UA, timeout=60).json()
    out = RAW / name
    for f in meta["files"]:
        z = fetch(f["download_url"], out / f["name"], f["size"])
        unzip(z, out / Path(f["name"]).stem)
    record(name, source=f"https://figshare.com/articles/{article}", licence=licence,
           files=[{"name": f["name"], "bytes": f["size"], "md5": f.get("computed_md5")} for f in meta["files"]])


def zenodo(name: str, record_id: int, licence: str) -> None:
    meta = requests.get(f"https://zenodo.org/api/records/{record_id}", headers=UA, timeout=60).json()
    out = RAW / name
    jobs = [(f["links"]["self"], out / f["key"], f["size"]) for f in meta["files"]]
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(lambda j: fetch(*j), jobs))
    for _, p, _ in jobs:
        if p.suffix == ".zip":
            unzip(p, out / p.stem)
    record(name, source=f"https://zenodo.org/records/{record_id}", licence=licence, n_files=len(jobs))


def hf_dataset(name: str, repo_id: str, licence: str) -> None:
    from huggingface_hub import snapshot_download
    snapshot_download(repo_id=repo_id, repo_type="dataset", local_dir=RAW / name,
                      token=os.environ.get("HF_TOKEN"), max_workers=16)
    record(name, source=f"https://huggingface.co/datasets/{repo_id}", licence=licence)


STEPS = {
    "soybean_v1": lambda: mendeley_zips("soybean_v1", "d97rjyk2tz", 1, "CC BY 4.0"),
    "soybean_v2": lambda: mendeley_zips("soybean_v2", "d97rjyk2tz", 2, "CC BY 4.0"),
    "soybean_seeds_5classes": mendeley_seeds_5classes,
    "ghana_soybean": ghana_soybean,
    "harvest_soybean": harvest_soybean,
    "indonesia_soybean": indonesia_soybean,
    "grainset_tiny": lambda: figshare("grainset_tiny", 22989029, "CC BY 4.0"),
    "pea_zenodo": lambda: zenodo("pea_zenodo", 21110940, "CC BY 4.0"),
    "faba_zenodo": lambda: zenodo("faba_zenodo", 18226381, "CC BY 4.0"),
    "corn1000": lambda: hf_dataset("corn1000", "SmartFarmingLab/corn1000", "CC BY-NC 4.0"),
    "grainset_raw": lambda: figshare("grainset_raw", 24137472, "CC BY 4.0"),
}
if os.environ.get("HF_TOKEN"):
    STEPS["radio_lentille"] = lambda: hf_dataset("radio_lentille", "JeanEudesH/Radio_lentille", "MIT")


def main() -> None:
    wanted = sys.argv[1:] or list(STEPS)
    RAW.mkdir(parents=True, exist_ok=True)
    mf = RAW / "MANIFEST.json"
    if mf.exists():
        MANIFEST.update(json.loads(mf.read_text()))
    for name in wanted:
        try:
            STEPS[name]()
        except Exception as e:  # keep going: one broken source must not block the others
            print(f"[FAILED] {name}: {e!r}", flush=True)
            MANIFEST.setdefault(name, {})["error"] = repr(e)
        mf.write_text(json.dumps(MANIFEST, indent=2))
    if "radio_lentille" not in STEPS:
        print("[skipped] radio_lentille: gated on HuggingFace, set HF_TOKEN after accepting the terms", flush=True)


if __name__ == "__main__":
    main()
