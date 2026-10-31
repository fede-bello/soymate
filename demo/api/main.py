"""SoyMate demo API (contract: demo/API.md).

Run on the box:  cd ~/soymate-next && uv run uvicorn demo.api.main:app --host 127.0.0.1 --port 8000
"""
import json
import os
import threading
from datetime import date
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from demo.api import evidence
from demo.api.pipeline import MODEL_NAME, Pipeline, analyze

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE / "examples"
MAX_BYTES = 15 * 1024 * 1024
MODES = {"auto", "single", "batch", "bulk"}

pipe = Pipeline()
if os.environ.get("SOYMATE_BULK_WARM", "1") == "1":  # load FastSAM in the background so the first bulk call is fast
    def _warm_bulk():
        try:
            from demo.api import bulk
            bulk.warm()
            print("bulk: FastSAM loaded", flush=True)
        except Exception as e:  # bulk mode then fails per request with a 503; other modes are unaffected
            print(f"bulk: warm-up failed: {e!r}", flush=True)
    threading.Thread(target=_warm_bulk, daemon=True).start()
EVIDENCE = evidence.build()
VERSION = os.environ.get("SOYMATE_VERSION", date.today().isoformat())

app = FastAPI(title="SoyMate demo API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok", "model": MODEL_NAME, "version": VERSION}


@app.post("/api/analyze")
def analyze_endpoint(file: UploadFile = File(...), mode: str = Form("auto"), threshold_pct: float = Form(5.0),
                     defect: str = Form("any")):
    if mode not in MODES:
        raise HTTPException(400, f"mode must be one of {sorted(MODES)}")
    if defect != "any" and defect not in pipe.classes:
        raise HTTPException(400, f"defect must be 'any' or one of {pipe.classes}")
    if not 0 < threshold_pct < 100:
        raise HTTPException(400, "threshold_pct must be between 0 and 100")
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File larger than 15 MB.")
    try:
        return analyze(pipe, data, mode, threshold_pct, defect)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except (ImportError, AssertionError, FileNotFoundError) as e:
        if mode == "bulk":
            raise HTTPException(503, f"Bulk mode is not available on this server: {e}")
        raise
    except OSError:
        raise HTTPException(400, "Could not read the image (JPEG or PNG expected).")


@app.get("/api/examples")
def examples():
    p = EXAMPLES / "examples.json"
    items = json.loads(p.read_text()) if p.exists() else []
    for ex in items:  # gallery thumbnail from make_thumbs.py, when present; analysis still uses ex["url"]
        stem = Path(ex["url"].rsplit("/", 1)[-1]).stem
        if (EXAMPLES / f"{stem}.thumb.jpg").exists():
            ex["thumb_url"] = f"/api/examples/files/{stem}.thumb.jpg"
    return items


@app.get("/api/evidence")
def get_evidence():
    return EVIDENCE


EXAMPLES.mkdir(exist_ok=True)
app.mount("/api/examples/files", StaticFiles(directory=EXAMPLES), name="example_files")
