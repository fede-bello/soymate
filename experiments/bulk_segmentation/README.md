# Experiment A: zero-shot segmentation of bulk (packed) soybean photos

Question: can a zero-shot instance segmenter find seeds in packed bulk photos well enough for a "bulk" mode in
the demo? Decision rule: add the mode only if the best method reaches **count MAPE <= 5 % and instance F1 >= 0.85
on the 6 test originals**.

Script: [`bulk_segmentation.py`](bulk_segmentation.py) (run commands in its docstring). Results:
`results/bulk_segmentation.json`, `__images.csv` (per image and method), `__configs.csv` (every train sweep
point), `__ghana.csv`.

## Data and protocol

- Mechanical-harvest soybean hwdtghttp7 (Mendeley, CC BY 4.0): 40 original images (aug 01, 1280x1024,
  harvester camera, seeds packed edge to edge with dark gaps, 62 to 90 GT instances each).
- GT instances rebuilt from the per-pixel class masks with the `pipeline/harvest_index.py` rules (palette snap,
  4-connected components per class, specks dropped, merged crushed/intact components split by watershed); per-class
  counts are asserted equal to `data/splits/harvest_seeds.csv`. GT counts all labelled instances, including seeds
  cut by the image border and impurities (stems, pods).
- No method was trained on this dataset, so all 40 originals are unseen; settings were picked on the 28 train
  originals only (pooled instance F1), headline on the 6 test originals, all 40 as secondary.
- Matching: greedy one-to-one at IoU >= 0.5. Count = kept masks (segment_multi: its sum of per-component
  estimates). 95 % CIs: bootstrap over images (2000 draws).

## Results (6 test originals, 95 % bootstrap CIs; all 40 in brackets)

| Method (config picked on train) | Count MAPE | Signed count err | Precision | Recall | F1 | Matched IoU | s / image |
|---|---:|---:|---:|---:|---:|---:|---:|
| FastSAM-s, imgsz 640, conf 0.5 + post | 5.03 % [2.84, 7.18] (5.31) | -0.2 (+0.2) | 0.945 | 0.943 | **0.944** [0.936, 0.953] (0.945) | 0.913 | 0.34 |
| Cellpose-SAM, diameter 130 | 4.37 % [0.95, 8.03] (6.61) | -3.2 (-4.1) | 0.975 | 0.934 | **0.954** [0.938, 0.973] (0.938) | 0.906 | 32 |
| Watershed on grey Otsu | 6.65 % (10.55) | -5.2 (-8.6) | 0.905 | 0.844 | 0.873 (0.887) | 0.853 | 0.30 |
| segment_multi (as deployed) | ~11,000 % | +8,445 | 0.10 | 0.04 | 0.06 | | 0.02 |
| FastSAM, JP's exact settings (reference) | 14.8 % (17.0) | +11 | 0.837 | 0.958 | 0.893 (0.889) | | 0.25 |

- Winner by train F1: FastSAM-s, `imgsz=640, retina_masks=False, iou=0.9`, then post-processing: conf >= 0.5,
  drop masks > 25 % of the image or > 4x the median mask area, drop masks darker than 0.6x the median mask L*
  (the dark gaps between packed seeds were the main false positives), de-dup at IoU 0.5 or 80 % containment.
  Train (28): F1 0.945, MAPE 5.42 %. Boundary F (3 px) on matched pairs 0.77.
- Per-class recall (FastSAM, test): crushed 1.00, intact 0.95, impurity 0.40 (all 40: 0.96 / 0.96 / 0.58).
  Crushed fragments are found as often as intact seeds; impurities (stems, pods) are often missed.
- Count MAPE vs seeds only (crushed + intact): FastSAM 5.19 % test, Cellpose 3.67 %.
- Cellpose has the best test numbers but is 100x slower on CPU (32 s per image) and worse on all 40 (MAPE 6.6 %,
  undercounts), and lost on train F1 (0.932). Its seconds were measured while the box was shared with experiment B. The full-resolution auto-diameter Cellpose config (`cp_d0`, about
  57 s per image) was cut for time; the half-resolution config gave train F1 0.931.
- segment_multi fails as expected: packed seeds form one connected foreground, which it divides by a tiny
  "median seed" area.
- Ghana spread photos (demo examples), FastSAM with the same settings vs segment_multi vs published count:
  g17 165 / 164 / 164, Favor 186 / 186 / 186, Afayak shadow 259 / 259 / (89 published boxes, incomplete;
  semi-automatic estimate 257). No regression on spread seeds. On Favor FastSAM hit its 300 raw-mask cap before
  post-processing, so very dense spread photos may undercount.

**Decision: does not pass** (test MAPE 5.03 % > 5 %, F1 0.944 passes). It misses the count bar by 0.03 pp and
the CI [2.8, 7.2] straddles 5 %, so the honest reading is "count accuracy about 5 %, not shown to be <= 5 %".

## What a demo bulk mode would need (FastSAM)

- Package `ultralytics` (8.4.194, AGPL-3.0); it pulls full `opencv-python`, which needs `mesa-libGL` on the box
  (or force-reinstall `opencv-python-headless`).
- Weights `FastSAM-s.pt`, 23.9 MB, from
  `https://github.com/ultralytics/assets/releases/download/v8.3.0/FastSAM-s.pt`, SHA-256
  `c9f78716a81c7aff0d608ccc73e1b82ab3aaad86005049f6a92106a0be6d0844`.
- Latency on the c7i.4xlarge, 6 threads, fresh process: model load 1.2 s, first image 1.4 s, then 0.28 to 0.35 s
  per 1280x1024 image (about 1 to 1.5 s on 3000 px Ghana photos). Peak RSS 1.2 GB (Cellpose: 2.4 GB, 10 s per
  image even at half resolution).
- The post-processing above (about 40 lines in `postprocess`), and a warning when the raw output hits the
  300-mask cap.

## Licences

- FastSAM code and Ultralytics: AGPL-3.0 (the FastSAM README calls the model Apache 2.0; unresolved, see
  `docs/fastsam_grain_experiment.md`). Serving it from our API means the AGPL network clause applies to the
  service code unless an Ultralytics enterprise licence is bought.
- Cellpose: BSD-3-Clause (the cpsam weights are downloaded from Hugging Face on first use).
- hwdtghttp7 and the Ghana photos: CC BY 4.0.
