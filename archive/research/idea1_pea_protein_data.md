# Idea 1: probability of "food-grade" protein and pea yield (Pea_dataset)

Deep data audit done on 30/10/2026, before the start of the hackathon. Data inspection only (counts, distributions, joins, missing values). **No model was fitted, no correlations were computed as a result, and no validation was run.**

Tags: **[V]** I verified it myself with the data or an API; **[F]** I read it in a source; **[NV]** not verified / my own inference.

Data downloaded to `scratchpad/n1/data/` and **deleted when finished** (only the scripts in `scratchpad/n1/scripts/` remain).

---

## 0. One-line verdict

Clean dataset, well joined (zero duplicates, complete weather for every trial), but the effective n is small: **12 years with protein (2013-2024), 224 site-years, 256 site-year×type trials**. Trial protein tracks the national harvest protein very closely (a difference of ±1 point per year), while trial yield is ~1.5-1.7× that of farm fields. Best to **lead with protein** and treat yield as relative risk. 20 h feasibility: **7/10**.

---

## 1. Files, columns, units and keys

Source: Dataverse API of Recherche Data Gouv, doi 10.57745/FW78RE, version 1, published 2026-08-05, deposited 2026-07-09, Etalab 2.0 license [V]. Authors: A. Diallo, V. Biarnès, M. Prudent, M. Chanis, M.-H. Jeuffroy, S. Gervois, A. Van Boxsom, W. Horrigue, A. Larmure (INRAE Agroécologie Dijon, Terres Inovia, INRAE Agronomie Palaiseau) [V]. `dataOrigin`: "experimental data, simulation data, aggregate data" [V]. DataCite: 0 citations, 125 views, 3 downloads [V], so almost nobody has used it.

| File | Size | Content [V] |
|---|---|---|
| `trials_data.tab` | 1,45 MB | 4.450 rows × 33 columns, one per situation |
| `crop_traits_data.tab` | 4,56 MB | 27.168 rows, long format (`situation_id, ..., variable, value`) |
| `metadata.tab` | 4,9 kB | dictionary: file, variable, description, unit |
| `weather_data.zip` | 2,96 MB | 158 daily CSVs, one per site, `;` separator |

**Key:** `situation_id` = `SITIO__Genotype_N__AÑO` (3.787) or `SITIO__Genotype_N__AÑO__Mk` (663, when there are management modes within the same site-year: Burstin 386, Terres Inovia 197, Vocanson 54, Gaudio 26) [V]. 0 duplicates, all IDs match across tables [V].

**Data paper:** the dataset description says "In this paper, we present a dataset", but I did not find the published article (HAL, web search, DataCite without `IsSupplementTo`) [V search]. It is probably under review [NV]. Closest thing: a poster by Diallo, Larmure, Trépos, Casellas, Prudent (2024, hal-04910021), "Comment adapter la culture de pois au changement climatique ? Approche par simulation de combinaisons génotype × environnement × pratiques culturales... 2024-2027" [How to adapt pea cropping to climate change? A simulation approach to genotype × environment × management combinations... 2024-2027] [F]. It is a thesis that uses this dataset to calibrate a crop model.

### 1.1 `trials_data` (inputs)

- **Location:** `site_name`, `postal_code` (int, must be padded with zeros: 02, 08...), `longitude`, `latitude` (3 decimals in 94%), `harvest_year`, `weather_file` [V]. **There are coordinates**, not just the department. But 158 sites have only 141 distinct coordinate pairs: 13 coordinate groups shared by 2-4 sites (e.g. AIGREFEUILLE_D_AUNIS, CHAMBON, VIRSON, FORGES at -0,945 / 46,117) [V]. The coordinates look approximate (reference station or commune) [NV].
- **Soil (0% missing) [V]:** `soil_class_usda` (8 classes), `soil_depth` in classes (30, 50, 100, 131, 200 cm; 131 only at 3 sites: GENICOURT, AUVERS_SUR_OISE, JOUY_LE_MOUTIER), clay/silt/sand 0-100 cm (%), `soil_awc` (mm, 0-100 cm; site mean 99,8, range 58-144), `soil_CN_ratio`, `soil_caco3_content` (g/kg), `soil_N_content` (g/kg). Constant per site except 2 sites [V]. The granular depth suggests it comes from a soil database rather than sampling [NV].
- **Previous crop:** `previous_crop`, 41,1% missing, free-text codes with history (`winter_wheat__sugar_beet`); winter wheat 1.185 [V].
- **Type:** `pea_type` SPRING 2.705 / WINTER 1.745 [V]. Each genotype is of a single type (72 spring, 45 winter) [V].
- **Variety traits (from the breeder and Terres Inovia, not measured in the trial) [V]:**
  - `seed_prot`: declared protein **class** (low 546, medium 1.665, medium/high 105, high 979, very high 530, NA 625). It is not a number.
  - `Hr_allele` (YES 85, NO 1.660, NA 2.705: only reported for winter), `seed_color` (yellow 4.087, green 264, coral 13, NA 86), `flow_precocity` (5 classes, 15% NA), `lodg_tolerance` (17% NA), `cold_tolerance` (61% NA, winter only), `TSW` in classes (`<180`, `180-200`... `>270`).
- **Management [V]:** `sowing_date` (complete), `sowing_density` (plants/m² according to the dictionary; mean 88, range 35-120; in reality it is the target sowing density [NV]), `irrigation_event_1..3` as text `date=AAAA-MM-DD$dose=mm` (100 irrigated situations: 2022: 39, 2014: 20, 2004: 13, 2015: 12, 2013: 11; 74 of them with protein). `management` 87,7% missing, heterogeneous codes (TF fungicide, TI insecticide, NT no treatment, Irg/Nirg irrigation, S sowing strategy, MOD, cond). **No fungicide or insecticide is reported for the Terres Inovia network in general**: assumed to be protected variety-trial management [NV].
- **No fertilization or diseases/pests** (aphanomyces, bruchid, ascochyta) [V].

### 1.2 `crop_traits_data` (measurements)

Counts by variable [V]: `start_flo_date` 4.450, `yield_14` 4.230, `tsw_14` 3.369, `protein_content` 3.326, `plant_height` 2.762, `end_flo_date` 2.640, `seed_weight` 2.519, `dry_biomass` 998, `plant_density` 689, `emergence_date` 584, `seed_number` 455, `total_N_content` 375, `seed_dry_biomass` 329, `LAI` 172, `N_seed_amount` 76, `N_veg_perc` 73, `N_veg_amount` 68, `N_abs_shoot_fixation` 53.

- Each row also carries `sowing_date`, `harvest_date` and `measurement_date`. `harvest_date` is missing in 185 situations (Terres Inovia 2015: 38, 2017: 94, 2022: 45; Vocanson 2003: 7; Burstin 2014: 1) [V].
- Several rows per situation×variable only for dynamics variables (biomass 231, LAI 45, height 33, total N 31, fixation 9). Yield and protein: one row per situation [V].
- **Dictionary units [V]:** `yield_14` in q/ha at 14% moisture; `tsw_14` g at 14%; `seed_weight` g at 0% moisture; `protein_content` "Seed protein concentration", unit **"%" without specifying a basis**.
- **Protein in % DM?** The dictionary does not say [V]. Terres Inovia's national survey measures protein as **N × 6,25 in % dry matter, by NIRS** in its Ardon lab (45) [F, fiche qualité graines pois 2025]. The annual means of the dataset fall within ±1,1 points of that national series in % DM (table in §6) [V data, F series]. Conclusion: **almost certainly % DM** [NV], but it has to be stated as an assumption. Values with 1 decimal [V]. Lab method for the trials: not reported [NV].
- `crop_traits.measurement_stage` appears in the dictionary but not as a variable [V].

### 1.3 Weather

- 158 files, one per site, all with columns `AN;MOIS;JOUR;ETPP;TMC;RG;RR;TX;TN` [V]. Units: Penman potential evapotranspiration (ETP) in mm, temperatures °C, **RG in J/cm²** (mean ~1.240, i.e. 12,4 MJ/m²/day; divide by 100), RR mm [V].
- 186.179 rows, 0 duplicate dates, only 1 NaN (Thiverval_Grignon), 0 cases TX < TN [V].
- Coverage: most files have 730 days (two years: sowing year and harvest year); some are discontinuous (MONS_EN_PEVELE 2012-2024 with a gap of 2.556 days) [V]. **For all 302 site-years there is complete weather from 1/9 of the prior year to 31/8 of the harvest year**, and 60 days before each sowing [V].
- Site → file mapping: 1 to 1 via `weather_file`, with mixed upper and lower case names (`condom_weather.csv`, `ANGERS_FNAMS_weather.csv`, `Angers_brainsurlauthion_2011.csv`) [V].
- **Sites that share coordinates have identical weather** on overlapping days (maximum difference 0,0 in TX and RR) [V]. The weather is assigned by coordinate, probably from a grid or reference station, not measured in the plot [NV on the origin].
- **Gotcha:** since each file covers almost only the trial season, **it cannot be used to build a site climatology** (scenarios for the "rest of the season"). That requires external weather: SAFRAN (the French meteorological reanalysis) or ERA5/Open-Meteo by coordinate [V coverage, NV alternative source].

---

## 2. Counts and network structure

### 2.1 By source [V]

| Source | Situations | With protein | With yield | Years | Sites |
|---|---|---|---|---|---|
| Terres Inovia GEVES and partners | 3.936 | 3.049 | 3.759 | 2015-2024 | 145 |
| Burstin et al. (2021) | 425 | 232 | 424 | 2013-2016 | 10 |
| Vocanson & Jeuffroy (2008) | 54 | 45 | 47 | 2003-2004 | 2 |
| Gaudio et al. (2024) | 35 | 0 | 0 | 2002-2013 | 9 |

### 2.2 By year [V]

| Year | n | Sites | Genotypes | Spring | Winter | With yield | With protein | Mean yield | Mean protein | n protein ≥23 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2003 | 30 | 4 | 3 | 12 | 18 | 20 | 20 | 66,6 | 20,8 | 2 |
| 2004 | 28 | 3 | 3 | 10 | 18 | 27 | 25 | 58,8 | 21,0 | 3 |
| 2002, 2006-2012 | 22 | 1-2 | 1-3 | 1 | 21 | 0 | 0 | - | - | 0 |
| 2013 | 146 | 11 | 11 | 44 | 102 | 132 | 64 | 58,7 | 22,6 | 27 |
| 2014 | 166 | 8 | 10 | 42 | 124 | 165 | 124 | 48,1 | 22,9 | 62 |
| 2015 | 551 | 37 | 40 | 226 | 325 | 513 | 223 | 55,1 | 22,9 | 134 |
| 2016 | 126 | 10 | 20 | 126 | 0 | 126 | 125 | 50,1 | 23,8 | 83 |
| 2017 | 534 | 36 | 32 | 244 | 290 | 440 | 253 | 52,5 | 22,5 | 109 |
| 2018 | 459 | 29 | 38 | 228 | 231 | 459 | 283 | 49,0 | 20,8 | 50 |
| 2019 | 435 | 30 | 36 | 332 | 103 | 435 | 421 | 57,7 | 22,0 | 137 |
| 2020 | 343 | 28 | 39 | 270 | 73 | 343 | 318 | 45,3 | 22,7 | 147 |
| 2021 | 353 | 21 | 45 | 266 | 87 | 353 | 303 | 40,9 | 23,4 | 175 |
| 2022 | 496 | 27 | 48 | 353 | 143 | 451 | 451 | 45,7 | 22,4 | 189 |
| 2023 | 496 | 29 | 44 | 350 | 146 | 496 | 473 | 45,0 | 24,8 | 416 |
| 2024 | 270 | 19 | 42 | 201 | 69 | 270 | 243 | 47,4 | 24,1 | 182 |

Heads up: 2016 has no winter pea; winter has been a minority since 2019 [V].

### 2.3 By department and region [V]

40 départements (the French administrative units, identified by the first two digits of the postal code). Top: 28 Eure-et-Loir 394 (8 sites, 9 years), 49 Maine-et-Loire 339 (11 sites, 17 years), 18 Cher 309, 80 Somme 300, 91 Essonne 269, 17 Charente-Maritime 241, 10 Aube 225, 59 Nord 220, 32 Gers 203 (**a single site, CONDOM, 10 years**), 31 Haute-Garonne 190. 13 departments have only 1 site; 7 have no protein at all (81, 53, 55, 76, 84, 14, 63).

By region (protein only over measured rows):

| Region | n situations | n protein | Mean yield | Mean protein | ≥22 % | ≥23 % | ≥24 % |
|---|---|---|---|---|---|---|---|
| Centre-Val de Loire | 821 | 575 | 49,3 | 23,6 | 80 % | 65 % | 43 % |
| Hauts-de-France | 728 | 554 | 53,2 | 23,2 | 80 % | 58 % | 33 % |
| Île-de-France | 545 | 472 | 52,9 | 23,2 | 72 % | 57 % | 36 % |
| Occitanie | 536 | 441 | 50,2 | 22,3 | 56 % | 41 % | 25 % |
| Nouvelle-Aquitaine | 490 | 406 | 41,9 | 22,8 | 67 % | 54 % | 41 % |
| Grand Est | 571 | 395 | 46,5 | 22,5 | 61 % | 41 % | 27 % |
| Pays de la Loire | 351 | 211 | 47,5 | 22,0 | 48 % | 30 % | 14 % |
| Bourgogne-Franche-Comté | 175 | 124 | 44,2 | 22,5 | 64 % | 35 % | 21 % |
| Bretagne | 96 | 63 | 68,2 | 23,5 | 87 % | 71 % | 44 % |
| Normandie | 62 | 43 | 58,2 | 22,5 | 65 % | 58 % | 23 % |
| AURA | 65 | 42 | 51,4 | 22,2 | 57 % | 40 % | 24 % |
| PACA | 10 | 0 | - | - | - | - | - |

### 2.4 Genotypes [V]

- 117 anonymized genotypes. Years per genotype: 1 year 23, 2 years 23, 3 years 25, 4: 10, 5: 12, 6: 8, 7: 8, 8: 3, 9: 3, 11: 2.
- 36 genotypes with ≥5 years, 30 with ≥50 situations, 11 with ≥100, 60 at ≥20 sites. The 20 most frequent cover 47,8% of situations. Top: Genotype_98 (spring, 189 situations, 11 years, 79 sites), Genotype_58 (150, 11 years), Genotype_90, _42, _74 (winter), _37, _14...
- 88,3% of situations are of a genotype seen in ≥3 years. 30 genotypes have protein in ≥4 of the years 2019-2024.
- Breeder protein class vs measured protein (descriptive): low 21,9; medium 22,5; high 23,2; very high 24,5% [V]. The declared class ranks well, and it is available at sowing (12% NA among rows with protein).

### 2.5 Network structure [V]

- 158 sites, **302 site-years**, 355 site-year×type trials (208 spring, 147 winter), 53 site-years with both types. A site-year has on average 14,7 genotypes (median 14, max 51).
- **Sites are not stable:** 104 of 158 sites appear in a single year; 17 in 2; 14 in 3; only 13 in ≥5 (CONDOM 10 years, LOUVILLE_LA_CHENARD, CASTELNAUDARY, BRETENIERE, AUCHY_LES_ORCHIES 7). Site names are unique and consistent (one postal code, one coordinate, one weather file per site). No ambiguous reuse of IDs.
- For protein: 118 sites, 224 site-years (221 with ≥5 values), **256 site-year×type trials** (178 spring, 78 winter), median 13,5 genotypes per trial. 76 of the 118 sites with protein appear in only one year.
- Missing protein: **by entire site-year**, not at random within the trial: 196 complete site-years, 78 without any protein, 28 partial. Years with a lot of missing: 2015 (328 of 551 without protein), 2017 (281 of 534), 2018 (176 of 459), 2013 (82 of 146). From 2019 onward the missingness is <15%.
- **Within a trial, protein varies little; between trials, a lot:** standard deviation of the site-year protein mean 1,97 points vs median within-site-year deviation 0,84 [V, descriptive statistics]. For yield: 13,5 q/ha between site-years vs 3,7 within. **The environment (site×year) dominates.** The real unit of information is the trial, not the row.

### 2.6 Quality, outliers, errors [V]

- Yield < 20 q/ha: 55; > 90 q/ha: 10. Protein < 18%: 79; > 28%: 29. The extremes come **in blocks per trial**, not as isolated rows:
  - Low protein (16-17,4%): CONDOM 2018 and 2019, PRISSE_LA_CHARRIERE 2018, VILLEMAIN 2018, BOURGES 2018, ARGOEUVES 2019. Consistent with the low national 2018 (21,7% DM).
  - High protein (28-31%): LE_SUBDRAY 2023 (16 genotypes, yield 15-27 q/ha, protein 28-31%: strong stress, N concentrated in few grains), LOUVILLE_LA_CHENARD 2021-2022, GUMERY 2023, SAVIGNY_SUR_BRAYE 2024 (winter, yield ~31). They are agronomically plausible, not obvious errors.
- **Date error:** `LE_RHEU__Genotype_58__2013__M1` has `harvest_date` 2017-07-16 for a sowing on 2013-03-06 (1.500 days flowering→harvest). It should be 2013 [V the value, NV the correction].
- No harvests before flowering or flowering before sowing [V].
- Sowings: spring mostly Feb-Mar (also 300 in January and 59 in December, typically in the Southwest); winter Oct-Nov (+74 in December, 37 in January) [V]. Median Julian day: spring sowing 62 (3 March), winter 312 (8 Nov.); flowering 144 (24 May) vs 119 (29 April); harvest 195 (14 July) vs 181 (30 June) [V]. Sowing→flowering: 81 days (spring) and 167 (winter); flowering→harvest ~52-63 days.
- Sowing and harvest dates are per trial (only 33-35 trials have more than one date); flowering varies by genotype (median 5 different dates per trial) [V].

---

## 3. Distributions and thresholds

### 3.1 Distributions [V]

- **Protein:** n = 3.326, mean 22,9, range 16,1-31,4. Spring n 2.384: p5/p25/p50/p75/p95 = 19,3 / 21,9 / 23,4 / 24,7 / 26,4. Winter n 942: 18,3 / 20,9 / 22,1 / 23,6 / 25,6. **Winter has ~1 point less protein.**
- **Yield:** n = 4.230, mean 49,5. Spring 23,2 / 37,6 / 46,4 / 57,0 / 69,0; winter 28,7 / 43,2 / 54,3 / 64,8 / 77,8 q/ha.

### 3.2 Real commercial thresholds

- **I found no public protein threshold** in contracts from Roquette or other fractionators [V search, NV existence]. Roquette processes ~250.000 t of pea per year in Vic-sur-Aisne (isolates) [F press].
- The Terres Inovia / Terres Univia survey does give the market benchmark [F, fiches qualité graines pois 2022, 2024, 2025]:
  - National protein series (% DM, N×6,25, NIRS, samples from collection silos): 2014 22,4; 2015 22,9; 2016 23,1; 2017 22,4; 2018 21,7; 2019 22,2; 2020 21,6; 2021 22,7; 2022 21,9; 2023 24,4; 2024 24,1; 2025 22,8. Mean 2014-2023: 22,5; mean 2015-2024: 22,7.
  - The sheets use classes 20-20,9 / 21-21,9 / 22-22,9 / 23-23,9 / >24 % DM per basin.
  - **Heads up, this matters for the pitch:** the "alimentation humaine" (human food) criteria mentioned in the survey are **visual** (bruchid/insects, split grains, sprouted grains, color), not protein. Only ~7% (2022) and 9,5% (2025) of lots with a known destination go to human food; 2025: "Environ 60 % des lots pourraient satisfaire les critères exigés en alimentation humaine" [About 60% of lots could meet the criteria required for human food] [F]. 2021/22 balance sheet: 150 kt to "alimentation humaine et ingrédients" [human food and ingredients] out of 555 kt produced [F].
- **Proposed thresholds for the product [NV commercially]:** 23% DM ("above the ten-year average", interesting for fractionation) and 24% DM ("premium"). A more defensible alternative: **kg of protein per hectare** (yield × protein), which is what a fractionator really cares about.

### 3.3 Share of situations above threshold [V]

| Threshold | All | Spring | Winter |
|---|---|---|---|
| ≥ 20 % | 89,7 % | | |
| ≥ 21 % | 81,8 % | 84,7 % | 74,3 % |
| ≥ 22 % | 68,8 % | 74,8 % | 53,7 % |
| ≥ 23 % | 51,6 % | 58,3 % | 34,5 % |
| ≥ 24 % | 32,6 % | 37,8 % | 19,5 % |
| ≥ 25 % | 16,6 % | | |

By year, ≥23%: 2018 18%, 2019 33%, 2017 43%, 2022 42%, 2020 46%, 2014 50%, 2021 58%, 2015 60%, 2016 66%, 2024 75%, **2023 88%** [V]. The variation between years is huge: the problem is well posed as a probability, with a positive class that is reasonably balanced (~50%).

Yield + protein combined set (n = 3.326 with both) [V]: yield ≥45 and protein ≥23: 27,6%; ≥40 and ≥23: 35,0%; ≥50 and ≥24: 12,3%.

### 3.4 Yield-protein relationship (descriptive only) [V]

- Mean protein by yield band: ≤30 q/ha 23,4; 30-40: 23,1; 40-50: 22,9; 50-60: 23,0; 60-70: 22,3; >70: 22,3. Mild negative slope.
- Within each site-year (deviation from the trial mean): genotypes with yield 10 q/ha or more below the trial mean have +0,4 points of protein; those 10 q/ha or more above have -0,6 points. It is the classic dilution effect, but small compared with the environment effect.
- Extreme cases (LE_SUBDRAY 2023) show that high protein can be a stress signal with low yield: **a high "P(protein ≥ 23)" is not necessarily good economic news**. That is why the joint probability is the better choice.

---

## 4. Information leakage and decision date

| Moment | Available | Notes |
|---|---|---|
| **At sowing** | coordinates, department, soil, type, genotype and breeder traits (protein class, earliness, TSW, Hr, cold, color), sowing date and density, previous crop (41% NA), weather for the 60 prior days, planned irrigation | `seed_prot` comes from the catalogue, not from the harvest: no leakage |
| **At flowering** | + `start_flo_date` (100% complete), weather sowing→flowering (thermal time, frost, rain, ETP), `emergence_date` and `plant_density` (sparse, 13-15%) | `end_flo_date` (59%) is after flowering starts; use only if the cutoff date is later |
| **Before harvest** (e.g. 3 weeks before) | + weather flowering→cutoff: days with TX > 25/30 °C during grain fill, water deficit (RR - ETPP), radiation | Grain fill (~50-60 days after flowering) is where protein is determined |
| **Post-harvest (target or leakage)** | `yield_14`, `protein_content`, `tsw_14`, `seed_weight`, `seed_number`, `harvest_date`, `N_*`, `seed_dry_biomass`, final biomass, `total_N_content` | Never as a feature. `harvest_date` defines the end of the cycle: for features use a fixed cutoff date or flowering + k days, not the actual harvest |
| **Doubtful** | `plant_height` (unknown at which stage it was measured), `management` of the research trials (modality codes) | Exclude from the MVP |

**Building weather features up to a cutoff:** for each `situation_id`, take the `weather_file`, build the date from `AN/MOIS/JOUR`, filter `sowing_date ≤ d ≤ cutoff`, and aggregate: sum of TMC (base 0 °C), days TN < -5 °C (winter), sum of RR and of RR-ETPP per phase (sowing-flowering, flowering-cutoff), days TX ≥ 25 and ≥ 30 since flowering, RG/100 in MJ/m². 100% coverage verified for all trials [V]. For "the rest of the season" in forecast mode you have to use external climatology (see §1.3).

**Subtle leakage:** rows from the same trial share weather and soil. A random row-level split puts the same environment in both train and test and inflates everything. Validation has to group at least by site-year.

---

## 5. Validation designs

| Scheme | Folds | What it measures | Comment |
|---|---|---|---|
| **Leave-one-year-out (LOYO)** | 12 years with protein (2013-2024); 10 if only Terres Inovia | generalization to a new season: **the real use case** | Main scheme. Years like 2018 (low) and 2023 (high) are the hard tests |
| Leave-site-year-out (site-year group) | 224 groups | new environments within years already seen | Optimistic: the year is already in train |
| Leave-site-out | 118 sites with protein | new sites | Since 76 sites appear in only one year, it is very similar to the previous one |
| Leave-genotype-out | 117 genotypes | new variety | Only with breeder traits as features; useful as a secondary check |
| Year + site blocked | 12 × region | the most honest | Little data per cell |

**Effective size:** 3.326 rows with protein, but the environmental information comes from **256 trials (224 site-years) spread across 12 years**. For the climate part, the effective n is around 200-250; for the year effect, 12. For the genotype, ~13 observations per trial, with 30 well-replicated genotypes. With LOYO, the uncertainty of any metric is large: report the metric per year, not just the average.

---

## 6. Joinability and generalization to farm fields

### 6.1 Join [V unless noted]

- **Department:** first 2 digits of the postal code (pad to 5 characters). 40 departments, all metropolitan, no Corsica. This mapping works except for CEDEX codes or rare cases [NV for the edge cases].
- **SAFRAN / ERA5:** with lat/lon (3 decimals) to an 8 km or 0,25° cell. Useful for climatology and for extending the weather to any plot in the RPG (the French graphic parcel register).
- **RPG:** PPR codes (spring pea) and PHI codes (winter pea), already audited in `datasets/agronomy_plant_health.md`; allows weighting by actual area per department.
- **Agreste (the French agricultural statistics service) SAA / Eurostat:** department × year for area and yield of "pois protéagineux" [protein pea crops] [F that they exist; I did not download the departmental SAA].

### 6.2 Trial vs farm field gap

| Year | Trial mean yield [V] | National yield Terres Univia [F] | Eurostat P1100 t/ha [V API] | Trial protein [V] | National protein % DM [F] |
|---|---|---|---|---|---|
| 2014 | 48,1 | - | 3,63 | 22,9 | 22,4 |
| 2015 | 55,1 | - | 3,62 | 22,9 | 22,9 |
| 2016 | 50,1 | 28,6 (Agreste, F) | 2,49 | 23,8 | 23,1 |
| 2017 | 52,5 | - | 3,41 | 22,5 | 22,4 |
| 2018 | 49,0 | - | 3,38 | 20,8 | 21,7 |
| 2019 | 57,7 | - | 3,88 | 22,0 | 22,2 |
| 2020 | 45,3 | 27,4 | 2,86 | 22,7 | 21,6 |
| 2021 | 40,9 | 28,4 | 2,98 | 23,4 | 22,7 |
| 2022 | 45,7 | 29,4 | 3,10 | 22,4 | 21,9 |
| 2023 | 45,0 | 32,0 | 3,29 | 24,8 | 24,4 |
| 2024 | 47,4 | 28,2 (27,9 in "chiffres clés" [key figures]) | 2,92 | 24,1 | 24,1 |

- **Yield:** trials are ~1,4-1,7× the farm field in 2020-2024 (45 vs 28-32 q/ha). In addition, 2016, a national disaster (Agreste 28,6 q/ha), shows up as 50 q/ha because that year only has Burstin spring trials. **Absolute trial yield does not carry over to farm fields**: use relative yield (percentile within the year or ratio vs the trial mean) or calibrate against departmental Agreste.
- **Protein:** annual trial means fall within ±1,1 points of the national survey and follow the same high years (2023, 2024) and low years (2018). Descriptive comparison of 11 pairs, not a model result. **Protein generalizes much better than yield.**
- Eurostat P1100 (2,5-3,9 t/ha) does not match the Terres Univia figures (different definition or moisture) [V the numbers, NV the cause].

---

## 7. Prior art and innovation gap

- **Process models:**
  - **Azodyn-Pea** (Jeuffroy, Vocanson, Roger-Estrade, Meynard 2012, Eur. J. Agron. 42:68-78) simulates yield and grain protein and was used to compare pea types (winter, spring, Hr) in French regions (hal-01604092) [F].
  - Larmure et al. 2022 use it in Bourgogne-Franche-Comté with climate regionalized to 8 km under RCP 4.5/8.5 [F, hal-04107539]. Larmure, Lecomte et al. 2022 project frost risk for winter pea [F, hal-04107426].
  - STICS was used for pea and faba bean in the Southwest (Field Crops Research 2020: -28% yield in spring pea under the worst scenario) [F]. Falconnier et al. 2019 calibrated STICS for faba bean [F].
  - "Afisol": I did not find a specific reference [NV].
- **This same dataset:** it was put together by the team of A. Diallo's thesis (2024-2027, Dijon), whose stated goal is to simulate G×E×M with a crop model (poster hal-04910021) [F]. The dataset description says it serves "to evaluate and improve crop models" [V]. **No published work with ML or calibrated probabilities on it** (0 citations in DataCite) [V].
- **Statistical diagnostics:** OCL 2017, "Impact of climate and diseases on pea yields" (yield stagnation since 1999, role of climate and diseases) [F]. Jeuffroy et al., "Performances of five crop models simulating yield and grain protein content in farmers' fields" (Azodyn among them; results not read) [F title].
- **ML on pea:** Poland, neural networks for protein (Agriculture 2023, 13(1):29: MAPE 2,7% vs 8,9% for a multiple linear regression) and for yield, at a single site, 2016-2020 [F]. Klein et al. 2026 (Plant Phenome J.), phenomic + genomic selection on 288 accessions × 12 environments in France [F]. None of them is multi-site French, probabilistic, or built around a decision date.
- **Terres Inovia tools:** myVar (varietal results by region, no probabilities) [F, previous audit].

**Gap:** nobody delivers a **calibrated probability, updated during the season (sowing → flowering → pre-harvest)**, of exceeding a protein threshold (and a yield one) by department × type, validated out-of-year. Process models give point estimates without calibrated uncertainty and with costly calibration. What is new is a probabilistic forecast validated with LOYO, with honestly quantified uncertainty, designed for the collection and lot-segregation decision of a cooperative.

---

## 8. Evaluation for 20 h

### 8.1 Feasibility: 7/10

- In favor: clean data, already joined, small (loads in seconds), complete weather, balanced target (~50% ≥23%), natural validation (LOYO), external national benchmark for the pitch.
- Against: low effective n (12 years), undocumented commercial threshold, human use depends on visual quality that is not in the data, trial vs farm field yield gap, external climatology needed for forecast mode.

### 8.2 Is AI essential? 6/10

The "AI" part is tabular supervised learning plus uncertainty quantification. It becomes essential if: (a) the learning maps daily weather trajectories to probabilities **that can be updated over time** (there is no simple rule that does it), (b) the uncertainty is calibrated (conformal), (c) it is compared against the process model or climatology as a baseline. Risk: the jury sees it as "just a regression". An LLM to explain the forecast to the advisor adds little rigor; better to spend the time on calibration.

### 8.3 Concrete MVP

1. **Targets:** `y1 = protein_content ≥ 23` (and 24 as a variant); `y2 = yield_14 ≥ year's 50th percentile` (relative yield) or yield ≥ X only as a trial scenario; plus the continuous variable `protein_content` for quantiles.
2. **Unit and features (~15-20):** per situation, with three cutoffs (sowing, flowering, flowering + 30 days):
   - static: type, breeder protein class (ordinal), earliness, TSW, AWC, clay, depth, CaCO3, latitude, sowing day, density, irrigation;
   - weather by phase: thermal time, rain, RR-ETPP, days TX ≥ 25 and ≥ 30 after flowering, frost.
3. **Models:**
   - baseline 0: climatology (rate ≥23% in training years by type × region);
   - baseline 1: breeder protein class + type (logistic);
   - main: mixed model (random effect of site-year and genotype) **or** a small gradient boosting model (LightGBM, depth ≤3, monotonicity in post-flowering heat) on the features. With environmental n ~250, an unregularized GBM overfits: prefer the mixed model or a GBM with early stopping under LOYO.
4. **Uncertainty:** quantile regression (q10/q50/q90) for protein plus **year-grouped conformal** (calibrate with LOYO residuals, Mondrian by type) for intervals with nominal coverage. The threshold probability comes from the predictive distribution, recalibrated (isotonic over the out-of-year predictions). Metrics: Brier, reliability, 80% coverage, per year.
5. **Aggregation:** probability by department × type × cutoff, weighting typical genotypes.

### 8.4 Demo

Department map (RPG, to show where pea is grown) with a **decision-date slider** (sowing → flowering → pre-harvest): the probability of a lot "≥23% DM" and its interval narrow down. Storyline: replay of 2018 (low year) vs 2023 (high year) with the model trained without that year. Advisor panel: "expected collection with ≥23%: X t; separate silos in these departments". One economics line: assumed protein premium [NV] × tonnage.

### 8.5 Stopping rule

- **Hour ~6:** feature pipeline + baselines 0 and 1 evaluated under LOYO. If not done, cut back to a single cutoff (flowering).
- **Hour ~10:** if the main model with a flowering cutoff does not lower the climatology's Brier score by at least 10% under LOYO, or does not beat the breeder class in ≥7 of 12 years, **do not add complexity**: pivot to a descriptive "risk atlas" (empirical probabilities by region × type × year type) with bootstrap uncertainty by year, and sell the value of in-season updating as future work.
- **Hour ~14:** freeze the model; the rest is calibration, demo and pitch.

### 8.6 Main risks

1. **Unverified economics:** there is no protein threshold or public premium; human consumption (casserie, the French trade term for pulses processed for human food) depends on bruchid, split grains and color, not on protein. Mitigation: talk about protein/ha for fractionators and validate with a mentor or cooperative at the event.
2. **Effective n = 12 years:** LOYO metrics will be noisy; 2023 is atypical (88% ≥23%).
3. **Trial ≠ farm field for yield** (~1,5×). Mitigation: relative yield; protein does generalize.
4. **Protein unit undocumented** (almost certainly % DM, given the match with the national series, but with no written confirmation).
5. **Trial weather only covers the season:** for scenarios of the rest of the season you need to download ERA5 or historical Open-Meteo by coordinate (2-3 h of work).
6. **Anonymous genotypes:** varieties cannot be recommended by name; only by breeder class.
7. Sites are almost always new (104 of 158 from a single year): good for generalization, bad for "knowing the site".
8. Direct competition from the dataset authors' team (Diallo thesis with a process model): present it as a probabilistic complement and cite them.

---

## Sources

- Dataset and metadata: https://doi.org/10.57745/FW78RE (Dataverse and DataCite APIs, accessed 30/10/2026).
- Diallo et al. 2024 poster: https://hal.inrae.fr/hal-04910021
- Larmure et al. 2022 (soils, climate, Azodyn-Pea): https://hal.inrae.fr/hal-04107539 ; frost risk: https://hal.inrae.fr/hal-04107426
- Azodyn-Pea, regional adaptation: https://hal.archives-ouvertes.fr/hal-01604092
- OCL 2017, climate and diseases in pea yield: https://www.ocl-journal.org/articles/ocl/pdf/2017/01/ocl160055s.pdf
- Pea protein with neural networks (Poland): https://www2.mdpi.com/2077-0472/13/1/29
- Klein et al. 2026, phenomic/genomic selection: https://acsess.onlinelibrary.wiley.com/doi/10.1002/ppj2.70076
- Terres Inovia / Terres Univia quality surveys: https://www.terresunivia.fr/fichiers/publications/qg-pois-2022.pdf , https://www.terresunivia.fr/fichiers/publications/qg-pois-2024.pdf , https://www.terresunivia.fr/fichiers/publications/qualite-graines-pois-2025.pdf (the PDFs on terresinovia.fr return 403 to bots)
- Yield 2024 vs 2016: https://www.lafranceagricole.fr/conjoncture-cultures/article/877187/fort-recul-de-la-production-de-pois-en-2024
- Eurostat `apro_cpsh1`, FR, P1100 (API, accessed 30/10/2026).
- Roquette Vic-sur-Aisne: https://www.reussir.fr/lesmarches/roquette-investit-et-innove-sur-la-proteine-de-pois
