# Idea 3: damage risk ranking for bruchids (Bruchus) in lentil and faba bean, independent verification

Date: 29/10/2026. Author: verification with data I downloaded myself, without training or fitting any model (respecting the hackathon rule). Only counts, joins, missingness and descriptive statistics.

Scripts: `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/idea1_scripts/` (`peek.py`, `audit.py`, `grains.py`, `misc.py`, output in `audit_out.txt`, per-field descriptive table in `field_level.csv`).
Data: `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/idea1_data/`.

## TL;DR

- All the numbers in the previous brief are confirmed (481 / 397 / 100 fields / 57 lentils / 43 faba beans, 420, 315, 105, 3870 / 86 / 85). What the brief **does not say** and what changes the idea:
  1. **The damage is huge**: median per field 13,7 % in faba bean and 33,4 % in lentil. **No field** is at ≤2 %, only 3 faba beans at ≤3 % and 5 lentils at ≤10 %. A "fit for human consumption yes/no" classifier with a commercial threshold is degenerate: almost everything is "no".
  2. **91 of the 100 labelled fields are organic** (the rest are soil conservation, plus 1 conventional, none with insecticide, according to the data paper). It is not a representative sample of commercial export faba bean production in France (mostly conventional).
  3. **The label is noisy**: in 65 % of the rows **25 grains** were inspected; 65 of 100 fields have ≤100 grains in total. Binomial standard error ~4,6 pp at 30 % damage with 100 grains.
  4. **69-70 % of the variance in damage is "field identity"**, and distance to the field edge explains <1 % (Chery-Lagrange et al. 2026). The problem is between fields, not within a field: good for a field ranking, bad for "edge hotspots".
  5. **No coordinates**: only 4 "Productionregion" values (Paris, Nogent-sur-Seine, Toulouse, Dijon). The climate data come from SAFRAN (8 km), already aggregated by phenological windows.
  6. **I found no published predictive or ranking model on this dataset** (a real gap), but there is a "drivers" paper by the same authors announced as under review, and an already published IOBC summary with landscape drivers.
- Feasibility in 20 h: **5/10**. Technically easy (small tables, clean joins), but the product is weak: the real commercial problem (thresholds of ~1-3 % for human consumption, see below) cannot be represented with these data, and "essential AI" is debatable with ~100 rows.

## 1. Dataset metadata (verified via the Dataverse API)

- DOI 10.57745/HPEMYW, version **2.0**, published 2026-09-01T13:24:08Z, license **etalab 2.0**. Source: `https://entrepot.recherche.data.gouv.fr/api/datasets/:persistentId/?persistentId=doi:10.57745/HPEMYW`.
- Title: "Spatio-temporal field, landscape and meteorological datasets describing bruchid beetle populations, grain damage and parasitism in faba bean and lentil fields in France". Contact: Antoine Gardarin (INRAE). Funding declared in the metadata: **Soufflet** (now the InVivo group, according to the data paper).
- Collection: 2020-04-01 to 2022-09-01. "Year" in the tables = harvest year (2020, 2021, 2022).
- 8 `.tab` tables (originally xlsx) + `READ_ME.txt` (which refers everything to the data paper; missing-value code `NA`).

| id | file |
|---|---|
| 722703 | Agricultural_practice_characterization.tab |
| 722704 | Yield_and_seed_damage.tab |
| 722705 | Bruchids.tab |
| 722706 | Flower_cover.tab |
| 722707 | Extrafloral_Nectar.tab |
| 722708 | Landscape.tab |
| 722709 | Meteorological_data.tab |
| 722702 | Parasitism.tab |
| 769369 | READ_ME.txt |

Design (practices table, 105 fields):

| Year | Region | Faba bean | Lentil |
|---|---|---|---|
| 2020 | Nogent-sur-Seine | 5 | 5 |
| 2020 | Paris | 6 | 4 |
| 2020 | Toulouse | 3 | 7 |
| 2021 | Nogent-sur-Seine | 5 | 5 |
| 2021 | Paris | 7 | 8 |
| 2021 | Toulouse | 3 | 7 |
| 2022 | Dijon | 7 | 0 |
| 2022 | Nogent-sur-Seine | 6 | 5 |
| 2022 | Paris | 3 | 8 |
| 2022 | Toulouse | 0 | 11 |

Faba bean: 35 winter + 10 spring. Each field appears in only one year (no fields repeated across years). Dijon exists only in 2022 and only with faba bean; Toulouse 2022 only has lentil. Region and year are partly confounded.

## 2. Tables: exact columns, units, rows, missing values

### Yield_and_seed_damage.tab (481 rows, 103 fields) [target]
Columns: `Year`, `Productionregion`, `Crop`, `Cropcultivated`, `Field`, `Distancetothefieldedge(m)` (1 NA), `Numberofbruchid-damagedgrains` (84 NA), `Numberofnobruchid-damagedgrains` (83 NA), `Meancropdensity(plants/m2)` (197 NA), `Yield(g/m2)` (128 NA), `Thousand-grainweight(g)` (178 NA).

- Valid rows (both counts present and sum >0): **397**, **100 fields** (57 lentil, 43 faba bean). 83 rows with both NA, 1 with only one NA, 0 with sum 0. **Confirms the brief.**
- 3 to 4 rows per field (median 4). Distances: 5, 15, 30 m almost always, plus a fourth (50 m in 2020; the field "centre" with variable distance 35-610 m in 2021-2022).
- **Grains per row: median 25** (65 % of rows exactly 25; 87 % ≤100; max 1531 in lentil 2022). Per field: median 100 grains, 65/100 fields with ≤100. The data paper says "random sample of 25 grains per distance".
- Practice fields without a valid label: ID044, ID045, ID062, ID065, ID079 (Paris/Toulouse 2021-2022).

### Meteorological_data.tab (420 rows, 105 fields × 4 stages) [predictors]
Columns: `Year`, `Productionregion`, `Crop`, `Cropcultivated`, `Field`, `Cropstage` (Vegetative, Flowering, Young pod, Mature pod), `Numberofdayswithameantemperatureabove12°C` (days), `Numberofdayswithameantemperaturebetween20°Cand25°C` (days), `Cumulatedprecipitation(mm)`, `Meanprecipitationperday(mm)`, `Maximumprecipitation(mm)`, `Maximumdailywindspeed(m/s)`.

- 8 NA rows = 2 complete fields (ID057, ID063, Toulouse 2021).
- Source according to the data paper: SAFRAN (Météo-France's meteorological reanalysis, 8 km grid, via SICLIMA); windows defined with crop stage dates observed in the field surveys. Watch out: the data paper summary describes 3 windows, but the table has 4 (it includes Mature pod).
- Granularity: in 2020-2021 almost every field has its own vector; in 2022 there are many repeats (Dijon 2022: 3 distinct vectors for 7 fields), consistent with shared SAFRAN cells.

### Landscape.tab (315 rows = 105 fields × buffers 500/1000/2000 m)
Columns: `Year`, `Productionregion`, `Crop`, `Cropcultivated`, `Field`, `Bufferzone(m)`, `Areaoforganicagriculture(%)`, `Areaofcropthesameyear(%)`, `Grassland(%)`, `Areaofcropthepreviousyear(%)`, `Woodyhabitats(%)`, `Totallinearmetersofhedgerows` (m). **No missing values.**

- Sources (data paper): RPG 2019-2022 (Registre parcellaire graphique, the French plot register), OSO 2023 (land-cover map), BD TOPO 2024 (IGN topographic database), national hedgerow database 2024, RPG Bio 2021, around the field **centroid**. Hedgerows and organic status assumed constant 2020-2022.
- Units, watch out: `Grassland(%)` has values like 0,024-0,67, which looks like a fraction or a very low %; `Areaoforganicagriculture(%)` reaches 61 %. The scale must be checked before use (not verifiable without the full paper).

### Agricultural_practice_characterization.tab (105 rows, key `Parcelle`)
28 columns: `Year`, `Productionregion`, `Parcelle`, `Crop`, `Cropcultivated`, `Modeofproduction(organicfarming,soilconservationagricultureorconventional)`, `Cropvariety` (2 NA), `Fieldarea(ha)` (19 NA), `Fieldperimeter(m)` (11 NA), `Fieldcentre(maximalsurveyeddistancefromfieldedge,m)`, `Intercroppedspecies,ifapplicable` (23 NA), `Dominantvegetationatfieldedge(onlygrassystrip,hedgeorwoodland)` (15 NA), `Sowingdate` (21 NA), `Seedorigin(...)` (21 NA), `Seedtreatment(yes/no)` (19 NA), `Sowingdensity(seeds/m2)` (22 NA, **string**: one value reads "80 (Axel) et 100 (nebraska)"), `Mouldboardploughing(yes/no)` (53 NA), `Weederharrow(numberofpassages)`, `Rotaryhoe(...)`, `Hoeing(...)`, `Pollarding(...)`, `Herbicides(numberoftreatments)`, `Fungicides(numberoftreatments)`, `Fertilisation(yes/no,specifiedifapplicable)` (free text), `Quantityoffertilizer(kg/ha)`, `Farmers'syield(kg/ha)` (46 NA), `On-farmseedstorage(yes/no)` (23 NA), `Presenceofalegumestockpilewithin2km(yes/no)` (23 NA).

Problems detected:
- **There is no insecticide column.** Production mode: 94 organic, 10 soil conservation, 1 conventional (among the 100 labelled: 91 organic).
- `Sowingdate` is an Excel serial (origin 1899-12-30). Range: winter faba bean 2019-10-20 to 2020-12-05, lentil 2020-02-25 to 2022-04-15.
- `Farmers'syield(kg/ha)`: values from 2,3 to 58, clearly **quintals/ha (q/ha)**, not kg/ha. Unit error in the header.
- `Quantityoffertilizer(kg/ha)`: up to 90 000, mixes compost in kg with mineral fertilizer; unusable without manual cleaning (the data paper says kg N/ha, which does not match).
- Practices block almost empty for 2022 Dijon and 2022 Nogent (18 NA per row on average). 19 labelled fields with ≥10 NA.
- Varieties with typos (Axel/Axell, "Diva Probabon"). Lentil: Anicia 35/57 (the variety of the Lentille verte du Puy AOP, the Le Puy protected designation of origin green lentil).

### Bruchids.tab (3870 rows, 86 fields)
Columns: `Year`, `Productionregion`, `Crop`, `Cropcycle`, `Field`, `Cropstage` (**only 3**: Vegetative, Flowering, Young pod; the brief does not clarify this), `Distancetothefieldedge(m)` (9 NA), `Bruchidsex` (Female/Male/Not Available, exactly 1290 each: long format with one row per sex), `Numberofbruchids`.

- 85 fields with a valid label (+ ID062 without a label). **Confirms the brief.**
- Counts missing in 15 labelled fields, 10 of them in Paris 2022.
- Method changed: suction sampling in 2020 (very low catches, 10 % of cells >0, total 804 insects) vs entomological net 2021-2022 (totals 5632 and 2538). Not comparable across years without normalization.

### Others (not used in the MVP)
- Parasitism.tab: 449 rows, 101 fields, post-harvest measurement (seed rearing). **Pure leakage**.
- Flower_cover.tab: 660 rows, 83 fields, 4 stages.
- Extrafloral_Nectar.tab: 74 rows, 38 fields (faba bean only).

## 3. Joinability

- Keys match exactly (`Field` = `Parcelle`, format `ID001`..`ID105`). Year/region/crop are consistent across tables for the 100 labelled fields (0 discrepancies).
- Label ∩ climate (no NA) ∩ landscape ∩ practices: **98 fields**. Adding bruchid counts: **83 fields**.
- Label ∩ early climate (complete Vegetative + Flowering): 98.
- But "practices" for those 98 has a lot of missing data (see above); a model with practices loses or imputes ~20 fields, concentrated in 2022 Dijon/Nogent (non-random missingness).

## 4. Damage distribution (% of grains with bruchid, aggregated per field = sum of damaged grains / sum of grains)

The row mean and the pooled per-field value correlate at 0,9999, so the definition barely matters.

| Crop | n | mean | median | sd | min | Q1 | Q3 | max | ≤3 % | ≤5 % | ≤10 % | >10 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Faba bean | 43 | 22,9 | 13,7 | 22,6 | 2,1 | 7,2 | 32,5 | 94,0 | 3 | 4 | 15 | 28 |
| Lentil | 57 | 34,2 | 33,4 | 18,8 | 4,3 | 18,0 | 49,0 | 74,0 | 0 | 2 | 5 | 52 |

**No field at ≤1 % or ≤2 %.**

By year:

| Crop | Year | n | mean | median | ≤10 % |
|---|---|---|---|---|---|
| Faba bean | 2020 | 14 | 37,2 | 21,5 | 2 |
| Faba bean | 2021 | 14 | 18,4 | 12,5 | 6 |
| Faba bean | 2022 | 15 | 13,9 | 10,3 | 7 |
| Lentil | 2020 | 16 | 22,6 | 19,0 | 4 |
| Lentil | 2021 | 17 | 34,0 | 30,0 | 1 |
| Lentil | 2022 | 24 | 42,0 | 45,5 | 0 |

By region: faba bean Dijon 8,0 mean (n=7, 2022 only), Nogent 21,4, Paris 22,2, Toulouse 46,3 (n=6, bimodal: 2020 ~86 %, 2021 ~7 %). Lentil Nogent 28,3, Paris 32,4, Toulouse 39,5.

Descriptive observations:
- A lot of year×region variance: lentil Paris 2022 mean 50 % vs Nogent 2022 13,6 %. A "region-year mean" baseline probably captures much of it, and in leave-one-year-out validation the year is exactly what cannot be predicted.
- Total variance of % per row 523 vs mean within-field variance 100: ~80 % is between fields, consistent with the 69-70 % for "Field" reported in the paper.
- Distance: lentil damage declines slightly with distance (37,6 % at 5 m vs 33 % at 30 m), faba bean is flat. Matches the paper.
- Consistency with the paper: Chery-Lagrange et al. report medians of 13,3 % (IQR 8,0-29,0) for faba bean and 30,3 % (IQR 16,0-48,1) for lentil, very close to mine.

## 5. Leakage and decision date

Known **only after harvest** (never as input for early alerts):
- `Yield(g/m2)`, `Thousand-grainweight(g)`, `Farmers'syield`, all of Parasitism.tab.
- `Mature pod` climate (and partly `Young pod` if the decision is made at flowering).
- Watch out for a subtle leakage: the **climate windows are defined with observed crop stage dates** in the field. In real time those dates would have to be estimated (e.g. by growing degree-days from sowing) or calendar windows used.
- `Areaofcropthesameyear(%)` comes from the current year's RPG. It is known only after the PAC (CAP, Common Agricultural Policy) declarations (15 May), so it is usable in spring but not at sowing.

Available early (decision towards flowering, April-June):
- Crop/type (winter/spring), variety, production mode, sowing date and density, seed treatment, farm-saved seed, on-farm storage and a legume stockpile within <2 km (these two are biologically key: bruchids overwinter in stored grain).
- Landscape (host crop of the previous year = positive driver according to Herrera et al. IOBC 2026).
- Climate Vegetative + Flowering.
- Bruchid counts at Vegetative/Flowering (expensive: they require going into the field with a net).

## 6. Location information

- **No coordinates, commune or centroid** in any table. Only `Productionregion` (4 values). The data paper shows a map (Fig. 1) but does not publish coordinates; the PMS paper (Pest Management Science) says the data are available "upon reasonable request".
- Consequence: it cannot be joined with satellite data, your own RPG, or external daily climate data. It also cannot be validated spatially. A demo with a map would have to be by region.

## 7. Related papers and innovation gap

- **Herrera et al. 2026, Data in Brief**, doi 10.1016/j.dib.2026.112939 (https://pmc.ncbi.nlm.nih.gov/articles/PMC13264089/): describes the dataset. 105 fields (45 faba bean, 60 lentil), 4 regions, 3 seasons. Damage: 25 grains per distance, inspection of emergence holes or live bruchids. SAFRAN 8 km. 94 organic fields, the rest conventional **without insecticide**. It reports no models or results; it mentions "decision-support tools" as a potential use. Funding from InVivo (formerly Soufflet) + INRAE. There are internal inconsistencies (5 vs 4 distances; 25 grains vs quadrants).
- **Chery-Lagrange et al. 2026, Pest Manag Sci** 82(6):5780-5794, doi 10.1002/ps.70679 (https://pubmed.ncbi.nlm.nih.gov/41730720/, full text https://pmc.ncbi.nlm.nih.gov/articles/PMC13158440/): 59 lentil + 45 faba bean. GLMM/GLM and variance partitioning. Findings: fairly uniform distribution within the field (distance <1 % of variance; "Field" 69-70 %); female-damage correlation significant at Young pod but scattered (marginal R² 0,47 faba bean, 0,12 lentil; in faba bean ~9 females per +10 % of damage, in lentil ~59); colonization modelled with a Gompertz curve over degree-days (gd) (base 10 °C, biofix 1/1; peak ~267 gd faba bean, ~245 gd lentil; Malaise traps in 7 fields, one year, "preliminary"). It uses no numerical commercial thresholds and proposes no per-field risk tool.
- **Herrera et al. 2026, IOBC-WPRS Bulletin 182:97-101** (https://iobc-wprs.org/product/managing-populations-of-bruchid-pests-in-grain-legumes-role-of-resource-provisioning-at-field-and-landscape-levels/): 80 fields, 2 years. Bruchid density rises with the host area of the **previous year** and falls with the area of the current year (dilution); woodland raises it in lentil, hedgerows lower it in faba bean; nectar slightly raises bruchids and parasitism; **field practices have no effect**. Explanatory, with no prediction or R².
- The data paper cites a "Herrera et al. (under review)" on multiple drivers: its content is **not verified**; it is probably an explanatory analysis of climate + landscape + practices on damage. Risk: if it comes out before or during the hackathon, the "finding" on drivers would already be made.
- **Gap**: I found no predictive model, ranking, or out-of-sample evaluation (by year or region) published with these data, nor any ML for field-level Bruchus damage risk (searches: "Bruchus rufimanus risk model prediction machine learning", see the sources section). The Rothamsted/PGRO monitoring and forecasting system for the UK exists (https://repository.rothamsted.ac.uk/item/8qv12/a-novel-monitoring-and-forecasting-system-for-the-integrated-management-of-bean-seed-beetle-bruchus-rufimanus), but it targets treatment timing, not damage ranking. The innovation would be modest: an "honest first predictive benchmark" more than something new in the domain.

## 8. The real problem (desk research)

Most sources were read by a search subagent. Some primary sites (terresinovia.fr, hal.inrae.fr, the INAO (National Institute of Origin and Quality) extranet) blocked automatic download, and whatever could not be confirmed in a primary text is marked **[NOT VERIFIED]**.

### 8.1 Commercial thresholds (what buyers use)
- **Faba bean for Egypt / human consumption**:
  - 2002 export contracts: annex VII bis "human food" allowed a **max. of 1,5-3 % bruchés (bruchid-damaged) grains in faba bean** and 3 % in pea. Feed contracts (INCOGRAIN/RUFRA, annex VII) **have no specific bruchid limit**, only a max. of 10 % for broken grains + bruchés + hulls combined. Source: Perspectives Agricoles n°292 (2003), https://www.perspectives-agricoles.com/sites/default/files/imported_files/292_1420355064180393423.pdf
  - La Dépêche (1/3/2016): "Egypt demands 1 % bruchés grains" and France "can only guarantee 3 %", https://www.reussir.fr/ladepeche/la-feverole-francaise-en-difficulte-sur-legypte. It is trade press, not a contract. **[Current GASC/Egypt specification NOT VERIFIED]**
  - Bioceres (Belgium, 2024) gives 1 % for human food and 10 % for feed, without citing a source: https://www.bioceres.be/fiche/bio-agresseurs-des-legumineuses-graines
  - In short: the **10 %** for feed is not a specific bruchid limit, and for human food the reference figure is **1-3 %**.
- **Lentil for human consumption**:
  - IGP (protected geographical indication) Lentilles vertes du Berry, specification approved 17/11/2025: after sorting, "graines inacceptables" [unacceptable seeds] (bruchées, stained, moldy) **< 0,1 %**, https://info.agriculture.gouv.fr/boagri/document_administratif-40f9105a-26b0-47e0-9799-f0161c3a8df5/telechargement
  - AOP (protected designation of origin) Lentille verte du Puy: the specification (2018) has no explicit bruchid tolerance, but it requires sorting, https://info.agriculture.gouv.fr/boagri/document_administratif-3b601fa7-0c84-48e9-b94b-bffff44295fb/telechargement
  - Packer's product sheet (Sabarot, Puy, 2023): "impropres" [unfit] < 1 % and no insects, https://wyapkgisccvpsoiyfieb.supabase.co/storage/v1/object/public/mirror-documents/docs/ft/3111957400182.pdf
  - **The key point**: in lentil **the lot is sorted** until it reaches ~0,1-1 %. The raw bruchés % mainly determines the **sorting loss (15-50 %)**, and the reject goes to flour, feed or methanization (lentil sector diagnosis, filière lentille (lentil sector), Perspectives Agricoles 2022, https://www.perspectives-agricoles.com/economie/diagnostic-de-la-filiere-lentille-une-culture-davenir-mais-encore-fragile). The Dauguet & Gouyo article (Terres Inovia, Perspectives Agricoles n°545, 24/5/2026) says in its visible part that **"le tri au stockage est opérant"** [sorting in storage works] and that field solutions are lacking, https://www.perspectives-agricoles.com/conduite-de-cultures/graines-legumineuses-bruches-stockage. The rest is behind a paywall.
  - **Consequence for the idea**: with thresholds of 0,1-3 %, almost all 100 fields in the dataset (minimum 2,1 %) would fail. The useful variable is not "pass/fail" but **"how much is lost in sorting"**, which is continuous and well represented (2-94 %).

### 8.2 Volumes: human food vs feed
- **Faba bean**:
  - 2024: 83 400 ha and 224 kt (Terres Univia, Chiffres clés 2024, https://www.terresunivia.fr/fichiers/publications/chiffres-cles-2024.pdf).
  - 2025: 358 kt according to Terres Univia (https://www.terresunivia.fr/l-interprofession/actualites/qualite-des-graines-de-feverole-une-bonne-teneur-en-proteines-en-2025) and 301 kt according to La France Agricole of 22/4/2026. The figures do not match.
  - Destinations 2025/26 according to La France Agricole: 68 % feed and on-farm use in France, **4 % human food in France**, 19 % third countries (mainly Norway, aquaculture) and 9 % EU feed. Egypt appears as the "main outlet for human food before 2016, now closed by bruchids": https://www.lafranceagricole.fr/conjoncture-cultures/article/897342/quels-sont-les-debouches-de-la-feverole-francaise
  - History: Egypt bought 245 kt in 2010/11 and 87 kt in 2014/15 (https://www.reussir.fr/ladepeche/terres-inovia-le-salut-de-la-feverole-passe-par-les-os), and a broker spoke of 200-300 kt that fell to ~2 kt in 2020 (https://www.producer.com/markets/fababean-buyer-shuts-down/).
  - By crop, this is the clearest case of human-food market loss caused by bruchids.
- **Lentil**:
  - 34 200 ha in 2024. 2023/24 imports of 39,5 kt (25,4 kt from Canada) against 3,9 kt exported (Terres Univia, Chiffres clés 2024).
  - About 20 kt collected in 2020, with ~half of the area under organic (Perspectives Agricoles 2022).
  - It is almost all human food, and France imports more than it produces. The protein sovereignty angle fits well here.
- **Insecticides**:
  - In faba bean a single application of lambda-cyhalothrin at flowering is allowed, which Terres Inovia rates as "insuffisant" [insufficient]. In 2018 trials, untreated plots had 19-55 % bruchés grains, and 3 applications gave no gain: https://www.semae.fr/uploads/17-2019-03-13-GNIS-FNAMS-bruche-feverole.pdf
  - In lentil no insecticide is effective in the field (Perspectives Agricoles 2022).
  - I found no specific regulatory changes for 2023-2026. The extension of lambda-cyhalothrin to 2029 comes from a secondary source **[NOT VERIFIED]**.

### 8.3 Economic loss
- **I found no published estimate in €/ha or €/t**, nor an official % of lots downgraded.
- Available proxies:
  - Faba bean: Terres Inovia 2024 guide with indicative prices of **feed 230-290 €/t vs human food 260-320 €/t, a premium of ~30-40 €/t**: https://germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/FEVEROLE-2024-Guide-culture-TERRES-INOVIA.pdf. On ~200 kt of lost exports, that gives an order of magnitude of **6-8 M€/year of premium**. It is my own estimate, not published.
  - Organic lentil: 900-1300 €/t (CRIT Grand Est 2025 reference, https://draaf.grand-est.agriculture.gouv.fr/IMG/pdf/crit_16_avril_2025___annexe_2___referentiel_des_prix_crit_2025.pdf). Lentille du Puy at ~3350 €/t **[snippet only, NOT VERIFIED]**.
  - Own illustrative example: an organic lentil field of 1,5 t/ha with 30 % sorting loss loses ~0,45 t/ha at ~1000 €/t, and the reject is worth feed level (~250 €/t, inferred). That is **~340 €/ha** lost.
  - Lentil: 11,9 % bruchés grains on average over 111 plots 2018-2020 (Perspectives Agricoles 2021, https://www.perspectives-agricoles.com/conduite-de-cultures/lutte-contre-la-bruche-de-la-lentille). Our dataset (organic, no insecticide) is well above that: 34 % mean.
  - Faba bean 2025: "most lots < 1 % bruchés" (Terres Univia 2025, link above). **Conventional commercial faba beans seem much less damaged than those in the dataset.** This is a representativeness warning.

### 8.4 Existing tools
- **Terres Inovia / BSV (Bulletin de santé du végétal, plant health bulletin)**:
  - Risk rule from the 2 cm pod stage until the end of flowering + 10 days: intervene if **Tmax ≥ 20 °C for ≥2 consecutive days** (Terres Inovia 2024 guide, link above).
  - Regional BSVs apply the same rule, for example the Centre-Val de Loire BSV of 13/5/2025: https://draaf.centre-val-de-loire.agriculture.gouv.fr/IMG/pdf/bsv_proteagineux_n10-13052025.pdf. The BSVs themselves state that they give a regional trend that cannot be transferred to the plot.
- **United Kingdom**: BruchidCAST (Syngenta + PGRO, 2009) gives a 5-day alert with the same 20 °C × 2 days rule: https://www.fwi.co.uk/arable/bruchid-beetle-alerts-to-help-time-sprays. Rothamsted published a monitoring and forecasting system, of which I only saw the repository record: https://repository.rothamsted.ac.uk/item/8qv12/a-novel-monitoring-and-forecasting-system-for-the-integrated-management-of-bean-seed-beetle-bruchus-rufimanus
- **Olfactory traps**:
  - FabaOdor (De Sangosse/AgriOdor): 20 traps/ha, ~115 €/pack, with a -50 % damage reduction claimed by the manufacturer: https://www.reussir.fr/grandes-cultures/feverole-des-leurres-olfactifs-pour-detourner-les-bruches-de-la-culture
  - Lentodor (lentil), tested in the KAIROL project: inconclusive result.
- **Post-harvest**: phosphine, deltamethrin (K-Obiol), heat at 50-70 °C, cold and CO2 (Terres Inovia 2024 guide; https://cuma.fr/intercropvalues-pa4-eliminer-les-bruches-des-lentilles).
- **I found no plot-level damage prediction tool** (neither an OAD (aide à la décision, decision-support tool) nor a "Bruchus" model). Everything that exists points to **treatment timing** at regional scale.

### 8.5 Who would pay
- **KAIROL (2022-23)** on the lentil bruche (bruchid): Axéréal, Soufflet Agriculture, CORAB, Qualisol and Val de Gascogne, with Terres Inovia, De Sangosse and AgriOdor, funded by FASO/Sofiprotéol (https://www.terresunivia.fr/l-interprofession/actualites/bruche-de-la-lentille-le-projet-kairol-evalue-une-nouvelle-solution-de-lutte). **Grain collectors are already putting money into this problem.**
- The dataset itself was funded by Soufflet (now InVivo). It is the natural client/partner, and also the one with the most data.
- Other candidates: the Berry IGP group (Axéréal and the Lentilles vertes du Berry association), the Puy packers (Sabarot) and the organic cooperatives (CORAB, Biocer).
- **I found no statements from Terrena, Vivescia, Cavac, Arterris or Sud Céréales** on bruchids.
- Plan protéines (French national protein plan): 100 M€ (2021-22), https://agriculture.gouv.fr/telecharger/122866. I found no bruchid-specific projects.

## 9. Errors or omissions in the previous brief

The brief's numbers are all **correct** (I checked them one by one). The problems are in what it omits or frames wrongly:
1. **It does not say the damage is extremely high** (median 13,7 % / 33,4 %), nor that **no field meets the human-food thresholds** of 1-2 %. Its proposal of "recall of high-damage fields with the buyer's threshold" is degenerate: with a 3 % threshold, 97 of 100 fields are "high damage".
2. **It does not mention that 91 % of the fields are organic and that none received insecticide.** The dataset represents organic lentil fairly well and commercial export faba bean (conventional, most lots < 1 % in 2025) quite poorly.
3. **It does not mention that the label comes from 25 grains per sampling point** (≤100 per field in 65 % of fields). There is binomial noise of ±4-5 pp, which caps any metric.
4. **Wrong user chosen**: "cooperative technician who prioritizes inspections". At intake, inspecting a lot (counting holes in a sample) is cheap and gets done anyway; besides, sorting works. Prioritizing inspections saves almost nothing. The value is **before** harvest: planning sorting capacity and post-harvest treatment, assigning lots to each outlet, forecasting sellable tonnes for human food, and deciding rotation or sowing for the following year.
5. It does not detect the unit error in `Farmers'syield(kg/ha)` (these are q/ha), the unusable fertilizer, that `Bruchids.tab` changed method in 2020 (suction) and 2021-22 (net), or that the climate windows use observed stage dates (subtle leakage).
6. It says "no external weather join needed", which is true, but without coordinates an external join is **also not possible**. The brief mentions this only in passing.
7. It overlooks that region and year are confounded (Dijon only in 2022, faba bean only). Validating leave-one-year-out with 3 years is very unstable.

## 10. Verdicts

- **Feasibility in 20 h: 5/10.**
  - In favor: small, clean data with perfect joins (98 complete fields), an open license, and a paper that gives the scientific baseline.
  - Against:
    - n ≈ 100 with 3 years and 4 regions.
    - Noisy label.
    - No coordinates.
    - A region×year baseline is probably hard to beat, and in a real operational setting the current year is exactly what is unknown.
    - The obvious commercial framing (threshold) does not work with these data.
  - Executing is easy; having a convincing and honest impact story is hard.
- **Is AI essential?** Weak. With ~100 rows and ~10 features, a regularized GLM or a rule-based ranking (host of the previous year, flowering climate, on-farm seed storage) is what fits, and the jury may ask "why AI?". The defensible part would be **quantifying uncertainty** (per-field intervals) and **simulating decisions** (how much sorting or treatment capacity to reserve). An LLM adds nothing essential.
- **Innovation: medium-low.** No published predictive model exists with these data (a real gap), but the drivers are already described (IOBC 2026) and there is a drivers paper "under review" by the same authors. What would be new is the **honest out-of-sample benchmark** and the **translation into €** (sorting loss).
- **Impact story**:
  - France imports ~40 kt of lentil (mostly from Canada) and lost ~200 kt/year of faba bean for human consumption in Egypt due to bruchids.
  - There is no effective chemical control, so management relies on landscape, rotation and post-harvest logistics.
  - A tool that estimates **what fraction of each lot will remain for human food** lets cooperatives hire and plan sorting better, and reward landscape practices that lower risk.
  - It is a reasonable story, but the link to "more pulses for human consumption" is indirect.
- **Business model**: SaaS or a service for grain collectors (Axéréal, InVivo/Soufflet, CORAB, Qualisol, Val de Gascogne) and IGP/AOP bodies, charged per tonne collected or per season. It could also fit as a module of a Terres Inovia OAD (funded by FASO or the Plan protéines). Willingness to pay is plausible (they already fund KAIROL) but **not verified**. The real competitor is "sort everything and be done".
- **Main risks**:
  1. The model does not beat the region×year baseline in year-based validation (likely).
  2. Representativeness: organic without insecticide vs conventional faba bean.
  3. Label noise.
  4. An agronomist on the jury may point out that sorting already solves the problem.
  5. The "Herrera et al. under review" paper may publish the same drivers.
  6. Without coordinates, the map demo is not real.

### Concrete MVP and demo (if chosen)
- **Question**: "At flowering, what fraction of this field's harvest will be lost to bruchid sorting, and with what uncertainty?"
- **Inputs, as of flowering**:
  - Crop and type
  - Variety (grouped)
  - Host of the previous year and of the current year at 1000 m
  - Woodland and hedgerows
  - Climate Vegetative + Flowering
  - On-farm seed storage and legume stockpile within <2 km
  - Sowing date
  - No insect counts in the base version; Flowering counts as a "with monitoring" variant.
- **Models**: crop×region-year baseline (or crop only), beta-binomial or logistic GLM on counts, and a shallow tree. Leave-one-year-out and leave-one-region-out validation, reported by crop. Metrics: MAE in pp, Spearman of the ranking and interval coverage.
- **Demo**:
  - One screen for a "fictitious cooperative" with the fields of a year the model never saw.
  - Ranking with bars of expected loss in € (tonnage × % sorting × price difference, with explicit assumptions).
  - A slider for "post-harvest treatment or fine sorting capacity" showing how many € are protected by prioritizing with the model versus doing it at random or with the baseline.
  - A panel "what changes the risk": host of the previous year and woodland, with an agronomic reading and no causal claims.
- **Demo data**: region only, no invented map.

### Cut-off rule
- **Hour 4**: if the early features, in leave-one-year-out, do not lower MAE by ≥15 % versus the crop baseline **or** the within year-crop Spearman ranking is not > 0,3 in at least 2 of 3 years, the "predictive AI" angle is dropped and the idea is changed or reframed as a "sorting loss calculator + landscape rules" (honest, but it loses the 20 % "AI essential" score).
- **Hour 8**: if the model with early features does not consistently beat the baseline in both crops, the pitch has to say exactly that. If there is nothing more than that, it is better to go back to another idea.

## Main sources (summary)
- Dataset: https://doi.org/10.57745/HPEMYW (API: https://entrepot.recherche.data.gouv.fr/api/datasets/:persistentId/?persistentId=doi:10.57745/HPEMYW)
- Data paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC13264089/
- Chery-Lagrange et al. 2026: https://pubmed.ncbi.nlm.nih.gov/41730720/, https://pmc.ncbi.nlm.nih.gov/articles/PMC13158440/, https://hal.inrae.fr/hal-05526495v1
- Herrera et al. IOBC 2026: https://iobc-wprs.org/product/managing-populations-of-bruchid-pests-in-grain-legumes-role-of-resource-provisioning-at-field-and-landscape-levels/
- All other links appear inline in each section.
