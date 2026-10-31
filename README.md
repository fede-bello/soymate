<p align="center">
  <img src="assets/logo.png" alt="SoyMate logo" width="260">
</p>

# SoyMate

**Phone-photo quality control for pulses at grain intake.** A grain collector's intake technician takes a photo of a sample of peas or lentils; SoyMate separates every grain, classifies it (sound, broken, insect-holed, stained, foreign material), estimates the share of each defect with a confidence interval, and says whether the lot meets the human-food criterion or goes to animal feed.

Project for **Hack the Fork Paris 2026** (AgroParisTech, Palaiseau, 30 October to 1 November 2026), **Track 3: Protein sovereignty, from French fields to the proteins of tomorrow**.

> **Single source of truth:** [`CONTEXT.md`](CONTEXT.md). Every figure in it carries its source (`[S#]`) and a confidence tag. If anything in this repo disagrees with it, `CONTEXT.md` wins.

---

## Why

- Whether a lot of pulses is sold for human food (better price) or animal feed is decided at intake, today by looking at and counting grains by hand.
- Bruchid damage and broken grains are the main reasons lots lose the human-food outlet. The figures, thresholds and their sources are in [`CONTEXT.md` §3](CONTEXT.md).
- Image-based grain analysis exists for cereals (for example Inarix in France), but we found no tool doing it for pulses.

## How

1. **Photo:** phone, plain matte background, 30 to 200 grains.
2. **Separate:** threshold and contours (a pretrained segmenter such as SAM if grains touch).
3. **Classify:** frozen pretrained features (DINOv2) plus a small linear classifier, trained on CPU.
4. **Decide:** percentage per class with a binomial interval, compared with the chosen threshold.

There is no public image dataset of damaged peas, lentils or faba beans. We train on the best open insect-damage dataset (soybean, which we audited and re-split because the published split leaks), plus cereal datasets, and **measure the transfer** to French peas and lentils with our own photos taken during the event. The transfer curve (no tuning vs 5, 10, 25, 50 labelled grains per class) is the core result. Soybean is only training data; the product and the demo are about French pulses for human food.

## Repository layout

```
.
├── README.md              this file
├── CONTEXT.md             single source of truth: problem, data, method, plan, pitch, sources
├── assets/logo.png
├── docs/
│   ├── soymate_team_plan.pdf     short plan for the team (flow, roles, schedule, checkpoints)
│   └── soymate_data_report.pdf   data report with plots
├── research/              pre-event data exploration for SoyMate (no models trained)
│   ├── README.md
│   ├── soybean_bruchid/   audit of the soybean pulse-beetle dataset + leak-free re-split CSV
│   ├── other_datasets/    survey of 16 seed and grain image datasets
│   └── context/           intake standards, soybean for food, competitors, photo protocol
├── event/                 Hack the Fork participant guide
└── archive/               earlier idea exploration (ideas 1 to 8), kept for reference
```

## Hackathon rules we follow

- No solution code, model, prototype, results or pitch deck before the event starts. Everything in this repo up to the event is desk research and data exploration; no model was trained.
- Pre-existing resources (public datasets, pretrained models, the derived CSVs and analyses in `research/`) are declared at submission. See [`CONTEXT.md` §14](CONTEXT.md).
- Data provenance is labelled as measured, sourced, assumed or synthetic.

## Data

Datasets are downloaded at the event, never committed (`data/` is git-ignored). The full dataset map, licences and download links are in [`CONTEXT.md` §6](CONTEXT.md). Main ones:

| Dataset | Use | Licence |
|---|---|---|
| Soybean pulse-beetle infestation (Mendeley d97rjyk2tz) | Insect exit-hole detection (proof of concept) | CC BY 4.0 |
| GrainSet (Scientific Data 2023) | Broken and pest-damaged kernels, expert labels | CC BY 4.0 |
| corn1000 (Hugging Face) | Counting grains in multi-grain phone photos | CC BY-NC 4.0 |
| Radio_lentille (Terres Inovia, Hugging Face) | X-rays of bruchid-damaged French lentils, validation | MIT |
| Our own photos | French peas and lentils, transfer evaluation | Ours |

## Dataset review setup

Install [uv](https://docs.astral.sh/uv/), then run `uv sync --locked` from the repository root (Python 3.14). Start JupyterLab with `uv run jupyter lab` and open `notebooks/01_soybean_data_review.ipynb` using the environment's Python 3 kernel. Extract the soybean dataset under `data/raw/Soybean_Seed_Dataset/` first. The local `.venv/` and data are ignored by Git.

## Team

Three people, Hack the Fork Paris 2026. Repository is private.

### Soybean hole-only baseline

Install the optional training dependencies with `uv sync --locked --group baseline`. Prepare the data with `uv run --group baseline python scripts/prepare_soybean_holes.py`. The script refuses to overwrite an existing `data/processed/soybean_hole/`; move an old output aside to rebuild. It validates the manifest, source image mapping and retained labels before writing. It retains every training variant and selects the lexicographically smallest retained v2 filename per original group for validation and test: v2 metadata does not identify an unaugmented original. Empty Hole labels are **candidate negatives**, not verified hole-free images. The output includes `selected_images.csv`, `counts.yaml`, `data.yaml` (with a machine-specific absolute path), and `prepared_examples.png`. Regenerate it after moving the repository. The raw dataset is unchanged; image filenames still reflect their published folders, not their new grouped split.

The following commands were run from the repository root with Ultralytics 8.4.194 and PyTorch 2.15.0 on Apple M5 Pro MPS. The seed does not guarantee bitwise reproducibility: PyTorch warned that some MPS operations are nondeterministic. For a machine without MPS, use `device=cpu`. Get the pretrained weights with:

```bash
mkdir -p data/weights
curl -fL -o data/weights/yolo11n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt
```

The downloaded file's SHA-256 was `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`. Training commands (the smoke test uses only 5% of training images; both validate only on the grouped validation split):

```bash
mkdir -p runs/soybean_hole
set -o pipefail
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/yolo detect train model=data/weights/yolo11n.pt data=data/processed/soybean_hole/data.yaml epochs=1 fraction=0.05 imgsz=640 batch=8 device=mps workers=0 seed=42 project=runs/soybean_hole name=smoke exist_ok=False plots=True 2>&1 | tee runs/soybean_hole/smoke.log
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/yolo detect train model=data/weights/yolo11n.pt data=data/processed/soybean_hole/data.yaml epochs=8 imgsz=640 batch=8 device=mps workers=0 seed=42 project="$PWD/runs/soybean_hole" name=baseline exist_ok=False plots=True 2>&1 | tee runs/soybean_hole/baseline.log
```

The smoke run's relative `project` path was resolved by Ultralytics under `runs/detect/runs/soybean_hole/smoke/`; the baseline is in `runs/soybean_hole/baseline/`. Each run saves `args.yaml`, `results.csv`, weights and validation plots, while the console logs are in `runs/soybean_hole/`. Data, weights and runs are Git-ignored. Do not interpret the validation metrics as test or French-pulse performance: missing and ambiguous boxes and background/date shortcuts remain concerns. The held-out grouped test set is not used by these commands.

The eight-epoch run took 289 seconds through its final epoch. On the 175 grouped validation images (124 annotated holes), the best checkpoint's reported precision was 0.823, recall 0.563, mAP@0.50 0.640 and mAP@0.50:0.95 0.427. These are validation results against the existing labels, not verified ground truth. For example, `val_batch0_labels.jpg` and `val_batch0_pred.jpg` show a missed annotated hole in `train_0832.jpg` (a published filename now assigned to validation). The earlier audit also reported missing Hole boxes and ambiguous labels, so apparent false positives and negatives need human review. Background and date correlations may inflate apparent performance. The smoke run only checked that the pipeline works and is not the baseline result.

### Validation comparison gallery

Open `runs/soybean_hole/validation_review_comparison_v2/review.html` locally to compare annotations and predictions side by side. The gallery uses the 40-epoch checkpoint on the 175 grouped validation images; the source filename prefix does not identify the new split. Matching uses confidence 0.10 and IoU 0.50. An unmatched box can indicate a model or annotation issue, and these fixed-confidence review counts are not the reported Ultralytics precision and recall. The test split is not used.

The following command refreshes that gallery **without rerunning inference**, using the ignored local cache at `runs/soybean_hole/validation_prediction_cache/`. It verifies the checkpoint and manifest hashes, image dimensions and labels. The cache, prepared images and checkpoint must exist locally. To create a new gallery instead, omit `--refresh` and use a new `--output` directory; without `--predictions`, the script runs validation inference again.

```bash
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/python scripts/review_soybean_holes.py \
  --weights runs/soybean_hole/long40/weights/best.pt \
  --predictions runs/soybean_hole/validation_prediction_cache/predictions.jsonl \
  --output runs/soybean_hole/validation_review_comparison_v2 --refresh \
  --review-confidence 0.10 --match-iou 0.50 --sample-size 25 --seed 42
```

Choose a review status and add notes for each image, then use **Export reviews as CSV** for a portable backup. The page reports whether local browser storage is available; if it is not, export before closing. Browser storage is tied to the browser, origin and gallery path: refreshing at the same path keeps the same storage key, but moving the file or switching between `file://` and a local server can make notes inaccessible. Export before moving or changing how you open it; the CSV is a backup, not an import mechanism. Browser data clearing can remove stored notes.

### Separated-grain counting and visible-hole prototype

The local prototype segments separated grains, runs the soybean Hole detector on
padded crops or the full photo, and saves an inspection report. It is **experimental**:
thresholds have not been calibrated on pea/lentil trays. Images must have one
species, separated whole grains, a uniform contrasting background, and clear
image borders. Inspect the numbered silhouettes before trusting a count.
Touching grains may merge. See [the implementation and evaluation notes](docs/grain_pipeline_mvp.md)
for the annotation format, capture protocol, limitations, and observed smoke results.
An [experimental FastSAM option](docs/fastsam_grain_experiment.md) also
produces individual masks, crops and mapped hole candidates for review. To
review a local photo, first install the baseline group and both local checkpoints
as described in those notes, then run:

```bash
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl \
  .venv/bin/python scripts/experiments/analyze_fastsam_grains.py path/to/photo.jpg \
  --output outputs/fastsam-demo/my-photo --compare-masked 0
```

Choose a fresh output directory for each photo and open its `review.html` in a
browser. Uncheck false candidates to update the retained and visible-hole flag
totals; download review decisions as a separate JSON backup. Browser storage is
local to the report location and may be unavailable or cleared. Review flags,
overlapping masks, missed grains and merged grains manually. Rejecting a mask
does not rerun hole association or recover detections rejected for overlap.
Visible-hole accuracy on natural multi-grain samples has not been measured.
The pea example requires attribution, SoyCult image rights are unresolved, and
FastSAM/Ultralytics licensing requires review before sharing; see the notes.

Install the locked baseline group with `uv sync --locked --group baseline`.
The checkpoint and datasets are ignored local files, so obtain them separately
on another machine. From the repository root:

```bash
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl \
  .venv/bin/python scripts/analyze_grain_sample.py path/to/photo.jpg \
  --species pea --provenance natural --device auto --mode compare \
  --output outputs/pea-development-01
```

Open `outputs/pea-development-01/report.html`. Use a fresh output path for each
run. The report links a machine-readable `sample.json`, per-mode grain CSVs,
foreground/instance images, crops, and mapped detections. Excluded components
are magenta; rejected predictions are red. `--mode crops` is the default; `full`
provides a whole-image comparator, and `compare` records both independently.

Default component area and colour thresholds, and the 0.40 flagging confidence,
are initial development settings, not validated operating points. See `--help`
for explicit segmentation and confidence options. A zero-grain image reports an
undefined percentage. Candidate detections describe visible features only;
this prototype cannot assess hidden infestation or food/feed suitability.

To evaluate manually annotated photos, follow the JSON manifest schema in the
implementation notes, then run:

```bash
.venv/bin/python scripts/evaluate_grain_samples.py path/to/manifest.json \
  --mode crops --output outputs/pea-evaluation-01
```

The evaluator rejects physical-set IDs and identical image bytes shared across
development/final, and checks consistent settings within each species. It cannot
prove that differently named physical sets contain different grains or that bags
are independent. Centre-only annotations cannot establish whether an extra
instance is a split. Keep final physical sets aside while calibrating.

Run the focused checks with:

```bash
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl \
  .venv/bin/python -m unittest discover -s tests -v
```
