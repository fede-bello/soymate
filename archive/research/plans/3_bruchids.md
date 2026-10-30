# Dossier Idea 3: bruchid damage risk in lentil (and organic faba bean), in € per field

Date: 30/10/2026 (morning of the opening day). This dossier was built only with desk research and descriptive data exploration: no model was fitted, there is no cross-validation and no predictive results. Scripts used (disposable, not solution code): `audit.py` (descriptive statistics of the INRAE dataset) and `rpg_landscape.py` (test of access to the RPG WFS), in the scratchpad `plan_i1/scripts/`. Downloaded data was deleted at the end.

Tags: **[V]** verified by me in the file, the API or the primary source today; **[F]** read in a source I opened but not cross-checked against primary data; **[NV]** not verified; **[E]** own estimate (explicit calculation, not published); **[A]** assumption.

---

## 1. Summary in 5 lines + verdict

1. Real and current problem: the bruchid (*Bruchus signaticornis*) is "la bête noire de la lentille" (Terres Inovia 2023 guide, which also says the fight "doit être collective"). In 2025 the national harvest had **24.4% bruchid-damaged grains on average** (bruchés), the record since the surveys started in 2021 (Centre-Ouest: 36.8%) [V]. Since 31/7/2024 no authorised insecticide remains for lentil [V].
2. User: the head of the lentil supply chain (filière lentille) of a grain collector cooperative (profile Axéréal, InVivo/Soufflet, CAVAC, Qualisol, CORAB). They make two decisions: in June, how much food-grade tonnage to commit and how to allocate sorting and fumigation by lot; and in winter, where to advise sowing next year's lentil.
3. Product: at flowering, an expected sorting loss **per field, with an interval and in €**, plus a landscape risk map that can be recomputed for **any parcel in France** from the RPG. I verified that the dataset's landscape variables can be recomputed via WFS in 1 to 5 s per parcel [V].
4. Data: the INRAE dataset (doi 10.57745/HPEMYW, etalab 2.0) has 100 labelled fields (57 lentils, 43 faba beans), SAFRAN climate and RPG landscape [V]. For inference the climate comes from Météo-France's SIM2, open and updated daily [V]. The n is small and the variance is highly concentrated in region×year (descriptive η² 0.59 for lentil and 0.68 for faba bean) [V].
5. Main risk: that under leave-one-year-out the model does not beat the region×crop baseline. That is only known on Saturday at midday. There is a second framing risk: "Insects" is on the list of excluded topics (it refers to insects as food, but this must be confirmed on Friday).

**Verdict: conditional GO, focus on lentil.** It is the idea with the most concrete and best-documented problem in Track 3, and the user and the buyer have names. But the AI component is fragile (n = 100) and the expected score is average: **6.0/10 weighted** (section 12). It is worth choosing only if the team accepts a hard go/no-go on Saturday at 13:00 and has the section 7 fallback ready.

---

## 2. Problem, user and decision

### The problem (with figures)
- The larva develops inside the grain and the adult emerges after harvest. The damage "est invisible pendant le cycle", it is only noticed at sorting, and in severe cases the lot is downgraded to feed because the requirements for human food "sont très strictes" (Le Bihan et al. 2025, Innovations Agronomiques 99:165-176, HAL hal-04926988) [V].
- Terres Inovia national quality survey (X-ray of lots at reception), mean bruchid-damaged grains per year: **11.6% (2021), 15.3% (2022), 10.3% (2023), 14.5% (2024), 24.4% (2025)** [V]. The values come from the text extracted from the chart in the 2025 sheet. I deduced the order of the series because the 2025 value matches the 24.4% in the text and in the table. In 2025, 40 samples were measured: min 1.0%, max 75.5%, standard deviation 18.7. By basin: Centre-Ouest 36.8, Sud-Ouest 22.3, Nord-Est 18.6, Sud-Est 15.4 [V].
- In 2022 Centre-Ouest averaged 35.5% (range 21.5-51%), while Nord-Est, AURA and Nord-Ouest stayed below 6% (Le Bihan et al. 2025) [V]. Some lots reached 80% (KAIROL 2022, cited there) [V].
- Sorting losses ("freintes") of **15 to 50%**. What is discarded goes to flour, livestock or methanisation (Perspectives Agricoles n°500, 1/6/2022) [V].
- There is no field control: the only authorised insecticide against the lentil bruchid (CYTHRINE MAX, cypermethrin) could no longer be used from 31/7/2024 and was also not very effective. The tested biocontrols did not work, and the Lentodor traps (KAIROL) showed no significant effect (Le Bihan et al. 2025) [V]. Management happens in storage (phosphine, CO2, vacuum, cold) plus sorting [V].
- There is no agreed counting method. Collectors use different methods, but "des grilles de réfaction existent" (price deduction grids) based on the % of bruchés, and processors can buy lots without insects in Canada (Le Bihan et al. 2025) [V]. France imported **39.5 kt of lentil in 2023/24 (25.4 kt from Canada) and exported 3.9 kt**, with 34,200 ha sown in 2024 (Terres Univia, Chiffres clés 2024) [V].

### Concrete user
**Head of the lentil supply chain (or grain collection and pulse quality manager, responsable de collecte et qualité de légumes secs) of a grain collector cooperative** that buys lentil from dozens or hundreds of producers, sorts it and sells it to packers. For lentil with IGP Berry, sorting is done at a sorting centre within the area, and non-compliant lots "sont retriés ou déclassés" [V]. Typical organisations: Axéréal, InVivo (ex Soufflet, which funded the INRAE dataset), CAVAC, Qualisol (the first three and Qualisol appear in the acknowledgements of Le Bihan et al. 2025 [V]), CORAB and Val de Gascogne (KAIROL partners [V]).

Secondary user: the cooperative technician who advises members on where to sow lentil.

### Decisions
| Decision | When | Information used today | Cost of getting it wrong |
|---|---|---|---|
| D1. How much food-grade tonnage ("apto consumo humano") to commit in contracts with packers, and which lots to send to separate cells for fumigation and fine sorting | Flowering to young pod (June) until reception (July-August) | The regional BSV rule (heat), the collector's history, intuition. The real % only arrives with the reception analysis | If overestimated, there is not enough product to meet the contract (buy imported or pay penalties) [A]. If underestimated, sell spot more cheaply [A]. Mixing heavily bruchid lots with clean lots contaminates silos and forces re-sorting [F: Le Bihan, IGP Berry] |
| D2. Where to advise sowing lentil next year (stay away from areas with a lot of lentil the year before) | Sowing planning (Dec-Feb) | Nothing systematic. Terres Inovia calls for a "collective" fight [V] | A campaign in a hot area can reach 30-50% sorting losses [V range] |

The exact cost of each error is not published; see questions for mentors (section 11).

---

## 3. Hypotheses

| # | Hypothesis | Status | Evidence | If false |
|---|---|---|---|---|
| H1 | The dataset has 100 fields with valid labels (57 L, 43 H) and clean joins | [V] | 397 valid rows; the intersection label ∩ climate ∩ landscape ∩ practices gives 98 fields; with bruchid counts, 83 | n/a |
| H2 | The label noise (25 grains per point) does not dominate | [V] (corrects the prior research) | Grains per field: min 75, median 100. The mean binomial standard error per field is 3.2 pp, but binomial variance is only **2.1% (faba bean) and 3.8% (lentil)** of the variance between fields | Weight by n with an equivalent binomial model |
| H3 | Damage varies mainly between fields, not within a field | [V] | Chery-Lagrange et al. 2026: "Field identity" explains 69% (faba bean) and 70% (lentil), distance <1% | Already assumed: the product is per field |
| H4 | A large share of the variance between fields is region×year | [V] descriptive | η² region×year 0.585 (L) and 0.675 (H); η² year alone 0.18 (L) and 0.20 (H) | If the model does not capture region-year with climate, the baseline wins. This is the main risk |
| H5 | Early variables (landscape of the previous year, vegetative + flowering climate) predict out-of-year damage better than the baseline | **[NV]** (cannot be tested before the event) | IOBC 2026: bruchid density rises with the previous year's host area, across 80 fields and 2 years. Note: the result is about **density, not damage** [V]. Chery-Lagrange: female-to-damage relationship "highly dispersed" [V] | Section 7 fallback: € calculator + landscape map with regional prior, reduced AI that only quantifies uncertainty |
| H6 | Landscape variables can be recalculated for any parcel from the RPG | [V] | See 4.2: Geoplateforme WFS, codes LEC / FVL / FVP / FEV stable 2019-2025, calculation in 1-5 s per parcel and year | n/a |
| H7 | My recalculation reproduces the authors' definition | [F]/[NV] | Data paper: "% of land grown with the same crop as the focal field (lentil or faba bean)", buffers of 500/1000/2000 m around the centroid, RPG 2019-2022 [V text]. The dataset values (same year, 500 m: median 1.7%, max 6.9%, 10 zeros) are incompatible with including the focal field (8 ha in 78.5 ha would give ≥10%). With the focal field **excluded** my values are in the same range (0-4%) [V] | Calibrate against the dataset distribution and write to A. Gardarin. Use only "previous year", where exclusion changes nothing |
| H8 | Inference climate can be computed the same way as in the dataset | [V] partial | SIM2 (the same 8 km SAFRAN reanalysis), daily file `QUOT_SIM2_latest.csv.gz` updated 30/10/2026 with data to 29/10, columns T, PRELIQ, FF [V]. But the dataset defined the windows with **observed stage dates** [V paper] | In inference, estimate the stages by growing degree-days from sowing and declare it as a source of error |
| H9 | The dataset conditions (91% organic, no insecticide) represent current French lentil | [V] mostly | Lentil has had no insecticide since 31/7/2024 [V]. 45% of lentil area is organic (Le Bihan) [V]; 13,060 ha organic in 2023 (Terres Univia) [V] | For conventional faba bean it is NOT representative: there one application at flowering is allowed [V] and most 2025 lots have <1% [V]. Limit the claim about faba bean to organic faba bean |
| H10 | The dataset regions cover production | [V] partial | Aube (Nogent-sur-Seine) is the **first lentil département** (3,838 ha in 2024), and Yonne, Marne and Côte-d'Or are also high [V RPG]. **There is no Berry (Indre) or Puy (Haute-Loire)**, where the IGP/AOP production is | Show the map over Aube. Mark Berry and Puy as extrapolation |
| H11 | Mass sorting loss ≈ % bruchid-damaged grains × factor r ≤ 1 | [A] | In lentil the larva "consume almost the entire grain", and in faba bean the dry weight loss is 5-10% per grain (Chery-Lagrange 2026) [V]. Published sorting losses: 15-50% [V] | Show an r slider (0.6-1.0) and ask a mentor or collector for the figure |
| H12 | Food lentil price ≈ €806-873/t (conventional) | [V] | FranceAgriMer, full campaign price Q4: 854 (23/24), 873 (24/25), 806 (25/26). Includes "réfactions et bonifications" (deductions and bonuses) | n/a |
| H13 | Value of the discard ≈ animal feed price (proxy: faba bean €231/t in 25/26) | [A] | No quote found for downgraded lentil (negative search). FranceAgriMer faba bean 25/26: €231/t [V]. Terres Inovia 2024 guide for faba bean: feed €230-290/t vs human €260-320/t [V] | Slider |
| H14 | Thresholds: IGP Berry <0.1% "graines inacceptables" (including bruchid-damaged) after sorting | [V] | Specification approved on 17/11/2025 | n/a |
| H15 | Egypt requires 1% bruchid-damaged in faba bean and France guarantees 3% | [F] old | La Dépêche, 1/3/2016 (trade press, not a contract) [V what the article says]. **I found no GASC specification** (in fact GASC tenders wheat; Egyptian faba bean imports are private) [NV] | Do not use "GASC" in the pitch. Say "trade press 2016: 1% required" |
| H16 | The cooperative pays for this | [NV] | Indirect signal: collectors financed and took part in KAIROL (FASO/Sofiprotéol) [V] and InVivo funded the dataset [V] | Pivot the client to Terres Inovia (OAD funded by FASO or Cap Protéines) |
| H17 | No field-level damage prediction tool exists (France or UK) | [V] negative searches | BruchidCAST (Syngenta + PGRO, 2009) gives a spray alert 5 days ahead with the rule of >20 °C for 2 days [V], but does not predict damage. BSV: regional temperature rule [V]. I found no bruchid OAD at Terres Inovia (negative search) | If one appears, differentiate by € + landscape + parcel |
| H18 | The "drivers" paper by Herrera et al. (under review) did not come out | [V] as of 30/10/2026 | No results in HAL (search "Bruchus" 2025-2026) or Crossref (author Herrera Gardarin). Exact title in the data paper: "Multiple spatiotemporal drivers consistently shape bruchid pest abundance, damage and parasitism in grain legumes" | If it comes out, cite it as validation of the explanatory analysis. Ours is out-of-sample prediction + € + tool |
| H19 | The project does not fall into the excluded topics | [NV] | "Insects" is excluded (understood as insects-as-food) and "Animal feed" too. Our goal is to **keep lentil in human food** | Ask a mentor on Friday before 23:00 |

---

## 4. Datasets

### 4.1 Core: INRAE "bruchid beetle populations, grain damage and parasitism" (doi 10.57745/HPEMYW)
- **URL / API:** `https://entrepot.recherche.data.gouv.fr/api/datasets/:persistentId/?persistentId=doi:10.57745/HPEMYW` [V]. Version 2.0, published 2026-09-01T13:24:08Z, **etalab 2.0 licence** [V]. The README only refers to the data paper (Herrera et al. 2026, Data in Brief, doi 10.1016/j.dib.2026.112939, PMC13264089) and the missing-value code is `NA` [V].
- **Access:** tested, no login, 9 files [V]:

| id | file | rows | fields | key missing values |
|---|---|---|---|---|
| 722704 | Yield_and_seed_damage.tab | 481 | 103 | damaged 84 NA, no-damaged 83 NA, Yield 128, TGW 178, density 197 |
| 722703 | Agricultural_practice_characterization.tab | 105 | 105 (`Parcelle`) | sowing 21, seed origin 21, on-farm storage 23, stockpile <2 km 23, ploughing 53 |
| 722708 | Landscape.tab | 315 | 105 × buffers 500/1000/2000 | 0 |
| 722709 | Meteorological_data.tab | 420 | 105 × 4 stages | 8 (2 fields: ID057, ID063) |
| 722705 | Bruchids.tab | 3870 | 86 | distance 9 |
| 722702 | Parasitism.tab | 449 | 101 | post-harvest (leakage) |
| 722706 | Flower_cover.tab | 660 | 83 | distance 10 |
| 722707 | Extrafloral_Nectar.tab | 74 | 38 (faba bean only) | 17 |
| 769369 | READ_ME.txt | | | |

- **Columns and units** [V]: damage = `Numberofbruchid-damagedgrains`, `Numberofnobruchid-damagedgrains`. According to the data paper it is the "sum for three 0.25 m² plots", but the methods say "random sample of 25 grains per distance": an internal inconsistency in the paper [V]. In the data, 65% of rows have exactly 25 grains [V].
  - Landscape: `Areaofcropthepreviousyear(%)`, `Areaofcropthesameyear(%)`, `Woodyhabitats(%)`, `Grassland(%)`, `Areaoforganicagriculture(%)`, `Totallinearmetersofhedgerows` (m).
  - Climate by stage (Vegetative, Flowering, Young pod, Mature pod): days with mean T >12 °C, days with 20-25 °C, accumulated / mean / maximum rain (mm), daily maximum wind (m/s).
- **Counts and target distribution (pooled by field)** [V]:

| Crop | n | mean | median | min | p25 | p75 | max | ≤3% | ≤10% | ≥20% |
|---|---|---|---|---|---|---|---|---|---|---|
| Faba bean | 43 (36 winter, 7 spring) | 22.9 | 13.7 | 2.1 | 7.2 | 32.5 | 94.0 | 3 | 15 | 17 |
| Lentil | 57 | 34.2 | 33.4 | 4.3 | 18.0 | 49.0 | 74.0 | 0 | 5 | 40 |

  By region-year, in lentil it ranges from 13.6% (Nogent 2022) to 50.2% (Paris 2022). In faba bean, Toulouse 2020 gives 85.7% (n=3) and Toulouse 2021 7.0% (n=3) [V].
- **Landscape range** [V]: previous year at 1000 m, median 0.19%, max 3.8%, 41/105 zeros; at 2000 m, median 0.57%, max 3.2%. The correlation between previous-year buffers is 0.71 (500-1000) and 0.35 (500-2000). `Grassland(%)` has a median of 0.5-1.8%, suspiciously low: the scale must be checked with the authors or the paper [V the value, NV the interpretation].
- **Gotchas** [V]:
  - Each field appears in one year only. Dijon exists only in 2022 and only with faba bean; Toulouse 2022 only with lentil.
  - In 2022 there are repeated climate vectors (Dijon 2022: 3 distinct vectors for 7 fields, because of shared SAFRAN cells).
  - The bruchid capture method changed from aspiration (2020) to net (2021-22) [V paper].
  - `Farmers'syield(kg/ha)` is actually in q/ha (values 2.3-58).
  - `Quantityoffertilizer` mixes kg of compost and kg of N.
  - `Sowingdate` is an Excel serial.
  - `Sowingdensity` is a string.
  - Varieties with typos; Anicia 35/57 in lentil.
  - Buffers overlap between neighbouring fields ("non-independence", according to the paper) [V].
  - **There are no coordinates** [V].
- **Download on Friday (30 s):**
```bash
mkdir -p data/raw/inrae && cd data/raw/inrae
for id in 722703 722704 722705 722706 722707 722708 722709 722702 769369; do
  curl -sL "https://entrepot.recherche.data.gouv.fr/api/access/datafile/$id" -o "f_$id.tab"; done
# 722703 practices, 722704 damage, 722705 bruchids, 722706 flower, 722707 nectar,
# 722708 landscape, 722709 meteo, 722702 parasitism, 769369 README
```

### 4.2 RPG (Registre Parcellaire Graphique, graphic parcel register) via Geoplateforme WFS
- **URL:** `https://data.geopf.fr/wfs/ows`, no key [V]. Layers: `RPG.2015..2024:parcelles_graphiques`, `RPG.LATEST:parcelles_graphiques` (= **RPG 2025**, the title confirms it), `RPG.20xx:codes_cultures`, `IGNF_RPG_PARCELLES-BIO_2025:parcelles_bio` [V]. Licence: Licence Ouverte (IGN) [F].
- **Codes** (from `RPG.2024:codes_cultures`) [V]: `LEC` "Lentille cultivée (non fourragère)"; `FVL` "Féverole semée avant le 31/05"; `FVP` "Féverole de printemps"; `FEV` "Fève". Field names vary by year [V]:
  - 2019-2024: `code_cultu`, `surf_parc`, `id_parcel` (anonymised, changes every year).
  - 2025: also `num_parcel`, `num_ilot`, `bio` (boolean), `pp`, `iae`.
  - Geometry: `geom`, except **2022, which uses `the_geom`**.
- **Tested syntax** [V]: `CQL_FILTER=code_cultu='LEC' AND BBOX(geom,lat_min,lon_min,lat_max,lon_max)` (order **lat, lon**; with lon, lat it returns 0). To pull a whole rectangle, use `BBOX=lat_min,lon_min,lat_max,lon_max,urn:ogc:def:crs:EPSG::4326` and `SRSNAME=EPSG:2154` to get metres.
- **Recalculation of "% same crop" in buffers around the centroid** (one focal parcel per area, the largest of the crop) [V]:

| Area (focal year) | Focal parcel | Previous year (500/1000/2000 m) | Same year without the focal field (500/1000/2000) | Time |
|---|---|---|---|---|
| Berry, Indre (lentil 2024) | 38.8 ha, 47.001 N 1.879 E | 0.44 / 8.17 / 3.74% | 0 / 0.64 / 0.55% | ~5 s |
| Aube (lentil 2021) | 20.0 ha | 17.98 / 5.74 / 2.47% | 0 / 0 / 0.21% | <5 s |
| Aube (faba bean 2021) | 10.0 ha (FVL) | 0 / 0.15 / 0.30% | 0 / 0.01 / 0.26% | <5 s |
| Côte-d'Or (faba bean 2022) | 15.2 ha | 0 / 0.45 / 0.67% | 0 / 0 / 0% | <5 s |
| Haute-Garonne (lentil 2022) | 12.5 ha | 0 / 0.37 / 0.18% | 4.11 / 1.03 / 0.26% | <5 s |
| Haute-Loire, Puy (lentil 2025) | 16.6 ha | 0 / 2.25 / 3.71% | 2.79 / 3.07 / 4.46% | ~5 s |

  Conclusions: (a) **it can be recalculated for arbitrary parcels** [V]. (b) The dataset's "same year" is only compatible with excluding the focal field [V, by range]. (c) There are values **outside the training range** (Aube 18% at 500 m, Berry 8.2% at 1000 m, against a maximum of 4.7% and 3.8% in the dataset), so the map has to mark the extrapolation [V].
- **Calendar gotcha:** the RPG for year N is published around September of N+1 (today, 30/10/2026, the most recent is 2025 [V]; the exact publication date is [F] from the prior research). So for the 2027 season, the "previous year" (2026) **is not public in time**. Solution: the cooperative knows its own contracted areas in 2026 (its members), and the rest is completed with RPG N-2 as a proxy [A]. This must be said in the pitch.
- **Other WFS layers for the landscape** [V hits in a test bbox]: `BDTOPO_V3:zone_de_vegetation` (forests), `BDTOPO_V3:haie` and `HAIES.BOCAGES:haie` (hedgerows), `IGNF_RPG_PARCELLES-BIO_2025:parcelles_bio`.
- **Download on Friday:** no need to download all of France. A script of a few lines (requests + shapely + pyproj), cached as parquet by bbox.

### 4.3 Inference climate: SIM2 / SAFRAN (Météo-France, data.gouv)
- Dataset "Données changement climatique - SIM quotidienne", licence **lov2** [V]. `https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/QUOT_SIM2_latest.csv.gz` weighs 19.9 MB, Last-Modified 30/10/2026, last day 20261029 [V]. The annual files (`QUOT_SIM2_2020.csv.gz`, etc.) are in the same folder [V].
- Columns [V]: `LAMBX;LAMBY;DATE;PRENEI;PRELIQ;T;FF;Q;DLI;SSI;HU;EVAP;ETP;PE;SWI;...`. Coordinates in hectometres Lambert II étendu (8 km grid), with a separate grid coordinates file [F prior research]. With T, PRELIQ and FF the 6 climate variables of the dataset are reproduced.
- Faster alternative for the demo: Open-Meteo `archive-api` with `models=era5`, no key. I tested it with 48.37 N 3.64 E in May 2026 [V]. Note: with `era5_land` rain comes out empty [F prior research].
- Download:
```bash
curl -sLO https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/QUOT_SIM2_latest.csv.gz
```

### 4.4 Prices: FranceAgriMer, prices paid to producers (quarterly)
- File: `https://visionet.franceagrimer.fr/Pages/OpenDocument.aspx?fileurl=SeriesChronologiques%2fproductions%20vegetales%2fgrandes%20cultures%2fprix%20pay%c3%a9s%20aux%20producteurs%2fSCR-CER-HISTOPRIXTRIMESTRIELS-C25-26.xlsx&telechargersanscomptage=oui` [V]. Sheet "Publication nationale", header in row 11 (header=10). Data to 30/6/2026. It is conventional and the price is "complet" (includes réfactions). The credit line "Source : FranceAgriMer (tous droits réservés)" must be used [V].
- Lentil Q4: **854 / 873 / 806 €/t** (23/24, 24/25, 25/26). Faba bean Q4: 257 / 273 / **231** €/t. Pea 247 / 275 / 222 [V].

### 4.5 Document references (not tabular, for the € assumptions)
- Lentil quality sheet 2025, Terres Inovia (`https://www.terresinovia.fr/sites/default/files/2026-02/fiche-qualite-graines-lentille_2025.pdf`). **Blocks bots** (403 with curl and WebFetch). I read it from Chrome with pdf.js [V]. It contains 60 samples (the % bruchid-damaged was measured on 40), the figures by basin and the 2021-2025 series.
- Le Bihan et al. 2025 (HAL hal-04926988, CC BY). HAL has anti-bot protection (Anubis) and I read it from Chrome [V]. **Note**: Chrome auto-translated the text into English, so for literal quotes go back to the original French PDF.
- Specification IGP Lentilles vertes du Berry (17/11/2025) and AOP Lentille verte du Puy (2018), at info.agriculture.gouv.fr (direct download with curl) [V].
- Terres Inovia guides: faba bean 2024 and lentil 2023, on the germineo.com mirror (direct curl) [V].
- Terres Univia Chiffres clés 2024 (direct curl) [V].

### 4.6 Prior derived table
- `archive/research/datasets/rpg_pulses_dept_year.csv`: made before the event, to be declared. National lentil 17,179 ha (2015), 37,529 (2019, peak), 28,670 (2023), 34,220 (2024). Faba bean 83,081 ha (2024). Top lentil départements 2024: Aube 3,838, Haute-Loire 2,680, Marne 2,596, Yonne 2,495, Indre 1,839 [V recalculated today from the CSV].

### 4.7 Tested joins
- INRAE internal: `Field` = `Parcelle` (ID001..ID105), with no discrepancies in year, region or crop between tables [F prior + V count 98/83].
- INRAE ↔ RPG / SIM2: **cannot be joined** (no coordinates). RPG and SIM2 are used only for **inference** on new parcels, with the same variable definitions. It is a transferability assumption that has to be declared.
- RPG ↔ SIM2: by coordinate (centroid in Lambert 93 → Lambert II étendu → 8 km cell). Must be implemented on Friday [NV the exact conversion].

---

## 5. AI method

**Unit:** field. **Target:** k bruchid-damaged grains out of n examined (pooled by field). Modelled as binomial with overdispersion (beta-binomial), not as a loose %.

**Decision dates and allowed features:**

| Date | Use | Features | Forbidden (leakage) |
|---|---|---|---|
| D0, planning (before sowing) | Landscape map (D2 of section 2) | Crop/cycle, region, % host of previous year (500/1000/2000 m), forest %, hedgerows m, % organic | Everything from the current year: climate, same year, counts |
| D1, flowering (BBCH 65) | Ranking in € (D1 of section 2) | D0 + Vegetative + Flowering climate + sowing date (day of year) + on-farm seed storage + stockpile at <2 km (these two have 23 NA) + same year without the focal field (optional, depends on the RPG or the collector's data) | Young pod / Mature pod climate, Yield, TGW, Farmers' yield, Parasitism, Flower_cover from later stages |
| D1+, "with monitoring" variant | Comparison | D1 + females captured in Vegetative/Flowering (83 fields; the method changed in 2020, so an indicator per year must be used) | Young pod counts |

Subtle leakage, to declare:
1. Climate windows use observed stage dates. In inference they are estimated by degree-days, so the real error will be larger than in validation.
2. Buffers overlap between neighbouring fields of the same year. That is why validation is done by region-year group.
3. The current year's RPG does not exist in time (4.2).

**Baselines** (all with the same validation):
- B0: crop mean.
- B1: crop × region mean from the training years. If the region is not in the train set (for example Dijon), B0 is used.
- B2: BSV/BruchidCAST heat rule (days with 20-25 °C at flowering) as the only predictor, in a 1-variable GLM. It is "what exists today".

**Model family, justified by n ≈ 100 (57 / 43):**
- Main: **hierarchical beta-binomial GLM** (logit), with a random effect by region and slopes shared across crops plus a crop interaction only where there is a biological prior. Implementation: `bambi`/PyMC, or `statsmodels` binomial GLM with ridge penalty if sampling is slow. Between 4 and 7 predictors chosen **a priori** from the literature (previous-year host at 1000 m, forest, hedgerows, days with 20-25 °C at flowering, days >12 °C in vegetative stage, rain at flowering, cycle). No automatic selection.
- Check: a shallow tree or LightGBM with a high `min_data_in_leaf`, only to see whether a non-linearity appears. With this n it is not expected to win, and this has to be said.
- **What is not done:** deep learning, predictive LLM, hyperparameter tuning with 3 folds.

**Uncertainty:** the 80% posterior predictive interval (beta-binomial, includes overdispersion and the sampling noise of 100 grains) is converted to € with Monte Carlo over the price and r-factor assumptions. The **empirical coverage** of the 80% interval must be reported in LOYO.

**Validation design:**
- Leave-one-year-out (3 folds: 2020, 2021, 2022), reported by crop. It is the honest test for D1, because the year is the unknown.
- Leave-one-region-out (4 folds), for the spatial transfer claim. Dijon only has faba bean 2022.
- All preprocessing (imputation, standardisation) goes inside the fold.
- The 3-4 distance rows per field are aggregated first. They are never split between train and test.

**Metrics:**
1. MAE in pp, against B0, B1 and B2.
2. Spearman within each year-crop (ranking).
3. **"€ captured in the top 20%"**: fraction of the real loss € that falls in the 20% of fields the model flags as highest risk. Compared with chance (0.20) and with B1.
4. 80% interval coverage.
5. Calibration by deciles (with n=100, chart only).

**Go/no-go (rules closed before looking at test):** see section 7. The minimum rule is that the D1 model beats B1 in MAE or in Spearman in at least 2 of 3 years for lentil. If it does not pass, the pitch says so.

**What the AI adds (jury test):** without a model, the collector has a regional heat rule (BSV) that the BSV itself says does not transfer to the field, and the real data arrives only after harvest. With the model:
1. A number per field with an interval, before harvest.
2. A landscape map applicable to any parcel in France.
3. A translation into € that integrates the uncertainty.

If the model is removed, what remains is a lentil density map without calibrated weight and a calculator. That is the argument. Its weakness is that, if the model does not beat B1, the AI adds little.

**Explainability:**
- GLM coefficients as odds ratios with intervals, and the contribution of each feature per field (the logit is additive, so this is exact, without SHAP).
- A "what changes the risk" panel for the map: the % of previous-year host, with its CI.
- No causal claims: the data are observational.

---

## 6. MVP and demo

**Stack:**
- Python + pandas + `bambi`/PyMC (or statsmodels).
- **Streamlit** + `folium`/`streamlit-folium` for the map.
- `shapely` + `pyproj` + `requests` for the WFS.
- Cache in parquet.
- AWS: S3 for the data and model artefacts, and Streamlit deployed on **EC2 or App Runner** with a public URL for the deck.
- Optional, non-essential Bedrock: a short explanation paragraph in French per field from the GLM contributions. Do not sell that as "the AI".
- **Backup before Sunday 12:00** (AWS accounts are closed). The GitHub repo is the source of truth.

**Screens:**
1. **"Campagne en cours" (D1).** A fictitious cooperative (invented name and marked as such) with the fields of a held-out year in the dataset (for example, the 24 lentil fields of 2022), with the model trained on 2020-2021.
   - Table sorted by € at risk, with the 80% interval.
   - Sliders: food price (default €806/t, FranceAgriMer), discard value (default €231/t, faba bean proxy, [A]), r factor (0.6-1.0, [A]), yield (default 1.5 t/ha, Terres Inovia 2025 sheet).
   - "Révéler la réalité" button that shows the observed damage alongside (in a held-out year it is measured, not synthetic).
2. **"Carte paysage" (D0).** The user picks an area (default Aube, near Nogent-sur-Seine) and the reference year.
   - The app downloads the RPG live, calculates the % of lentil at 1000 m for each candidate parcel and paints the D0 risk (landscape model + regional prior, with climate at its historical median).
   - Parcels outside the training range are marked with a dotted border and "extrapolation".
3. **"Pourquoi / Fiabilité".** Contributions per field, LOYO metrics against the baselines (the real ones, whatever they are), interval coverage and a provenance table (measured / source / assumption / synthetic).

**Live demo script (≈ 80 s within the 4 min):**
1. (10 s) "Je suis responsable lentille chez une coopérative de l'Aube, le 15 juin 2022. Mes 24 parcelles sont en fleur." Opens screen 1.
2. (25 s) "Le modèle ne connaît pas 2022. Voici le classement en euros. Ces 5 parcelles concentrent X % des pertes attendues, avec cette fourchette." I move the price slider: the € ranking changes and the risk ranking does not.
3. (15 s) Click on "révéler la réalité": measured against predicted, and the real "€ captured top 20%" against chance. The result must be shown whether it is good or bad.
4. (30 s) Screen 2: "Et pour 2027 : où semer ?" Map of Aube with the RPG 2025 live, two candidate parcels, low vs high risk, and the explanation "8% lentil at 1 km last year".

**Demo backup plan:**
- 60 s video recorded Saturday night.
- All the RPG for the demo area cached in parquet, so as not to depend on the WFS in the room.

**Repo structure:**
```
bruche-risk/
  README.md            # data provenance, declaration of prior resources
  data/raw/            # (gitignored) INRAE, SIM2, RPG cache
  data/processed/      # field_table.parquet (1 row per field), rpg_cache/*.parquet
  src/ingest_inrae.py  # download + cleaning + pooled target
  src/features.py      # landscape/climate pivots by decision date (D0, D1)
  src/rpg.py           # WFS, buffers, focal field exclusion
  src/climate.py       # SIM2/Open-Meteo -> windows by degree-days
  src/model.py         # baselines + beta-binomial GLM
  src/evaluate.py      # LOYO / LORO, metrics, coverage
  src/euros.py         # conversion to € with Monte Carlo
  app/streamlit_app.py
  reports/metrics.json, figures/
```

---

## 7. Hour-by-hour work plan

Roles: **A** data and evaluation (the most methodical), **B** modelling (the ML/CV master's student), **C** product, business and pitch.

### Friday 30/10
| Time | A | B | C |
|---|---|---|---|
| 17:45-20:45 | Welcome. **Ask a mentor about "Insects" being excluded (H19)** and declare prior resources | Ask the agri mentors: sorting losses, price deductions, discard value, a contact at a cooperative | Open the deck template, create the repo and the channel |
| 20:45-21:30 | Download INRAE (4.1) and build `field_table` (pooled, 1 row per field, D0/D1) | Re-read the methods of Chery-Lagrange and the data paper. Fix 4-7 predictors a priori and **freeze** the go/no-go rules in the README | Declare the track before 23:00. Streamlit skeleton |
| 21:30-23:00 | LOYO/LORO splits and baselines B0, B1, B2 with metrics (B1 is the number to beat) | First binomial GLM (statsmodels) in LOYO, lentil only | `rpg.py` script (reuse the syntax of 4.2) and cache for Aube 2024-2025 |
| **23:00 checkpoint 0** | The baseline table exists and the joins give 98/100 fields | | |

### Saturday 31/10
| Time | A | B | C |
|---|---|---|---|
| 9:30-10:15 | Workshop (one goes and takes notes on what the jury expects of the AI) | | |
| 10:15-13:00 | Full metrics: € top 20%, Spearman by year, coverage | Hierarchical beta-binomial (bambi), D0 and D1, both crops; "with monitoring" variant | `climate.py` (Open-Meteo for the demo, SIM2 if time allows) and stage conversion by degree-days |
| **13:00 GO/NO-GO** | **GO** if for lentil D1 beats B1 in MAE (≥10%) **or** in within-year Spearman (>0.3) in ≥2 of 3 years, **and** 80% coverage is between 65 and 95%. **NO-GO** triggers the fallback | | |
| 14:00-16:00 | LORO and final figures; provenance table | Adjust intervals; final D0 (landscape) model for the map; export coefficients | Full screen 1 with the € sliders |
| 16:00-18:00 | Leakage review (checklist in section 5) and drafting the limitations | Screen 3 (contributions) | Screen 2 (map) with the extrapolation mark; deploy on AWS |
| **18:00 checkpoint 2** | The demo runs end to end on the public URL | | |
| 19:00-24:00 (off campus) | Online project sheet (draft) | Harden the demo: cache, backup video | Deck v1 (section 10), script, timed rehearsal ×3 |

### Sunday 1/11
| Time | Everyone |
|---|---|
| 8:30-9:15 | Final numbers in the deck (from `reports/metrics.json`, not by hand), export the PDF with the link to the repo and demo, complete the online sheet |
| **9:15** | Upload. **Deadline 9:30** |
| 9:30-10:15 | Final rehearsal; test the demo on someone else's machine; video ready |
| 12:00 | Full backup of AWS (S3 and EC2) to the repo and to a drive |

**Fallback (NO-GO at 13:00):** reframe as "**Bruche Desk: carte de pression paysagère + calculateur d'impact en €**".
- The "AI" becomes the hierarchical GLM used as the **uncertainty estimator** of the region×crop prior, plus the landscape map with the previous-year effect (citing IOBC). It is presented as a hypothesis to validate with collector data (which has thousands of lots with X-ray).
- It is stated explicitly: "avec 100 parcelles, le paysage et la météo ne battent pas la moyenne régionale ; voici ce qu'il faudrait (données de réception des coopératives) pour que ce soit le cas".
- Loses AI points (see section 12), but keeps the rigour.

**Cut list (in order of what goes first):**
1. Exact SIM2 (use Open-Meteo).
2. The "with monitoring" variant.
3. The tree or LightGBM.
4. Bedrock.
5. Faba bean (keep only lentil).
6. LORO.
7. The live map (use the cache).

Never cut: the baselines, LOYO, the provenance table or the backup video.

---

## 8. Business

- **Value proposition:** "Savoir en juin combien de tonnes de lentilles alimentaires vous aurez, parcelle par parcelle, et où vos adhérents devraient semer l'an prochain pour casser le cycle de la bruche."
- **Who pays:** the grain collector cooperative (quality and filière budget). Alternative channel: Terres Inovia/Terres Univia, as an OAD funded by FASO or Cap Protéines (which already funded KAIROL and the work of Le Bihan et al.) [V the funding of those projects].
- **Pricing (assumption, with benchmarks):**
  - Market reference for a crop OAD: xarvio Field Manager, approx. €10/ha/year for the full package and €5/ha per module (secondary source ki-syndikat.de, checked 14/6/2026, prices "nicht öffentlich gelistet") [F].
  - Proposal: €5/ha of lentil per campaign, or a licence per collector [A]. Against a loss of ~€200/ha in a parcel with 30% bruchid-damaged (1.5 t/ha × 30% × r 0.8 × (806-231) €/t = €207/ha [E]), the price is <3% of the value at stake.
- **Market size (all [E] unless stated):**
  - Lentil: 34,200 ha (2024) [V]. At €5/ha that gives €171k/year: small.
  - Adding organic faba bean (16,496 ha organic + conversion in 2023 [V]) and pea (*B. pisorum*, no data here): < €0.5m/year.
  - **The SaaS market is small. The value lies in the avoidable loss for the filière**, which is what has to be pitched as impact. The realistic business model is a service for about 10 collectors plus an institutional licence.
- **Adoption:**
  1. Pilot with a collector in Aube or Yonne (the data area), feeding the model with its geo-referenced reception analyses by lot (which they already have, especially if they use X-ray).
  2. Validate against the Terres Inovia survey.
  3. Integrate as a module of the BSV or of a Terres Inovia OAD.
- **Competitors and differentiation:**

| Existing | What it does | Difference |
|---|---|---|
| Regional BSVs / Terres Inovia rule (Tmax ≥20 °C for 2 days from young pod) [V] | Regional activity alert to treat | There is no longer a treatment for lentil. We predict damage per field and in € |
| BruchidCAST (Syngenta + PGRO, UK, 2009) [V] | Spray timing 5 days ahead in faba bean | No damage, no landscape, no France |
| Lentodor / FabaOdor (kairomone traps) [V] | Biocontrol; no significant effect in lentil (KAIROL) | Complementary: the map says where to place traps if they ever work |
| X-ray / dissection at reception [V] | Measures real post-harvest damage | Arrives too late for contracting and for sowing planning. It is our future source of labels |
| "Sort everything" | What is done today | Does not reduce the population or help plan volume |

---

## 9. Impact and sustainability

- **Current food lentil loss [E]:** 34,200 ha × 1.50 t/ha × bruchid % × r × (806 - 231) €/t.
  - 2025 (24.4%): **7.5-12.5 kt taken out of the food chain, €4.3-7.2m** (r from 0.6 to 1.0).
  - "Typical" year 2021-2024 (mean 12.9%): 4.0-6.6 kt, €2.3-3.8m.
  - Context: France imports 39.5 kt/year [V], so the 2025 losses equal **19-32% of imports** [E].
- **What part of that the tool can move [A, to declare as hypothesis]:**
  1. Logistics: separating high-risk lots at reception avoids re-contaminating silos and re-sorting, although we do not know how much that is worth.
  2. Population: if sowing moves away from areas with a high % of lentil the year before, pressure falls. The effect has been observed on bruchid density (IOBC) [V], **not quantified on damage**.
  - Illustrative scenario, labelled as such: if 1 point of bruchid % were avoided at national level, that would be 513 t/year (r = 1) ≈ €0.3m [E].
- **Protein sovereignty and hectares:** Le Bihan et al. note that the annual pressure "pourrait décourager" the expansion of lentil [V, translation]. Area fell from 37,529 ha (2019) to 28,670 ha (2023) [V RPG]; the causality with the bruchid is [NV]. The track's goal (doubling pulses by 2030) [V guide] runs into a risk with no insurance or tool.
- **CO2 [E, weak, use with care]:** replacing imported lentil from Canada with French lentil saves sea transport. I did not find a published factor per tonne for this route, so **do not give a figure in the pitch** unless a mentor provides one.
- **Insecticides:** the tool does not recommend chemicals. In faba bean, it helps avoid the application at flowering that is "rarement valorisée" (2024 guide) [V] when the damage risk is low.

---

## 10. Pitch

### Script (4:00 strict)
| Time | Content |
|---|---|
| 0:00-0:40 | **Problem.** Photo of bruchid-damaged lentils. "In 2025, one French lentil in four was bruchid-damaged (Terres Inovia, 24.4%). No insecticide authorised since 2024. France imports 39,500 t, mostly from Canada." User: "Claire, lentil supply chain manager at a cooperative in Aube." |
| 0:40-1:20 | **Solution.** Two decisions: in June, the food volume and the lots to separate; in winter, where to sow. INRAE data (100 fields, 3 years, 4 regions) + RPG + SAFRAN. Beta-binomial model with uncertainty. |
| 1:20-2:40 | **Live demo** (script in section 6). |
| 2:40-3:20 | **Rigour.** "Tested on a year never seen": metrics against the regional mean, interval coverage and limits (91% organic, no Berry or Puy, n=100). Measured / source / assumption in colours. |
| 3:20-4:00 | **Scaling.** Pilot with a collector (its reception analyses as labels), extension to organic faba bean and pea, Terres Inovia OAD. € at stake: €2.3-7.2m/year of lentil leaving the food chain [E]. |

### Deck slides (official template)
1. Title + team + track 3.
2. Problem in figures (2021-2025 series, Centre-Ouest, no insecticide, imports).
3. User and decisions (table in section 2).
4. Data and provenance (measured / source / assumption / synthetic).
5. Method (decision dates, leakage avoided, model, uncertainty).
6. LOYO results against the baselines (the real ones).
7. Demo (screenshot + link).
8. Impact in € and tonnes (labelled [E]).
9. Business and adoption.
10. Limits and next steps.
11. Sources and declaration of prior resources.

### Likely jury questions
- **"Do 100 fields suffice?"** To claim mechanisms, no. For a prior with honest uncertainty, yes, and that is why the model is hierarchical and simple, and coverage is measured. The product scales with collectors' reception data, which has thousands of lots.
- **"If sorting works, why predict?"** Sorting saves quality but not tonnes (15-50% losses), and it does not help plan contracts or sowing. IGP Berry requires <0.1% unacceptable after sorting: the lost volume is the problem.
- **"The dataset is almost all organic."** Conventional lentil has had no insecticide since July 2024 either, and 45% of lentil area is organic. For conventional faba bean we make no claims.
- **"Does it beat the regional mean?"** Show the number as it is. If it does not: "c'est notre résultat, et voici pourquoi les données de réception changeraient ça".
- **"How do you know the % of previous-year lentil in real time?"** The RPG arrives a year late. We use the cooperative's contracted areas plus RPG N-2. We demonstrate live with the WFS.
- **"Isn't it a project about insects?"** It is protection of a human-food crop, not insects as food. Confirmed with the organisers on Friday (if confirmed).
- **"Causality?"** We do not claim it. The landscape is a predictor, consistent with INRAE (IOBC 2026). Causality would be tested with a coordinated rotation pilot.

---

## 11. Risks, questions, prior resources, checklist

### Risks and mitigations
| Risk | Prob. | Mitigation |
|---|---|---|
| The model does not beat B1 in LOYO | High | Go/no-go at 13:00, fallback and honest reporting |
| Exclusion for "Insects" | Low-medium | Ask in writing on Friday (organisers' WhatsApp) |
| Landscape definition different from the authors' | Medium | Use only "previous year"; compare the distribution; email A. Gardarin on Friday (optional) |
| WFS down during the pitch | Medium | Parquet cache + video |
| € assumptions challenged | High | Sliders, [A] label and question to mentors |
| Extrapolation (Berry/Puy, landscape values out of range) | High | Dotted border "extrapolation" on the map |
| The "drivers" paper comes out | Low | Cite it as backup |
| Stage windows at inference | Medium | Degree-days, and declare it |

### Questions for mentors (Friday)
1. Does a project about an insect pest of a food crop fall under "Insects"?
2. How much does it cost to sort one tonne of lentil, and what typical loss does a lot with 20% bruchid damage have (by count)? What mass factor r do they use?
3. What price is paid for downgraded lentil (feed or methanisation)? What does a typical bruchid réfaction grid look like?
4. Do collectors keep the % bruchid-damaged per lot and per parcel of origin? (That is the data needed to scale.)
5. On what date does the cooperative decide today the food volume it contracts with packers?
6. Do they know anyone at Axéréal, InVivo, CAVAC or Qualisol to validate the user?

### Prior resources to declare
- Desk research: `archive/research/idea3_bruchids.md`, `archive/research/track3_context.md`, `archive/research/datasets*.md`, this dossier, `archive/initial_ideas/track3_pest_risk_and_drone_yield_mvp_plans.*`.
- Derived table `archive/research/datasets/rpg_pulses_dept_year.csv`.
- Descriptive exploration of the INRAE dataset (counts, missing values, descriptive η²) and the WFS syntax test (not solution code; rewritten at the event).
- Generic libraries: pandas, statsmodels, bambi/PyMC, shapely, pyproj, streamlit, folium.

### Deliverables checklist (Sunday 9:30)
- [ ] Deck PDF from the official template, with the link to the repo and the demo.
- [ ] Project sheet completed online (non-confidential: problem, solution, business model).
- [ ] Public repo with README (provenance, prior resources, how to run it).
- [ ] `reports/metrics.json` with LOYO/LORO and the baselines.
- [ ] Demo deployed and tested on another machine, plus the backup video.
- [ ] Measured / source / assumption / synthetic table in the deck and in the app.
- [ ] Sources verified (no citation without opening it).
- [ ] AWS backup before 12:00 on Sunday.

---

## 12. Rubric (self-assessment)

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Impact and sustainability | 30% | 6 | Large, documented problem (24.4% in 2025, no insecticide, 39.5 kt imported), aligned with human food. But predicting does not reduce damage by itself: the effect on tonnes is hypothetical |
| Scientific and technical rigour | 20% | 7 | Open data with a data paper, validation by year, explicit leakage, traceable provenance. n=100, no coordinates, RPG→model transfer not validatable |
| Appropriate and essential AI | 20% | 5.5 | The hierarchical model with uncertainty is the right method for the n, but if it does not beat B1 the AI is incidental. The live map helps |
| Economic viability | 20% | 5 | Named buyer (collectors from KAIROL, InVivo), but small SaaS market (<€0.5m) and willingness to pay not verified |
| Execution and pitch | 10% | 7 | Simple stack, convincing demo with "révéler la réalité", low risk of failure |
| **Weighted total** | | **6.0** | 0.3×6 + 0.2×7 + 0.2×5.5 + 0.2×5 + 0.1×7 |

If the 13:00 GO goes well, AI rises to 7 and the total to ~6.3. With fallback, AI drops to 4 and impact to 5: total ~5.4.

---

## 13. Sources (only pages opened today)

- INRAE dataset, Dataverse API: https://entrepot.recherche.data.gouv.fr/api/datasets/:persistentId/?persistentId=doi:10.57745/HPEMYW (and `/api/access/datafile/{id}`)
- Herrera et al. 2026, Data in Brief (data paper): https://pmc.ncbi.nlm.nih.gov/articles/PMC13264089/
- Chery-Lagrange et al. 2026, Pest Manag Sci, doi 10.1002/ps.70679: https://pmc.ncbi.nlm.nih.gov/articles/PMC13158440/
- Herrera et al. 2026, IOBC-WPRS Bulletin 182:97-101: https://iobc-wprs.org/product/managing-populations-of-bruchid-pests-in-grain-legumes-role-of-resource-provisioning-at-field-and-landscape-levels/
- HAL search (API) and Crossref, with no trace of the "drivers" paper: https://api.archives-ouvertes.fr/search/ , https://api.crossref.org/works
- Le Bihan, Jauvion, Dauguet, Ruck, Riquet 2025, Innovations Agronomiques 99:165-176 (read via Chrome because of HAL's anti-bot): https://hal.inrae.fr/hal-04926988v1 (PDF https://hal.inrae.fr/hal-04926988/document)
- Terres Inovia, lentil grain quality sheet, harvest 2025 (read via Chrome, 403 for bots): https://www.terresinovia.fr/sites/default/files/2026-02/fiche-qualite-graines-lentille_2025.pdf
- Terres Univia, KAIROL project (9/10/2023): https://www.terresunivia.fr/l-interprofession/actualites/bruche-de-la-lentille-le-projet-kairol-evalue-une-nouvelle-solution-de-lutte
- Terres Univia, faba bean quality 2025 (9/4/2026): https://www.terresunivia.fr/l-interprofession/actualites/qualite-des-graines-de-feverole-une-bonne-teneur-en-proteines-en-2025
- Terres Univia, Chiffres clés 2024: https://www.terresunivia.fr/fichiers/publications/chiffres-cles-2024.pdf
- Perspectives Agricoles n°500 (1/6/2022), lentil supply chain diagnosis: https://www.perspectives-agricoles.com/economie/diagnostic-de-la-filiere-lentille-une-culture-davenir-mais-encore-fragile
- La Dépêche (1/3/2016), faba bean and Egypt: https://www.reussir.fr/ladepeche/la-feverole-francaise-en-difficulte-sur-legypte
- Specification IGP Lentilles vertes du Berry (17/11/2025): https://info.agriculture.gouv.fr/boagri/document_administratif-40f9105a-26b0-47e0-9799-f0161c3a8df5/telechargement
- Specification AOP Lentille verte du Puy (2018): https://info.agriculture.gouv.fr/boagri/document_administratif-3b601fa7-0c84-48e9-b94b-bffff44295fb/telechargement
- Terres Inovia faba bean guide 2024 (mirror): https://germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/FEVEROLE-2024-Guide-culture-TERRES-INOVIA.pdf
- Terres Inovia lentil guide 2023 (mirror): https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/LENTILLE-2023-Guide-culture-TERRES-INOVIA.pdf
- FranceAgriMer, quarterly prices paid to producers: https://visionet.franceagrimer.fr/Pages/OpenDocument.aspx?fileurl=SeriesChronologiques%2fproductions%20vegetales%2fgrandes%20cultures%2fprix%20pay%c3%a9s%20aux%20producteurs%2fSCR-CER-HISTOPRIXTRIMESTRIELS-C25-26.xlsx&telechargersanscomptage=oui
- Geoplateforme WFS (GetCapabilities, DescribeFeatureType, GetFeature RPG 2019-2025, codes_cultures 2024, BDTOPO hedgerow/vegetation): https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities
- Météo-France SIM2 on data.gouv (API) and latest file: https://www.data.gouv.fr/api/1/datasets/donnees-changement-climatique-sim-quotidienne/ , https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/QUOT_SIM2_latest.csv.gz
- Open-Meteo archive (test): https://archive-api.open-meteo.com/v1/archive
- BSV protein crops Centre-Val de Loire, balance 2025-2026: https://draaf.centre-val-de-loire.agriculture.gouv.fr/IMG/pdf/bsv_proteagineux_bilan_2025_2026.pdf
- Farmers Weekly (26/5/2009), BruchidCAST: https://www.fwi.co.uk/arable/bruchid-beetle-alerts-to-help-time-sprays
- ki-syndikat.de, xarvio prices (secondary source): https://www.ki-syndikat.de/tools/xarvio-field-manager/
- Participant Guide Hack the Fork 2026 (local file): `event/participant_guide.txt`

Failed attempts (so they are not repeated): Terres Inovia and HAL block curl/WebFetch (403 and Anubis), so use Chrome. There is no public GASC specification for faba bean. I found no published costs of sorting lentil (€/t) or a price for downgraded lentil.
