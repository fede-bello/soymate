# models/

Training of the pooled demo model `soymate-pooled-v1`: frozen dinov2-small features plus a standardised
logistic regression (`FrozenLogReg` from `experiments/harness.py`), six classes (sound, broken, stained,
immature, insect_hole, impurity) pooled from soybean d97rjyk2tz, Lin v6vzvfszj6 and harvest hwdtghttp7.

```bash
cd ~/soymate-next && uv run python models/train_models.py
```

| | |
|---|---|
| Reads | `data/crops/manifest.csv`, `data/features/dinov2-small__crops.parquet` (from `pipeline/`), `results/dataset_id.json` (for the warning text) |
| Does | trains on the train split only (multi-seed crops excluded), picks C on val, reports per-dataset test macro F1 with grouped bootstrap CIs |
| Writes | `data/models/soymate-pooled-v1.joblib` (pickled model) and `soymate-pooled-v1.json` (model card), then copies both to `s3://fb-soymate-team4-258601136235/derived/models/` |
| Used by | `demo/api/pipeline.py` (loaded at API startup) |

The pickle refers to `harness.FrozenLogReg`, so anything that loads it must have `experiments/` on `sys.path`
(the demo API does). The pooled model is a demo, not evidence of cross-dataset defect recognition: see the
dataset-ID check in `results/README.md`.
