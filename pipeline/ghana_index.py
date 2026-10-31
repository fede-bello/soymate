"""Per-seed ground truth for the Ghana soybean group photos (Mendeley t94nzy4ptz v2, CC BY 4.0).

Run on the box:  cd ~/soymate-next && uv run python pipeline/ghana_index.py [--overlays DIR]
Reads data/raw/ghana_soybean/seed_data/Soyabean/, writes data/splits/ghana_seeds.csv (one row per seed) and
data/splits/ghana_photos.csv (one row per photo).

The dataset ships one single_seeds/<Variety>/Group<N>/_crop_metadata.csv per group photo but does not say which
PXL_*.jpg each group came from, and the group numbers do not follow capture order. The mapping is recovered per
variety from the boxes themselves:
- a group can only come from a photo that contains all its boxes (the photos are hand-cropped, sizes all differ);
- score(group, photo) = fraction of box centres that land on a seed pixel (red > blue, i.e. not blue paper);
- a one-to-one assignment maximises the total score (Hungarian). The right photo scores ~1.0, the runner-up
  well under 0.6, so `mapping_confidence` is "high" when score >= HIT_MIN and score - runner_up >= MARGIN_MIN,
  "low" otherwise (low rows are kept but should not be trusted). No photo carries an EXIF rotation, so the boxes
  are already in displayed (EXIF-transposed) pixel coordinates; the script still transposes to be safe.

The published boxes come from an automatic detector and are NOT complete counts: seeds in shadow and some in
sun have no box, and in Favor the boxes sit on the seed plus its cast shadow, clipping the lit side. Per-photo QC
therefore estimates missed seeds (seed-coloured, seed-sized compact blobs away from every box; a lower bound, it
misses seeds touching a box or the border), the median share of each seed's pixels inside its box
(`median_box_coverage`), overlapping boxes (touching seeds; duplicates when IoU > DUP_IOU) and boxes larger than
MERGED_AREA x the photo median (possibly two seeds). `gt_status` summarises: ok, missing_seeds, boxes_clip_seeds.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageOps
from scipy import ndimage
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "raw" / "ghana_soybean"
SOY = BASE / "seed_data" / "Soyabean"
OUT = ROOT / "data" / "splits"
HIT_MIN = 0.90  # fraction of box centres on seed pixels for a confident match
MARGIN_MIN = 0.30  # required gap to the second-best photo
DUP_IOU = 0.5
MERGED_AREA = 1.8
SEED_RB = 15  # red minus blue for a confident seed pixel (missed-seed search)
BLOB_AREA = (0.4, 2.5)  # missed-seed blob area, as a fraction of the photo median box area
COVERAGE_MIN = 0.85  # median share of a seed inside its box; below this the boxes clip the seeds


def seed_mask(img: np.ndarray) -> np.ndarray:
    """True where a pixel is not blue paper (seeds are yellow/brown, red channel above blue)."""
    return img[..., 0].astype(int) - img[..., 2].astype(int) > 0


def load_groups(variety: str) -> dict[int, pd.DataFrame]:
    out = {}
    for d in (SOY / "single_seeds" / variety).glob("Group*"):
        df = pd.read_csv(d / "_crop_metadata.csv")
        df["x1"], df["y1"] = df.bbox_x + df.bbox_w, df.bbox_y + df.bbox_h
        df["cx"], df["cy"] = df.bbox_x + df.bbox_w // 2, df.bbox_y + df.bbox_h // 2
        out[int(d.name.removeprefix("Group"))] = df
    return dict(sorted(out.items()))


def hit_rate(df: pd.DataFrame, mask: np.ndarray) -> float:
    h, w = mask.shape
    if df.x1.max() > w or df.y1.max() > h:
        return -1.0  # a box falls outside the photo: impossible
    return float(mask[df.cy, df.cx].mean())


def box_qc(df: pd.DataFrame, img: np.ndarray, mask: np.ndarray) -> dict:
    b = df[["bbox_x", "bbox_y", "x1", "y1"]].to_numpy(float)
    ix = np.clip(np.minimum(b[:, None, 2], b[None, :, 2]) - np.maximum(b[:, None, 0], b[None, :, 0]), 0, None)
    iy = np.clip(np.minimum(b[:, None, 3], b[None, :, 3]) - np.maximum(b[:, None, 1], b[None, :, 1]), 0, None)
    inter = ix * iy
    area = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    iou = inter / (area[:, None] + area[None, :] - inter)
    np.fill_diagonal(iou, 0)
    h, w = mask.shape
    covered = np.zeros_like(mask)
    coverage = []
    for x0, y0, x1, y1 in b.astype(int):
        covered[y0:y1, x0:x1] = True
        px, py = (x1 - x0) // 3, (y1 - y0) // 3  # seed pixels inside the box / inside the box grown by 1/3 per side
        grown = mask[max(0, y0 - py):y1 + py, max(0, x0 - px):x1 + px].sum()
        coverage.append(mask[y0:y1, x0:x1].sum() / max(grown, 1))
    # Missed seeds: seed-coloured, seed-sized, compact blobs clear of every box and of the photo border.
    strong = img[..., 0].astype(int) - img[..., 2].astype(int) > SEED_RB
    near_box = ndimage.binary_dilation(covered, iterations=15)
    lab, n = ndimage.label(ndimage.binary_opening(strong, iterations=3))
    med = df.area_px.median()
    missed = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        blob = lab[sl] == i + 1
        a, bh, bw = blob.sum(), blob.shape[0], blob.shape[1]
        if not (BLOB_AREA[0] * med <= a <= BLOB_AREA[1] * med) or a < 0.5 * bh * bw or max(bh, bw) > 2.5 * min(bh, bw):
            continue
        if sl[0].start == 0 or sl[1].start == 0 or sl[0].stop == h or sl[1].stop == w or near_box[sl][blob].any():
            continue
        missed.append(sl)
    return {"overlapping": (iou > 0).any(1), "duplicate": (iou > DUP_IOU).any(1),
            "merged": df.area_px.to_numpy() > MERGED_AREA * med, "coverage": np.array(coverage), "missed": missed}


def overlay(img: Image.Image, df: pd.DataFrame, qc: dict, path: Path) -> None:
    draw = ImageDraw.Draw(img)
    for i, r in enumerate(df.itertuples()):
        colour = "red" if not r.on_seed else "orange" if qc["merged"][i] else "magenta" if qc["overlapping"][i] else "lime"
        draw.rectangle([r.bbox_x, r.bbox_y, r.x1, r.y1], outline=colour, width=5)
    for sy, sx in qc["missed"]:
        draw.rectangle([sx.start, sy.start, sx.stop, sy.stop], outline="yellow", width=9)
    img.thumbnail((1600, 1600))
    img.save(path, quality=85)


def main(overlay_dir: Path | None) -> None:
    seeds, photos = [], []
    for vdir in sorted((SOY / "group_capture").iterdir()):
        variety = vdir.name
        paths = sorted(vdir.glob("*.jpg"))
        imgs = [ImageOps.exif_transpose(Image.open(p)).convert("RGB") for p in paths]
        masks = [seed_mask(np.asarray(im)) for im in imgs]
        groups = load_groups(variety)
        gids = list(groups)
        score = np.array([[hit_rate(groups[g], m) for m in masks] for g in gids])
        rows, cols = linear_sum_assignment(-score)
        assigned = dict(zip(cols, rows))
        for pi, (path, im, mask) in enumerate(zip(paths, imgs, masks)):
            rel = path.relative_to(BASE).as_posix()
            rec = {"photo": rel, "variety": variety, "width": im.width, "height": im.height,
                   "exif_orientation": Image.open(path).getexif().get(274, 1)}
            if pi not in assigned:
                photos.append({**rec, "group": None, "n_seeds_gt": None, "mapping_confidence": "unmapped"})
                continue
            gi = assigned[pi]
            g, df = gids[gi], groups[gids[gi]].copy()
            hit = score[gi, pi]
            runner = float(np.max(np.delete(score[gi], pi), initial=-1.0))
            conf = "high" if hit >= HIT_MIN and hit - runner >= MARGIN_MIN else "low"
            df["on_seed"] = mask[df.cy, df.cx]
            qc = box_qc(df, np.asarray(im), mask)
            n_missed, cov = len(qc["missed"]), float(np.median(qc["coverage"]))
            photos.append({**rec, "group": g, "n_seeds_gt": len(df), "centre_hit_rate": round(hit, 4),
                           "runner_up_hit_rate": round(runner, 4),
                           "runner_up_photo": paths[int(np.argsort(score[gi])[-2])].name if len(paths) > 1 else "",
                           "n_feasible_photos": int((score[gi] >= 0).sum()),
                           "n_boxes_off_seed": int((~df.on_seed).sum()), "n_overlapping": int(qc["overlapping"].sum()),
                           "n_duplicates": int(qc["duplicate"].sum()), "n_merged_suspects": int(qc["merged"].sum()),
                           "n_missed_seeds_est": n_missed, "n_seeds_est": len(df) + n_missed,
                           "gt_completeness": round(len(df) / (len(df) + n_missed), 3),
                           "median_box_coverage": round(cov, 3),
                           "gt_status": "ok" if n_missed == 0 and cov >= COVERAGE_MIN else
                                        "missing_seeds" if cov >= COVERAGE_MIN else
                                        "boxes_clip_seeds" if n_missed == 0 else "missing_seeds;boxes_clip_seeds",
                           "median_area_px": float(df.area_px.median()),
                           "mapping_confidence": conf})
            for i, r in enumerate(df.itertuples()):
                seeds.append({"photo": rel, "variety": variety, "group": g, "seed_index": r.index,
                              "crop_filename": r.filename, "x0": r.bbox_x, "y0": r.bbox_y, "x1": r.x1, "y1": r.y1,
                              "area_px": r.area_px, "circularity": r.circularity, "centre_on_seed": bool(r.on_seed), "box_coverage": round(float(qc["coverage"][i]), 3),
                              "overlaps_other": bool(qc["overlapping"][i]), "merged_suspect": bool(qc["merged"][i]),
                              "mapping_confidence": conf})
            if overlay_dir:
                overlay(im.copy(), df, qc, overlay_dir / f"{variety}_G{g:02d}_{path.stem}.jpg")
        print(f"{variety}: {len(paths)} photos, {len(gids)} groups, assigned {len(assigned)}")
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(seeds).to_csv(OUT / "ghana_seeds.csv", index=False)
    ph = pd.DataFrame(photos)
    ph.to_csv(OUT / "ghana_photos.csv", index=False)
    print(ph.mapping_confidence.value_counts().to_dict(), "seeds:", len(seeds))
    print(ph.n_seeds_gt.describe().round(1).to_dict())
    print(ph.gt_status.value_counts().to_dict(), "missed (est):", int(ph.n_missed_seeds_est.sum()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--overlays", type=Path, help="write one QC overlay JPEG per photo here")
    a = ap.parse_args()
    if a.overlays:
        a.overlays.mkdir(parents=True, exist_ok=True)
    main(a.overlays)
