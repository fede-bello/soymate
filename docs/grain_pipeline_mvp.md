# Separated-grain prototype: implementation and evidence

## What it does

`experiments/grain_counting/analyze_grain_sample.py` reads one EXIF-upright photo, estimates a
background colour from the border in Lab colour space, thresholds distance from
that colour, and labels filled foreground components. It excludes small objects
and objects crossing an image edge. It preserves original RGB pixels for detector
inference, even where the silhouette is filled over a dark hole.

The prototype runs the existing single-class YOLO11n detector on square padded
crops, the full image, or both separately. Ultralytics returns crop-space boxes;
the recorded crop origin maps these back to upright source coordinates. The
centre must lie within the intended filled grain silhouette. Full-image detections
are associated by centre containment. One or more flagged boxes on the same
instance count as one flagged grain. Unassigned boxes and exclusions are recorded.

The HTML report is static and uses relative local assets. `instances.png` is a
16-bit image: zero is background/excluded and positive pixels are grain IDs.
`sample.json` stores settings, hashes, crop origins, detections, and timing;
`grains_crops.csv` and/or `grains_full.csv` list grain statuses. `total` in the
JSON timing starts after image decoding and model loading; the CLI also records
`command_including_model_load`, measured after Python imports and argument setup.

Colour-distance threshold defaults to Otsu; use `--distance-threshold` for an
explicit 0–255 threshold. `--min-area-fraction` is a fraction of the full image;
the default is 0.00005. `--border-fraction` defaults to 0.01 of the shorter
dimension. Defaults are uncalibrated for real pea/lentil trays. Record and freeze
settings selected on development photos before running final samples. A .40
flagging threshold is a provisional starting point from soybean validation; it
is not a calibrated probability. Review candidates appear at .10 by default.
The JSON also gives flag counts at .10/.20/.40/.60.

Assumptions: one species, separated whole grains, even lighting, matte uniform
background, and unobstructed borders. Shadows, text, grain colour similar to the
background, touching grains, and occlusion can create spurious or missing
instances. The algorithm does not reliably identify merges; recapture after
separating grains. Cropping cannot restore details that were not recorded. Check
masks and detections visually; a flag is a candidate visible feature, not an
infestation or lot suitability decision.

## Annotation and evaluation

Manually count the upright photograph and, for damage evaluation, mark each
visible grain's centre in upright pixel coordinates. Use a fresh physical-set ID
for each disjoint set of grains. Repeated arrangements or views of the same
physical grains must share that ID and the same split. Record bag/lot, capture
conditions, and which side is visible in your data log. `provenance` should
identify the whole photo's damage type, such as `natural`, `synthetic`, or
`composite`; do not combine natural and synthetic-positive images in one group.

Example manifest (`sample_json` paths are relative to the manifest):

```json
{
  "photos": [
    {
      "sample_json": "../pea-development-01/sample.json",
      "species": "pea",
      "physical_set_id": "bag-a-set-01",
      "source_bag": "bag-a",
      "capture_id": "bag-a-set-01-photo-01",
      "split": "development",
      "provenance": "natural",
      "manual_total": 2,
      "damage_complete": true,
      "grains": [
        {"x": 150, "y": 240, "status": "hole"},
        {"x": 400, "y": 240, "status": "no_hole"}
      ]
    }
  ]
}
```

The manifest species and provenance must match the values recorded in each
analysis. `split` is `development` or `final`. For a counting-only photo set
`damage_complete` to `false` and omit `grains`, or provide all grain centres
with statuses `hole`, `no_hole`, or `uncertain`. If centres are provided, their
number must equal `manual_total`. Set `damage_complete` to `true` only when
every visible grain has been inspected and has a known status. `no_hole` means
no visible hole in that view, not that the grain is internally undamaged.
Record natural and hand-made holes as separate provenance groups.

Run the evaluator as documented in the README. It writes `photos.csv` and
`summary.json` in a fresh output directory. It matches each centre to the label
under it; if several centres occur in one component, the centre nearest that
component's centroid is matched and the component is reported as merged.
Unmatched predictions are extras or possible splits: centre-only labels cannot
reliably distinguish them. Reported errors include count bias, MAE, count
percentage error, damage-count error, percentage-point error, and pooled
precision/recall/F1 for fully labelled photos. Zero denominators produce null.
The manual-denominator damage percentage helps diagnose count versus detection
errors. Summary also reports errors averaged within physical set, then across
sets; pooled grain metrics and ordinary photo means overweight repeat views.

A reused physical-set ID or identical image bytes crossing development/final
cause an error. The tool cannot recognize the same grains given misleading IDs,
or establish source-bag independence or annotation correctness. The model and
settings must match within each species across a manifest. Use final data only
once the development settings are frozen; these checks cannot prove a freeze
happened. Annotations and metrics remain conditional on the visible face.

## Capture plan

For each of pea and lentil, prepare six disjoint sets of approximately 30, 60,
and 80 grains, two sets at each size. Allocate one of each size to development
and one to final evaluation before tuning. Photograph each set from overhead on
contrasting matte card with diffuse light, separated grains, clear margins, and
no scale marks in the analysis area. Check full-resolution focus. Optionally
take a second image per physical set for robustness; keep both in the same split.
Manually count and record natural, synthetic, or uncertain visible damage, and
have another person verify counts/positives. If there are not enough real
naturally damaged grains, report counting independently and treat synthetic
examples as software checks, not natural-damage evaluation.

## Observed checks on 31 October 2026

No pea/lentil tray photos or natural-damage labels were present locally, so no
tray-counting or transfer performance has been measured. The soybean test split
was not used. The following are development/integration checks only:

- A drawn synthetic image containing four separated circles and a dark spot
  produced four components in both inference modes. The counting-only evaluator
  matched all four marked centres and omitted damage metrics. This is a software
  smoke test, not a natural-grain or natural-damage measurement.
- Default Otsu and minimum area on grouped validation `test_0013.jpg` gave 15
  candidates for one apparent seed; the mask includes shadow/surface effects
  and watermark specks. This directly shows that defaults are not generally
  reliable on the published soybean photographs.
- With `--distance-threshold 20 --min-area-fraction 0.005`, the visually reviewed
  `test_0013.jpg` positive and `test_0012.jpg` candidate-negative each produced
  one accepted component. Both crop and full modes flagged the positive and
  neither flagged the candidate-negative at .40. The positive crop's strongest
  box scored .618 with IoU .766 against its published hole box; full-image
  strongest scored .556 with IoU .797. It also produced multiple boxes around
  the same hole; aggregation counted the grain once. The adjusted settings were
  selected on these images and are not validated tray settings.
- The positive run still excluded 216 small components, and its silhouette
  included a strong shadow. The negative had 36 exclusions. The negative had
  no annotated hole and no obvious visible hole in this single-view review;
  the source dataset is incompletely labelled.
- The two-photo evaluator smoke manifest conservatively groups both images under
  one physical-set ID because their physical identity is unknown. Its numbers
  are only a software check, not a performance estimate.
- On the local CPU the adjusted 640×640 compare runs took approximately 0.57 s
  inference and 0.71–0.72 s in `run_analysis` after image decoding and model
  loading. These two concurrent single-photo runs are not a tray benchmark.
  MPS training exists in historical logs, but MPS was unavailable in this tool
  session. The CLI checks availability and supports explicit CPU execution.

The local smoke artifacts are under ignored `outputs/soybean-val-0012-adjusted/`,
`outputs/soybean-val-0013-final/`, and `outputs/soybean-validation-smoke-evaluation/`.
To reproduce them with fresh output names:

```bash
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl \
  .venv/bin/python experiments/grain_counting/analyze_grain_sample.py \
  data/processed/soybean_hole/validation/images/test_0013.jpg \
  --species soybean --provenance natural-source --mode compare --device cpu \
  --min-area-fraction 0.005 --distance-threshold 20 \
  --output outputs/soybean-val-0013-reproduction
```

The prefix `test_` here comes from the source dataset's published file name;
`selected_images.csv` assigns both images to the new grouped **validation**
split. No soybean test-split inference is implied.
