"""R4a: seed-count error of the training-free segmenter (scripts/data/segment_multi.py) on the Ghana group photos.

Run on the box:  cd ~/soymate/eval && OMP_NUM_THREADS=4 uv run python r4_ghana_counts.py [--overlays qc/r4] [--n-fail 5]
Reads data/splits/ghana_photos.csv and ghana_seeds.csv (from scripts/data/ghana_index.py) and the 105 photos in
data/raw/ghana_soybean/seed_data/Soyabean/group_capture/; writes results/r4_ghana_counts.json and
results/r4_ghana_counts__photos.csv, plus overlays of the worst photos.

References (neither is a perfect ground truth):
  a) published box count, only on the gt_status=ok photos (no missed seed found by the QC: the only complete
     published counts);
  b) n_seeds_est = published boxes + missed-seed blobs found by ghana_index.py's QC detector, on every photo. This is
     a semi-automatic ESTIMATE (a lower bound: it misses seeds touching a box or the border), not ground truth.
Instance level: a published box is recalled when its centre lies on one of our kept components (lower-bound recall,
the boxes are incomplete). Our components with no box centre are split into shadow / sun by the brightness of the
paper in a ring around them.
"""
import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image

from harness import N_BOOT, ROOT, SEED, wilson, write_result

sys.path.insert(0, str(ROOT / "scripts" / "data"))
from segment_multi import WORK_PX, load, segment  # noqa: E402

BASE = ROOT / "data" / "raw" / "ghana_soybean"
RING = 9  # px at work scale, paper ring around a component used for its local brightness
SHADOW_FRAC = 0.75  # ring L* below this fraction of the photo's bright-paper L* (90th pct) = in shadow


def labels_like_segment(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[int], float, np.ndarray]:
    """Same mask and component filter as segment_multi.segment, also returning the label image (work scale).
    Kept in sync by an assertion on the component count in main()."""
    scale = WORK_PX / max(rgb.shape[:2])
    small = cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) if scale < 1 else rgb
    scale = min(scale, 1.0)
    lab_img = cv2.cvtColor(small, cv2.COLOR_RGB2LAB)
    b = cv2.GaussianBlur(lab_img[..., 2], (5, 5), 0)
    _, fg = cv2.threshold(b, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg = cv2.morphologyEx(cv2.morphologyEx(fg, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(fg, 8)
    areas = stats[1:, cv2.CC_STAT_AREA].astype(float)
    big = areas[areas > 0.2 * np.median(areas)]
    unit = float(np.median(big)) if len(big) else float(np.median(areas))
    kept = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 0.3 * unit]
    return lab, fg > 0, kept, scale, lab_img[..., 0]


def shadow_flags(lab: np.ndarray, fg: np.ndarray, kept: list[int], L: np.ndarray) -> dict[int, bool]:
    paper = ~fg
    ref = np.percentile(L[paper], 90)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * RING + 1, 2 * RING + 1))
    out = {}
    for i in kept:
        ys, xs = np.nonzero(lab == i)
        y0, y1, x0, x1 = max(ys.min() - RING, 0), ys.max() + RING + 1, max(xs.min() - RING, 0), xs.max() + RING + 1
        comp = (lab[y0:y1, x0:x1] == i).astype(np.uint8)
        ring = (cv2.dilate(comp, k) > 0) & paper[y0:y1, x0:x1]
        out[i] = bool(ring.any() and np.median(L[y0:y1, x0:x1][ring]) < SHADOW_FRAC * ref)
    return out


def boot(err: np.ndarray, ref: np.ndarray, rng) -> dict:
    """MAE, mean signed error (ours - ref), MAPE with 95 % percentile CIs, resampling photos."""
    def stats(e, r):
        return np.array([np.abs(e).mean(), e.mean(), 100 * (np.abs(e) / r).mean()])
    point = stats(err, ref)
    n = len(err)
    draws = np.array([stats(err[j], ref[j]) for j in (rng.integers(0, n, n) for _ in range(N_BOOT))])
    lo, hi = np.percentile(draws, [2.5, 97.5], axis=0)
    return {name: {"value": round(float(point[i]), 3), "ci95": [round(float(lo[i]), 3), round(float(hi[i]), 3)]}
            for i, name in enumerate(["mae", "mean_signed_error", "mape_pct"])} | {"n_photos": n}


def draw_overlay(rgb, inst, lab, kept, scale, boxes, hit, unmatched_shadow, path: Path) -> None:
    out = rgb.copy()
    t = max(3, rgb.shape[1] // 600)
    for i, ins in zip(kept, inst):
        x1, y1, x2, y2 = map(int, ins["bbox"])
        col = (0, 255, 0) if ins["n_est"] == 1 else (0, 120, 255)
        if i in unmatched_shadow:
            col = (255, 255, 0) if unmatched_shadow[i] else (255, 0, 255)
        cv2.rectangle(out, (x1, y1), (x2, y2), col, t)
        if ins["n_est"] > 1:
            cv2.putText(out, str(ins["n_est"]), (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 1.5, col, t)
    for (cx, cy), h in zip(boxes, hit):
        cv2.circle(out, (int(cx), int(cy)), 3 * t, (255, 255, 255) if h else (255, 0, 0), -1)
    im = Image.fromarray(out)
    im.thumbnail((1600, 1600))
    im.save(path, quality=85)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overlays", type=Path, default=ROOT / "qc" / "r4")
    ap.add_argument("--n-fail", type=int, default=5)
    a = ap.parse_args()
    a.overlays.mkdir(parents=True, exist_ok=True)
    photos = pd.read_csv(ROOT / "data" / "splits" / "ghana_photos.csv")
    seeds = pd.read_csv(ROOT / "data" / "splits" / "ghana_seeds.csv")
    seeds["cx"], seeds["cy"] = (seeds.x0 + seeds.x1) / 2, (seeds.y0 + seeds.y1) / 2
    rows, cache = [], {}
    for p in photos.itertuples():
        t0 = time.perf_counter()
        rgb = load(str(BASE / p.photo))
        t1 = time.perf_counter()
        inst, _ = segment(rgb)
        t2 = time.perf_counter()
        lab, fg, kept, scale, L = labels_like_segment(rgb)
        assert len(kept) == len(inst), p.photo
        sh = shadow_flags(lab, fg, kept, L)
        b = seeds[seeds.photo == p.photo]
        bx = np.clip((b.cx * scale).astype(int), 0, lab.shape[1] - 1)
        by = np.clip((b.cy * scale).astype(int), 0, lab.shape[0] - 1)
        on = lab[by, bx]
        keptset = set(kept)
        hit = np.array([c in keptset for c in on], bool)
        matched = {int(c) for c in on if c in keptset}
        unm = {i: sh[i] for i in kept if i not in matched}
        n_ours = sum(i["n_est"] for i in inst)
        rows.append({"photo": p.photo, "variety": p.variety, "gt_status": p.gt_status,
                     "mapping_confidence": p.mapping_confidence, "n_boxes": len(b), "n_seeds_est": p.n_seeds_est,
                     "n_ours": n_ours, "n_components": len(inst),
                     "n_multi_components": sum(i["n_est"] > 1 for i in inst),
                     "err_vs_est": n_ours - p.n_seeds_est, "err_vs_boxes": n_ours - len(b),
                     "boxes_recalled": int(hit.sum()),
                     "box_recall": round(hit.mean(), 4) if len(b) else None,
                     "n_unmatched_components": len(unm), "n_unmatched_shadow": sum(unm.values()),
                     "n_unmatched_sun": len(unm) - sum(unm.values()),
                     "n_components_shadow": sum(sh.values()),
                     "t_load_s": round(t1 - t0, 3), "t_segment_s": round(t2 - t1, 3)})
        cache[p.photo] = (inst, kept, scale, list(zip(b.cx, b.cy)), hit, unm)
        print(f"{p.variety:10s} {Path(p.photo).name}: ours {n_ours} est {p.n_seeds_est} boxes {len(b)} "
              f"recall {hit.mean():.2f} {t2 - t1:.2f}s", flush=True)
    df = pd.DataFrame(rows)
    rng = np.random.default_rng(SEED)
    ok = df[df.gt_status == "ok"]
    res = {"n_photos": len(df), "mapping_confidence": df.mapping_confidence.value_counts().to_dict(),
           "a_vs_published_boxes_gt_ok": {"overall": boot(ok.err_vs_boxes.to_numpy(float), ok.n_boxes.to_numpy(float), rng),
                                          "photos": ok[["photo", "n_boxes", "n_seeds_est", "n_ours"]].to_dict("records")},
           "b_vs_n_seeds_est_SEMI_AUTOMATIC_ESTIMATE": {
               "overall": boot(df.err_vs_est.to_numpy(float), df.n_seeds_est.to_numpy(float), rng),
               "per_variety": {v: boot(g.err_vs_est.to_numpy(float), g.n_seeds_est.to_numpy(float), rng)
                               for v, g in df.groupby("variety")}},
           "c_vs_published_boxes_all_photos_incomplete": {
               "overall": boot(df.err_vs_boxes.to_numpy(float), df.n_boxes.to_numpy(float), rng)}}
    nb, nr = int(df.n_boxes.sum()), int(df.boxes_recalled.sum())
    res["box_recall_lower_bound"] = {"pooled": round(nr / nb, 4), "wilson95_ignoring_clustering": wilson(nr, nb),
                                     "n_boxes": nb, "per_photo_mean": round(float(df.box_recall.mean()), 4),
                                     "per_photo_min": round(float(df.box_recall.min()), 4),
                                     "per_variety_pooled": {v: round(g.boxes_recalled.sum() / g.n_boxes.sum(), 4)
                                                            for v, g in df.groupby("variety")}}
    nc = int(df.n_components.sum())
    res["unmatched_components"] = {"n_components": nc, "n_unmatched": int(df.n_unmatched_components.sum()),
                                   "n_unmatched_shadow": int(df.n_unmatched_shadow.sum()),
                                   "n_unmatched_sun": int(df.n_unmatched_sun.sum()),
                                   "n_components_shadow": int(df.n_components_shadow.sum())}
    res["timing_s_per_photo"] = {k: {"median": round(float(df[k].median()), 3), "p90": round(float(df[k].quantile(.9)), 3),
                                     "max": round(float(df[k].max()), 3)} for k in ["t_load_s", "t_segment_s"]}
    worst = df.reindex(df.err_vs_est.abs().sort_values(ascending=False).index).head(a.n_fail)
    res["worst_vs_est"] = worst[["photo", "n_ours", "n_seeds_est", "n_boxes", "err_vs_est", "n_multi_components",
                                 "n_unmatched_sun", "n_unmatched_shadow"]].to_dict("records")
    for r in worst.itertuples():
        inst, kept, scale, boxes, hit, unm = cache[r.photo]
        draw_overlay(load(str(BASE / r.photo)), inst, None, kept, scale, boxes, hit, unm,
                     a.overlays / f"{r.variety}_{Path(r.photo).stem}.jpg")
    how = ("Training-free segmenter scripts/data/segment_multi.py (Lab b* Otsu on a 1600 px copy, open/close, "
           "count per component = round(area / median single-seed area)) run on all 105 Ghana group photos "
           f"(c7i.4xlarge box, OMP_NUM_THREADS=4). Errors are ours minus reference; MAE, mean signed error and "
           f"MAPE (|err|/ref) with 95 % percentile bootstrap CIs over photos ({N_BOOT} draws, seed {SEED}). "
           "(a) reference = published box count on the gt_status=ok photos only, the only complete published counts. "
           "(b) reference = n_seeds_est from scripts/data/ghana_index.py = published boxes + missed-seed blobs from its "
           "colour-blob QC detector: a semi-automatic estimate and lower bound, NOT ground truth. (c) vs all published "
           "boxes, which are known to be incomplete (shown only for scale). Box recall: share of published box centres "
           "lying on one of our kept components (lower bound, boxes are incomplete); Wilson CI ignores clustering by "
           "photo. Unmatched components = ours with no box centre; shadow if the median L* of a "
           f"{RING}px paper ring around it is below {SHADOW_FRAC} x the photo's 90th-percentile paper L*. Timing is "
           "wall-clock per photo: JPEG load + EXIF transpose, and segment().")
    write_result("r4_ghana_counts", res, how, tables={"photos": df})


if __name__ == "__main__":
    main()
