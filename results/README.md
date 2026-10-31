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
- **Lin v6vzvfszj6:** 5,513 crops; 290 exact duplicates and 33 near-duplicate label conflicts dropped (5,190
  kept); groups are near-duplicate clusters (16x16 dHash, 8 dihedral variants, Hamming <= 12/256 in both
  directions; pairs at 11-12 were checked by eye and included same-image pairs).
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
every arm, including F: not credible as hole detection yet.** 452 of the hole crops were shot on 9-11/08, when
no other class was photographed (380 on black background, zoomed out so the crop is upsampled); only ~297 holes
share days and background with sound seeds (13-14/08, light). See R2 session control.


### R2: per-class F1 and session control (`eval/r2_per_class.py`, `r2_per_class.json`, `r2_session_control.json`)

dinov2-small + logistic regression, C chosen on val, burst-level split, test = one crop per photo, multi-seed
crops excluded, 95 % CIs from a bootstrap over bursts.

| Scope | Per-class F1 [95 % CI] | Macro |
|---|---|---|
| Soybean (132 crops, 19 bursts) | insect_hole 1.00 [1.00, 1.00], broken 0.82 [0.77, 0.88], sound 0.82 [0.73, 0.93] | 0.88 [0.85, 0.93] |
| Lin | broken 0.93, immature 0.91, sound 0.91, stained 0.88 | 0.91 [0.88, 0.93] |

Soybean errors are mostly sound called broken (14 of 54). **Session control** (grouped 5-fold CV over bursts,
because the fixed test has a single same-day hole burst): holes vs sound on the only days with both classes
(13-14/08, light background; 297 hole crops in 7 bursts, 895 sound in 43) give hole F1 0.975 [0.92, 0.99];
trained only on holes from 9-11/08 and tested on holes from 13-14/08, 0.96 [0.91, 0.98]. Features do encode
the session (capture-date probe AUC 0.99 for sound 13 vs 14/08, 0.85 for holes 9-11 vs 13-14), but a hole
detector that never saw a 13-14/08 hole still finds them, so it is not only reading the session. With 7 hole
bursts this is indicative, not conclusive.

### Dataset-ID check (`eval/dataset_id.py`, `dataset_id.json`)

A probe on frozen features tells soybean d97rjyk2tz from Lin with **100 % accuracy** (AUC 1.00; sound seeds
187 test crops, Wilson 95 % [0.98, 1.00]), also on broken seeds, and also from a **texture-only central 50 %
patch** of sound seeds (98-100 % seed pixels, so no outline or background). The datasets are separable from the
seed surface alone (camera, magnification, lighting). Consequences: per-class numbers are reported **within
each dataset**; a pooled 5-class model is not evidence of defect recognition across setups, and is
uncalibrated on third-party photos. The pooled model flags 8.3 % [4.7, 14.2] of Lin sound seeds and 13.0 %
[6.4, 24.4] of soybean sound seeds as defective (never as the other dataset's classes).

### R3: transfer between soybean datasets (`eval/r3_transfer.py`, `r3_transfer.json`, `__curve.csv`, `r3_transfer.png`)

Shared classes sound vs broken, dinov2-small + logistic regression, k labelled target seeds per class (one per
photo), 10 random draws per k (mean shown), CIs from a bootstrap over target groups. Soybean "broken" is testa
cracking; Lin "broken" is (a) broken + skin-damaged or (b) skin-damaged only.

| Direction | k=0 (source only) | k=10: source+k / target only | k=50: source+k / target only | target ceiling |
|---|---|---|---|---|
| soybean -> Lin, (a) | 0.52 | 0.68 / 0.89 | 0.83 / 0.93 | 0.98 |
| soybean -> Lin, (b) | 0.59 | 0.74 / 0.90 | 0.86 / 0.93 | 0.97 |
| Lin -> soybean, (a) | 0.37 | 0.68 / 0.63 | 0.74 / 0.71 | 0.79 [0.72, 0.87] |
| Lin -> soybean, (b) | 0.55 | 0.67 / 0.63 | 0.73 / 0.71 | 0.79 |

Macro F1. **Another setup's data does not substitute for target labels:** on Lin, 10 target labels per class
alone beat ~1,000 pooled soybean images (0.89 vs 0.68); on soybean, adding Lin gives +0.02 to +0.05, inside the
CIs (soybean test: 11 bursts). Part of the zero-shot drop is label shift (definition (b) is closer to testa
cracking and scores higher). For a new crop or capture setup, budget for labelled target data.
