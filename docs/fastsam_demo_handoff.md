# SoyMate demo handoff

## Immediate organizer question

The participant guide excludes “Insects” and animal feed, but does not say whether detecting insect damage on human-food grain is excluded. **Eligibility is unconfirmed:** ask the organizers and record their answer. The local guide says to submit the official-template PDF and online project sheet before **Sunday, November 1, 09:30 Paris time**, and says pitches use a shared computer. Check for newer organizer instructions and test that computer. Saturday campus closing is 18:00. The online pitch deck described in `pitch/README.md` belongs to a teammate; local slide edits do not update it.

## Demo, in two separate images

The ignored local directory `outputs/hackathon-demo/` contains fresh reports and a portable `bundle/`. Open `bundle/index.html` offline. The bundle is not tracked by Git; copy the whole directory or the ZIP to the presentation machine. It includes both required checkpoints, source images, reports, code and a silent, precomputed 24-second backup video. `review.html` starts with all candidates kept; the saved JSON is a record, not an import file.

1. **Pea candidate review:** open `bundle/outputs/pea-40/review.html`. The model produced 48 mask candidates and zero visible-hole flags. Uncheck IDs **4, 12, 14, 17, 20, 34, 37, 44**; these outline background gaps. The retained total changes from 48 to 40 while the original model count remains visible. Download the decisions for a portable record. The overview does not redraw after rejection; the original manifest is unchanged. Masks and padded crops may include neighbours. The model was not evaluated for damage on this photo, and zero flags do not establish absence of holes.
2. **Soybean visible-hole example:** open `bundle/outputs/soybean-hole/report.html`. On grouped validation image `test_0013.jpg`, the contour pipeline found one component and the soybean-trained detector flagged a visible feature. This is a different photo and species, and an example chosen during development; it is not a multi-grain pea or lentil damage test. The input filename prefix reflects the published split, not the grouped split. Image and detector settings were inspected together during development.

The pea and soybean datasets are real; no synthetic damage is used in this demonstration. Neither result is a grade or a lot decision. No visible flag does not establish that a grain is safe or free of hidden infestation. A sampling interval would not account for detection errors, sampling bias or hidden damage.

## What was checked on the pea example

A visual image-only pass placed 40 approximate centres on the unannotated upright image (`outputs/hackathon-demo/pea-manual-count.png` and `pea-manual-centres.json`). Each marked centre falls in a distinct retained candidate; the eight remaining masks are background. No marked centre was missed and no candidate contained multiple marked centres. The marked image was inspected visually for gaps and duplicates, but this was **not a blinded independent human recount**: the same assistant had previously seen the model overlay and expected count. Ask a teammate to recount and verify the image without the overlay. Centre containment alone does not prove exact mask boundaries or reveal hidden grains.

Separately, the existing polygon evaluator matched 40 of 40 source polygons at IoU ≥ 0.5 and found eight extra candidates. This is the same development photo used to select the approach, not a held-out accuracy result. The original polygon labels and the manual centre check are distinct references; neither establishes hole-detection accuracy.

## Re-run the bundled demo

From inside `bundle/`, on a compatible machine with Python 3.14, `uv` and the locked dependencies installed:

```sh
uv sync --locked --group baseline
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/python scripts/experiments/analyze_fastsam_grains.py data/raw/pea_zenodo_21110940/images/20210406_145931.jpg --output outputs/pea-live --confidence 0.4 --compare-masked 0
YOLO_CONFIG_DIR=/tmp/soy-yolo MPLCONFIGDIR=/tmp/soy-mpl .venv/bin/python scripts/analyze_grain_sample.py data/processed/soybean_hole/validation/images/test_0013.jpg --species soybean --provenance natural-source --mode crops --device cpu --min-area-fraction 0.005 --distance-threshold 20 --output outputs/soybean-live
```

Use fresh output directories. The CLI needs Python, compatible installed dependencies and checkpoints; installing dependencies may require network access. The precomputed HTML, images and video need no Python, models or network, but browser JavaScript and permission to open local files are required for interactive review/export. Browser storage is tied to the report location and can be disabled or cleared; export before closing. Import is not implemented. Copying a directory changes that storage location.

The fresh pea run took 3.49 seconds internally on the local CPU; the fresh soybean command reported 1.74 seconds after imports. These are single runs, not latency guarantees. Confirm local file access, video decoding and review interaction on the actual presentation computer; headless Chrome could not launch in the agent environment. The review JavaScript was exercised offline in a simulated DOM, including eight rejections, saved state and JSON export, but that does not replace a browser rehearsal.

## Provenance and weights

- Pea photo and polygons: Gulzar and Ünal, [Zenodo 21110940 v1.0](https://zenodo.org/records/21110940), CC BY 4.0. Attribution and modifications must accompany reuse. Input SHA-256: `57038c60dac33461a7cd84133ccc328342322a77a1bcf4d09c398863342482a9`.
- Soybean photo and training data: Shinde et al., [Mendeley d97rjyk2tz v2](https://doi.org/10.17632/d97rjyk2tz.2), CC BY 4.0. The prepared grouped split is an earlier project research artifact. Input SHA-256: `87f4f17f6b60cde0e1a56483391961c1d1d2a435cab04ce6452d70d362cf12b3`.
- FastSAM-small checkpoint: `c9f78716a81c7aff0d608ccc73e1b82ab3aaad86005049f6a92106a0be6d0844`.
- Locally trained soybean hole checkpoint: `bf9f04f017f30c81f19385b8542a8202a0fb31cef6daa8728fbd878b733eed93`. It is not publicly downloadable and is not interchangeable with generic YOLO weights.
- The FastSAM repository and Ultralytics implementation state AGPL-3.0; the FastSAM README separately describes the model as Apache 2.0. Applicability to this exact checkpoint and distribution remains unresolved. Review terms before sharing the bundle beyond the team or deploying it. SoyCult image rights were not established; SoyCult is not included.

Declare the datasets, pretrained models, implementation libraries, prior research and grouped split at submission. See `docs/fastsam_grain_experiment.md` and `docs/soybean_baseline_status.md` for the earlier validation, caveats and attribution details.
