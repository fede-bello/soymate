"""Experiment B, eye check: contact sheets of chroma vs FastSAM masks.

Run on the box after make_masks.py:  cd ~/soymate-exp && .venv/bin/python experiments/mask_quality/contact_sheet.py
Writes data/exp_masks/qc/disagree16.png (the 16 lowest-IoU images, FastSAM fallbacks excluded) and
data/exp_masks/qc/random16_broken.png (16 random broken seeds). Each tile: the raw image (zoomed on the seed)
with the chroma contour in red, FastSAM in green and the dilated FastSAM in cyan; below it the current crop,
the FastSAM crop and the no-mask crop. Caption: class, background, IoU.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "experiments" / "mask_quality"))
from make_crops import SOY_V2  # noqa: E402
from make_masks import dilate  # noqa: E402

EXP = ROOT / "data" / "exp_masks"
T = 336  # tile width


def tile(r) -> Image.Image:
    stem = Path(r.source_image).stem
    rgb = np.asarray(Image.open(SOY_V2 / r.source_image).convert("RGB")).copy()
    ch = np.asarray(Image.open(EXP / "masks" / "chroma" / f"{stem}.png"))
    fs = np.asarray(Image.open(EXP / "masks" / "fastsam" / f"{stem}.png"))
    for m, col in ((dilate(fs), (0, 255, 255)), (ch, (255, 0, 0)), (fs, (0, 255, 0))):
        cnts, _ = cv2.findContours((m > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(rgb, cnts, -1, col, 2)
    ys, xs = np.nonzero((ch > 0) | (fs > 0))
    pad = 30
    y1, y2, x1, x2 = max(0, ys.min() - pad), min(rgb.shape[0], ys.max() + pad), max(0, xs.min() - pad), min(rgb.shape[1], xs.max() + pad)
    s = max(y2 - y1, x2 - x1)
    zoom = Image.fromarray(rgb[y1:y1 + s, x1:x1 + s]).resize((T, T))
    crops = [Image.open(p).resize((T // 3, T // 3)) for p in
             (ROOT / "data" / "crops" / r.crop, EXP / "crops" / "fastsam" / r.exp_crop, EXP / "crops" / "nomask" / r.exp_crop)]
    out = Image.new("RGB", (T, T + T // 3 + 18), "white")
    out.paste(zoom, (0, 0))
    for i, c in enumerate(crops):
        out.paste(c, (i * (T // 3), T))
    ImageDraw.Draw(out).text((4, T + T // 3 + 3), f"{r['class']} | {r.background} | IoU {r.iou_chroma_fastsam:.2f} | {stem}", fill="black")
    return out


def sheet(rows: pd.DataFrame, path: Path) -> None:
    tiles = [tile(r) for _, r in rows.iterrows()]
    w, h = tiles[0].size
    out = Image.new("RGB", (4 * w + 15, 4 * h + 15), "grey")
    for i, t in enumerate(tiles):
        out.paste(t, ((i % 4) * (w + 5), (i // 4) * (h + 5)))
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    q = pd.read_csv(EXP / "masks.csv")
    q = q[~q.fastsam_fallback]
    sheet(q.nsmallest(16, "iou_chroma_fastsam"), EXP / "qc" / "disagree16.png")
    sheet(q[(1 - q.iou_chroma_fastsam > 0.10) & (q["class"] == "broken")].sample(16, random_state=0, replace=False)
          if ((1 - q.iou_chroma_fastsam > 0.10) & (q["class"] == "broken")).sum() >= 16
          else q[q["class"] == "broken"].nsmallest(16, "iou_chroma_fastsam"), EXP / "qc" / "disagree16_broken.png")
    sheet(q[q["class"] == "broken"].sample(16, random_state=0), EXP / "qc" / "random16_broken.png")
