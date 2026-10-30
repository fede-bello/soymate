# Datasets on economics, markets, trade and farm income (Track 3, protein sovereignty)

Audit done on 29/10/2026. Convention: **[V]** I verified it myself by downloading or querying the API; **[F]** I read it at the source (official or technical document); **[NV]** not verified (comes from a search engine, memory, or a press article without opening the primary source).

Already audited by others (not repeated here): Agreste SAA long departmental series and the FranceAgriMer protein crops sheet 2026. See `research/*.md`.

Hackathon rule respected: exploration only (download, counts, tables). No models. Downloaded data was deleted at the end.

## Summary in 10 points

1. **Lentil: France imports ~40 kt/year for ~46 M€ (2023-2025 average), exports ~5 kt.** Net imports 34-38 kt/year in 2023-2025, +25-30% vs 2015 (31.8 kt). Canada 46% of volume, Belgium 32% (re-export hub, the true origin is hidden) [V, Comext].
2. With 2025 production of ~45 kt (Terres Univia via `track3_context.md`), apparent self-sufficiency in lentil is around 55% [own calculation, production NV].
3. **Chickpea: France is almost a net exporter** (imports 13 kt, exports 16 kt, 2023-25 average). The gap is not in the grain but in processing (canned, flours) [V].
4. **Dry bean (CN 07133390): imports ~32 kt/year, ~40 M€; exports ~5 kt.** Plus prepared/canned bean (CN 20055100): imports 30-36 kt/year, 36-44 M€ [V].
5. Substitutable gap in dry grain (lentil + dry bean, 2023-25 average): **gross imports ~73 kt and ~86 M€/year; net of exports ~63 kt and ~70 M€/year**. At 15 q/ha this would be ~42,000 ha of pulses for human food, on the order of the current lentil area [own calculation on Comext; assumed yield].
6. **Producer price paid (FranceAgriMer, conv.): lentil 854 / 873 / 806 €/t** (marketing years 2023/24, 24/25, 25/26) vs **soft wheat 205 / 194 / 170 €/t**, pea 247 / 275 / 222, faba bean 257 / 273 / 231 [V].
7. Import unit value of lentil 1.07-1.17 €/kg (2023-25) vs ~0.85 €/kg at the producer: there is ~200-300 €/t of margin for cleaning, grading, logistics and branding [V, calculation].
8. Reference gross margins (Terres Inovia): **winter pea 810 €/ha (250 €/t, feed) to 945 €/ha (280 €/t, human food) vs wheat 1,025 €/ha** on high-potential soil; with the preceding-crop effect, the wheat that follows pea rises to 1,189 €/ha [F]. Conventional chickpea: 505 €/ha at 15 q/ha and 500 €/t; 1,155 €/ha at 20 q/ha and 700 €/t [F]. Lentil: operating costs 518 €/ha [F].
9. Coupled aid "légumineuses à graines" (grain legumes): 104.2 €/ha (2023), **122 €/ha (2024 and 2025)** [F/NV, see section 7]. Individual CAP 2023-27 beneficiaries only via CASD (restricted access).
10. Agence Bio publishes organic area by department and crop 2008-2025: **organic lentil ~14,100 ha, organic chickpea ~7,600 ha, organic faba bean ~21,700 ha in 2025** (lower bound, 37% of cells under statistical secrecy) [V].

## Summary table

| Dataset | Owner | Coverage | Granularity | License | Access | Relevance (1-10) | Main limitation |
|---|---|---|---|---|---|---|---|
| Eurostat Comext DS-045409 (EU trade by CN8) | Eurostat (data from Douane) | 1988-2025 annual + monthly, FR vs ~180 partners | CN8 × partner × flow × month/year | Eurostat reuse (CC BY 4.0) | JSON API, no key | **10** | Partner = consignment country; Belgium/Netherlands hide the true origin |
| Douane: national foreign trade statistics | DGDDI (French customs) | Monthly, CN8 × country | NC8 × country × month | Licence Ouverte v2 | Zips on lekiosque / ODS API on data.economie.gouv.fr | 7 | ODS mirror is frozen (Mar-2023 to Mar-2024); intra-EU series break in 2022 (EMEBI) |
| FranceAgriMer: average prices paid to producers (quarterly) | FranceAgriMer | 2004/05-2025/26, national | Species × quarter × marketing year | LO v2 on data.gouv, but the xlsx says "tous droits réservés, mention de la source" (all rights reserved, cite the source) | Direct xlsx | **9** | Lentil only from 2023/24; no chickpea or dry bean; national, no regions |
| Terres Inovia crop guides (pea 2025, chickpea 2023, lentil 2023) | Terres Inovia | France, indicative examples | Crop × yield × price | Documentary use | PDF (site with anti-bot, mirror germineo.com) | **8** | "Indicative" margins, not observed; lentil with costs only, no margin |
| Coupled pulse aid (amounts) | MASA / arrêtés (ministerial orders) in JO | 2023-2025 | € /ha, national | Public | Arrêtés, press | 6 | No hectares or beneficiaries published |
| CAP beneficiaries (transparency) | ASP / MASA | 2023-27 microdata | Beneficiary × intervention | Restricted | CASD (with authorization) | 3 | Not accessible in 20 h |
| RICA (French FADN) / EU FADN Public Database | SSP Agreste / DG AGRI | 2004-2023/24 | OTEX × size class × region (aggregate) | Public aggregate; microdata via CASD | Qlik dashboards, DRAAF PDFs | 5 | Does not isolate pulses; restricted microdata |
| Agence Bio: areas by production, by dept | Agence Bio | 2008-2025 | Dept × production (lentil, chickpea, faba bean, pea, dry bean) | LO v2 | Direct CSV (224 KB) | 7 | 37% of cells "NC" due to statistical secrecy |
| Agence Bio: organic parcels declared to CAP (RPG bio) | Agence Bio / ASP | 2019-2023 | Parcel | LO v2 | Zip 400-500 MB | 6 | Heavy; organic only |
| Agence Bio: organic operators | Agence Bio | Current | Operator (SIRET, activities) | LO v2 | CSV 8.5 MB | 5 | No volumes |
| FranceAgriMer: collecte par département, ASP surfaces, RNM | FranceAgriMer | Varies | Dept × species × marketing year | LO v2 | Visionet (JS pages, manual download) | 6 | Portal hostile to scripts; content not verified |
| EU agri-food data portal (cereal prices) | DG AGRI | Weekly, 2000s-2026 | Market (Rouen, La Pallice) × product | EC reuse | JSON API, no key | 5 | No pulses; useful for the comparison wheat |
| Eurostat apri_ap_crpouta (sale prices) | Eurostat | 2000-2024 | Country × product | CC BY 4.0 | API | 2 | France has not reported pulses since 2017 |
| Géorisques ICPE (silos, rubrique 2160) | MTE / BRGM | Current | Facility with coordinates and capacity in m³ | LO v2 | JSON API, no key | 6 | Rubriques must be filtered client-side; does not say which grain |
| INCA3 consumption | ANSES | 2014-2015 | Individual × food | Not specified | CSV on data.gouv (204 MB) | 4 (covered by another agent) | Old; pulses rare in 24-hour recall |
| Open Food Facts (FR supply proxy) | OFF | Current | Product | ODbL | API | 3 | API down on audit day |

---

## 1. Eurostat Comext DS-045409: France's foreign trade by CN8 code (core dataset)

- **URL:** API `https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409?format=JSON&freq=A&reporter=FR&product=07134000&flow=1&indicators=QUANTITY_IN_100KG&time=2024`. Web explorer: https://ec.europa.eu/eurostat/comext/newxtweb/
- **Owner:** Eurostat; the data is transmitted by French customs (DGDDI). **License:** Eurostat reuse policy (CC BY 4.0) [F].
- **Coverage:** 1988 to 2025 complete; 2026 months partial. Last dataset update: **16/10/2026** (`updated` field of the response) [V].
- **Granularity:** reporter × partner (country, plus aggregates `WORLD`, `EXT_EU27_2020`, `INT_EU27_2020`, `EXT_EA`...) × CN8 × flow (1 import, 2 export) × indicator (`VALUE_IN_EUROS`, `QUANTITY_IN_100KG`, `SUPPLEMENTARY_QUANTITY`) × period (A annual, M monthly) [V].
- **Access:** GET without key, JSON-stat 2.0. One CN8 × 11 years × all partners × 2 flows × 2 indicators takes ~10 s and returns 500-3,000 cells [V]. Heads up: the JSON-stat comes as a flat `value` dict indexed by position; the coordinates have to be rebuilt with `size` (I did it in a 40-line script).
- **What I downloaded [V]:** FR, 2015-2025, 14 CN8 codes of 0713 (dry pulses) and 5 for preparations (20054000, 20055100, 20055900, 11061000, 07108095). 23,862 rows for 0713, 181 distinct partners (172 countries + 9 aggregates).

### Audit [V]

- **Units:** quantity in **100 kg** (divide by 10 for tonnes), value in current euros (CIF on imports, FOB on exports, per the Comext methodology [F]).
- **Missing values:** absent cells = zero or confidential. For small codes (07133400 bambara, 07133500 cowpea) some years are NaN. Lentil, chickpea, dry bean and pea have all 11 years complete.
- **Consistency:** `WORLD` = `INT_EU27_2020` + `EXT_EU27_2020` adds up exactly in the rows I checked (e.g. lentil 2023: 13,762 + 27,174 = 40,936 t).
- **Useful CN8 codes** (2025 combined nomenclature): 07131010 pea for sowing, **07131090 dry pea**, **07132000 chickpea**, 07133100 black gram (vigna mungo), 07133200 adzuki, 07133310 dry bean for sowing, **07133390 common/kidney bean**, 07133500 cowpea, 07133900 other beans, **07134000 lentil**, **07135000 faba bean and forage faba bean**, 07136000 pigeon pea, 07139000 other pulses. Preparations: **20055100 prepared beans (canned)**, 20054000 prepared peas, 11061000 pulse flour.
- **Joinability:** it has no geographic dimension within France, so it does not join with SAA or RPG by department. It joins by crop and year (CN8 ↔ SAA crop) and by price (unit value €/kg ↔ FranceAgriMer price).

### Main series (France, all partners)

**Lentil (CN 07134000)**

| Year | Imports t | of which extra-EU t | Imports M€ | Exports t | Exports M€ | Balance t (X-M) | €/kg import |
|:------|:-----------|:----------------------|:------------|:-----------|:------------|:----------------|:--------------|
| 2015  | 31,764     | 26,968                | 26.7        | 3,907      | 5.4         | -27,857         | 0.84          |
| 2016  | 27,890     | 21,278                | 28.1        | 5,005      | 7.6         | -22,885         | 1.01          |
| 2017  | 29,073     | 22,618                | 32.0        | 5,803      | 8.5         | -23,270         | 1.1           |
| 2018  | 34,224     | 23,073                | 29.0        | 5,728      | 8.6         | -28,496         | 0.85          |
| 2019  | 24,167     | 18,109                | 19.7        | 5,893      | 8.9         | -18,274         | 0.82          |
| 2020  | 29,101     | 21,671                | 23.8        | 5,775      | 8.3         | -23,326         | 0.82          |
| 2021  | 31,592     | 23,912                | 29.6        | 5,204      | 7.3         | -26,388         | 0.94          |
| 2022  | 35,570     | 24,688                | 44.5        | 3,617      | 7.1         | -31,953         | 1.25          |
| 2023  | 40,936     | 27,174                | 48.0        | 4,938      | 7.5         | -35,999         | 1.17          |
| 2024  | 42,188     | 24,200                | 49.3        | 4,361      | 7.9         | -37,828         | 1.17          |
| 2025  | 39,371     | 21,973                | 42.1        | 5,032      | 8.6         | -34,339         | 1.07          |

**Chickpea (CN 07132000)**

| Year | Imports t | of which extra-EU t | Imports M€ | Exports t | Exports M€ | Balance t (X-M) | €/kg import |
|:------|:-----------|:----------------------|:------------|:-----------|:------------|:----------------|:--------------|
| 2015  | 4,317      | 3,069                 | 4.5         | 6,200      | 3.8         | 1,883           | 1.04          |
| 2016  | 7,932      | 4,875                 | 9.0         | 7,737      | 6.0         | -194            | 1.14          |
| 2017  | 11,509     | 6,473                 | 13.8        | 14,070     | 12.6        | 2,561           | 1.2           |
| 2018  | 12,108     | 6,544                 | 11.8        | 13,215     | 10.5        | 1,107           | 0.98          |
| 2019  | 6,749      | 3,834                 | 6.8         | 13,834     | 9.0         | 7,085           | 1.0           |
| 2020  | 6,992      | 3,759                 | 7.1         | 17,199     | 10.7        | 10,208          | 1.02          |
| 2021  | 6,933      | 3,892                 | 7.6         | 26,224     | 15.6        | 19,290          | 1.1           |
| 2022  | 14,010     | 6,910                 | 17.1        | 22,475     | 18.6        | 8,465           | 1.22          |
| 2023  | 18,750     | 10,980                | 21.5        | 17,048     | 17.4        | -1,702          | 1.15          |
| 2024  | 10,645     | 5,532                 | 13.8        | 16,633     | 17.6        | 5,988           | 1.3           |
| 2025  | 9,838      | 4,915                 | 12.5        | 13,788     | 13.0        | 3,949           | 1.27          |

**Dry bean (kidney/common, not for sowing) (CN 07133390)**

| Year | Imports t | of which extra-EU t | Imports M€ | Exports t | Exports M€ | Balance t (X-M) | €/kg import |
|:------|:-----------|:----------------------|:------------|:-----------|:------------|:----------------|:--------------|
| 2015  | 33,512     | 27,040                | 38.2        | 2,299      | 3.0         | -31,213         | 1.14          |
| 2016  | 31,384     | 22,699                | 27.5        | 2,751      | 3.1         | -28,633         | 0.88          |
| 2017  | 26,594     | 18,488                | 26.1        | 2,700      | 3.2         | -23,894         | 0.98          |
| 2018  | 26,758     | 20,790                | 24.8        | 3,111      | 3.7         | -23,647         | 0.93          |
| 2019  | 32,882     | 21,673                | 32.7        | 5,391      | 6.9         | -27,491         | 0.99          |
| 2020  | 35,247     | 23,956                | 39.0        | 5,606      | 7.5         | -29,641         | 1.11          |
| 2021  | 32,067     | 20,046                | 35.0        | 2,968      | 4.3         | -29,099         | 1.09          |
| 2022  | 31,197     | 18,544                | 36.3        | 5,163      | 6.8         | -26,034         | 1.16          |
| 2023  | 35,746     | 14,198                | 38.1        | 4,386      | 6.6         | -31,360         | 1.07          |
| 2024  | 31,179     | 16,451                | 41.1        | 5,505      | 8.0         | -25,674         | 1.32          |
| 2025  | 29,736     | 16,276                | 40.6        | 4,971      | 7.9         | -24,765         | 1.37          |

**Dry pea, not for sowing (CN 07131090)**

| Year | Imports t | of which extra-EU t | Imports M€ | Exports t | Exports M€ | Balance t (X-M) | €/kg import |
|:------|:-----------|:----------------------|:------------|:-----------|:------------|:----------------|:--------------|
| 2015  | 6,460      | 1,691                 | 3.7         | 264,532    | 73.1        | 258,072         | 0.57          |
| 2016  | 31,266     | 19,762                | 9.3         | 357,542    | 103.3       | 326,276         | 0.3           |
| 2017  | 76,353     | 37,091                | 23.8        | 281,972    | 69.6        | 205,619         | 0.31          |
| 2018  | 29,691     | 7,075                 | 7.7         | 203,373    | 45.8        | 173,682         | 0.26          |
| 2019  | 29,118     | 6,952                 | 8.7         | 237,497    | 55.3        | 208,379         | 0.3           |
| 2020  | 28,519     | 8,379                 | 9.4         | 226,319    | 59.2        | 197,801         | 0.33          |
| 2021  | 47,190     | 2,164                 | 14.8        | 188,745    | 58.6        | 141,556         | 0.31          |
| 2022  | 44,445     | 18,500                | 19.7        | 183,438    | 78.3        | 138,993         | 0.44          |
| 2023  | 14,843     | 1,824                 | 7.6         | 233,877    | 76.0        | 219,034         | 0.51          |
| 2024  | 44,645     | 3,079                 | 15.7        | 165,071    | 57.8        | 120,426         | 0.35          |
| 2025  | 61,582     | 4,304                 | 20.1        | 159,701    | 52.3        | 98,120          | 0.33          |

**Faba bean / forage faba bean (CN 07135000)**

| Year | Imports t | of which extra-EU t | Imports M€ | Exports t | Exports M€ | Balance t (X-M) | €/kg import |
|:------|:-----------|:----------------------|:------------|:-----------|:------------|:----------------|:--------------|
| 2015  | 12,565     | 657                   | 4.7         | 97,914     | 30.6        | 85,349          | 0.38          |
| 2016  | 8,991      | 5,124                 | 3.7         | 92,263     | 24.3        | 83,272          | 0.41          |
| 2017  | 22,134     | 13,264                | 6.3         | 101,748    | 26.3        | 79,614          | 0.29          |
| 2018  | 27,882     | 25,484                | 7.9         | 60,706     | 16.4        | 32,824          | 0.28          |
| 2019  | 30,396     | 27,787                | 9.8         | 46,466     | 15.0        | 16,070          | 0.32          |
| 2020  | 25,371     | 22,819                | 8.7         | 43,538     | 12.9        | 18,167          | 0.34          |
| 2021  | 46,572     | 37,169                | 16.1        | 49,040     | 15.7        | 2,469           | 0.35          |
| 2022  | 65,191     | 62,717                | 27.5        | 75,231     | 32.8        | 10,041          | 0.42          |
| 2023  | 40,657     | 28,008                | 15.3        | 64,460     | 24.5        | 23,803          | 0.38          |
| 2024  | 34,631     | 16,607                | 13.8        | 72,712     | 28.5        | 38,082          | 0.4           |
| 2025  | 15,067     | 9,962                 | 6.6         | 69,017     | 24.0        | 53,951          | 0.44          |

**Preparations (CN8, all partners) [V]:**

| Year | 20055100 canned beans: imports t | imports M€ | exports t | 11061000 pulse flour: imports t | exports t |
|---|---|---|---|---|---|
| 2015 | 29,027 | 23.0 | 9,203 | 1,254 | 10,019 |
| 2019 | 30,818 | 27.6 | 8,629 | 3,962 | 13,424 |
| 2023 | 30,513 | 35.8 | 12,168 | 3,948 | 11,557 |
| 2024 | 30,543 | 37.4 | 11,816 | 4,689 | 14,373 |
| 2025 | 36,416 | 43.7 | 14,945 | 3,666 | 13,401 |

(Weight of the canned product, includes covering liquid: do not add directly to dry grain. Canned chickpea falls under 20059980 "other vegetables", mixed with other items [NV], so it cannot be isolated.)

### Main partners, 2023-2025 average [V]

| Product and flow | Total t/year | M€/year | Partner 1 | Partner 2 | Partner 3 | Partner 4 |
|---|---|---|---|---|---|---|
| Lentil, imports | 40,832 | 46.4 | Canada 18,681 t (46%, 1.03 €/kg) | Belgium 13,166 t (32%, 1.07 €/kg) | Turkey 2,661 t (7%) | China 1,106 t; USA 1,085 t |
| Lentil, exports | 4,777 | 8.0 | Belgium 30% | Netherlands 14% | Italy 11% | Germany 8% |
| Chickpea, imports | 13,078 | 15.9 | Belgium 25% | Mexico 18% (1.51 €/kg) | Canada 14% | Spain 10% |
| Chickpea, exports | 15,823 | 16.0 | Belgium 26% | Italy 18% | Netherlands 17% | United Kingdom 12% |
| Dry bean 07133390, imports | 32,220 | 39.9 | Belgium 21% | Argentina 17% | Portugal 16% | USA 11% (1.65 €/kg) |
| Dry pea, imports | 40,357 | 14.5 | Lithuania 24% | Latvia 20% | Sweden 19% | Estonia 12% (0.27 €/kg, feed) |
| Dry pea, exports | 186,216 | 62.1 | Belgium 44% | China 14% | Portugal 12% | Netherlands 8% |
| Faba bean, exports | 68,730 | 25.7 | Norway 67% (fish farming, my guess [NV]) | Netherlands 10% | Italy 8% | Belgium 6% |

### Readings and gotchas

- **Belgium is a hub (Antwerp port, packers).** A third of the lentil "imported from Belgium" is almost certainly re-exported Canadian or Turkish lentil. For the true origin, look at the mirror: Canadian exports to France in UN Comtrade (reporter 124, partner 251, HS 071340) [NV, not downloaded].
- **The unit import price of lentil jumped from 0.82 €/kg (2019-2020) to 1.25 €/kg (2022)** and settled at 1.07-1.17 (2023-25). That volatility is exactly what a French producer with a contract does not see, and what an industrial buyer does arbitrage.
- **Chickpea: the balance went from +19 kt (2021) to ~-1/+5 kt (2023-25).** France produces ~40 kt (Terres Univia 2025, NV) and exports cheap grain (0.8-1.1 €/kg) to Italy/Belgium, while importing premium Mexican chickpea (1.51 €/kg, large calibre). The opportunity is in quality/calibre and processing, not volume.
- **Pea and faba bean are exported as commodities (0.3-0.4 €/kg)**, much of it to feed (Norway, China). What is excluded from the challenge (feed) dominates the volume of these two crops: filter by destination if you use them.
- Intra-EU quantities from 2022 onward are affected by the change of survey to EMEBI (see section 2) [F].

**Track 3 relevance: 10/10.** It is the only open source, monthly, with CN8 and origin, that sizes import substitution in tonnes and euros.

---

## 2. Douane: "Statistiques nationales du commerce extérieur" (national source)

- **URL:** https://www.data.gouv.fr/datasets/statistiques-nationales-du-commerce-exterieur and full databases at https://lekiosque.finances.gouv.fr (Téléchargement menu). Opendatasoft API: `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/statistiques-nationales-du-commerce-exterieur/records`.
- **Owner:** DGDDI (French customs). **License:** Licence Ouverte v2 [V, data.gouv metadata `lov2`].
- **Format:** monthly zips `NATIONAL_NC8PAYSI.txt` / `NATIONAL_NC8PAYSE.txt` (`;`, UTF-8), plus NC8, country, CPF6 and A129 nomenclatures [F, LISEZ-MOI (read-me file)].
- **Audit [V]:** the ODS API has 5,082,641 rows with unnamed columns (`column_1` flow I/E, `column_2` month, `column_3` year, `column_6` NC8 **as an integer, the leading 0 is lost**: 07134000 → 7134000, `column_7` ISO2 country, `column_8` value €, `column_9` mass kg). It only covers **March 2023 to March 2024** (13 months) and the last update is 05/06/2024: the mirror is frozen. Lentil imports in those 13 months (including two Marches): ~45.4 kt, consistent with the ~41 kt annual figure from Comext.
- **Gotcha [F, LISEZ-MOI]:** since January 2022 the EMEBI survey (the new intra-EU survey) has replaced DEB (the former intra-EU trade declaration) for intra-EU trade; the open data are "raw from collection, without non-response correction", with series breaks for EU partners and for third-country goods dispatched through another Member State.
- **Advantage over Comext:** none in granularity (also NC8 × country × month). The regional version (by region/department of the declaring company) exists on lekiosque, but aggregated at a coarser product level [NV].
- **Relevance: 7/10.** Use Comext for long series; use this source only if you want the official French figure to cite.

---

## 3. FranceAgriMer: average prices paid to producers (cereals and oilseeds/protein crops, quarterly)

- **Dataset URL:** https://www.data.gouv.fr/datasets/historique-des-prix-moyens-mensuels-et-trimestriels-payes-aux-producteurs-depuis-2005-cereales-et-oleoproteagineux ; file: `https://visionet.franceagrimer.fr/Pages/OpenDocument.aspx?fileurl=SeriesChronologiques%2fproductions%20vegetales%2fgrandes%20cultures%2fprix%20pay%c3%a9s%20aux%20producteurs%2fSCR-CER-HISTOPRIXTRIMESTRIELS-C25-26.xlsx&telechargersanscomptage=oui`
- **Owner:** FranceAgriMer. **License:** data.gouv says Licence Ouverte v2, but the "Infos" sheet of the xlsx says "tous droits réservés, reproduction interdite sans mention de la source" (all rights reserved, reproduction forbidden without citing the source) [V]. In practice: cite "Source: FranceAgriMer".
- **Method [F, Infos sheet]:** quarterly survey of a panel of collectors (cooperatives and négoce, grain trading); price = value of deliveries / tonnage collected, cumulated from the start of the marketing year, including price supplements, bonuses and discounts. Q4 (April-June) gives the **full marketing-year price**. National = regional average weighted by collection. Conventional farming.
- **Coverage [V]:** marketing years 2004/05 to 2025/26, data as of 30/06/2026. 19 species: soft wheat, durum wheat, barley, maize, rye, oats, sorghum, triticale, rapeseed, **pea (Pois)**, sunflower, **faba bean (Féverole)**, soybean, spelt, **lentil**, flax, **lupin**, rice, buckwheat. Format: xlsx 266 KB, sheet "Publicación nacional" (National publication), 93 useful rows × 21 columns, header on row 11.
- **Missing data [V]:** lentil only from 2023/24 (12 quarters); pea from 2005/06; faba bean later. **There is no chickpea or dry bean.**

**Full marketing-year price (Q4), €/t [V]:**

| Marketing year | Soft wheat | Pea | Faba bean | Lentil | Rapeseed | Soybean |
|---|---|---|---|---|---|---|
| 2015/16 | 147 | 212 | 178 | | 351 | 321 |
| 2017/18 | 141 | 180 | 166 | | 339 | 323 |
| 2019/20 | 158 | 188 | 228 | | 369 | 330 |
| 2020/21 | 179 | 213 | 242 | | 400 | 374 |
| 2021/22 | 217 | 266 | 280 | | 549 | 518 |
| 2022/23 | 270 | 340 | 346 | | 591 | 593 |
| 2023/24 | 205 | 247 | 257 | **854** | 430 | 439 |
| 2024/25 | 194 | 275 | 273 | **873** | 471 | 468 |
| 2025/26 | 170 | 222 | 231 | **806** | 473 | 401 |

- **Reading:** lentil pays 4.2-4.7 times the wheat price per tonne; pea 1.2-1.4 times. The risk lies in yield (lentil 8-22 q/ha depending on year and dept, see `ideas2_4_time_series.md`), not in price.
- **Joinability:** by species × marketing year with SAA (yield) to compute gross output €/ha by dept. Note: marketing year July N to June N+1 vs harvest year N in SAA.
- **Relevance: 9/10.**

---

## 4. EU agri-food data portal: weekly cereal prices (for the comparison wheat)

- **URL:** `https://ec.europa.eu/agrifood/api/cereal/prices?memberStateCodes=FR&productCodes=BLTPAN&beginDate=01/07/2025&endDate=30/09/2026` (note: `www.ec.europa.eu` returns an HTML redirect page; use `ec.europa.eu` or `curl -L`) [V].
- **Owner:** DG AGRI. License: Commission reuse [F].
- **Audit [V]:** 175 weekly records for FR bread wheat 07/2025-09/2026, markets Rouen, La Pallice and "National Average", price as text `"€244,36"` (needs parsing). 2026 average (Jan-Sep): ~207 €/t Rouen. Available products: wheat, barley, maize, oats, rye, sorghum; oilseeds (rapeseed, soybean, sunflower, meals). **No pulses** (I tried `PEA` and `proteinCrops`: 404).
- **Relevance: 5/10.** Useful for the opportunity-cost price series (wheat) week by week.

## 5. Eurostat apri_ap_crpouta (sale prices of plant products): discarded for France

- It has codes for dry pea (02210000), dry bean, faba bean, lentil (02991000), chickpea (02992000). **France only reports 2015-2016** (lentil 75.2 and 67.9 €/100 kg; pea 38.5 and 34.7; wheat 22.3 and 20.1) and nothing since 2017 [V]. Useful to compare other EU countries, not France. **Relevance: 2/10.**

---

## 6. Reference gross margins: pulses vs wheat

There is no open tabular dataset of margins by crop and department. What exists are technical references (Terres Inovia, Cerfrance, Chambres d'agriculture (regional farm chambers)) in PDF. The Terres Inovia and Chambre sites block automated downloads (403/404 to curl and to the fetcher); Terres Inovia guides can be downloaded from the seed distributor mirror germineo.com.

### 6.1 Terres Inovia, protein pea guide 2025 [F, PDF read]

Mirror URL: https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/POIS-PROTEAG.-2025-Guide-culture-TERRES-INOVIA.pdf (original on terresinovia.fr, 403).
Source of the numbers: "projection de marges 2025 du Cerfrance Nord-Est Île-de-France, observatoire des résultats économiques à la production TI-TU à partir des données du CN Cerfrance" (2025 margin projection by Cerfrance Nord-Est Île-de-France, economic results observatory for production TI-TU, based on Cerfrance CN data). Gross margin = gross output - operating costs excluding hail insurance, + coupled aid for pea of 110 €/ha.

| Soil | Rotation | Rapeseed | Wheat | 3rd crop | Following wheat | Rotation mean |
|---|---|---|---|---|---|---|
| High potential | 3-year reference rapeseed-wheat-wheat | 1264 (42 q) | 1025 (85 q) | wheat 845 (79 q) | | **1045** |
| High potential | With winter pea at 250 €/t (feed) | 1264 | 1025 | **pea 810 (45 q)** | 1189 (86.4 q) | **1072** |
| High potential | With pea at 280 €/t (**human food**) | 1264 | 1025 | **pea 945** | 1189 | **1106** |
| Limited potential | 3-year reference | 740 (30 q) | 755 (65 q) | wheat 575 (59 q) | | **690** |
| Limited potential | Pea at 250 €/t | 740 | 755 | **pea 500 (35 q)** | 899 (66.4 q) | **724** |
| Limited potential | Pea at 280 €/t (HF) | 740 | 755 | **pea 605** | 899 | **750** |

Assumptions: wheat after pea vs wheat after wheat = +7.4 q/ha at 200 €/t, -40 kg N at 1.2 €/unit, -60 €/ha of herbicide. Coupled aid "between 100 and 130 €/ha, final amount set after the campaign".
**Key message:** pea alone earns less than wheat (810 vs 1025), but the rotation with pea earns **€27-61/ha/year more** than the reference, thanks to the preceding-crop effect; and the human-food destination (+30 €/t) adds ~135 €/ha on pea. This is exactly the economic argument for the farmer.

### 6.2 Terres Inovia, chickpea guide 2023 [F, PDF read]

germineo mirror: `.../POIS-CHICHE-2023-Guide-culture-TERRES-INOVIA.pdf`. Potential yield 15-30 q/ha (conv.), 10-25 (organic). Operating costs 270-390 €/ha (seed 200 €/ha, herbicides 96, insecticides 0-56, fungicides 0-40). Indicative coupled aid 100 €/ha. Gross margin matrix with coupled aid (€/ha):

| q/ha | Conv. 300 €/t | 500 €/t | 700 €/t | 900 €/t | Organic 600 €/t | Organic 900 €/t | Organic 1200 €/t |
|---|---|---|---|---|---|---|---|
| 10 | 55 | 255 | 455 | 655 | 400 | 700 | 1000 |
| 15 | 205 | **505** | 805 | 1105 | 700 | 1150 | 1600 |
| 20 | 355 | **755** | 1155 | 1555 | 1000 | 1600 | 2200 |
| 25 | 505 | 1005 | 1505 | 2005 | 1300 | 2050 | 2800 |

Terres Inovia "strongly encourages going through production contracts" to avoid overproduction [F].

### 6.3 Terres Inovia, lentil guide 2023 [F, PDF read]

Indicative conventional operating costs: **518 €/ha** (seed 150, PK fertilization 174, herbicides 155, insecticides 19, fungicides 20). Selling price "very variable, from 450 to 1800 €/t" (Terres Univia), depending on mode (conv./organic), colour and quality signs (AOP lentille verte du Puy (protected designation of origin), Label Rouge lentille verte du Berry (red label), lentille blonde de Saint-Flour, lentillon rosé de Champagne). **It does not give a gross margin.**

**My own calculation (indicative, not a published reference):** with FranceAgriMer price 806-873 €/t, costs 518 €/ha and coupled aid 122 €/ha:

| Lentil yield | Output (850 €/t) | Gross margin with aid |
|---|---|---|
| 8 q/ha (bad year, e.g. Champagne 2021) | 680 | ~284 €/ha |
| 15 q/ha (national average 2025) | 1275 | ~879 €/ha |
| 22 q/ha (good year, Aube/Marne 2024-25) | 1870 | ~1474 €/ha |

Compare with Terres Inovia wheat (755-1025 €/ha at 200 €/t; with 2025/26 wheat at 170 €/t it would be ~200-250 €/ha less). **Lentil ties with or beats wheat in an average year and loses a lot in a bad year: the problem is yield variance, not expected margin.** That is the angle for the AI.

### 6.4 Other references found (not verified at source)

- Faba bean: costs 300-400 €/ha, gross margin with coupled aid 500-1200 €/ha; wheat after legume +180 €/ha (Terres Inovia, early 2024 context) [NV, search engine summary].
- Pea: preceding-crop effect +140 to 200 €/ha on the following wheat; the FOP says that at 35 q/ha pea does not compete with wheat, ≥45 q/ha is needed; Terres Univia/Terres Inovia study Nov-2024: 11-23 q/ha short to match wheat under rainfed conditions [NV, Réussir/Pleinchamp via search].
- Chickpea Occitanie (Qualisol, 2018 data): 1.8 t/ha at 550 €/t, gross margin ~663 €/ha, net margin ~263 €/ha; ~40% of 132 producers under 15 q/ha [NV, Chambre Aude PDF not downloadable].
- Lentil: NatUp contract (Normandy) 500-600 €/t with yields of 5 to 30 q/ha [NV]; Chambre Centre-Val de Loire (May 2024) lentil/camelina 10 q/ha at 1000 €/t, margin 945 €/ha [NV]; Euralis/Bonduelle 2024: chickpea 2.5 t/ha, lentil 1 t/ha [NV].
- Chambre d'agriculture Pays de la Loire publishes each year "Marges brutes des cultures de vente" (gross margins of cash crops) (wheat, pea, faba bean) [NV, PDF returns 404 on fetch].
- Cerfrance Poitou-Charentes, 2024 yield survey: pea 3.0 t/ha (ten-year average 3.0; 2022: 1.4), wheat 5.7 t/ha; pea sample < 1,000 ha [F, PDF read].

**Relevance: 8/10** (these are the numbers the jury wants to see under "economic viability"). Limitation: they are indicative examples, not observed distributions.

---

## 7. Coupled aid for grain legumes (CAP 2023-2027) and beneficiary transparency

- **Unit amounts:** 2023: 104.2 €/ha (Weblex) [NV]; **2024: 122 €/ha** (arrêté (ministerial order) of 6/02/2025, JO (Official Journal) 9/02/2025) [NV, via Réussir/Chambre Normandie]; **2025: 122 €/ha** (Réussir, 13/03/2026) [F, article read]. The Terres Inovia 2025 pea guide says "between 100 and 130 €/ha" [F]. Forage legumes: 124 €/ha (2024).
- **Hectares and beneficiaries:** I found no open dataset. Eligible area can be approximated with the RPG (pulse crop codes) × 122 €/ha [possible calculation, not done].
- **Individual CAP 2023-27 beneficiaries:** microdata "Bénéficiaires et interventions PSN" (beneficiaries and PSN interventions) only in **CASD** (access approved, takes weeks) [F, casd.eu]. Telepac (the online CAP application portal) does not offer bulk download [V, page read]. On data.gouv there are only old files (2011, 2015, 2016, legal entities only) because of the 2010 CJEU (EU Court of Justice) ruling [F].
- **Relevance: 6/10** for the amount (goes into any margin calculation), **3/10** for the microdata (inaccessible in 20 h).

## 8. RICA (Réseau d'information comptable agricole, French farm accountancy data network) and EU FADN / FSDN

- **RICA France:** annual accounting survey of ~7,000 "medium and large" farms (PBS, standard gross output, > €15,000), extrapolated; results by OTEX (type of farming orientation), size class and region. DRAAF publications in PDF (e.g. Grand Est "étude RICA 2024", Hauts-de-France RICA 2023) [F, listings]. **Microdata only via CASD** [F].
- **EU FADN Public Database** (now FSDN): https://agridata.ec.europa.eu/extensions/FADNPublicDatabase/FADNPublicDatabase.html. Standard results (SE variables) averaged by Member State × farm type × economic size, since 2004; Qlik dashboard with manual export [F]. There is a product variable "protein crops" (SE145) [NV].
- **Why it does not work directly:** there is no OTEX "pulses"; pulses fall within "grandes cultures" (field crops, OTEX 15/16). Farms with and without pulses cannot be compared without microdata.
- **Relevance: 5/10.** Useful for context (EBE (gross operating surplus) per FTE in field crops, weight of aid in the result), not for the core of the project.

---

## 9. Agence Bio: certified areas by department and production (2008-2025)

- **URL:** https://www.data.gouv.fr/datasets/historique-detaille-des-surfaces-cheptels-et-nombre-doperateurs-par-departement ; file `donnees-dept-secretstat-14092026-surfaces-par-production.csv`. Note: on data.gouv the resource titles "SAU" (utilised agricultural area) and "surfaces par production" are **swapped**: the one titled "des surfaces de 2008 à 2025" is the one broken down by production [V].
- **Owner:** Agence Bio (French organic certification agency). **License:** LO v2. Last update 16/09/2026.
- **Audit [V]:** 130,980 rows, 16 columns (`annee, coderegion, region, codedepartement, departement, code_groupe, groupe_production, sous_groupe_production, production, nb_exp, surfab, surfc1, surfc2, surfc3, surfc123, surfbio`). 2008-2025, 103 départements (includes DOM, the overseas departments). Areas in ha (certified organic + conversion years 1-3). **37.4% of `surfbio` values are "NC"** (statistical secrecy, fewer than 3 farms), so sums are lower bounds. INSEE department code stored as text ("971", "01"): joins with SAA and RPG via `codedepartement`.
- Pulse productions available: "Lentilles, sèches", "Pois chiches, secs", "Haricots, secs", "Autres légumes secs", "Fèves, sèches (yc féveroles)", "Pois, secs", "Lupin", "Mélanges Céréales-légumineuses".

**Organic area (ha, sum of depts without NC) [V]:**

| Production | 2019 | 2021 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| Dry lentil | 14,415 | 17,564 | 12,982 | 14,836 | 14,096 |
| Dry chickpea | 8,192 | 7,382 | 9,472 | 9,588 | 7,623 |
| Dry bean | | 1,667 | 353 | 578 | 861 |
| Dry faba bean (incl. forage faba bean) | 17,873 | 19,432 | 16,443 | 17,422 | 21,685 |
| Dry pea | 10,793 | 11,381 | 7,427 | 5,728 | 4,248 |
| Cereal-legume mixtures | 75,041 | 58,390 | 108,276 | 103,553 | 96,975 |

Top 2025 organic lentil: Yonne 1,643 ha (108 farms), Deux-Sèvres 856, Charente-Maritime 772, Gers 664, Aube 662, Côte-d'Or 652. Organic chickpea: **Gers 2,193 ha (156 farms)**, Lot-et-Garonne 714, Charente-Maritime 615, Haute-Garonne 540 [V].
- **Other Agence Bio datasets (not downloaded):** AB parcels declared to the CAP (RPG bio, 2022-2023, zips of 400-500 MB, gpkg) [V, metadata]; CartoBio certified parcels 2025 by region [V, metadata]; `operateursbio.csv` (8.5 MB, operators with activities: production, processing, distribution) [V, metadata], useful for finding organic pulse processors.
- **Relevance: 7/10.** Organic is where lentil and chickpea are worth most (organic chickpea 600-1200 €/t according to Terres Inovia), and the data is departmental and recent.

---

## 10. Other FranceAgriMer datasets (data.gouv catalogue, 185 datasets)

All point to Visionet (https://visionet.franceagrimer.fr), whose pages are built with JavaScript: with curl the links to the xlsx files do not appear. You have to download by hand from the browser or guess the `fileurl` (as in section 3). License LO v2 on data.gouv. Content not verified except where stated.

- **Grandes cultures, collecte par département** and **collecte mensuelle par département**: tonnages collected by organismes stockeurs (grain storage bodies) by species and department, recent marketing years. If it includes pea and faba bean (likely), it is the best departmental measure of **marketed production** (vs estimated SAA production) [NV].
- **Séries chronologiques sur les surfaces déclarées à l'ASP au titre de la PAC**: areas declared to the CAP, national/regional/departmental, including "oléagineux et protéagineux" and "légumineuses" [F, data.gouv description]. A lighter alternative to the RPG.
- **Historique (régional, national et départemental) sur les stocks** and **collecte bio de grandes cultures et oléo-protéagineux** (monthly, since 2000) [F, titles].
- **Prix annuels moyens payés aux producteurs bio** (since 2005/06) [F, title]: the organic counterpart of section 3, probably with organic lentil and faba bean.
- **Cotations du Réseau des Nouvelles des Marchés (RNM)** (market news network quotations): fresh product prices; dry pulses probably not included, except fresh bean/pea [NV].
- **Relevance: 6/10** (departmental collection could rise to 8 if it confirms pulses).

## 11. Géorisques: classified installations (ICPE), grain silos and dryers

- **API URL:** `https://georisques.gouv.fr/api/v1/installations_classees?departement=51&page_size=1000&page=1` (no key). **Owner:** Ministry of Ecological Transition / BRGM. License LO v2 [F].
- **Audit [V]:** 138,878 installations in total. The `rubriqueIcpe=2160` filter **does not filter** (returns everything): you have to download by department and filter client-side. In the Marne: 1,419 ICPE; 76 on the first page of 1,000 with rubrique 2160 (grain silos) or 2260 (drying/milling). Each record includes company name, SIRET, NAF code, INSEE commune, **lat/lon** and, per rubrique, **capacity in m³** (e.g. Cristal Union Sillery 133,000 m³, Vivescia Reims 42,000 m³, Luzéal Sept-Saulx 26,960 + 11,400 m³).
- **Use:** map of collection points to estimate plot-to-silo distance (logistics cost) and locate cooperatives. **Limitation:** it does not say which grain is stored, nor whether there is a sorting/cleaning line for pulses for human food (grading, sorting of bruchid-damaged grains, "bruches"). Small silos (declaration regime below the threshold) are not included.
- **Relevance: 6/10.** Joins with RPG by coordinates and with SAA by department.

## 12. Protein plan (France Relance recovery plan): "structuration des filières" winners

- **What I know:** 50 M€ call for projects (AAP) for supply chain structuring (structuration des filières); 26 first winners in June 2021 for a bit over 17 M€; the protein component (volet protéines) of the recovery plan ~137 M€, 151 M€ in total according to a ministerial review [NV, press releases via search]. FranceAgriMer managed the equipment aid.
- **Dataset:** I found no open tabular list of winners with amounts. There are regional press-release PDFs (DRAAF, prefectures) [NV].
- **Relevance: 4/10.** Useful for the narrative ("money has already gone into structuring, the decision tool is still missing") and to identify players (Qualisol, Euralis, NatUp, Vivescia, Cavac, Bonduelle).

## 13. Demand (light; another agent covers food in depth)

- **INCA3 (ANSES):** https://www.data.gouv.fr/datasets/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-3 ; `conso-compo-alim.csv` 204 MB, nomenclature 12.9 MB, survey 2014-2015 [V, metadata]. License "notspecified" on data.gouv.
- **Terres Univia, OléoProtéines observatory 2025:** ~23,000 t of raw dry pulses sold in GMS (grandes et moyennes surfaces, large retail) in 2024, +5% in one year, driven by lentil (+8%); volume -6% since 2019 but value rising [NV, via search]. Another source (2021) says France covers ~70% of its dry pulse needs and lentil is half of the volume consumed [NV].
- **Open Food Facts:** the API was down ("Page temporarily unavailable") on 29/10/2026, so I could not count products with French origin [V of the failure].
- **Trade-based proxy [V, calculation]:** apparent lentil consumption ≈ production ~45 kt + imports 39-42 kt - exports ~5 kt ≈ 80 kt/year (includes industry and losses).

---

## Joinability with SAA and RPG

| Dataset | Key with SAA | Key with RPG | Comment |
|---|---|---|---|
| Comext / Douane | crop + year | no | National. Map CN8 → SAA crop (07134000 ↔ lentille, 07132000 ↔ pois chiche, 07131090 ↔ pois protéagineux, 07135000 ↔ féverole, 07133390 ↔ haricot sec) |
| FranceAgriMer producer prices | species + marketing year (July-June) | no | National; convert marketing year N/N+1 → harvest year N |
| Terres Inovia margins | crop | no | Parameters of a margin model, not series |
| Agence Bio dept × production | `codedepartement` + year + crop | via dept | NC = statistical secrecy |
| Agence Bio RPG bio / CartoBio | via dept | parcel (geometry) | Heavy |
| Géorisques ICPE | `codeInsee` → dept | lat/lon (distance) | Filter rubriques 2160/2260 |
| FranceAgriMer collection by dept | dept + species + marketing year | via dept | Check in Visionet |

---

## Seed ideas (project, user, decision, why AI is essential)

1. **"Lentil Risk Desk": insurance/contract indexed to yield for human-food pulses.** User: cooperative or packer (Qualisol, NatUp, Vivescia, Euralis). Decision: at what price and with what minimum-yield clause to contract lentil/chickpea hectares with each producer. AI: probabilistic yield forecast by dept (SAA + climate) → margin distribution (FranceAgriMer price 806-873 €/t, costs 518 €/ha, aid 122 €/ha); the expected margin already competes with wheat; what holds the farmer back is the tail (8 q/ha → ~284 €/ha). Viability: the coop sells the covered risk as a premium. Data: sections 3, 6, 7 + SAA.
2. **Import-substitution simulator by basin.** User: region or filière (supply chain) (Terres Univia, interprofession). Decision: how many hectares and where, to capture what share of the ~63 kt / ~70 M€ net imports of lentil and dry bean. AI: spatial optimization (agronomic suitability by dept × yield risk × distance to ICPE silos with capacity) under rotation constraints. Data: Comext + SAA + RPG + Géorisques + Agence Bio.
3. **Rotation comparator "with or without pulse" for the farmer.** User: arable farmer with an adviser from the Chambre or coop. Decision: whether or not to put a pea/lentil/chickpea into next year's rotation. AI: full rotation margin model (preceding-crop effect +140-200 €/ha on wheat, N savings) with yield and price uncertainty learned from the series; show that the rotation with pea earns +27 to +61 €/ha/year (Terres Inovia) and in which depts it does not. Risk: the jury sees it as "a calculator"; the AI has to live in the uncertainty and the spatialization.
4. **Import market monitor (nowcasting of prices and volumes).** User: buyer/industrial or coop that sells French lentil. Decision: when to sell, and at what price to ask for a "French origin" premium. AI: monthly forecast of import volume and unit value (monthly Comext, Canada/Turkey) and of the Canadian harvest; alert when the import price rises (as in 2022: 0.82 → 1.25 €/kg). Data: monthly Comext + FranceAgriMer. Less direct impact on the farmer.
5. **Adding value to French chickpea through quality/calibre.** France already exports more chickpea than it imports, but imports Mexican chickpea at 1.51 €/kg and exports at 0.8-1.1 €/kg. User: coop + processor. AI: computer vision to grade calibre/defects on reception (see `idea3_bruchids.md`) and route lots to the premium market. Data from this domain: Comext unit values by origin as a "target price".

---

## Sources consulted

- Eurostat Comext DS-045409 API: https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409
- Eurostat apri_ap_crpouta: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apri_ap_crpouta
- Douane, national statistics: https://www.data.gouv.fr/datasets/statistiques-nationales-du-commerce-exterieur ; https://data.economie.gouv.fr/explore/dataset/statistiques-nationales-du-commerce-exterieur/
- FranceAgriMer producer prices: https://www.data.gouv.fr/datasets/historique-des-prix-moyens-mensuels-et-trimestriels-payes-aux-producteurs-depuis-2005-cereales-et-oleoproteagineux
- FranceAgriMer catalogue on data.gouv: https://www.data.gouv.fr/organizations/534fff78a3a7292c64a77e02/
- EU agri-food data portal API: https://ec.europa.eu/agrifood/api/cereal/prices
- Terres Inovia, pea guide 2025 (mirror): https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/POIS-PROTEAG.-2025-Guide-culture-TERRES-INOVIA.pdf
- Terres Inovia, lentil guide 2023 (mirror): https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/LENTILLE-2023-Guide-culture-TERRES-INOVIA.pdf
- Terres Inovia, chickpea guide 2023 (mirror): https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/POIS-CHICHE-2023-Guide-culture-TERRES-INOVIA.pdf
- Cerfrance Poitou-Charentes, 2024 yield survey: https://poitoucharentes.cerfrance.fr/wp-content/uploads/2025/01/Enquete_rendements_cultures_2024.pdf
- Réussir, coupled aid 2025: https://www.reussir.fr/pac-quel-montant-des-aides-couplees-vegetales-pour-la-campagne-2025 ; 2024: https://www.reussir.fr/pac-quel-montant-pour-les-aides-couplees-vegetales-pour-la-campagne-2024
- Chambre Normandie, protein aid: https://normandie.chambres-agriculture.fr/sinformer/respecter-la-reglementation/aides-financements/detail-de-laide/aides-aux-proteines-vegetales-pac
- CASD, PSN beneficiaries: https://www.casd.eu/en/source/beneficiaires-et-interventions-psn-en/
- EU FADN Public Database: https://agridata.ec.europa.eu/extensions/FarmEconomyFocus/FADNDatabase.html
- Agence Bio by department: https://www.data.gouv.fr/datasets/historique-detaille-des-surfaces-cheptels-et-nombre-doperateurs-par-departement
- Géorisques API ICPE: https://georisques.gouv.fr/api/v1/installations_classees
- INCA3: https://www.data.gouv.fr/datasets/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-3
- Protein plan, 26 winners: https://www.reussir.fr/lesmarches/26-nouveaux-projets-soutenus-par-le-plan-proteines-vegetales
- Qualisol pulse supply chain (not downloadable): https://aude.chambre-agriculture.fr/fileadmin/user_upload/National/FAL_commun/publications/Occitanie/Productions_techniques/IRD210219-LARRIBEAU-QUALISOL-filiere-legumineuse-chez-Qualisol.pdf
