"""Experiment A: zero-shot instance segmentation of packed (bulk) soybean photos, for a possible demo "bulk" mode.

Ground truth: Mechanical-harvest soybean hwdtghttp7 (CC BY 4.0), the 40 original images (aug 01). Per-instance GT
masks are rebuilt from the per-pixel class masks exactly as pipeline/harvest_index.py does (snap to palette,
4-connected components per class, specks dropped, merged crushed/intact components split by watershed); the
per-class counts are checked against data/splits/harvest_seeds.csv. None of the methods is trained on this dataset,
so all 40 originals are unseen test data; settings are picked on the 28 train originals only and the 6 test
originals are the headline.

Methods (CPU): FastSAM-s (Ultralytics, AGPL-3.0), Cellpose-SAM (cellpose 4, BSD-3), our classical segmenter
(pipeline/segment_multi.py) and a distance-transform watershed on its foreground.

Run on the box (separate env, never in ~/soymate-next):
  cd ~/soymate-exp && export UV_PROJECT_ENVIRONMENT=.venv-bulk OMP_NUM_THREADS=6
  uv run python experiments/bulk_segmentation/bulk_segmentation.py predict --method fastsam    # also cellpose, classical, watershed
  uv run python experiments/bulk_segmentation/bulk_segmentation.py report --overlays <dir>
  uv run python experiments/bulk_segmentation/bulk_segmentation.py latency --config <raw config name>
Raw predictions are cached under outputs/bulk_segmentation/ (ignored); report writes results/bulk_segmentation.json
and results/bulk_segmentation__images.csv, __configs.csv, __ghana.csv.
"""
import argparse
import itertools
import json
import pickle
import resource
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import N_BOOT, ROOT, SEED, write_result  # noqa: E402

sys.path.insert(0, str(ROOT / "pipeline"))
import harvest_index as hi  # noqa: E402
from segment_multi import load as load_rgb, segment  # noqa: E402

CACHE = ROOT / "outputs" / "bulk_segmentation"
WEIGHTS = ROOT / "weights" / "FastSAM-s.pt"
FASTSAM_URL = "https://github.com/ultralytics/assets/releases/download/v8.3.0/FastSAM-s.pt"
FASTSAM_SHA = "c9f78716a81c7aff0d608ccc73e1b82ab3aaad86005049f6a92106a0be6d0844"
MAX_DET = 300  # FastSAM raw-mask cap; hitting it can undercount dense photos
SHEET_FRAC = 0.25  # any mask above this fraction of the image is the sheet/background, always dropped
IOU_MATCH = 0.5
BF_TOL = 3  # px, boundary F-score tolerance at native resolution
GHANA = ["ghana_g17", "ghana_favor", "ghana_afayak_shadow"]


# --------------------------------------------------------------------------- masks as compact crops
class Mask:
    """A binary mask stored as its bounding-box crop (full-image masks of 1.3 Mpx are too big to keep 300 of)."""
    __slots__ = ("y0", "x0", "m")

    def __init__(self, full: np.ndarray | None = None, y0=0, x0=0, m=None):
        if full is not None:
            ys, xs = np.nonzero(full.any(1))[0], np.nonzero(full.any(0))[0]
            self.y0, self.x0 = int(ys[0]), int(xs[0])
            self.m = full[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1].astype(bool)
        else:
            self.y0, self.x0, self.m = y0, x0, m

    @property
    def box(self):
        return self.y0, self.x0, self.y0 + self.m.shape[0], self.x0 + self.m.shape[1]

    @property
    def area(self):
        return int(self.m.sum())

    def full(self, shape):
        out = np.zeros(shape, bool)
        y0, x0, y1, x1 = self.box
        out[y0:y1, x0:x1] = self.m
        return out


def masks_from_labels(lab: np.ndarray) -> list[Mask]:
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is not None:
            out.append(Mask(y0=sl[0].start, x0=sl[1].start, m=lab[sl] == i))
    return out


def inter(a: Mask, b: Mask) -> int:
    ay0, ax0, ay1, ax1 = a.box
    by0, bx0, by1, bx1 = b.box
    y0, x0, y1, x1 = max(ay0, by0), max(ax0, bx0), min(ay1, by1), min(ax1, bx1)
    if y0 >= y1 or x0 >= x1:
        return 0
    return int((a.m[y0 - ay0:y1 - ay0, x0 - ax0:x1 - ax0] & b.m[y0 - by0:y1 - by0, x0 - bx0:x1 - bx0]).sum())


# --------------------------------------------------------------------------- ground truth
def originals() -> pd.DataFrame:
    im = pd.read_csv(ROOT / "data" / "splits" / "harvest_images.csv", dtype={"group": str})
    return im[im["is_original"]].reset_index(drop=True)


def gt_instances(lab: np.ndarray) -> tuple[np.ndarray, list[str]]:
    """Instance label map (0 = none) and class per instance, same rules as harvest_index.instances."""
    cc = {c: ndi.label(lab == c) for c in hi.CLASSES}
    a_int = np.bincount(cc[2][0].ravel())[1:]
    ref = float(np.median(a_int[a_int > 0.2 * a_int.max()])) if a_int.size else 5000.0
    r_ref = np.sqrt(ref / np.pi)
    out, classes = np.zeros(lab.shape, np.int32), []
    from skimage.feature import peak_local_max
    from skimage.measure import regionprops
    from skimage.segmentation import watershed
    for c, (L, _) in cc.items():
        for rp in regionprops(L):
            if rp.area < hi.MIN_AREA_FRAC * ref:
                continue
            y0, x0, y1, x1 = rp.bbox
            pieces = [rp.image]
            if c != 3 and rp.solidity < hi.SOLIDITY_MIN and rp.area > hi.AREA_MERGE * ref:
                sub = np.pad(rp.image, 1)
                dist = ndi.distance_transform_edt(sub)
                pk = peak_local_max(dist, min_distance=max(3, int(hi.PEAK_MIN_DIST_FRAC * r_ref)),
                                    threshold_abs=0.3 * r_ref, labels=sub.astype(int), exclude_border=False)
                if len(pk) > 1:
                    mk = np.zeros_like(sub, dtype=np.int32)
                    mk[tuple(pk.T)] = np.arange(1, len(pk) + 1)
                    ws = watershed(-dist, mk, mask=sub)[1:-1, 1:-1]
                    pieces = [ws == q for q in np.unique(ws) if q]
            for p in pieces:
                classes.append(hi.CLASSES[c])
                out[y0:y1, x0:x1][p] = len(classes)
    return out, classes


def load_gt(stems: list[str]) -> dict:
    seeds = pd.read_csv(ROOT / "data" / "splits" / "harvest_seeds.csv")
    gt = {}
    for s in stems:
        lab, _ = hi.snap(np.array(Image.open(hi.VOC / "SegmentationClass" / f"{s}.png").convert("RGB")))
        L, cls = gt_instances(lab)
        ref = seeds[seeds["image"] == f"JPEGImages/{s}.jpg"]["class"].value_counts().to_dict()
        assert pd.Series(cls).value_counts().to_dict() == ref, (s, ref)
        gt[s] = (L, np.array(cls))
    return gt


def image_path(stem: str) -> Path:
    return hi.VOC / "JPEGImages" / f"{stem}.jpg"


# --------------------------------------------------------------------------- methods (raw predictions)
def fastsam_model(weights: Path = WEIGHTS):
    import hashlib
    from ultralytics import FastSAM
    if not weights.exists():
        import urllib.request
        weights.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(FASTSAM_URL, weights)
    assert hashlib.sha256(weights.read_bytes()).hexdigest() == FASTSAM_SHA, "FastSAM-s.pt SHA-256 mismatch"
    return FastSAM(str(weights))


def fastsam_predict(model, rgb: np.ndarray, imgsz: int, retina: bool, iou: float, long_side: int | None = None,
                    conf: float = 0.1, max_det: int = MAX_DET) -> tuple[list[Mask], np.ndarray]:
    """Raw FastSAM masks at native resolution (score-ordered) and their confidences. conf is filtered later."""
    from ultralytics.utils.ops import scale_masks
    H, W = rgb.shape[:2]
    inp = rgb
    if long_side and max(H, W) != long_side:
        s = long_side / max(H, W)
        inp = cv2.resize(rgb, (int(W * s), int(H * s)))
    r = model(cv2.cvtColor(inp, cv2.COLOR_RGB2BGR), device="cpu", retina_masks=retina, imgsz=imgsz, conf=conf,
              iou=iou, max_det=max_det, verbose=False)[0]
    if r.masks is None:
        return [], np.zeros(0)
    scores = r.boxes.conf.cpu().numpy()
    out = []
    for k in range(len(scores)):
        m = r.masks.data[k]
        if m.shape != inp.shape[:2]:  # retina_masks=False: letterboxed inference size, undo the padding
            m = scale_masks(m[None, None].float(), inp.shape[:2])[0, 0]
        m = m.cpu().numpy() > 0.5
        if m.shape != (H, W):
            m = cv2.resize(m.astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST) > 0
        out.append(Mask(m) if m.any() else None)
    keep = [i for i, m in enumerate(out) if m is not None]
    return [out[i] for i in keep], scores[keep]


FASTSAM_RAW = {f"fs_{sz}_{'ret' if ret else 'noret'}_iou{iou}": dict(imgsz=sz, retina=ret, iou=iou)
               for sz, ret, iou in itertools.product([640, 1024, 1280], [True, False], [0.7, 0.9])}
FASTSAM_RAW["fs_jp"] = dict(imgsz=640, retina=True, iou=0.9, long_side=1024, conf=0.4)  # JP's exact settings
# cpsam rescales by 30 / diameter; 130 px is about the median train seed diameter (2 x sqrt(area / pi))
# Full-resolution auto-diameter ("cp_d0", ~23 min on CPU) was cut for time; the fixed diameter matches the
# median seed size measured on train.
CELLPOSE_RAW = {"cp_half_d0": dict(scale=0.5, diameter=None), "cp_d130": dict(diameter=130.0)}
WATERSHED_RAW = {f"ws_{fg}_md{md}": dict(fg=fg, md=md) for fg in ["bstar", "gray"] for md in [0.4, 0.6, 0.8]}


def cellpose_predict(model, rgb, diameter=None, scale=1.0):
    H, W = rgb.shape[:2]
    inp = cv2.resize(rgb, (int(W * scale), int(H * scale)), interpolation=cv2.INTER_AREA) if scale != 1 else rgb
    lab = model.eval(inp, diameter=diameter, batch_size=8)[0]
    if scale != 1:
        lab = cv2.resize(lab.astype(np.int32), (W, H), interpolation=cv2.INTER_NEAREST)
    ms = masks_from_labels(lab.astype(np.int32))
    return ms, np.ones(len(ms))


def classical_fg(rgb, kind):
    """Foreground used by segment_multi (Lab b* Otsu, opened/closed) or a grey-level Otsu alternative."""
    ch = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 2] if kind == "bstar" else cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    ch = cv2.GaussianBlur(ch, (5, 5), 0)
    _, fg = cv2.threshold(ch, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    return cv2.morphologyEx(cv2.morphologyEx(fg, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k) > 0


def classical_predict(rgb):
    """segment_multi as deployed: components of the b* foreground; count = sum of n_est (area / median seed)."""
    inst, scale = segment(rgb)
    assert scale == 1.0  # harvest images are 1280 px, below segment_multi.WORK_PX, so no resize
    n, lab = cv2.connectedComponents(classical_fg(rgb, "bstar").astype(np.uint8), connectivity=8)
    ms = masks_from_labels(lab)
    a = np.array([m.area for m in ms], float)
    if len(a):  # same component filter as segment_multi.segment
        big = a[a > 0.2 * np.median(a)]
        unit = float(np.median(big)) if len(big) else float(np.median(a))
        ms = [m for m in ms if m.area >= 0.3 * unit]
    assert len(ms) == len(inst)
    return ms, np.ones(len(ms)), int(sum(i["n_est"] for i in inst))


def watershed_predict(rgb, fg, md, r_seed):
    from skimage.feature import peak_local_max
    from skimage.segmentation import watershed
    f = classical_fg(rgb, fg)
    dist = ndi.distance_transform_edt(f)
    pk = peak_local_max(dist, min_distance=max(3, int(md * r_seed)), threshold_abs=0.3 * r_seed, labels=f.astype(int),
                        exclude_border=False)
    mk = np.zeros(f.shape, np.int32)
    mk[tuple(pk.T)] = np.arange(1, len(pk) + 1)
    ms = masks_from_labels(watershed(-dist, mk, mask=f))
    return ms, np.ones(len(ms))


# --------------------------------------------------------------------------- per-image summaries
def mean_lightness(ms: list[Mask], rgb: np.ndarray) -> np.ndarray:
    """Mean Lab L* per mask: gaps between packed seeds are dark, seeds are light."""
    light = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(float)
    out = []
    for m in ms:
        y0, x0, y1, x1 = m.box
        out.append(light[y0:y1, x0:x1][m.m].mean())
    return np.array(out)


def summarise(ms: list[Mask], scores, L: np.ndarray, secs: float, extra=None, rgb=None) -> dict:
    """Everything post-processing and matching need, so masks need not be kept for the sweep."""
    n = len(ms)
    areas = np.array([m.area for m in ms], float)
    light = mean_lightness(ms, rgb) if rgb is not None else np.ones(n)
    n_gt = int(L.max())
    ig = np.zeros((n, n_gt))
    for i, m in enumerate(ms):
        y0, x0, y1, x1 = m.box
        bc = np.bincount(L[y0:y1, x0:x1][m.m], minlength=n_gt + 1)
        ig[i] = bc[1:n_gt + 1]
    ipp = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            ipp[i, j] = ipp[j, i] = inter(ms[i], ms[j])
    return {"areas": areas, "scores": np.asarray(scores, float), "ig": ig, "ipp": ipp, "light": light,
            "gt_areas": np.bincount(L.ravel(), minlength=n_gt + 1)[1:].astype(float), "secs": secs,
            "img_area": float(L.size), **(extra or {})}


def run_method(method: str, stems: list[str], gt: dict, r_seed: float) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    if method == "fastsam":
        model, configs = fastsam_model(), FASTSAM_RAW
    elif method == "cellpose":
        from cellpose import models
        model, configs = models.CellposeModel(gpu=False), CELLPOSE_RAW
    elif method == "classical":
        model, configs = None, {"classical": {}}
    else:
        model, configs = None, WATERSHED_RAW
    for name, cfg in configs.items():
        path = CACHE / f"{name}.pkl"
        if model is not None and not path.exists():  # warm-up so the first image's time excludes lazy init
            predict_masks(method, cfg, load_rgb(str(image_path(stems[0]))), model, r_seed)
        if path.exists():
            print(f"{name}: cached", flush=True)
            continue
        res = {}
        for s in stems:
            rgb = load_rgb(str(image_path(s)))
            t = time.perf_counter()
            extra = None
            if method == "fastsam":
                ms, sc = fastsam_predict(model, rgb, **cfg)
            elif method == "cellpose":
                ms, sc = cellpose_predict(model, rgb, **cfg)
            elif method == "classical":
                ms, sc, n_est = classical_predict(rgb)
                extra = {"n_est": n_est}
            else:
                ms, sc = watershed_predict(rgb, cfg["fg"], cfg["md"], r_seed)
            secs = time.perf_counter() - t
            res[s] = summarise(ms, sc, gt[s][0], secs, extra, rgb)
            print(f"{name} {s}: {len(ms)} masks, {secs:.2f} s", flush=True)
        pickle.dump(res, path.open("wb"))


# --------------------------------------------------------------------------- post-processing and matching
def postprocess(d: dict, conf=0.0, a_lo=0.0, a_hi=np.inf, dedup_iou=1.0, contain=1.0, jp=False, sheet=True,
                light=0.0) -> np.ndarray:
    """Indices of kept masks: drop sheet masks, low conf, area outside [a_lo, a_hi] x median, masks darker than
    light x the median mask L* (gaps between seeds), then greedy de-dup by score (IoU above dedup_iou or
    intersection / smaller area above contain). jp=True replays JP's filter."""
    a, s, ipp = d["areas"], d["scores"], d["ipp"]
    idx = np.arange(len(a))
    if jp:  # 300 <= area <= 3 % of the 1024-px image (in its pixels), then IoU > .5 de-dup in model order
        k = (1024 / 1280) ** 2
        idx = idx[(a * k >= 300) & (a <= 0.03 * d["img_area"])]
        a_lo, a_hi, dedup_iou, contain = 0, np.inf, 0.5, 1.0
    else:
        idx = idx[((a <= SHEET_FRAC * d["img_area"]) | (not sheet)) & (s >= conf)]
        if len(idx):
            med = np.median(a[idx])
            idx = idx[(a[idx] >= a_lo * med) & (a[idx] <= a_hi * med)]
        if len(idx) and light:
            lt = d.get("light", np.ones(len(a)))
            idx = idx[lt[idx] >= light * np.median(lt[idx])]
        idx = idx[np.argsort(-s[idx], kind="stable")]
    kept = []
    for i in idx:
        ok = True
        for j in kept:
            it = ipp[i, j]
            if it and (it / (a[i] + a[j] - it) > dedup_iou or it / min(a[i], a[j]) > contain):
                ok = False
                break
        if ok:
            kept.append(i)
    return np.array(kept, int)


def postprocess_masks(ms: list[Mask], scores, rgb: np.ndarray, post: dict) -> np.ndarray:
    """postprocess() on masks of a new image (no GT): builds the summary it needs. Also used by the demo bulk mode."""
    n = len(ms)
    ipp = np.zeros((n, n))
    if n:
        b = np.array([m.box for m in ms])  # only pairs whose boxes overlap can intersect
        ov = ((b[:, None, 0] < b[None, :, 2]) & (b[None, :, 0] < b[:, None, 2]) &
              (b[:, None, 1] < b[None, :, 3]) & (b[None, :, 1] < b[:, None, 3]))
        for i, j in zip(*np.nonzero(np.triu(ov, 1))):
            ipp[i, j] = ipp[j, i] = inter(ms[i], ms[j])
    d = {"areas": np.array([m.area for m in ms], float), "scores": np.asarray(scores, float), "ipp": ipp,
         "light": mean_lightness(ms, rgb), "img_area": float(rgb.shape[0] * rgb.shape[1])}
    return postprocess(d, **post)


def match(d: dict, kept: np.ndarray) -> list[tuple[int, int, float]]:
    """Greedy one-to-one matching at IoU >= 0.5: (pred index, gt index, IoU)."""
    if not len(kept) or not d["ig"].shape[1]:
        return []
    it = d["ig"][kept]
    iou = it / (d["areas"][kept][:, None] + d["gt_areas"][None] - it)
    pairs = np.argwhere(iou >= IOU_MATCH)
    order = np.argsort(-iou[pairs[:, 0], pairs[:, 1]])
    up, ug, out = set(), set(), []
    for p, g in pairs[order]:
        if p not in up and g not in ug:
            up.add(p), ug.add(g)
            out.append((int(kept[p]), int(g), float(iou[p, g])))
    return out


def image_metrics(d: dict, kept: np.ndarray, classes: np.ndarray, count=None) -> dict:
    m = match(d, kept)
    n_pred = int(count if count is not None else len(kept))
    n_gt, n_seed = len(classes), int(np.isin(classes, ["crushed", "intact"]).sum())
    tp = len(m)
    hit = np.zeros(n_gt, bool)
    hit[[g for _, g, _ in m]] = True
    row = {"n_gt": n_gt, "n_gt_seeds": n_seed, "n_pred": n_pred, "n_masks": len(kept), "tp": tp,
           "fp": len(kept) - tp, "fn": n_gt - tp, "count_err": n_pred - n_gt,
           "ape_all": 100 * abs(n_pred - n_gt) / n_gt, "ape_seeds": 100 * abs(n_pred - n_seed) / n_seed,
           "sum_iou": sum(i for *_, i in m), "secs": d["secs"]}
    for c in ["crushed", "intact", "impurity"]:
        row[f"gt_{c}"], row[f"hit_{c}"] = int((classes == c).sum()), int(hit[classes == c].sum())
    return row


def aggregate(df: pd.DataFrame) -> dict:
    tp, fp, fn = df.tp.sum(), df.fp.sum(), df.fn.sum()
    p, r = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
    out = {"mape_all": df.ape_all.mean(), "mape_seeds": df.ape_seeds.mean(), "mae_count": df.count_err.abs().mean(),
           "mean_signed_count_err": df.count_err.mean(), "precision": p, "recall": r,
           "f1": 2 * p * r / max(p + r, 1e-9), "mean_iou_matched": df.sum_iou.sum() / max(tp, 1),
           "secs_per_image": df.secs.mean()}
    for c in ["crushed", "intact", "impurity"]:
        out[f"recall_{c}"] = df[f"hit_{c}"].sum() / max(df[f"gt_{c}"].sum(), 1)
    return out


def boot(df: pd.DataFrame, keys=("mape_all", "mape_seeds", "precision", "recall", "f1", "mean_iou_matched",
                                  "recall_crushed", "recall_intact", "recall_impurity")) -> dict:
    point = aggregate(df)
    rng = np.random.default_rng(SEED)
    draws = [aggregate(df.iloc[rng.integers(0, len(df), len(df))]) for _ in range(N_BOOT)]
    out = {k: round(float(v), 4) for k, v in point.items()}
    for k in keys:
        lo, hi_ = np.percentile([d[k] for d in draws], [2.5, 97.5])
        out[f"{k}_ci95"] = [round(float(lo), 4), round(float(hi_), 4)]
    return out | {"n_images": len(df)}


POST_GRID = [dict(a_lo=lo, a_hi=hi_, dedup_iou=0.5, contain=ct, light=lt) for lo, hi_, ct, lt in
             itertools.product([0.0, 0.2], [np.inf, 4.0], [1.0, 0.8], [0.0, 0.6, 0.75, 0.85])]
CONF_GRID = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]


def candidates(raw_name: str):
    """(post-processing params) to sweep for a raw config."""
    if raw_name == "fs_jp":
        return [dict(jp=True)]
    if raw_name == "classical":
        return [dict(sheet=False)]  # segment_multi as deployed: every component kept, count = sum of n_est
    confs = CONF_GRID if raw_name.startswith("fs_") else [0.0]
    return [dict(conf=c, **p) for c in confs for p in POST_GRID]


def evaluate(raw: dict, post: dict, stems, gt, raw_name) -> pd.DataFrame:
    rows = []
    for s in stems:
        d = raw[s]
        kept = postprocess(d, **post)
        rows.append({"stem": s} | image_metrics(d, kept, gt[s][1], d.get("n_est")))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- boundary F, overlays, ghana
def boundary_f(a: np.ndarray, b: np.ndarray, tol=BF_TOL) -> float:
    k = np.ones((3, 3), np.uint8)
    ba = a & ~cv2.erode(a.astype(np.uint8), k).astype(bool)
    bb = b & ~cv2.erode(b.astype(np.uint8), k).astype(bool)
    kt = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * tol + 1, 2 * tol + 1))
    da, db = cv2.dilate(ba.astype(np.uint8), kt) > 0, cv2.dilate(bb.astype(np.uint8), kt) > 0
    p = (ba & db).sum() / max(ba.sum(), 1)
    r = (bb & da).sum() / max(bb.sum(), 1)
    return float(2 * p * r / max(p + r, 1e-9))


def predict_masks(method, cfg, rgb, model, r_seed):
    """(masks, scores) for one image."""
    if method == "fastsam":
        return fastsam_predict(model, rgb, **cfg)
    if method == "cellpose":
        return cellpose_predict(model, rgb, **cfg)
    if method == "classical":
        return classical_predict(rgb)[:2]
    return watershed_predict(rgb, cfg["fg"], cfg["md"], r_seed)


def method_of(raw_name):
    return {"fs": "fastsam", "cp": "cellpose", "ws": "watershed"}.get(raw_name[:2], "classical")


def raw_cfg(raw_name):
    return {**FASTSAM_RAW, **CELLPOSE_RAW, **WATERSHED_RAW}.get(raw_name, {})


def overlay(rgb, L, classes, ms, kept, matches, title, path):
    """Left: GT instances by class. Right: predictions, green matched, red unmatched; missed GT outlined yellow."""
    col = {"crushed": (255, 60, 60), "intact": (60, 220, 60), "impurity": (60, 140, 255)}
    left, right = rgb.copy(), rgb.copy()
    for g, c in enumerate(classes, 1):
        cs, _ = cv2.findContours((L == g).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(left, cs, -1, col[c], 3)
    mp = {p for p, _, _ in matches}
    mg = {g for _, g, _ in matches}
    for i in kept:
        m = ms[i].full(L.shape).astype(np.uint8)
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(right, cs, -1, (60, 220, 60) if i in mp else (255, 40, 40), 3)
    for g in range(len(classes)):
        if g not in mg:
            cs, _ = cv2.findContours((L == g + 1).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(right, cs, -1, (255, 230, 0), 2, lineType=cv2.LINE_AA)
    both = np.concatenate([left, np.full((L.shape[0], 12, 3), 255, np.uint8), right], 1)
    cv2.putText(both, "GT: red crushed, green intact, blue impurity", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 4)
    cv2.putText(both, title, (L.shape[1] + 32, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 4)
    im = Image.fromarray(both)
    im.thumbnail((2000, 2000))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, quality=85)


def ghana(raw_name, post, model, r_seed, overlay_dir) -> pd.DataFrame:
    ex = {e["id"]: e for e in json.loads((ROOT / "demo" / "api" / "examples" / "examples.json").read_text())}
    photos = pd.read_csv(ROOT / "data" / "splits" / "ghana_photos.csv").set_index("photo")
    rows = []
    for eid in GHANA:
        p = photos.loc[ex[eid]["source"]]
        rgb = load_rgb(str(ROOT / "demo" / "api" / "examples" / f"{eid}.jpg"))
        t = time.perf_counter()
        ms, scores = predict_masks(method_of(raw_name), raw_cfg(raw_name), rgb, model, r_seed)
        secs = time.perf_counter() - t
        n = len(ms)
        kept = postprocess_masks(ms, scores, rgb, post)
        inst, _ = segment(rgb)
        rows.append({"example": eid, "photo": ex[eid]["source"], "gt_status": p["gt_status"],
                     "published_count": int(p["n_seeds_gt"]), "semi_auto_estimate": int(p["n_seeds_est"]),
                     "segment_multi": int(sum(i["n_est"] for i in inst)), "bulk_method": len(kept),
                     "bulk_raw_masks": n, "bulk_secs": round(secs, 2)})
        if overlay_dir:
            out = rgb.copy()
            for i in kept:
                cs, _ = cv2.findContours(ms[i].full(rgb.shape[:2]).astype(np.uint8), cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(out, cs, -1, (255, 40, 40), 4)
            im = Image.fromarray(out)
            im.thumbnail((1400, 1400))
            im.save(Path(overlay_dir) / f"ghana_{eid}_{raw_name}.jpg", quality=80)
        print(rows[-1], flush=True)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- report
def seed_radius(o: pd.DataFrame) -> float:
    seeds = pd.read_csv(ROOT / "data" / "splits" / "harvest_seeds.csv")
    tr = seeds[seeds["image"].isin(o[o.split == "train"]["image"]) & (seeds["class"] == "intact")]
    return float(np.sqrt(tr.area_px.median() / np.pi))


def report(overlay_dir: str | None) -> None:
    o = originals()
    stems = [Path(p).stem for p in o.image]
    split = dict(zip(stems, o.split))
    train = [s for s in stems if split[s] == "train"]
    test = [s for s in stems if split[s] == "test"]
    gt = load_gt(stems)
    r_seed = seed_radius(o)
    # 1) pick post-processing per raw config on train (max pooled F1, ties -> lower MAPE), then the best per method
    sweep = []
    raws = {p.stem: pickle.load(p.open("rb")) for p in sorted(CACHE.glob("*.pkl"))}
    for name, raw in raws.items():
        for post in candidates(name):
            a = aggregate(evaluate(raw, post, train, gt, name))
            sweep.append({"raw": name, "method": method_of(name), "post": json.dumps(post, default=str),
                          **{f"train_{k}": v for k, v in a.items()}})
    sw = pd.DataFrame(sweep).sort_values(["train_f1", "train_mape_all"], ascending=[False, True])
    best = sw.groupby("method", sort=False).head(1)
    best_per_raw = sw.groupby("raw", sort=False).head(1)
    print(best_per_raw[["raw", "post", "train_f1", "train_mape_all", "train_secs_per_image"]].to_string(), flush=True)
    result = {"protocol": {}, "methods": {}, "jp_fastsam_settings": {}, "per_raw_config_train": [], "ghana": {}}
    images = []
    for r in best.itertuples():
        post = json.loads(r.post)
        post = {k: (np.inf if v == "inf" else v) for k, v in post.items()}
        df = evaluate(raws[r.raw], post, stems, gt, r.raw).assign(method=r.method, config=r.raw,
                                                                    split=lambda x: x.stem.map(split))
        images.append(df)
        result["methods"][r.method] = {"raw_config": r.raw, "raw_settings": raw_cfg(r.raw), "post": r.post,
                                       "test_6": boot(df[df.split == "test"]), "all_40": boot(df),
                                       "train_28": boot(df[df.split == "train"])}
    # JP's exact FastSAM settings, reported for reference (not selected)
    if "fs_jp" in raws:
        df = evaluate(raws["fs_jp"], dict(jp=True), stems, gt, "fs_jp").assign(split=lambda x: x.stem.map(split))
        result["jp_fastsam_settings"] = {"test_6": boot(df[df.split == "test"]), "all_40": boot(df)}
    result["per_raw_config_train"] = best_per_raw[["raw", "post", "train_f1", "train_mape_all",
                                                   "train_secs_per_image"]].round(4).to_dict("records")
    winner = max(result["methods"], key=lambda m: result["methods"][m]["train_28"]["f1"])
    wr = result["methods"][winner]
    post = {k: (np.inf if v == "inf" else v) for k, v in json.loads(wr["post"]).items()}
    model = fastsam_model() if winner == "fastsam" else None
    if winner == "cellpose":
        from cellpose import models
        model = models.CellposeModel(gpu=False)
    # boundary F on the winner's matched pairs (test images and all 40), needs the masks again
    bf = {}
    for s in stems:
        rgb = load_rgb(str(image_path(s)))
        ms, sc = predict_masks(winner, wr["raw_settings"], rgb, model, r_seed)
        d = raws[wr["raw_config"]][s]
        if len(ms) != len(d["areas"]):  # re-run differs from the cache: summarise this run instead
            print(f"warning: {s} re-run gave {len(ms)} masks vs {len(d['areas'])} cached", flush=True)
            d = summarise(ms, sc, gt[s][0], d["secs"], rgb=rgb)
        kept = postprocess(d, **post)
        m = match(d, kept)
        L, cls = gt[s]
        bf[s] = [boundary_f(ms[p].full(L.shape), L == g + 1) for p, g, _ in m]
        if overlay_dir and s in test[:3]:
            overlay(rgb, L, cls, ms, kept, m, f"{winner}: {len(kept)} pred vs {len(cls)} GT",
                    Path(overlay_dir) / f"harvest_{s}_{winner}.jpg")
    for k, ss in [("test_6", test), ("all_40", stems)]:
        wr[k]["boundary_f_matched_tol3px"] = round(float(np.mean([v for s in ss for v in bf[s]])), 4)
    # segment_multi overlay for contrast on one test image
    if overlay_dir and "classical" in result["methods"]:
        s = test[0]
        rgb = load_rgb(str(image_path(s)))
        ms = classical_predict(rgb)[0]
        d = raws["classical"][s]
        kept = postprocess(d, sheet=False)
        overlay(rgb, *gt[s], ms, kept, match(d, kept), f"segment_multi: {len(kept)} components",
                Path(overlay_dir) / f"harvest_{s}_segment_multi.jpg")
    gh = ghana(wr["raw_config"], post, model, r_seed, overlay_dir)
    result["ghana"] = {"method": winner, "photos": gh.to_dict("records")}
    t6 = wr["test_6"]
    result["decision"] = {"rule": "add bulk mode only if count MAPE <= 5 % and instance F1 >= 0.85 on the 6 test originals",
                          "best_method": winner, "test_mape_all": t6["mape_all"], "test_f1": t6["f1"],
                          "passes": bool(t6["mape_all"] <= 5 and t6["f1"] >= 0.85)}
    result["protocol"] = {"gt": "hwdtghttp7 originals, instances rebuilt as harvest_index.instances (checked vs harvest_seeds.csv)",
                          "n_train": len(train), "n_test": len(test), "n_all": len(stems),
                          "selection": "post-processing (and raw config) chosen by pooled instance F1 on the 28 train originals",
                          "match": "greedy one-to-one at IoU >= 0.5", "bootstrap": f"{N_BOOT} resamples of images",
                          "seed_radius_px_train_median": round(r_seed, 1)}
    how = ("Zero-shot instance segmentation of packed soybeans on the 40 original images (aug 01) of Mechanical-harvest "
           "soybean hwdtghttp7. GT instances: palette-snapped class masks, 4-connected components per class, specks "
           "< 5 % of the median intact seed dropped, merged crushed/intact components split by distance watershed "
           "(pipeline/harvest_index.py rules, counts checked against harvest_seeds.csv). Methods: FastSAM-s "
           "(Ultralytics 8.4.194, weights v8.3.0 SHA-256 c9f78716..., CPU), Cellpose-SAM (cellpose 4.2.1.1, cpsam), "
           "segment_multi (Lab b* Otsu components, count = sum of area/median-seed estimates) and a distance-transform "
           "watershed on its foreground. Raw configs (FastSAM imgsz 640/1024/1280, retina on/off, NMS IoU .7/.9; "
           "Cellpose diameter auto/130, half resolution; watershed foreground and peak distance) and post-processing "
           "(conf threshold, drop masks > 25 % of the image, area band relative to the image's median mask, drop masks "
           "darker than a fraction of the median mask L* (gaps between seeds), greedy de-dup by IoU and containment) chosen by pooled F1 on the 28 train originals only; headline on the 6 test "
           "originals, secondary on all 40 (no method saw any of them). Matching: greedy one-to-one at IoU >= 0.5. "
           "Count error = number of kept masks (segment_multi: sum of n_est) minus GT instances (all classes; seeds "
           "only = crushed + intact). Boundary F with 3 px tolerance on matched pairs. 95 % CIs: percentile bootstrap "
           "over images. Seconds per image: model inference + post-processing, model loaded, OMP_NUM_THREADS=6 on a "
           "c7i.4xlarge shared with another job. The winner (by train F1) is also run on the 3 Ghana demo photos.")
    write_result("bulk_segmentation", result, how,
                 {"images": pd.concat(images).round(4), "configs": sw.round(4), "ghana": gh})


def latency(raw_name: str) -> None:
    """Fresh-process latency and peak RSS of one config on the 6 test originals (what the demo would see)."""
    t0 = time.perf_counter()
    method = method_of(raw_name)
    if method == "fastsam":
        model = fastsam_model()
    elif method == "cellpose":
        from cellpose import models
        model = models.CellposeModel(gpu=False)
    else:
        model = None
    load_s = time.perf_counter() - t0
    o = originals()
    secs = []
    for s in [Path(p).stem for p in o[o.split == "test"].image]:
        rgb = load_rgb(str(image_path(s)))
        t = time.perf_counter()
        predict_masks(method, raw_cfg(raw_name), rgb, model, 60.0)  # r_seed only used by watershed
        secs.append(time.perf_counter() - t)
    print(json.dumps({"config": raw_name, "model_load_s": round(load_s, 2), "secs_per_image": [round(x, 2) for x in secs],
                      "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("predict")
    p.add_argument("--method", choices=["fastsam", "cellpose", "classical", "watershed"], required=True)
    p.add_argument("--only", nargs="*", help="raw config names to run (default all for the method)")
    r = sub.add_parser("report")
    r.add_argument("--overlays")
    la = sub.add_parser("latency")
    la.add_argument("--config", required=True)
    a = ap.parse_args()
    if a.cmd == "predict":
        o = originals()
        stems = [Path(x).stem for x in o.image]
        if a.only:
            for d in (FASTSAM_RAW, CELLPOSE_RAW, WATERSHED_RAW):
                for k in list(d):
                    if k not in a.only:
                        d.pop(k)
        run_method(a.method, stems, load_gt(stems), seed_radius(o))
    elif a.cmd == "report":
        report(a.overlays)
    else:
        latency(a.config)
