# pipeline/

Data pipeline: raw datasets to leak-free grouped splits, masked seed crops and cached frozen features. Every
experiment in `experiments/` and the demo model in `models/` read these outputs. Outputs go to `data/`
(git-ignored); on the box that is `~/soymate-next/data`, a symlink to `~/soymate/data`.

Run from the repo root (on the box: `cd ~/soymate-next`), in this order:

```bash
uv run python pipeline/download_datasets.py            # 1. data/raw/ + data/raw/MANIFEST.json (all datasets, or name ...)
uv run python pipeline/make_splits.py                  # 2. data/splits/{soybean,lin,harvest,ghana}.csv + SUMMARY.json
uv run python pipeline/ghana_index.py                  # 3. data/splits/ghana_{seeds,photos}.csv (R4a reference counts)
uv run python pipeline/harvest_index.py                # 4. data/splits/harvest_{seeds,images}.csv (instances from masks)
uv run python pipeline/make_crops.py                   # 5. data/crops/<dataset>/*.png + data/crops/manifest.csv
uv run python pipeline/features.py --full-soybean      # 6. data/features/dinov2-small__{crops,soybean_full}.parquet
```

| File | Purpose | Reads | Writes |
|---|---|---|---|
| `download_datasets.py` | Download the datasets of CONTEXT.md §6; re-runnable, skips what is complete | internet | `data/raw/` |
| `make_splits.py` | Grouped splits (soybean: 30 s capture bursts; Lin: near-duplicate clusters; harvest: id prefix) | `data/raw/`, `research/soybean_bruchid/resplit_by_original.csv` | `data/splits/` |
| `ghana_index.py` | Per-seed boxes of the Ghana group photos, mapped back to their source photo | `data/raw/ghana_soybean/` | `data/splits/ghana_*.csv` |
| `harvest_index.py` | Seed instances (crushed / intact / impurity) from the harvest masks | `data/raw/harvest_soybean/`, `data/splits/harvest.csv` | `data/splits/harvest_*.csv` |
| `make_crops.py` | One square masked crop per seed (background painted grey to remove shortcuts) | `data/splits/` | `data/crops/` |
| `features.py` | Frozen DINOv2 features (CLS + mean patch), cached; only new crops are embedded | `data/crops/manifest.csv` | `data/features/` |
| `segment_multi.py` | Training-free seed finder and counter for multi-seed photos (used by R4a and the demo) | an image | overlay (optional) |
| `qc_sheet.py` | Contact sheet of source / masked crop pairs, to check masks by eye | a manifest | a JPEG |

`make_crops.py` and `segment_multi.py` are also imported as modules by `experiments/` and `demo/api/pipeline.py`
(they add `pipeline/` to `sys.path`), so the demo crops seeds exactly like the training crops.
