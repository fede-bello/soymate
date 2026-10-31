<p align="center">
  <img src="assets/logo.png" alt="SoyMate logo" width="260">
</p>

# SoyMate

**A seed grade from a phone photo, that the farmer can check too.** At grain intake, someone at the cooperative counts damaged seeds by eye, and that count sets what the farmer is paid. SoyMate finds every seed in a few phone photos, classifies it (sound, broken, stained, unripe, insect hole), and gives the share of each defect with its uncertainty and a verdict: pass, take more photos, or fail.

Project for **Hack the Fork Paris 2026** (AgroParisTech, Palaiseau, 30 October to 1 November 2026), **Track 3: Protein sovereignty, from French fields to the proteins of tomorrow**.

> **Single source of truth:** [`CONTEXT.md`](CONTEXT.md), starting with **§0 Current plan** (31/10), which supersedes the pre-event plan in §1, §5 and §8-§12. Every figure carries its source (`[S#]`) and a confidence tag.

---

## Why

- Seed damage is high and uneven: in 2025, French lentil truckloads averaged 24.4 % beetle-damaged seeds (from 1 % to 75 % between lots), the highest of the 2021-2025 survey. Sources in [`CONTEXT.md` §3](CONTEXT.md).
- The damage sets the price, but it is counted by eye, varies between people and sites, and the farmer cannot check it.
- SoyMate does not remove damage. It makes the grade fast, consistent and visible to both sides.

## Why soybean first, lentil next

- **Soybean** is the only bean with public labelled photos of damaged seeds (~8,000). We found none for lentils, peas or faba beans. French food soy is real (45 kt/yr) but pays only 20 to 70 €/t more than feed, so it is where we build and test the method, not the business.
- **Lentil** is where the value is: ~550 €/t between food and feed outlets. Taking the tool there needs French lentil photos labelled by graders, ~1,000 seeds per grade, calibration against the visual reference count, and a pilot with one cooperative.
- AI grading of pulses already sells in Australia (Cropify). Nobody publicly covers French soy or pulses. Full analysis: [`docs/soymate_viability_brief.pdf`](docs/soymate_viability_brief.pdf).

## How

1. **Photo:** phone, plain matte background, a few photos per sample.
2. **Find:** threshold and contours (a pretrained segmenter such as SAM if seeds touch).
3. **Classify:** frozen pretrained features (DINOv2) plus a small linear classifier, trained on CPU.
4. **Grade:** percentage per class with a Wilson interval; "take more photos" when the interval crosses the threshold.

The public soybean defect dataset leaks (80-84 % of its test images are copies of training images), so we re-split it. Results to produce at the event: leaky vs clean split, per-class F1, a check that the model is not recognising the source dataset, transfer between soybean datasets, and lot-level error on real hand-labelled photos.

## Repository layout

```
.
├── README.md              this file
├── CONTEXT.md             single source of truth (§0 = current plan)
├── pyproject.toml         Python dependencies (uv)
├── assets/logo.png
├── docs/
│   ├── soymate_viability_brief.pdf   viability, money, competition, assumptions, sources (current)
│   ├── figures/viability/            charts used in the brief
│   ├── aws_setup.md                  the team's AWS dev box: connect, run, back up
│   ├── soymate_team_plan.pdf         pre-pivot team plan (outdated: plans own pea/lentil photos)
│   └── soymate_data_report.pdf       pre-event data report
├── pitch/                 pitch deck: link, outline, slides to fill, backup copy of the slides
├── research/
│   ├── viability/         soy market, pulses market, grading and competition, synthesis
│   ├── critique.md        adversarial review of the plan (31/10)
│   ├── soybean_bruchid/   audit of the soybean beetle-damage dataset + leak-free re-split CSV
│   ├── other_datasets/    survey of seed image datasets + new_candidates.md (31/10 search)
│   └── context/           intake standards, soybean for food, competitors, photo protocol
├── scripts/
│   ├── aws/               EC2 bootstrap, Session Manager connect, dataset downloader
│   └── docs/              generator of the viability brief PDF
├── event/                 Hack the Fork participant guide
└── archive/               earlier idea exploration (ideas 1 to 8), kept for reference
```

## Hackathon rules we follow

- No solution code, model, prototype, results or pitch deck before the event starts. Everything in this repo up to the event is desk research and data exploration; no model was trained.
- Pre-existing resources (public datasets, pretrained models, the derived CSVs and analyses in `research/`) are declared at submission. See [`CONTEXT.md` §14](CONTEXT.md).
- Data provenance is labelled as measured, sourced, assumed or synthetic.

## Data

Datasets are downloaded at the event, never committed (`data/` is git-ignored). The full dataset map, licences and download links are in [`CONTEXT.md` §6](CONTEXT.md). Main ones:

| Dataset | Use | Licence |
|---|---|---|
| Soybean beetle damage (Mendeley d97rjyk2tz) | Insect holes, seed-coat cracks, sound seeds; audited and re-split | CC BY 4.0 |
| Soybean Seeds, 5 classes (Mendeley v6vzvfszj6) | Broken, stained, immature, skin-damaged, intact; 5 multi-seed originals | CC BY 4.0 |
| Ghana seed varieties, soybean part (Mendeley t94nzy4ptz) | Real multi-seed phone photos: seed count, false positives on sound seeds | CC BY 4.0 |
| Mechanical-harvest soybean (Mendeley hwdtghttp7) | Multi-seed images with intact / crushed / impurity masks (split by id prefix) | CC BY 4.0 |
| Indonesian soybean varieties (Mendeley c733bjz4m3) | Multi-seed flatbed scans | CC BY 4.0 |
| GrainSet (Scientific Data 2023) | Broken and pest-damaged cereal kernels, expert labels | CC BY 4.0 |
| Radio_lentille (Terres Inovia, Hugging Face) | X-rays of bruchid-damaged French lentils, lot damage counts | MIT |

Download with `uv run python scripts/aws/download_datasets.py [name ...]` (see the script's docstring).

## Team

Three people, Hack the Fork Paris 2026. Repository is private.
