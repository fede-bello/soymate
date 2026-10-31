# Pitch handoff

The guide specifies four minutes plus two minutes of questions, a PDF on the official template containing a code/demo link, and an online non-confidential project sheet, due Sunday November 1 at 09:30 Paris time. It says the presentation uses a shared computer; check for newer organizer messages and test local files and video there. The online deck at https://claude.ai/artifact/AiZ254A4Y2tTDnwKEr5GH2 is private to Fede until shared: **local `slides/` edits do not update that deck**. Transfer the corrected content to the actual submission and obtain the official template.

**Eligibility remains open:** the guide excludes “Insects” but does not clarify whether this includes detecting grain damage. Ask an organizer; do not present an interpretation as a confirmed answer.

## Four-minute story

- 0:00–0:40: identify the cooperative intake technician and the problem of reviewing grain quality. Scope the 2025 lentil survey correctly: 24.4% mean damaged grains per lot among 40 measured samples.
- 0:40–1:15: show the current prototype and identify its two components: FastSAM masks and a soybean-trained visible-hole detector.
- 1:15–2:25: open the 40-pea review and reject background gaps; then show the separate soybean visible-hole example. The pea photo has no reference hole labels. If the live report fails, use the precomputed silent video or report bundle.
- 2:25–3:10: state evidence and limits: one pea development image, imperfect soybean validation labels, no measured natural multi-grain damage accuracy, and no view of hidden infestation.
- 3:10–4:00: describe the proposed path to French lentils: expert-labelled images, representative sampling, independent evaluation and a cooperative pilot. Savings, disputes avoided and income effects are hypotheses.

Use the local backup bundle described in `docs/fastsam_demo_handoff.md`. Remove unmeasured placeholders, unsupported claims of grading, automatic verdicts, multiclass classification or lentil transfer. The prototype does not compute a sampling interval; sampling uncertainty, model error and sample-selection bias are distinct. State measured versus model-predicted versus human-reviewed outcomes.

## Q&A

- **Does it work on lentils?** Not validated; the current examples are pea masks and a different soybean hole image.
- **Does a zero flag mean healthy?** No; the detector can miss visible damage and cannot see hidden infestation.
- **What is the error?** The 40-pea development image produced 48 candidates, with eight background gaps; a prior polygon comparison matched 40 polygons. This is not a generalization estimate. Soybean box validation has incomplete labels and is not pea accuracy.
- **Can review recover a missed grain?** The current page can reject candidates; it cannot add a missed grain or split a merge.
- **Is value proven?** No. The user and proposed pilot are clear; decision impact and willingness to pay remain to be tested.
