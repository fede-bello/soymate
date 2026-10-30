# Dataset map: Hack the Fork Paris 2026 (Track 3)

Audit done on 29/10/2026 by 9 subagents (4 in the first round on the original ideas, 5 in this round by domain). Data was downloaded, rows were counted and joins were verified; **no model was trained** (hackathon rule). All downloaded data was deleted afterwards; only the scripts remain in the session scratchpad.

Tags: **[V]** verified against the file or API, **[F]** read at the source, **[NV]** not verified.

Detailed reports (with all URLs):

| File | Contents |
|---|---|
| `datasets/agronomy_plant_health.md` | Trials, rotations, plant health (23 datasets) |
| `datasets/geo_soil_climate.md` | RPG, Sentinel-2, soil, climate, suitability (23 datasets) |
| `datasets/economics_markets.md` | Trade, prices, margins, subsidies, organic, silos (16 datasets) |
| `datasets/food_quality.md` | Open Food Facts, Ma Cantine, DECP, CIQUAL, Agribalyse (12 datasets) |
| `datasets/ai_corpus_benchmarks.md` | Corpus for RAG, images, ML benchmarks (30 assets) |
| `datasets/rpg_pulses_dept_year.csv` | Derived table: year × dept × pulse, parcels and ha, RPG 2015-2024 (8,336 rows) |
| `idea3_bruchids.md`, `idea5_drone.md`, `ideas2_4_time_series.md`, `track3_context.md` | First-round audits |

---

## 1. The 12 datasets that matter

Sorted by usefulness for a 20 h project on Track 3.

| # | Dataset | What it contains (verified numbers) | Access / license | Main limitation |
|---|---|---|---|---|
| 1 | **RPG 2015-2024** (IGN, WFS `data.geopf.fr/wfs`) | Polygon of each PAC parcel (PAC = Politique agricole commune, the EU Common Agricultural Policy) with fine crop code: LEC (lenteja = lentil), PCH (garbanzo = chickpea), FVL/FVP (haba = faba bean), PPR/PHI (arveja = pea), PHS (arveja and poroto seco = dry bean, for human food, since 2023). 2024: lentil 34,226 ha / 8,077 parcels, chickpea 27,491 ha / 6,373 parcels [V] | WFS without login, 5,000 features per page; Licence Ouverte (French open government license) | No department or destination column; `id_parcel` matches the previous year only 63% of the time, so rotations require a geometric join |
| 2 | **Pea_dataset** (INRAE + Terres Inovia + GEVES, doi 10.57745/FW78RE, published 05/08/2026) | 4,450 site × genotype × year records, 158 sites, 40 départements (French administrative departments), 117 genotypes, 2002-2024 (95% in 2013-2024). 4,230 yields (mean 49.5 q/ha) and 3,326 protein values (mean 22.9%, 16-31%). Full flowering data, soil without gaps, daily climate per site. Clean joins [V] | Direct download 10 MB; Etalab 2.0 | Anonymized genotypes; pea only; protected trials, not farms; no pests or diseases |
| 3 | **Bruchid INRAE** (doi 10.57745/HPEMYW) | 98 fields with damage + climate + landscape + practices, 2020-2022, 4 regions. Median damage 13.7% faba and 33.4% lentil [V] | Direct download; Etalab 2.0 | 91% organic, noisy label (25 grains per point), no coordinates |
| 4 | **Eurostat Comext DS-045409** | FR trade by CN8 × country × month, 1988-2025. Lentil: ~40.8 kt/year imported for 46.4 M€ (2023-25), 46% Canada, 32% Belgium. Dry bean: ~32 kt for 40 M€. Substitutable gap lentil + dry bean: ~63 kt and ~70 M€ net/year [V] | JSON API, no key; CC BY 4.0 | Belgium and the Netherlands hide the true origin; chickpea is already almost a net exporter |
| 5 | **FranceAgriMer, producer prices** (quarterly, 2004/05-2025/26) | Lentil 854 / 873 / 806 €/t (2023/24 to 2025/26) vs wheat 205 / 194 / 170 and pea 247 / 275 / 222 [V] | Direct xlsx; the file says "tous droits réservés" (all rights reserved), cite the source | Lentil only from 2023/24; no chickpea or dry bean; national level only |
| 6 | **Agreste SAA séries longues** (departmental, 2010-2025, long series) | Area, production and yield by département. Pea: 38 usable départements for temporal holdout; faba 28 [V] | ZIP xlsx; Licence Ouverte | Lentil and chickpea heavily imputed (~51-53% of values copied between départements); 2010-2019 back-cast |
| 7 | **SAFRAN / SIM2** (Météo-France, data.gouv) | 8 km grid, daily since 1958: rain, temperature, ETP (potential evapotranspiration), soil moisture [F] | Download ~137 MB/year; Licence Ouverte | Heavy if many years are downloaded; for a single point, Open-Meteo is enough |
| 8 | **Sentinel-2 L2A** | Test on a 16.4 ha lentil field near Le Puy: 14 scenes and 1,637 pixels [V] | Planetary Computer (anonymous SAS token), Earth Search (public COGs, no token) | Clouds; +1000 offset in Planetary Computer since 2022 |
| 9 | **BSV OCR archive** (data.gouv, PestObserver) | 40,828 BSV bulletins (Bulletin de santé du végétal, French plant health bulletin) 1950-2016; 3,077 mention pulses, 597 mention the bruche (bruchid). The threshold ">2 jours >20°C au stade jeune gousse" (more than 2 days above 20°C at the young pod stage) appears verbatim [V] | Zip 173 MB; CC-BY | Ends in 2016; medium OCR quality. BSV 2017-2026 are scattered across DRAAF sites (regional agriculture directorates), with no index |
| 10 | **Open Food Facts** (HF `food.parquet`) | 1.29 M products sold in France; 12,069 with a pulse ingredient. Only 17.5% declare origin; 8.3% explicitly say "France" [V] | Parquet queryable with remote duckdb; ODbL | Crowdsourced; origin of the whole product, not of the ingredient |
| 11 | **Ma Cantine** (registry + télédéclarations, online reporting) | 66,346 canteens registered; 49,570 reported in 2025. Open data per canteen only includes % organic and % EGalim (French law on canteen food) [V] | Daily CSV on data.gouv; Licence Ouverte | No pulse purchase data or origin; vegetarian menu only in aggregates |
| 12 | **Cereal-pulse intercropping** (Zenodo 14160885) | 37 trials (26 in France), 34,737 rows, with lentil, chickpea, pea and faba bean, each mix with its pure crop [V] | Download 8 MB; CC-BY 4.0 | Station trials 2001-2017, no economic variables |

---

## 2. Full map by domain

### 2.1 Areas, parcels and rotations

| Dataset | Granularity | Access | Rel. | Notes and limitations |
|---|---|---|---|---|
| RPG 2015-2024 | Parcel, annual | WFS without login | 10 | See table 1. In 2022 the geometry is called `the_geom`. `RESULTTYPE=hits` counts without downloading |
| RPG 2025 v4 | Parcel + `precision` + `bio` | 7z only (national 10.9 GB) | 9 | In Île-de-France, 61% of lentil and 75% of chickpea is organic [V]. Meaning of `precision` unconfirmed |
| RPG Bio 2019-2023 (Agence Bio) | Organic parcel with INSEE commune | GPKG per region | 8 | Distinguishes destination: "Pois protéagineux (alimentation animale)" (protein pea, animal feed) vs "Pois cassé" (split pea) [V] |
| Derived table RPG × dept | Year × dept × pulse | CSV in this repo | 10 | National lentil 17.2k ha (2015) → 34.2k (2024); chickpea 8.9k → peak 36.7k (2019) → 27.5k; pea 158k → 124k [V] |
| Crop succession indicators 2015-2023 (doi 10.57745/WQ4MIF) | Commune / dept, AB (organic) vs conventional | CSV 77 MB | 6 | "Legumbre" (pulse) mixes alfalfa and grasslands with grain pulses |
| Agence Bio, area by dept 2008-2025 | Dept × production | CSV 224 KB | 7 | 2025: ~14,100 ha organic lentil, 7,600 chickpea, 21,700 faba bean. 37% of cells "NC" (non communiqué, not disclosed). CSV titles swapped on data.gouv |
| Theia OSO 2016-2023 | 10 m raster | ~5 GB/year | 5 | A single class "protéagineux (féverole/pois)" (protein crop: faba bean/pea) |
| PASTIS / EuroCrops / Sen4AgriNet / AI4Boundaries / HRL Crop Types | Varied | Zenodo / HF | 2-4 | PASTIS has no grain pulses; EuroCrops France = RPG 2018 recoded. Better to go straight to the RPG |
| CropHarvest | Points | Zenodo | 4 | 618 pulse points in Île-de-France |

**Sample rotations [V]:** in the Le Puy basin, lentil follows cereal (58%) or grassland (25%) and is followed by soft wheat (66%); it returns after 2 years only 7% of the time. In Charente, chickpea follows cereal (87%) and is followed by wheat (64%).

**Territorial shifts [V]:** lentil in Haute-Loire -35% (4,113 → 2,680 ha), Indre -66% since 2017, Gers -66% since 2020, Aube +186% (1,340 → 3,838 ha). Chickpea in Vendée from 6 to 2,324 ha: chickpea is moving northwest.

### 2.2 Yields and trials

| Dataset | Granularity | Access | Rel. | Notes and limitations |
|---|---|---|---|---|
| Pea_dataset | Site × genotype × year | 10 MB | 9 | See table 1. Annual means fall from 55-58 q/ha (2015, 2019) to 41 (2021) |
| Agreste SAA | Dept × year | ZIP | 7 | See table 1. Oise pea with an artifact in 2020 |
| Eurostat `apro_cpsh1` / `apro_cpshr` | Country / NUTS2 | API | 5-6 | Yield is almost never published at regional level. Eurostat pea 166 kha in 2024 vs 124 kha in RPG and Terres Univia |
| WSU/USDA drone (Zenodo 8280431) | Trial plot, USA | 10.8 GB | 4 | See `idea5_drone.md`. Deflate64, uncalibrated mosaics |
| Intercropping 37 trials | Plot × date | 8 MB | 7-8 | Allows computing the LER (land equivalent ratio, i.e. the advantage of the mixture) |
| Rés0Pest 2013-2023 | Plot × year | CSV | 3 | ~55 rows with pulses |
| Chickpea × service plants (doi 10.57745/05KBPZ) | Block × treatment | 34 kB | 5 | One site, 84 yields |
| CY-Bench | Region | Zenodo | 1 | Maize and wheat only [V] |
| Global grain legume experiments (Cernay) | Meta-dataset | Zenodo, CC0 | 5 | 173 articles, 39 species, 2017 |
| myVar / GEVES / Epiphyt / EVA Aphanomyces | | Closed or no download | | myVar behind reCAPTCHA; Epiphyt has no open pest data; EVA database (780 plots) closed |

### 2.3 Plant health

| Dataset | Rel. | Notes |
|---|---|---|
| Bruchid INRAE | 8 | See table 1 and `idea3_bruchids.md` |
| BSV OCR archive | 9 | See table 1. Ideal for LLM extraction |
| BSV 2017-2026 (DRAAF) | 8 | DRAAF Centre-Val de Loire: ~15-22 PDFs per pulse campaign, extractable text. No explicit license |
| GBIF (Bruchus, Sitona, Aphanomyces) | 2 | 4 Aphanomyces records in France, 80 of *B. rufimanus* with coordinates |
| Ascochyta pea (doi 10.57745/5B1XGU) | 3 | Lab, 2 cultivars |

### 2.4 Images for vision

| Dataset | Size | License | Rel. | Limitation |
|---|---|---|---|---|
| Soybean with *Callosobruchus* (Mendeley d97rjyk2tz) | 2,726 images, 14,475 YOLO boxes, 5 classes | CC-BY 4.0 | 8 | Soybean and storage bruchid, not *Bruchus* on faba/lentil; 53 test images nearly duplicated from train |
| Soybean Seeds 5 classes | 5,513 images | CC-BY 4.0 | 6 | Soybean; 290 duplicate groups |
| Faba bean leaves INRAE (doi 10.57745/H7JVFN) | 2,110 photos, 8 classes, zip 6.7 GB | CC-BY-NC | 6-7 | 60% multi-cause; almost all from one site |
| Faba bean X-rays GEVES (7,210 RAGT seeds) | | Not public | 7 if provided | Must be requested from GEVES |
| Faba Bean Seed Image (Zenodo 18226381) | 554 lines | CC-BY 4.0 | 4 | No damage labels |
| Lentil disease (AgML), Pea seed viability, Indian Lentils, Dry Bean (Koklu) | | Various | 2-5 | Bangladesh/China/Turkey, augmented or with duplicates |

**There is no open dataset of faba, lentil or pea grain damaged by *Bruchus*.** Searched on Kaggle, HF, Zenodo, Mendeley and Recherche Data Gouv.

### 2.5 Economics, markets and supply chain

| Dataset | Rel. | Notes |
|---|---|---|
| Comext DS-045409 | 10 | See table 1. Chickpea: imports 13 kt at €1.51/kg (Mexico premium) and exports 16 kt at €0.8-1.1/kg |
| Douane (lekiosque / ODS) | 7 | The ODS mirror is frozen (Mar-2023 to Mar-2024); NC8 codes stored as integers, without the leading 0 |
| FranceAgriMer prices | 9 | See table 1 |
| Terres Inovia guides (margins) | 8 | Winter pea €810/ha (feed) to €945/ha (human) vs wheat €1,025/ha; preceding-crop effect +€27 to +€61/ha/year. Chickpea €505-1,155/ha. Lentil costs only (€518/ha) [F]. Site blocks bots, `ai-train=no` |
| Coupled pulse aid | 6 | €122/ha in 2024-2025 [F]; no hectares or beneficiaries published |
| RICA / FADN (farm accountancy data network), CAP beneficiaries | 3-5 | Do not isolate pulses; microdata in CASD (Centre d'accès sécurisé aux données, French secure data access centre), inaccessible in 20 h |
| Géorisques ICPE (silos) | 6 | Coordinates and capacity in m³; filter rubrique (classification heading) 2160 client-side; does not say which grain. ICPE = installations classées pour la protection de l'environnement (French classified facilities) |
| FranceAgriMer Visionet (collecte, grain collection, by dept) | 6 | JS pages, not verified |
| EU agri-food portal (cereal prices) | 5 | No pulses; Rouen wheat ~€207/t in 2026 |

### 2.6 Food and consumption

| Dataset | T3 | T2 | Notes |
|---|---|---|---|
| Open Food Facts | 8 | 9 | France share among those declaring origin: green lentil 86%, lentils 59%, split pea 73%, chickpea 49%, meat analogues 41%, hummus 32% [V]. Analogues: median 18 ingredients, 54% NOVA group 4 |
| Ma Cantine | 7 | 9 | See table 1. 96.7% of school canteens that responded serve a weekly vegetarian menu |
| DECP (public contracts; Données essentielles de la commande publique, French public procurement open data) | 6 | 8 | 3.36 M contracts; 246 related to pulses since 2019 (7 in 2019, 63 in 2025). Origin "France" empty in 79% of food contracts. "Lentille" (lentil) matches optical lenses |
| CIQUAL 2025 (French food composition table) | 6 | 8 | 38 pulses; dry protein: lentil 25.1 g, faba 26.1, lupin 36.2 |
| Agribalyse 3.2 (French food LCA database) | 7 | 8 | Dry lentil 0.58 kg CO2e/kg vs ~29 for beef. **Does not distinguish origin** for pulses |
| Agribalyse 4 | 6 | 7 | Looks preliminary (DQR = 5 in all rows, 15 negative scores) |
| INCA3 (2014-15) | 4 | 7 | Adults: 7.7 g/day of pulses alone |
| SIQO reference (INAO; official quality signs) | 6 | 4 | List of AOP/IGP (protected designation of origin / protected geographical indication) pulses, without volumes |
| Terres Inovia "qualité des graines" (seed quality) | 9 | 4 | Only aggregated PDFs: faba 2025 28.4% protein; pea 2025 22.8%, ~60% of lots fit for human food [F] |
| LCA of lentil and chickpea, INRAE | 4 | | National average |
| Lentil consumption survey 2022 (doi 10.57745/KMGODH) | 4 | | 607 responses |

### 2.7 Soil, climate and suitability

| Dataset | Rel. | Notes |
|---|---|---|
| SAFRAN / SIM2 | 8 | See table 1 |
| Open-Meteo | 6 | No key, ERA5-Land since 1950; with `era5_land` the rain comes out empty, use `era5`. 10,000 calls/day, non-commercial |
| SoilGrids 2.0 | 7 | 250 m; use VRT/COG (the API has a rate limit); no carbonates |
| BDAT (Base de données analyses de terre, French soil analysis database), BDGSF (Base de données géographique des sols de France, French soil geographic database), LUCAS, RMQS (Réseau de mesures de la qualité des sols, French soil quality monitoring network) | 4-6 | Restricted or require manual registration |
| GAEZ v4 | 6 | Chickpea, pea and dry bean yes; lentil and faba bean no. Chickpea suitability = 0 north of the Loire (climate 1981-2010), contradicting the observed expansion in the RPG |
| Crop Suitability *Pisum* ERA5 (doi 10.57745/EYAMIF) | 4 | Static index, not validated |
| DRIAS / Explore2, Climadiag (DRIAS: French climate projections portal) | 4-6 | Require an account |
| ADMIN EXPRESS (IGN) | support | Commune and dept polygons to join the RPG with Agreste |

### 2.8 Text corpora (for LLM or RAG)

| Corpus | License | Rel. | Notes |
|---|---|---|---|
| BSV OCR archive | CC-BY | 9 | See table 1 |
| BSV 2017-2026 (DRAAF) | No explicit license | 8 | Must be scraped region by region |
| HAL pulses (HAL: French open archive) | Mixed | 7 | 5,084 records, 1,494 with PDF, 289 CC-BY |
| Legume Hub | Non-commercial | 6 | 268 articles, English |
| GECO (EcophytoPIC) | CC BY-NC-SA 3.0 FR | 5 | Focused on pesticide reduction |
| Terres Inovia (guides) | `ai-train=no`, `use=reference` | 3 (by license) | **Do not ingest in bulk.** Cite with a link or ask for permission |
| EIP-AGRI practice abstracts | EU legal notice | 5 | No bulk download |

---

## 3. Join keys between datasets

| Key | Datasets using it | Caution |
|---|---|---|
| Dept code (INSEE) | SAA, Agence Bio, RPG derived table, Ma Cantine | The RPG does not include it: centroid + ADMIN EXPRESS (0.01% no match) |
| Commune code (INSEE) | RPG Bio, Ma Cantine, crop successions, DECP | Commune mergers between years |
| RPG crop code | RPG, RPG Bio, EuroCrops | Code change in 2023 (HAR/PPO → PHS/PHF) |
| CN8 (EU combined nomenclature, 8 digits) | Comext, Douane | 0713xx; in Douane's ODS it comes without the leading 0 |
| Geometry / coordinates | RPG, Sentinel-2, SAFRAN, SoilGrids, ICPE silos | Different CRS (Lambert 93 in RPG, UTM in S2) |
| Trial site | Pea_dataset | No public exact coordinates [NV], joined by dept |

## 4. What does not exist (gaps that may be opportunities)

- Images of pulse grain damaged by *Bruchus* (only soybean with *Callosobruchus*).
- Pulse purchase data in canteens and their origin (Ma Cantine does not publish it; DECP hides it in "épicerie" (grocery) lots).
- Origin per ingredient in products (Open Food Facts: 17.5% with declared origin, of the whole product).
- An LCA that distinguishes French from imported lentil (Agribalyse does not).
- Reliable dept-level yield for lentil and chickpea (Agreste imputes ~half).
- Forecast of the current year's areas: the RPG for year N only comes out in September of N+1.
- Open surveys on why farmers do not sow pulses (only PDF reports from the LEGITIMES project).
- Closed databases worth requesting: EVA Aphanomyces (Terres Inovia), faba bean X-rays (GEVES), Epiphyt.

## 5. Sector figures to cite with care

- Pea area: 124k ha (RPG and Terres Univia, 2024) vs 166k (Eurostat 2024) vs 98k (Terres Univia 2025) vs 150k (Agreste 2026, "purs ou mélangés", pure or mixed). Always cite the source and scope.
- Lentil: RPG 2024 34.2k ha matches Eurostat 2025 (33.9k ha) [V].
- The "4%" in the guide includes forage crops; grain pulses are ~1.6% of the UAA (utilised agricultural area, SAU) (see `track3_context.md`).
