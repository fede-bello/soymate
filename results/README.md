# Results (Hack the Fork, 31/10/2026)

Every number here was computed at the event by a committed script. Each `<name>.json` holds the numbers, a
`how` field (data, split, model, metric), the creation time and the code revision. CSV files next to it hold
the tables. Re-run everything on the box from `~/soymate` (see `docs/aws_setup.md`).

## Pipeline

| Step | Script | Output (on the box, git-ignored) |
|---|---|---|
| Download | `scripts/aws/download_datasets.py` | `data/raw/`, `data/raw/MANIFEST.json` |
| Grouped splits | `scripts/data/make_splits.py` | `data/splits/{soybean,lin,harvest,ghana}.csv`, `SUMMARY.json` |
| Masked seed crops | `scripts/data/make_crops.py` | `data/crops/<dataset>/*.png`, `data/crops/manifest.csv` |
| Frozen features | `eval/features.py` | `data/features/<model>__crops.parquet` |
| Harness | `eval/harness.py` | model interface, grouped bootstrap F1, Wilson intervals |

## Splits (regenerated at the event)

- **soybean d97rjyk2tz:** 2,726 v2 images; 253 exact duplicates and 39 unlabelled dropped (292, as in the
  pre-event audit); 2,434 images in 1,165 original-photo groups; train/val/test 815/175/175 groups. The
  published split leaks: 217/272 validation and 229/274 test images share an original photo with published
  train (recomputed, identical to the pre-event audit). Grouping agrees with the declared pre-event
  `resplit_by_original.csv` on 98.8 % of images.
- **Lin v6vzvfszj6:** 5,513 crops; 290 exact duplicates and 7 near-duplicate label conflicts dropped; groups
  are near-duplicate clusters (16x16 dHash, 8 dihedral variants, Hamming <= 10/256).
- **harvest hwdtghttp7:** split by 4-digit id prefix (40 originals).
- **Ghana t94nzy4ptz:** 105 group photos, evaluation only.

## Results

(Filled in as experiments finish.)
