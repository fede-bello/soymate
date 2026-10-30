# Dossier Idea 2: "Climate analogue seasons" (Track 3, Hack the Fork Paris 2026)

Audit date: 30/10/2026 (morning of the event day). Done before the official start: desk research and data exploration only (downloads, counts, joins, descriptive statistics). **No model was fitted, no distance between seasons was computed and no backtest was run.**

Tags: **[V]** verified by me on the file, the API or the primary open source today. **[F]** read in a source (or in the prior research in the repo, done by another agent) without re-verifying it myself. **[NV]** not verified: hypothesis, memory or my own account.

Exploration scripts used (counts and descriptives only): `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/plan_ib/scripts/`. Downloaded data was deleted at the end.

---

## 1. Summary in 5 lines and verdict

1. **The finding that changes the idea:** Agreste publishes, in addition to the 2010-2025 long series, a ZIP with departmental SAA **2000-2020** (table `SAANR_DEVELOPPE_2`, one CSV per year). Splicing the two sources, dry pea has **43 départements with ≥500 ha and yield in ≥20 of 26 seasons (2000-2025)**, and lentil in Haute-Loire and Indre has all 26 seasons complete [V]. The "only 15 analogues" from the prior research is superseded.
2. **Second finding, which forces a change of method:** pea yield has a strong downward trend (national weighted mean ~45 q/ha in 2000-2009 vs ~30 q/ha in 2020-2025) [V]. An analogue from 2002 "brings" 49 q/ha even if the climate is identical. **Analogues must return anomalies relative to a trend estimated only from the past, not raw yields.**
3. Climate: SAFRAN/SIM2 daily by year since 1958 (8 km, 9,892 points, Licence Ouverte, updated to 26/10/2026), no missing values, with rain, T, hourly Tmax, ETP, radiation and soil moisture index [V]. Aggregated to département it weighs ~1.5 MB per year [V].
4. Recommended variant: **"Campagne jumelle pois"** (twin pea season), a case-based reasoning engine over ~1,000 département-seasons of pea (2000-2025) with a metric learned only from earlier years, which at a cut-off date (15/05 and 15/06) returns the most similar seasons, their yield anomaly distribution and an interval estimate for the grain collection manager of a cooperative that sells peas to the food industry. The protein layer with Pea_dataset becomes an extension, and bruchid data is not useful for analogues.
5. User and money: 117 cooperatives and 360 négociants (grain traders) collect protein crops [V]; 146 kt of protein crops went to human food in 2024/25 [V]. The addressable market is small (estimate of the order of €0.2-1m/year [NV]), so the business has to grow toward more crops or be sold as a module within the cooperatives' OAD packages (decision-support tool packages).

**Verdict:** viable and defensible in 20 h, with a real scientific risk: the analogues may not beat the département's moving average. **Estimated weighted score: 6.1/10** (section 12). Idea 2 is stronger as an **explainable engine for a grain collection estimate** (2 + 4 merged: the estimate comes from the analogues) than as a pure exploration tool. I recommend it as the main idea only if the mentor confirms that a cooperative makes a volume decision in May-June. If not, it is better used as the explanation layer of another idea.

---

## 2. Problem, user and decision

### 2.1 Problem
Pulse yields in France are very volatile: national pea 23.4 q/ha in 2016 vs 49.4 in 2002, and 27.6 in 2020 [V, spliced SAA, area-weighted mean]. Lentil in Indre: 7 q/ha in 2020 and 23 q/ha in 2021 [V]. Ben-Ari et al. (2018) show that the 2016 wheat drop was **not anticipated** by operational forecasts [V title via Crossref: "Causes and implications of the unforeseen 2016 extreme yield loss in the breadbasket of France"]. For whoever bought or sold food-grade pulse volume in advance, that volatility translates into broken contracts, replacement purchases and undersupplied plants. That this is **the** barrier to producing more food-grade pulses is a hypothesis [NV]: the event guide talks about farmers' fear of losing income, and yield volatility is one of the components of that risk.

### 2.2 Concrete user
**Grain collection manager / protein crops supply-chain manager (responsable de collecte / responsable filière protéagineux) of a field-crop cooperative** that contracts peas for the food industry. Documented profile: SCAEL (Eure-et-Loir) for Cosucra; Roquette contracts through "around fifteen organismes stockeurs (grain storage bodies)" with cahier des charges (contract specifications) [F, `idea1_pea_protein_market.md`, sources Terres Inovia 2023 and La France Agricole 2018]. Secondary user: **agronomic supply manager of a processor** (Roquette Vic-sur-Aisne, Cosucra).

### 2.3 Decision
| | Detail | Status |
|---|---|---|
| What is decided | How much food-grade pea volume to commit (forward sales, allocation between human food and animal feed, reception and cleaning logistics) and whether to trigger complementary purchases | [NV] validate with mentor |
| When | Between mid-May and end of June: flowering of spring pea; winter pea is harvested in early July | [F] Terres Inovia: yield components are set from flowering, and stress >25 °C in that period "peut lourdement impacter le nombre de grains par m²" [V, terre-net 205909] |
| What information is used today | Average of recent years, field tours by technicians (tours de plaine), regional crop condition reports from the DRAAF, expert opinion of the type "it looks like 2016" | [F] prior research; analogy used informally in the farm press (section 2.4) |
| Cost of getting it wrong | Illustrative example [NV]: a cooperative with 5,000 ha of peas that expects 35 q/ha and harvests 25 has a shortfall of 5,000 t. At ~€220-275/t (pea producer price 2023/24 to 2025/26 [F, `datasets.md`, FranceAgriMer]) that is €1.1 to 1.4m of volume not delivered, plus penalties or replacements | estimate |

### 2.4 Is "analogue year" reasoning used today?
- **Yes in the press and campaign discourse**, but informally: in July 2024, when giving Arvalis and Intercéréales's wheat forecast (64 q/ha), the press placed it "en dessous de 2020 (68 q/ha) mais tout de même au-dessus de 2016 (54 q/ha)" [V, terre-net 869327, 05/07/2024; the comparison is the journalist's, not a quote from Arvalis].
- **Arvalis uses "prévisions fréquentielles"** (frequency-based forecasts), i.e. completing the rest of the season with the climate of past years: in 2019, Arvalis said seasonal forecasts "étaient plus précises que les prévisions fréquentielles usuelles, lesquelles n'intègrent pas le changement climatique". Météo-France, in turn, "rejouent 24 années passées climatiques" to build scenarios [V, Pleinchamp 05/06/2019]. It is the same principle of using past years as scenarios.
- **In the US, the USDA uses analogue years in the WASDE**, traditionally chosen "by eye" [V only the title of NASA NTRS report 20120003729: "Retrospective Analog Year Analyses Using NASA Satellite Data to Improve USDA's World Agricultural Supply and Demand Estimates", 2011; that the choice is visual is [F] from the search engine summary].
- **Counter-evidence to be aware of:** Chen et al. (2022, Agric. For. Meteorol.) found that "weather records from recent years performed better than analogue years" for rainfed maize [V title via Crossref]. Liu et al. (2021, Remote Sensing) propose an "analogy-based" forecast with LAI [V title]. I did not read these papers in full [F for their content].
- **I did not find** any Terres Inovia or Chambre document that defines an "analogue year" method for pulses [NV, negative search]. This needs to be asked of the mentor.

---

## 3. Hypotheses

| # | Hypothesis | Type | Status | Evidence | If false |
|---|---|---|---|---|---|
| H1 | There are enough seasons with departmental yield for analogues to make sense | data | **[V]** | Pea: 43 départements ≥500 ha in ≥20/26 years and 27 départements in all 26 years (2000-2025); faba bean 23; lentil 3 (Indre, Haute-Loire, Aube) | Move to regional or national scale (FAOSTAT 1961-2024) |
| H2 | The 2000-2009 series (RA 2010 base) and 2010-2025 series (RA 2020 base) can be spliced | data | **[V] with bias** | Overlap 2010-2020 (dept-year ≥500 ha): pea identical in 83.5% of cases, mean difference -1.28 q/ha (new minus old), r = 0.876; faba bean identical 95.4%; lentil 94.5%, r = 1.0 | Adjust the offset by département in the overlap, or use only 2010-2025 |
| H3 | Departmental SAA yield reflects the département's climate and not only imputations | data | **[V] partial** | Pea 2000-09: 33% of yields are identical to another département's in the same region that year (23.5% in 2010-25 [F]); faba bean 43%; lentil 26% (small n). Oise 2010-2019 is an artefact (9-16 q/ha vs 40-55 before and after) | Deduplicate by region-year, evaluate with effective n per region, exclude Oise 2010-19 |
| H4 | There is a trend in yield and it must be removed | data | **[V]** | Pea weighted: 45.1 (2000), 48.7 (2009), 35.8 (2015), 28.3 (2024). Lentil Haute-Loire: 16 (2000) to 3.5-6.6 (2020-25) | If not removed, old analogues bias upward |
| H5 | Similar climate up to the cut-off date implies similar yield | agronomic | **[NV]** | Documented mechanisms: stress >25 °C and water stress at flowering [V, Terres Inovia]; wet spring and little sun in 2016 [F]. But Aphanomyces, the bruchid, the variety, the winter/spring mix and sowing also matter | This is the main risk: if the backtest does not beat the département moving average, it is presented as an exploration tool and that is stated |
| H6 | Climate after the cut-off (June-July) does not dominate | agronomic | **[NV]** | The mid-June 2025 stress occurred in full flowering (according to the search, I did not open it) | Run two cut-offs (15/05 and 15/06) and show how much the second improves; complete the rest of the season with analogue scenarios |
| H7 | The departmental climate average represents the pea area | technical | **[NV]** | Départements have 76-131 SAFRAN points [V]. The Open-Meteo point for Le Puy gives 232 mm (01/03-15/06/2026) vs 185 mm for the SAFRAN average of Haute-Loire [V] | Weight by RPG parcels (derived table already exists [F]) |
| H8 | The SAA does not separate human and animal use, but pea has a relevant human outlet | market | **[V]/[F]** | FranceAgriMer: 146 kt of protein crops to human food in 2024/25 [V]; Terres Univia: 140 kt of pea to human food and ingredients out of 349 kt [F] | Show lentil as a 100% human case (Haute-Loire, Indre) |
| H9 | The user (cooperative) makes a volume decision in May-June that they currently make with little information | user | **[NV]** | No primary verification | Ask the mentor on Friday. If the real decision is autumn contracting, pivot to "departmental yield risk" to set clauses (the same engine on the full climate) |
| H10 | The user trusts "it looks like 2016 in Marne" more than a black-box number | user | **[NV]** | Suggested by the informal use of comparisons in the farm press [V] | The product still delivers a number with an interval; the explanation is a bonus |
| H11 | The cooperative would pay a subscription of the order of €1-10k/year | market | **[NV]** | Benchmarks: Unéal's ODACIO from €300/year + €5 to 16/ha depending on the service [V]; Sencrop stations via chambre ~€16/month [F] | B2B2F per-hectare model within the OAD package |
| H12 | A grain collection manager does not have such a tool today | market | **[NV]** | Climadiag Agriculture is free but projects to 2030/2050/2100, without comparing with past years or pulses [V, Réussir 05/12/2024]. JRC MARS gives field peas at EU level [F] | Differentiate by département scale, food-grade pulses and traceability |
| H13 | SIM2 arrives in time to decide | technical | **[V]** | The 2026 file runs to 26/10/2026, consulted on 30/10 (~4 days' lag) | Complete the last days with Open-Meteo (`era5_seamless`, ~5 days' lag [V]) |
| H14 | Climate can be downloaded and processed during the event | technical | **[V]** | 130 MB per year; 3 years in parallel took 3 min 43 s on my connection; each year is read and aggregated in ~8 s | Download on AWS (Paris region) or use fewer years |
| H15 | Open-Meteo is usable for a commercial product | technical/business | **[V] no** | "The free API is for non-commercial use" [V] | Use SIM2 (Licence Ouverte) in the product |

---

## 4. Datasets (audit)

### 4.1 Agreste SAA long series 2010-2025 (core, labels) [V]
- Page: https://agreste.agriculture.gouv.fr/agreste-web/disaron/SAA-SeriesLongues/detail/ ("Published 25/04/2024, updated 10/07/2026"). Licence: Licence Ouverte (data.gouv `fr-lo` for the SAA) [V].
- Download tested today (HTTP 200, 7.08 MB):
  ```
  curl -L -o saa_2010_2025.zip "https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAA-SeriesLongues/SAA-SeriesLongues-2010-2025_DonneesProvisoires-DepartementalesRegionales.zip"
  ```
- Inside: `SAA_2010-2025_provisoires_donnees_departementales.xlsx` (11 MB) and `..._regionales.xlsx`. Sheet `COP`, header in row 6 (`header=5`), 4,500 rows × 52 columns: `LIB_REG2, LIB_DEP, LIB_SAA, STATUT_QUALITE, SURF_2010..2025, REND_2010..2025, PROD_2010..2025` [V].
- Units: ha, q/ha, q. Products of interest: `41 - Pois protéagineux`, `38 - Féveroles et fèves`, `40 - Lentilles`, `43 - Pois chiches`, `39 - Haricots secs`, `44 - Lupin doux` [V]. **It does not separate winter and spring pea** [V].
- National totals (metropolitan France, sum of départements) [V]: pea 2016 188,022 ha and 23.4 q/ha; 2024 123,071 ha and 28.3; 2025 97,884 ha, 348 kt and 35.6 q/ha. Lentil 2025 33,857 ha and 15.2 q/ha. Chickpea 2025 27,643 ha and 16.1 q/ha.
- **Join gotcha:** `LIB_DEP` uses a 3-digit code (`077 - Seine-et-Marne`); it must be turned into `77` to join with the old SAA and with the geography. Corsica `2A/2B`.
- Gotchas: 2025 provisional; 2010-2019 series "rétropolées" onto RA 2020 (revised data, not what was known in real time); `STATUT_QUALITE` one per row [F, prior research]; Oise pea 2010-2019 artefact [V].

### 4.2 Agreste SAA "Cultures développées" 2000-2020 (core, extends the history) [V], NEW
- Page: https://agreste.agriculture.gouv.fr/agreste-web/disaron/SAANR_DEVELOPPE_2/detail/ . Warning from the page itself: "les séries 2000-2020 [...] diffusées dans les tableaux interactifs sont les séries avant mise en cohérence avec le recensement agricole (RA) 2020 et rétropolation. Les séries mises en cohérence [...] à partir de 2010 sont à privilégier" [V]. The DRAAF Pays de la Loire describes this data as "données 2001-2009 rebasées sur le RA 2010" [V, data presentation PDF 2024].
- Download tested (HTTP 200, 8.8 MB, 21 CSVs of ~6-7 MB):
  ```
  curl -L -o saa_2000_2020.zip "https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAANR_DEVELOPPE_2/FDS_DEVELOPPE_2.zip"
  ```
- Format: `FDS_DEVELOPPE_<year>.csv`, separator `;`, UTF-8, **CR line endings (classic Mac)**: `\r` must be normalised before `read_csv`. 949,415 rows in total. Columns: `NOM, ANNREF, FRANCE, FRDOM, REGION, DEP, N306, N306_MOD, N306_LIB, N027, N027_MOD, N027_LIB, VALEUR, QUALITE` [V].
- Codes: `N306_MOD` 1.13.1 Pois protéagineux, 1.13.2 Féveroles et fèves, 1.13.3 Lupin doux, 6.16.1 Haricots secs, 6.16.2 Lentilles, 6.16.3 Pois secs (casserie). **There is no chickpea.** `N027_MOD`: 020.01 production (q), 050.08 area developed (ha), 070.01 yield (q/ha). National level with `DEP=='...'` and `REGION=='...'`. `DEP` in 2 digits (`77`, `2A`). `QUALITE` is always "OUI"; there are no non-numeric values [V].
- Counts (département, ≥500 ha and yield >0) [V]:

| Crop | Départements 2000-2020 with all 21 years | Départements with 2000-2009 complete | Splice 2000-2025: départements with ≥20/26 years | With 26/26 |
|---|---|---|---|---|
| Pea protéagineux | 36 | 41 | **43** | 27 |
| Faba bean | 6 | 7 | 23 | 6 |
| Lentil | 2 | 2 | 3 (Indre 26, Haute-Loire 26, Aube 20) | 2 |
| Dry bean | 1 | 1 | 1 (Vendée) | 1 |
| Chickpea | n/a | n/a | 0 (max. 16 years: Aude, Gard) | 0 |

- Comparison in the 2010-2020 overlap (dept-year with ≥500 ha in both sources) [V]: pea n=502, 83.5% identical, mean difference -1.28 q/ha, r=0.876, median area ratio 1.0. Faba bean n=432, 95.4% identical. Lentil n=109, 94.5% identical.
- Beware of old national totals: national lentil 2010 gives 6,497 ha in the old series vs 12,186 ha in the new [V]. The RA 2020 rebasing changed the area of small pulses a lot; at département level, with ≥500 ha, the areas match.
- Example series [V]: lentil Haute-Loire 2000-2025: 16, 13, 13, 9, 4, 14, 6, 8, 9, 11, 9, 10, 9, 9, 7, 6.4, 4.9, 8, 7.5, 7.8, 4, 3.5, 4.3, 4.8, 6.6, 5.1 q/ha. Indre: from 7 (2020) to 28 (2002), with 23 repeated in 2021-2023 (suspected imputation).
- **Before 2000:** I did not find downloadable départemental series for 1989-1999 [NV]. A DRAAF says it uses surveys from 1989 [F, search result]. Not worth looking for them during the event.

### 4.3 SAFRAN / SIM2 quotidienne (core, climate) [V]
- Dataset: https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne (licence `lov2`, last modified 29/10/2026). 83 resources: one `QUOT_SIM2_<year>.csv.gz` per year from 1958 to 2026, `QUOT_SIM2_latest.csv.gz`, the coordinate grid, shapefiles and the parameters PDF [V].
  - Note: prior research said "one CSV.gz per year since 1958"; that is correct, and the 2026 file is updated (Last-Modified 27/10/2026, last day 2026-10-26) [V].
- Sizes: 2016 = 137.3 MB, 1976 = 132 MB, 2026 (partial) = 112.5 MB [V]. 1991-2026 ≈ 36 files ≈ 4.7 GB [NV, extrapolation].
- Grid: `coordonnees_grille_safran_lambert-2-etendu.csv` with 9,892 points, columns `LAMBX (hm);LAMBY (hm);LAT_DG;LON_DG`, **decimal commas** [V].
- Columns: `LAMBX;LAMBY;DATE;PRENEI;PRELIQ;T;FF;Q;DLI;SSI;HU;EVAP;ETP;PE;SWI;SSWI_10J;DRAINC;RUNC;...;WG_RACINE;WGI_RACINE;TINF_H;TSUP_H`. Units according to the parameters PDF [V]: rain and snow in mm (06-06 UTC), mean T °C (00-00 UTC), SSI visible radiation in J/cm², ETP Penman-Monteith FAO-56 in mm, TSUP_H = maximum of the 24 hourly temperatures (06-06 UTC), TINF_H minimum (18-18 UTC).
- **Gotcha:** the PDF says SWI is in "%", but the values come as a fraction (0.19 to 1.0 in the examples) [V].
- Quality: 0% NaN in 1976, 2016 and 2026; 366 dates in 2016; 3,620,472 rows per full year [V].
- Join with départements: point-in-polygon with `departements-version-simplifiee.geojson` (gregoiredavid/france-geojson): 8,582 points assigned, **1,310 with no département** (sea, borders or outside France), 95 of 96 départements with points; **Paris (75) has no points**. Points per département: median 93, minimum 3. Haute-Loire 76, Marne 131, Indre 108, Eure-et-Loir 94 [V].
- Control descriptive, 01/03 to 15/06 (total rain, days with TSUP_H ≥25 °C) [V]: 1976 Eure-et-Loir 59 mm and 12 days; 2016 Eure-et-Loir 311 mm and 0 days, Indre 388 mm; 2026 Indre 134 mm and 17 days. The 1976 drought and the wet spring of 2016 are clearly visible.
- Quick download on Friday (in parallel, on an AWS instance in eu-west-3):
  ```
  for y in $(seq 1991 2026); do echo "https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/QUOT_SIM2_$y.csv.gz"; done | xargs -P 8 -n 1 curl -sS -O
  curl -sS -O https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/coordonnees_grille_safran_lambert-2-etendu.csv
  ```
  Read with `usecols=['LAMBX','LAMBY','DATE','PRELIQ','PRENEI','T','TSUP_H','TINF_H','ETP','SWI','SSI']` and aggregate to département straight away: ~1.5 MB in parquet per year remains.

### 4.4 Open-Meteo Historical (auxiliary, only to complete the last days or as fallback) [V]
- `https://archive-api.open-meteo.com/v1/archive?latitude=45.04,48.95&longitude=3.88,4.36&start_date=2026-03-01&end_date=2026-06-15&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration&models=era5_seamless&timezone=Europe/Paris`: HTTP 200, no key, several coordinates in one request, 107 days, 0 nulls in rain [V].
- Last day with data as of 30/10/2026: 2026-10-24 (after that, `None`) [V].
- With `era5_land` rain comes out null [F, prior research]. Use `era5_seamless`.
- Limits: 600/min, 5,000/h, 10,000/day, 300,000/month; "The free API is for non-commercial use" [V, pricing page]. **It is not usable for the commercial product.**

### 4.5 Pea_dataset (protein variant) [V]
- doi 10.57745/FW78RE, Recherche Data Gouv, licence etalab 2.0, published 2026-08-05, version 1 [V].
- Files (Dataverse ids): `crop_traits_data.tab` (764685, 4.6 MB), `metadata.tab` (764683), `trials_data.tab` (764684, 1.5 MB), `weather_data.zip` (764686, 3.0 MB). Download:
  ```
  for p in 764685:crop_traits.csv 764683:metadata.csv 764684:trials.csv 764686:weather.zip; do id=${p%%:*}; f=${p##*:}; curl -sS -L -o "$f" "https://entrepot.recherche.data.gouv.fr/api/access/datafile/$id?format=original"; done
  ```
  (In zsh, `set -- $p` does not split the words: use the form above.)
- `trials`: 4,450 situations × 33 columns (site, postcode, lat/lon, year, soil, winter/spring type, genotype, sowing, irrigation). `crop_traits` in **long format** (`situation_id, variable, value`, 27,168 rows): 4,230 `yield_14` (q/ha at 14%) and 3,326 `protein_content` (%) [V].
- Protein by year: 2003, 2004 and 2013-2024 (**12 years**), with 20 to 473 situations per year. 2005-2012: almost empty [V].
- 256 site-year-type with protein; median 13 genotypes per site-year; only 8 sites have protein in ≥5 years [V].
- Descriptive: the annual mean explains ~27% of the variance of protein between site-years; protein ranges from 16.9 to 29.2%; the site-year correlation between yield and protein is -0.13 [V].
- Climate: 158 files `<site>_weather.csv` (`AN;MOIS;JOUR;ETPP;TMC;RG;RR;TX;TN`), 100% joinable with `weather_file`. **They cover only the trial years** (730 to 4,018 days per site), not a long history [V]. For long-term analogues, SIM2 at the site coordinates must be used.

### 4.6 Auxiliaries
| Dataset | Use in B | Status | Access |
|---|---|---|---|
| FAOSTAT QCL (Europe bulk, 3.9 MB) | National context 1961-2024: Peas dry and Broad beans 64 years, Lentils 57 years, in kg/ha. Pea: 1,900 kg/ha (1961), 4,502 (2000), 2,529 (2016), 2,925 (2024) | [V]. **The FAOSTAT REST API now asks for `Authorization`**; the bulk works | `curl -O https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_Europe.zip` (use `..._NOFLAG.csv`, latin1) |
| Eurostat `apro_cpshr` (NUTS2) | Not usable as a label: for Champagne-Ardenne (FRF2) and Centre (FRB0) it returns area, moisture and production, **but no yield value** | [V] | JSON API without key |
| Derived RPG (`archive/research/datasets/rpg_pulses_dept_year.csv`) | Choose départements by current area and weight the climate | [F], columns `year, code_dep, nom_dep, grp, n_parcelles, surface_ha` [V] | In the repo |
| Département outlines | Assign SAFRAN points | [V] | `curl -L -O https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson` (for production, better IGN ADMIN EXPRESS) |
| INRAE bruchids (doi 10.57745/HPEMYW) | Bruchid variant: **not useful for analogues**: 3 seasons (2020-2022), each field appears in one year only | [F] `idea3_bruchids.md` | |
| BSV OCR archive (PestObserver) | The threshold "> 2 jours > 20 °C au stade jeune gousse" for the bruchid [F] | [F] | |

### 4.7 Tested joins [V]
- New SAA ↔ old SAA: (`crop`, normalised `DEP`, `ANNREF`). OK after normalising the 3 digits.
- SAFRAN ↔ département: point-in-polygon with the grid's lat/lon. OK (except Paris).
- SAA ↔ SAFRAN: by `DEP` and campaign year. For winter pea, the window starts in autumn of year N-1, so **the previous year must also be downloaded** before the first label year (1999 if used from 2000).
- Pea_dataset: `trials.situation_id` ↔ `crop_traits.situation_id` (pivot) ↔ `weather/<weather_file>`. OK at 100%.

---

## 5. AI method

### 5.1 Unit and inputs
- **Case** = (département d, season y). Case base: pea 2000-2025, 43 central départements (≥500 ha in ≥20 years), minus Oise 2010-2019 → ~1,050 cases [V count of départements; approximate total].
- **Query** = (d, y, cut-off date c). Cut-offs: **15/05** (start of flowering of spring pea [NV, confirm with mentor]) and **15/06** (end of flowering). Climate window: 01/10 of y-1 to c (covers winter and spring pea).
- **Features** (SAFRAN département average, per dekad or per month, as a standardised anomaly against the département's normal computed only from earlier years): accumulated rain, accumulated ETP - P (water balance), mean SWI, days with TSUP_H ≥25 °C from 01/05 (Terres Inovia threshold [V]), days with rain >1 mm in April-June (proxy for disease and Aphanomyces [NV]), accumulated SSI radiation in May-June (2016 = little sun [F]), frost days TINF_H < -5 °C in winter (winter pea [NV]).
- **Case target** = relative yield anomaly: `r = yield / past_trend - 1`, with the trend estimated **only with years < y** (for example, the median of the last 5 years or a robust line over the last 10).

### 5.2 Analogue definition and distance (from simple to learned)
1. **Simple analogue:** Euclidean distance over the vector of standardised anomalies with equal weights. It is "what a human would do", systematised. It goes in as the **AI baseline**.
2. **Learned metric (main proposal):** diagonal Mahalanobis distance `d(a,b)=sqrt(Σ w_j (a_j-b_j)^2)`, with weights `w_j ≥ 0` learned **only from cases in years < y**, so that close cases have similar yield anomalies (NCA-style or metric learning, optimised with internal leave-one-year-out over the past). A cheap and robust alternative: weights = |coefficient| of a standardised ridge over the past, or the proximity of a random forest (two cases are close if they fall in the same leaves) trained on the past.
3. **DTW over cumulative daily curves:** an extension, not a requirement. With ~1,000 cases and curves of ~250 days it adds cost and overfitting risk. I leave it on the cut list.
- **Search constraints:** only years < y (never future ones); cases from the same year and from other départements in the same region are excluded if one wants to avoid "copying" the year (a decision is needed: including them is legitimate in real-time production, because the current year does not have a yield yet. **In the backtest they must never be included, because their labels are not known at the cut-off**). Optional: restrict to départements of the same climate cluster.
- **Output:** the k=5-10 nearest neighbours with their weights; estimate = weighted mean of their anomalies × the queried département's trend; interval = weighted quantiles of the neighbours' anomalies, calibrated with conformal methods on earlier backtest years.

### 5.3 Why the AI is essential (jury test)
- Without AI, the user has the 5-year average and their memory ("it looks like 2016"). Human memory recalls few extreme years for their area; the engine **searches ~1,000 département seasons**, **learns which climate dimensions matter** for pea (instead of weighting January rain the same as June rain), **quantifies uncertainty** with the spread of the neighbours, and **is evaluated against the mean** without looking at the future.
- It is case-based reasoning with a learned metric: ranking and recommendation, one of the uses the guide counts as real ("recommendation or ranking"). The explanation comes from the method itself, it is not stuck on top.
- An LLM does not add to the core. It can write the explanation paragraph from the neighbours and their dominant features, but that is decoration: it has to be stated that way.

### 5.4 Information leakage and how to cut it
| Leakage source | Control |
|---|---|
| Labels from the same year or future years in the case base | Case base = years < y, strictly |
| Climate normalisation with future years | Département normals with years < y (or a fixed 1961-1990 SIM2 normal, applied to all test years) |
| Yield trend with future years | Trend only with years < y |
| Metric weights learned with the test year | Re-learn the weights in each fold with years < y |
| Revised SAA (back-calculation 2010-2019, base change in 2010) | Declare it: it is a backtest on revised data, not on what was published in real time |
| SAFRAN is a reanalysis (also revised) | Declare it |
| Regional imputations (départements with the same yield) | Also evaluate at region-year level and report the effective n |
| Choosing départements by current area (RPG 2024) | Minor; declare it or choose them with area ≤ test year |

### 5.5 Validation
- **Rolling origin (leave-future-out):** for each test year and in 2010..2025, the case base is years 2000..y-1. With that, the first test years have ~10 years of history and the last ones ~25.
- **Baselines:** B0 = median of the département's previous 5 years; B1 = robust département trend; B2 = analogues with equal weights; (optional) B3 = ridge over the same features (idea 4).
- **Metrics:** MAE in q/ha by test year and overall; skill = 1 - MAE_model/MAE_B0; detection of a "bad year" (anomaly < -15%): precision and recall; 80% interval coverage; all with **effective n = number of years** (16 test years, not 600 département-years).
- **Pre-registered success criterion** (write it in the README before running anything): the learned metric beats B0 in MAE in ≥10 of 16 test years and in the overall MAE. If not, it is said in the pitch and the product is sold as "a climate analogue season explorer with an honest estimate".
- **Lentil:** only Haute-Loire and Indre (26 years): shown as a human use case, without claiming statistical validation.

### 5.6 Explainability
- For each neighbour: département, year, actual yield, anomaly, and the 3 features that bring it closest and the 3 that push it furthest (contribution `w_j (a_j-b_j)^2`).
- Overlaid curves of accumulated rain, water balance and days >25 °C: the queried season against the 3 main neighbours.
- Learned metric weights as "what the model learned matters for pea" (and check against agronomy: heat at flowering, water in May-June).

### 5.7 Variants evaluated
| Variant | Data | Feasibility | Verdict |
|---|---|---|---|
| **B-pea-département (recommended)** | SAA 2000-2025 + SIM2 | High | Best rigour/time ratio |
| 2 as the explanation layer of 4 | Same | High | Good: the idea 4 estimate is justified with neighbours. Merging them into a single engine (the estimate is the neighbours') is more coherent than having two models |
| B-protein (Pea_dataset) | 256 site-years with protein, 12 years | Medium | Directly tied to the food industry (extraction yield). But the analogues would be trial site-years, without grain collection scale; the year explains only 27% of the variance [V]. Serves as a **second tab** if time allows or as a layer of Idea 1 |
| B-bruchid | 3 years of damage | Low | Not enough seasons for analogues. At most, a SIM2 climatology of the ">2 jours >20 °C" threshold by département since 1958, which is a rule, not AI |
| B-lentil Haute-Loire (AOP Puy) | 26 years | Medium for demo | Very good human story; n=26 in a single département: demo only |

---

## 6. MVP and demo

### 6.1 Screens
1. **Query:** pea département map (coloured by area), selector for département, season and cut-off date (15/05 or 15/06).
2. **Twin seasons:** cards for the 5 neighbours (département, year, anomaly, yield), overlaid curve chart (accumulated rain, water balance, days >25 °C) and a "why they look alike" with the dominant features.
3. **Estimate:** fan of expected yield (median and 80% interval) next to B0 and, for past years, a "reveal" button showing the actual SAA value.
4. **Confidence:** backtest table by year (model MAE vs B0, bad-year hits) and the effective n. Banner with "revised data, reanalysis, imputations".
5. **2026 live:** the current season at 15/06/2026 against the 2000-2025 base.
6. (Extension) **Lentil Haute-Loire:** the same view, labelled as experimental.

### 6.2 Live demo script (≈75 s within the 4 min)
1. "We are the grain collection manager of a cooperative in Eure-et-Loir, 15 June 2016." Choose Eure-et-Loir, 2016, cut-off 15/06 (2016 is a test year with base 2000-2015).
2. The neighbours and the explanation appear ("very wet spring, little radiation in May-June"; this is only an example: show what the model gives, without making things up).
3. Show the estimate with its interval against the 5-year average. Reveal the actual value (Eure-et-Loir 2016 in the SAA).
4. Switch to 2026, same département: "this is what you would have seen this year". If an Agreste 2026 conjoncture estimate for pea exists, show it alongside [NV, look for it on Friday].
5. Ten seconds on the confidence screen: "over 16 test years we beat (or did not beat) the average in X". **Never show a hand-picked year as if it were the rule.**

### 6.3 Stack
- Python 3.12 + `uv`, pandas/pyarrow, numpy, scikit-learn (ridge, RF for proximity), optional `metric-learn` for NCA [NV whether it is needed]; shapely for the spatial assignment.
- App: **Streamlit** (fastest for three people), with plotly. Deploy on AWS (small EC2 or App Runner) plus a copy on Streamlit Community Cloud or a backup video, in case the network goes down.
- Processed data (parquet of a few MB) versioned in the repo; raw data, no.

### 6.4 Repo structure
```
campagne-jumelle/
  README.md            # problem, data, licences, prior resources, pre-registered success criterion
  data/raw/            # .gitignore
  data/processed/      # saa_spliced.parquet, sim_dep_daily_YYYY.parquet, features_cut.parquet
  src/etl_saa.py       # splice 2000-2009 + 2010-2025, département codes, Oise and imputation flags
  src/etl_sim2.py      # parallel download, département assignment, daily aggregation
  src/features.py      # windows at the cut-off, anomalies with past normals
  src/analogs.py       # simple distance, learned metric, neighbours, interval
  src/backtest.py      # rolling origin, baselines, metrics, effective n
  app/streamlit_app.py
  notebooks/eda.ipynb  # descriptive only
  deck/                # PDF from the official template
```

---

## 7. Work plan (Fri 20:45 to Sun 9:30)

Roles: **A** = data and evaluation, **B** = modelling (the ML/CV student), **C** = product, business and pitch.

| Time | A (data/eval) | B (modelling) | C (product/business/pitch) | Checkpoint |
|---|---|---|---|---|
| **Fri 20:45-21:30** | Spin up AWS (EC2 in eu-west-3) and launch the parallel download of SIM2 1999-2026 + the two SAA files | Read this dossier and write the success criterion in the README | Find a cooperative or Terres Inovia mentor: user, decision, date | |
| 21:30-22:30 | SAA ETL: splice and flags (Oise, regional duplicates) | SIM2 ETL: département assignment and aggregation of 3 test years | Validate H9 with the mentor and note the answers | |
| 22:30-23:00 | Coverage table by département | Cut-off features script (1 département) | **Declare track 3** and prior resources | **GO/NO-GO 1 (22:45):** does the mentor confirm a May-June decision? If not, pivot to autumn contracting (same engine, another cut-off) or merge with another idea |
| **Sat 9:30-10:15** | Workshop (one person); the other two carry on | Full SIM2 aggregation (in background) | Workshop | |
| 10:15-13:00 | Master table case × features × anomaly (43 départements, 2000-2025) | Simple analogues (B2) + B0/B1 baselines in the backtest loop | Streamlit skeleton with fake data marked as synthetic | **CP 2 (12:00):** the master table exists and has no gaps. If not, reduce to 15 départements and 2010-2025 |
| 13:00-14:00 | Lunch | | | |
| 14:00-16:00 | Rolling origin backtest and metrics by year | Learned metric (weights by ridge or NCA) re-trained per fold | Connect the app to real data; neighbours screen | **CP 3 (16:00):** first backtest number. **Stopping rule:** if the learned metric does not beat B2 and B0, stop iterating on the model: freeze the simple version and put the effort into honesty and UX |
| 16:00-18:00 | Conformal intervals and coverage; leakage audit (checklist 5.4) | Per-feature explanations; overlaid curves | Business: pricing, market, competitors; first draft of the deck | **CP 4 (17:45):** end-to-end demo for one département and one year. Repo backup to GitHub before leaving campus |
| Sat 19:00-23:00 (off campus) | Backtest figures for the deck; lentil Haute-Loire (optional) | 2026 live view; smoke tests | Full deck, script, project sheet | **CP 5 (22:00):** timed rehearsal number 1 |
| 23:00-00:30 | Freeze the data; hashes in the README | Deploy on AWS + backup | Rehearsals 2 and 3, Q&A | Cut-off: nothing new after 00:30 |
| **Sun 8:30-9:15** | Check the links | Smoke test of the deployed app | Final PDF from the template + online sheet | |
| **9:15** | | | **Submit** (deadline 9:30) | |
| 12:00 | Backup of everything outside AWS | | | |

**Backup plan:** if SIM2 does not download in time, use Open-Meteo `era5_seamless` at a centroid per département for 15 départements (within the free tier, non-commercial use during the hackathon), and say so. If the model does not beat the average, present the explorer with an honest estimate ("over 16 years we did not beat the average on MAE, but we detected X of Y bad years"), provided that is what comes out.

**Cut list (in order):** DTW → lentil → protein tab → RPG weighting → 15/05 cut-off (only 15/06 left) → conformal (the neighbours' empirical range remains).

---

## 8. Business

### 8.1 Value proposition
"On 15 June, the cooperative knows which past seasons the current one resembles in each département in its area, how much they yielded and with what uncertainty, to size forward sales, reception and complementary purchases of pea for the food industry."

### 8.2 Who pays
1. **Cooperative or storage body** that contracts pea or lentil for human food, as a module within its OAD package or its grain collection tool.
2. **Processor** (Roquette, Cosucra) as a licence for "supply intelligence" over its collection basin.
3. **Interprofession** (Terres Univia) as a financed public good.

### 8.3 Price benchmarks
| Reference | Value | Status |
|---|---|---|
| Unéal ODACIO 2026 (cooperative OAD packages) | From €300/year; options "+ €12/ha" (cap 400 ha), "+ €5/ha", "+ €16/ha (1 year)" | [V] Unéal PDF |
| Sencrop stations via chambre | €16/month per station | [F] `track3_context.md` |
| Farmstar via cooperative | €8-10/ha (old figure) | [F] |
| Climadiag Agriculture | Free | [V] Réussir 05/12/2024 |
| Open-Meteo commercial | Paid plan with no public price | [V] |

**Proposed price [NV]:** €2,000-8,000/year per cooperative depending on the contracted pulse area (or ~€1-2/t of food-grade pulse collected). To be validated with the mentor.

### 8.4 Market size
- Collectors: 477 (117 cooperatives, 360 négociants) in 2024/25; ~12,400 producers delivering protein crops in 2024 [V, FranceAgriMer filière sheet 2026].
- Pea 2025: 97,884 ha and 348 kt [V, SAA]; protein crops to human food 146 kt in 2024/25 [V].
- **Estimate [NV]:** if 30-60 collectors contract food-grade pulses and pay €3-8k/year → **€0.1-0.5m/year** in France, pea only. With lentil, chickpea, faba bean and other European countries it could reach a few €m [NV]. It is a small business: the pitch has to be honest ("niche product, low marginal cost, scalable to any crop with departmental statistics").

### 8.5 Adoption path
1. Free pilot with a cooperative that already contracts food-grade pea (SCAEL profile) in the 2027 season, on its 3-5 départements, comparing against its own collection (which is a better label than the SAA).
2. Integration into the cooperative's OAD package (API or widget).
3. Scale to other crops and countries with the same recipe (regional statistics + climate reanalysis).

### 8.6 Competitors and differentiation
| Actor | What it does | Difference |
|---|---|---|
| Climadiag Agriculture (Météo-France + Solagro) | Free, >200 indicators, 8 km, projections 2030/2050/2100 [V] | Projects future climate; does not compare the current season with past seasons or link them to pulse yields |
| Météo-France services | Seasonal forecasts (51 members [F]), "rejouent 24 années passées" [V, 2019] | Climate scenarios, not departmental pulse yield |
| Sencrop / Weenat | Connected stations, disease models [F] | Real-time plot data, with no memory of departmental yields [NV] |
| ITK and crop models | Plot-level DSS [NV, did not review their pulse catalogue] | Plot scale and mechanistic models; ours is statistical, at collection scale |
| Arvalis / Terres Inovia | National harvest forecasts, "prévisions fréquentielles" [V] | Do not publish departmental pulse estimates [NV] |
| JRC MARS | Field peas at EU level [F] | EU or country scale |
| Cooperatives' in-house tools | Field tours, technicians' estimates [NV] | Complementary: our engine gives an objective, comparable base across départements |

---

## 9. Impact and sustainability

- **Mechanism:** less volume risk for whoever contracts food-grade pulses → more willingness to contract hectares → more pulse area for human food. The causal chain is plausible, but **not demonstrated** [NV]. The measurable direct impact is better volume estimation.
- **Order of magnitude [NV, estimate]:** a cooperative with 5,000 ha of pea faces a typical yield swing of ±5-10 q/ha between seasons (the national weighted range 2016-2025 was 23.4-38.7 q/ha [V]), i.e. 2,500-5,000 t, about €0.5-1.4m at €220-275/t [F prices]. If the engine reduces the mid-June estimation error by X% (to be measured in the backtest), the expected value is proportional. **No saving is quantified until the backtest exists.**
- **Environmental [F]:** dry lentil emits 0.58 kg CO2e/kg against ~29 for beef (Agribalyse 3.2, per `datasets.md`). Attributing an animal-protein substitution to the product would be speculative: it goes in as context, not as product impact.
- **Sovereignty:** imported lentil runs at ~40.8 kt/year (46% from Canada) [F, `datasets.md`, Comext]. Making local production less risky points in that direction, without figures of our own.
- **Product sustainability:** open data (Licence Ouverte), negligible compute cost (all aggregated climate fits in <50 MB), and re-trained once a year.
- **For the pitch:** separate on the slide what is measured (backtest), what is sourced (SAA, FranceAgriMer) and what is assumed (economic impact).

---

## 10. Pitch

### 10.1 4-minute script
| Time | Block | Content |
|---|---|---|
| 0:00-0:40 | Problem | "2016: French pea fell to 23 q/ha, half of 2002. Nobody saw it coming (Ben-Ari 2018). Whoever contracted pea for the food industry came up short." User: grain collection manager of a cooperative, decision on 15 June |
| 0:40-1:20 | Solution | "Campagne jumelle": 26 seasons × 43 pea départements = ~1,000 cases; daily SAFRAN climate; learned metric that finds the seasons most alike up to the cut-off date and returns expected yield with interval and its reasons |
| 1:20-2:40 | Live demo | Script 6.2 |
| 2:40-3:20 | Rigour | 16-year backtest without looking at the future, against the 5-year average; effective n = years; limits (revised data, imputations, trend) |
| 3:20-4:00 | Scale and business | Pilot with one cooperative, OAD module at €2-8k/year, extension to lentil, chickpea, faba bean and Europe; all with open data |

### 10.2 Slides (official template)
1. Title + team + track. 2. Problem with the pea chart 2000-2025 (2016, 2020, 2024 marked). 3. User and decision (persona + calendar). 4. Solution (diagram cases → metric → neighbours → estimate). 5. Data (SAA 2000-2025, SIM2, licences, labels measured/sourced/assumed). 6. Demo (backup screenshots). 7. Backtest results (by year, vs B0, effective n). 8. Limits. 9. Business and adoption. 10. Impact (with labels). 11. Declared prior resources + link to the repo and demo.

### 10.3 Likely jury questions
| Question | Prepared answer |
|---|---|
| "Isn't it just a kNN?" | It is kNN with a metric learned from past data to weight the variables that matter for pea, with anomalies and trend without leakage and with calibrated intervals. We compare it against the equal-weight kNN (B2) and report it |
| "How many independent data points do you have?" | 16 test years; départements in the same year are correlated, so we report error by year |
| "Isn't the SAA imputed?" | Partly: 23-33% of pea yields repeat across départements in the same region [V]. That is why we also evaluate at region-year level and exclude Oise 2010-2019 |
| "Why not a crop model?" | It needs variety and soil calibration we do not have in 20 h; the statistical approach is transparent and cheap. Complementary, not a rival |
| "Isn't pea feed?" | In 2024/25, 146 kt of protein crops went to human food (FranceAgriMer); the chosen user contracts for the food industry. And the same engine runs on lentil |
| "What about climate change, if the old years no longer represent?" | We use anomalies relative to the recent trend and moving normals; analogues can be restricted to the last N years. It is a real limit |
| "What if June changes everything after the cut-off?" | We show two cut-offs and how the interval narrows; the neighbours also bring their June-July as scenarios |
| "Who pays?" | The cooperative, as a module within its OAD package (ODACIO benchmark: from €300/year + €/ha) |

---

## 11. Risks, mentors, prior resources and deliverables

### 11.1 Risks and mitigations
| Risk | Prob. | Mitigation |
|---|---|---|
| Does not beat B0 | Medium-high | Pre-registered criterion; state it honestly; strengthen bad-year detection and explainability |
| SIM2 download slow | Medium | AWS in Paris, in parallel, from Friday; Open-Meteo fallback |
| User or decision not confirmed | Medium | Mentor on Friday; pivot to the contracting cut-off |
| Trend badly estimated (few years at the start) | Medium | Robust 5-year median; start the test in 2010 |
| The jury sees it as "not AI" | Medium | Learned metric + explicit comparison against the naive analogue |
| "Animal feed" exclusion | Low | User = contracts for human food; lentil as a case |
| Demo fails | Low | Screenshots and video in the deck; local app |

### 11.2 Questions for mentors
1. On what date does a cooperative commit pea or food lentil volume, and with what information?
2. Do they informally use "c'est une année comme 2016"? Would it help them to see the neighbours?
3. What mid-June estimation error would be useful (±3 q/ha, ±5 q/ha)?
4. Would they pay for something like this, or do they expect it free from Terres Inovia or the interprofession?
5. Are there collection series by cooperative or by silo that we could use as a label in a pilot?
6. Do Terres Inovia or Arvalis have any unpublished departmental pulse forecast?
7. For AWS: can ~5 GB be downloaded to an eu-west-3 instance with the credits?

### 11.3 Prior resources to declare
- This desk research (dossier, data audits in `research/`): no solution code and no results.
- Exploration scripts used to count and describe (not reused in the solution).
- Public datasets: Agreste SAA (Licence Ouverte), SIM2 (Licence Ouverte v2), Pea_dataset (etalab 2.0), FAOSTAT, france-geojson (check its licence in the repo before using it [NV]), derived RPG (Licence Ouverte).
- Generic libraries (pandas, scikit-learn, Streamlit).

### 11.4 Deliverables checklist
- [ ] Deck PDF from the official template, with the link to the repo and the demo.
- [ ] Project sheet completed online.
- [ ] Public repo (or accessible to the jury) with README: data, licences, prior resources, success criterion and results labelled measured/sourced/assumed/synthetic.
- [ ] Demo deployed and tested from another network; backup video.
- [ ] Track declared before 23:00 on Friday.
- [ ] Backup outside AWS (before 12:00 on Sunday).

---

## 12. Rubric (own estimate)

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Impact and sustainability | 30% | 6 | Real problem (volatility, 2016), but the link to more food-grade pulses is indirect and the user is not validated; the economic impact can only be estimated after the backtest |
| Scientific and technical rigour | 20% | 7 | 26 seasons, leak-free backtest, baselines, effective n, imputation audit; limited by revised data and trend |
| Appropriate use of AI | 20% | 6 | Case-based reasoning with a learned metric and intervals: the AI is the product. Risk of being seen as "a kNN" if it does not beat the naive analogue |
| Economic viability | 20% | 5 | Identifiable user and real price benchmarks, but small market and willingness to pay not validated |
| Execution and pitch | 10% | 7 | Visual, intuitive demo ("looks like 2016"), simple stack |
| **Weighted total** | | **6.1** | 0.3×6 + 0.2×7 + 0.2×6 + 0.2×5 + 0.1×7 = 6.1 |

To raise it: confirm the user's decision with a mentor (impact +1, economics +1) and have the learned metric beat the naive analogue (AI +1).

---

## 13. Sources (only pages or files I opened today)

Data and documentation:
- Agreste, SAA séries longues 2010-2025: https://agreste.agriculture.gouv.fr/agreste-web/disaron/SAA-SeriesLongues/detail/ and the linked ZIP [V].
- Agreste, SAANR_DEVELOPPE_2 "Cultures développées" 2000-2020: https://agreste.agriculture.gouv.fr/agreste-web/disaron/SAANR_DEVELOPPE_2/detail/ and https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAANR_DEVELOPPE_2/FDS_DEVELOPPE_2.zip [V].
- DRAAF Pays de la Loire, statistical data presentation 2024: https://draaf.pays-de-la-loire.agriculture.gouv.fr/IMG/pdf/2024-presentation_donnees_statistiques_pdl.pdf [V].
- data.gouv, Agreste SAA (licence): https://www.data.gouv.fr/datasets/agreste-statistique-agricole-annuelle-saa/ [V].
- data.gouv, SIM quotidienne: https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne (API, files 1976/2016/2026, grid, parameters PDF https://static.data.gouv.fr/resources/donnees-changement-climatique-sim-quotidienne/20260331-150448/sim-quotidienne-parametres-20260331.pdf) [V].
- Open-Meteo archive API (test query) and pricing: https://open-meteo.com/en/pricing [V].
- Recherche Data Gouv, Pea_dataset doi:10.57745/FW78RE (API and files) [V].
- FAOSTAT bulk: https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_Europe.zip [V].
- Eurostat `apro_cpshr` (JSON API) [V].
- france-geojson: https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson [V].
- FranceAgriMer, protein crops filière sheet 2026: https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf [V].
- Unéal, ODACIO 2026 brochure: https://uneal.com/INTERSHOP/static/WFS/ADVITAM-Site/Uneal/ADVITAM-Uneal/fr_FR/Nos%20services/Plaquette_ODACIO_2026.pdf [V].

Press and technical:
- Terre-net, "Blé tendre 2024: des rendements estimés en forte baisse" (05/07/2024): https://www.terre-net.fr/ble/article/869327/ble-tendre-2024-des-rendements-de-ble-tendre-estimes-en-forte-baisse [V].
- Terre-net / Terres Inovia, "Semer précocement pour sécuriser le potentiel des protéagineux de printemps" (15/02/2022, upd. 25/08/2022): https://www.terre-net.fr/pois-proteagineux/article/205909/semer-precocement-pour-securiser-le-potentiel-des-proteagineux-de-printemps [V].
- Pleinchamp, "La météo saisonnière au service de décisions stratégiques en agriculture" (05/06/2019): https://www.pleinchamp.com/actualite/grandes-cultures~culturales-la-meteo-saisonniere-au-service-de-decisions-strategiques-en-agriculture [V].
- Réussir, "Climadiag Agriculture, le service gratuit de Météo-France et Solagro" (05/12/2024): https://www.reussir.fr/climadiag-agriculture-le-service-gratuit-de-meteo-france-et-solagro-pour-sadapter-au-rechauffement [V].

Literature (metadata verified via Crossref or NTRS; I did not read the content in full):
- Ben-Ari T. et al. (2018). Causes and implications of the unforeseen 2016 extreme yield loss in the breadbasket of France. Nature Communications. doi:10.1038/s41467-018-04087-x [V metadata].
- Paudel D. et al. (2021). Machine learning for large-scale crop yield forecasting. Agricultural Systems. doi:10.1016/j.agsy.2020.103016 [V metadata].
- Liu, Kim, Fleisher, Kim (2021). Analogy-Based Crop Yield Forecasts Based on Temporal Similarity of Leaf Area Index. Remote Sensing. doi:10.3390/rs13163069 [V metadata].
- Chen, He, Dong, Li (2022). Weather records from recent years performed better than analogue years when merging with real-time weather measurements for dynamic within-season predictions of rainfed maize yield. Agricultural and Forest Meteorology. doi:10.1016/j.agrformet.2022.108810 [V metadata].
- NASA NTRS 20120003729 (2011). Retrospective Analog Year Analyses Using NASA Satellite Data to Improve USDA's World Agricultural Supply and Demand Estimates [V metadata].

Not opened: the FranceAgriMer/Arvalis/Terres Inovia statement of 05/08/2016 on the 2016 harvest (expired TLS certificate on `www-rec.franceagrimer.fr`; not cited).

Prior repo research used as [F]: `archive/research/ideas2_4_time_series.md`, `archive/research/datasets.md`, `archive/research/track3_context.md`, `archive/research/idea1_pea_protein_market.md`, `archive/research/idea3_bruchids.md`.
