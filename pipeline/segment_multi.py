"""Find and count seeds on real multi-seed photos (R4), with no training.

Usage on the box: uv run python pipeline/segment_multi.py <image> [--overlay out.jpg]
As a module: segment(rgb) -> list of instances (bbox, area, centroid, n_est).

Method: soybean seeds are yellow (Lab b* > 0) even in shadow, while the blue paper (Ghana) is b* < 0 and the
table at the photo edges is neutral, so b* is thresholded with Otsu on a downscaled copy. Components are
cleaned with opening/closing; a component's seed count is round(area / median single-seed area), which handles
pairs of touching seeds without watershed. Packed bulk photos (Lin originals) have no background and are out
of scope for this method: they are evaluated with the hand-labelled points only.
"""
import argparse

import cv2
import numpy as np
from PIL import Image, ImageOps

WORK_PX = 1600  # long side used for segmentation


def segment(rgb: np.ndarray) -> tuple[list[dict], float]:
    """Return (instances in original pixel coordinates, scale used)."""
    scale = WORK_PX / max(rgb.shape[:2])
    small = cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) if scale < 1 else rgb
    scale = min(scale, 1.0)
    b = cv2.cvtColor(small, cv2.COLOR_RGB2LAB)[..., 2]
    b = cv2.GaussianBlur(b, (5, 5), 0)
    _, fg = cv2.threshold(b, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg = cv2.morphologyEx(cv2.morphologyEx(fg, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
    n, lab, stats, cents = cv2.connectedComponentsWithStats(fg, 8)
    areas = stats[1:, cv2.CC_STAT_AREA].astype(float)
    if not len(areas):
        return [], scale
    # Single-seed area: median of mid-sized components (drops specks and merged blobs from the estimate).
    big = areas[areas > 0.2 * np.median(areas)]
    unit = float(np.median(big)) if len(big) else float(np.median(areas))
    inst = []
    for i in range(1, n):
        a = stats[i, cv2.CC_STAT_AREA]
        if a < 0.3 * unit:
            continue
        x, y, w, h = stats[i, :4] / scale
        inst.append({"bbox": [float(x), float(y), float(x + w), float(y + h)], "area": float(a / scale**2),
                     "centroid": [float(cents[i][0] / scale), float(cents[i][1] / scale)],
                     "n_est": max(1, int(round(a / unit)))})
    return inst, scale


def load(path: str) -> np.ndarray:
    return np.asarray(ImageOps.exif_transpose(Image.open(path)).convert("RGB"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--overlay")
    a = ap.parse_args()
    rgb = load(a.image)
    inst, _ = segment(rgb)
    print(f"components {len(inst)}  seeds_est {sum(i['n_est'] for i in inst)}")
    if a.overlay:
        out = rgb.copy()
        for i in inst:
            x1, y1, x2, y2 = map(int, i["bbox"])
            cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0) if i["n_est"] == 1 else (255, 0, 0), 4)
        im = Image.fromarray(out)
        im.thumbnail((1600, 1600))
        im.save(a.overlay, quality=80)
