"""Seed-level index of the Mechanical-harvest soybean masks (Mendeley hwdtghttp7 v2, CC BY 4.0).

Run on the box:  cd ~/soymate && uv run python scripts/data/harvest_index.py
Reads data/raw/harvest_soybean/.../VOC2007/{JPEGImages,SegmentationClass} and data/splits/harvest.csv,
writes data/splits/harvest_seeds.csv (one row per instance) and data/splits/harvest_images.csv (one row per image).

Rules:
- Palette (VOC2007/ImageSets/Segmentation/class.txt, confirmed on overlays): (0,0,0) background,
  (128,0,0) crushed, (0,128,0) intact, (128,128,0) impurity. Resampled augmentations (scale, rotate) carry
  interpolated near-colours: every pixel is snapped to the nearest palette colour (RGB L2).
- Instances: 4-connected components per class, specks below MIN_AREA_FRAC of the median intact seed dropped.
  A crushed/intact component is merged_suspect when area > AREA_MERGE x median intact seed AND solidity < SOLIDITY_MIN
  (a neck between seeds); suspect components are split by distance-transform watershed (one marker per distance
  peak) and every piece keeps the flag. Low solidity alone is mostly occluded seeds, and big impurity (pods, stems)
  is genuinely large, so neither is flagged or split.
- Augmentation index (file NNNNAA.jpg, AA = 01..20): 01 original, 02-05 scale, 06-09 rotate, 10-12 flip,
  13-16 filter, 17-20 noise (measured, see is_original). The original is the native-size, exact-palette image whose
  mask is unflipped and whose pixels a flipped sibling reproduces (lowest mean abs difference).
- % crushed = crushed / (crushed + intact), by instance count and by pixel area; impurity is excluded.
- Split: read from harvest.csv (make_splits.py) at run time and joined on group; if absent, recomputed in memory
  with make_splits.group_split.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.measure import regionprops
from skimage.segmentation import watershed

ROOT = Path(__file__).resolve().parents[2]
VOC = ROOT / "data" / "raw" / "harvest_soybean" / "Mechanical-harvest Soybean Images Dataset" / "VOC2007"
OUT = ROOT / "data" / "splits"
PALETTE = np.array([[0, 0, 0], [128, 0, 0], [0, 128, 0], [128, 128, 0]])
CLASSES = {1: "crushed", 2: "intact", 3: "impurity"}
NATIVE = (1024, 1280)  # H, W
MIN_AREA_FRAC = 0.05   # of the median intact seed area
SOLIDITY_MIN = 0.90
AREA_MERGE = 1.8
PEAK_MIN_DIST_FRAC = 0.5  # of the median intact seed radius
FLIPS = {"lr": lambda a: a[:, ::-1], "ud": lambda a: a[::-1], "r180": lambda a: a[::-1, ::-1]}


def load_split() -> pd.DataFrame:
    p = OUT / "harvest.csv"
    stems = sorted(q.stem for q in (VOC / "JPEGImages").glob("*.jpg"))
    df = pd.DataFrame({"stem": stems, "group": [s[:4] for s in stems]}).set_index("stem")
    if p.exists():  # read at run time, joined on group, so a regenerated harvest.csv is always picked up
        h = pd.read_csv(p, dtype={"group": str}).dropna(subset=["split"])
        by_group = h.groupby("group")["split"].agg(lambda s: s.iloc[0] if s.nunique() == 1 else "LEAK")
        assert (by_group != "LEAK").all(), "harvest.csv puts one group in several splits"
        df["split"] = df["group"].map(by_group)
        print(f"split from {p.relative_to(ROOT)}: {by_group.value_counts().to_dict()} groups")
        return df
    sys.path.insert(0, str(ROOT / "scripts" / "data"))
    from make_splits import group_split  # same rule and seed as make_splits.harvest()
    g = df.groupby("group").agg(stratum=("group", lambda s: "all"))
    df["split"] = df["group"].map(group_split(g, "stratum"))
    print("harvest.csv absent: split recomputed in memory with make_splits.group_split")
    return df


def snap(mask_rgb: np.ndarray) -> tuple[np.ndarray, float]:
    """Nearest-palette label map and the fraction of pixels that were off-palette."""
    m = mask_rgb.astype(np.int32)
    d = ((m[..., None, :] - PALETTE[None, None]) ** 2).sum(-1)
    lab = d.argmin(-1).astype(np.uint8)
    return lab, float((d.min(-1) > 0).mean())


def instances(lab: np.ndarray) -> list[dict]:
    """Per-class components, watershed-split when they look merged."""
    cc = {c: ndi.label(lab == c) for c in CLASSES}  # 4-connectivity (default structure)
    a_int = np.bincount(cc[2][0].ravel())[1:]
    ref = float(np.median(a_int[a_int > 0.2 * a_int.max()])) if a_int.size else 5000.0  # typical single seed
    r_ref = np.sqrt(ref / np.pi)
    rows = []
    for c, (L, n) in cc.items():
        for rp in regionprops(L):
            if rp.area < MIN_AREA_FRAC * ref:
                continue
            suspect = c != 3 and rp.solidity < SOLIDITY_MIN and rp.area > AREA_MERGE * ref
            pieces = [(rp.image, rp.bbox)]
            if suspect:
                sub = np.pad(rp.image, 1)
                dist = ndi.distance_transform_edt(sub)
                pk = peak_local_max(dist, min_distance=max(3, int(PEAK_MIN_DIST_FRAC * r_ref)),
                                    threshold_abs=0.3 * r_ref, labels=sub.astype(int), exclude_border=False)
                if len(pk) > 1:
                    mk = np.zeros_like(sub, dtype=np.int32)
                    mk[tuple(pk.T)] = np.arange(1, len(pk) + 1)
                    ws = watershed(-dist, mk, mask=sub)[1:-1, 1:-1]
                    y0, x0 = rp.bbox[:2]
                    pieces = []
                    for q in regionprops(ws):
                        by0, bx0, by1, bx1 = q.bbox
                        pieces.append((q.image, (y0 + by0, x0 + bx0, y0 + by1, x0 + bx1)))
            for img, (y0, x0, y1, x1) in pieces:
                ys, xs = np.nonzero(img)
                rows.append({"class": CLASSES[c], "area_px": int(img.sum()), "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                             "cx": round(float(xs.mean() + x0), 1), "cy": round(float(ys.mean() + y0), 1),
                             "merged_suspect": bool(suspect), "n_pieces": len(pieces), "component": f"{c}-{rp.label}"})
    return rows


def find_originals(meta: pd.DataFrame, cache: dict) -> dict:
    """group -> stem of the original, using native size, exact palette, unflipped mask and a lossless flip twin."""
    best = {}
    for grp, g in meta.groupby("group"):
        cand = g[(g["h"] == NATIVE[0]) & (g["w"] == NATIVE[1]) & (g["off_palette_frac"] == 0)].index.tolist()
        flipped = {s for s in cand for t in cand if s != t and any(np.array_equal(f(cache[s][0]), cache[t][0])
                   for f in FLIPS.values()) and not np.array_equal(cache[s][0], cache[t][0])}
        ids = [s for s in cand if s not in flipped] or cand
        others = [t for t in cand if t in flipped]
        score = {s: min((np.abs(f(cache[t][1]) - cache[s][1]).mean() for t in others for f in FLIPS.values()
                         if np.array_equal(f(cache[t][0]), cache[s][0])), default=np.inf) for s in ids}
        best[grp] = min(score, key=score.get)
    return best


def main() -> None:
    split = load_split()
    seeds, meta, cache = [], [], {}
    for p in sorted((VOC / "JPEGImages").glob("*.jpg")):
        s = p.stem
        rgb = np.array(Image.open(VOC / "SegmentationClass" / f"{s}.png").convert("RGB"))
        lab, off = snap(rgb)
        rows = instances(lab)
        for r in rows:
            r.update(image=f"JPEGImages/{p.name}", group=split.at[s, "group"], split=split.at[s, "split"])
        seeds += rows
        areas = np.bincount(lab.ravel(), minlength=4) / lab.size * 100
        meta.append({"stem": s, "image": f"JPEGImages/{p.name}", "group": s[:4], "aug": int(s[4:6]),
                     "split": split.at[s, "split"], "h": lab.shape[0], "w": lab.shape[1],
                     "off_palette_frac": round(off, 5),
                     **{f"pct_area_{n}": round(float(areas[c]), 3) for c, n in CLASSES.items()}})
        if lab.shape == NATIVE and off == 0:
            cache[s] = (lab, np.asarray(Image.open(p).convert("L"), dtype=np.float32))
        print(f"{s}: {len(rows)} instances", flush=True) if s.endswith("01") else None
    sd = pd.DataFrame(seeds)
    im = pd.DataFrame(meta).set_index("stem")
    orig = find_originals(im, cache)
    im["is_original"] = im.index.isin(orig.values())
    cnt = sd.groupby(["image", "class"]).size().unstack(fill_value=0).reindex(columns=list(CLASSES.values()), fill_value=0)
    area = sd.groupby(["image", "class"])["area_px"].sum().unstack(fill_value=0).reindex(columns=list(CLASSES.values()), fill_value=0)
    im = im.join(cnt.add_prefix("n_"), on="image").join(sd.groupby("image")["merged_suspect"].mean().rename("frac_merged_suspect"), on="image")
    seeds_n = im["n_crushed"] + im["n_intact"]
    im["pct_crushed_count"] = (100 * im["n_crushed"] / seeds_n).round(2)
    a = area.reindex(im["image"]).to_numpy()
    im["pct_crushed_area"] = np.round(100 * a[:, 0] / (a[:, 0] + a[:, 1]), 2)
    cols = ["image", "group", "split", "class", "area_px", "x0", "y0", "x1", "y1", "cx", "cy", "merged_suspect", "n_pieces", "component"]
    sd[cols].to_csv(OUT / "harvest_seeds.csv", index=False)
    im.reset_index(drop=True).to_csv(OUT / "harvest_images.csv", index=False)

    o = im[im["is_original"]]
    so = sd[sd["image"].isin(o["image"])]
    comp = so.drop_duplicates(["image", "component"])
    print(f"originals: aug index counts {o['aug'].value_counts().to_dict()}; split {o['split'].value_counts().to_dict()}")
    print("per-original instances by class:\n", o[["n_crushed", "n_intact", "n_impurity"]].describe().round(1))
    print("pct area by class (originals, mean):", o[[c for c in o if c.startswith("pct_area")]].mean().round(2).to_dict())
    print("pct crushed count: min %.1f median %.1f max %.1f" % tuple(o["pct_crushed_count"].quantile([0, .5, 1])))
    print("pct crushed area:  min %.1f median %.1f max %.1f" % tuple(o["pct_crushed_area"].quantile([0, .5, 1])))
    print("components flagged merged (originals): %d / %d = %.1f %%, split into >1 piece: %d" % (
        comp["merged_suspect"].sum(), len(comp), 100 * comp["merged_suspect"].mean(), (comp["n_pieces"] > 1).sum()))
    print("by class:", comp.groupby("class")["merged_suspect"].agg(["sum", "count"]).to_dict("index"))
    print("instance count by aug (mean over groups):", im.groupby("aug")[["n_crushed", "n_intact", "n_impurity"]].mean().round(1).to_dict("index"))


if __name__ == "__main__":
    main()
