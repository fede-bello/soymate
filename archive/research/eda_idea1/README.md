# Idea 1: what the data says (exploratory analysis report)

Exploratory analysis done on 2026-10-30, before the event, by three subagents: structure of the Pea_dataset, climate by crop phase, and farm-field and buyer context. **No model was trained** (hackathon rule): these are group means, descriptive decompositions, exploratory correlations and maps. The raw data was deleted; what remains are plots, three `findings.md` files and small derived CSVs.

PDF with the plots for the team: `../../../idea1_data_report.pdf`.

| Folder | Contents |
|---|---|
| [pea/](pea/findings.md) | 15 Pea_dataset plots: protein and yield by year and type, variance decomposition, genotype × environment, breeder protein class, site map, missing data |
| [climate/](climate/findings.md) | 17 SAFRAN climate plots by phase against protein and yield, 2018 vs 2023, 1981-2024 climatology, how much is known at each decision date |
| [context/](context/findings.md) | 12 plots and maps: RPG area, winter pea, trial coverage, trial-to-farm gap, national and per-basin protein, Roquette basin |

---

## 1. The data, in a table

| Dataset | Type | Granularity | Range | Role in the model |
|---|---|---|---|---|
| Pea_dataset, trials and measurements (INRAE, doi 10.57745/FW78RE) | Tabular | Site × variety × year (4,450 situations, 3,326 with protein) | 2013-2024 useful (+2003-04) | **Labels** (protein % DM, yield) and inputs (soil, type, breeder class, sowing) |
| SAFRAN / SIM2 (Météo-France) | Daily series on an 8 km grid | Cell → site or département | 1958 to yesterday (processed 1981-2024) | **Climate by phase** for training, scenarios for the rest of the season, live season |
| Climate of the Pea_dataset itself | Daily series by site | Only the season of each trial | 2001-2024 | Sensitivity check only (differs from SAFRAN) |
| Agreste SAA long series | Annual panel | Département × year | 2010-2025 | Farm-field yield (to go from relative yield to q/ha) |
| RPG (CAP parcels) | Vector, aggregated | Département × year × type | 2015-2024 | Weight of each département and winter share in the buyer's basin |
| Terres Univia quality surveys | Small table (PDF) | National (11 years) and 5 basins (35 values) | 2015-2025 / 2019-2025 | **Calibrate the level** of protein against what reaches the silos |
| Imagery | None | | | Not applicable: trial plots measure ~10 m² |

---

## 2. The 12 findings that matter

1. **The environment rules.** Of the variation in protein, ~84% is environment (year 24%, type 7%, site 14%, site × year 39%) and only 8% is the variety within the trial. For yield, ~88% is environment. The real unit of information is the trial (site × year × type): **~250 with protein**, not 3,326 rows. [pea/05]
2. **The year alone is not enough.** Annual means range from 20.9% (2018) to 24.9% (2023), but within the same year the trials spread with an SD of 1.7 points. What the model has to explain is **site × year** (~40% of the variation). [pea/15]
3. **23% threshold:** 51% of trials exceed it, but the share goes from 15% (2018) to 87% (2023). Spring 59%, winter 34%. [pea/01, pea/13]
4. **Variety is a stable shift and the breeder class captures it:** low −0.8, medium −0.3, high +0.3, very high +0.9 points relative to the trial, every year. But it depends on the type ("high" is +1.1 in winter and +0.1 in spring). [pea/08, pea/06, pea/07]
5. **Protein and yield barely relate** between trials (ρ −0.07 spring, −0.23 winter). Very high protein is usually stress (LE_SUBDRAY 2023: 29% with 21 q/ha). Both have to be predicted. [pea/03, pea/04]
6. **The climate signals are weak.** No exploratory climate-protein correlation exceeds |ρ| 0.27 (17 phase indices). And heat during grain filling goes with **more** protein, not less (+0.27 in winter). Total season rainfall says nothing: the signal is in the phase. [climate/08]
7. **Climate is confounded with the year.** In spring, heat vs protein gives ρ −0.31 between annual means but +0.23 within the year. With 12 years, a variable that separates 2018 from 2023 can "explain" a lot without being a cause. [climate/09]
8. **2018 and 2023 had equally hot grain fillings.** What separates them is something else: 2018 was sown late, dark (radiation z −1.2) and wet (soil moisture z +1.2); 2023 had the driest grain filling in 44 years in Eure-et-Loir and Aisne. [climate/15, climate/12, climate/13]
9. **At the decision date "flowering + 30 days" most of the grain-filling heat is still missing** (only 36% seen in spring and 20% in winter), and grouping by a single index does not visibly shrink the spread. **The pitch has to sell calibration, not precision.** [climate/02, climate/11]
10. **Trial protein is on the farm-field scale** (r 0.86 against the national series, bias +0.2 points; r 0.66 against the 35 per-basin means). **Yield is not:** the trial yields 1.36 times the farm field, and the trial-to-département correlation is only 0.35. Yield is always relative. [context/07, context/08, context/06]
11. **The Roquette basin is the right place for the demo, and it has a story:** within ≤250 km of Vic-sur-Aisne there is 64% of the French pea area, with trials in départements that sum to 89% of that area. Winter pea is growing there (Aisne 11% → 46%, Loiret 10% → 51% between 2015 and 2024), and it gives ~1 point less protein. Gap: Oise, the country's 2nd département by area, has only 1 trial with protein. [context/10, context/02, context/03]
12. **2023 is at the edge of the climatology:** days of heat in grain filling rise by +1.2 to +2.2 per decade (Marne: 11.6 → 17.3 days between 1981-2000 and 2005-2024). Scenarios have to weigh recent years more. [climate/14]

---

## 3. Honest reading: what changes in idea 1

- **The easy, solid part:** type (winter/spring) + breeder class + region already order the expected protein well, and the level is calibrated against the silos. That alone is already a useful tool for the September-January contract.
- **The hard part:** getting the season's climate to clearly improve that estimate. The signals exist but are weak and confounded with the year. The model with climate may barely beat the baseline: the plan already has the cutoff rule and the fallback (descriptive calibrated risk atlas).
- **The pitch message:** "calibrated, honest probability of reaching the threshold, updated as the season goes", not "we predict the exact protein". And show the risk the buyer does control: the winter/spring mix and where it sources.
- **The 2% question:** nationally, protein explains 2% of protein tonnage (area 68%, yield 30%). Answer: the processor cares about the protein per tonne it processes and about its own basin; that is why the tool predicts protein and relative yield, per basin.

---

## 4. How the data connects

1. **Clean the Pea_dataset:** fix the 5 bad coordinates (AVANCON → 08, GRIGNON → 78, DIOU, GRIGNON_INRAE, ANGERS_JAILLIERE) and the 2013 harvest date of LE_RHEU. Do not drop the 2018 outliers: they are signal.
2. **Trial → SAFRAN cell** by the nearest cell to the coordinates (all within ≤5.1 km).
3. **Climate indices by phase** anchored at flowering (observed, or estimated with growing degree-days before flowering) with fixed lengths: sowing → flowering, flowering → +30 d, +30 d → +55 d. Never anchor on the actual harvest. Always SAFRAN, in training and in operation.
4. **Training table, trial level:** mean protein and relative yield of the trial + phase indices + soil + type + region + sowing date.
5. **Variety-level table:** deviation of each variety from the trial mean + breeder class × type.
6. **Département → buyer's basin:** SAFRAN climate aggregated by département (column `num_dep` of the shapefile), weighted by RPG area × winter share (`context/rpg_winter_share_dept.csv`). In season, the area is replaced by the monthly Agreste note.
7. **Farm-field yield** = SAA mean yield of the département × predicted relative index.
8. **Level calibration** against the national series (11 years) and the 35 per-basin means (`context/terres_inovia_protein_basin_2019_2025.csv`), without touching the test year.

---

## 5. What has to be trained at the event

| Component | What it predicts | With what | How |
|---|---|---|---|
| **Environmental model** (the core) | Mean trial protein and relative yield | Phase climate indices + soil + type + region + sowing | Ridge or small GBM (~250 trials: few variables, 10 to 20). One per decision date (sowing, flowering, flowering + 30 d) |
| **Variety shift** | Deviation of the variety within the trial | Breeder class × type (+ earliness) | Table of means (no ML needed) |
| **Uncertainty** | Protein distribution and P(≥23%) | Residuals of the environmental model | Quantile regression or conformal grouped by year, isotonic recalibration |
| **Scenarios for the rest of the season** | Climate still missing after the cutoff date | SAFRAN climatology 1995-2024, without the test year | Ensemble: observed up to today + each historical year from today |
| **Basin aggregation** | Protein tonnes in the basin (optional, ex idea 6) | Previous outputs + RPG + SAA | Monte Carlo |

**Baselines to show:**
- **B0:** ≥23% rate by type × macro-region, because region × year cells have ≤5 trials.
- **B1:** B0 + the shift by breeder class.
- **"Year oracle":** the actual mean of the year. Unreachable at sowing, but it shows how much remains in the site × year component.

**Validation:** leave one year out (12 folds), never mixing rows. Metrics per year: Brier, reliability curve, interval coverage, error in protein points.

**Cutoff rule** (from the dossier): at hour 10, the model with climate has to lower B0's Brier by at least 10% and beat B1 in 7 of 12 years. If not, the calibrated risk atlas (B1 + scenarios) is presented, and it is stated clearly that climate did not add enough.

---

## 6. Demo suggested by the data

- **Basin:** Roquette (≤250 km of Vic-sur-Aisne). Core with Aisne, Marne, Somme and Eure-et-Loir; Oise as the honest case of "lots of area, almost no trials"; Charente-Maritime as a contrast outside the north.
- **Blind replay:** 2018 (bad year) and 2023 (good year) with the model trained without that year, showing how the probability is updated between sowing, flowering and flowering + 30 d.
- **Winter/spring mix slider** in the basin: the risk the buyer does control.
- **On-screen warning:** 2023 is at the edge of the climatology.

---

## 7. Prior resources to declare

The derived CSVs (`climate/trial_indices.csv`, `climate/dept_safran_indices_1981_2024.csv`, `context/*.csv`) and the exploration scripts (`pea/scripts/`) were made before the event. They have to be declared as prior resources or regenerated at the event. The recommendation is to regenerate them and use these only as reference.
