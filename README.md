<p align="center">
  <img src="assets/logo.png" alt="SoyMate logo" width="260">
</p>

# SoyMate

**A seed grade from a phone photo, that the farmer can check too.** At grain intake, someone at the cooperative counts damaged seeds by eye, and that count sets what the farmer is paid. SoyMate finds every seed in a phone photo, classifies it (sound, broken, stained, immature, insect hole, impurity), and gives the share of each defect with a Wilson interval and a verdict: pass, take more photos, or fail. Proof of concept on soybean, business case on lentil: see [`CONTEXT.md` §0](CONTEXT.md#0-current-plan-31102026-during-the-event).

Project for **Hack the Fork Paris 2026** (AgroParisTech, Palaiseau, 30 October to 1 November 2026), **Track 3: Protein sovereignty, from French fields to the proteins of tomorrow**.

**Live demo: http://18.206.176.19** (upload a photo or pick an example; the "Trust" tab shows the evidence cards).

> **Single source of truth:** [`CONTEXT.md`](CONTEXT.md), starting with **§0 Current plan** (31/10), which supersedes the pre-event plan in §1, §5 and §8-§12. Every figure carries its source (`[S#]`) and a confidence tag.

## Why soybean first, lentil next

- **Soybean** is the only bean with public labelled photos of damaged seeds (~8,000). We found none for lentils, peas or faba beans. French food soy is real (45 kt/yr) but pays only 20 to 70 €/t more than feed, so it is where we build and test the method, not the business.
- **Lentil** is where the value is: ~550 €/t between food and feed outlets, and in 2025 French lentil truckloads averaged 24.4 % beetle-damaged seeds (1 % to 75 % between lots). Taking the tool there needs French lentil photos labelled by graders, calibration against the visual reference count, and a pilot with one cooperative.
- SoyMate does not remove damage: it makes the grade fast, consistent and visible to both sides. Full analysis: [`docs/soymate_viability_brief.pdf`](docs/soymate_viability_brief.pdf).

## Repository layout

| Path | What |
|---|---|
| [`pipeline/`](pipeline/README.md) | Data pipeline: download, leak-free grouped splits, masked seed crops, frozen DINOv2 features, training-free multi-seed segmenter |
| [`experiments/`](experiments/README.md) | Event results R1 to R4 and the dataset-ID check on a shared harness; teammate prototypes in `yolo_holes/`, `grain_counting/`, `fastsam/` |
| [`models/`](models/README.md) | Training of the pooled demo model `soymate-pooled-v1` |
| [`demo/`](demo/README.md) | Demo API (FastAPI), web app (React), API contract, deploy files (nginx, systemd, `deploy.sh`) |
| [`labelling/`](labelling/README.md) | Label Studio package for hand-labelled lot-level ground truth |
| [`results/`](results/README.md) | Every number computed at the event (JSON + CSV), with `provenance.md` |
| `tests/` | Unit tests for the grain counting and FastSAM prototypes |
| `notebooks/` | Soybean dataset review notebook |
| `research/` | Dataset audits and survey, viability research, adversarial critique |
| `docs/` | Viability brief (PDF), AWS box guide, prototype notes |
| `pitch/` | Pitch outline and slides |
| `scripts/aws/`, `scripts/docs/` | EC2 bootstrap, Session Manager connect and remote run; viability brief generator |
| `CONTEXT.md` | Plan, sources, datasets, prior resources to declare |
| `archive/`, `event/`, `assets/` | Earlier idea exploration, participant guide, logo |

`data/`, `runs/` and `outputs/` are git-ignored.

## Quickstart

Install [uv](https://docs.astral.sh/uv/), then `uv sync --locked` from the repository root (Python 3.12 to 3.14). Data and heavy jobs live on the team's EC2 box: connect and run commands as described in [`docs/aws_setup.md`](docs/aws_setup.md) (`scripts/aws/connect.sh` for a shell, `scripts/aws/run_remote.sh '<bash>'` for one command). On the box the current code is in `~/soymate-next`, whose `data/` points to `~/soymate/data`.

Reproduce everything, from the repo root on the box:

```bash
uv run python pipeline/download_datasets.py                      # raw datasets -> data/raw/
uv run python pipeline/make_splits.py                            # grouped splits -> data/splits/
uv run python pipeline/ghana_index.py && uv run python pipeline/harvest_index.py   # per-seed indexes
uv run python pipeline/make_crops.py                             # masked crops -> data/crops/
uv run python pipeline/features.py --full-soybean                # dinov2-small features -> data/features/
for e in r1_leaky_vs_clean r2_per_class dataset_id r3_transfer r4_ghana_counts r4_harvest_lots; do
  OMP_NUM_THREADS=4 uv run python experiments/$e.py               # results/<name>.json + CSV
done
uv run python models/train_models.py                             # data/models/soymate-pooled-v1.joblib
uv run uvicorn demo.api.main:app --host 127.0.0.1 --port 8000    # demo API (web: demo/web, deploy: demo/deploy)
```

Run the unit tests with `uv run --with pytest pytest tests -q`.

## Headline results

All numbers, CIs and caveats are in [`results/README.md`](results/README.md); sources per claim in [`results/provenance.md`](results/provenance.md). In short:

- **The public soybean defect dataset leaks:** 229/274 published test images (83.6 %) share an original photo with published train. Leakage inflates macro F1 by about 0.03 to 0.06 (R1).
- **Per-class F1 on clean grouped splits** (R2): soybean macro 0.83 [0.80, 0.85] and broken 0.67 [0.60, 0.74] (5-fold CV over 131 capture bursts; the fixed 19-burst test gave an optimistic 0.88), Lin macro 0.91 [0.88, 0.93]. Better FastSAM seed masks do not change this (paired CIs include 0). Holes vs sound on the only days with both classes give F1 0.975 [0.92, 0.99], and 0.96 when trained only on other sessions (7 hole bursts: indicative).
- **The model can recognise the source dataset** with 100 % accuracy, so per-class numbers are reported within each dataset and the pooled demo model is uncalibrated on new camera setups.
- **Another setup's data does not substitute for target labels** (R3): on Lin, 10 target labels per class beat ~1,000 pooled soybean images (0.89 vs 0.68).
- **Seed counts on real phone photos** (R4a): MAPE 1.1 % [0.2, 2.3] against the 7 complete published counts.
- **Lot-level % crushed** (R4b): MAE 1.5 pp [0.5, 3.0] on 6 held-out lots, but per-seed crushed F1 is only 0.48, so the demo shows the interval and says "inconclusive" when it straddles the threshold.

## Team and workstreams

Team: **Fede Bello**, **Juan Pedro Maestrone** and **Pedro Pertusso**.

Code workstreams in this repository (from the git history):

- **Data, evaluation and demo** (Fede Bello): `pipeline/`, `experiments/` (R1 to R4), `models/`, `demo/`, `labelling/`, `results/`, research and pitch.
- **YOLO hole baseline, grain counting and FastSAM prototypes** (Juan Pedro Maestrone): `experiments/yolo_holes/`, `experiments/grain_counting/`, `experiments/fastsam/`, `notebooks/`, `tests/`, and the notes in `docs/soybean_baseline_status.md`, `docs/grain_pipeline_mvp.md`, `docs/fastsam_grain_experiment.md`. Summary below.

### Soybean hole-only YOLO baseline (`experiments/yolo_holes/`)

Install the optional training dependencies with `uv sync --locked --group baseline`, then prepare the data with `uv run --group baseline python experiments/yolo_holes/prepare_soybean_holes.py`. It refuses to overwrite an existing `data/processed/soybean_hole/`, validates the manifest, source image mapping and retained labels, keeps every training variant, and picks one v2 file per original group for validation and test. Empty Hole labels are **candidate negatives**, not verified hole-free images. `data.yaml` holds a machine-specific absolute path: regenerate it after moving the repository.

Weights: `curl -fL -o data/weights/yolo11n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt` (SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`). Training (Ultralytics 8.4.194, PyTorch 2.15.0, Apple MPS; use `device=cpu` elsewhere; MPS is not bitwise reproducible):

```bash
mkdir -p runs/soybean_hole
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/yolo detect train model=data/weights/yolo11n.pt data=data/processed/soybean_hole/data.yaml epochs=8 imgsz=640 batch=8 device=mps workers=0 seed=42 project="$PWD/runs/soybean_hole" name=baseline exist_ok=False plots=True 2>&1 | tee runs/soybean_hole/baseline.log
```

On the 175 grouped validation images (124 annotated holes), the eight-epoch best checkpoint reported precision 0.823, recall 0.563, mAP@0.50 0.640 and mAP@0.50:0.95 0.427. These are validation results against labels known to miss and confuse holes, not test or French-pulse performance; background and date correlations may inflate them. The 40-epoch run and its review are in `docs/soybean_baseline_status.md`.

Review gallery of validation predictions (refresh without re-running inference, from the local prediction cache):

```bash
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/python experiments/yolo_holes/review_soybean_holes.py \
  --weights runs/soybean_hole/long40/weights/best.pt \
  --predictions runs/soybean_hole/validation_prediction_cache/predictions.jsonl \
  --output runs/soybean_hole/validation_review_comparison_v2 --refresh \
  --review-confidence 0.10 --match-iou 0.50 --sample-size 25 --seed 42
```

Open `review.html`, set a status and notes per image, and use **Export reviews as CSV** as a backup (browser storage is tied to the browser and the file path).

### Separated-grain counting and visible-hole prototype (`experiments/grain_counting/`, `experiments/fastsam/`)

Experimental, thresholds not calibrated on pea or lentil trays. Images need one species, separated whole grains, a uniform contrasting background and clear borders; touching grains may merge, so inspect the numbered silhouettes before trusting a count. Needs the `baseline` group and local checkpoints (git-ignored). Use a fresh output directory under `outputs/` for each run.

```bash
# threshold/contour segmentation + hole detector, HTML report with sample.json and per-grain CSVs
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/python experiments/grain_counting/analyze_grain_sample.py \
  path/to/photo.jpg --species pea --provenance natural --device auto --mode compare --output outputs/pea-development-01
# evaluate reports against hand-counted photos (manifest schema in docs/grain_pipeline_mvp.md)
.venv/bin/python experiments/grain_counting/evaluate_grain_samples.py path/to/manifest.json --mode crops --output outputs/pea-evaluation-01
# FastSAM masks and mapped hole candidates, with a review page
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/python experiments/fastsam/analyze_fastsam_grains.py \
  path/to/photo.jpg --output outputs/fastsam-demo/my-photo --compare-masked 0
```

The 0.40 flagging confidence and the default area and colour thresholds are development settings, not validated operating points. Candidate detections describe visible features only: the prototype cannot assess hidden infestation or food/feed suitability, and visible-hole accuracy on natural multi-grain samples has not been measured. The evaluator rejects physical-set IDs and identical image bytes shared across development and final sets, but cannot prove that differently named sets hold different grains. Details, capture protocol and limitations: [`docs/grain_pipeline_mvp.md`](docs/grain_pipeline_mvp.md), [`docs/fastsam_grain_experiment.md`](docs/fastsam_grain_experiment.md).

## Hackathon rules we follow

- No solution code, model, prototype, results or pitch deck before the event started. Everything up to the event was desk research and data exploration.
- Pre-existing resources (public datasets, pretrained models, the derived CSVs and analyses in `research/`) are declared at submission: [`CONTEXT.md` §14](CONTEXT.md) and [`results/provenance.md`](results/provenance.md).
- Data provenance is labelled as measured, sourced, assumed or synthetic.

## Data, licences and credits

Datasets are downloaded with `pipeline/download_datasets.py`, never committed. Full map, licences and links in [`CONTEXT.md` §6](CONTEXT.md).

| Dataset | Use | Licence |
|---|---|---|
| Soybean beetle damage (Mendeley d97rjyk2tz, Shinde et al.) | Insect holes, seed-coat cracks, sound seeds; audited and re-split | CC BY 4.0 |
| Soybean Seeds, 5 classes (Mendeley v6vzvfszj6, Lin et al.) | Broken, stained, immature, skin-damaged, intact | CC BY 4.0 |
| Ghana seed varieties, soybean part (Mendeley t94nzy4ptz) | Real multi-seed phone photos: seed counts (R4a), demo examples | CC BY 4.0 |
| Mechanical-harvest soybean (Mendeley hwdtghttp7) | Multi-seed images with intact / crushed / impurity masks (R4b, demo model) | CC BY 4.0 |
| Indonesian soybean varieties (Mendeley c733bjz4m3) | Multi-seed flatbed scans | CC BY 4.0 |
| GrainSet (Scientific Data 2023) | Broken and pest-damaged cereal kernels | CC BY 4.0 |
| Pea instances (Zenodo 21110940) | FastSAM and watershed comparisons (attribution required) | CC BY 4.0 |
| Radio_lentille (Terres Inovia, Hugging Face) | X-rays of bruchid-damaged French lentils (gated, not downloaded) | MIT |

Models and libraries: DINOv2 (`facebook/dinov2-small`, Meta, Apache 2.0) through Hugging Face Transformers; scikit-learn, statsmodels, OpenCV, FastAPI, React and Vite. The teammate prototypes use Ultralytics YOLO11 and FastSAM (AGPL-3.0: review before sharing them outside the team; SoyCult image rights are unresolved, see `docs/fastsam_grain_experiment.md`). The repository is private.
