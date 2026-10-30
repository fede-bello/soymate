# Hack the Fork Paris 2026: research index

> This is an archive of the earlier idea exploration. The project is now **SoyMate**, formerly idea 9.

Research done on 29 and 30/10/2026, before the event: desk research and data exploration, without training any model (the rules forbid it). All downloaded data was deleted; only these reports remain.

Summary to discuss with the team: `../ideas_overview.pdf` (5 pages).

## The 8 ideas

Each dossier has: verified or unverified hypotheses, an audit of each dataset with download commands, the AI method, the MVP and demo script, an hour-by-hour plan with 3 roles and checkpoints, business case, impact, a 4-minute pitch with jury questions, risks and a rubric.

| # | Idea | Track | Score | Verdict | Dossier |
|---|---|---|---|---|---|
| 1 | Pea protein for the ingredients industry | 3 | 6,4 | Main (add the explanation from 2 and, optionally, 6) | [plans/1_pea_protein.md](plans/1_pea_protein.md) |
| 2 | Twin season (climate analogs) | 3 | 6,1 | Better as an explanatory layer for another idea | [plans/2_twin_season.md](plans/2_twin_season.md) |
| 3 | Bruchid risk in lentil and faba bean | 3 | 6,0 | Alternative with the best story | [plans/3_bruchids.md](plans/3_bruchids.md) |
| 4 | Early departmental yield | 3 | 5,9 | Solid plan B | [plans/4_departmental_yield.md](plans/4_departmental_yield.md) |
| 5 | Drone-based trial yield | 3 | 5,4 | Discard | [plans/5_drone.md](plans/5_drone.md) |
| 6 | Protein radar by basin | 3 | 5,6 | Only as an optional module of 1 | [plans/6_protein_radar.md](plans/6_protein_radar.md) |
| 7 | French lentil: where to recruit producers | 3 | 6,1 | Good, uncertain market | [plans/7_french_lentil.md](plans/7_french_lentil.md) |
| 8 | French pulses in canteens | 2 | 6,2 | Best alternative in Track 2 | [plans/8_pulses_canteens.md](plans/8_pulses_canteens.md) |

Scores estimated by us with the jury's weights (impact 30%, rigor 20%, AI 20%, economics 20%, execution 10%), before validating with mentors and having results.

## Exploratory analysis of idea 1

- [eda_idea1/README.md](eda_idea1/README.md): what the data says, how to cross them and what to train at the event. 44 plots in `eda_idea1/` (pea, climate, context). PDF with the main plots: `../idea1_data_report.pdf`.

- [../../CONTEXT.md](../../CONTEXT.md): **complete, self-contained context for idea 9** (for agents and for the team). Short plan for the team: `../../docs/soymate_team_plan.pdf`.
- [../../research/README.md](../../research/README.md): idea 9, quality control of pulses from a photo (computer vision). Audit of the soybean weevil dataset, 16 seed and grain datasets, standards, competition and photo protocol. PDF: `../../docs/soymate_data_report.pdf`.

## Data

- [datasets.md](datasets.md): map of more than 100 datasets, the 12 that matter, join keys, gaps and figures that contradict each other across sources.
- [datasets/safran.md](datasets/safran.md): SAFRAN/SIM2 climate data from Météo-France (the French national meteorological service), how to download and aggregate it (used by ideas 1, 2, 3, 4 and 6).
- `datasets/`: audits by domain (agronomy and plant health, geo/soil/climate, economics and markets, food, AI corpora and benchmarks) and the derived table `rpg_pulses_dept_year.csv`.

## Context and earlier audits

- [track3_context.md](track3_context.md): verified sector data, competitors, what the jury rewarded in 2025.
- First audits by idea (the dossiers expand them): [idea1_pea_protein_data.md](idea1_pea_protein_data.md), [idea1_pea_protein_market.md](idea1_pea_protein_market.md), [ideas2_4_time_series.md](ideas2_4_time_series.md), [idea3_bruchids.md](idea3_bruchids.md), [idea5_drone.md](idea5_drone.md).
- Original sources in `../docs/`: the participant guide and the two PDFs of initial ideas.

## What to confirm on Friday before 23:00

- With a mentor: whether a pea protein factory would find it useful to know in September how much protein it will receive, and to prepare the answer to "protein explains only 2% of national tonnage" (idea 1).
- With the organizers: that the exclusion of "insects" refers to insects as food, not to pests (idea 3).
- With the organizers: that pea and faba bean are eligible even if part of the crop goes to animal feed (ideas 2 and 4).
- With a mentor: whether conventional lentil is also oversupplied (idea 7).
- With the organizers: whether a public procurement project looks different from Ardoise, and which Bedrock models are available on AWS (idea 8).
- With a cooperative mentor: whether any volume decision is made in May-June (idea 2).
