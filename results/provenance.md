# Provenance of every number and resource (submission, 1/11/2026)

Tags: **measured** = computed at the event by a committed script in this repo (re-runnable, see
`results/README.md`); **sourced** = taken from a third-party document or dataset page, with its reference;
**assumed** = our assumption, not verified; **synthetic** = produced by simulation, never a real-world claim.

## Numbers used in the pitch and the brief

| Claim | Value | Tag | Where it comes from |
|---|---|---|---|
| Published d97rjyk2tz test images sharing an original photo with published train | 229/274 (83.6 %); 97.1 % share a 30 s capture burst | measured | `scripts/data/make_splits.py`, `data/splits/SUMMARY.json` |
| Macro F1, published split, full image (dinov2-small + logreg) | 0.885 [0.832, 0.932] | measured | R1, `results/r1_leaky_vs_clean.json` |
| Macro F1, our burst split, masked crop | 0.852 [0.801, 0.900] | measured | R1 |
| insect_hole F1 0.99-1.00 | not a valid hole result (session confound) | measured, flagged | R1, R2 session control |
| Per-class F1 within each dataset, with grouped CIs | soybean broken 0.82, sound 0.82; Lin macro 0.91 | measured | R2 |
| Dataset-ID probe accuracy on sound seeds | 100 %, also texture-only | measured | `eval/dataset_id.py` |
| Transfer soybean <-> Lin with 0/10/50 labels | 10 target labels beat ~1,000 other-setup images | measured | R3 |
| Seed-count error on real Ghana photos | MAPE 1.1 % on 7 complete photos | measured | R4a |
| Lot-level % crushed error on held-out harvest originals | MAE 1.5 pp, but per-seed F1 0.48 (errors cancel) | measured, dataset masks as reference | R4b |
| Lot-level % error on hand-labelled real photos (~450 seeds) | pending | measured (labels by a team member at the event) | `scripts/labels/` |
| Wilson 95 % intervals on lot percentages | formula | measured | `eval/harness.py::wilson` |
| Ghana published per-seed boxes miss seeds in shadow | e.g. 89 boxes vs ~257 seeds in Afayak G15; 7/105 photos complete | measured | `scripts/data/ghana_index.py`, QC overlays |
| Dataset contents (image counts, classes, licences) | see CONTEXT.md §6 | sourced | dataset pages [S29]-[S35], [S41]; counts re-checked on download |
| Market, threshold and price figures | see CONTEXT.md §18 claims register | sourced | CONTEXT.md §17 sources |
| Simulated lots built from labelled crops | if shown, labelled "synthetic" | synthetic | none produced yet |

## Prior resources (made before the event, declared)

- Datasets (public, licences re-checked at download, `data/raw/MANIFEST.json`): soybean d97rjyk2tz v1 and
  v2 (CC BY 4.0), Lin soybean seeds v6vzvfszj6 (CC BY 4.0), Ghana seed varieties t94nzy4ptz (CC BY 4.0),
  mechanical-harvest soybean hwdtghttp7 (CC BY 4.0). Downloaded but unused so far: GrainSet, corn1000
  (CC BY-NC 4.0), Zenodo pea 21110940 and faba 18226381 (CC BY 4.0).
- Pretrained model: DINOv2 (Meta, `facebook/dinov2-small`), used frozen.
- Pre-event analyses (exploration only, no training): the d97rjyk2tz audit in `research/soybean_bruchid/`
  and `resplit_by_original.csv`. The split was **regenerated at the event** by
  `scripts/data/make_splits.py` from the raw files and is stricter (burst grouping); the pre-event CSV is only
  read to report agreement (98.8 % same photo groups).
- Market, viability and dataset research in `research/` and `docs/` (desk research).
- Code idea reused: border-colour seed masking from a teammate's `scripts/grain_pipeline.py`
  (branch `jp/soybean-baseline`, written at the event).

## Changes made to CC BY datasets (attribution requirement)

Images were cropped to one seed, the background outside the seed mask painted grey, resized to 224 px, and
labels remapped to our classes (`scripts/data/make_crops.py`). Duplicates and unlabelled images were removed.
