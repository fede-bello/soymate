# experiments/

The event results R1 to R4 and the dataset-ID check, all through one shared harness, plus the teammate
prototypes (YOLO hole detector, grain counting, FastSAM) in subfolders. Numbers and their reading are in
[`results/README.md`](../results/README.md).

## Event results (top level)

Inputs: `data/crops/manifest.csv`, `data/features/*.parquet` and `data/splits/` from `pipeline/`. Each script
writes `results/<name>.json` (numbers, a `how` field, creation time, code revision) and CSV tables next to it.
Run from the repo root (on the box: `cd ~/soymate-next`):

```bash
OMP_NUM_THREADS=4 uv run python experiments/r1_leaky_vs_clean.py   # R1 (about 30 s on the box)
OMP_NUM_THREADS=4 uv run python experiments/r2_per_class.py        # R2 + session control (about 2 min)
OMP_NUM_THREADS=4 uv run python experiments/dataset_id.py          # dataset-ID probe
OMP_NUM_THREADS=4 uv run python experiments/r3_transfer.py         # R3 transfer curve (+ r3_transfer.png)
OMP_NUM_THREADS=4 uv run python experiments/r4_ghana_counts.py     # R4a seed counts (overlays in qc/r4)
OMP_NUM_THREADS=4 uv run python experiments/r4_harvest_lots.py     # R4b lot-level % crushed
```

| File | What |
|---|---|
| `harness.py` | Data loading, the model interface (`MODELS`, default `FrozenLogReg`), grouped bootstrap F1, Wilson intervals, `write_result` |
| `r1_leaky_vs_clean.py` | Published vs photo vs burst split, full image vs masked crop, on d97rjyk2tz |
| `r2_per_class.py` | Per-class F1 on the grouped test split, and the soybean session control |
| `dataset_id.py` | Can a probe tell the source dataset from the features (also from a texture-only patch)? |
| `r3_transfer.py` | Transfer d97rjyk2tz to and from Lin with k labelled target seeds per class |
| `r4_ghana_counts.py` | Count error of `pipeline/segment_multi.py` on the 105 Ghana group photos |
| `r4_harvest_lots.py` | Lot-level % crushed on held-out harvest originals (oracle segmentation) |

`harness.py` is imported as the top-level module `harness` (the scripts add `experiments/` to `sys.path` when
needed). Keep that name: the demo model pickle refers to `harness.FrozenLogReg`.

## Teammate prototypes (subfolders)

Local, human-reviewed experiments by JP. They need the optional `baseline` dependency group
(`uv sync --locked --group baseline`, adds Ultralytics) and local checkpoints; details in the top-level README.

| Folder | Files | Notes |
|---|---|---|
| `yolo_holes/` | `prepare_soybean_holes.py` (grouped hole-only YOLO dataset to `data/processed/soybean_hole/`), `review_soybean_holes.py` (HTML review gallery of validation predictions) | Status: `docs/soybean_baseline_status.md` |
| `grain_counting/` | `grain_pipeline.py` (library: segment separated grains, associate hole detections), `analyze_grain_sample.py` (one photo to an HTML report), `evaluate_grain_samples.py` (reports vs hand counts) | Notes: `docs/grain_pipeline_mvp.md`; tested by `tests/test_grain_pipeline.py` |
| `fastsam/` | `analyze_fastsam_grains.py` (FastSAM masks + hole candidates, review page), `pea_*_comparison.py`, `evaluate_pea_fastsam.py` (pea polygon comparisons) | Notes: `docs/fastsam_grain_experiment.md`; tested by `tests/test_fastsam_experiment.py` |

Outputs of the prototypes go to `outputs/` and `runs/` (git-ignored). The FastSAM scripts import
`grain_counting/grain_pipeline.py` through `sys.path`.
