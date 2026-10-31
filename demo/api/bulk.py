"""Experimental bulk mode: seeds packed edge to edge (harvester camera), found with FastSAM-s.

One implementation: masks and post-processing come from experiments/bulk_segmentation/bulk_segmentation.py
(fastsam_predict + postprocess_masks), with the raw config and post-processing chosen there on the 28 train
originals and read here from results/bulk_segmentation.json. Needs ultralytics (AGPL-3.0, dependency group
`baseline`) and data/models/FastSAM-s.pt (SHA-256 checked on load). The model is loaded once, on the first bulk
request or by warm() at startup.
"""
import json
import threading
from pathlib import Path

import numpy as np

from demo.api.pipeline import MODEL_DIR, ROOT, masked_crop, polygon

import bulk_segmentation.bulk_segmentation as bs  # noqa: E402  (experiments/ is on sys.path via pipeline)

WEIGHTS = MODEL_DIR / "FastSAM-s.pt"
RESULT = ROOT / "results" / "bulk_segmentation.json"

_model = None
_load_lock = threading.Lock()
_run_lock = threading.Lock()


def config() -> tuple[dict, dict, dict]:
    """(raw FastSAM settings, post-processing params, test_6 metrics) as selected in the benchmark."""
    fs = json.loads(RESULT.read_text())["result"]["methods"]["fastsam"]
    post = {k: (np.inf if v == "inf" else v) for k, v in json.loads(fs["post"]).items()}
    return dict(fs["raw_settings"]), post, fs["test_6"]


RAW, POST, TEST6 = config()
WARNING = (f"Experimental bulk mode: count error about {TEST6['mape_all']:.0f} % and per-seed match F1 "
           f"{TEST6['f1']:.2f} on held-out packed photos; only the top layer is visible.")
CAP_WARNING = (f"FastSAM returned its maximum of {bs.MAX_DET} raw masks on this photo, so seeds may be missed "
               "(undercount). Use a photo with fewer seeds or a closer crop.")


def model():
    global _model
    with _load_lock:
        if _model is None:
            _model = bs.fastsam_model(WEIGHTS)
    return _model


def warm() -> None:
    """Load the model and run it once on a blank image (call from a background thread at startup)."""
    m = model()
    with _run_lock:
        bs.fastsam_predict(m, np.full((640, 640, 3), 128, np.uint8), **RAW)


MAX_DET_HIGH = 1000  # second pass when the benchmark cap (bs.MAX_DET) is hit: photos with more than 300 seeds


def find_bulk(rgb: np.ndarray, s: float) -> tuple[list[dict], list[str]]:
    """Seeds in a packed photo: one masked crop and polygon per kept FastSAM mask, plus warnings.
    rgb is the processing image, s its scale relative to the original (as in pipeline.find_batch).
    Whole frame at the benchmark settings; when FastSAM hits its raw-mask cap (more than 300 seeds in view) it is
    re-run once with a higher cap. Tiling was tried and over-segments seeds (upsampled tiles split seeds in parts)."""
    m = model()
    with _run_lock:
        ms, scores = bs.fastsam_predict(m, rgb, **RAW)
        raised = len(ms) >= bs.MAX_DET
        if raised:
            ms, scores = bs.fastsam_predict(m, rgb, **RAW, max_det=MAX_DET_HIGH)
    kept = bs.postprocess_masks(ms, scores, rgb, POST) if ms else []
    warnings = [WARNING]
    if raised:
        warnings.append(f"More than {bs.MAX_DET} seeds in view: FastSAM was re-run with a cap of {MAX_DET_HIGH} masks, "
                        "a setting not covered by the benchmark numbers above.")
    if len(ms) >= MAX_DET_HIGH:
        warnings.append(CAP_WARNING.replace(str(bs.MAX_DET), str(MAX_DET_HIGH)))
    out = []
    for i in kept:
        mk = ms[i]
        y0, x0, y1, x1 = mk.box
        crop = masked_crop(rgb[y0:y1, x0:x1], mk.m.astype(np.uint8) * 255)
        out.append({"bbox": [int(x0 / s), int(y0 / s), int(np.ceil(x1 / s)), int(np.ceil(y1 / s))],
                    "polygon": polygon(mk.m, x0, y0, s), "n_est": 1, "crop": crop})
    return out, warnings


if __name__ == "__main__":  # quick check on one image: python -m demo.api.bulk <image>
    import sys
    import time

    from demo.api.pipeline import downscale, load_image
    rgb, s = downscale(load_image(Path(sys.argv[1]).read_bytes()))
    t = time.perf_counter()
    found, w = find_bulk(rgb, s)
    print(len(found), "seeds", f"{time.perf_counter() - t:.2f} s", w)
    if len(sys.argv) > 2:  # overlay of the kept outlines
        import cv2
        out = rgb.copy()
        for f in found:
            pts = (np.array(f["polygon"]) * s).astype(np.int32)
            cv2.polylines(out, [pts], True, (255, 40, 40), 2)
        cv2.imwrite(sys.argv[2], cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
