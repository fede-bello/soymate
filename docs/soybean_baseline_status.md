# SoyMate computer-vision status

Audit of the repository and locally saved artifacts on 31 October 2026. **The working result is a soybean Hole bounding-box detector, not the proposed end-to-end grain-intake product.** No model was trained or evaluated for this audit. Experiment outputs and datasets under `runs/` and `data/` are Git-ignored; links to them below work only where those local artifacts exist ([.gitignore](../.gitignore)). The preparation script and dependency changes are currently uncommitted; status can change after this audit.

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
