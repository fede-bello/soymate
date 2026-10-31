# SoyMate demo API (contract between `app/api` and `app/web`)

Served by FastAPI under `/api`; the built React app is served at `/` by the same origin (nginx on the box),
so the frontend calls relative URLs (`/api/...`). All coordinates are pixels of the uploaded image after EXIF
orientation is applied. All percentages are 0-100.

## `GET /api/health`
`{"status": "ok", "model": "<model name>", "version": "<git rev or date>"}`

## `POST /api/analyze` (multipart/form-data)
Fields:
- `file`: JPEG/PNG, up to 15 MB.
- `mode`: `auto` (default) | `single` | `batch`. `auto` picks `single` when one dominant seed is found.
- `threshold_pct`: float, default `5`. Illustrative decision threshold on the defect share.
- `defect`: `any` (default; every class except `sound`) or one class name.

Response 200:
```json
{
  "mode": "batch",
  "image": {"width": 3183, "height": 2037},
  "model": {
    "name": "soymate-pooled-v1",
    "classes": ["sound", "broken", "stained", "immature", "insect_hole", "impurity"],
    "trained_on": ["soybean d97rjyk2tz", "soybean Lin v6vzvfszj6", "harvest hwdtghttp7"],
    "warnings": ["Classes come from different datasets; on photos from a new camera setup the class shares are uncalibrated (dataset-ID check: 100 %)."]
  },
  "seeds": [
    {"id": 1, "bbox": [x1, y1, x2, y2], "polygon": [[x, y], "..."], "n_est": 1,
     "class": "sound", "confidence": 0.93, "probs": {"sound": 0.93, "broken": 0.04, "...": 0.0}}
  ],
  "summary": {
    "n_seeds": 164,
    "classes": {"sound": {"n": 150, "pct": 91.5, "ci95": [86.2, 94.8]}, "...": {}},
    "defect": {"label": "any defect", "n": 14, "pct": 8.5, "ci95": [5.2, 13.8]}
  },
  "verdict": {
    "threshold_pct": 5.0,
    "status": "pass | fail | inconclusive",
    "seeds_needed": 420,
    "explanation": "The 95 % interval (5.2-13.8 %) is above 5 %: fail."
  },
  "timing_ms": {"segment": 40, "classify": 3100, "total": 3200}
}
```
- `seeds[].n_est` > 1 means a blob counted as several touching seeds (classified once, counted n_est times).
- `seeds_needed`: total seeds needed for the Wilson interval at the observed share to exclude the threshold
  (null when already decided or when the share equals the threshold).
- Errors: 400 `{"detail": "..."}` (no seed found, bad file), 413 too large.

## `GET /api/examples`
`[{"id": "ghana_g17", "label": "Ghana farmer-saved lot (164 seeds)", "kind": "batch|single",
   "dataset": "Ghana t94nzy4ptz (CC BY 4.0)", "url": "/api/examples/files/ghana_g17.jpg",
   "note": "Held-out photo; hand count available", "ground_truth": {"n_seeds": 164} }]`
Only test-split or evaluation-only images, never training images.

## `GET /api/evidence`
Curated from `results/*.json` (numbers copied by code, never typed by hand):
`{"cards": [{"id": "r1", "title": "...", "headline": "...", "numbers": [{"label": "...", "value": "0.852",
"ci95": "[0.801, 0.900]"}], "caveat": "...", "source": "results/r1_leaky_vs_clean.json"}], "provenance_url": "..."}`
