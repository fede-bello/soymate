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
