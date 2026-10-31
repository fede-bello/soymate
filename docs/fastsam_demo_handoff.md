# FastSAM demo handoff

Prepared for the other Codex chat. The main application was not modified by this handoff; all existing uncommitted changes were preserved. No commit or staging was performed.

## What is available

The experimental CLI is `scripts/experiments/analyze_fastsam_grains.py`; it calls FastSAM-small and the existing `grain_pipeline.YoloDetector` on CPU. It writes `annotated.png`, `numbered_masks.png`, `manifest.json`, padded `crops/grain-NNNN.png`, and aligned crop-space `masks/grain-NNNN.png`. The existing threshold/contour pipeline remains `scripts/analyze_grain_sample.py`. The separate evaluator is `scripts/experiments/evaluate_pea_fastsam.py`; historical comparison scripts are `pea_fastsam_comparison.py`, `pea_initial_comparison.py` and `pea_watershed_comparison.py` under the same directory. Geometry/association tests are in `tests/test_fastsam_experiment.py`. The more complete setup, prior results and licensing notes are in `docs/fastsam_grain_experiment.md`; `README.md` contains its link.

At the start of this handoff, the above `scripts/experiments/` files, the focused test, and `docs/fastsam_grain_experiment.md` were untracked; `README.md` was modified. This handoff document is also new and trackable. No files were staged. The worktree belongs to branch `jp/soybean-baseline`; no other worktree was present. `data/`, `runs/`, `outputs/` and `*.pt` are Git-ignored. In particular, **neither checkpoint, images, generated crops, nor review overlays will travel with a commit**.

Local required checkpoints:

- FastSAM-small `outputs/multigrain-experiment/weights/FastSAM-s.pt`, SHA-256 `c9f78716a81c7aff0d608ccc73e1b82ab3aaad86005049f6a92106a0be6d0844`. Download source: [Ultralytics v8.3.0 asset](https://github.com/ultralytics/assets/releases/download/v8.3.0/FastSAM-s.pt).
- Locally trained hole detector `runs/soybean_hole/long40/weights/best.pt`, SHA-256 `bf9f04f017f30c81f19385b8542a8202a0fb31cef6daa8728fbd878b733eed93`. It has no public download; obtain a local copy or retrain as documented in `docs/soybean_baseline_status.md`. Retraining need not reproduce the same checkpoint.

## Demo and runtime

Use `uv sync --locked --group baseline`; observed versions were Python 3.14.6, Ultralytics 8.4.194, PyTorch 2.15.0, OpenCV 5.0.0, and NumPy 2.5.4. The input below comes from the [Zenodo 21110940 v1 demonstration subset](https://zenodo.org/records/21110940); download/extract commands and checksum are in `docs/fastsam_grain_experiment.md`. With both local checkpoints present, run from the repo root with a **fresh** ignored output path:

```sh
/usr/bin/time -p env YOLO_CONFIG_DIR=/private/tmp/soy-yolo MPLCONFIGDIR=/private/tmp/soy-mpl \
  .venv/bin/python scripts/experiments/analyze_fastsam_grains.py \
  data/raw/pea_zenodo_21110940/images/20210406_145931.jpg \
  --output outputs/fastsam-demo/pea-40 --confidence 0.4 --compare-masked 0
```

On the available ARM Mac, CPU only, one fresh process took **3.08 s wall time** for 40 peas and **11.14 s** for 187 peas (same command with `20210406_150838.jpg` and a fresh output). These are single runs, including Python startup/imports, model loading, segmentation, saving artifacts and hole detection, not a latency guarantee. The CLI's internal stage timings report respectively FastSAM inference 0.51/0.54 s, mask filtering 0.38/5.57 s, and hole detection/association 0.73/2.74 s. The CLI total excludes startup and final JSON write; the external wall time includes both. `--compare-masked 0` disables the optional diagnostic second detector pass. Saved run manifests: `outputs/fastsam-demo-runtime/pea-40/manifest.json` and `outputs/fastsam-demo-runtime/pea-187/manifest.json`.

Annotated demo: `outputs/fastsam-demo-runtime/pea-40/annotated.png`; a comparison of padded and suppressed crops from SoyCult is `outputs/fastsam-final/soycult-al83/crop_comparison.png`. SoyCult's repository did not state an image licence in the inspected tree; clarify rights before using those images in a shared demo. The pea subset is CC BY 4.0 and needs attribution. FastSAM's repository LICENSE and Ultralytics implementation state AGPL-3.0, while FastSAM's README separately describes the model as Apache 2.0. Applicable terms for this exact checkpoint and intended distribution remain unresolved.

## What the error review shows

At IoU ≥ 0.5, the 40-pea development image has 40 matches and eight extra candidates. All eight (candidate IDs 4, 12, 14, 17, 20, 34, 37 and 44) visually outline **background gaps** between peas, not duplicate peas. Review `outputs/fastsam-review/20210406_145931-labelled-overlay.png` and `outputs/fastsam-review/20210406_145931-extras.png`. IDs refer to the saved spatially sorted run, not permanent identities.

The 187-polygon image was reported as 174 matches, 13 misses and 18 extras by the current evaluator. Inspect before quoting these as physical-grain errors: eleven extra candidates (32, 53, 65, 71, 80, 81, 120, 130, 137, 140, 163) visually cover background gaps; the other seven (84, 112, 113, 160, 183, 184, 187) visually cover peas, but their IoU against the rasterized labels is below 0.5. Five annotations (168, 174, 178, 183, 184) each enclose two peas and overlap earlier single-pea annotations. Because the evaluator writes polygons into a single label image in annotation order, ten earlier individual polygons (10, 30, 62, 75, 81, 107, 115, 150, 153, 157) lose most of their pixels; two composite polygons (168, 178) are also unmatched. Polygon 180 outlines a scratch/background feature. Consequently these 13 label-relative misses are not evidence that 13 distinct peas were missed, and seven label-relative extras are not clearly false objects. The apparent net count error is not a trustworthy physical count comparison. No fully corrected independent manual count was made.

Inspect `outputs/fastsam-review/20210406_150838-labelled-overlay.png`, `20210406_150838-extras.png`, `20210406_150838-misses.png`, and `187-composite-polygons.png`. In the whole-image overlays, P = predicted candidate, BG = apparent background gap (red), G = apparent grain affected by composite truth (magenta), T = unmatched ground-truth polygon (yellow). In the crop sheets red outlines are predicted masks, green are ground-truth polygons, and yellow outlines are missed ground-truth polygons. These are visual interpretations, not corrected authoritative labels. The 40 image is development data; physical-set independence of the 187 image is unknown. The denser three images hit the 300-candidate cap. No natural-damage-labelled multi-grain reference was available, so end-to-end hole accuracy has not been measured.

## Smallest app-facing interface to discuss

For a hackathon, the least coupled option is a background process invoking the existing CLI with an input file and a fresh output directory. Read `manifest.json` and per-candidate mask files, then display `annotated.png` or draw each candidate using `id`, `bbox_original_xyxy`, `crop_origin_xy`, `crop_size`, `crop_mask_path` and the source dimensions. These coordinates refer to the EXIF-upright image. Each mask PNG is aligned to its padded crop, not a full-image mask; add the crop origin to convert crop coordinates to original-image coordinates, clipping to image bounds.

The current CLI already sends ordinary padded crops to the detector. It adds the crop origin to each predicted box, tests whether its centre lies inside the target mask, and rejects centres that lie outside or in multiple candidate masks. Multiple accepted hole boxes count once per grain at the stored 0.4 threshold. Each detection and rejection reason is saved under its candidate; overlapping masks and edge candidates carry warnings.

A minimal review UI could show the candidate IDs, outlines and crops, and allow a user to toggle IDs as rejected. Recompute the displayed grain and flagged-grain totals from the retained candidates, preserving the original manifest and saving the review decisions separately. The current CLI has **no reject UI or persisted review-state interface**; this is a proposed consumer contract, not an implemented feature. Existing detector associations were computed before any user rejection. If the app should recover previously rejected ambiguous detections after a mask is removed, it must explicitly rerun association against the retained masks; simply filtering totals will not do that. Confirm file access and lifecycle, error handling, concurrency, checkpoint loading and licensing with the app's owner before integrating.
