# demo/

The live SoyMate demo: upload a photo, get every seed outlined and classified, the share of each defect with a
Wilson interval, and a pass / take more photos / fail verdict. Live at **http://18.206.176.19**.

| Path | What |
|---|---|
| `api/` | FastAPI backend (`main.py`), seed finding and classification (`pipeline.py`), evidence cards built from `results/*.json` (`evidence.py`), example gallery (`examples/`, `build_examples.py`, `make_thumbs.py`), end-to-end smoke numbers (`smoke.py`) |
| `web/` | React + TypeScript + Vite frontend; see [`web/README.md`](web/README.md) (mock mode, dev proxy) |
| `API.md` | The contract between `api/` and `web/`: `/api/health`, `/api/analyze`, `/api/examples`, `/api/evidence` |
| `deploy/` | nginx site, systemd unit and `deploy.sh`; see [`deploy/README.md`](deploy/README.md) |

## How it fits together

`api/pipeline.py` crops seeds with `pipeline/make_crops.py` and `pipeline/segment_multi.py` (same masks as the
training crops), embeds them with dinov2-small, and classifies them with `data/models/soymate-pooled-v1.joblib`
(from `models/train_models.py`). On the box, nginx serves `web/dist` at `/` and proxies `/api/` to uvicorn on
127.0.0.1:8000 (systemd `soymate-api`, code in `~/soymate-next`).

## Run

```bash
# API (repo root; needs data/models/ and the cached dinov2-small weights)
uv run uvicorn demo.api.main:app --host 127.0.0.1 --port 8000
# web, against that API or with mock data
cd demo/web && npm install && npm run dev          # or: npm run dev:mock
cd demo/web && npm run build                       # production build to demo/web/dist
# smoke numbers to results/demo_smoke.json (on the box)
uv run python -m demo.api.smoke
# redeploy to the box (laptop, team AWS credentials)
AWS_PROFILE=soymate demo/deploy/deploy.sh
```

Quick check of a running API:

```bash
curl -s http://18.206.176.19/api/health
curl -s -F file=@demo/api/examples/ghana_g17.jpg -F mode=auto http://18.206.176.19/api/analyze | head -c 300
```

The examples are held-out or evaluation-only images (Ghana, test splits of d97rjyk2tz and Lin), picked by rule.
Class shares on photos from a new camera setup are uncalibrated (the model card carries that warning).
