"""Leak-free grouped splits for the soybean datasets, regenerated at the event.

Run on the box:  cd ~/soymate && uv run python scripts/data/make_splits.py [soybean lin harvest ghana]
Reads data/raw/, writes data/splits/<dataset>.csv and data/splits/SUMMARY.json.

Rules (see research/critique.md C1/M6 and research/soybean_bruchid/findings.md):
- soybean (Mendeley d97rjyk2tz): v2 images are matched to v1 by md5; the group is the original photo
  (IMG_YYYYMMDD_HHMMSS prefix of the v1 Roboflow name). Exact duplicates (same md5, keep one) and images
  without labels are dropped. Groups are split 70/15/15, stratified by image type and background.
  The published v2 split is kept as `published_split` for the leaky arm of R1.
- lin (Mendeley v6vzvfszj6): groups are near-duplicate clusters (16x16 dHash under the 8 flips/rotations,
  Hamming <= LIN_DHASH_MAX of 256 bits), split 70/15/15 stratified by class.
- harvest (Mendeley hwdtghttp7): group = 4-digit id prefix (40 originals x 20 augmentations).
- ghana (Mendeley t94nzy4ptz): evaluation only, every photo is its own group in `test`.

This regenerates research/soybean_bruchid/resplit_by_original.csv (a declared pre-event resource) from
the raw files; that CSV is only read at the end, to report agreement.
"""
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "splits"
SEED = 42
FRACTIONS = {"train": 0.70, "val": 0.15, "test": 0.15}
LIN_DHASH_MAX = 10  # of 256 bits; nearest-neighbour distances show a near-duplicate tail at 1-10, then a continuum
SOY_CLASSES = {0: "Egg", 1: "Hole", 2: "Testa cracking", 3: "Normal_Damage", 4: "Healthy"}
SUMMARY: dict = {}


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def group_split(groups: pd.DataFrame, strata_col: str, seed: int = SEED) -> dict:
    """Assign each group to train/val/test, 70/15/15 within each stratum. groups: one row per group."""
    rng = np.random.default_rng(seed)
    assign = {}
    for _, g in groups.groupby(strata_col, sort=True):
        ids = g.index.to_numpy().copy()
        rng.shuffle(ids)
        n = len(ids)
        n_val = int(round(n * FRACTIONS["val"]))
        n_test = int(round(n * FRACTIONS["test"]))
        for i, gid in enumerate(ids):
            assign[gid] = "test" if i < n_test else "val" if i < n_test + n_val else "train"
    return assign


def border_background(img: np.ndarray) -> str:
    """Brightness of a 5 % border, the same cue as the pre-event audit (black vs light background)."""
    h, w = img.shape[:2]
    b = max(1, int(0.05 * min(h, w)))
    border = np.concatenate([img[:b].ravel(), img[-b:].ravel(), img[:, :b].ravel(), img[:, -b:].ravel()])
    m = float(border.mean())
    return "black" if m < 60 else "white/light" if m > 120 else "intermediate"


def check_no_leak(df: pd.DataFrame, name: str) -> None:
    kept = df[df["split"].notna()]
    per_group = kept.groupby("group")["split"].nunique()
    assert (per_group == 1).all(), f"{name}: {int((per_group > 1).sum())} groups in more than one split"
    if "md5" in kept:
        per_md5 = kept.groupby("md5")["split"].nunique()
        assert (per_md5 == 1).all(), f"{name}: identical files in more than one split"


def summarise(df: pd.DataFrame, name: str, label_col: str) -> None:
    kept = df[df["split"].notna()]
    SUMMARY[name] = {
        "rows": len(df), "kept": len(kept), "dropped": df["drop_reason"].value_counts().to_dict(),
        "images_per_split": kept["split"].value_counts().to_dict(),
        "groups_per_split": kept.groupby("split")["group"].nunique().to_dict(),
        "labels_per_split": {s: Counter(x for v in g[label_col] for x in str(v).split("|") if x)
                             for s, g in kept.groupby("split")},
    }
    print(json.dumps({name: SUMMARY[name]}, indent=1, default=int), flush=True)


# --------------------------------------------------------------------------- soybean (d97rjyk2tz)
def soybean() -> None:
    v1_root, v2_root = RAW / "soybean_v1", RAW / "soybean_v2" / "Soybean_Seed_Dataset" / "Soybean_Seed_Dataset"
    v1_by_md5 = defaultdict(list)
    for p in sorted(v1_root.glob("*/*/images/*/*.jpg")) + sorted(v1_root.glob("*/*/images/*.jpg")):
        v1_by_md5[md5(p)].append(p.name)
    rows = []
    for split_dir in ("train", "validation", "test"):
        for img in sorted((v2_root / split_dir / "images").glob("*.jpg")):
            lab = v2_root / split_dir / "labels" / (img.stem + ".txt")
            cls = [int(line.split()[0]) for line in lab.read_text().splitlines() if line.strip()] if lab.exists() else []
            h = md5(img)
            v1_names = sorted(set(v1_by_md5.get(h, [])))
            m = re.match(r"(IMG_\d{8}_\d{6})", v1_names[0]) if v1_names else None
            names = {SOY_CLASSES[c] for c in cls}
            typ = ("unlabeled" if not cls else "bruchid-damaged" if names & {"Egg", "Hole"}
                   else "Testa/Normal" if names & {"Testa cracking", "Normal_Damage"} else "Healthy only")
            rows.append({
                "image": f"{split_dir}/images/{img.name}", "published_split": {"validation": "val"}.get(split_dir, split_dir),
                "md5": h, "v1_name": v1_names[0] if v1_names else "",
                "group": m.group(1) if m else f"v2only_{img.stem}",
                "labels": "|".join(sorted(names)), "n_boxes": len(cls), "type": typ,
                "background": border_background(np.asarray(Image.open(img).convert("L"))),
                "capture_date": m.group(1)[4:12] if m else "",
            })
    df = pd.DataFrame(rows)
    df["drop_reason"] = ""
    df.loc[df.duplicated("md5", keep="first"), "drop_reason"] = "exact duplicate (md5)"
    df.loc[(df["n_boxes"] == 0) & (df["drop_reason"] == ""), "drop_reason"] = "unlabeled"
    kept = df[df["drop_reason"] == ""]
    # Group stratum: most severe type in the group, plus its majority background.
    order = {"bruchid-damaged": 0, "Testa/Normal": 1, "Healthy only": 2}
    g = kept.groupby("group").agg(type=("type", lambda s: min(s, key=order.get)),
                                  background=("background", lambda s: s.mode().iloc[0]))
    g["stratum"] = g["type"] + "/" + g["background"]
    assign = group_split(g, "stratum")
    df["split"] = df["group"].map(assign).where(df["drop_reason"] == "")
    # One image per group for val/test reporting (first by name), so augmented variants count once.
    first = df[df["split"].notna()].sort_values("image").drop_duplicates("group").index
    df["eval_rep"] = df.index.isin(first)
    check_no_leak(df, "soybean")
    published_leak = {}
    pub_train_groups = set(df.loc[df["published_split"] == "train", "group"])
    for s in ("val", "test"):
        sub = df[df["published_split"] == s]
        published_leak[s] = {"images": len(sub), "group_also_in_published_train": int(sub["group"].isin(pub_train_groups).sum())}
    df.to_csv(OUT / "soybean.csv", index=False)
    summarise(df, "soybean", "labels")
    SUMMARY["soybean"]["n_v2_without_v1_match"] = int((df["v1_name"] == "").sum())
    SUMMARY["soybean"]["published_split_leakage"] = published_leak
    SUMMARY["soybean"]["agreement_with_pre_event_csv"] = compare_pre_event(df)


def compare_pre_event(df: pd.DataFrame) -> dict:
    """Compare with the declared pre-event resplit: same groups and same drops? (split labels differ by design)."""
    pre_path = ROOT / "research" / "soybean_bruchid" / "resplit_by_original.csv"
    if not pre_path.exists():
        return {"available": False}
    pre = pd.read_csv(pre_path)
    cur = df.assign(image_v2=df["image"].str.split("/").str[-1]).set_index("image_v2")
    pre = pre.set_index("image_v2").reindex(cur.index)
    same_group = (pre["group"].fillna("") == cur["group"].where(~cur["group"].str.startswith("v2only_"), "")).mean()
    same_drop = (pre["discard"].notna() == (cur["drop_reason"] != "")).mean()
    return {"available": True, "same_group_frac": round(float(same_group), 4), "same_drop_frac": round(float(same_drop), 4),
            "n_groups_now": int(cur.loc[cur["drop_reason"] == "", "group"].nunique()),
            "n_groups_pre": int(pre.loc[pre["discard"].isna(), "group"].nunique())}


# --------------------------------------------------------------------------- Lin (v6vzvfszj6)
def dhash_variants(path: Path) -> np.ndarray:
    """256-bit difference hash of the 8 dihedral variants, so flips and 90-degree rotations still match."""
    im = Image.open(path).convert("L").resize((17, 17), Image.Resampling.LANCZOS)
    a = np.asarray(im, dtype=np.int16)
    out = []
    for k in range(4):
        r = np.rot90(a, k)
        for v in (r, r[:, ::-1]):
            bits = (v[:16, 1:] > v[:16, :-1]).ravel()
            out.append(np.packbits(bits))
    return np.stack(out)  # (8 variants, 32 bytes) uint8


def lin() -> None:
    root = RAW / "soybean_seeds_5classes"
    files = sorted(p for p in root.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
                   and "original" not in p.parent.name.lower())
    cls = [p.parent.name.replace(" soybeans", "").lower() for p in files]
    hashes = np.stack([dhash_variants(p) for p in files])  # (n, 8, 8)
    md5s = [md5(p) for p in files]
    n = len(files)
    base = np.unpackbits(hashes[:, 0, :], axis=1).astype(np.uint8)  # (n, 256)
    allv = np.unpackbits(hashes, axis=2).astype(np.uint8)           # (n, 8, 256)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(n):  # min Hamming over the 8 variants of j against the base hash of i
        d = (allv[i + 1:] != base[i][None, None, :]).sum(axis=2).min(axis=1)
        for j in np.nonzero(d <= LIN_DHASH_MAX)[0] + i + 1:
            parent[find(int(j))] = find(i)
    roots = [find(i) for i in range(n)]
    df = pd.DataFrame({"image": [p.relative_to(root).as_posix() for p in files], "md5": md5s, "label": cls,
                       "group": [f"lin_{r:05d}" for r in roots]})
    df["drop_reason"] = ""
    df.loc[df.duplicated("md5", keep="first"), "drop_reason"] = "exact duplicate (md5)"
    conflict = df[df["drop_reason"] == ""].groupby("group")["label"].nunique()
    df.loc[df["group"].isin(conflict[conflict > 1].index) & (df["drop_reason"] == ""), "drop_reason"] = "label conflict in near-duplicate group"
    kept = df[df["drop_reason"] == ""]
    g = kept.groupby("group").agg(stratum=("label", "first"))
    df["split"] = df["group"].map(group_split(g, "stratum")).where(df["drop_reason"] == "")
    check_no_leak(df, "lin")
    df.to_csv(OUT / "lin.csv", index=False)
    summarise(df, "lin", "label")
    sizes = df.groupby("group").size()
    SUMMARY["lin"]["near_duplicate_groups_size_gt1"] = int((sizes > 1).sum())
    SUMMARY["lin"]["dhash_max_hamming"] = LIN_DHASH_MAX


# --------------------------------------------------------------------------- harvest (hwdtghttp7)
def harvest() -> None:
    root = RAW / "harvest_soybean"
    imgs = sorted(p for p in root.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg"} and "JPEGImages" in p.parts)
    masks = {p.stem: p for p in root.rglob("*.png") if "SegmentationClass" in p.parts}
    rows = []
    for p in imgs:
        m = re.match(r"(\d{4})", p.stem)
        rows.append({"image": p.relative_to(root).as_posix(), "md5": md5(p),
                     "mask": masks[p.stem].relative_to(root).as_posix() if p.stem in masks else "",
                     "group": m.group(1) if m else p.stem})
    df = pd.DataFrame(rows)
    df["drop_reason"] = ""
    df.loc[df["mask"] == "", "drop_reason"] = "no mask"
    df.loc[df.duplicated("md5", keep="first") & (df["drop_reason"] == ""), "drop_reason"] = "exact duplicate (md5)"
    g = df[df["drop_reason"] == ""].groupby("group").agg(stratum=("image", lambda s: "all"))
    df["split"] = df["group"].map(group_split(g, "stratum")).where(df["drop_reason"] == "")
    df["label"] = "multi-seed mask"
    check_no_leak(df, "harvest")
    df.to_csv(OUT / "harvest.csv", index=False)
    summarise(df, "harvest", "label")
    SUMMARY["harvest"]["n_groups"] = int(df["group"].nunique())


# --------------------------------------------------------------------------- Ghana (t94nzy4ptz)
def ghana() -> None:
    root = RAW / "ghana_soybean"
    imgs = sorted(p for p in root.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"} and "group_capture" in p.parts)
    df = pd.DataFrame({"image": [p.relative_to(root).as_posix() for p in imgs], "md5": [md5(p) for p in imgs]})
    df["label"] = [next((part for part in p.parts if part in {"Afayak", "FarmerSaved", "Favor", "Jenguma"}), "") or p.parent.parent.name
                   for p in imgs]
    df["group"] = [p.stem for p in imgs]
    df["drop_reason"] = ""
    df.loc[df.duplicated("md5", keep="first"), "drop_reason"] = "exact duplicate (md5)"
    df["split"] = np.where(df["drop_reason"] == "", "test", None)
    check_no_leak(df, "ghana")
    df.to_csv(OUT / "ghana.csv", index=False)
    summarise(df, "ghana", "label")


STEPS = {"soybean": soybean, "lin": lin, "harvest": harvest, "ghana": ghana}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    sp = OUT / "SUMMARY.json"
    if sp.exists():
        SUMMARY.update(json.loads(sp.read_text()))
    for name in sys.argv[1:] or list(STEPS):
        STEPS[name]()
        sp.write_text(json.dumps(SUMMARY, indent=2, default=int))
