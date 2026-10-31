<p align="center">
  <img src="assets/logo.png" alt="SoyMate logo" width="260">
</p>

# SoyMate

**A seed grade from a phone photo, that the farmer can check too.** At grain intake, someone at the cooperative counts damaged seeds by eye, and that count sets what the farmer is paid. SoyMate finds every seed in a few phone photos, classifies it (sound, broken, stained, unripe, insect hole), and gives the share of each defect with its uncertainty and a verdict: pass, take more photos, or fail.

Project for **Hack the Fork Paris 2026** (AgroParisTech, Palaiseau, 30 October to 1 November 2026), **Track 3: Protein sovereignty, from French fields to the proteins of tomorrow**.

> **Single source of truth:** [`CONTEXT.md`](CONTEXT.md), starting with **§0 Current plan** (31/10), which supersedes the pre-event plan in §1, §5 and §8-§12. Every figure carries its source (`[S#]`) and a confidence tag.

---

## Why

- Seed damage is high and uneven: in 2025, French lentil truckloads averaged 24.4 % beetle-damaged seeds (from 1 % to 75 % between lots), the highest of the 2021-2025 survey. Sources in [`CONTEXT.md` §3](CONTEXT.md).
- The damage sets the price, but it is counted by eye, varies between people and sites, and the farmer cannot check it.
- SoyMate does not remove damage. It makes the grade fast, consistent and visible to both sides.

## Why soybean first, lentil next

- **Soybean** is the only bean with public labelled photos of damaged seeds (~8,000). We found none for lentils, peas or faba beans. French food soy is real (45 kt/yr) but pays only 20 to 70 €/t more than feed, so it is where we build and test the method, not the business.
- **Lentil** is where the value is: ~550 €/t between food and feed outlets. Taking the tool there needs French lentil photos labelled by graders, ~1,000 seeds per grade, calibration against the visual reference count, and a pilot with one cooperative.
- AI grading of pulses already sells in Australia (Cropify). Nobody publicly covers French soy or pulses. Full analysis: [`docs/soymate_viability_brief.pdf`](docs/soymate_viability_brief.pdf).

## How

1. **Photo:** phone, plain matte background, a few photos per sample.
2. **Find:** threshold and contours (a pretrained segmenter such as SAM if seeds touch).
3. **Classify:** frozen pretrained features (DINOv2) plus a small linear classifier, trained on CPU.
4. **Grade:** percentage per class with a Wilson interval; "take more photos" when the interval crosses the threshold.

The public soybean defect dataset leaks (80-84 % of its test images are copies of training images), so we re-split it. Results to produce at the event: leaky vs clean split, per-class F1, a check that the model is not recognising the source dataset, transfer between soybean datasets, and lot-level error on real hand-labelled photos.

## Repository layout

```
.
├── README.md              this file
├── CONTEXT.md             single source of truth (§0 = current plan)
├── pyproject.toml         Python dependencies (uv)
├── assets/logo.png
├── docs/
│   ├── soymate_viability_brief.pdf   viability, money, competition, assumptions, sources (current)
│   ├── figures/viability/            charts used in the brief
│   ├── aws_setup.md                  the team's AWS dev box: connect, run, back up
│   ├── soymate_team_plan.pdf         pre-pivot team plan (outdated: plans own pea/lentil photos)
│   └── soymate_data_report.pdf       pre-event data report
├── pitch/                 pitch deck: link, outline, slides to fill, backup copy of the slides
├── research/
│   ├── viability/         soy market, pulses market, grading and competition, synthesis
│   ├── critique.md        adversarial review of the plan (31/10)
│   ├── soybean_bruchid/   audit of the soybean beetle-damage dataset + leak-free re-split CSV
│   ├── other_datasets/    survey of seed image datasets + new_candidates.md (31/10 search)
│   └── context/           intake standards, soybean for food, competitors, photo protocol
├── scripts/
│   ├── aws/               EC2 bootstrap, Session Manager connect, dataset downloader
│   └── docs/              generator of the viability brief PDF
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
| Soybean beetle damage (Mendeley d97rjyk2tz) | Insect holes, seed-coat cracks, sound seeds; audited and re-split | CC BY 4.0 |
| Soybean Seeds, 5 classes (Mendeley v6vzvfszj6) | Broken, stained, immature, skin-damaged, intact; 5 multi-seed originals | CC BY 4.0 |
| Ghana seed varieties, soybean part (Mendeley t94nzy4ptz) | Real multi-seed phone photos: seed count, false positives on sound seeds | CC BY 4.0 |
| Mechanical-harvest soybean (Mendeley hwdtghttp7) | Multi-seed images with intact / crushed / impurity masks (split by id prefix) | CC BY 4.0 |
| Indonesian soybean varieties (Mendeley c733bjz4m3) | Multi-seed flatbed scans | CC BY 4.0 |
| GrainSet (Scientific Data 2023) | Broken and pest-damaged cereal kernels, expert labels | CC BY 4.0 |
| Radio_lentille (Terres Inovia, Hugging Face) | X-rays of bruchid-damaged French lentils, lot damage counts | MIT |

Download with `uv run python scripts/aws/download_datasets.py [name ...]` (see the script's docstring).

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
