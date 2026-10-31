# Soybean hole detector: YOLO11n experiments

Local archive created 2026-10-31 for future comparison; these are experimental
candidates, not a final model selection. Both models detect annotated Hole
bounding boxes in full soybean images. They do not classify whole grains or
establish grain safety.

| Run | Original run | Training | Validation precision / recall | mAP@0.50 | mAP@0.50:0.95 |
|---|---|---|---|---|---|
| `baseline-8-epochs` | `runs/soybean_hole/baseline/` | 8 epochs, patience 100 | 0.823 / 0.563 | 0.640 | 0.427 |
| `long40-40-epochs` | `runs/soybean_hole/long40/` | 40 epochs, patience 7 | 0.882 / 0.581 | 0.709 | 0.481 |

Metrics are final validation of each `best.pt` on 175 images with 124 annotated
holes. Precision and recall use confidence thresholds chosen separately on that
validation set, so they are not a fixed-threshold comparison. Label quality,
possible capture-condition shortcuts and transfer to other grain photographs
remain limitations; no held-out test evaluation is evidenced. See
[the detailed evaluation](../../../docs/soybean_baseline_status.md) for the
fixed-threshold comparison and caveats.

Both runs started from `data/weights/yolo11n.pt` (SHA-256
`0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`),
using the prepared Mendeley soybean dataset d97rjyk2tz v2, 1,715 training
images, image size 640, batch size 8, seed 42, Ultralytics 8.4.194 and PyTorch
2.15.0 on Apple M5 Pro MPS. MPS operations reported nondeterminism. The two
training schedules differ in more than duration, including mosaic and learning
rate schedules. Each directory preserves its original `args.yaml` and per-epoch
`results.csv`; the longer run also includes its validation fingerprint. Paths
in the original configuration refer to the machine that ran training.

`best.pt` is the validation-selected checkpoint and `last.pt` is the final
checkpoint. The saved training logs say the optimizer was stripped, so these
files should not be assumed to support resuming the original optimizer state.

| Archived checkpoint | Bytes | SHA-256 |
|---|---:|---|
| `baseline-8-epochs/best.pt` | 5,500,570 | `aa15afb6be96ade7184c1d2bca70534dd44394fdea903895e34ef71511e80604` |
| `baseline-8-epochs/last.pt` | 5,500,570 | `3e739d09dce152d99951cb831a89b856c04faac6441a255178303000407363d9` |
| `long40-40-epochs/best.pt` | 5,504,666 | `bf9f04f017f30c81f19385b8542a8202a0fb31cef6daa8728fbd878b733eed93` |
| `long40-40-epochs/last.pt` | 5,504,666 | `93cc1ba7116aee479c0fb1aa15e13311975920d24890d8db4979a0b8a872914a` |

This archive is explicitly exempted from the repository's `*.pt` ignore rule
so its checkpoints can be tracked alongside their evaluation records. Other
generated checkpoints remain ignored.
