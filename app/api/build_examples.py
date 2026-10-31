"""Copy the demo example images into app/api/examples/ and write examples.json.

Run on the box:  cd ~/soymate && uv run python app/api/build_examples.py
Only evaluation-only (Ghana) or test-split images (d97rjyk2tz, Lin), picked by rule, never by prediction.
Originals are copied byte for byte, never re-encoded (files over BIG_MB are kept and get a size note).
"""
import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "examples"
RAW = ROOT / "data" / "raw"
SOY_V2 = RAW / "soybean_v2" / "Soybean_Seed_Dataset" / "Soybean_Seed_Dataset"
LIN = RAW / "soybean_seeds_5classes"
GHANA = RAW / "ghana_soybean"
BIG_MB = 6
CREDIT = {"ghana": "Ghana soybean seeds t94nzy4ptz, Mendeley Data (CC BY 4.0)",
          "soy": "Soybean seed defects d97rjyk2tz v2, Mendeley Data (CC BY 4.0)",
          "lin": "Soybean seeds 5 classes (Lin) v6vzvfszj6, Mendeley Data (CC BY 4.0)"}


def save(src: Path, name: str) -> tuple[str, float]:
    """Copy the original file byte for byte (re-encoding moves class shares, see results/demo_smoke.json)."""
    dst = OUT / f"{name}{src.suffix.lower()}"
    shutil.copyfile(src, dst)
    mb = dst.stat().st_size / 2**20
    if mb > BIG_MB:
        print(f"note: {dst.name} is {mb:.1f} MB", flush=True)
    return f"/api/examples/files/{dst.name}", mb


def ghana() -> list[dict]:
    p = pd.read_csv(ROOT / "results" / "r4_ghana_counts__photos.csv")
    p["stem"] = p["photo"].map(lambda s: Path(s).stem)
    g17 = p[p["stem"] == "PXL_20260315_135711992"].iloc[0]
    favor = p[(p["variety"] == "Favor") & (p["gt_status"] == "ok") & (p["err_vs_boxes"] == 0)].iloc[0]
    afa = p[(p["variety"] == "Afayak") & (p["err_vs_est"].abs() <= 3)]
    afa = afa.sort_values("n_components_shadow", ascending=False).iloc[0]
    out = []
    for eid, r, label in [("ghana_g17", g17, f"Ghana farmer-saved lot ({g17['n_boxes']} seeds)"),
                          ("ghana_favor", favor, f"Ghana Favor lot ({favor['n_boxes']} seeds)"),
                          ("ghana_afayak_shadow", afa, "Ghana Afayak lot in hard shadow")]:
        ok = r["gt_status"] == "ok"
        note = ("Evaluation-only phone photo; complete published count available." if ok else
                f"Evaluation-only phone photo with hard shadow; the published boxes miss seeds in shadow "
                f"(semi-automatic estimate about {r['n_seeds_est']} seeds, not ground truth).")
        url, mb = save(GHANA / r["photo"], eid)
        if mb > BIG_MB:
            note += f" Original file, {mb:.1f} MB."
        out.append({"id": eid, "label": label, "kind": "batch", "dataset": CREDIT["ghana"],
                    "url": url, "note": note,
                    "ground_truth": {"n_seeds": int(r["n_boxes"])} if ok else None,
                    "source": r["photo"]})
    return out


def singles() -> list[dict]:
    m = pd.read_csv(ROOT / "data" / "crops" / "manifest.csv", keep_default_na=False)
    m = m[(m["split"] == "test") & (m["eval_rep"].astype(str) == "True") & (m["multi_seed"].astype(str) != "True")].sort_values("source_image")
    soy = m[(m["dataset"] == "soybean_d97rjyk2tz") & (m["background"] == "white/light") & (m["seg_note"] == "")
            & (pd.to_numeric(m["mask_frac"], errors="coerce") >= 0.2)]
    lin = m[m["dataset"] == "lin_v6vzvfszj6"]
    out = []
    for c in ("sound", "broken", "insect_hole"):
        r = soy[soy["class"] == c].iloc[0]
        eid = f"soy_{c}"
        out.append({"id": eid, "label": f"Single soybean seed, labelled {c.replace('_', ' ')}", "kind": "single",
                    "dataset": CREDIT["soy"], "url": save(SOY_V2 / r["source_image"], eid)[0],
                    "note": f"Test-split image (dataset label: {r['source_label']}).",
                    "ground_truth": {"class": c, "n_seeds": 1}, "source": r["source_image"]})
    for c in ("stained", "immature"):
        r = lin[lin["class"] == c].iloc[0]
        eid = f"lin_{c}"
        out.append({"id": eid, "label": f"Single soybean seed (Lin), labelled {c}", "kind": "single",
                    "dataset": CREDIT["lin"], "url": save(LIN / r["source_image"], eid)[0],
                    "note": f"Test-split crop (dataset label: {r['source_label']}).",
                    "ground_truth": {"class": c, "n_seeds": 1}, "source": r["source_image"]})
    return out


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*"):
        f.unlink()
    ex = ghana() + singles()
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1, default=int))
    print(json.dumps([{k: e[k] for k in ("id", "url", "source")} for e in ex], indent=1))
