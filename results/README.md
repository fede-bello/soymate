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
  pre-event audit); 2,434 images from 1,165 original photos. **Group = 30 s capture burst** (146 bursts):
  with a photo-level split, 15/291 test crops had their nearest train neighbour (DINOv2 cosine) in a photo
  shot within 10 s, against 0.9 expected by chance; the burst split brings it to 0. The photo-level split is
  kept as `split_photo`. The published split leaks: 229/274 test images (83.6 %) share an original photo with
  published train, 266/274 (97.1 %) share a burst. Photo grouping agrees with the declared pre-event
  `resplit_by_original.csv` on 98.8 % of images.
- **Lin v6vzvfszj6:** 5,513 crops; 290 exact duplicates and 7 near-duplicate label conflicts dropped; groups
  are near-duplicate clusters (16x16 dHash, 8 dihedral variants, Hamming <= 10/256).
- **harvest hwdtghttp7:** split by 4-digit id prefix (40 originals).
- **Ghana t94nzy4ptz:** 105 group photos, evaluation only.

## Results

### R1: leaky vs clean split (`eval/r1_leaky_vs_clean.py`, `r1_leaky_vs_clean.json`, `__arms.csv`)

d97rjyk2tz, classes insect_hole / broken / sound, frozen dinov2-small + logistic regression, same 2,083
images in every arm, trained on train only, tested on one image per original photo, 95 % CIs from 2,000
grouped bootstrap resamples (over photos, or over bursts for the burst split).

| Arm | Split | Input | macro F1 [95 % CI] | broken F1 |
|---|---|---|---|---|
| as distributed | published, duplicates kept | full image | 0.913 [0.872, 0.951] | 0.838 |
| A | published | full image | 0.885 [0.832, 0.932] | 0.785 |
| D | photo-level | masked crop | 0.859 [0.788, 0.915] | 0.704 |
| F (ours) | burst-level | masked crop | 0.852 [0.801, 0.900] (19 test bursts) | 0.771 |

Leakage inflates macro F1 by about 0.03 to 0.06; the intervals overlap. **insect_hole F1 is 0.99 to 1.00 in
every arm, including F: not credible as hole detection.** Every bruchid seed was photographed in its own
sessions (9-11/08, black or light background), so the model can read the session; see R2 session control.

