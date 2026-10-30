# Dossier Idea 7: French lentil, where and with whom to sow to replace imports

Date: 30/10/2026 (morning of the opening day). This dossier was built only with desk research and descriptive data exploration: no model was fitted, there is no cross-validation and no predictive results. Disposable scripts (not solution code, to be rewritten at the event): `comext.py`, `comext2.py`, `rpg_lec2.py`/`rpg_lec3.py` (LEC plots per year), `rpg_poly.py` (LEC polygons), `lec_stats.py` (join to communes and dynamics), `lec_parcel.py` (return and landscape of the previous year), `rotation.py` (previous crop per point), `entry.py` (communes that enter), in the scratchpad `plan7/scripts/`. The downloaded data was deleted at the end.

Labels: **[V]** verified by me today on the file, the API or the primary source; **[F]** read today in an open source but not checked against primary data; **[NV]** not verified; **[E]** own estimate with an explicit calculation; **[A]** assumption.

---

## 1. Summary in 5 lines + verdict

1. **Real gap:** France imported on average **40.8 kt/year of lentils for €46.4M (2023-2025), 45.8% from Canada** and exported 4.8 kt: net imports ~36 kt/year [V, Comext]. French area in 2025 is **35,690 ha across 8,591 plots and 2,853 communes, 41% organic** [V, RPG 2025].
2. **The buyer's problem is not just "more hectares": it is recruiting producers who stay.** Of the communes that grew lentils one year, only **53-72% grow them the following year** (2015-2025), and of the communes that entered in 2016-2020, only **19-33% are still active in ≥2 of 2023-2025** [V, RPG]. Vivien Paille (Avril) puts it this way: "Nos plus grands concurrents ne sont pas les autres acheteurs de légumes secs mais les autres cultures" (our biggest competitors are not the other dry-pulse buyers but the other crops) [V].
3. **Product:** for the supply manager of a cooperative or packer, a ranking of communes (and within them, eligible plots) where to recruit producers for next season. It combines the probability of adoption and persistence learned from the RPG 2015-2025 (temporal validation: "stopped at the end of 2021, whom would you have gone looking for?" and 2022-2025 is revealed), the rotation constraints (≥5 years without lentil or pea, Terres Inovia guide), the bruchid risk from the landscape (IOBC 2026) and the distance to silos (Géorisques).
4. **Tension that makes the optimisation interesting:** 81% of the communes that entered in 2022-2025 were ≤10 km from a commune growing lentils in 2021 (versus 51% at random) [V], so lentil spreads by contagion. But 78% of 2025 plots already have lentil from the previous year within ≤2 km [V], and bruchid density rises with the host area of the previous year (IOBC 2026) [V]. Recruiting "where it is easy" feeds the pest.
5. **Main risk (market, not technical):** Canadian lentil entered 2026 at **€0.75/kg CIF** (January-August) against **€0.81-0.87/kg paid to the French producer** [V], and in 2025 there was **"surproduction de lentilles vertes sèches bio"** (overproduction of organic dry green lentils) according to Agence Bio as cited by Reporterre [F]. More French supply only helps if there is a buyer who pays for French origin. Second risk: the label measures adoption, not agronomic suitability, and the "distance to existing lentil" baseline is strong.

**Verdict: CONDITIONAL GO, framed as "recruitment and retention of producers for a buyer that already pays for French origin" (packer or cooperative with a contract), in conventional.** It is the idea with the best verified data pipeline (the RPG gives 11 years of labels at commune and plot scale, without depending on 100 fields) and with a very saleable "blind replay" demo. It scores **6.1/10 weighted** (section 12): it narrowly beats idea 3 (6.0), and sits below idea 1 (6.4). It is not clearly a superior idea; its advantage is that the technical risk is low and the user is verified with quotes.

---

## 2. Problem, concrete user, decision

### The problem (with figures)
- **Deficit:** lentil imports (CN 07134000) 40,936 t (2023), 42,188 t (2024), 39,371 t (2025); value €48.0 / 49.3 / 42.1M; exports 4,938 / 4,361 / 5,032 t [V, Comext, updated 16/10/2026]. Average 2023-2025: Canada 18,681 t/year (45.8%, €1.03/kg), Belgium 13,166 t (32.2%, re-export hub), Turkey 2,661 t (6.5%) [V].
- **Import price falling:** January-July 2026, 19,508 t imported for €17.96M (€0.92/kg); Canada January-August 2026: 9,028 t for €6.74M (**€0.75/kg**) [V, Comext monthly]. The conventional French producer was paid €854 / 873 / 806 per tonne in the 2023/24, 24/25 and 25/26 seasons (Q4, "complet" price with réfactions (quality deductions) and bonuses) [V, FranceAgriMer]. **French grain is not cheaper than imported grain: it is sold for origin, quality or risk diversification.**
- **Production is moving:** RPG, lentil area by department (ha) [V]:

| Dept | 2015 | 2017 | 2020 | 2024 | 2025 | Reading |
|---|---|---|---|---|---|---|
| 10 Aube | 1,340 | 2,256 | 3,112 | 3,827 | 3,339 | +149% 2015-2025 |
| 43 Haute-Loire (AOP Puy) | 4,113 | 3,846 | 3,180 | 2,680 | 3,301 | -35% to 2024, rebound 2025 (-20% 2015-2025) |
| 36 Indre (IGP Berry) | 2,927 | 5,461 | 2,929 | 1,839 | 2,074 | -62% from the 2017 peak |
| 32 Gers | 771 | 1,770 | 3,203 | 1,102 | 714 | -78% from the 2020 peak |
| 02 Aisne | 18 | 111 | 223 | 771 | 952 | x53, Unéal / Vivien Paille area |
| 51 Marne | 398 | 1,508 | 1,917 | 2,596 | 2,550 | |
| 89 Yonne | 1,150 | 2,370 | 3,143 | 2,495 | 2,368 | |

  Note: the "Haute-Loire -35%" figure from the prior research is 2015-2024; with RPG 2025 it becomes -20%. The top-5 departments went from 60% of area (2015) to 38% (2025): lentil has deconcentrated [V].
- **Producer turnover (churn):** communes growing lentil that keep it the following year: 65% (2015→16), 72%, 63%, 65%, 61%, 59%, 53% (2021→22), 57%, 59%, 59% (2024→25) [V]. Communes that entered for the first time (no lentil since 2015) and are still active in ≥2 of 2023-2025: cohort 2016 33%, 2017 28%, 2018 25%, 2019 21%, 2020 19% [V].
- **Very uneven yield between basins:** SAA 2025 provisional, q/ha: Aube 22, Marne 22, Vendée 19.5, Indre 12, Yonne 10, **Haute-Loire 5.1** (and 3.5-7.75 in 2019-2025) [V]. Note: Aube, Marne and Haute-Marne have the exact same series for 2019-2025 (regional imputation) [V].
- **Bruchids:** 24.4% average bruchid-damaged grains at the 2025 harvest, with no authorised insecticide on lentil since 31/7/2024 [V in the idea 3 dossier, Terres Inovia source read via Chrome; not reopened today].

### Concrete user (verified with quotes)
**Supply manager ("approvisionnement" / "responsable filière légumes secs") of a packer or of a cooperative with a downstream contract**, who every winter has to secure N new hectares of lentil under contract and retain those they already have.

| Actor | What they do with French lentil | Source |
|---|---|---|
| Vivien Paille (Avril subsidiary, Valenciennes) | 15-20 kt/year of dry pulses out of ~180 kt (mostly rice). Trialled green lentil with Unéal on 40 ha (2023) and aimed for 100 ha in 2024, to reduce climate risk after having to import due to poor harvests in the South. ~30 production contracts for the 2024 harvest | Réussir, 12/2/2024 [V] |
| Sabarot-Wassner (Chaspuzac, Haute-Loire) | 80% French origin in pulses (20% fifteen years ago); raised the purchase price to producers by >25% in 2023 to convince them to sow lentil instead of soybean or maize; sorting capacity doubled to 40 kt/year, 80 kt possible by 2030 | Le Journal des Entreprises, 26/10/2023 [V] |
| Centre-Val de Loire Region + Axéréal (Cibèle) | "Filière locale lentilles vertes du Berry" contract: 55 producers, 925 ha, 49 communes in Indre and Cher (2025) | Axéréal, 10/7/2025 [V] |
| Graines Équitables (Aude, organic) | ~80 t unsold, "Faut-il dire à nos agriculteurs de ne pas semer pour l'an prochain ?" (should we tell our farmers not to sow for next year?) | Reporterre, 19/1/2026 [F] |
| NatUp / Lunor (Normandy), Euralis / Bonduelle | Three-party lentil contracts | [NV] (pages 404 or not opened today) |

Contracting: "La quasi-totalité de la collecte est contractualisée avec les acteurs de la filière aval" (almost all of the collection is contracted with downstream players), with contracts signed before sowing (Chambres d'agriculture, 24/9/2024) [V]. This matters: **the decision of where lentil will be grown is taken by the collector when signing contracts in winter**, not by the spot market.

### Decision
| Decision | When | What information today | Cost of getting it wrong |
|---|---|---|---|
| D1. Which communes and farms to send the field technician to to sign new contracts | Oct-Feb (sowing Mar-Apr; Chambres d'agriculture [V]) | The technician's personal network, cooperative members, intuition. No tool found (negative search, section 8) | Lost visits; producers who try one year and quit (cohorts: 19-33% stay) [V]; plots that break rotation (Aphanomyces) or sit in hot bruchid zones [A on the causality] |
| D2. How many ha to contract and where, to cover a target volume with diversified climate risk | Same time | Regional historical yield (imputed SAA) | Shortfall → import (Vivien Paille already had to [V]); surplus → unsold stock (2025 organic case [F]) |

The monetary cost of a visit or of a lost producer is not published: ask the mentors (section 11).

---

## 3. Hypotheses

| # | Hypothesis | Status | Evidence | If false |
|---|---|---|---|---|
| H1 | France imports ~40 kt/year of lentil (~€46M), ~46% from Canada | [V] | Comext 2023-2025: 40,832 t/year, €46.4M, Canada 45.8% | n/a |
| H2 | Buyers want more French lentil | **[V partial, with counterexample]** | Yes: Sabarot +25% producer price and 80% FR origin; Vivien Paille expanding to the North; Berry regional contract [V]. No: organic surplus 2025 and unsold stock in Aude [F] | Focus on conventional and on buyers with contracts (not organic spot). If a mentor says conventional is also in surplus, pivot to "retain" instead of "expand" |
| H3 | French lentil competes on price with imported lentil | **False** [V] | Canada €0.75/kg CIF 2026 vs French producer €0.81-0.87/kg | Assumed: the pitch is origin + climate diversification, not price |
| H4 | The RPG allows tracking lentil by commune and plot 2015-2025 | [V] | 89,425 LEC plots 2015-2025 downloaded via WFS in <1 min/year; 10 without commune (0.01%) | n/a |
| H5 | There are enough "events" to learn adoption/persistence | [V] | Pool of 28,546 communes without lentil 2015-2021; 1,920 entered in 2022-2025 (6.7%), 582 with ≥2 years (2.0%) | n/a |
| H6 | Entry is partly explained by proximity (contagion) | [V descriptive] | 81% of entrants ≤10 km from a lentil commune in 2021 vs 51% of non-entrants; median 5.7 vs 9.8 km | If the model does not beat distance, say so: the value moves to the constraints and to the €. |
| H7 | A model with more variables (crops, soil, climate, silos, organic, prior pea) beats the distance baseline in temporal precision@k | **[NV]** (not allowed to test beforehand) | No evidence | Fallback (section 7): rule-based ranking + constraints + honest replay |
| H8 | Persistence is an acceptable proxy for "suitability" | [A] weak | Mixes agronomy, price, contract and logistics. No open yield per plot | Call it "propensity to adopt and stay", never "agronomic suitability" |
| H9 | SAA yield works as a success label | **False at fine scale** [V] | Aube = Marne = Haute-Marne identical 2019-2025; only ~16 depts with ≥500 ha | Use SAA only as a regional yield prior, flagged as imputed |
| H10 | Agronomic rule: ≥5 years without lentil or another Aphanomyces host (pea, certain vetches) | [V] | Terres Inovia lentil guide 2023: "sur une même parcelle (minimum 5 ans)" (on the same plot, minimum 5 years) | n/a |
| H11 | Today the rule is often broken | [V] | 2025: 13.7% of LEC plots had LEC at the same point 1-4 years earlier; 17.7% at 1-5 years (polygons). Sample of 349 plots with 5 full years: 15.2% LEC and 20.3% LEC or pea in 2020-2024 | n/a |
| H12 | Typical previous crop: cereal | [V sample] | Sample of 377 LEC plots 2025: 2024 crop cereal ~71%, grassland/forage ~15%, oilseeds (rapeseed, sunflower) ~6%, pulses ~4% | n/a |
| H13 | More lentil nearby the previous year = more bruchids | [V on density, NV on damage] | IOBC 2026 (80 fields, 2 years): density positively related to the previous year's host area; the same year's area dilutes it | Show it as a constraint the user can choose, not as a € loss |
| H14 | Current plots fall outside the range of the INRAE dataset | [V] | 2025: 16.2% of LEC plots have >3.8% LEC of the previous year at 1 km (maximum of the INRAE dataset at 1 km) | Flag extrapolation |
| H15 | An existing tool already does this | [V negative search] | Terres Inovia has EVA and an Aphanomyces infection potential test (for pea); no lentil sourcing tool found | If one appears (cooperatives with in-house GIS), differentiate on the landscape part + validated replay |
| H16 | ICPE silos can serve as collection points | [V partial] | Aube: 52 of the first 1,000 ICPE have heading 2160/2260 with capacity in m³ (e.g. Soufflet Luyères 120,600 m³). They do not say whether they sort lentil | Use as a proxy for distance to collection; the user uploads their own sites |
| H17 | Lentil margin comparable to wheat in an average year | [E] | 15 q/ha × €830/t + €122 aid − €518 costs = **€849/ha**; at 8 q/ha €268/ha; at 22 q/ha €1,430/ha. Coupled aid 2025: €122 (Réussir, JO 28/2/2026) [V]; costs €518/ha (TI guide 2023) [V today on the mirror PDF, prior figure only] | Slider; the wheat number is [F] from the prior research |
| H18 | The project does not fall into excluded topics | [A] | It is not insects as food or feed; it is sourcing of human food | Confirm on Friday, same as idea 3 |
| H19 | A temporal replay 2021→2022-2025 is honest | [V design] | Training labels end in 2021; features only ≤2021 (section 5) | n/a |

---

## 4. Datasets

### 4.1 RPG plots, WFS Geoplateforme (core)
- **URL:** `https://data.geopf.fr/wfs/ows`, no key [V]. Layers `RPG.2015..2024:parcelles_graphiques` and `RPG.LATEST:parcelles_graphiques` (= 2025) [V GetCapabilities today]. Licence Ouverte (IGN) [F].
- **2025 schema differs** [V DescribeFeatureType]: `num_parcel, num_ilot, surf_parc, cat_cult_p, code_cultu, code_group, culture_d1, culture_d2, precision, gcp, pp, bio, iae, geom`. **There is no `id_parcel` in 2025**: `SORTBY=id_parcel` returns HTTP 400 (this happened to me today); use `SORTBY=num_ilot,num_parcel`. 2019-2024 use `id_parcel` (not stable across years) and 2022 names the geometry `the_geom` [V prior].
- **LEC counts** [V, `RESULTTYPE=hits` and download]: 5,840 (2015), 6,137, 8,722, 9,489, 9,388, 9,249, 8,851, 7,485, 7,596, 8,077, **8,591 (2025)**. Area: 17,179 ha (2015), 37,529 (2019, peak), 28,671 (2023), 34,226 (2024), **35,690 (2025)**. Median plot 2.4 ha (2025).
- **Organic (2025 only):** 37.2% of plots and 41.2% of lentil area are organic; 0 nulls [V]. Matches Agence Bio ~14,100 ha organic 2025 [V prior] and "40 % des surfaces" from Terres Univia in Reporterre [F].
- **Timing:** all LEC of one year, with geometry, in 25-55 s (2 pages of 5,000); polygons ~8-10 MB/year in GeoJSON [V]. All plots in a box like Aube (47.92-48.72 N, 3.38-4.86 E): 128,301 plots in 2025, 127,336 in 2024; **one page of 5,000 takes ~4 s and weighs 5.3 MB** → ~2 min and ~140 MB per year and basin [V].
- **Query by point (previous crop):** `BBOX=x-1,y-1,x+1,y+1,urn:ogc:def:crs:EPSG::2154` with `SRSNAME=EPSG:2154` works (x,y order in 2154) [V]. 2,000 queries with 8 threads: 347 s, **6% errors** (ERR) that have to be retried [V].
- **Join to communes:** representative point inside geo.api.gouv.fr polygons: 10 of 89,425 without commune [V].
- **Gotchas:** RPG year N comes out around September N+1 (today the latest is 2025 [V]); only plots declared to the CAP; geometries change between years (use point-in-polygon, not ids); `culture_d1/d2` (secondary crops) not used.
- **Friday commands:**
```bash
# LEC + PHI/PPR/PHS (Aphanomyces hosts) + FVL/FVP/FEV, all years, polygons
python src/ingest_rpg.py --codes LEC PHI PPR PPT PHS FVL FVP FEV --years 2015-2025 --out data/raw/rpg/
#   internally: TYPENAMES=RPG.{y}:parcelles_graphiques (2025 -> RPG.LATEST), CQL_FILTER=code_cultu='LEC',
#   COUNT=5000, STARTINDEX paginated, SORTBY=id_parcel (2025: num_ilot,num_parcel), SRSNAME=EPSG:2154
# All plots in the demo basin, 2019-2025 (~2 min/year, ~140 MB/year)
python src/ingest_rpg.py --bbox 47.92,3.38,48.72,4.86 --years 2019-2025 --out data/raw/rpg_basin/
```

### 4.2 Communes (geo.api.gouv.fr)
- `https://geo.api.gouv.fr/departements/{dep}/communes?fields=code,nom,codeDepartement&format=geojson&geometry=contour` [V]. **The unfiltered national call with outline is prohibited** ("This endpoint does not support an unfiltered API call with a geojson format output") [V]. 96 metropolitan departments in ~1 min, **277 MB** in total, 34,746 communes [V]. Licence: IGN/Etalab data [NV exact].
- Lighter alternative for the event: simplified ADMIN EXPRESS COG via the same WFS (not tested today) [NV].
```bash
for d in 01 02 ... 2A 2B ... 95; do curl -s "https://geo.api.gouv.fr/departements/$d/communes?fields=code,nom,codeDepartement&format=geojson&geometry=contour" -o data/raw/communes/$d.geojson; done
```

### 4.3 Eurostat Comext DS-045409 (motivation and impact)
- `https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409?format=JSON&freq=A&reporter=FR&product=07134000&flow=1&indicators=QUANTITY_IN_100KG&indicators=VALUE_IN_EUROS&time=2023&time=2024&time=2025` [V, 17 KB, updated 2026-10-16]. Monthly: `freq=M&sinceTimePeriod=2026-01&partner=WORLD&partner=CA` [V, data up to 2026-07 (WORLD) and 2026-08 (CA)].
- Units: quantity in 100 kg (divide by 10 for t), value in € [V]. Eurostat reuse licence [F prior]. Gotcha: Belgium is a hub (32%); the real origin is hidden [F prior].

### 4.4 FranceAgriMer, prices paid to producers
- xlsx 265 KB (URL in section 13), sheet "Publication nationale", `header=10` [V]. Lentil Q4: 854 (23/24), 873 (24/25), 806.1 (25/26) €/t; soft wheat Q4 25/26: €169.8/t [V]. Conventional, "complet" price. "Tous droits réservés", cite the source [F prior].

### 4.5 Agreste SAA long series (yield prior)
- ZIP 7.1 MB: `https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAA-SeriesLongues/SAA-SeriesLongues-2010-2025_DonneesProvisoires-DepartementalesRegionales.zip` [V today, xlsx dated 10/07/2026]. Tab `COP`, row `40 - Lentilles (y compris semences)` (lentils, including seed), `header=5`, columns `SURF_2010..2025`, `REND_..`, `PROD_..`, `STATUT_QUALITE` (1 reliable, 2 fragile) [V].
- 16 departments with ≥500 ha in 2024 [V]. Imputation: Aube/Marne/Haute-Marne series identical [V]. Only as a regional prior.

### 4.6 Géorisques ICPE (collection sites)
- `https://georisques.gouv.fr/api/v1/installations_classees?departement=10&page=1&page_size=1000` [V]: 1,032 installations in Aube, fields `raisonSociale, codeInsee, latitude, longitude, etatActivite, rubriques[numeroRubrique, quantiteTotale, unite]`. 52 of the first 1,000 with 2160 (silos, m³) or 2260 (drying, kW). **Page 2 returned "Request Rejected" (WAF) twice in a row** [V]: on Friday, download with pauses (≥5 s) and a smaller `page_size`, and cache.
- Gotcha: it does not say which grain or whether lentil is sorted; silos under declaration regime are not included [F prior].

### 4.7 INRAE bruchid dataset (only to justify the landscape layer)
- doi 10.57745/HPEMYW, etalab 2.0, 100 fields [V in dossier 3]. Nothing is trained on it here: its landscape range (max 3.8% LEC of the previous year at 1 km) is used to flag extrapolation, and the IOBC result as justification.

### 4.8 Climate and soil (optional, cut list)
- SIM2 Météo-France `QUOT_SIM2_latest.csv.gz` (19.9 MB, lov2) [V in dossier 3]. Useful for commune normals (8 km grid). If there is no time, lat/lon + department capture almost the same at commune scale.
- Soil: SoilGrids per point tested in prior research (pH, clay) [V prior]; CaCO3 missing. **Not tested at the scale of 30,000 communes**: goes to the cut list.

### 4.9 Previous derived table
- `archive/research/datasets/rpg_pulses_dept_year.csv` (2015-2024, department × group). It has to be declared. The RPG 2025 I downloaded today extends it.

### 4.10 Joins tested today
| Join | Key | Result |
|---|---|---|
| RPG LEC → commune | representative point ∈ polygon | 99.99% [V] |
| RPG LEC year t → LEC years t-1..t-6 | point ∈ polygon | [V], basis of the 5-year rule |
| RPG LEC 2025 → all crops 2020-2024 | BBOX 2 m + contains | 94% OK, 6% ERR to retry [V] |
| Commune → department → SAA | `codeDepartement` = prefix of `LIB_DEP` ("010 - Aube" → `10`) | [V format] |
| Commune → ICPE | lat/lon distance | [V coordinates present] |

---

## 5. AI method

**Main unit:** candidate commune (no lentil in the 4 previous years). **Secondary unit:** eligible plot within a chosen commune (filters and scores only, no own training).

**Targets (defined before looking at test):**
- `y_entry`: the commune has LEC in T+1 or T+2.
- `y_persist` (main): enters in T+1..T+2 **and** has LEC in ≥2 of the years T+1..T+4. National base rate with T=2021: 2.0% (582 / 28,546) [V].
- What is NOT a target: yield (imputed SAA), bruchid damage (no per-plot data).

**Snapshots and leakage:**
| Role | Snapshot T | Features with data | Labels use |
|---|---|---|---|
| Train | 2016, 2017 | ≤T | 2017-2021 |
| Test (replay) | 2021 | ≤2021 | 2022-2025 |

No train label uses years >2021, so the replay is what would have been known at the end of 2021. Leakage to watch: (1) "spatial" features computed with future years (for example normalising with 2015-2025 means): forbidden; (2) RPG 2025 carries `bio` and 2015-2024 do not: do not use `bio` as a feature in the replay; (3) 2026 commune boundaries applied to 2015 (commune mergers): acceptable, declare it.

**Features (all ≤T):**
- Contagion: distance to the nearest lentil commune at T; ha of LEC within 5/10/20 km at T and T-1; department trend.
- Cropping system (demo basin, or national if time allows): % cereals, % grassland, % rapeseed, presence of pea/faba bean (hosts and "pulse culture"), average plot size.
- Logistics: distance to the nearest ICPE silo and capacity within 30 km.
- Yield prior: mean departmental SAA yield ≤T and its `STATUT_QUALITE`.
- Optional: SIM2 climate normals, lat/lon.

**Baselines (same metric):**
- B0: chance (precision = base rate).
- B1: distance to the nearest lentil at T (the strong baseline: 81% of entrants within ≤10 km [V]).
- B2: ha of LEC within 10 km × department trend.

**Models, justified by n:** ~28,000 candidates per snapshot, ~2% positive → ~500 positives per snapshot. Enough for:
- Regularised logistic regression (interpretable, coefficients with CIs).
- LightGBM with high `min_child_samples` and an imposed monotonicity in distance (further away, lower propensity), evaluated against the logistic.
- **Positive-unlabelled**: a commune without lentil is not "unsuitable", it may simply not have had an offer. No formal PU is needed to rank (order is preserved under PU with random selection), but it is needed so as **not to call the score "suitability probability"**. It is reported as propensity.

**Validation:** temporal replay T=2021 (single, honest test). Within train, validation by spatial blocks (department) to choose hyperparameters. **Intervals:** bootstrap by department of the metrics.

**Metrics:**
1. Precision@k and recall@k (k = 50, 200, 500 communes) on `y_persist`, against B0-B2.
2. "Persistent ha captured in the top-k": 2022-2025 LEC ha in the recommended communes.
3. Calibration by deciles (to convert to "expected ha").
4. For the bruchid layer: there is no damage metric; the exposure (% LEC of the previous year at 1-2 km) of the recommended portfolio is reported.

**Optimisation (what makes it a tool and not just a ranking):** given a collection site and an ha target:
- maximise Σ propensity × eligible available ha × yield prior × price − distance cost [A];
- subject to: eligible plot (previous crop cereal/grassland; no LEC or pea in 5 years; distance ≤R km);
- and to a bruchid exposure cap chosen by the user (% LEC of the previous year at 1 km ≤ threshold; default 3.8%, the maximum observed by INRAE).
- Result: the **frontier** "expected ha vs bruchid exposure": how much volume is lost by moving away from hot zones. Solver: greedy by ratio (sufficient and explainable) or `pulp` if time allows.

**What the AI adds:** without a model, the technician goes where lentil already is (B1) and sees neither rotation nor landscape. With the model: (1) a ranking validated on a year it did not see; (2) the translation into expected ha and t; (3) the volume-risk frontier. If the model does not beat B1, the tool still filters eligible plots and shows the frontier, but the "AI" part loses weight (section 12).

**Explainability:** logistic coefficients; GBM SHAP per commune ("4 km from 300 ha of lentil, 70% cereal, silo 8 km away"); for the plot, explicit rules (rotation, landscape).

---

## 6. MVP and demo

**Stack:** Python, geopandas, scikit-learn + LightGBM, Streamlit + pydeck (or folium), parquet/GeoParquet cache. AWS: S3 for data and EC2/App Runner for the demo with a public URL; backup before Sunday 12:00. Optional Bedrock: French summary of the commune profile (not "the AI").

**Screens:**
1. **"Déficit" (deficit)**: imports 2015-2026 (Comext), CIF price Canada vs French producer price, lentil map 2015 vs 2025 (shift to Champagne and Aisne).
2. **"Où recruter" (where to recruit)**: the user chooses a collection site (by default a real ICPE silo in Aube or Aisne) and an ha target. Map of communes with propensity, top-20 table with expected ha and interval, sliders for radius, bruchid threshold and price.
3. **"Parcelles éligibles" (eligible plots)**: within the chosen commune, RPG 2025 plots with cereal previous crop, no LEC/pea in 5 years, with their % LEC of the previous year at 1 km (dotted border if >3.8%, "extrapolation").
4. **"Replay & fiabilité" (replay & reliability)**: "end 2021": top-k of the model and of B1, and a "révéler 2022-2025" (reveal 2022-2025) button that paints the communes that actually entered and stayed. Precision@k with interval, volume-bruchid frontier, provenance table (measured / source / assumption / synthetic).

**Demo script (80 s within the 4 min):**
1. (10 s) "Je suis acheteuse chez un conditionneur. Fin 2021, je veux 300 ha de lentilles en plus autour de ce silo de l'Aube." (I am a buyer at a packer. End 2021, I want 300 extra ha of lentils around this Aube silo.)
2. (25 s) Screen 2: top-20 communes, expected ha. I move the bruchid threshold: the volume drops from X to Y ha. "Voilà le prix d'éloigner les nouvelles lentilles des foyers de bruche." (That is the price of keeping new lentils away from bruchid hotspots.)
3. (20 s) Screen 4: "révéler 2022-2025". The model's communes that actually entered and stayed, against B1. The real number, whatever it is.
4. (25 s) Screen 3: one commune, its eligible plots in 2025, one discarded for lentil 3 years ago, another for 6% lentil at 1 km the previous year.

**Plan B:** 60 s video recorded on Saturday; everything cached in parquet (no live WFS).

**Repo:**
```
lentille-sourcing/
  README.md                 # provenance, prior resources, how to run
  src/ingest_rpg.py         # paginated WFS by code / bbox, 2025 with num_ilot
  src/ingest_admin.py       # geo.api communes, ICPE, Comext, FranceAgriMer, SAA
  src/history.py            # point-in-polygon: years since LEC/pea, previous crop
  src/features.py           # snapshot T: contagion, crops, silos, SAA
  src/labels.py             # y_entry, y_persist
  src/model.py              # baselines + logistic + LightGBM
  src/evaluate.py           # replay 2021, precision@k, bootstrap by dept
  src/optimize.py           # greedy with constraints + bruchid frontier
  app/streamlit_app.py
  reports/metrics.json
```

---

## 7. Hour-by-hour plan

Roles: **A** geo data (RPG, histories), **B** modelling and evaluation (ML/CV student), **C** product, business and pitch.

### Friday 30/10
| Time | A | B | C |
|---|---|---|---|
| 17:45-20:45 | Welcome. Declare prior resources | Ask mentors: cost of recruiting a producer, whether conventional is also in surplus (H2) | Deck template, repo, channel |
| 20:45-21:30 | `ingest_rpg.py` LEC + pea 2015-2025 (background, ~15 min) | Freeze targets, snapshots, baselines and go/no-go rule in the README | Declare track before 23:00. Streamlit skeleton |
| 21:30-23:00 | Communes (geo.api, ~1 min) + join; `labels.py` | `features.py` contagion (LEC only) + B0/B1/B2 in the replay | Comext, FranceAgriMer, SAA in clean tables (screen 1) |
| **23:00 checkpoint 0** | Commune × year table and labels with the counts from this dossier (1,920 / 582) | | |
| night (off-site) | Download all plots of the demo basin 2019-2025 (~15 min) | | |

### Saturday 31/10
| Time | A | B | C |
|---|---|---|---|
| 9:30-10:15 | Workshop (one person takes notes) | | |
| 10:15-13:00 | `history.py` for basin plots (years since LEC/pea, previous crop), ICPE with pauses | Logistics + LightGBM; crop (basin) and silo features | Screens 1 and 2 with real data |
| **13:00 GO/NO-GO** | **GO** if the best model beats B1 on precision@200 of `y_persist` by ≥20% relative **and** the bootstrap CI does not cross B1. **NO-GO**: fallback | | |
| 14:00-16:00 | Landscape layer (LEC t-1 at 1 and 2 km) for candidate plots | `optimize.py` + frontier; SHAP | Screen 3 |
| 16:00-18:00 | Leakage review; provenance table | Final metrics to `metrics.json` | Screen 4 + AWS deploy |
| **18:00 checkpoint 2** | End-to-end demo at a public URL | | |
| 19:00-24:00 (off-site) | Online profile | Backup video, cache | Deck v1, script, 3 rehearsals |

### Sunday 1/11
| Time | Everyone |
|---|---|
| 8:30-9:15 | Final numbers from `metrics.json`, PDF with links, online profile |
| **9:15** | Upload. **Deadline 9:30** |
| 9:30-10:15 | Rehearsal, demo on another machine |
| 12:00 | AWS backup |

**Fallback (NO-GO):** "Lentille Sourcing Desk: carte d'éligibilité + frontière volume/bruche" (eligibility map + volume/bruchid frontier). The ranking becomes B1 (contagion) plus rotation and landscape filters; the AI is limited to the calibrated prior of expected ha. Said in the pitch: "à l'échelle commune, la proximité explique l'essentiel de l'adoption ; ce qui manque ce sont les données de contrats des collecteurs" (at commune scale, proximity explains most of adoption; what is missing is collectors' contract data).

**Cut list (first things first):** soil and climate → Bedrock → `pulp` solver (greedy remains) → national crops (only the basin remains) → LightGBM (logistic remains) → animated screen 1. **Never cut:** baselines, 2021 replay, provenance table, video.

---

## 8. Business

- **Value proposition:** "Trouver les bons producteurs de lentilles, au bon endroit, et les garder: un ciblage validé sur 10 ans de RPG, qui respecte la rotation et éloigne les nouvelles parcelles des foyers de bruche." (Find the right lentil producers, in the right place, and keep them: targeting validated on 10 years of RPG, that respects rotation and keeps new plots away from bruchid hotspots.)
- **Who pays:**
  1. Packers with a France-origin policy (Sabarot-Wassner, Vivien Paille/Avril) [V that they have it].
  2. Cooperatives with lentil contracts (Axéréal, Unéal, NatUp, Euralis, CAVAC, Qualisol) [V Axéréal and Unéal; rest NV].
  3. Regions that finance sector contracts (Centre-Val de Loire, Berry contract) [V].
- **Pricing [A]:** annual licence per buyer of €5-15k (equivalent to a fraction of a technician). Benchmark: xarvio ~€5-10/ha/year (secondary source, prior research) [F]. I did not find published prices for sourcing tools.
- **Market size [E]:** for lentil alone, of the order of 20-40 buyers × €5-15k = €0.1-0.6M/year. **Small.** Scaling is the same engine for other diversification crops with contracts (chickpea, dry bean, quinoa, hemp, buckwheat): all can be tracked in the RPG by code. That this would be a larger market is [A].
- **Adoption:** pilot with a buyer that hands over its historical georeferenced contracts (the real label of "producer who stayed"), replay on its data, then a real recruitment season.
- **Competitors:**

| Existing | What it does | Difference |
|---|---|---|
| Technician + partner network (today's practice) | Recruitment by proximity | It is our baseline B1; we add rotation, landscape and validation |
| Terres Inovia EVA / infection potential test [F] | Aphanomyces risk per plot (pea) | Complementary: input for the rotation rule |
| Cooperatives' internal GIS [NV] | Member maps | No adoption model and no data beyond their members (the RPG sees everyone) |
| Generic farm-data platforms [NV] | Plot management | Not oriented to sourcing a single crop |

---

## 9. Quantified impact

- **Net imports [V/E]:** 40,832 − 4,777 = **~36 kt/year** (2023-2025), ~€46M of gross imports.
- **Hectares to replace 10 kt [E]:** at 15 q/ha (national average 2025, Terres Univia via prior research [F]) → 6,700 ha (+19% on 35,690 ha). At 22 q/ha (Champagne 2024-25, imputed SAA) → 4,500 ha.
- **Retention [E, illustrative]:** if of 1,000 newly recruited ha ~25% are still growing it in year 3 (order of the 2018-2019 cohorts [V at commune level]) and the tool raised it to 35% [A], that would be +100 stable ha ≈ 150 t/year at 15 q/ha ≈ €125k/year at €830/t, per 1,000 ha recruited. Labelled as a scenario.
- **Agronomy:** 13.7-17.7% of 2025 lentil was sown with a return <5-6 years [V]; filtering that reduces Aphanomyces risk (no figure for avoided loss) [A].
- **Bruchids:** 16% of 2025 plots are in landscapes more loaded than any of the 100 INRAE fields [V]. Moving recruitment away from those hotspots is consistent with IOBC; the effect on damage is not quantified [NV].
- **Producer income [E]:** gross margin €849/ha at 15 q/ha (range 268-1,430). Yield risk (Haute-Loire 3.5-7.75 q/ha vs Champagne 8-22) is the most plausible reason for abandonment [A].
- **CO2:** Agribalyse does not distinguish origin for pulses [F prior]; I give no figure.

---

## 10. Pitch

### Script (4:00)
| Time | Content |
|---|---|
| 0:00-0:40 | **Problem.** "La France importe 41 000 tonnes de lentilles par an, 46 % du Canada. Les acheteurs veulent de l'origine France, mais leurs producteurs partent: dans les communes qui ont essayé la lentille en 2018, une sur quatre seulement en cultive encore." (France imports 41,000 tonnes of lentils a year, 46% from Canada. Buyers want French origin, but their producers leave: in communes that tried lentil in 2018, only one in four still grows it.) Persona: "Claire, acheteuse légumes secs" (Claire, dry pulses buyer). |
| 0:40-1:20 | **Solution.** 10 years of RPG (89,000 lentil plots), rotation, bruchids, silos. "Où recruter, quelles parcelles, et à quel coût de risque bruche." (Where to recruit, which plots, and at what bruchid risk cost.) |
| 1:20-2:40 | **Demo** (script in section 6). |
| 2:40-3:20 | **Rigour.** "Entraîné jusqu'en 2021, testé sur 2022-2025." (Trained up to 2021, tested on 2022-2025.) Against the "go near what exists" rule. Limits: propensity, not suitability; imputed SAA yields; bruchids on density, not damage. |
| 3:20-4:00 | **Scale and business.** Pilot with a packer's contracts; same engine for chickpea and dry bean; Regions that finance sectors. "Le canadien entre à 0,75 €/kg: sans fidéliser les producteurs, l'origine France ne tient pas." (Canadian lentil enters at €0.75/kg: without keeping producers, French origin does not hold.) |

### Slides
1. Title, team, track 3. 2. Deficit and CIF price vs producer. 3. User and quotes (Vivien Paille, Sabarot, Berry). 4. Data and provenance. 5. Method (snapshots, leakage, baselines). 6. Replay results (real). 7. Volume-bruchid frontier. 8. Demo. 9. Impact (labelled [E]). 10. Business. 11. Limits, sources, prior resources.

### Likely jury questions
- **"Why not simply go where lentil already is?"** Because the bruchid pressure rises there the following year (IOBC), and because the producers who left are there. We show how much the model gains over that rule (or that it does not gain, and why).
- **"Does persistence measure suitability?"** No. It measures successful adoption, which is what the buyer cares about. For pure agronomic suitability, per-plot yields would be needed (collectors have them).
- **"If organic lentil is in surplus, why more?"** That is why we aim at conventional and at buyers with contracts. The Canadian price means the risk is losing producers, not lacking a market.
- **"What about the RPG 2026?"** It comes out around September 2027. To recruit for winter 2026-27 we use RPG 2025 plus the buyer's own contracts.
- **"Are insects excluded?"** It is protection of a food crop; bruchids are only one risk layer.

---

## 11. Risks, questions, resources, checklist

### Risks
| Risk | Prob. | Mitigation |
|---|---|---|
| The market does not want more lentil (organic in surplus, Canada €0.75/kg) | Medium-high | Retention framing and conventional; ask mentors on Friday |
| The model does not beat B1 | Medium-high | Go/no-go at 13:00, fallback, honest report |
| Jury: "it's a map with rules" | Medium | Blind replay + optimisation frontier |
| WFS errors (6% in point queries, 400 from the 2025 schema) | Medium | Retries, cache, `num_ilot` in 2025 |
| Géorisques WAF | Medium | Pauses, cache, or manual list of 10 silos |
| Commune mergers 2015-2026 | Low | Use current boundaries, declare it |
| Weight of geo.api (277 MB) | Low | Simplified ADMIN EXPRESS or only the basin's departments |

### Questions for mentors
1. Does conventional lentil also end up in surplus in 2025-26, or only organic?
2. How much does it cost to recruit a new producer (visits, seed, support) and how many leave after the first year?
3. Would buyers keep/share their historical georeferenced contracts?
4. What is the maximum plot-to-sorting-centre distance they accept?
5. Does the 5-year delay in practice include pea and faba bean?
6. Contact at Vivien Paille, Sabarot, Unéal or Axéréal?

### Prior resources to declare
- Desk research: this dossier, `archive/research/plans/3_bruchids.md`, `archive/research/datasets*.md`, `archive/research/track3_context.md`.
- Derived table `archive/research/datasets/rpg_pulses_dept_year.csv`.
- Today's descriptive exploration (RPG counts, commune churn, return, landscape of the previous year, previous-crop sample, Comext). Disposable scripts, not reused.
- Libraries: geopandas, shapely, pandas, scikit-learn, lightgbm, streamlit, pydeck.

### Checklist (Sunday 9:30)
- [ ] Deck PDF from the template with links to the repo and the demo
- [ ] Online project profile
- [ ] Public repo with README (provenance, prior resources)
- [ ] `reports/metrics.json` with the replay and the baselines
- [ ] Demo deployed + backup video
- [ ] Measured / source / assumption / synthetic table
- [ ] Open and verified sources
- [ ] AWS backup before 12:00

---

## 12. Rubric

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Impact and sustainability | 30% | 6 | Verified import gap and protein sovereignty; attacks a real bottleneck (abandonment). But the organic counterexample and the Canadian price weaken "more supply = fewer imports", and the effect in t is a scenario |
| Scientific and technical rigour | 20% | 6.5 | 11 years of RPG, clean temporal replay, leakage listed, joins tested. The label is a proxy (propensity, not suitability), with no per-plot yield and bruchids only on density |
| Appropriate and essential AI | 20% | 6.5 | Spatio-temporal + constrained optimisation is natural AI for the problem and n is enough (~500 positives/snapshot). The contagion baseline is strong: if it wins, the AI becomes secondary |
| Economic viability | 20% | 5 | User with verbatim quotes and a buyer that pays for origin; small lentil market (€0.1-0.6M), multi-crop scaling is [A] |
| Execution and pitch | 10% | 7.5 | Pipeline tested today (downloads in minutes), attractive map, convincing "reveal" replay |
| **Weighted total** | | **6.1** | 0.3×6 + 0.2×6.5 + 0.2×6.5 + 0.2×5 + 0.1×7.5 = 6.15 |

**Comparison:** idea 1 (6.4): better on AI (6.5, equal) and on viability (5.5 vs 5), with similar impact; this idea wins on execution. Idea 3 (6.0): this one has much more abundant data (89,000 plots vs 100 fields) and lower technical risk, but a less acute problem than "24% bruchid-damaged grains". **It does not beat idea 1; it beats idea 3 by a margin within the error of the self-assessment.** Scenarios: if the GO works out and a mentor confirms that conventional is not in surplus, impact 6.5 and AI 7 → ~6.4. With fallback, AI 4.5 → ~5.7.

Suggested combination: use this idea's landscape layer as the "sowing screen" (D2) of idea 3; idea 3 provides the acute problem and this one the abundant data.

---

## 13. Sources (open today)

- Eurostat Comext DS-045409 (API): https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409
- WFS Geoplateforme RPG (GetCapabilities, DescribeFeatureType `RPG.LATEST:parcelles_graphiques`, GetFeature 2015-2025): https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities
- geo.api.gouv.fr, communes by department: https://geo.api.gouv.fr/departements/10/communes?fields=code,nom,codeDepartement&format=geojson&geometry=contour
- Géorisques API ICPE: https://georisques.gouv.fr/api/v1/installations_classees?departement=10&page=1&page_size=1000
- FranceAgriMer, quarterly prices to producers: https://visionet.franceagrimer.fr/Pages/OpenDocument.aspx?fileurl=SeriesChronologiques%2fproductions%20vegetales%2fgrandes%20cultures%2fprix%20pay%c3%a9s%20aux%20producteurs%2fSCR-CER-HISTOPRIXTRIMESTRIELS-C25-26.xlsx&telechargersanscomptage=oui
- Agreste SAA long series 2010-2025: https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAA-SeriesLongues/SAA-SeriesLongues-2010-2025_DonneesProvisoires-DepartementalesRegionales.zip
- Terres Inovia lentil guide 2023 (germineo mirror), "minimum 5 ans", soils: https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/LENTILLE-2023-Guide-culture-TERRES-INOVIA.pdf
- Réussir, "Comment Vivien Paille développe ses approvisionnements" (12/2/2024): https://www.reussir.fr/lesmarches/comment-vivien-paille-developpe-ses-approvisionnements
- La Gazette France, Vivien Paille (13/5/2024): https://www.lagazettefrance.fr/article/vivien-paille-les-mains-dans-les-rayons-et-les-pieds-dans-les-champs
- Le Journal des Entreprises, "Sabarot aiguise son appétit sur le marché des légumineuses" (26/10/2023): https://www.lejournaldesentreprises.com/article/sabarot-aiguise-son-appetit-sur-le-marche-des-legumineuses-2072557
- Axéréal, contract "Filière locale lentilles vertes du Berry" (10/7/2025): https://www.axereal.com/en/news/signing-contract-filiere-locales-lentilles-vertes-du-berry-cibele
- Chambres d'agriculture, "La production de lentilles en France" (24/9/2024, upd. 29/10/2024): https://chambres-agriculture.fr/actualites/actualite/la-production-de-lentilles-en-france
- Reporterre, "Moins chère, aspergée de pesticides : la lentille canadienne met à mal la filière française" (19/1/2026): https://reporterre.net/Moins-chere-aspergee-de-pesticides-la-lentille-canadienne-met-a-mal-la-filiere-francaise
- Le Tribunal du Net (21/11/2025), unsold organic lentil in Aude (low-quality press, only as a signal): https://www.letribunaldunet.fr/societe/lentilles-bio-francaises-importations-canada-2025.html
- Réussir, coupled plant aids 2025 (€122, JO 28/2/2026): https://www.reussir.fr/pac-quel-montant-des-aides-couplees-vegetales-pour-la-campagne-2025
- Herrera et al. 2026, IOBC-WPRS Bulletin 182:97-101: https://iobc-wprs.org/product/managing-populations-of-bruchid-pests-in-grain-legumes-role-of-resource-provisioning-at-field-and-landscape-levels/
- Participant Guide Hack the Fork 2026 (local): `event/participant_guide.txt`
- Sources from idea 3 reused without reopening today (bruchid damage 2025, INRAE): see `archive/research/plans/3_bruchids.md`, section 13.

Failed attempts: europe1.fr (403; the figure "Vivien Paille €900/t with Unéal" was left **unverified** and is not used), Terres Inovia 2026 PDF "Maîtriser la culture de la lentille" (403 also with a browser user-agent), Réussir NatUp (404), terre-net aides couplées (502), SEMAE dry-pulse note 2026 (PDF without extractable text), page 2 of Géorisques (WAF).
