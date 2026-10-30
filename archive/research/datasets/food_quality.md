# Datasets: food end of pulses and the field-to-plate link

Audit done on 29/10/2026 (eve of Hack the Fork). Exploration only: download, inspection and counts. No model fitted.

Legend: **[V]** verified by me on the data (download or direct query), **[F]** read from an official source (page, PDF, search engine) but not recalculated, **[NV]** not verified (memory or inference).

## Summary table

| Dataset | Owner | Coverage | Granularity | License | Access | T3 | T2 | Main limitation |
|---|---|---|---|---|---|---|---|---|
| Open Food Facts (food.parquet) | Open Food Facts (association) | World, 4.88 M products; 1.29 M sold in France | Product (EAN) | ODbL (data), AGPL (code) | Parquet on HuggingFace, queryable with remote duckdb; API | 8 | 9 | Declared origin only for 17.5% of products with pulses; crowdsourced |
| Ma Cantine: national canteen register | MASA (betagouv) | 66,346 restaurants | Restaurant (SIRET, commune, EPCI, PAT) | Licence Ouverte 2.0 | Daily CSV on data.gouv | 7 | 9 | No pulse purchase data |
| Ma Cantine: télédéclarations (online reporting) 2021-2024 | MASA | 5,081 (2022) to 21,592 (2024) declarations | Declaration per canteen/central kitchen, annual | Licence Ouverte 2.0 | CSV on data.gouv | 6 | 8 | Open data only includes % organic and % EGalim; vegetarian menu and diversification plan NOT published per canteen |
| Ma Cantine public API + EGalim 2025 statistical report | MASA | 66,353 canteens published | Canteen (badges), national aggregate (vegetarian) | Licence Ouverte | REST JSON / PDF | 6 | 9 | Diversification only as a boolean badge or in report aggregates |
| CIQUAL 2025 | ANSES | 3,484 foods, 84 columns | Generic food | Etalab 2.0 | XLSX/XML on recherche.data.gouv | 6 | 8 | No origin or variety; 38 pulses |
| Agribalyse 3.2 (data.ademe "31") | ADEME / INRAE | 2,451 foods | Generic food, per stage and per ingredient | Licence Ouverte 2.0 | CSV via data-fair API | 7 | 8 | No FR vs imported distinction for pulses; green/yellow/coral lentils identical |
| Agribalyse 4 (synthèse) | ADEME | 2,455 foods | Generic food | No license declared in the API | CSV via data-fair API | 6 | 7 | Looks preliminary: DQR = 5 in 100% of rows, 15 unique negative scores |
| INCA3 | ANSES | 4,114 individuals (2,121 adults, 1,993 children), 2014-2015 | Individual, consumption g/day per 44 groups and per food | "notspecified" on data.gouv | CSV on data.gouv | 4 | 7 | Old (2014-15); pulses alone only 7.7 g/day in adults |
| DECP consolidated | Colin Maudry / Etalab (public sources) | 3.36 M public contracts | Contract (buyer, supplier, CPV, amount) | Licence Ouverte 2.0 | Parquet 255 MB, remote duckdb | 6 | 8 | Only contracts above threshold; pulses grouped under "épicerie" (grocery); many duplicates |
| SIQO reference (INAO) | INAO | 5,246 products under an official quality sign | Product / designation | Licence Ouverte 2.0 | CSV on data.gouv | 6 | 4 | Nominal list: no volumes, areas or number of producers |
| Terres Inovia "qualité des graines" (seed quality) pea/faba bean | Terres Inovia / Terres Univia | French harvest, ~76 faba bean samples (2025) | Samples from organismes stockeurs (grain storage organisations), aggregated | Public document, not open data | PDF (blocks bots) | 9 | 4 | Only PDFs with aggregates; no downloadable table by variety |
| HuggingFace / Kaggle "pulse" | Various | n/a | n/a | Various | HF API | 1 | 1 | Found nothing useful outside OFF |

## 1. Open Food Facts

- **URL:** https://huggingface.co/datasets/openfoodfacts/product-database (file `food.parquet`, 8.02 GB) [V]. API: https://world.openfoodfacts.org/api/v2/
- **Owner:** Open Food Facts. **License:** ODbL for the database, AGPL-3.0 declared on the HF card [V].
- **Last update:** HF repo modified 29/10/2026 [V] (daily dump).
- **Size:** 4,882,161 products in total [V]; 1,292,692 with `countries_tags` containing `en:france` (none marked `obsolete`) [V].
- **Access used:** duckdb + httpfs reading only the required columns of the remote parquet, France filter, local export of 233 MB (deleted afterwards). Took about 20 min.
- **Key variables:** `ingredients_tags` (normalized taxonomy), `categories_tags`, `origins_tags`/`origins`, `manufacturing_places_tags`, `labels_tags`, `ingredients_n`, `nutriscore_grade`, `nova_group`, `environmental_score_grade`, `categories_properties` (CIQUAL/Agribalyse codes), `nutriments`, `unique_scans_n`, `brands`, `stores`.

### Audit [V] (products sold in France)

Overall completeness in France: origin (`origins_tags`) 6.4%, categories 49.4%, `ingredients_tags` 28.5%, computed Nutri-Score (a-e) 36.6%. Note: the pulse ingredient counts are a floor, because 71% of products have no parsed ingredients.

Products with a pulse in the ingredients (not obsolete):

| Flag | n products | declared origin | % FR among those declaring | % FR of total | any FR signal (origin, label or text) | ingredients (mean / median) |
|---|---|---|---|---|---|---|
| Any pulse (lentil, chickpea, faba bean, pea protein/flour/fibre, dry beans, lupin) | 12,069 | 17.5% | 47.3% | 8.3% | 27.4% | 21.9 / 17 |
| Lentil | 2,943 | 22.6% | 53.0% | 12.0% | 30.6% | 16.1 / 13 |
| Chickpea | 3,039 | 18.2% | 40.2% | 7.3% | 24.1% | 20.5 / 16 |
| Faba bean (faba) | 1,472 | 14.9% | 51.4% | 7.7% | 28.7% | 31.4 / 23 |
| Pea protein/flour/fibre | 3,233 | 16.2% | 51.0% | 8.3% | 33.5% | 23.8 / 19 |
| Dry beans (porotos secos) | 897 | 15.2% | 32.4% | 4.9% | 23.1% | 24.4 / 19 |
| Soy (reference) | 45,263 | | | | | |

By category (products where the pulse is the product):

| OFF category | n | declared origin | % FR among declaring | median ingredients | % NOVA 4 | % Nutri-Score A/B |
|---|---|---|---|---|---|---|
| en:legumes (all pulses) | 8,224 | 18.9% | 54.2% | 3 | 13.0% | 66.7% |
| en:lentils | 1,391 | 25.0% | 59.2% | 1 | 10.9% | 69.6% |
| en:green-lentils | 436 | 36.7% | 86.3% | 1 | 3.0% | 78.2% |
| en:chickpeas | 818 | 17.1% | 48.6% | 3 | 4.8% | 73.5% |
| en:canned-chickpeas | 279 | 23.3% | 44.6% | 3 | 9.0% | 87.8% |
| en:dried-split-peas | 171 | 30.4% | 73.1% | 1 | 0% | 74.9% |
| en:hummus | 1,153 | 6.0% | 31.9% | 13 | 14.1% | 21.5% |
| en:meat-analogues | 1,903 | 16.8% | 40.9% | 18 | 53.9% | 55.9% |
| en:plant-based-meals | 992 | 21.1% | 43.1% | 17 | 36.5% | 55.0% |

Most frequent origins in pulse-category products: France 847, Italy 74, EU 56, China 55, Canada 55, Turkey 44, USA 40 [V]. For lentils: France 353, "EU and non-EU" 52, EU 50, Canada 49, Turkey 36 [V].

Distribution in products with pulses in the ingredients: Nutri-Score A 2,716, B 1,753, C 3,121, D 1,611, E 689; NOVA 1: 1,238, NOVA 3: 2,798, NOVA 4: 7,260 [V]. 55% have an Agribalyse code (direct or proxy) via the category and 47.7% a CIQUAL code [V].

Labels: organic (`en:organic`) on 2,866 products with pulses; PDO only 28 and PGI 25 [V], so the pulse SIQO labels are barely tagged in OFF.

**Answer to the key question:** of the pulse products sold in France, only 17.5% declare origin; of those, 47% say France. Across the total, only 8% explicitly declare France origin (27% if any mention of France in a label or ingredient text is counted, a noisy upper bound). For "simple" pulses the share is higher (green lentil 86% FR among those declaring) and it drops in processed products (hummus 32%, meat analogues 41%). There is a strong selection bias: whoever has French origin to sell is the one who declares origin.

### Quality issues
- `origins` is at product level, not ingredient level: in "petit salé aux lentilles" (salt pork with lentils) it shows `fr:Porc origine France` [V]. For pulses in composite dishes you have to parse the ingredients text ("lentilles (origine France)").
- Some products have `origins_tags` filled and `origins` empty (tags inferred from other fields) [V].
- The `en:pea` flag mixes green pea (vegetable) and dry pea; I separated them (4,260 products with `en:pea` not counted as pulses).
- Many ghost products (few photos, no scans); `unique_scans_n` is useful to weight by relevance.
- Regional EAN duplicates and private labels.

**Relevance:** T3 8/10 (measures how "French" the shelf is and the market gap), T2 9/10 (ingredient lists, NOVA, Nutri-Score, price not included).

## 2. Ma Cantine (MASA, betagouv)

### 2a. National canteen register
- **URL:** https://www.data.gouv.fr/datasets/registre-national-des-cantines/ (id 6482def590d4cf8cea3aa33e); CSV `registre_cantines.csv` 26 MB [V]. Schema on GitHub betagouv/ma-cantine.
- **License:** Licence Ouverte 2.0 [V]. **Update:** daily (29/10/2026) [V].
- **Rows:** 66,346 restaurants [V]. Columns: SIRET, INSEE commune, EPCI, PAT (projet alimentaire territorial, local food plan), département, région, economic model, direct/concession management, production type (site, satellite), central kitchen SIRET, meals per day and per year, sector, ministry, `declaration_donnees_2021..2025` flags [V].
- **Missingness:** SIRET 4.2%, meals/year 6.5%, sector 1.5%, management 3.6% [V]. Sum of `yearly_meal_count`: 2.52 billion meals/year [V] (self-declared figure, not cleaned).
- **Canteens that declared** (per the register flags): 2,801 (2021), 8,941 (2022), 16,106 (2023), 33,604 (2024), 49,570 (2025) [V].

### 2b. Results of télédéclaration campaigns
- **URL:** https://www.data.gouv.fr/datasets/resultats-de-campagnes-de-teledeclaration-des-cantines/ (id 6482ed2ee3f9ec5215b41828). One CSV per year, 2021 to 2024 (no 2025 file yet) [V].
- **Rows:** 5,081 (2022), 10,317 (2023), 21,592 (2024) [V]. Mode SITE/CENTRAL_ALL/CENTRAL_APPRO.
- **Variables:** only `teledeclaration_ratio_bio` and `teledeclaration_ratio_egalim_hors_bio` plus canteen characteristics [V]. Median organic 2024: 12.8%, EGalim excluding organic 18.0% [V].
- **What is NOT there:** vegetarian menu frequency, protein diversification plan, vegetarian menu bases. These fields exist in the data model (`vegetarian_weekly_recurrence`: NEVER/LOW/MID/HIGH/DAILY; `vegetarian_menu_bases`: GRAIN = "céréales et/ou légumes secs" (cereals and/or dry pulses), SOY, CHEESE, EGG, READYMADE; `has_diversification_plan`; `diversification_plan_actions`) [V, source code `data/models/diagnostic_volet_diversification.py`], but they are not published per canteen.
- There is also no "pulses" family in the purchase amounts: the families are meat/poultry, seafood, etc. [NV, I did not read the whole purchase model].

### 2c. Public API
- `GET https://ma-cantine.agriculture.gouv.fr/api/v1/publishedCanteens/` returns 66,353 canteens [V], with `badges` per year (`appro`, `waste`, `diversification`, `plastic`, `info`, booleans) and, in the per-canteen detail, historical `approDiagnostics` with % organic, SIQO, EGalim meats, French meats, French seafood [V]. It does not include the diversification section detail, only the badge and `diversificationComments` (free text).
- `GET /api/v1/canteenStatistics/?year=2024`: 53,875 canteens, 33,769 télédéclarations, organic 11%, EGalim 29%, French meat/poultry 11% [V]. Does not carry vegetarian data.
- Counting `diversification` badges per canteen: I did not complete it. The API limits results to 30 per page (even if you ask for `limit=500`) and takes about 14 s per page [V], which means more than 2,000 requests and hours for the 66k canteens. If needed, paginate in the background during the event or filter by département.

### 2d. EGalim 2025 statistical report (2024 data)
- PDF: https://ma-cantine.agriculture.gouv.fr/static/documents/rapport-bilan-statistique-EGALIM_2025.pdf [V].
- School: 17,841 obligated restaurants that declared; 11,730 answered the vegetarian menu question (66%); 96.7% comply with the weekly vegetarian menu (94% in the previous cycle, out of 5,457) [V].
- State (daily vegetarian option): 1,622 obligated, 680 answered (42%), 65.8% comply [V].
- The large majority of schools serve exactly 1 vegetarian menu per week, no more [V, report text; the exact distribution is in charts, not in a table].
- Nothing on pulse volumes or their origin [V, grep with no results]. The 2026 campaign adds "a new focus on the origin of products" [F, agriculture.gouv.fr].

**Answer to the key question:** about 33,600 canteens declared 2024 data (≈50% of the register) and 49,570 have a 2025 declaration flag, but the per-canteen open data only includes % organic and % EGalim. Vegetarian data exists for ≈11,700 schools at canteen level within the platform, but it is only published as an aggregate (report) and as a badge. **There is no pulse purchase data or origin data at all.** That gap is precisely an opportunity.

**Relevance:** T3 7/10 (the institutional demand to map against supply), T2 9/10 (EGalim and protein diversification, like Ardoise).

## 3. CIQUAL 2025 (ANSES)

- **URL:** https://entrepot.recherche.data.gouv.fr/dataset.xhtml?persistentId=doi:10.57745/RDMHWY (replaces the 2020 version on data.gouv) [V]. Published 19/11/2025, Etalab 2.0 license [V].
- **Files:** XLSX 1.5 MB, XLS, XML (compo 69 MB) [V].
- **Size:** 3,484 foods × 84 columns [V]. Subgroup "légumineuses": 38 foods [V].
- **Examples [V]** (g/100 g, protein N×Jones / fibre / iron mg): dry green lentil 25.1 / 16.4 / 6.3; dry red (coral) lentil 27.7 / 15.4 / 6.3; dry faba bean 26.1 / 25 / 6.7; dry split pea 23.8 / 25.5 / 4.82; dry chickpea 20.5 / 12.2 / 4.31; dry lupin 36.2 / 18.9 / 4.36; dry white bean 23.4 / 15.2 / 10.4.
- **Missingness:** protein and lipids almost complete (<1% missing), but "-" in micronutrients (e.g. iron of frozen faba beans) [V].
- **Limitations:** generic food, no variety, origin or lot; does not cover isolated pea protein or industrial ingredients.
- **Relevance:** T3 6, T2 8. Useful for nutritional equivalences (pulse portion that replaces meat in a menu).

## 4. Agribalyse (ADEME)

### 4a. Agribalyse 3.2 (data.ademe datasets "agribalyse-31-*")
- **URLs:** synthèse https://data.ademe.fr/datasets/agribalyse-31-synthese, detail per stage, detail per ingredient. License Licence Ouverte 2.0 [V]. Files dated 29/01/2026 [V].
- **Size:** 2,451 real foods in the synthèse (the CSV has 14,956 lines, 12,505 empty) [V]; 8,882 rows in the per-ingredient detail [V].
- **Variables:** AGB code, CIQUAL code, group, LCI name, seasonality, air freight, packaging, preparation, DQR, single score EF 3.1 and 16 indicators (climate change, land use, water...) [V].
- **Pulses:** 36 foods in the "légumineuses" subgroup plus dishes (falafel, lentil soup, hummus, soy steaks) [V]. Climate change (kg CO2e/kg): dry lentil 0.581; dry chickpea 0.899; dry split pea 0.75; dry faba bean 0.858; dry white bean 0.448 [V]. Raw beef median 28.9; raw chicken 5.58 [V].
- **FR vs imported?** Not for pulses [V]: green, yellow and coral lentils have exactly the same values (0.581), i.e. a single proxy. Origin variants exist only for specific cases (mango by plane/boat, imported haricot vert by air, Gruyère IGP France) [V].

### 4b. Agribalyse 4 (synthèse, detail per stage and per ingredient)
- data.ademe ids `shxqzuee9i461wn9lmdsbnvr` etc., 2,455 foods, updated 02/06/2026 [V]. The description still says "v3.2" and the API does not expose a license [V].
- **Signs of a preliminary version:** DQR = 5 in 100% of rows, 15 foods with a negative single score (e.g. dry lentils −0.049) [V]. Dry lentil rises to 1.036 kg CO2e/kg and dry faba bean to 3.94 [V]. Do not use without reading the documentation.

**Relevance:** T3 7 (environmental argument for producing and eating French pulses, although without origin differentiation), T2 8 (comparing a meat menu vs a pulse menu).

## 5. INCA3 (ANSES)

- **URL:** https://www.data.gouv.fr/datasets/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-3/ [V]. Fieldwork 2014-2015, published 2017, files 2019-2021 [V]. License "notspecified" on data.gouv [V].
- **Files:** `conso-compo-alim.csv` 205 MB (consumption per food and occasion), `conso-gpe-inca3.csv` 1 MB (g/day per 44 groups), `description-indiv.csv` (weights), nomenclature, notice PDF [V].
- **Calculation [V]:** with weights `pond_indiv_adu_pop3`/`pond_indiv_enf_pop3`, group 22 "légumineuses" gives 7.7 g/day in adults (14.7% consumers on the surveyed days) and 3.9 g/day in children (11.7%). It excludes composite dishes (group 39 mixes potato, cereals and pulses) and it is an average of few 24-hour recalls, so it underestimates usual consumption. For comparison: the PNNS recommends pulses at least 2 times a week [NV].
- **Relevance:** T3 4, T2 7. Old demand baseline. INCA4 in progress [NV].

## 6. DECP: consolidated public contracts

- **URL:** https://www.data.gouv.fr/datasets/donnees-essentielles-de-la-commande-publique-consolidees-format-tabulaire/ (id 608c055b35eb4e6ee20eb325), `decp.parquet` 255 MB updated 29/10/2026, code https://github.com/ColinMaudry/decp-processing [V]. Licence Ouverte 2.0 [V].
- **Size:** 3,358,206 rows [V]. Variables: buyer (SIRET, category, commune, coordinates), supplier (SIRET, NAF, commune, distance to buyer), object, CPV, amount, procedure, `considerationsEnvironnementales`, `origineFrance`, dates [V].
- **Pulses [V]:** with CPV 032122* (dry pulses) or an object mentioning légumineuses/légumes secs/lentilles (excluding medical CPVs 31/33/38, because "lentille" is also an optical lens): 381 rows, 246 unique contracts, 134 buyers, since 2019. Per year (unique contracts): 7 (2019), 20, 30, 27, 31, 52 (2024), 63 (2025), 41 (2026 to October). Examples: Aubervilliers "LOT4 LEGUMINEUSES BIOLOGIQUES" €250k; Caisse des écoles Paris 20e "produits de 5e gamme bio à base de légumineuses en circuit court" (organic 5th-range pulse products, short supply chain) €1M; Metropolis of Lyon lot "fruits, légumes et légumineuses bio" (organic fruit, vegetables and pulses).
- **Quality:** amounts are maximum framework-agreement values, not actual purchases; duplicates per source (381 rows vs 246 uids); `origineFrance` empty in 78.6% of food contracts (CPV 03/15) [V]; pulses usually sit inside "épicerie" (grocery) lots without breakdown.
- **Relevance:** T3 6 (who buys, from whom and at what distance), T2 8 (canteen tenders; upward trend in pulse lots).

## 7. INAO: SIQO product reference

- **URL:** https://www.data.gouv.fr/datasets/referentiel-des-produits-sous-signe-officiel-didentification-de-la-qualite-et-de-lorigine-siqo/ CSV 1.1 MB, 31/12/2025, Licence Ouverte 2.0 [V]. 5,246 lines [V].
- **Dry pulses (category 42 "Légume sec") [V]:** AOP Lentille verte du Puy (protected designation of origin, green lentil from Puy), AOP Coco de Paimpol, IGP Lentilles vertes du Berry (protected geographical indication, green lentils from Berry), IGP Haricot de Castelnaudary, IGP Mogette de Vendée, IGP Lingot du Nord, IGP Haricot de Soissons, IGP Haricot tarbais, Label Rouge lentilles vertes (red label green lentils), haricots blancs, lingot, haricot; Lentillon champenois in process (PNT, national transitional protection).
- Geographic areas are in other INAO datasets (shapefiles) [V]. **Volumes, areas and number of producers are not in open data** [V for data.gouv]; they live in the INAO "fiches chiffres clés" (key figures sheets) or in the ODGs (organisations de défense et de gestion, producer bodies) [NV].
- **Relevance:** T3 6, T2 4.

## 8. Terres Inovia: pea and faba bean grain quality

- Annual "qualité des graines" sheets (survey since 2015 for Terres Univia, samples from organismes stockeurs). PDFs: pea 2025 and faba bean 2025 on terresinovia.fr [F]. The server returns 403/HTML to automated downloads; I could not read the PDF [V].
- Figures from the source snippet [F]: faba bean 2025: 28.4% protein on DM (dry matter), 76 samples, yield 26.8 q/ha, production 358,000 t. Pea 2025: 22.8% protein on DM, ~60% of lots compatible with human food. Pea 2022: 21.9%.
- **Limitation:** aggregates in PDF, no table by variety or by region available for download; microdata would have to be requested from Terres Inovia. Variety-level data is in the variety trials (myVar) [NV].
- **Relevance:** T3 9 (the "% of lots fit for human consumption" figure is the field-to-plate bridge), T2 4.

## 9. Other items reviewed

- **HuggingFace / Kaggle:** searches for "pulse", "lentil", "legume", "chickpea", "faba", "plant-based" on HF return nothing useful (lentil images for foreign-body detection, OWID protein supply datasets) [V]. The only relevant item on HF is OFF itself.
- **Ecolab (data.gouv):** "Part des cantines respectant les obligations EGalim" (share of canteens meeting EGalim obligations) by region/département/EPCI and "Surface de cultures en légumineuses" (pulse crop area) [V, exists; not audited in detail]. Useful to cross supply (area) and demand (canteens) at territorial level.
- **Municipal menus** (Antibes, Rezé, Anglet, Noé…) on data.gouv: day-by-day menus, some with detailed dishes [V, exist]. Few communes, heterogeneous formats.
- **CNRC (Conseil national de la restauration collective, national collective catering council):** protein diversification guides and vegetarian recipe sheets [NV, not audited]; they are PDFs, not datasets.
- **Open recipes:** I did not find an open French dataset of recipes with pulses in this pass [V for HF].

## Seed ideas

1. **"French origin" on the pulse shelf (T3/T2).** User: cooperatives, IGP/AOP bodies, Terres Univia, large retailers. Decision: in which categories (hummus, analogues, ready meals) there is the most gap in French supply, and for which brands. Essential AI: an LLM extracts the origin of each pulse ingredient from free text and from OFF label photos (today only 17.5% have structured origin), classifies products and estimates the pulse volume per product.
2. **Matching French supply with canteen tenders (T2 bridge to T3).** User: public buyers (caisses des écoles, hospitals) and regional pulse processors (legumeries). Decision: split lots and draft the tender specifications (cahier des charges) so that French/local pulses can win (separate lot, 5th range, criteria). Essential AI: classify the 3.36 M DECP contracts (free-text object) to detect pulse purchases hidden in grocery lots, and generate lots and clauses from the Ma Cantine register (meals/day, PAT) and from the SIQO/production zones.
3. **"French pulse" vegetarian menu assistant for canteens (T2, Ardoise style).** User: canteen cook or manager. Decision: a weekly menu that meets EGalim (≥1 vegetarian, "GRAIN" base instead of "READYMADE") with lower cost and CO2. Essential AI: menu generation with nutritional (CIQUAL), environmental (Agribalyse) and origin constraints, using real OFF products; natural-language explanation for the télédéclaration.
4. **Grain quality → food use (T3).** User: cooperative collecting pea/faba bean. Decision: which lots to allocate to human consumption (price premium) vs animal feed. Essential AI: predict food suitability (protein, split, defects) from grain images and parcel data. Risk: no open microdata (only Terres Inovia PDFs), so data would have to be obtained or simulated.
5. **Simplifying the ingredient list (T2).** User: French food SME. Decision: reformulate a meat analogue or hummus to move away from NOVA 4 (54% of analogues) and from a median of 18 ingredients, using French pulses. Essential AI: a model that proposes substitutions using the OFF database as a space of real industrial recipes and predicts Nutri-Score/Eco-score.

## Process note

- Scripts in `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/ds_food/scripts/` (extract.py, off.py, off3.py, mc.py, agb*.py, ciq.py, inca.py, decp*.py). Downloaded data was deleted at the end.
- OFF percentages are calculated over products with the `en:france` flag in `countries_tags` and not obsolete; the per-ingredient counts depend on the product having parsed ingredients (28.5% in France).
