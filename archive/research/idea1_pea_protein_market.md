# Idea 1: food-grade pea with yield and protein risk (market, verification and evaluation)

Desk research, 2026-10-30. Complements `track3_context.md`, `datasets/economics_markets.md`, `datasets/food_quality.md` and `datasets/agronomy_plant_health.md` (I don't repeat what is already there except where I correct it or re-verified it).

**Convention:** **[V]** I opened and read the primary source. **[S]** press or secondary source (or a search-engine snippet from a primary source I could not open). **[NV]** not verified, or my own calculation/hypothesis.

Method note: Terres Inovia blocks curl and the fetcher (403), but **I read the 2025 quality PDF and the July 2025 press release in full** by opening the site in Chrome and extracting the text with pdf.js. The EUR-Lex antidumping regulation returns an anti-bot challenge (empty 202), so for that case I read the European Commission's press release and the French Customs notice, not the full text of the regulation.

---

## 0. TL;DR for the team

1. **Protein is not the criterion that defines "food-grade" in pea.** In Terres Inovia's 2025 survey, the filter that limits human use is the **% of split grains (<1 %)**: only 55 % of lots meet it, versus 86 % for insect damage and 96 % for stained grains. That is where the "about 60 % of lots could meet the human food criteria" comes from. [V] Protein matters for the **extraction yield of the fractionator** (Roquette, Cosucra), not as a published acceptance threshold. I found no public minimum protein threshold or price grid per protein point for pea. [NV, negative search]
2. **There is a new, dated market window:** on 25/09/2026 the European Commission imposed definitive antidumping duties of **40,5 % to 67,1 %** on Chinese pea protein (>65 % protein), for 5 years; EU market of around **175 M€**. [V] European fractionators will need more European pea just when France fell from 150.000 ha (2023) to 98.000 ha (2025). [V]
3. **The sector itself (filière, supply chain) acknowledges a winter/spring problem for ingredients:** Pea4Ever (50 M€, 5 years) aims to "comprendre et corriger la moindre qualité des pois d'hiver sur les marchés ingrédients" [understand and correct the lower quality of winter peas on ingredient markets], with a multi-year pilot trial "pour objectiver les différences de transformation des types hiver et printemps" [to objectively establish the processing differences between winter and spring types]. [S, Pleinchamp 30/01/2026] This gives the pitch a very strong external anchor for the question "winter or spring?".
4. **There is no service that forecasts pea protein** (there is one for wheat: Arvalis' national forecast, Farmstar for nitrogen). Terres Inovia's OAD (outil d'aide à la décision, decision-support tool) for pea are for variety choice (Myvar) and aphanomyces risk (éva), not quality. [S]/[V]
5. **The direct economic value per hectare is modest** (human-food premium of ~30 €/t, about 135 €/ha in the Terres Inovia guide) [V mirror]; the big value is on the **buyer's** side (securing volume and quality for a plant that has already invested) and on the country side (replacing protein imports from China that are now taxed). The user who pays is the fractionator or the cooperative that sells to it, not the farmer.

---

## 1. What "human food / ingredients" buyers require

### 1.1 What defines a lot fit for human food (Terres Inovia 2025 survey) [V]

Source: "Qualité des graines 2025, Pois" [Seed quality 2025, Peas], Terres Inovia for Terres Univia, January 2026, 85 samples from grain collection organizations. https://www.terresinovia.fr/sites/default/files/2026-01/fiche_terres_inovia_qual_graines_pois2025.pdf (read in full via browser).

| Criterion | 2025 result | Reading |
|---|---|---|
| Protein | 22,8 % of MS (matière sèche, dry matter), production-weighted regional average | "teneur en protéines moyenne correcte" [average protein content is acceptable] |
| Split grains | **55 % of lots <1 %** ("utilisables en alimentation humaine" [usable for human food]), 39 % between 1-10 %, 6 % >10 % | Worse than 2024 due to grain that was very dry at harvest (12,3 % moisture) |
| Stained grains | 96 % of lots <1 %, 41 % with none | Very low disease pressure |
| Insect-damaged grains (mainly bruchid) | **86 % of lots <1 %** "et peuvent être utilisés en alimentation humaine" [and can be used for human food] | The damaged grains come mainly from Nouvelle-Aquitaine and Occitanie |
| Impurities before cleaning | ~70 % of lots <1 %; 3,5 % >10 % | Always cleaned before sale |
| Colour | 82,4 % yellow, 11,8 % green | "Les graines jaunes sont demandées spécifiquement pour une utilisation dans l'industrie agro-alimentaire" [yellow seeds are specifically requested for use in the agri-food industry]; green ones go to casserie or oisellerie [split-pea processing or birdseed] |
| Germinated grains | 0 % | They degrade visual quality for human use |
| Conclusion | "Environ 60 % des lots pourraient satisfaire les critères exigés en alimentation humaine. Tous les lots peuvent être utilisés en alimentation animale." [About 60 % of lots could meet the criteria required for human food. All lots can be used for animal feed.] | |

Notable data point from the same document: **of the half of lots whose destination was declared, 90,5 % went to animal feed and only 9,5 % to human food.** [V] Caveat: it is a small subsample (about 42 lots) and biased by which collector declared the destination; it does not contradict the balance (below), but it suggests that **the potential quality is not turning into human-food contracts**. That gap (60 % fit vs. a minority under contract) is precisely the gap Idea 1 can attack.

Rigor warning from the same PDF: high protein can be an artifact of disease. In Vendée there were samples at 28 and 32 % that "peuvent donc provenir de parcelles malades" [may therefore come from diseased plots] (ascochyta blight, "souvent responsable de teneurs en protéines élevées" [often responsible for high protein contents]). [V] And in the North/East, late sowings of winter pea due to November rains gave "mauvais enracinement, une mauvaise nodulation" [poor rooting, poor nodulation] and low protein. [V] A protein model has to handle this (outliers and sowing-date effect).

### 1.2 Fractionator requirements (Roquette, Cosucra)

- **Roquette Vic-sur-Aisne:** contracts through about fifteen grain collectors "sous un cahier des charges précis" [under precise specifications]; pays a premium (amount not published); target 100 % French origin, mainly Hauts-de-France and Champagne-Ardenne; critical criterion: contamination with wheat from the gluten-free market, "Les camions de pois qui arrivent chez nous, et comptent 2 grains de blé pour 100 g de pois sont refusés" [Trucks of peas that arrive at our plant and contain 2 wheat grains per 100 g of peas are rejected]. [S, La France Agricole 25/05/2018, updated 2022] https://www.lafranceagricole.fr/cultures/article/799802/roquette-a-besoin-de-pois-proteagineux
- Réussir (2018) lists Roquette's premium criteria: "qualité, volume, propreté physique du pois, sans OGM, traçable" [quality, volume, physical cleanliness of the pea, GMO-free, traceable], within a technical program launched in 2017. **No published protein threshold.** [S] https://www.reussir.fr/grandes-cultures/roquette-developpe-une-filiere-pois-pour-le-marche-des-proteines-vegetales
- **SCAEL (Eure-et-Loir) for Cosucra:** the specifications are "simple": recommended varieties and full traceability of interventions; "les agriculteurs peuvent bénéficier d'une prime supplémentaire par rapport au prix lié à l'alimentation animale" [farmers can receive an additional premium over the price linked to animal feed]. [V] Terres Inovia, 13/02/2023 (modified 05/03/2026): https://www.terresinovia.fr/fr/actualites/lalimentation-humaine-un-debouche-interessant-pour-le-pois
- **Implication for Idea 1:** the protein "target" in today's contracts is **indirect** (via the recommended variety). A threshold such as "≥ 23 % MS" is a design hypothesis, not market data. [NV] It should be presented as a "buyer-configurable threshold", and 22,7 % (2015-2024 average) used as a neutral reference.

### 1.3 Human-food premium vs. feed

| Data | Value | Status | Source |
|---|---|---|---|
| Terres Inovia 2025 guide: indicative price animal feed vs. human food | 250 vs **280 €/t** (+30 €/t), pea margin 810 → 945 €/ha (high potential) | [V] (germineo mirror, read in `economics_markets.md` §6.1) | https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/POIS-PROTEAG.-2025-Guide-culture-TERRES-INOVIA.pdf |
| Same guide: human outlets "sont mieux valorisés en termes de prix de vente que l'alimentation animale" [are better valued in terms of selling price than animal feed] | qualitative | [V] | same |
| Feed pea FOB Creil | 224-240 €/t (July-August 2026) | [S] (Argus via Pleinchamp, snippet) | https://www.pleinchamp.com/les-cours/grandes-cultures/40-pois-fourrager |
| Green food pea in Beauce | +45 % over feed pea | [S], date unclear | Réussir/La Dépêche (snippet) |
| Beuzelin contract (Sarthe), spring pea for human food | ~250 €/t indexed to Euronext wheat, ~40 q/ha | [S] 04/03/2021 | https://www.reussir-agri72.fr/25-ha-de-pois-pour-lalimentation-humaine |
| €/protein-point grid for pea | **Not found** | [NV] | For wheat there is indeed an obligation for a "barème de prix en fonction du taux" [price scale based on the rate] (interprofessional agreement, ref. 11,5 %) [S] |

### 1.4 Historical series of national average protein (pea, % MS) [V]

From the same Terres Inovia 2025 sheet:

| 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | Average 2015-2024 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 22,9 | 23,1 | 22,4 | 21,7 | 22,2 | 21,6 | 22,7 | 21,9 | 24,4 | 24,1 | 22,8 | 22,7 |

By basin in 2025 (PDF text): "supérieures à 23 % de la MS dans les bassins Ouest, Sud et Centre-Ile-de-France" [above 23 % DM in the West, South and Centre-Ile-de-France basins], North/Normandy 22,7 % and East 21,6 %. [V] The map has five boxes (n=14 mean 23,7; n=25 mean 23,5 range 20,1-32,0; n=22 mean 23,3; n=11 mean 22,7; n=13 mean 21,6), but the text extraction loses which basin each box corresponds to beyond North and East: check visually before citing them.

**National year-to-year range: 21,6 to 24,4 (2,8 points); range between basins in one year: ~2 points.** In other words, variability between years and places is of the same order as any reasonable threshold: there is signal for a probabilistic model. [NV, my reading]

### 1.5 Pea use balance (Terres Univia, November 2025) [V]

| (kt) | 2024/25 | 2025/26 (forecast) |
|---|---|---|
| Production | 345 | 349 |
| Area (kha) | 124 | 98 |
| Yield (q/ha) | 27,9 | 35,6 |
| Imports | 44 | 40 |
| Animal feed (industrial and on-farm) | 106 | 77 |
| **Human food and ingredients** | **140** | **140** |
| Exports (total) | 131 | 132 |
| of which to Belgium ("alimentation animale et ingrédients alimentaires" [animal feed and food ingredients]) | 55 | 55 |

Source: Terres Inovia 2025 sheet (table "France : bilan d'utilisation du pois" [France: pea use balance]). The 55 kt to Belgium are very likely Cosucra (Warcoing, 10 km from the border) [NV]. FranceAgriMer gives a different figure for **pea + faba bean**: 146 kt human vs. 62 kt processed by the compound feed industry in 2024/25, and Belgium as the first client of French pea with 91 kt/year on average over 2020/21-2024/25 (45 % of exports). [V] https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf

**Why the figures don't add up:** FranceAgriMer counts only what is processed by the compound feed industry (no on-farm consumption) and adds faba bean; Terres Univia counts industrial + on-farm feed and only pea. [V the definitions at the foot of each table; the reconciliation is mine, NV]. Pleinchamp (Pea4Ever) gives another breakdown of destination for 2024/25: 52 % human, 40 % animal, 8 % seed. [S] The 2025 guide gives (by area, practices survey 2023): ~60 % animal, ~25 % human, ~15 % seed. [V] **For the pitch: "by volume, already more than half of French pea's domestic use is human/ingredients (140 of 242 kt in 2025/26)".**

---

## 2. Market size and actors

### 2.1 EU antidumping on Chinese pea protein [V]

- European Commission, 25/09/2026: definitive duties of **40,5 % to 67,1 %**, **5 years**; provisional duties in force since 29/04/2026; the EU pea protein market is worth "some €175m"; uses: human food, animal feed, pet food, aquaculture. Implementing Regulation (EU) 2026/2101. https://policy.trade.ec.europa.eu/news/commission-acts-against-imports-pea-protein-china-2026-09-25_en
- French Customs, notice 2026-134: product = pea protein ">65 % de protéines sur la base du poids sec" [>65 % protein on a dry-weight basis], yellow and green, powder or liquid, textured or not; entry into force 26/09/2026. [V] https://www.douane.gouv.fr/sites/default/files/2026-09/25/2026-134%20Avis%20aux%20importateurs%20de%20prot%C3%A9ine%20de%20pois%20originaire%20de%20la%20R%C3%A9publique%20populaire%20de%20Chine.pdf
- Opening: 29/08/2025 after a complaint by the "Ad Hoc Coalition of Union Pea Protein Producers" (filed in July 2025). [S] (MLex, Global Trade Alert)
- Company rates: Yantai Shuangta 67,1 %, remaining cooperating companies 40,5 %. [S] (Lovguiden). Provisional rates up to 67,4 % according to Réussir/MLex. [S]
- The FOP (French oilseed and protein crop producers) supported the measures; Huel and the Chinese CFNA opposed them. [S] (Brussels Times)
- Circumvention risk: Expana (March 2026) reports suspicions that China is redirecting production via Thailand, Malaysia and Indonesia. [S]
- **I could not read China's volumes or market share** (EUR-Lex blocks access). Pending if someone opens it by hand: regulations 2026/916 (provisional) and 2026/2101 (definitive), sections "Union consumption" and "imports from the country concerned".
- Precedent: Canada imposed duties on Chinese pea protein in 2024 after a complaint from **Roquette Canada** and Nutri-Pea. [S] (CBSA / Canadian tribunal)

### 2.2 Roquette, Cosucra and others

| Actor | Data | Status |
|---|---|---|
| Roquette Vic-sur-Aisne (Aisne) | Capacity from 80 kt → 125 kt of pea/year (2018-2020); +40 M€ in 2015 and +40 M€ 2017-2020; pea protein for human food since 2005 (Nutralys) | [S] 2018 (Réussir, LFA). **I found no 2024-2026 figures.** |
| Roquette, sourcing | Target 100 % France; ~15 grain collectors; "más de 2.000 productores" [more than 2.000 producers] | [S] (Réussir, snippet; LFA 2018) |
| Roquette Canada (Portage la Prairie) | 125 kt of yellow pea/year | [S] |
| Cosucra (Warcoing, Belgium) | Pisane protein + chicory fiber; sources from Belgian and French farmers; Sofiprotéol (Avril) is a shareholder; 200 M€ plan 2023-2030 | [S] |
| French exports to Belgium | 91 kt/year of pea (5-season average), 55 kt in 2024/25 in the Terres Univia balance | [V] |
| Sotexpro (Bermericourt, Marne) | Textured pea (Texta Pois), co-developed with Roquette | [S] |
| Lantmännen (Sweden) | New pea isolate plant, >40 kt of pea/year, EIB loan | [S] |
| Market size (consultancies) | Europe: 0,48 MdUSD (Mordor 2025) vs 0,85 MdUSD (MarketsandMarkets 2024): do not use | [S], contradictory |

**Figure to use in the pitch:** 175 M€ (Commission). [V] Raw material order of magnitude [NV, calculation]: a 125 kt pea plant with 22,8 % protein has ~28 kt of incoming protein; each protein point in the grain (+4,4 % relative) is ~1.250 t more protein per year in the raw material.

### 2.3 Programs and targets

- **Pea4Ever / GIE PeaBoost** (GIE: economic interest group; Limagrain, Florimond Desprez, RAGT, with Sofiprotéol; INRAE, Terres Inovia, FNAMS, GEVES): ~50 M€ over 5 years, 50 % public; first subsidy of 5 M€; targets: +1 t/ha, multi-stress resistance (bacteriosis, aphanomyces, viruses, aphids, ascochyta, bruchid), drought, frost, and the point about lower quality of winter pea for ingredients. [S] Pleinchamp, R. Lecocq, 30/01/2026: https://www.pleinchamp.com/actualite/pois-proteagineux-pea4ever-or-never. Terres Inovia lists the project with 10,3 M€ and 36 months (different scope). [S]
- **Sector target:** 300.000 ha of pea. [S] (Réussir/Terre-net, snippet)
- **Cap Protéines+ (2024-2027):** coordinated by Terres Inovia with Arvalis, Idele, Ifip, Itavi and Terres Univia, 117 partners. [V] press release 31/07/2025.
- The July 2025 press release mentions "démonstrateurs territoriaux de production et de valorisation du pois" [territorial demonstrators for pea production and processing] funded by the interprofessional body. [V] I did not find the detail: **possible pilot channel for Idea 1**. [NV]

---

## 3. Why farmers drop pea

| Brake | Evidence | Status |
|---|---|---|
| Yield instability | Pea4Ever: yields "très variables" [very variable] within and between years; average yield fell from ~50 to ~30 q/ha over decades; ~700.000 ha at the end of the 1980s | [S] Pleinchamp 2026 |
| Bad winter year 2024 | Areas down to 98 kha "à la suite des mauvaises performances du pois d'hiver en 2024" [following the poor performance of winter pea in 2024] | [V] 2025 quality sheet |
| Sowing date (spring) | 2025: 40-55 q/ha with early sowings vs **20-30 q/ha** with late sowings | [V] Terres Univia/Terres Inovia/FOP press release, 31/07/2025 (https://www.terresinovia.fr/sites/default/files/document_library/20126/437704/726505/2024_07_31_cp_pois_hiver_r%C3%A9colte_2025.pdf) |
| Heat/drought at flowering | In a warmer, drier scenario, simulated yield of spring pea -28 % vs -14 % for winter pea (INRAE); winter pea partly escapes end-of-cycle stress but suffers frost | [S] OCL 2017 |
| Aphanomyces | "la maladie tellurique la plus préjudiciable sur pois" [the most harmful soil-borne disease on pea], present in all areas except very calcareous soils in the south and Champagne chalk; OAD éva + infection potential test | [V] 2025 guide |
| Price | Indexed to wheat and soybean meal; ~50 €/t gap to close | [S] |
| Policy | Coupled support revised in each PAC (Politique agricole commune, Common Agricultural Policy) (100-130 €/ha) | [S]/[V] guide |
| Logistics | Poor aggregation of volumes, variable flows for collectors and fractionators | [S] Pea4Ever |
| Margin | In 2024/25 "les marges obtenues en pois sont comparables à celles du blé tendre" [margins obtained on pea are comparable to those of soft wheat]; preceding-crop effect +140 to 200 €/ha of gross margin in the following wheat | [V] press release 31/07/2025 |

### 3.1 Why the areas don't match

| Figure | Scope | Status |
|---|---|---|
| 150 kha (2023), 124 kha (2024), 98 kha (2025) | **Pure** protein pea, Agreste estimate cited by Terres Univia/Inovia | [V] |
| 150 kha in 2026 (-7,4 %), 31,0 q/ha, 464 kt | Ministerial forecast as of 1/7/2026, "pois protéagineux **purs ou mélangés**" [protein pea, pure or mixed] | [S] Pleinchamp 16/07/2026 |
| ~162 kha in 2025 implied (150 / 0,926) and ~586 kt | Same scope "purs ou mélangés" [pure or mixed] | [NV] calculation |
| 166 kha (Eurostat 2024) | Probably includes cereal-legume mixtures counted as pea | [NV] |
| RPG (Registre parcellaire graphique, graphic parcel register) 2024: PPR 17.347 + PHI 7.196 parcels; MPC 9.365 mixed-crop parcels | CAP declaration, separate codes | [V] (`agronomy_plant_health.md`) |

**Proposed explanation [NV]:** the difference of ~60 kha between "pure" (98 kha) and "pure or mixed" (~160 kha) comes from pea-cereal mixtures, largely on-farm self-consumption for livestock. **For Idea 1 use pure pea only** (the one that goes to fractionation), i.e. the Terres Univia/Agreste pure series or the RPG PPR (spring) and PHI (winter) codes. Bonus: the RPG separates winter and spring by parcel, which is exactly Idea 1's decision variable.

---

## 4. Existing tools and competition

| Tool | What it does | Does it forecast pea protein or quality? | Status |
|---|---|---|---|
| Terres Inovia **Myvar** | Variety choice (includes winter/spring pea), free of charge, funded by the CVO (cotisation volontaire obligatoire, interprofessional levy); criteria: earliness, resistances, yield | No (shows average varietal protein, not the probability at a place/year) | [S] |
| Terres Inovia **éva** | Aphanomyces risk (low/high) by département (French administrative department), history, soil, irrigation | No | [V] 2025 guide |
| Terres Inovia guide | Varietal tables with "teneur en protéines" [protein content] by class | No, it is static | [V] |
| BSV protéagineux (BSV: bulletin de santé du végétal, plant health bulletin) | Weekly pest alerts | No | [V] |
| Arvalis (wheat) | National wheat protein forecast before harvest (crop models + measurements + experts; 11,6 % forecast in 2024) | Wheat only | [S] |
| **Farmstar** (Airbus/Arvalis) | Satellite + models for nitrogen in wheat, barley, rapeseed; claims better protein | Cereals/rapeseed only | [S] |
| xarvio, Wanaka, MesSatimages | Fungicide and nitrogen in cereals/rapeseed | No legumes | [S] |
| STICS (INRAE) | Crop model that simulates pea (N, yield) | Research, not a service | [S] |
| ML research | Poznań 2025: neural network for pea protein with climate, phenology and management (RMS 0,84 vs 2,70 for regression); Italy: genomic prediction of protein; NDSU: multi-trait multi-environment | Polish/Italian/US, not France, not a service | [S] |
| Fractionators | I found no public evidence that Roquette or Cosucra forecast the quality of their supply | Unknown | [NV] |

**Gap:** no one today delivers, before contracting, a **probability by department × type (winter/spring) × climate scenario** of reaching target yield and protein for pea. The closest are Myvar (static) and Pea4Ever's research (genetics, not supply logistics). [NV, from a negative search]

---

## 5. Business model and willingness to pay

| Benchmark | Value | Status |
|---|---|---|
| Unéal ODACIO 2026 (cooperative OAD package) | From 300 €/year + 12 €/ha, capped at 400 ha | [S] https://uneal.com/INTERSHOP/static/WFS/ADVITAM-Site/Uneal/ADVITAM-Uneal/fr_FR/Nos%20services/Plaquette_ODACIO_2026.pdf |
| Farmstar | 8-13 €/ha (old figures) | [S] |
| MesSatimages (Meuse Chamber of Agriculture) | 8 €/ha | [S] |
| Human premium vs. feed | ~30 €/t (≈135 €/ha at 45 q/ha) | [V] guide |
| Grain collectors | 477 (117 cooperatives, 360 négociants [traders]); ~12.400 protein-crop growers delivering in 2024 | [V] FranceAgriMer |

**Who pays (recommendation):** the **fractionator** (Roquette, Cosucra, or a new entrant such as Lantmännen) as an annual "supply intelligence" license, and secondly the **cooperative** that sells to them (SCAEL, Vivescia, Noriap, Axereal, Uneal) as a module within its OAD package. The farmer does not pay directly: they receive the recommendation (type, date, contract) via their technical advisor.

**Illustrative price [NV]:** 2-5 €/t contracted, or 5-10 €/ha contracted. With ~100 kha of pure pea and perhaps 40-50 % contracted for human food, the addressable market in France is **0,2 to 0,5 M€/year**. It is small: viability depends on extending it to faba bean (Egypt, milling) and lentil/chickpea, or on selling it to European fractionators who also buy in Belgium, Germany, the Netherlands and the Baltics.

**Value per protein point [NV]:** for the fractionator, +1 protein point in the grain is +4,4 % incoming protein per tonne at the same grain cost. If the plant's margin depends on extraction yield, that is worth much more than the 30 €/t premium the farmer receives. **I found no public price per point**, so in the pitch this goes as a hypothesis to validate with Roquette or Cosucra.

**Adoption path [NV]:** (1) pilot with a cooperative that already contracts for human food (SCAEL/Cosucra is the documented case), using its historical lots + Pea_dataset; (2) integration as a "quality" layer on top of Myvar or within Terres Univia's territorial demonstrators; (3) licensing to fractionators.

---

## 6. Impact numbers (illustrative, all [NV] except the inputs marked)

Inputs: production 349 kt on 98 kha [V]; 60 % of lots fit for human food [V]; human use + ingredients 140 kt [V]; exports to Belgium 55 kt [V]; premium +30 €/t [V]; early vs. late spring sowings 40-55 vs. 20-30 q/ha [V]; preceding-crop effect +140-200 €/ha [V]; legume mitigation 636 kg CO2e/ha (Pellerin et al. 2013, INRA) [S]; -20 to -60 kg N/ha in the following crop and +6-12 q/ha in wheat after pea [V guide].

1. **More food-grade tonnage:** if contracting in the right department/type raises the share of lots meeting the criteria from 60 to 70 %, with 349 kt that is **~35 kt more fit for human food**, on the order of 1 M€/year of premium for farmers at 30 €/t. [NV]
2. **Less area lost to a poor choice:** avoiding that, for example, 10 % of spring pea (~6 kha) falls in the 20-30 q/ha band instead of 40-55 recovers ~15 q/ha × 6 kha = **~9 kt of grain**, ~2,5 M€ at 280 €/t. [NV]
3. **Import substitution:** with antidumping duties, every 10 kt of extra French pea fractionated is ~2,3 kt of contained protein, on the order of 2 kt of isolated/concentrated protein that does not need to be imported. [NV]
4. **Climate:** going from 98 to 150 kha of pure pea (+52 kha) would avoid ~33 kt CO2e/year using INRA's average factor of 636 kg CO2e/ha. [NV with S input]
5. **Farmer income:** the strong argument is not the premium but the rotation: margin comparable to wheat + 140-200 €/ha in the following wheat [V], and Idea 1 lowers the risk that today makes them abandon it.

---

## 7. Evaluation of idea 1

| Criterion | Score | Why |
|---|---|---|
| Innovation | **6/10** | There is no probabilistic forecast of pea protein + yield to decide contracts (there is one for wheat). But G×E models of protein are already published, and Pea4Ever works on the winter/spring difference from the genetics side. The novelty is the **use** (sourcing decision), not the model. |
| Fit with Track 3 | **8/10** | Plant protein for human consumption, farmer income, sovereignty (EU antidumping dated September 2026). Risk: the jury may confuse protein pea with "feed"; say upfront that by volume more than half of domestic use is human/ingredients. |
| Impact fit | **6/10** | Direct numbers are modest (1-3 M€/year of premium/yield in France). The strong part is the story: sovereignty + antidumping + 35 % drop in area. |
| Economic viability | **5/10** | Few buyers (2-3 fractionators, ~15-20 cooperatives that contract for human food), small addressable market in France; viable as a B2B module or if extended to faba bean, lentil and chickpea. In its favor: a concentrated buyer with a clear sourcing pain point. |

Weak points to anticipate with the jury:
- **"Protein is not the rejection criterion."** Answer: you're right, so the model predicts yield × protein (tonnes of protein per hectare, which is what the fractionator cares about) and the agronomic risk; the 60 % fit is limited by split grains and bruchid, which are post-harvest and location-driven (bruchid in the south).
- **Trial data, not farm data** (Pea_dataset: average yield 49,5 q/ha vs. ~30-35 national). Answer: the model gives relative probabilities between departments and types, calibrated against the Agreste departmental series.
- **Anonymous genotypes.** Answer: we decide type and area, not variety; the traits (earliness, Hr, cold tolerance) are included.
- **High protein from disease** (ascochyta). It has to be filtered out or modeled.

## 8. Sharpened proposal

- **User:** agronomic sourcing manager at a pea fractionator (Roquette Vic-sur-Aisne or Cosucra profile), or the protein-crop lead at a cooperative that contracts for them (SCAEL profile).
- **Decision:** in August-September (winter pea contracts) and December-January (spring): **in which departments and with which type (winter or spring, and sowing window) to contract X tonnes** to secure the plant's protein volume with probability ≥ 80 %.
- **Output:** a department-level map of P(yield ≥ target and protein ≥ buyer target), with intervals, for winter vs. spring, plus the "protein tonnage at risk" of the contracted portfolio.
- **Essential AI:** G×E model with climate by growth stage (heat and drought at flowering, frost in winter) over 4.230 yield records and 3.326 protein records from the Pea_dataset; quantile or Bayesian regression for the uncertainty; validation by leaving one year out (2021 as the bad year).
- **Pitch hook:** *"Since 26 September, Europe charges up to 67 % on Chinese pea protein. French plants need French pea, but France lost a third of its area in two years, and the buyer only finds out in July whether its pea is usable. We tell them in September, when they sign the contract."*

---

## Main sources

- Terres Inovia, Qualité des graines 2025 Pois (read in full): https://www.terresinovia.fr/sites/default/files/2026-01/fiche_terres_inovia_qual_graines_pois2025.pdf
- Terres Univia/Terres Inovia/FOP, press release 31/07/2025: https://www.terresinovia.fr/sites/default/files/document_library/20126/437704/726505/2024_07_31_cp_pois_hiver_r%C3%A9colte_2025.pdf
- Terres Inovia, "L'alimentation humaine, un débouché intéressant pour le pois" [Human food, an interesting outlet for pea]: https://www.terresinovia.fr/fr/actualites/lalimentation-humaine-un-debouche-interessant-pour-le-pois
- European Commission, antidumping on pea protein (25/09/2026): https://policy.trade.ec.europa.eu/news/commission-acts-against-imports-pea-protein-china-2026-09-25_en
- French Customs, notice 2026-134: https://www.douane.gouv.fr/sites/default/files/2026-09/25/2026-134%20Avis%20aux%20importateurs%20de%20prot%C3%A9ine%20de%20pois%20originaire%20de%20la%20R%C3%A9publique%20populaire%20de%20Chine.pdf
- FranceAgriMer, protein crop sector sheet 2026: https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf
- Pleinchamp, Pea4Ever (30/01/2026): https://www.pleinchamp.com/actualite/pois-proteagineux-pea4ever-or-never
- Pleinchamp, 2026 forecasts (16/07/2026): https://www.pleinchamp.com/actualite/moisson-2026-rendements-en-baisse-jachere-en-hausse
- La France Agricole, Roquette (2018/2022): https://www.lafranceagricole.fr/cultures/article/799802/roquette-a-besoin-de-pois-proteagineux
- Terres Inovia, pea guide 2025 (mirror): https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/POIS-PROTEAG.-2025-Guide-culture-TERRES-INOVIA.pdf
