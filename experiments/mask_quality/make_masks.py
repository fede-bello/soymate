"""Experiment B, step 1: alternative seed masks and crops for the soybean d97rjyk2tz single-seed images.

Run on the box:  cd ~/soymate-exp && OMP_NUM_THREADS=6 .venv/bin/python experiments/mask_quality/make_masks.py
Reads data/crops/manifest_soybean.csv (the R2 rows) and the raw 640x640 images. Writes only under data/exp_masks/:
  masks/{chroma,fastsam}/<stem>.png       binary masks at image resolution
  crops/<arm>/soybean/<stem>.png          224 px crops for the arms below
  masks.csv                               per-image mask quality (IoU vs chroma, areas, FastSAM latency, notes)

Arms (crop geometry identical to pipeline/make_crops.masked_crop: square, seed bbox ~85 % of the side):
  fastsam      FastSAM-s mask, background painted FILL
  fastsam_dil  the FastSAM mask dilated by DIL_FRAC of the seed's equivalent diameter (keeps edge cracks)
  nomask       same square crop around the FastSAM mask, real background kept (control, session shortcut risk)
The current chroma arm ("current") is not recomputed: its crops and dinov2-small features already exist.

FastSAM-s (Ultralytics, AGPL-3.0) settings follow docs/fastsam_grain_experiment.md: imgsz 640 (the images are
640x640), conf 0.4, NMS IoU 0.9, max_det 300, retina masks, CPU. Mask choice: among FastSAM masks covering
0.5-90 % of the image, the one with the highest IoU against the chroma mask (holes filled, largest component kept).
If none is found at conf 0.4 the call is repeated at conf 0.1; if still none, or best IoU < 0.2, the image falls
back to the chroma mask (counted as fastsam_fallback) so that every arm has the same rows.
"""
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))
from make_crops import CROP_PX, FILL, SEED_FRACTION, SOY_V2, components, masked_crop, seed_mask  # noqa: E402

OUT = ROOT / "data" / "exp_masks"
WEIGHTS = ROOT / "weights" / "FastSAM-s.pt"
DIL_FRAC = 0.04
MIN_IOU = 0.2


def fill_largest(mask: np.ndarray) -> np.ndarray:
    comps = components(mask.astype(np.uint8) * 255, min_area=1)
    return comps[0] if comps else np.zeros(mask.shape, np.uint8)


def iou(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a > 0, b > 0
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 0.0


def bbox_crop(rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """masked_crop geometry without masking: real background kept, FILL only outside the image frame."""
    ys, xs = np.nonzero(mask)
    x1, x2, y1, y2 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    side = int(np.ceil(max(x2 - x1, y2 - y1) / SEED_FRACTION))
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    ox, oy = cx - side // 2, cy - side // 2
    canvas = np.empty((side, side, 3), np.uint8)
    canvas[:] = FILL
    h, w = mask.shape
    sx1, sy1, sx2, sy2 = max(0, ox), max(0, oy), min(w, ox + side), min(h, oy + side)
    canvas[sy1 - oy:sy2 - oy, sx1 - ox:sx2 - ox] = rgb[sy1:sy2, sx1:sx2]
    return cv2.resize(canvas, (CROP_PX, CROP_PX), interpolation=cv2.INTER_AREA)


def dilate(mask: np.ndarray, frac: float = DIL_FRAC) -> np.ndarray:
    d = 2 * np.sqrt((mask > 0).sum() / np.pi)
    r = max(1, int(round(frac * d)))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    return cv2.dilate(mask, k)


def fastsam_masks(model, rgb: np.ndarray, conf: float) -> np.ndarray:
    r = model(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), device="cpu", retina_masks=True, imgsz=640, conf=conf,
              iou=0.9, max_det=300, verbose=False)[0]
    if r.masks is None:
        return np.zeros((0, *rgb.shape[:2]), bool)
    m = r.masks.data.cpu().numpy() > 0.5
    if m.shape[1:] != rgb.shape[:2]:
        m = np.stack([cv2.resize(x.astype(np.uint8), rgb.shape[1::-1], interpolation=cv2.INTER_NEAREST) > 0 for x in m])
    return m


def pick(masks: np.ndarray, chroma: np.ndarray) -> tuple[np.ndarray | None, float, int]:
    n_px = chroma.size
    best, best_iou, n_ok = None, -1.0, 0
    for m in masks:
        frac = m.sum() / n_px
        if not 0.005 <= frac <= 0.9:
            continue
        n_ok += 1
        m = fill_largest(m)
        v = iou(m, chroma)
        if v > best_iou:
            best, best_iou = m, v
    return best, best_iou, n_ok


def save(arr: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).save(path)


def main():
    from ultralytics import FastSAM
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", 6)))
    man = pd.read_csv(ROOT / "data" / "crops" / "manifest_soybean.csv", keep_default_na=False)
    man = man[man["crop"] != ""]
    model = FastSAM(str(WEIGHTS))
    model(np.zeros((640, 640, 3), np.uint8), device="cpu", imgsz=640, verbose=False)  # warm-up
    rows = []
    for i, r in enumerate(man.itertuples()):
        stem = Path(r.source_image).stem
        rgb = np.asarray(Image.open(SOY_V2 / r.source_image).convert("RGB"))
        comps = components(seed_mask(rgb), min_area=int(0.01 * rgb.shape[0] * rgb.shape[1]))
        chroma = comps[0]
        t0 = time.perf_counter()
        masks = fastsam_masks(model, rgb, 0.4)
        fs, v, n_ok = pick(masks, chroma)
        conf_used = 0.4
        if fs is None:
            masks = fastsam_masks(model, rgb, 0.1)
            fs, v, n_ok = pick(masks, chroma)
            conf_used = 0.1
        dt = time.perf_counter() - t0
        fallback = fs is None or v < MIN_IOU
        if fallback:
            fs, v = chroma.copy(), 1.0
        fsd = dilate(fs)
        save(chroma, OUT / "masks" / "chroma" / f"{stem}.png")
        save(fs, OUT / "masks" / "fastsam" / f"{stem}.png")
        name = f"soybean/{stem}.png"
        save(masked_crop(rgb, fs), OUT / "crops" / "fastsam" / name)
        save(masked_crop(rgb, fsd), OUT / "crops" / "fastsam_dil" / name)
        save(bbox_crop(rgb, fs), OUT / "crops" / "nomask" / name)
        a_c, a_f = int((chroma > 0).sum()), int((fs > 0).sum())
        rows.append({"crop": r.crop, "exp_crop": name, "source_image": r.source_image,
                     "n_fastsam_masks": int(len(masks)), "n_plausible": n_ok, "conf_used": conf_used,
                     "fastsam_fallback": bool(fallback), "iou_chroma_fastsam": round(v, 4),
                     "iou_chroma_fastsam_dil": round(iou(chroma, fsd), 4),
                     "area_chroma": a_c, "area_fastsam": a_f, "area_ratio": round(a_f / max(a_c, 1), 4),
                     "fastsam_s": round(dt, 4)})
        if i % 100 == 0:
            print(i, len(man), rows[-1], flush=True)
    df = pd.DataFrame(rows).merge(man[["crop", "class", "split", "group", "background"]], on="crop")
    df.to_csv(OUT / "masks.csv", index=False)
    print(df[["iou_chroma_fastsam", "area_ratio", "fastsam_s"]].describe().to_string(),
          "\nfallbacks", int(df.fastsam_fallback.sum()), flush=True)


if __name__ == "__main__":
    main()
