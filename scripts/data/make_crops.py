"""One masked crop per seed, with a manifest, for every dataset split by make_splits.py.

Run on the box:  cd ~/soymate && uv run python scripts/data/make_crops.py [soybean lin harvest ghana]
Reads data/splits/<dataset>.csv, writes data/crops/<dataset>/*.png and data/crops/manifest_<dataset>.csv
(merged into data/crops/manifest.csv).

Every crop is square, seed centred, the seed filling ~85 % of the side, resized to CROP_PX, and everything
outside the seed mask painted the same neutral grey. That removes the black-background and printed-date
shortcuts in d97rjyk2tz (findings.md 2.3) and the background/scale differences between datasets, so a
dataset-ID probe has to work from the seed itself.

Seed masks: chroma distance (Lab a*, b*) from the median border colour, Otsu threshold, morphological
clean-up, holes filled (same idea as segment_grains in JP's scripts/grain_pipeline.py on jp/soybean-baseline).
Harvest seeds come from the dataset's own masks; Ghana seeds from its per-seed boxes.

Class mapping (CONTEXT.md 0 and 7): sound, broken (broken / seed-coat damage), stained, immature,
insect_hole. d97rjyk2tz: Hole -> insect_hole; else Testa cracking -> broken; Healthy -> sound only when the
image has no other box; Egg-only and Normal_Damage-only images are dropped. Lin: intact -> sound,
broken and skin-damaged -> broken, spotted -> stained, immature -> immature (the original label is kept).
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SPLITS = ROOT / "data" / "splits"
OUT = ROOT / "data" / "crops"
CROP_PX = 224
FILL = (124, 116, 104)  # ImageNet mean in 0-255, identical for every dataset
SEED_FRACTION = 0.85    # seed bbox side / crop side
LIN_MAP = {"intact": "sound", "broken": "broken", "skin-damaged": "broken", "spotted": "stained", "immature": "immature"}
SOY_V2 = RAW / "soybean_v2" / "Soybean_Seed_Dataset" / "Soybean_Seed_Dataset"


def seed_mask(rgb: np.ndarray, border_frac: float = 0.04) -> np.ndarray:
    """Binary mask of seeds against a roughly uniform background.

    Uses chroma distance only (Lab a*, b*; L ignored) from the median border colour: shadows and the white
    printed date have background-like chroma, while soybean seeds are strongly yellow/orange. Interior gaps
    (specular highlights, the inside of an exit hole) are filled.
    """
    h, w = rgb.shape[:2]
    b = max(1, int(round(min(h, w) * border_frac)))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)[..., 1:]
    border = np.concatenate([lab[:b].reshape(-1, 2), lab[-b:].reshape(-1, 2),
                             lab[:, :b].reshape(-1, 2), lab[:, -b:].reshape(-1, 2)])
    dist = np.linalg.norm(lab - np.median(border, axis=0), axis=2)
    dist8 = np.clip(dist * (255.0 / max(dist.max(), 1e-6)), 0, 255).astype(np.uint8)
    dist8 = cv2.GaussianBlur(dist8, (5, 5), 0)
    _, fg = cv2.threshold(dist8, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    fg = cv2.morphologyEx(cv2.morphologyEx(fg, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k, iterations=3)
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(fg)
    cv2.drawContours(filled, cnts, -1, 255, cv2.FILLED)
    return filled


def components(mask: np.ndarray, min_area: int) -> list[np.ndarray]:
    """Filled external contours above min_area, largest first."""
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in sorted(cnts, key=cv2.contourArea, reverse=True):
        if cv2.contourArea(c) < min_area:
            break
        m = np.zeros(mask.shape, np.uint8)
        cv2.drawContours(m, [c], -1, 255, cv2.FILLED)
        out.append(m)
    return out


def masked_crop(rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Square crop centred on the mask, background painted FILL, resized to CROP_PX."""
    ys, xs = np.nonzero(mask)
    x1, x2, y1, y2 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    side = int(np.ceil(max(x2 - x1, y2 - y1) / SEED_FRACTION))
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    ox, oy = cx - side // 2, cy - side // 2
    canvas = np.empty((side, side, 3), np.uint8)
    canvas[:] = FILL
    h, w = mask.shape
    sx1, sy1, sx2, sy2 = max(0, ox), max(0, oy), min(w, ox + side), min(h, oy + side)
    region = rgb[sy1:sy2, sx1:sx2]
    keep = mask[sy1:sy2, sx1:sx2] > 0
    tile = canvas[sy1 - oy:sy2 - oy, sx1 - ox:sx2 - ox]
    tile[keep] = region[keep]
    return cv2.resize(canvas, (CROP_PX, CROP_PX), interpolation=cv2.INTER_AREA)


def save(arr: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).save(path)


def touches_border(mask: np.ndarray) -> bool:
    return bool(mask[0].any() or mask[-1].any() or mask[:, 0].any() or mask[:, -1].any())


# --------------------------------------------------------------------------- per-dataset workers
def soy_class(labels: str) -> str | None:
    s = set(labels.split("|")) if labels else set()
    if "Hole" in s:
        return "insect_hole"
    if "Testa cracking" in s:
        return "broken"
    if s == {"Healthy"}:
        return "sound"
    return None  # Egg-only, Normal_Damage-only (with or without Healthy): dropped


def soy_one(row: dict) -> dict:
    rgb = np.asarray(Image.open(SOY_V2 / row["image"]).convert("RGB"))
    comps = components(seed_mask(rgb), min_area=int(0.01 * rgb.shape[0] * rgb.shape[1]))
    out = {"source_image": row["image"], "n_components": len(comps)}
    if not comps:
        return out | {"crop": "", "seg_note": "no component"}
    m = comps[0]
    name = f"soybean/{Path(row['image']).stem}.png"
    save(masked_crop(rgb, m), OUT / name)
    return out | {"crop": name, "mask_frac": round(float((m > 0).mean()), 4),
                  "seg_note": "touches border" if touches_border(m) else ""}


def dark_background_mask(rgb: np.ndarray, thresh: int = 35) -> np.ndarray:
    """Lin crops are seed-filled circles on black corners: everything not near-black is seed."""
    fg = (cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY) > thresh).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg = cv2.morphologyEx(cv2.morphologyEx(fg, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k, iterations=2)
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(fg)
    cv2.drawContours(filled, cnts, -1, 255, cv2.FILLED)
    return filled


def lin_one(row: dict) -> dict:
    rgb = np.asarray(Image.open(RAW / "soybean_seeds_5classes" / row["image"]).convert("RGB"))
    comps = components(dark_background_mask(rgb), min_area=int(0.02 * rgb.shape[0] * rgb.shape[1]))
    out = {"source_image": row["image"], "n_components": len(comps)}
    if not comps:
        return out | {"crop": "", "seg_note": "no component"}
    m = comps[0]
    name = f"lin/{Path(row['image']).parent.name.split()[0].lower()}_{Path(row['image']).stem}.png"
    save(masked_crop(rgb, m), OUT / name)
    return out | {"crop": name, "mask_frac": round(float((m > 0).mean()), 4),
                  "seg_note": "touches border" if touches_border(m) else ""}


def run(rows: list[dict], fn) -> pd.DataFrame:
    with ProcessPoolExecutor(14) as ex:
        return pd.DataFrame(list(ex.map(fn, rows, chunksize=16)))


def soybean() -> pd.DataFrame:
    sp = pd.read_csv(SPLITS / "soybean.csv", keep_default_na=False)
    sp = sp[sp["split"] != ""].copy()
    sp["class"] = sp["labels"].map(soy_class)
    sp = sp[sp["class"].notna()]
    res = run(sp.to_dict("records"), soy_one)
    m = sp.merge(res, left_on="image", right_on="source_image")
    return pd.DataFrame({
        "crop": m["crop"], "dataset": "soybean_d97rjyk2tz", "source_image": m["image"], "group": m["group"],
        "split": m["split"], "class": m["class"], "source_label": m["labels"], "eval_rep": m["eval_rep"],
        "background": m["background"], "capture_date": m["capture_date"], "published_split": m["published_split"],
        "n_components": m["n_components"], "mask_frac": m.get("mask_frac"), "seg_note": m["seg_note"]})


def lin() -> pd.DataFrame:
    sp = pd.read_csv(SPLITS / "lin.csv", keep_default_na=False)
    sp = sp[sp["split"] != ""].copy()
    res = run(sp.to_dict("records"), lin_one)
    m = sp.merge(res, left_on="image", right_on="source_image")
    first = m.sort_values("image").drop_duplicates("group").index
    return pd.DataFrame({
        "crop": m["crop"], "dataset": "lin_v6vzvfszj6", "source_image": m["image"], "group": m["group"],
        "split": m["split"], "class": m["label"].map(LIN_MAP), "source_label": m["label"],
        "eval_rep": m.index.isin(first), "n_components": m["n_components"], "mask_frac": m.get("mask_frac"),
        "seg_note": m["seg_note"]})


STEPS = {"soybean": soybean, "lin": lin}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or list(STEPS):
        df = STEPS[name]()
        df.to_csv(OUT / f"manifest_{name}.csv", index=False)
        ok = df[df["crop"] != ""]
        print(json.dumps({name: {"crops": len(ok), "failed": int((df["crop"] == "").sum()),
                                 "seg_notes": df["seg_note"].value_counts().to_dict(),
                                 "class_x_split": ok.groupby(["class", "split"]).size().unstack(fill_value=0).to_dict()}},
                         indent=1, default=int), flush=True)
    parts = [pd.read_csv(p) for p in sorted(OUT.glob("manifest_*.csv"))]
    pd.concat(parts, ignore_index=True).to_csv(OUT / "manifest.csv", index=False)
