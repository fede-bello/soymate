# Experimental FastSAM grain separation and hole-detector smoke test

This is a local, human-reviewed experiment, not a validated grain-quality assessment. The existing threshold/contour method remains available through `experiments/grain_counting/analyze_grain_sample.py`; the FastSAM path is isolated in `experiments/fastsam/analyze_fastsam_grains.py` and reuses the existing hole detector and padded crop helper. No main-pipeline behavior is changed.

## Inventory and provenance

Git status was clean at the start; there is one worktree, on `jp/soybean-baseline`. Local `main` and the local references for `origin/main` and `origin/jp/soybean-baseline` contained no FastSAM implementation. The remote references were inspected locally, not fetched. Before this work, all of the following were ignored: `outputs/multigrain-experiment/` (original scripts, reports, metrics and images), `data/raw/pea_zenodo_21110940/` (five photos, LabelMe polygons, metadata and ZIP), FastSAM weights, and `runs/soybean_hole/long40/weights/best.pt`. `data/`, `runs/`, `outputs/` and checkpoint extensions remain ignored. Git-trackable files added by this work are this document, `experiments/fastsam/` and `tests/test_fastsam_experiment.py`; no files are staged.

- FastSAM-small: [Ultralytics release v8.3.0](https://github.com/ultralytics/assets/releases/download/v8.3.0/FastSAM-s.pt), SHA-256 `c9f78716a81c7aff0d608ccc73e1b82ab3aaad86005049f6a92106a0be6d0844`. The benchmark's own download URL returned 401; byte identity with the checkpoint used by the benchmark authors was not established.
- Pea images: [Gulzar and Ünal, Zenodo 21110940 v1.0](https://zenodo.org/records/21110940), `pea_demo_subset_v1.zip`, MD5 `f7f805690eec308bf59a5e461ded6c5a`, CC BY 4.0. Five images and LabelMe polygon files are included; they contain instance labels, not hole labels. The 40 image is development data. Physical-set independence of the 187 and remaining images is unknown; they are exploratory checks, not held-out evaluation.
- Hole detector: locally trained `runs/soybean_hole/long40/weights/best.pt`, SHA-256 `bf9f04f017f30c81f19385b8542a8202a0fb31cef6daa8728fbd878b733eed93`. It is not provided by a public download. Use an existing local copy or follow [training and preparation documentation](soybean_baseline_status.md#longer-run-measured-comparison) and [README](../README.md#soybean-hole-only-baseline); retraining may produce different bytes and predictions, including because of MPS nondeterminism. Its initial [YOLO11n checkpoint](https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt) has SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`; the training source is Shinde et al.'s [soybean dataset v2](https://doi.org/10.17632/d97rjyk2tz.2), CC BY 4.0. The detector is a visible-hole box model trained on soybean images, and transfer to multi-grain pea photos is unvalidated.
- SoyCult AL83: [original file at commit 19a7fd5](https://github.com/eliezersflores/SoyCult/blob/19a7fd5b1423005a7bf57fc98200106f973a92b4/data/imgs/AL83.JPG), SHA-256 `c3e929abcd80fe0eeb1b9310e09b6342ed874f4d39170dc3799172e9d478609d`. The inspected source repository has no stated licence or independent defect labels; clarify image rights with its holders before reuse or redistribution.
- [Pea benchmark implementation](https://github.com/yavuz-unal/pea-seed-segmentation-benchmark/tree/65ac403c669b3a43ba48d8f5a82657a9874bc6d1) is MIT licensed. FastSAM's [repository licence](https://github.com/CASIA-LMC-Lab/FastSAM/blob/main/LICENSE) and [Ultralytics licence](https://github.com/ultralytics/ultralytics/blob/main/LICENSE) are AGPL-3.0; the FastSAM README separately describes its model as Apache 2.0. The applicability of these statements to this exact checkpoint and intended distribution is unresolved; do not infer a distribution or commercial-use permission from this experiment.

## Setup

From the repository root, use the existing lockfile and baseline group (`uv sync --locked --group baseline`). The recorded environment was Python 3.14.6, Ultralytics 8.4.194, PyTorch 2.15.0, OpenCV 5.0.0 and NumPy 2.5.4, ARM CPU. Versions and transitive dependencies are in `uv.lock`; use CPU as the script does. Install or prepare the detector weights as above. Download the segmentation weights and benchmark data into ignored locations:

```sh
mkdir -p outputs/multigrain-experiment/weights data/raw/pea_zenodo_21110940
curl -fL https://github.com/ultralytics/assets/releases/download/v8.3.0/FastSAM-s.pt -o outputs/multigrain-experiment/weights/FastSAM-s.pt
curl -fL 'https://zenodo.org/records/21110940/files/pea_demo_subset_v1.zip?download=1' -o data/raw/pea_zenodo_21110940/pea_demo_subset_v1.zip
unzip -n data/raw/pea_zenodo_21110940/pea_demo_subset_v1.zip -d data/raw/pea_zenodo_21110940
```

Verify the hashes above. For SoyCult, use the pinned raw image URL only if its terms permit the intended use, and place your authorized local copy under `data/raw/`. The saved long40 checkpoint is a separate prerequisite; neither the generic YOLO checkpoint nor the FastSAM weights can substitute for it.

## Run a local photo

Place an authorized photo, e.g. `data/raw/phone/my-sample.jpg`, under ignored `data/`. Photograph 20–40 grains on a contrasting matte surface, with margins, sharp focus and grains spread apart; independently count them and record the physical set, species and capture conditions. Then:

```sh
YOLO_CONFIG_DIR=/private/tmp/soy-yolo MPLCONFIGDIR=/private/tmp/soy-mpl .venv/bin/python experiments/fastsam/analyze_fastsam_grains.py data/raw/phone/my-sample.jpg --output outputs/fastsam-smoke/my-sample --segmentation-weights outputs/multigrain-experiment/weights/FastSAM-s.pt --detector-weights runs/soybean_hole/long40/weights/best.pt --confidence 0.4 --compare-masked 5
```

Output must be a fresh subdirectory of ignored `outputs/`; select a different path for each run. `annotated.png` shows numbered mask outlines and mapped boxes: green = accepted centre at the stated threshold, red = rejected association, orange outline = candidate warning. `numbered_masks.png` shows the masks without boxes. `crops/` holds one unmasked padded crop per candidate; `masks/` contains corresponding binary crop-coordinate masks, aligned to the stored crop origin and size. `manifest.json` records source hash, dimensions, settings, weight hashes, per-candidate original bounding box, crop origin, warnings, crop and original box coordinates, association decision, counts and timing. IDs are sorted by mask geometry and stable for the same accepted masks, but are not persistent identities if predictions change. `crop_comparison.png` compares the first N ordinary crops with pixels outside each target mask replaced by median border colour; both were sent to the detector and individual records are in the manifest. The masked variant is a diagnostic, not the default result.

The hole model collects boxes at confidence ≥0.05; the output flag threshold defaults to 0.4 and is recorded. A box centre must lie inside the target mask and outside overlapping masks to be associated. Rejected boxes remain in the manifest, and a grain with multiple accepted boxes is counted once. Masks can overlap; warnings indicate any overlap, a small mask dimension, or the image edge. The global warning `max_detections_reached` means Ultralytics returned its explicit limit of 300 raw masks; a photo may contain additional grains. Other false objects and poorly shaped masks are possible even without warnings. Resizing to 1024 and mask boundaries can also lose detail; crop masking may cause a distribution shift for the soybean-trained detector.

## Reproduce and evaluate benchmark runs

```sh
YOLO_CONFIG_DIR=/private/tmp/soy-yolo MPLCONFIGDIR=/private/tmp/soy-mpl .venv/bin/python experiments/fastsam/analyze_fastsam_grains.py data/raw/pea_zenodo_21110940/images/20210406_145931.jpg --output outputs/fastsam-smoke/pea-40-reproduction
.venv/bin/python experiments/fastsam/evaluate_pea_fastsam.py outputs/fastsam-smoke/pea-40-reproduction/manifest.json data/raw/pea_zenodo_21110940/annotations/20210406_145931.json
```

The evaluator rasterizes polygons in annotation order at original resolution and compares the stored crop masks at IoU ≥ 0.5 with greedy one-to-one matching. `polygon_metrics.json` records matches and IDs of misses and extras. To evaluate the other photos, substitute a stem from `metadata.csv` for both image and annotation, and use a fresh output path. The prior independent comparison and watershed prototypes are preserved as `experiments/fastsam/pea_fastsam_comparison.py`, `pea_watershed_comparison.py`, and `pea_initial_comparison.py`; they reproduce the earlier experiment conventions and expect ignored baseline outputs and weights at the paths in the scripts. The corrected watershed additionally requires scikit-image 0.26.0 and SciPy 1.18.1 in a separate environment; it was not added to project dependencies.

No available multi-grain photo has natural damage with complete reference hole labels. End-to-end hole accuracy is therefore **not measured**. Zero detections on an unlabelled image do not show correctness. The historical comparison reported 40/40 matches with eight extras on the 40 photo and 174/187 with 18 extras on the 187 photo; review full instance errors, not only net count error. A separate local report under ignored `outputs/multigrain-experiment/RESULTS.md` retains the exploratory watershed diagnosis and historical timings.

## Recorded smoke results

All five [Zenodo v1](https://zenodo.org/records/21110940) images were processed with the above settings, CPU and 0.4 hole-flag threshold. The three densest hit the 300-candidate limit, recorded as a warning. Their misses therefore include the effect of the cap; increasing it would be a new experimental configuration. All images belong to the same demonstration subset, and none is an independent end-to-end damage test.

| Polygon count | Candidates | Matched | Missed | Extra | Count error | Total seconds |
|---:|---:|---:|---:|---:|---:|---:|
| 40 | 48 | 40 | 0 | 8 | +8 | 2.78 |
| 187 | 192 | 174 | 13 | 18 | +5 | 11.31 |
| 397 | 300 | 288 | 109 | 12 | −97 | 20.56 |
| 441 | 300 | 298 | 143 | 2 | −141 | 20.60 |
| 542 | 300 | 280 | 262 | 20 | −242 | 20.95 |

Totals include model loading, rendering and crop detector inference, but not the separate polygon evaluator. They are single local runs, not controlled latency benchmarks. On SoyCult AL83, 51 candidates matched the previously visually checked 51 visible soybeans; this is an exploratory manual count, not instance ground truth. The hole detector flagged zero at 0.4. One unrelated crop yielded a rejected 0.065 box; the first five SoyCult crops produced no boxes at collection threshold 0.05 in either padded or suppressed form. Neither finding supports an accuracy claim. The saved local review artifacts are `outputs/fastsam-final/soycult-al83/annotated.png`, `crop_comparison.png`, and `manifest.json`.

The historical default produced 1/40 polygon matches with 39 misses and 1 extra; the fixed watershed produced 9 matches, 31 misses and 4 extras. Its predecessor's background marker captured most of a synthetic foreground; constraining a watershed to the filled foreground corrected that particular failure, but the pea foreground still had insufficient peaks and merged many grains. These results do not validate watershed under other settings or capture conditions.
