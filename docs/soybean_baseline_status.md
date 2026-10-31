# SoyMate computer-vision status

Audit of the repository and locally saved artifacts on 31 October 2026. **The working result is a soybean Hole bounding-box detector, not the proposed end-to-end grain-intake product.** No model was trained or evaluated for this audit. Experiment outputs and datasets under `runs/` and `data/` are Git-ignored; links to them below work only where those local artifacts exist ([.gitignore](../.gitignore)).

## Intended workflow

1. A collector photographs a representative sample of pea or lentil grains on a contrasting matte background under a defined capture protocol.
2. Separate and count individual grains; associate visible defects with each grain, including grains with several defects.
3. Classify or otherwise label each grain, show an annotated image, and aggregate grain-level classifications into a sample percentage with an uncertainty interval.
4. Compare the result with a user-selected, appropriately sourced threshold and show a cautious result or warning in a usable interface.

This is the **planned** workflow in [CONTEXT.md §§5, 7 and 9](../CONTEXT.md#5-product-what-needs-to-be-built), not a description of the current detector. Visible surface damage is not a measurement of hidden infestation ([CONTEXT.md §3](../CONTEXT.md#3-the-problem-and-domain-data)).

## Stage-by-stage status

| Stage | Status | Evidence and boundary |
|---|---|---|
| Input image and capture conditions | **Planned** for the product; dataset ingestion **implemented and tested** | [CONTEXT.md §§5, 9](../CONTEXT.md#5-product-what-needs-to-be-built) proposes phone photos and a capture protocol. [Preparation](../scripts/prepare_soybean_holes.py), [training configuration](../runs/soybean_hole/baseline/args.yaml) and [log](../runs/soybean_hole/baseline.log) use published 640×640 soybean JPEGs; no product photo capture or quality check was found. |
| Multi-grain separation and counting | **Planned** | Threshold/contour separation and counting are specified in [CONTEXT.md §7](../CONTEXT.md#7-method); no such pipeline or count evaluation was found in the current project code. |
| Visible-hole detection | **Implemented and tested** as a limited baseline | YOLO11n training and validation are recorded in the [log](../runs/soybean_hole/baseline.log), [metrics](../runs/soybean_hole/baseline/results.csv) and [prediction montage](../runs/soybean_hole/baseline/val_batch0_pred.jpg). There is no verified product integration. |
| Attribute holes to individual grains | **Planned / not found** | The detector returns Hole boxes, but no grain masks, grain IDs, association logic or per-grain damaged/sound output were found; the intended per-grain workflow is described in [CONTEXT.md §7](../CONTEXT.md#7-method). |
| Other quality classes | **Planned** | Sound, broken, stained and foreign material are product targets in [CONTEXT.md §5](../CONTEXT.md#5-product-what-needs-to-be-built). The [preparation script](../scripts/prepare_soybean_holes.py) retains only Hole; no trained classifier for those other classes was found. |
| Sample-level percentage and uncertainty | **Planned** | [CONTEXT.md §7](../CONTEXT.md#7-method) proposes class percentages and Wilson intervals; no aggregation implementation or sample-level evaluation was found. |
| Decision support and user interface | **Planned** | Selectable thresholds, warnings and an upload/annotated-photo demo are specified in [CONTEXT.md §5](../CONTEXT.md#5-product-what-needs-to-be-built); no working UI or decision implementation was found. |
| French pea/lentil evaluation | **Planned / not found** | [CONTEXT.md §§5, 8](../CONTEXT.md#5-product-what-needs-to-be-built) proposes a transfer study. No French-pulse model evaluation, transfer curve or result artifacts were found among the current data, notebooks and runs. |

## What actually ran

The [executed review notebook](../notebooks/01_soybean_data_review.ipynb) inventories images, YOLO labels and metadata, plots examples and checks the existing grouped manifest. The only project preparation script copies selected **full images** and converts Hole boxes; it does not crop, segment or mask the background ([script](../scripts/prepare_soybean_holes.py), [prepared example montage](../data/processed/soybean_hole/prepared_examples.png)). Ultralytics takes these JPEGs at `imgsz=640` and produces predicted Hole bounding boxes with confidence scores, not whole-grain classes or sample percentages ([configuration](../runs/soybean_hole/baseline/args.yaml), [validation predictions](../runs/soybean_hole/baseline/val_batch0_pred.jpg)). The saved plots show boxes over images; no separate product inference workflow was found.

The earlier audit estimated 97.8% of published photos had one large seed component, with exceptions such as a second partial seed ([findings §4](../research/soybean_bruchid/findings.md)). The validation montage **does include** `train_0832.jpg`, assigned to the new validation split, with a second partially visible soybean; its annotated hole has no displayed prediction in the paired montage ([selection](../data/processed/soybean_hole/selected_images.csv), [labels](../runs/soybean_hole/baseline/val_batch0_labels.jpg), [predictions](../runs/soybean_hole/baseline/val_batch0_pred.jpg)). That is a single incidental multi-grain example; no systematic evaluation on tray photos, separation, counting or attribution is evidenced. The original filename prefix refers to the published folder, not the new split.

## Data and split

The local v2 release is Shinde et al.'s soybean pulse-beetle dataset, Mendeley DOI [10.17632/d97rjyk2tz.2](https://doi.org/10.17632/d97rjyk2tz.2), CC BY 4.0 ([dataset README](../data/raw/Soybean_Seed_Dataset/Readme.md), [CONTEXT.md §6.1](../CONTEXT.md#61-main-soybean-with-beetle-damage-mendeley-d97rjyk2tz)). Its published image folders are **not** the evaluation split: the [notebook](../notebooks/01_soybean_data_review.ipynb) matched all 2,726 filenames to the earlier [grouped manifest](../research/soybean_bruchid/resplit_by_original.csv), with no duplicated names, missing groups or retained groups assigned to multiple new splits. According to that manifest, 217/272 published validation and 229/274 published test images share an original group with published train. The earlier audit describes v1 filename and image-hash matching; this notebook did not independently reproduce that mapping ([audit §§1, 2.5 and 5](../research/soybean_bruchid/findings.md)).

[Preparation](../scripts/prepare_soybean_holes.py) discards manifest-marked rows, retains original Hole class 1 and remaps it to class 0, writes empty labels when no Hole is annotated, and leaves raw labels unchanged. Empty Hole labels are **candidate negatives**, not verified hole-free images. It keeps all retained training variants and chooses the lexicographically smallest retained v2 filename for each validation/test group; no reliable unaugmented-original indicator was available. The manifest before this selection retains 1,715/354/365 train/val/test images; the derived evaluation sets are smaller ([audit §5](../research/soybean_bruchid/findings.md), [selected images](../data/processed/soybean_hole/selected_images.csv)).

| Derived split | Images | Groups | Hole boxes | Candidate negatives |
|---|---:|---:|---:|---:|
| Train | 1,715 | 816 | 1,211 | 1,179 |
| Validation | 175 | 175 | 124 | 118 |
| Test | 175 | 175 | 121 | 124 |

Source: [generated counts](../data/processed/soybean_hole/counts.yaml). The audit's manual 100-image review reported 15 images with clear errors and nine doubtful cases, including missing boxes and hilum/Hole confusion; it also reported unlabelled visible defects and Healthy boxes coexisting with defects ([findings §3](../research/soybean_bruchid/findings.md)). The notebook's structural and count checks do not prove that boxes are complete or biologically correct.

## Run and evaluation

A one-epoch smoke test used 5% of train (86 images) and the full grouped validation set; it verified the execution path, not baseline performance ([smoke log](../runs/soybean_hole/smoke.log), [smoke metrics](../runs/detect/runs/soybean_hole/smoke/results.csv)). The baseline started from [YOLO11n pretrained weights](../data/weights/yolo11n.pt), using Ultralytics 8.4.194 / PyTorch 2.15.0, 8 epochs, all 1,715 training images, 640 input size, batch 8, seed 42 and Apple M5 Pro MPS. The auto-selected optimizer was AdamW; the final epoch time was 289.386 seconds. The log warns that some MPS operations were nondeterministic ([configuration](../runs/soybean_hole/baseline/args.yaml), [log](../runs/soybean_hole/baseline.log), [epoch metrics](../runs/soybean_hole/baseline/results.csv), [commands and weight hash](../README.md#soybean-hole-only-baseline)). The saved [best checkpoint](../runs/soybean_hole/baseline/weights/best.pt) was validated on 175 images with 124 annotated Hole boxes; its reported results were:

| Box metric | Validation result |
|---|---:|
| Precision | 0.823 |
| Recall | 0.563 |
| mAP@0.50 | 0.640 |
| mAP@0.50:0.95 | 0.427 |

Source: [final validation log](../runs/soybean_hole/baseline.log) and [results.csv](../runs/soybean_hole/baseline/results.csv). Precision is the fraction of predicted boxes matched to an annotated Hole; recall is the fraction of annotated Hole boxes matched by predictions. Matching uses box intersection-over-union (IoU). AP summarizes the precision–recall curve across confidence scores; with one class, mAP is that class's AP. `mAP@0.50` matches at IoU 0.50; `mAP@0.50:0.95` averages AP over ten IoUs from 0.50 through 0.95. These are box-level measures, not grain-level accuracy or percentage error.

The saved arguments specify `conf: null`, `iou: 0.7`, `split: val`. In the locally installed Ultralytics 8.4.194 code, a null detection-validation confidence becomes **0.001** for collecting predictions; **0.7 is NMS IoU**, not the box-matching IoU. Precision and recall are reported at the confidence maximizing the smoothed validation F1 curve at IoU 0.50; the saved [F1 curve](../runs/soybean_hole/baseline/BoxF1_curve.png) shows approximately **0.245**, selected on this same validation set, not an independently fixed deployment threshold. The montage displays predictions above 0.25, so absence from a montage is not proof no lower-confidence prediction existed. These details were checked in the local installed package's `ultralytics/engine/validator.py`, `models/yolo/detect/val.py`, `utils/metrics.py` and `utils/plotting.py`, whose version is locked in [uv.lock](../uv.lock). The [args](../runs/soybean_hole/baseline/args.yaml) and [log](../runs/soybean_hole/baseline.log) record validation on `val`; the prepared test split was counted and checked during preparation, but no test model inference or evaluation is evidenced in the saved runs.

## Risks and next steps

- **Labels and selection:** Missing boxes can make a correct detection look false; incorrect or ambiguous boxes can distort both false positives and false negatives. Candidate negatives may contain holes. The one-variant evaluation is reproducible but depends on which transformed image was selected ([audit §3](../research/soybean_bruchid/findings.md), [selection code](../scripts/prepare_soybean_holes.py)).
- **Grouping:** No retained manifest group crosses the new splits, but the original-photo identity relies on the earlier v1/hash reconstruction. Filename and label-count checks do not independently establish image identity or rule out unrecognized related photos ([notebook](../notebooks/01_soybean_data_review.ipynb), [audit §5](../research/soybean_bruchid/findings.md)).
- **Shortcuts and domain:** The earlier audit reported 505 of 513 black-background images were bruchid-damaged and dates correlated with classes. The baseline uses full images including background/date; the effect on its predictions has not been measured. Soybean macro photos, damage, lighting and scale differ from French pulse tray photos; transfer is not demonstrated ([audit §§2.3, 4, 6](../research/soybean_bruchid/findings.md), [CONTEXT.md §6.1](../CONTEXT.md#61-main-soybean-with-beetle-damage-mendeley-d97rjyk2tz)).

**Useful today:** manually inspect validation misses and apparent false positives against the original images; record ambiguous cases and select a validation operating point appropriate to the demo. Capture and label a small, clearly sourced set of mixed pea/lentil sample photos, and prototype grain separation/counting and hole-to-grain association with manual counts. Keep the existing test split held out while making development choices ([photo protocol and evaluation plan](../CONTEXT.md#8-evaluation)).

**Future validation:** independently verify group provenance and annotation completeness, evaluate shortcuts and performance by capture condition, and assess grain-level and sample-level errors on independently collected French-pulse photos, grouped by source photo or lot. After choices are frozen, evaluate the held-out soybean test set once; report its limits and a transfer curve only when measured ([CONTEXT.md §8](../CONTEXT.md#8-evaluation), [audit §9](../research/soybean_bruchid/findings.md)).

## Focused validation review and longer comparison

### Eight-epoch baseline review

The baseline's train box loss fell from 1.529 to 1.408 and classification loss from 11.368 to 1.545 over eight epochs; validation mAP@0.50 rose overall from 0.380 to 0.640 and mAP@0.50:0.95 from 0.210 to 0.427, but both dipped at epoch 4 before recovering. The logged precision/recall rose from 0.479/0.411 to 0.823/0.563, with substantial fluctuations. Each epoch's precision/recall uses that epoch's validation-selected smoothed maximum-F1 operating point, so changes do not describe a fixed-confidence curve ([results](../runs/soybean_hole/baseline/results.csv), [training plot](../runs/soybean_hole/baseline/results.png), [metric definitions above](#run-and-evaluation)).

The earlier CPU review evaluated the manifest-selected validation images with confidence-ordered one-to-one matching. Its [baseline metrics](../runs/soybean_hole/review_baseline_v2/metrics.json) and prediction records are preserved for the comparison below. Unmatched boxes are not automatically true errors: incomplete or ambiguous labels require human judgment. See the [README gallery instructions](../README.md#validation-comparison-gallery) for the maintained side-by-side viewer, its cached predictions and note export. This fixed-confidence review is distinct from the logged MPS validation at its F1-selected point; no test images are loaded.

At fixed confidence 0.10 and IoU 0.50, the baseline re-evaluation gives the following label-relative box counts by the **earlier audit's background category**. Positive images have at least one annotated Hole; they are not necessarily all truly positive images.

| Background | Images | Positive images | Annotated holes | Matched | Apparent FP | Apparent FN | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| White/light | 135 | 26 | 64 | 43 | 29 | 21 | 0.597 | 0.672 |
| Black | 35 | 30 | 59 | 34 | 53 | 25 | 0.391 | 0.576 |
| Intermediate | 5 | 1 | 1 | 1 | 1 | 0 | 0.500 | 1.000 |

These small, compositionally different groups contain only 26 and 30 annotated-positive images in the larger categories; the intermediate group is too small for a meaningful comparison. Boxes within an image are correlated, labels are incomplete, and background is confounded with capture session and type. Differences suggest questions for review, not a causal measurement of the background shortcut ([selection manifest](../data/processed/soybean_hole/selected_images.csv), [background audit](../research/soybean_bruchid/findings.md), [computed counts](../runs/soybean_hole/review_baseline_v2/metrics.json)). No reliable rotation/flip/crop **variant type** is stored in the selected manifest; its `type` field describes damage category, not augmentation. A variant-type breakdown cannot be inferred from it ([audit §5](../research/soybean_bruchid/findings.md)).

### Longer run: measured comparison

One comparison was run from the same pretrained YOLO11n weights and the same prepared paths, with the baseline settings unchanged except `epochs=40`, `patience=7` and a separate output name. It completed all 40 epochs in 1,424.43 seconds (23m 44s through the last epoch); early stopping did not trigger. In this installed Ultralytics version, checkpoint fitness and early stopping use validation mAP@0.50:0.95. The final [best checkpoint](../runs/soybean_hole/long40/weights/best.pt) was selected at epoch 40. Commands and output:

```bash
set -o pipefail
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/yolo detect train model=data/weights/yolo11n.pt data=data/processed/soybean_hole/data.yaml epochs=40 patience=7 imgsz=640 batch=8 device=mps workers=0 seed=42 project="$PWD/runs/soybean_hole" name=long40 exist_ok=False plots=True 2>&1 | tee runs/soybean_hole/long40.log
```

The [long-run configuration](../runs/soybean_hole/long40/args.yaml), [log](../runs/soybean_hole/long40.log), [per-epoch CSV](../runs/soybean_hole/long40/results.csv), [learning curves](../runs/soybean_hole/long40/results.png), [validation PR curve](../runs/soybean_hole/long40/BoxPR_curve.png) and [review metrics](../runs/soybean_hole/review_long40/metrics.json) are local, ignored artifacts. The original run was not overwritten. Both review outputs record the same selection-manifest SHA-256 `984e2852de965f2bf5912e5d463b08c0127dae451bd3a7695bc0b4259c9d0ad1`. The longer run used the same prepared validation path and did not change the selection; the old run did not record a historical content hash, so its exact input bytes cannot be independently established from its log. A [fingerprint of current validation images and labels](../runs/soybean_hole/long40/validation_fingerprint.txt) was recorded during the longer run.

| Final validation of selected checkpoint | 8 epochs | 40 epochs |
|---|---:|---:|
| Precision | 0.823 | 0.882 |
| Recall | 0.563 | 0.581 |
| mAP@0.50 | 0.640 | 0.709 |
| mAP@0.50:0.95 | 0.427 | 0.481 |

The longer run's train box/class losses went from 1.601/11.857 at epoch 1 to 1.189/0.978 at epoch 40; validation mAP@0.50:0.95 rose overall from 0.290 to 0.480 with fluctuations, including 0.224 at epoch 2. Its best-checkpoint final revalidation reports 0.481 (epoch CSV rounds the training-time evaluation to 0.480); final reported precision is 0.882 versus 0.874 in the epoch CSV. The saved F1 plots select approximately 0.245 confidence for the old checkpoint and 0.418 for the longer checkpoint, so the precision/recall pairs above are **not at a common threshold** ([baseline log](../runs/soybean_hole/baseline.log), [long log](../runs/soybean_hole/long40.log), [long F1 curve](../runs/soybean_hole/long40/BoxF1_curve.png)).

This is one development-set comparison, not a controlled estimate of the effect of duration alone: Ultralytics' unchanged `close_mosaic=10` disables mosaic throughout an eight-epoch run but only for the last ten epochs of a 40-epoch run; its learning-rate schedule also depends on total epochs. The MPS nondeterminism warnings remain. The gain could depend on these schedule differences, data composition, label noise or chance; none has been isolated ([configuration](../runs/soybean_hole/long40/args.yaml), [log](../runs/soybean_hole/long40.log)).

### Fixed-confidence screening trade-off

The following are **CPU re-inference**, confidence-ordered greedy one-to-one box matching at IoU ≥ 0.50, with NMS IoU 0.70. Counts are against 124 annotated holes on the same 175 validation images. Precision and recall here use explicit hard thresholds, rather than the library's interpolated F1-selected reporting; compare them within this table. FP/FN are *apparent* relative to incomplete annotations ([baseline metrics](../runs/soybean_hole/review_baseline_v2/metrics.json), [longer-run metrics](../runs/soybean_hole/review_long40/metrics.json)).

| Confidence | Baseline precision / recall | Baseline matched / apparent FP / FN | Longer precision / recall | Longer matched / apparent FP / FN |
|---:|---:|---:|---:|---:|
| 0.05 | 0.311 / 0.702 | 87 / 193 / 37 | 0.405 / 0.758 | 94 / 138 / 30 |
| 0.10 | 0.484 / 0.629 | 78 / 83 / 46 | 0.524 / 0.702 | 87 / 79 / 37 |
| 0.20 | 0.758 / 0.581 | 72 / 23 / 52 | 0.669 / 0.669 | 83 / 41 / 41 |
| 0.40 | 0.912 / 0.419 | 52 / 5 / 72 | 0.864 / 0.613 | 76 / 12 / 48 |
| 0.60 | 1.000 / 0.242 | 30 / 0 / 94 | 0.938 / 0.492 | 61 / 4 / 63 |

For a **human-reviewed screening demonstration**, use the longer checkpoint at provisional confidence **0.10**: on this validation set it matches 87 annotated boxes versus 83 at 0.20, with 79 rather than 41 unmatched predictions to review. Lowering to 0.05 matches seven more but raises unmatched predictions to 138. This choice prioritizes finding candidate holes while limiting review burden; it was selected using this same validation set and is not independently validated or a safe acceptance threshold. Even at 0.10, 37 annotated holes were unmatched. Confirm labels and choose an operating point with the intended reviewer before relying on it; detection confidence is not a probability of grain safety, and the system cannot infer hidden infestation or assess French pulses from these results.
