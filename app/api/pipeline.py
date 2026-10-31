"""Seed finding, crops and classification for the demo API (no web code here, so smoke tests can import it).

Crops are made exactly like the training crops (scripts/data/make_crops.py: seed_mask / masked_crop) and embedded
with the same frozen dinov2-small features as eval/features.py (CLS + mean patch token).
"""
import io
import json
import os
import sys
import threading
import time
from pathlib import Path

import cv2
import joblib
import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageOps
from transformers import AutoImageProcessor, AutoModel

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "scripts" / "data"))
from harness import wilson  # noqa: E402  (also needed to unpickle FrozenLogReg)
from make_crops import components, masked_crop, seed_mask  # noqa: E402
from segment_multi import WORK_PX, segment  # noqa: E402

MODEL_NAME = "soymate-pooled-v1"
MODEL_DIR = ROOT / "data" / "models"
DINO = "facebook/dinov2-small"
MAX_PX = 2000          # long side used for processing; coordinates are returned in original pixels
SINGLE_MAX_COMPS = 2   # auto mode: <= this many components ...
SINGLE_MIN_FRAC = 0.08  # ... and the largest covers more than this share of the image -> single
# (auto also picks single when one component is larger than BATCH_MAX_FRAC: a close-up of one seed)
SEEDS_NEEDED_CAP = 100000
BATCH_MAX_FRAC = 0.25   # batch mode: a component larger than this share of the image is background, not seeds
DATASET_LABELS = {"soybean_d97rjyk2tz": "soybean d97rjyk2tz", "lin_v6vzvfszj6": "soybean Lin v6vzvfszj6",
                  "harvest_hwdtghttp7": "harvest hwdtghttp7"}


class Pipeline:
    def __init__(self):
        torch.set_num_threads(os.cpu_count() or 4)
        self.clf = joblib.load(MODEL_DIR / f"{MODEL_NAME}.joblib")
        self.card = json.loads((MODEL_DIR / f"{MODEL_NAME}.json").read_text())
        self.classes = list(self.card["classes"])
        self.proc = AutoImageProcessor.from_pretrained(DINO)
        self.dino = AutoModel.from_pretrained(DINO).eval()
        self.lock = threading.Lock()
        self.classify([np.full((224, 224, 3), 128, np.uint8)])  # warm up

    def model_info(self) -> dict:
        return {"name": MODEL_NAME, "classes": self.classes, "trained_on": list(self.card["trained_on"]),
                "warnings": [self.card["warning"]]}

    @torch.inference_mode()
    def classify(self, crops: list[np.ndarray], batch: int = 64) -> np.ndarray:
        """Probabilities (n, len(classes)), columns ordered as self.classes."""
        feats = []
        with self.lock:
            for i in range(0, len(crops), batch):
                ims = [Image.fromarray(c) for c in crops[i:i + batch]]
                h = self.dino(**self.proc(images=ims, return_tensors="pt")).last_hidden_state
                feats.append(torch.cat([h[:, 0], h[:, 1:].mean(1)], dim=1).numpy())
        X = np.concatenate(feats).astype(np.float32)
        df = pd.DataFrame(X, columns=[f"f{j}" for j in range(X.shape[1])])
        p = self.clf.predict_proba(df)
        order = [list(self.clf.classes_).index(c) for c in self.classes]
        return p[:, order]


def load_image(data: bytes) -> np.ndarray:
    return np.asarray(ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB"))


def downscale(rgb: np.ndarray) -> tuple[np.ndarray, float]:
    s = MAX_PX / max(rgb.shape[:2])
    if s >= 1:
        return rgb, 1.0
    return cv2.resize(rgb, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), s


def polygon(mask: np.ndarray, ox: float, oy: float, scale: float, eps: float = 1.0) -> list[list[int]]:
    """Outer contour of a binary mask, simplified, mapped to original pixels: (pt + offset) / scale."""
    cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return []
    c = cv2.approxPolyDP(max(cnts, key=cv2.contourArea), eps, True)[:, 0, :]
    return [[int(round((x + ox) / scale)), int(round((y + oy) / scale))] for x, y in c]


def labels_like_segment(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[int], float]:
    """Same mask and component filter as segment_multi.segment, also returning the label image (work scale).
    Kept in sync by an assertion on the component count in find_batch()."""
    scale = WORK_PX / max(rgb.shape[:2])
    small = cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) if scale < 1 else rgb
    scale = min(scale, 1.0)
    b = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_RGB2LAB)[..., 2], (5, 5), 0)
    _, fg = cv2.threshold(b, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg = cv2.morphologyEx(cv2.morphologyEx(fg, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(fg, 8)
    areas = stats[1:, cv2.CC_STAT_AREA].astype(float)
    if not len(areas):
        return lab, stats, [], scale
    big = areas[areas > 0.2 * np.median(areas)]
    unit = float(np.median(big)) if len(big) else float(np.median(areas))
    kept = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 0.3 * unit]
    return lab, stats, kept, scale


def find_batch(rgb: np.ndarray, s: float, inst: list[dict] | None = None) -> list[dict]:
    """Seeds spread on a plain background (segment_multi), one masked crop and polygon per component.
    rgb is the processing image, s its scale relative to the original."""
    inst = segment(rgb)[0] if inst is None else inst
    lab, stats, kept, ws = labels_like_segment(rgb)
    assert len(kept) == len(inst), (len(kept), len(inst))
    h, w = rgb.shape[:2]
    out = []
    for i, it in zip(kept, inst):
        if it["area"] > BATCH_MAX_FRAC * h * w:
            continue
        x0, y0, bw, bh = stats[i, :4]
        sub = (lab[y0:y0 + bh, x0:x0 + bw] == i).astype(np.uint8)
        X0, Y0 = int(np.floor(x0 / ws)), int(np.floor(y0 / ws))
        X1, Y1 = min(w, int(np.ceil((x0 + bw) / ws))), min(h, int(np.ceil((y0 + bh) / ws)))
        local = cv2.resize(sub.astype(np.float32), (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_LINEAR) > 0.5
        if not local.any():
            continue
        crop = masked_crop(rgb[Y0:Y1, X0:X1], local.astype(np.uint8) * 255)
        x1, y1, x2, y2 = it["bbox"]
        out.append({"bbox": [int(x1 / s), int(y1 / s), int(np.ceil(x2 / s)), int(np.ceil(y2 / s))],
                    "polygon": polygon(sub, x0, y0, ws * s), "n_est": int(it["n_est"]), "crop": crop})
    return out


def find_single(rgb: np.ndarray, s: float) -> list[dict]:
    """One dominant seed (seed_mask, largest component), as for the training crops."""
    comps = components(seed_mask(rgb), min_area=int(0.01 * rgb.shape[0] * rgb.shape[1]))
    if not comps:
        return []
    m = comps[0]
    ys, xs = np.nonzero(m)
    return [{"bbox": [int(xs.min() / s), int(ys.min() / s), int(np.ceil((xs.max() + 1) / s)),
                      int(np.ceil((ys.max() + 1) / s))],
             "polygon": polygon(m > 0, 0, 0, s), "n_est": 1, "crop": masked_crop(rgb, m)}]


def pick_mode(rgb: np.ndarray) -> tuple[str, list[dict]]:
    inst = segment(rgb)[0]
    area = rgb.shape[0] * rgb.shape[1]
    big = max((i["area"] for i in inst), default=0)
    if (len(inst) <= SINGLE_MAX_COMPS and big > SINGLE_MIN_FRAC * area) or big > BATCH_MAX_FRAC * area:
        return "single", inst
    return "batch", inst


def seeds_needed(p: float, t: float) -> int | None:
    """Smallest total n where the Wilson interval at observed share p excludes threshold t (capped)."""
    if p == t:
        return None
    def excluded(n):
        lo, hi = wilson(p * n, n)
        return hi < t or lo > t
    if not excluded(SEEDS_NEEDED_CAP):
        return SEEDS_NEEDED_CAP
    lo, hi = 1, SEEDS_NEEDED_CAP
    while lo < hi:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if excluded(mid) else (mid + 1, hi)
    return lo


def summarize(seeds: list[dict], classes: list[str], defect: str, threshold_pct: float) -> tuple[dict, dict]:
    n = sum(sd["n_est"] for sd in seeds)
    def share(k):
        lo, hi = wilson(k, n)
        return {"n": int(k), "pct": round(100 * k / n, 1), "ci95": [round(100 * lo, 1), round(100 * hi, 1)]}
    counts = {c: sum(sd["n_est"] for sd in seeds if sd["class"] == c) for c in classes}
    bad = [c for c in classes if c != "sound"] if defect == "any" else [defect]
    k = sum(counts[c] for c in bad)
    d = share(k) | {"label": "any defect" if defect == "any" else defect.replace("_", " ")}
    t = threshold_pct / 100
    lo, hi = wilson(k, n)
    rng = f"{100 * lo:.1f}-{100 * hi:.1f} %"
    if hi < t:
        status, need, why = "pass", None, f"The 95 % interval ({rng}) is below {threshold_pct:g} %: pass."
    elif lo > t:
        status, need, why = "fail", None, f"The 95 % interval ({rng}) is above {threshold_pct:g} %: fail."
    else:
        status, need = "inconclusive", seeds_needed(k / n, t)
        why = f"The 95 % interval ({rng}) contains {threshold_pct:g} %: inconclusive."
        if need is not None:
            more = "at least " if need == SEEDS_NEEDED_CAP else "about "
            why += f" At the observed share, {more}{need} seeds in total would decide it."
    summary = {"n_seeds": int(n), "classes": {c: share(counts[c]) for c in classes}, "defect": d}
    verdict = {"threshold_pct": float(threshold_pct), "status": status, "seeds_needed": need, "explanation": why}
    return summary, verdict


def analyze(pipe: Pipeline, data: bytes, mode: str = "auto", threshold_pct: float = 5.0,
            defect: str = "any") -> dict:
    t0 = time.perf_counter()
    orig = load_image(data)
    rgb, s = downscale(orig)
    t1 = time.perf_counter()
    inst, auto = None, mode == "auto"
    if auto:
        mode, inst = pick_mode(rgb)
    found = find_single(rgb, s) if mode == "single" else find_batch(rgb, s, inst)
    if not found and auto and mode == "single":
        mode, found = "batch", find_batch(rgb, s, inst)
    if not found:
        raise ValueError("No seed found in the image.")
    t2 = time.perf_counter()
    probs = pipe.classify([f.pop("crop") for f in found])
    t3 = time.perf_counter()
    seeds = []
    for j, (f, p) in enumerate(zip(found, probs), 1):
        c = int(p.argmax())
        seeds.append({"id": j, **f, "class": pipe.classes[c], "confidence": round(float(p[c]), 3),
                      "probs": {k: round(float(v), 3) for k, v in zip(pipe.classes, p)}})
    summary, verdict = summarize(seeds, pipe.classes, defect, threshold_pct)
    return {"mode": mode, "image": {"width": int(orig.shape[1]), "height": int(orig.shape[0])},
            "model": pipe.model_info(), "seeds": seeds, "summary": summary, "verdict": verdict,
            "timing_ms": {"segment": round(1000 * (t2 - t1)), "classify": round(1000 * (t3 - t2)),
                          "total": round(1000 * (time.perf_counter() - t0))}}
