# Dossier Idea 1: "PeaSure" (provisional name). Protein risk and pea yield for the ingredients industry

Full dossier compiled on 30/10/2026, before the start of the event. Desk research and data exploration only (counts, joins, formats, extraction tests). **No model was fitted, there was no cross-validation and no solution results.** All solution code, the model, the demo and the deck are built during the event.

Tags: **[V]** verified by me in the file, the API or the primary open source today; **[F]** read in a source (press, secondary, or primary source read in earlier research and not reopened today); **[NV]** not verified, my calculation or hypothesis.

Audit scripts: `scratchpad/plan_n1/scripts/` (a1 to a6). Data downloaded to `scratchpad/plan_n1/data/` and **deleted at the end** (see the end).

---

## 1. Summary in 5 lines + verdict

1. **Problem:** the buyer of peas for fractionation (Roquette Vic-sur-Aisne, Cosucra, their cooperatives) signs contracts before sowing without knowing how much **protein** will reach the plant: the national average protein varied between 21.6 and 24.4% DM in 2015-2025 (a 13% relative difference in protein per tonne) [V], and the area fell from 151.6 to 97.9 kha between 2023 and 2025 [V].
2. **Solution:** a probabilistic forecast, by zone × type (winter/spring) × decision date, of grain protein and relative yield, trained on 3,326 protein measurements from the INRAE/Terres Inovia Pea_dataset and SAFRAN climate, which converts climate uncertainty into "tonnes of protein at risk" across the contract portfolio.
3. **AI:** a tabular G×E model (trial as the unit, ~256 trials with protein) + 35-year SAFRAN climate scenarios + conformal calibration validated by leave-one-year-out. Without the AI, the buyer only has the national historical average.
4. **Demo:** a département map with a date slider (contract → flowering → pre-harvest), a blind replay of 2018 (low year) and 2023 (high year), and the 2026/27 winter pea season that is being sown **now** with SAFRAN as of 29/10/2026 [V].
5. **Business:** B2B licence to the processor and a module for cooperatives that contract for "human food"; timing anchor: EU anti-dumping duties of 40.5-67.1% on Chinese pea protein from 26/09/2026 [V].

**Verdict: GO as the main idea, with two conditions.** (a) Lead with protein (which generalises from trial to farm field) and treat yield as relative risk; (b) validate on Friday with a mentor that the user "buyer at a processor" makes sense, because **contracts today almost never pay the farmer for protein** [V, Terres Univia 2022]: the value sits on the plant side, not the farmer side. Expected rubric score: **6.4/10** (section 12).

---

## 2. Problem, concrete user and decision

### User
- **Primary:** the person in charge of **pea procurement** ("responsable approvisionnement / filière pois") at a pea protein processor, profile Roquette Vic-sur-Aisne (Aisne). Roquette contracts through cooperatives and négoces (grain traders) within a 250-300 km radius [F, La France Agricole via search engine], with more than 2,000 producers in the filière (supply chain) [F, Réussir 04/01/2021, open].
- **Secondary (channel):** the head of the protein-crops (proteaginosas) division of a cooperative that signs production contracts for the processor: Natup ("Cap Duo", 780 ha and 2,500 t in 2020) [V, Réussir 04/01/2021], Cérésia (10-15 kt of peas, premium 20-40 €/t over standard peas) [V, L'Oise Agricole 09/12/2019], Noriap [V, same Réussir article].

### Decision they make
| When | Decision | Information used today | Cost of getting it wrong |
|---|---|---|---|
| Aug-Oct (winter) and Nov-Jan (spring), **before sowing** | How many ha to contract, in which sectors, what type (winter vs spring) | Previous year's areas, historical yield, varietal recommendations (Myvar), relationship with the cooperative | If too much: grain paid with a premium that is not needed; if too little: buying protein outside (the Chinese one now with 40.5-67.1% duty [V]) or underusing a plant that has ~125 kt/year of capacity [F, Réussir 21/05/2018: "250 000 t à l'horizon 2020, dont la moitié en France"] |
| Flowering (April-May) | Adjust volume and protein forecast, plan isolate sales | Field visits, BSV | Isolate sales commitments sized wrongly |
| Pre-harvest (June) | Segregate lots, plan silo and extraction logistics | Nothing quantitative on protein until the NIRS analyses at reception | Mixing lots, losing "human food" lots |

Evidence that contracting happens before sowing: "Les industriels concluent des contrats avant les semis avec des collecteurs qui, à leur tour, mettent en place chaque année des contrats de production avec les agriculteurs" [V, Terres Univia, "La filière du pois en France", May 2022].

### Why protein matters even if it is not paid
- "Pour le moment, peu de contrats prévoient de rémunérer l'agriculteur pour la teneur en protéines des graines" and the table of contract standards for "Ingrédients alimentaires" puts **"-" for protein content** [V, Terres Univia 2022]. The criteria that are required: moisture 14.5-15% max, impurities 1.5-2%, bruchés/tachés (bruchid-damaged/stained) 1.5-3%, splittés (split grains) 5%, other colours 2-3%, allergens 0-0.1% [V, same source].
- But the processor sells **pea protein isolate** (Expana, March 2026: pea isolate EXW Europe **4.15 €/kg**, China 1.60 USD/lb) [V, Expana PDF]. With the same tonnage of grain, a 2023-type year (24.4% DM) delivers ~13% more protein than a 2020-type year (21.6% DM) [V series, NV calculation]. **The protein risk today is absorbed by the plant, with no tool.**

---

## 3. Hypotheses

| # | Hypothesis | Type | Status | Evidence | If false |
|---|---|---|---|---|---|
| H1 | `protein_content` in the Pea_dataset is in % dry matter, N×6.25 | Data | **[V] partial** | In 45 rows (Vocanson & Jeuffroy, 2003-2004) `protein_content` = `N_seed_amount / seed_dry_biomass × 6.25` with mean error 0.00 and max 0.07 points [V, script a1]. For Terres Inovia (3,049 rows) there is no N or biomass: inferred from the ±1.1 point match with the national series in % DM (N×6.25, NIRS) [V series in Terres Univia 2025 PDF] | If Terres Inovia were on a wet basis (~14%), it would be ~3.5 points lower than the national series; it is not. Still, ask the authors (A. Diallo, depositor) |
| H2 | Trial protein follows the national harvest protein | Data/agronomic | [V] descriptive | Annual trial vs national means within ±1.1 points, same high years (2023, 2024) and low year (2018) [V prior + recounted] | Present the output as "trial protein" and calibrate with the national series (11 points) |
| H3 | Trial yield does not transfer to farm fields at all | Data | [V] | Trial 45-50 q/ha vs SAA 28-32 q/ha in 2020-2024 [V] | Already assumed: use relative yield and index, calibrated with departmental SAA |
| H4 | The environment (site×year) dominates protein | Agronomic | [V] descriptive | SD between trials 1.97 points vs 0.84 within the trial [V prior] | If genotype dominated, the product would be varietal choice (Myvar already exists) |
| H5 | Climate in the flowering-filling period explains a major part of variation between trials | Agronomic | [F] | Literature (Azodyn-Pea, OCL 2017) and Terres Inovia 2025: late sowings with poor nodulation → low protein; ascochyta → high protein [V 2025 PDF] | If the model does not beat climatology in LOYO, pivot to a descriptive "risk atlas" (section 7) |
| H6 | SAFRAN is a consistent climate source to train and to operate | Technical | **[V] with caveat** | I extracted SAFRAN for the 158 sites (133 cells, 3.1 km mean distance to the cell) and compared it with the dataset climate at 112 sites: mean temperature r=0.989, mean absolute error 0.86 °C; rain r=0.89; ETP error 0.46 mm. **The Pea_dataset climate is not SAFRAN** (probably weather stations) [V, script a4] | Train and operate with SAFRAN for both (do not mix), or use the dataset climate only for training and accept the bias |
| H7 | Site coordinates are reliable | Data | **[V] false at 3-4 sites** | Postcode vs commune cross-check by coordinates (geo.api.gouv.fr): AVANCON (postcode 08300 Ardennes, coords in Hautes-Alpes; its climate does match the north), DIOU (postcode 36 Indre, coords in Allier 03), GRIGNON (postcode 73200 Savoie, coords in Thiverval-Grignon 78, the postcode is wrong), GRIGNON_INRAE (postcode 73, coords in 28). ANGERS_JAILLIERE is on the 49/44 border [V, script a6] | Correct by hand (5 min) before extracting climate |
| H8 | There is growing industrial demand for French peas | Market | [V] | Definitive anti-dumping 40.5-67.1%, 5 years, EU market "some €175m" [V, Commission 25/09/2026] | The pitch loses urgency, the problem remains |
| H9 | Contracts do not pay for protein but the plant values protein | Market | Half [V], half [NV] | First half [V, Terres Univia 2022]. Second half: extraction-yield logic, no public figure | If the plant buys by tonnage and does not care about protein, the product shrinks to volume risk (yield): weaker. **Question #1 for mentors** |
| H10 | The "human food" premium is 20-40 €/t | Market | [V] (articles 2019-2021) | Cérésia 20-40 €/t [V 2019]; Natup 30 €/t, price ~250 €/t [V 2021]; Terres Inovia 2025 guide 250 vs 280 €/t [F prior] | Old figures: say so |
| H11 | Pea area: 98 kha pure in 2025 | Market | **[V], reconciled** | SAA "41 - Pois protéagineux": 151,603 ha (2023), 123,071 (2024), 97,884 (2025). "42 - Mélange de pois": 63,856 ha in 2025. Pure + mix 2025 = 161,740 ha; × (1 - 7.4%) = 149.8 kha, which is exactly the 2026 forecast "purs ou mélangés" of 150 kha [V SAA, F Pleinchamp]. RPG `pois_prot` 149,983 ha (2023) and 123,772 (2024) match SAA within ±1% [V] | None: the earlier discrepancy was mix vs pure |
| H12 | The user (processor procurement) would want a probability | User | [NV] | No interviews | Validate with mentors on Friday; fallback: user = cooperative |
| H13 | The winter vs spring problem for ingredients is real | Market | [V] | Pea4Ever: "comprendre et corriger la moindre qualité des pois d'hiver sur les marchés ingrédients", €50m, 5 years [V, Pleinchamp 30/01/2026]. In the dataset, winter has ~1 point less protein [V] | Lower that emphasis |
| H14 | A model with effective n ~256 trials / 12 years generalises | Technical | [NV] | This is what gets measured on Saturday | Stopping rule (section 7) |
| H15 | No existing tool forecasts pea protein | Market | [NV, negative search] | Myvar (varietal), éva (aphanomyces), Arvalis forecasts **wheat** protein [F] | Differentiate by the procurement decision and calibrated uncertainty |
| H16 | The project is eligible (not "animal feed") | Rules | [V] reading of the guide | The destination is processing for human food; 140 kt of 349 kt went to "alimentation humaine et ingrédients" in 2025/26 [V Terres Univia 2025 PDF] | Confirm with the organisers on Friday before 23:00 |
| H17 | The 2026/27 season can be demonstrated live | Technical | [V] | `QUOT_SIM2_latest.csv.gz` covers 31/08/2026 to 29/10/2026 [V] | Use Open-Meteo `era5_seamless` [V, responds] |

---

## 4. Datasets (verified audit)

### 4.1 Pea_dataset (core)
- **URL:** https://doi.org/10.57745/FW78RE ; API: `https://entrepot.recherche.data.gouv.fr/api/datasets/:persistentId/?persistentId=doi:10.57745/FW78RE` [V].
- **Licence:** Etalab 2.0 [V]. Version 1, published 05/08/2026, deposited 09/07/2026 by Abdourahmane Diallo, producer at UMR Agroécologie Dijon [V]. `dataOrigin`: experimental, simulation, aggregate [V]. Description: "In this paper, we present a dataset" (data paper not found) [V].
- **Files (fileId, size) [V]:** `crop_traits_data.tab` 764685 (4.56 MB), `metadata.tab` 764683 (4.9 kB), `trials_data.tab` 764684 (1.45 MB), `weather_data.zip` 764686 (2.96 MB, 158 CSV).
- **Counts [V, recounted today]:** 4,450 situations × 33 columns; 27,168 long rows; `yield_14` 4,230, `protein_content` 3,326, `start_flo_date` 4,450. Sources: Terres Inovia GEVES 3,936, Burstin 425, Vocanson 54, Gaudio 35.
- **Units [V data dictionary]:** `yield_14` q/ha at 14% moisture; `protein_content` "%" (see H1: N×6.25 dry basis, verified in 45 rows); climate `RG` J/cm², `ETPP` Penman mm, `TMC/TX/TN` °C, `RR` mm.
- **Protein by year and type [V, script a2]:**

| Year | Spring: n / trials / mean / %≥23 | Winter: n / trials / mean / %≥23 |
|---|---|---|
| 2013 | 21 / 6 / 22.9 / 52% | 43 / 5 / 22.4 / 37% |
| 2014 | 27 / 5 / 23.2 / 59% | 97 / 6 / 22.8 / 47% |
| 2015 | 153 / 14 / 23.2 / 69% | 70 / 8 / 22.2 / 40% |
| 2016 | 125 / 9 / 23.8 / 66% | no winter |
| 2017 | 215 / 15 / 22.9 / 51% | 38 / 3 / 20.1 / 0% |
| **2018** | 208 / 15 / **21.1** / 22% | 75 / 5 / **20.1** / 5% |
| 2019 | 318 / 22 / 22.1 / 35% | 103 / 9 / 21.5 / 24% |
| 2020 | 245 / 21 / 23.2 / 60% | 73 / 6 / 21.1 / 0% |
| 2021 | 219 / 15 / 24.1 / 71% | 84 / 7 / 21.7 / 23% |
| 2022 | 323 / 20 / 22.4 / 46% | 128 / 9 / 22.3 / 33% |
| **2023** | 327 / 18 / **25.2** / 93% | 146 / 12 / **24.0** / 76% |
| 2024 | 189 / 14 / 24.1 / 79% | 54 / 4 / 23.8 / 61% |

- **Demo cases [V]:** 2018 has 20 trials with protein (trial means 16.9 to 24.4; the lowest are VILLEMAIN 79, BOURGES 18, CONDOM 32, PRISSE 79); 2023 has 30 trials (20.5 to 29.2; LE_SUBDRAY 18 with 29.2% and 21 q/ha = stress, not good news). National contrast: 2018 yielded 34.0 q/ha and 2023 32.0 q/ha (SAA) [V], but national protein was 21.7 vs 24.4 [V]: **yield and protein decouple**, which is precisely the argument for modelling both.
- **Geographic coverage:** 40 départements (French administrative departments); Aisne (02, Roquette's home) has only 183 situations across 6 sites [V]. Top: 28, 49, 18, 80, 91, 17, 10, 59, 32, 31 [V].
- **Missing data:** protein missing for an entire site-year (2015, 2017, 2018 with a lot missing) [V prior]; `previous_crop` 41% NA, `cold_tolerance` 61% NA (winter only) [V prior]; `harvest_date` missing in 185 situations [V prior].
- **Gotchas:** wrong coordinates (H7); 2017 harvest date in `LE_RHEU__Genotype_58__2013__M1` [V prior]; 104 of 158 sites appear in only one year [V prior]; `seed_prot` is a breeder **class**, not a number; genotypes anonymised.
- **Download on Friday (30 s):**
```bash
B=https://entrepot.recherche.data.gouv.fr/api/access/datafile
mkdir -p data/raw/pea && cd data/raw/pea
curl -sL "$B/764684?format=original" -o trials_data.csv
curl -sL "$B/764685?format=original" -o crop_traits_data.csv
curl -sL "$B/764683?format=original" -o metadata.csv
curl -sL "$B/764686" -o weather_data.zip && unzip -q weather_data.zip -d weather
```

### 4.2 SAFRAN / SIM2 (climate, core for scenarios and operations)
- **URL:** https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne ; files at `https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/QUOT_SIM2_<AAAA>.csv.gz` (1958 to 2026) and `QUOT_SIM2_latest.csv.gz` [V data.gouv API].
- **Licence:** Licence Ouverte v2 ("lov2") [V].
- **Format [V]:** `;`-separated CSV, one file per calendar year, ~137 MB compressed (2023: 137,392,458 bytes). Columns: `LAMBX;LAMBY;DATE;PRENEI;PRELIQ;T;FF;Q;DLI;SSI;HU;EVAP;ETP;PE;SWI;SSWI_10J;DRAINC;RUNC;RESR_NEIGE;...;WG_RACINE;WGI_RACINE;TINF_H;TSUP_H`. `LAMBX/LAMBY` in hectometres Lambert II étendu; `DATE` YYYYMMDD. Units from the parameters PDF [V]: PRELIQ/PRENEI mm (06-06 UTC), T °C mean, TINF_H/TSUP_H hourly minimum/maximum temperatures, SSI J/cm² (radiation), ETP Penman-Monteith FAO-56 mm, SWI % (soil moisture index).
- **Grid [V]:** `coordonnees_grille_safran_lambert-2-etendu.csv` (9,892 points, columns `LAMBX (hm);LAMBY (hm);LAT_DG;LON_DG`, **decimal comma**). The shapefile `SHP_SIM_FRANCE.dbf` carries **`num_dep` per cell** (8,981 cells): it can be used to aggregate to département without GIS processing [V].
- **Temporal coverage [V]:** `latest` runs from 31/08/2026 to 29/10/2026 (updated 30/10/2026 08:03); 2023-2026 updated 27/10/2026.
- **Extraction test [V, script a4]:** nearest cell by lat/lon for the 158 sites: mean distance 3.1 km (max 5.1), 133 unique cells. Reading and filtering 4 years (2017, 2018, 2022, 2023) with pandas in chunks: **17 s in total**, 194,180 rows, 0 missing. Download: 5 files in parallel (~570 MB) in 2 min 56 s.
- **Comparison with the dataset climate [V]:** 112 comparable sites; mean temperature r 0.989 (absolute error 0.86 °C), max temperature error 1.45 °C, rain r 0.89 (error 0.74 mm/day), ETP error 0.46 mm, radiation RG/SSI = 1.11. AVANCON gives rain r 0.17 because of wrong coordinates.
- **Download on Friday (in background, ~25-30 min for 1991-2026, ~4.9 GB):**
```bash
U=https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM
mkdir -p data/raw/safran && cd data/raw/safran
curl -s -O $U/coordonnees_grille_safran_lambert-2-etendu.csv
curl -s -O $U/Shapefile/SHP_SIM_FRANCE.dbf
seq 1991 2026 | xargs -P 6 -I{} curl -s -O $U/QUOT_SIM2_{}.csv.gz
curl -s -O $U/QUOT_SIM2_latest.csv.gz
```
  Process each year as it is downloaded: keep `LAMBX, LAMBY, DATE, PRELIQ, PRENEI, T, TINF_H, TSUP_H, ETP, SSI, SWI` and only the site cells + the département cells where peas are grown; save as parquet (~tens of MB). If the campus network is slow: download from an AWS EC2 to S3 (see section 6).

### 4.3 Agreste SAA long series (departmental area and yield)
- **ZIP URL [V]:** https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAA-SeriesLongues/SAA-SeriesLongues-2010-2025_DonneesProvisoires-DepartementalesRegionales.zip (7.08 MB; inside `SAA_2010-2025_provisoires_donnees_departementales.xlsx` 11.2 MB).
- **Licence:** Licence Ouverte (Agreste) [F].
- **Structure [V]:** sheet `COP`, header in row 6 (`header=5`), columns `LIB_REG2, LIB_DEP, LIB_SAA, STATUT_QUALITE, SURF_2010..2025, REND_2010..2025, PROD_2010..2025`. Product: `41 - Pois protéagineux` (100 department rows). Units: ha, q/ha, quintals (PROD/10 = t).
- **National pure series [V]:** area 2018 145,362 ha, 2020 202,692, 2022 133,485, 2023 151,603, 2024 123,071, 2025 97,884; yield 2018 34.0, 2023 32.0, 2024 28.3, 2025 35.6 q/ha; production 2025 348.1 kt.
- **Quality [V]:** in 2024, 112,837 ha with statut 1 (reliable) and 10,234 ha statut 2. 32 départements with ≥1,000 ha in 2024; the top 10 account for 49%. Top 2024: Charente-Maritime 7,705, Oise 7,429, Eure-et-Loir 6,855, Marne 6,800, Aisne 5,858 ha.
- **Gotcha [V]:** Oise has `REND` 9-16 q/ha in 2010-2019 and 30-43 since 2020: an error or a unit change in the series; exclude Oise before 2020. Series revised and back-calculated (not what was known in real time) [F methodology].
- **Download:** the `curl` above + `pd.read_excel(f, sheet_name="COP", header=5)` (requires `openpyxl`).

### 4.4 RPG (where peas are grown)
- **Already aggregated:** `archive/research/datasets/rpg_pulses_dept_year.csv` (2015-2024, département × group, `pois_prot` = PPR + PHI). `pois_prot` totals [V]: 2023 149,983 ha, 2024 123,772 ha (match SAA within ±1%). **It is a prior resource to declare.**
- **WFS [V]:** `https://data.geopf.fr/wfs/ows`, layers `RPG.<year>:parcelles_graphiques`, filter `code_cultu='PPR'` or `'PHI'`. Counts: PPR 2023 19,211 parcels, PHI 2023 10,732, PPR 2024 17,347 [V]. **Gotcha:** a `RESULTTYPE=hits` query for PHI 2024 took more than 2 minutes; do not use the live WFS in the demo.
- **Use:** weight of each département and winter/spring split by département.

### 4.5 Terres Inovia / Terres Univia quality survey (national protein series)
- **URL that works without blocking [V]:** https://www.terresunivia.fr/fichiers/publications/qualite-graines-pois-2025.pdf and `.../qg-pois-2024.pdf`, `.../qg-pois-2022.pdf`. The copy on terresinovia.fr returns 403 to curl [V].
- **Series [V]:** protein % DM 2015-2025: 22.9 / 23.1 / 22.4 / 21.7 / 22.2 / 21.6 / 22.7 / 21.9 / 24.4 / 24.1 / 22.8; mean 2015-2024 22.7. Method: samples on arrival at the silo, "N x 6.25% of DM", NIRS, Ardon laboratory (45) [V]. 85 samples in 2025 [V].
- **Balance 2025/26 [V]:** production 349 kt, human food and ingredients 140 kt, animal feed 77 kt, export 132 kt. "Environ 60 % des lots pourraient satisfaire les critères exigés en alimentation humaine" [V].
- **Use:** level calibration (trial → national) and context slide. Only 11 points: not a training set.

### 4.6 Open-Meteo (backup)
- Archive `era5_seamless` responds with max temperature, min temperature, rain, ET0 and radiation, several coordinates per request [V today]. Seasonal API (`seasonal-api.open-meteo.com`) responds with ensemble members [V]. Limit 10,000 calls/day and paid commercial use [F prior]. Only if SAFRAN fails.

### 4.7 Tested joins
| Join | Key | Result |
|---|---|---|
| trials ↔ crop_traits | `situation_id` | 100%, 0 duplicates [V prior] |
| trials ↔ dataset climate | `weather_file` | 158/158 [V] |
| site ↔ SAFRAN | lat/lon → nearest cell | 158/158, ≤5.1 km [V] |
| SAFRAN ↔ département | `num_dep` from the DBF | 8,981 cells [V] |
| site ↔ département | postcode (2 digits) | 153/158 consistent; 4-5 to correct [V] |
| département ↔ SAA / RPG | département code | direct (SAA carries "017 - Charente-Maritime", take the 3 digits) [V] |

---

## 5. AI method

### 5.1 Targets
1. **T1 (main):** grain protein (% DM), continuous, at situation level; derived output **P(protein ≥ buyer's threshold)**, threshold configurable (default 23%, the decade mean rounded up; 22.7% is the 2015-2024 mean [V]).
2. **T2:** relative yield = `yield_14` / mean yield of the site-type in training years, or percentile within the training network. **Do NOT** use the median of the test year (leakage).
3. **T3 (derived, the one the plant cares about):** protein index per hectare = T1 × T2, translated into tonnes with contracted area × departmental SAA yield.

### 5.2 Decision dates and features
| Date | Available features |
|---|---|
| **D0, contract** (15/09 winter, 15/12 spring) | lat/lon, département, soil (AWC, clay, CaCO3, depth), type, breeder protein class (ordinal), earliness, TKW (PMG), Hr, planned sowing window, previous crop (if any). **Climate: 35-year SAFRAN ensemble (1991-2025)** for the future period |
| **D1, flowering** (~29/04 winter, ~24/05 spring, medians [V prior]) | + observed climate sowing → flowering (thermal time, frost TINF_H < -5, rain, ETP-rain, SWI) + `start_flo_date` + ensemble for the rest |
| **D2, pre-harvest** (15/06) | + climate flowering → 15/06: days TSUP_H ≥ 25 and ≥ 30, water deficit, minimum SWI, radiation |

### 5.3 List of leaks to avoid
- Post-harvest: `yield_14`, `protein_content`, `tsw_14`, `seed_weight`, `seed_number`, `harvest_date`, `N_*`, final `dry_biomass`, `total_N_content`.
- `end_flo_date` before D2; `plant_height` (stage unknown); `management` research codes.
- Climate windows anchored on the actual `harvest_date`: anchor on a fixed date or flowering + k days.
- Normalisations (year means, percentiles, thresholds) computed with the test year.
- Climate ensemble that includes the test year.
- Revised SAA used as "real-time data".
- Random row-level split: the same trial shares climate and soil. **Always group by year.**

### 5.4 Baselines (mandatory in the pitch)
- **B0 climatology:** protein mean of type × region in training years (what the buyer knows today).
- **B1 catalogue:** B0 + offset by breeder protein class (what Myvar gives).
- **B2 persistence:** national protein of the previous year.

### 5.5 Model family (justified by n)
- Effective n: **256 site-year × type trials with protein, 12 years, ~13 genotypes per trial** [V prior]. Between-trial variation (SD 1.97) dominates within-trial (0.84) [V].
- **Two-level architecture:**
  1. Environment level: trial mean ~ climate by phase + soil + type, with **ridge** (interpretable linear baseline) and **small LightGBM** (depth ≤ 3, minimum 20 leaves, monotonicity on hot days after flowering). 256 rows.
  2. Genotype level: deviation of the genotype from the trial mean ~ breeder protein class, earliness, TKW (ridge). ~3,300 rows.
- Equivalent alternative if time allows: mixed model (`statsmodels` MixedLM with a random site-year effect). No neural networks, no deep learning: with 12 years it would overfit.

### 5.6 Uncertainty
- **Climate (D0, D1):** pass the 35 years of SAFRAN climate through the model → distribution of forecasts (scenarios).
- **Model:** out-of-year residuals (LOYO) → **year-split conformal** (Mondrian by type) for 80% intervals.
- Final probability P(protein ≥ u) = mixture of scenarios × residual distribution; recalibrate with isotonic regression on out-of-year predictions if the reliability curve drifts.

### 5.7 Validation
- **Main: leave-one-year-out** over 2013-2024 (12 folds); report **by year**, with 2018 and 2023 highlighted.
- Secondary: grouped leave-site-out; leave-genotype-out only for the genotype level.
- External check: forecast annual mean (weighted by RPG area) vs the Terres Univia national series (11 points), descriptive.

### 5.8 Metrics
- Protein: MAE and CRPS by year; 80% interval coverage.
- Threshold: Brier score and Brier skill vs B0; reliability curve.
- Business: error in "incoming tonnes of protein" for a simulated portfolio of 125 kt (synthetic, labelled).

### 5.9 What the AI adds (judge's test)
Without AI: the buyer plans with the national mean (22.7%) and finds out in July, when the trucks arrive. With AI: (a) a risk map before signing, by zone and type, (b) updates at flowering and pre-harvest once the climate has already happened, (c) an honest error number. If in LOYO the model does not improve on B0's Brier, **we say so**, and the product is the risk atlas + scenario updates (which still requires the scenario model).

### 5.10 Explainability
- Ridge coefficients and LightGBM SHAP at trial level ("days > 30 °C after flowering: -X points").
- "Analogue years": the 3 historical years with climate most similar to the current season and their observed protein.
- Always show the interval and the origin label (measured / model / assumption).

---

## 6. MVP and demo

### 6.1 Screens (Streamlit)
1. **Supply map:** département choropleth (GeoJSON of French départements) with P(protein ≥ u) or expected protein, winter/spring type filter, D0/D1/D2 date slider, season selector (2018, 2023, 2026/27).
2. **Contract portfolio:** editable table (département, type, contracted ha). Output: expected grain tonnes, expected protein tonnes with 80% interval, P(reaching the plant's protein target).
3. **Explanation:** by département, season climate curve vs climatology, analogue years, model contributions.
4. **Transparency:** LOYO metrics by year vs baselines, and the source table for each data point.

### 6.2 Live demo script (≈ 80 s within the pitch)
1. "We are on 15 September 2017. You are the procurement manager of a 125 kt plant." D0 map 2018: probabilities centred near the mean, wide intervals.
2. Move slider to D1 (2018 flowering) and D2 (15/06/2018): the map turns red in the west and centre; the portfolio drops from X to Y t of protein. Reveal the observed value: 2018 national 21.7% [V].
3. Switch to 2023: same path, the map turns green; observed 24.4% [V].
4. Close: "And this is today": 2026/27 winter season, D0, with SAFRAN as of 29/10/2026. "If you contract 60% winter in the south, your risk of falling below 23% is Z."
(Every model trained without the year shown; X, Y, Z come out on Saturday.)

### 6.3 Stack
- Python 3.12, `uv`, pandas, pyarrow, scikit-learn, lightgbm, mapie (or conformal by hand), shap, plotly, streamlit, openpyxl.
- **AWS:** (a) EC2 or SageMaker notebook to download and process SAFRAN (4.9 GB) and save parquet to S3; (b) host the Streamlit app on EC2 or App Runner with a public URL for the deck link; (c) optional: Bedrock to generate the explanation text by département from the numbers (not the core AI, do not spend time on it). Everything is pushed to GitHub and USB on Sunday 12:00.
- **Demo backup:** 60 s video recorded Saturday night + screenshots in the deck.

### 6.4 Repo structure
```
peasure/
  README.md               # data, licences, declared prior resources, how to run
  pyproject.toml
  data/                   # .gitignore; download scripts in scripts/
  scripts/01_download.sh  scripts/02_safran_extract.py  scripts/03_features.py
  src/peasure/features.py model.py conformal.py scenarios.py portfolio.py
  notebooks/eval_loyo.ipynb
  app/streamlit_app.py
  reports/metrics_by_year.csv  reports/figures/
  deck/                   # final PDF
```

---

## 7. Work plan

Roles: **A** data/evaluation (pipeline, SAFRAN, validation), **B** modelling (ML/CV student: models, conformal, scenarios), **C** product/business/pitch (app, deck, mentors).

### Friday 30/10
| Time | A | B | C |
|---|---|---|---|
| 20:45-21:15 | Repo, launch SAFRAN download 1991-2026 (EC2 or laptop in background), download Pea, SAA, grid, DBF | Read metadata and build situation × static features table | **Ask the organisers and a mentor: eligibility (ingredients ≠ feed) and "does the plant value protein?"** |
| 21:15-22:30 | Correct coordinates (AVANCON, DIOU, GRIGNON, GRIGNON_INRAE), map sites to cells, extract SAFRAN for sites | Define targets and LOYO, implement B0, B1, B2 over the years | Streamlit skeleton with département map and SAA/RPG data |
| 22:30-23:00 | **Checkpoint 1:** SAFRAN climate for ≥1 year joined to trials | same | Declare track 3 before 23:00 |
| 23:00-01:00 (off campus) | Features by phase for D1 and D2 | Baselines evaluated LOYO by year | Deck storyline, problem and market slide |

**Go/no-go 1 (01:00):** if SAFRAN is not extracted for 2013-2024, use the dataset climate for training (already ready) and SAFRAN only for scenarios.

### Saturday 31/10
| Time | A | B | C |
|---|---|---|---|
| 08:30-09:30 | D0 features + 1991-2025 ensemble by site | Environment level: ridge + LightGBM, LOYO | App: map screen with labelled dummy data |
| 09:30-10:15 | Workshop (one goes, takes notes for "essential AI") | | |
| 10:15-13:00 | Département aggregation (RPG-weighted), calibration with national series | Genotype level + year-split conformal | Portfolio + explanation; talk to 2 mentors (business and agri) |
| **13:00 Go/no-go 2** | **If the D2 model does not improve B0's Brier by ≥10% or does not beat B1 in ≥7 of 12 years: freeze and pivot to "risk atlas + scenarios" (no more features)** | | |
| 14:00-16:00 | Metrics by year, reliability curves, figures | D0 and D1 scenarios, P(threshold) | Integrate real model into app |
| 16:00-18:00 | Replay 2018 and 2023, 2026/27 season with `latest` | SHAP, analogue years | Deck v1 in official template |
| **18:00 Checkpoint 3** | App runs end to end locally | | |
| 19:00-23:30 (off campus) | Deploy on AWS, README, resource declaration | Review leaks (checklist 5.3), freeze model | Pitch rehearsal ×3, timed; record backup video |

### Sunday 1/11
| Time | Everyone |
|---|---|
| 07:30-08:30 | Final rehearsal, URL check, deck PDF |
| 08:30-09:15 | Upload deck PDF (with link to repo and demo) and online form |
| **09:30** | **Deadline** |
| 10:15-12:00 | Pitch |
| 12:00 | Backup of S3/EC2 to GitHub and USB |

### Backup plan
- Without SAFRAN: dataset climate for training, Open-Meteo `era5_seamless` for département scenarios (few points).
- Without a model that wins: empirical risk atlas (frequencies by region × type × year type with year-level bootstrap) + scenarios with climate analogues.
- Without deploy: run locally on the team's notebook and backup video (the presentation is on a shared computer: **ask to test beforehand** whether we can use our own or open a URL).

### Cut list (in order)
1. Bedrock/LLM explanation. 2. Mixed model (keep ridge + LGBM). 3. Leave-genotype-out. 4. Transparency screen (moves to the deck). 5. D1 (keep D0 and D2). 6. Yield target (keep protein).

---

## 8. Business

- **Value proposition:** "Know in September how much protein will come in in July, and where to contract to secure it." For the cooperative: better arguments for contracting and segregating lots.
- **Who pays:** the processor (annual licence per plant); the cooperative as a module within its OAD package. The farmer does not pay.
- **Price benchmarks:** Unéal ODACIO 2026 from 300 €/year + 12 €/ha [F prior]; Farmstar 8-13 €/ha [F]; human food premium 20-40 €/t (Cérésia 2019) [V], 30 €/t (Natup 2021) [V].
- **Proposed price [NV, assumption]:** 30-60 k€/year per processing plant; 3-5 €/ha contracted for cooperatives.
- **Size [mixed]:** EU pea protein market ~175 M€ [V Commission]; isolate EXW Europe 4.15 €/kg [V Expana March 2026]; Roquette capacity ~250 kt of peas/year between Vic-sur-Aisne and Manitoba [V Roquette press release 07/06/2017], half in France [F Réussir 2018, no recent figure]. Pure area in France 97.9 kha (2025) [V]. Direct market in France is small (tens to a few hundred k€/year) [NV]: the scale lies in other EU plants (Cosucra in Belgium, Lantmännen in Sweden [F prior]) and in other pulses (faba bean, lentil) with the same method.
- **Adoption:** (1) pilot with a cooperative already contracting for Roquette (Natup/Cérésia/Noriap) using its historical NIRS analyses; (2) presentation to Terres Univia as a quality layer alongside Myvar or in the "démonstrateurs territoriaux" [F prior]; (3) licence to processors.
- **Competition [F/NV]:** Myvar and éva from Terres Inovia (do not forecast protein), Arvalis forecasts wheat protein, Farmstar/xarvio in cereals, JRC MARS forecasts yield of EU "field peas" (not protein, not by département) [F prior]. Differentiator: protein + decision date + calibrated uncertainty + département × type scale.

---

## 9. Impact and sustainability (all derived figures are [NV] and labelled as estimates)

1. **Protein at stake per year (estimate):** with 349 kt of production and 86% DM, moving from 21.6 to 24.4% protein is ~8.4 kt of contained protein difference at national scale; for a 125 kt plant, ~3 kt [NV calculation from V inputs].
2. **Import substitution:** each kt of protein the plant secures early in France is protein not bought from China with 40.5-67.1% duty [V rates]. Reference value: 4.15 €/kg of isolate [V], i.e. ~€4m per kt of isolate (before deducting extraction yield, which I do not have: assumption to validate).
3. **Area:** if better-managed risk helps recover part of the 53.7 kha lost between 2023 and 2025 [V SAA], every 10 kha adds ~35 kt of grain (at 35.6 q/ha, 2025 [V]) for human food.
4. **Climate and soil:** peas receive no mineral N and leave N for the following crop; INRA 2013 (Pellerin et al.) lists "accroître la surface en légumineuses à graines" as a mitigation action [V title and action in the report]; the factor ~636 kg CO2e/ha/year I only saw cited in secondary sources [F, not verified in the original]: use with that label or do not use.
5. **Farm income:** human premium 20-40 €/t [V] and more stable contracts; Terres Univia: margins comparable to wheat in 2024/25 [F prior].

Honest message: the direct impact of the software is enabling contracting and planning; the physical impact (ha, t, CO2) depends on adoption and is presented as a scenario.

---

## 10. Pitch

### 4-minute script
| Time | Block | Content |
|---|---|---|
| 0:00-0:40 | Problem | "Since 26 September Europe charges up to 67% on Chinese pea protein. French plants need French peas. But France went from 152 to 98 thousand ha in two years, and grain protein swings 13% from one year to the next. Today Roquette's procurement manager signs in September and finds out in July." |
| 0:40-1:20 | Solution | What it predicts, for whom, on which dates; data: 3,326 protein measurements at 158 sites (INRAE/Terres Inovia) + 35 years of Météo-France climate |
| 1:20-2:40 | Live demo | Script 6.2 (2018 → 2023 → today) |
| 2:40-3:20 | Rigour | LOYO by year vs climatology; error in protein points; what it cannot do (bruchid, split grains, absolute farm yield) |
| 3:20-4:00 | Scale and business | Who pays, cooperative pilot, extension to faba bean/lentil and to EU plants |

### Slides (official template)
1. Title + one sentence. 2. Problem with 3 numbers [V]. 3. User and decision (September → July timeline). 4. Solution (data → model → probability diagram). 5. Demo (backup screenshot). 6. Validation (metrics by year vs baselines). 7. Limits and data origin (measured / source / assumption / synthetic). 8. Business. 9. Impact (with estimate labels). 10. Team, prior resources, link to repo and demo.

### Likely questions
- **"Contracts do not pay for protein: who cares?"** The plant: it sells pea protein isolate at 4.15 €/kg; with the same tonnage, 2023 put ~13% more protein into it than 2020. The farmer is paid by tonnage and visual quality.
- **"Why not use Azodyn/STICS?"** They are point estimates with expensive calibration; we give calibrated probabilities validated out of year, and we could use their outputs as a feature.
- **"These are trials, not farm fields."** That is why we lead with protein (it follows the national series within ±1.1 points) and use relative yield calibrated with SAA.
- **"12 years is little."** Yes: we report by year and with intervals; the effective unit is the trial (256).
- **"What about the bruchid or split-grain criterion?"** We do not model it; it is the 40% of lots that do not qualify. It is future work (the INRAE bruchid dataset exists).
- **"Is it feed?"** No: processing for human food; 140 kt of 349 kt already go to human food and ingredients.
- **"What about 2026?"** Show the ongoing season with yesterday's SAFRAN.

---

## 11. Risks, mentors, prior resources and checklist

### Risks
| Risk | Prob. | Mitigation |
|---|---|---|
| The model does not beat climatology | Medium | Stopping rule at 13:00; sell uncertainty and scenarios |
| The judge sees "regression with a nice map" | Medium | Show scenarios + conformal + temporal updating; "no AI" test |
| User not validated | High | Friday mentors; cite Pea4Ever and Terres Univia as evidence of the pain |
| SAFRAN download slow | Low-medium | EC2; start at 20:45; backup with dataset climate |
| Coordinate errors | Certain | Correct 4 sites (list in H7) |
| Confusion with feed | Low | State it on slide 2 |
| Guide's "authorised data only" rule | Low | Ask on Friday whether external open data (SAFRAN, SAA, RPG) is OK |

### Questions for mentors
1. Does a processor plan with the expected grain protein? What does it lose with 1 point less?
2. Who decides the winter/spring mix in contracts?
3. Is there an implicit protein threshold in varietal choice in the cahiers des charges (contract specifications)?
4. Does it make sense to show Roquette by name or better "a processor"?
5. What protein extraction yield is reasonable for a pea isolate (for the impact calculation)?

### Prior resources to declare
- Desk research: `archive/research/idea1_pea_protein_data.md`, `idea1_pea_protein_market.md`, this dossier, `track3_context.md`, `datasets/*.md`.
- RPG aggregate `datasets/rpg_pulses_dept_year.csv` (made before the event).
- Data audit scripts (exploration, not solution; deleted or not reused).
- Open datasets: Pea_dataset (Etalab 2.0), SAFRAN SIM2 (LO 2.0), SAA (LO), RPG (LO), Terres Univia PDFs, Expana, EU Commission.
- Generic libraries (pandas, sklearn, lightgbm, streamlit).

### Deliverables checklist
- [ ] Track declared before 23:00 on Friday.
- [ ] Public repo (or private with access for the jury) with README, licences, prior resources.
- [ ] App deployed with URL + backup video.
- [ ] Deck PDF in official template with link to code and demo, uploaded before Sunday 9:30.
- [ ] Online project sheet (non-confidential: problem, solution, business model).
- [ ] Every number in the deck labelled measured / source / assumption / synthetic.
- [ ] Backup at 12:00 (S3, EC2, GitHub, USB).

---

## 12. Rubric (self-assessment)

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Impact and sustainability | 30% | 6 | Protein sovereignty and anti-dumping very topical; but the physical impact depends on adoption, and protein is not the "food-grade" bottleneck (bruchid and split grains) |
| Scientific and technical rigour | 20% | 7.5 | First-tier public data, verified units, LOYO by year, leaks listed, data errors detected; limit: n=12 years |
| Appropriate use of AI | 20% | 6.5 | Prediction + scenarios + calibration is "essential AI" if shown to beat B0; risk of looking like regression |
| Economic viability | 20% | 5.5 | Concentrated user with real pain, but few customers, no price per protein point and no user validation |
| Execution and pitch | 10% | 7 | Demo with blind replay and live season is powerful; small data and simple pipeline |
| **Weighted total** | | **6.4** | 0.3×6 + 0.2×7.5 + 0.2×6.5 + 0.2×5.5 + 0.1×7 = 6.40 |

---

## 12b. Optional module: protein radar by basin (formerly idea 6)

Full detail and verified data in [6_protein_radar.md](6_protein_radar.md). Summary of how it adds to this idea:

- **What it is:** an extra screen that estimates how many tonnes of pea protein the plant will have in its purchasing basin: area × expected yield × expected protein, with an interval (Monte Carlo).
- **Data:** area and production for the current season are already published monthly by Agreste by département (area from ~13/04, yield from ~13/07) [V in 6_protein_radar.md]. Protein and yield come from this idea's model. External validation: the 35 basin-by-year protein averages for 2019-2025 from the Terres Inovia quality surveys (transcribe by hand from the PDF).
- **Joint sampling:** use the twin seasons from idea 2 to sample yield and protein together, so their correlation is respected (national r -0.16 in logarithms) instead of treating them as independent.
- **Cost:** 2 to 3 hours, only if the Saturday checkpoint went well. It is in the cut list: first thing to be cut.
- **What it adds:** a concrete figure for the pitch ("your basin will have between X and Y tonnes of protein") and an additional regional validation.
- **Caution:** at national level, the variation in protein tonnage is explained 68% by area, 30% by yield and 2% by protein content (descriptive decomposition 2015-2025). That is why it is shown by basin and for the contracting decision, never as a national radar. It is a likely jury question: the answer is that the plant cares about protein per tonne it processes and about its own basin, where the share of trials with 23% protein or more ranges from 18% (2018) to 88% (2023) depending on the year.
- **Do not use the "human food suitable" part** (split grains): there is almost no data series (only ~80% in 2024 and ~60% in 2025).

## 13. Sources (open today unless stated)

- Pea_dataset, Dataverse API: https://entrepot.recherche.data.gouv.fr/api/datasets/:persistentId/?persistentId=doi:10.57745/FW78RE (and files `api/access/datafile/764683..764686`).
- SAFRAN SIM2: https://www.data.gouv.fr/api/1/datasets/donnees-changement-climatique-sim-quotidienne/ ; parameters PDF https://static.data.gouv.fr/resources/donnees-changement-climatique-sim-quotidienne/20260331-150448/sim-quotidienne-parametres-20260331.pdf ; grid and DBF at `meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/`.
- Agreste SAA long series 2010-2025 (ZIP, see 4.3).
- RPG WFS: https://data.geopf.fr/wfs/ows (queries `RESULTTYPE=hits`).
- geo.api.gouv.fr (reverse commune lookup from coordinates): https://geo.api.gouv.fr/communes
- Open-Meteo archive and seasonal (test queries).
- Terres Univia, "La filière du pois en France" (May 2022): https://www.terresunivia.fr/fichiers/publications/filiere-pois-2022.pdf
- Terres Inovia/Terres Univia, Qualité des graines pois 2025: https://www.terresunivia.fr/fichiers/publications/qualite-graines-pois-2025.pdf ; 2024: https://www.terresunivia.fr/fichiers/publications/qg-pois-2024.pdf
- European Commission, anti-dumping on pea protein (25/09/2026): https://policy.trade.ec.europa.eu/news/commission-acts-against-imports-pea-protein-china-2026-09-25_en
- Expana, Plant-Based Protein Report, March 2026: https://www.mintecglobal.com/hubfs/Expana%20Plant-Based%20Protein%20Report%20-%20March%202026.pdf
- Roquette, press release 07/06/2017: https://www.roquette.com/press-releases/pea-protein-investment-vic-sur-aisne-france
- Réussir, 21/05/2018: https://www.reussir.fr/grandes-cultures/roquette-developpe-une-filiere-pois-pour-le-marche-des-proteines-vegetales
- Réussir, 04/01/2021 (Natup, premium 30 €/t): https://www.reussir.fr/grandes-cultures/les-pois-jaunes-une-culture-exigeante-mais-rentable
- L'Oise Agricole, 09/12/2019 (Cérésia, 20-40 €/t): https://www.oise-agricole.fr/actualites/ceresia-relance-la-culture-du-pois-avec-roquette:4BUB0VSS.html
- France 3 Régions, 17/06/2026 (Roquette, 310 jobs, no mention of peas): https://france3-regions.franceinfo.fr/hauts-de-france/pas-calais/bethune/suppression-d-emplois-chez-roquette-le-groupe-agroalimentaire-ne-dans-le-pas-de-calais-prevoit-de-fermer-310-postes-en-france-3370453.html
- Pleinchamp, Pea4Ever (30/01/2026): https://www.pleinchamp.com/actualite/pois-proteagineux-pea4ever-or-never
- INRA 2013, "Quelle contribution de l'agriculture française à la réduction des émissions de GES" (open report, per-hectare factor not found in the text): https://www.inrae.fr/sites/default/files/pdf/37cdee0e58f99f555be7f4655faf63c0.pdf
- Blocked or failed today: terresinovia.fr (403), lafranceagricole.fr (502), EUR-Lex regulation 2026/916 (202 empty). What I cite from there comes from prior research [F].
