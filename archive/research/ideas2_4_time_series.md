# Data audit: time series ideas (idea 4: early yield estimate, idea 2: climate analog seasons)

Date: 29 October 2026. Track 3 "Protein sovereignty", Hack the Fork Paris.
Scope: data inspection and document research. No model was fitted and no backtest was computed (event rule).

Legend: **[V]** verified by me by opening the file or the API. **[S]** taken from a cited web source (read directly or through a search engine). **[NV]** not verified: stated by a secondary source or from my own memory, needs confirmation.

---

## 0. TL;DR

1. **The file exists and I opened it.** It is the ZIP "SAA séries longues 2010-2025, données provisoires, départementales et régionales" from Agreste (the French agricultural statistics service; SAA = Statistique Agricole Annuelle, annual agricultural statistics) (published 25/04/2024, updated 10/07/2026, "données arrêtées au 30/03/2026, données 2025 provisoires") [V]. It contains 16 seasons (2010 to 2025), 100 départements (departments), including 5 DROM (overseas departments), and for each crop the columns `SURF_` (ha), `REND_` (q/ha) and `PROD_` (q), plus a `STATUT_QUALITE` per row (1 = reliable, 2 = fragile, 3 = extrapolated and "only for totals") [V].
2. **The crop with data for a temporal holdout is field pea (pois protéagineux)** (38 departments with ≥500 ha, ≥7 of 9 train years 2010-2018 and 6 of 6 test years 2019-2024; 92% of the area with statut 1 (quality status 1)). Followed by faba bean (féverole) (28 departments, 66% statut 1) and soybean (16 departments, which is not a dry pulse for the track). **Lentil, chickpea and dry bean, which are the most "human food", have few departments and many imputed yields**: lentil 4 departments with ≥500 ha, chickpea 3, dry bean 1 [V].
3. **Strong imputation signals** in lentil and chickpea: ~51-53% of departmental yields (with ≥100 ha) are identical to that of another department in the same region in that same year (for wheat it is 17%). Example: Aube and Marne have exactly the same lentil series for 2019-2025 (19, 15, 8, 16, 16, 22, 22 q/ha); Charente and Charente-Maritime have the same chickpea series for 2016-2025 [V]. In other words: there are fewer independent observations than it seems.
4. **Climate:** Open-Meteo works without a key, ERA5-Land from 1950, ~7 days of lag. **But with `models=era5_land` precipitation comes back `null`** (ERA5-Land does not expose rain in Open-Meteo; you have to use `era5` or `era5_seamless`, at 0,25°) [V]. The free tier caps at 10,000 calls/day, and it counts requests longer than 2 weeks as several calls, so 16 years of daily data × dozens of points exceeds the limit [S]. **Better alternative for France: SAFRAN/SIM2 from Météo-France** (8 km, daily since 1958, rain, T, ETP (potential evapotranspiration) and soil wetness index SWI, annual files of ~137 MB under Licence Ouverte (open licence), updated today) [V].
5. **RPG:** since 2015 it goes down to the parcel level with crop type [S], which is useful for weighting climate by where each pulse is sown. RPG = Registre Parcellaire Graphique (the French agricultural parcel register). For the MVP, weighting by department is enough; the RPG is optional.
6. **Prior art:** JRC MARS already forecasts the yield of **field peas** every month at EU level (2,23 t/ha in September 2026, according to Reuters) [S]; I mark as [NV] that it also gives it by country. Agreste and the DRAAF (regional agriculture directorates) publish crop status reports and regional "prévisions de collecte" [collection forecasts] during the season [S]. The real gap is **departmental, specific to dry pulses for human consumption, open and explainable**. Do not sell it as "first pulse yield forecast".
7. **Verdict:** A = 6/10 viability with pea (3/10 if we insist on lentil as the main label). B = 7/10 technical, but with a scientific weakness: there are only 15 prior seasons as analog candidates. **Recommendation:** combine both into a single product ("which season is this one most like?" + estimate with interval), train and evaluate on **pea** (healthy data), show **lentil** as the human-use case with an explicit quality warning, and use the same climate variables as "risk drivers" for the bruche (bruchid beetle) idea.

---

## 1. Agreste SAA source: what is really there

### 1.1 File and download [V]
- Page: https://agreste.agriculture.gouv.fr/agreste-web/disaron/SAA-SeriesLongues/detail/
- ZIP (8 MB): https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAA-SeriesLongues/SAA-SeriesLongues-2010-2025_DonneesProvisoires-DepartementalesRegionales.zip
- Inside: `SAA_2010-2025_provisoires_donnees_departementales.xlsx` (11 MB) and `..._regionales.xlsx` (3,5 MB).
- Tabs: `COP` (cereals, oilseeds, protein crops), `FOU`, `IND`, `PDT`, `LEG` (vegetables), `FRT`, etc.
- Header in row 6: `LIB_REG2, LIB_DEP, LIB_SAA, STATUT_QUALITE, SURF_2010..SURF_2025, REND_2010..REND_2025, PROD_2010..PROD_2025`. The COP tab has 4.500 rows (45 products × 100 departments).
- Units (stated in the sheet itself): area in ha, production in quintals and yield in q/ha. There are no non-numeric values (not even "s" for secret); missing values are NaN.
- Warnings on the page: the series are "mettent en cohérence avec le recensement agricole 2020 puis rétropolées de 2010 à 2019" [“aligned with the 2020 agricultural census and then back-extrapolated from 2010 to 2019”], and since the provisional SAA 2025, the data from 2010 "ont fait l'objet de plusieurs ajustements" [“have been subject to several adjustments”]. **These are revised data, not what was known in real time.**
- Calendar: the provisional SAA comes out in spring and the final one in November ([SAA methodology](https://agreste.agriculture.gouv.fr/agreste-web/download/methode/S-SAA/Methodologie_Statistique-Agricole-Annuelle.pdf), p. 3). At the time of the event, **2025 is provisional and 2026 is not available yet**.
- Yield definition: yield "en récolte, au stade arrivée ferme" [“at harvest, at the firm-arrival stage”]. If there was no harvest due to hazards (aléas) without resowing, the area is counted with yield 0 (same methodology note). Pea is expressed at 14% moisture.
- Methodology note on use: "Les pois secs sont utilisés soit en alimentation humaine pour la casserie [...] soit pour l'alimentation animale" [“Dry peas are used either for human food, for casserie (pulse processing) [...] or for animal feed”]; the féverole "comprend pourtant les fèves destinées à l'alimentation humaine" [“nevertheless includes the faba beans intended for human food”]. **The SAA does not separate human and animal use.**

### 1.2 Statut qualité (quality status) [V]
Source: [Statut_qualité_SAA.pdf](https://agreste.agriculture.gouv.fr/agreste-web/download/methode/S-SAA/Statut_qualit%C3%A9_SAA.pdf)
- **1**: various sources, tested over time, "raisonnablement fiables" [“reasonably reliable”].
- **2**: partial sources, "plus fragiles" [“more fragile”], better used in totals.
- **3**: very partial sources, "extrapolées à partir des données des autres régions et/ou sur la base du dernier recensement agricole" [“extrapolated from the data of other regions and/or on the basis of the last agricultural census”], **"à utiliser exclusivement pour des totaux" [“to be used exclusively for totals”]**.
- The status is one per row (department × crop) and "reflète la qualité pour la dernière année publiée" [“reflects the quality for the last published year”]. There is no status per year.
- The note adds: "si les données de surface sont souvent bien connues, les données de rendements sont souvent plus difficiles à établir" [“if area data are often well known, yield data are often harder to establish”].

### 1.3 Pulse counts (COP tab, departmental) [V]

Script: `scratchpad/ts_scripts/count_pulses.py`. Full output in `scratchpad/ts_data/count_pulses_out.txt`.

| SAA product | National area 2010 → 2019 → 2025 (ha) | Depts with area>0 per year | Depts with ≥500 ha (2019-24) | Depts with valid yield and ≥500 ha in ≥7/9 train years and 6/6 test | Area in statut 1 / 2 / 3 (avg. 2019-24) | National yield min-max (q/ha) |
|---|---|---|---|---|---|---|
| 41 Pois protéagineux | 209.980 → 153.779 → 97.884 | 85-90 | 40-48 | **38** | 92% / 8% / 0% | 23,4 (2016) to 43,0 (2010) |
| 38 Féveroles et fèves | 151.342 → 63.118 → 112.231 | 82-90 | 41-47 | **28** | 66% / 34% / 0% | 19,3 (2020) to 45,1 (2012) |
| 33 Soja (oilseed, outside focus) | 49.736 → 163.800 → 150.155 | 62-86 | 39-44 | 16 | 95% / 5% / 0% | 20,4 to 30,0 |
| 42 Mélange de pois | 29.537 → 30.778 → 63.856 | 58-87 | 20-36 | 12 | 15% / 78% / 7% | 31,9 to 42,5 |
| 40 Lentilles | 12.186 → 38.014 → 33.927 | 57-87 | 14-18 | **4** (Indre, Yonne, Aube, Haute-Loire) | 58% / 29% / 13% | **8,2 (2020), 8,6 (2021)** to 17,0 |
| 43 Pois chiches | 2.781 → 33.204 → 27.645 | 21-80 | 11-17 | **3** (Aude, Gard, Hérault) | 44% / 38% / 18% | 12,9 to 18,6 |
| 39 Haricots secs | 3.353 → 7.615 → 7.254 | 44-71 | 3-4 | **1** (Vendée) | 22% / 43% / 36% | 18,0 to 25,0 |
| 44 Lupin doux | 6.273 → 2.910 → 3.765 | 42-63 | 1-4 | 1 | 26% / 73% / 1% | 20,8 to 28,8 |
| 45 Autres protéagineux | 0 until 2019 | 0 until 2019 | 0-1 | 0 | n/a | n/a |
| (ref.) 03 Total blé tendre | n/a | ~91 | ~91 | n/a | n/a | n/a |

Other useful counts:
- **Pea**: 83 departments with valid yield in all 16 years; 49 with ≥100 ha in all 16 years; 28 with ≥1000 ha in all 16 years.
- **Faba bean**: 52 departments with ≥100 ha in all 16 years, but only 3 with ≥1000 ha in all 16 years.
- **Lentil**: 16 departments with ≥100 ha in all 16 years and 3 with ≥500 ha in all 16 years.
- **Chickpea**: 6 departments with ≥100 ha in all 16 years and 0 with ≥1000 ha.
- Cells with area>0 almost always have yield. The "hard" missing values are few; the problem is quality, not NaNs.
- **Concentration**: the top 10 lentil departments add up to 63% of the 2019-24 area (Aube, Haute-Loire, Yonne, Indre, Gers, Marne, Vendée, Cher, Deux-Sèvres, Côte-d'Or). Chickpea: the top 8, 56% (Gers, Charente, Charente-Maritime, Hérault, Gard, Aude, Yonne, Haute-Garonne).

### 1.4 Imputation and break signals (the most important finding of the audit) [V]

Script: `scratchpad/ts_scripts/dups.py`. Among department-years with ≥100 ha:

| Crop | % of yield identical to that of another department in the same region that year | % identical to that of the same department the previous year | Test 2019-24: departments/year → distinct values |
|---|---|---|---|
| Field pea | 23,5% | 3,6% | 62,8 → 52,2 |
| Faba bean | 44,2% | 9,5% | 65,8 → 48,2 |
| Lentil | **51,1%** | 15,4% | 42,2 → **25,7** |
| Chickpea | **52,6%** | 14,3% | 32,0 → **20,2** |
| Dry bean | 25,0% | 25,5% | 15,3 → 12,8 |
| Soft wheat (ref.) | 16,9% | 1,6% | 91,0 → 82,5 |

Heads up: yields are usually integers, so part of the matches is chance, especially in crops with a narrow range (lentil from 5 to 25 q/ha). Even so, the specific cases are unambiguous:
- **Lentil**: Aube = Marne in 2019-2025 (19/15/8/16/16/22/22), and Aube with a fixed 25 q/ha from 2014 to 2018. Yonne ≈ Côte-d'Or (8; 3,5; 3 vs 2,5; 6; 9; 15). Indre and Cher with 23 and 19 repeated for three years (2021-23). Deux-Sèvres with 6, 6 and then 20.
- **Chickpea**: Charente = Charente-Maritime in 2016-2025; Aude, Gard and Hérault with almost constant values in 2014-2017 (16,88 / 17,33 / 17).
- **Dry bean**: Vendée = Maine-et-Loire in 2018-2023. Morbihan and Côtes-d'Armor have area linearly interpolated (+50 ha/year) and a fixed yield of 18,27 in 2022-25 (statut 3).
- **Break in 2020**: the number of departments with area jumps (lentil 74→87, chickpea 59→80, dry bean 55→71, pea mix 62→85). It is consistent with the realignment to the 2020 agricultural census (RA 2020).
- **Anomaly in pea, Oise**: yield from 9 to 16 q/ha in 2010-2019 and from 30 to 43 in 2020-2025. It is almost certainly a back-extrapolation artifact or an error. It must be excluded or corrected.
- **Chickpea, Yonne**: 0 ha until 2018 and 2.629 ha in 2019.

**Consequence:** for lentil and chickpea, a "departmental" model actually learns from repeated regional series. An MAE computed over departments would inflate the effective n. Evaluate by region-year or deduplicate, and report the effective n.

### 1.5 Which crop survives a temporal holdout (train ≤2018, test 2019-2024)?
- **Field pea: yes.** It's ~38 departments × 6 test years = ~228 department-years, but only **6 independent climate years** (departments within the same year are correlated). The train set includes 2016, the disaster (23,4 q/ha nationally, Yonne 11, Aube 13,2), and the test set includes 2020 (27,6) and 2024 (28,3), two bad years. It's a good test.
- **Faba bean: yes, with caution** (a third of the area is statut 2; Gers is statut 2 and is the department with the most area).
- **Lentil: marginal.** There are 4 to 9 departments with relevant area, and half of the values are imputed. Good for a demo, not for validation.
- **Chickpea and dry bean: no.** Enough to show, not to evaluate.
- Honest alternative for lentil: use the **regional file** (same ZIP) and evaluate by region, which is in any case the real unit of the data. I did not count the regional file in detail [NV regarding counts].

---

## 2. Which pulse goes to human food in France?

| Crop | Main use | Source |
|---|---|---|
| Lentil | Human consumption (AOP (protected designation of origin) lentille verte du Puy, Label Rouge (French quality label) lentille verte du Berry). Imports cover ~50% of French consumption even though the area doubled in 10 years. Growing it under contract is recommended. | Terres Inovia sheet [S]: https://www.terresinovia.fr/fr/pdf-download/7477349/fffff887fc7dc2c91514233173ef1fc8757db02e2f4bcded6f56299c480a93cb |
| Chickpea | Human consumption (flours, prepared dishes) and some animal feed; Terres Inovia works on varieties adapted to France. | same sheet [S] |
| Dry bean | Human consumption (tarbais, lingot de Castelnaudary; the SAA defines it this way). Euralis + Bonduelle: 1.000 ha in 2023 with 115 growers (30 chickpea, 40 lentil, 45 dry bean). | SAA methodology [V]; Euralis: https://www.euralis.fr/wp-content/uploads/2023/06/1er-anniversaire-partenariat-Bonduelle-legumes-secs-juin-2023.pdf [S] |
| Faba bean | **Mostly animal feed**; the national human-food and ingredients market is around 10.000 t/year; the first export destination is Norwegian fish farming (aquaculture). The Egyptian human-food market collapsed due to quality (bruche: Egypt requires ≤1% bruchid-damaged grains). | Terres Inovia 2024 faba bean guide [S]: https://germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/FEVEROLE-2024-Guide-culture-TERRES-INOVIA.pdf ; Réussir: https://www.reussir.fr/ladepeche/la-feverole-francaise-en-difficulte-sur-legypte [S] |
| Field pea | **More human than the brief assumed.** Terres Univia balance sheet (Nov. 2025) for 2025/26, per the Terres Inovia 2025 pea quality sheet: production 349 kt, of which 77 kt go to animal feed, **140 kt to human food and ingredients** and 132 kt to export. | [NV]: I saw it cited by the search engine; the PDF https://www.terresinovia.fr/sites/default/files/2026-01/fiche_terres_inovia_qual_graines_pois2025.pdf returned 403. The 349 kt matches what the SAA 2025 gives (348,1 kt) [V]. |
| Pea (ingredients) | Roquette, in Vic-sur-Aisne (Aisne), extracts pea protein; with its Canada plant (125 kt) it declares capacity for 250.000 t/year in total, so the French share would be ~125 kt (my own calculation). | Roquette press release 2021 [S]: https://fr.roquette.com/-/media/media-centre/press-releases/2021/20211117-pr/20211117-communique---roquette-ouvre-la-plus-grande-usine-de-proteines-de-pois-au-monde.pdf |
| Market | The OléoProtéines 2025 observatory covers 7 pulses; lentil leads dry pulses in supermarkets (+8% in 2024, ~23.000 t of dry pulses in GMS (grandes et moyennes surfaces, French large retail stores)); canned goods are growing (122.000 t). | Terre-net [S]: https://www.terre-net.fr/debouches/article/889517/les-legumineuses-confirment-leur-ancrage-dans-les-assiettes-francaises |

**Reading for the pitch:** pea has the best data, and a growing share goes to human food (pea protein, casserie). That takes the wind out of the objection that "pea is feed", but the figure should only be cited after it is confirmed. Lentil is the cleanest human-food story, but its data is the weakest.

---

## 3. Climate

### 3.1 Open-Meteo (test done) [V]
Query: `archive-api.open-meteo.com/v1/archive?latitude=45.04&longitude=3.88&start_date=2016-06-01&end_date=2016-06-30&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration&models=era5_land` (Le Puy, June 2016). Response saved in `scratchpad/ts_data/meteo/`.
- HTTP 200, no key. ERA5-Land cell 45,0 N / 3,9 E, 644 m.
- **With `era5_land`, `precipitation_sum` and `et0` all come back `null`.** Hourly precipitation with `era5_land` also comes back null, while soil moisture (`soil_moisture_0_to_7cm`, `7_to_28cm`) does come back.
- With `models=era5`, `era5_seamless` or the default, June 2016 rain comes to 75,2 mm. With `era5`, the cell is 45,0/4,0 (0,25° grid).
- Coverage: `era5_land` returns data from 1950-01-01. Checked on 29/10/2026, the last day with data was 2026-10-22, i.e. ~7 days of lag (the documentation says 5).
- The documentation confirms: ERA5 from 1940 at 0,25°, ERA5-Land from 1950 at 0,1°, and precipitation "no disponible" [not available] in ERA5-Land because it is forced by ERA5. It accepts several coordinates per request. https://open-meteo.com/en/docs/historical-weather-api [S]
- **Free tier limits** (non-commercial): 600/min, 5.000/h, 10.000/day and 300.000/month. A request covering more than 2 weeks or more than 10 variables counts as several calls (in their example, 4 weeks = 3,0). https://open-meteo.com/en/pricing [S]. Extrapolating their rule (my own calculation, [NV]): 16 years of daily data per point ≈ 400 calls, and 50 points ≈ 20.000, which **exceeds the daily limit**. In addition, commercial use requires a paid plan, and that affects the business model.

### 3.2 Recommendation: SAFRAN / SIM2 from Météo-France [V]
- Dataset: https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne (Licence Ouverte v2, last modified 29/10/2026).
- One CSV.gz per year since 1958 (2016 weighs 137 MB) plus `QUOT_SIM2_latest.csv.gz` (20 MB, updated today), with the SAFRAN 8 km grid in Lambert II étendu (extended Lambert II, the French projection) (`coordonnees_grille_safran_lambert-2-etendu.csv`).
- Confirmed columns: `LAMBX;LAMBY;DATE;PRENEI;PRELIQ;T;FF;Q;DLI;SSI;HU;EVAP;ETP;PE;SWI;SSWI_10J;DRAINC;RUNC;...;WG_RACINE;TINF_H;TSUP_H` (liquid rain and snow, mean T, hourly Tmin/Tmax, ETP, **soil wetness index SWI** and water in the root zone).
- Advantages: it is the French agroclimatic reference, has no call limit, allows commercial use, and has water variables that matter for pulses (water stress and heat at flowering). Cost: ~2,2 GB compressed for 2010-2025. It is processed year by year and aggregated to department right away.

### 3.3 RPG for weighting climate [S]
- The IGN feed says that "à partir de la version 2015 du RPG, les données diffusées comportent les îlots et les parcelles agricoles: l'information sur [...] le type de culture redescend au niveau de la parcelle" [“from the 2015 version of the RPG, the data published include the blocks (îlots) and agricultural parcels: the information on [...] the crop type goes back down to the parcel level”] (https://data.geopf.fr/telechargement/resource/RPG). In the feed listing I only found the v1 packages (2007-2014, by region); I could not list the v2 packages by year [NV].
- The per-parcel crop codes for lentil, chickpea, faba bean and pea (of the LEN, PCH... style) **I have not verified them** [NV].
- Proposed use: with one year of RPG (e.g. 2023), take the centroid of each pulse's parcels per department and weight the SAFRAN cells. It's a bonus, not a requirement. Zero-effort alternative: department centroid or average of the agricultural SAFRAN cells.

---

## 4. Prior art: what already exists

| Actor | What it does | Relevance | Source |
|---|---|---|---|
| JRC MARS / MCYFS | Monthly bulletin with yield forecasts for the EU and by member state. Includes **field peas** (EU: 2,23 t/ha in September 2026, -2% vs. the 5-year average). | There is already a pea forecast at EU level (and probably by country). It is not departmental, does not cover lentil, chickpea or dry bean, and it is not a tool for a cooperative. | https://capital.com/en-eu/news/rain-came-too-late-to-rescue-eu-summer-crop-yields [S]; https://joint-research-centre.ec.europa.eu/scientific-activities/crop-monitoring-and-yield-forecasting_en [S]. Country tables with peas: [NV] |
| Agreste conjoncture / DRAAF | Monthly estimates of areas and yields for the current season. Some DRAAFs publish "état des cultures et prévisions de collecte" [crop status and collection forecasts] (Pays de la Loire, April and July 2026). | There is already an official estimate during the season, regional, with no public ML methodology. | https://draaf.pays-de-la-loire.agriculture.gouv.fr/IMG/pdf/2026_07_plaquette_etat_des_cultures_previsisons_de_collecte_recolte_2026.pdf [S]; https://draaf.centre-val-de-loire.agriculture.gouv.fr/IMG/pdf/no8_bimestrielle_juin_2026.pdf [S] |
| Terres Inovia / Terres Univia | Balance sheets, harvest reports (e.g. lentil 2021: 8 q/ha in Aube, Marne and Yonne vs. 27,3 for the 3-year average; 6 q/ha in Centre vs. 15). Agronomic tools. | I did not find a published departmental yield forecast for pulses [NV: have to ask a mentor]. | https://www.terresinovia.fr/-/2021-lentil-and-chickpea-crop-report [S]; https://www.pleinchamp.com/actualite/un-plat-de-lentilles-en-guise-de-recolte-2021 [S] |
| Academia | Ben-Ari et al. 2018 (Nat. Commun.): the 2016 French wheat disaster was not anticipated by operational forecasts and is explained by a warm autumn followed by a wet spring. Paudel et al. 2021/2022: regional ML in Europe, which beats the operational system 60 days before harvest in 18 of 35 cases. Cernay et al. 2015: pulses in Europe are more volatile than non-pulses. CY-Bench: subnational benchmark (maize and wheat, [NV]). Challenge Crop Data 2018 (Reims). | For pea or lentil at French departmental scale I found nothing published [NV, limited search]. | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5915531/ ; https://research.wur.nl/en/publications/machine-learning-for-regional-crop-yield-forecasting-in-europe/ ; https://ideas.repec.org/a/eee/agisys/v187y2021ics0308521x20308775.html ; https://www.nature.com/articles/srep11171 ; https://agris.fao.org/search/ar/records/691dcd9ab5c644bfae85675d ; https://www.univ-reims.fr/media-files/16262/cropdata.pdf [S] |
| Private | Satellite forecasting platforms (EarthDaily, etc.). | I did not review them [NV]. | n/a |

**Defensible gap:** (1) departmental or collection-basin scale; (2) dry pulses for human consumption, which MARS does not cover; (3) explainable through analogs ("this season looks like 2016 and 2021"); (4) open and traceable (SAA + SAFRAN, both under Licence Ouverte); (5) with explicit uncertainty. **Do not claim:** "nobody forecasts pulse yields".

### 4.1 User and decision
- **User**: the person in charge of collection or marketing at a cooperative or an organisme stockeur (grain collector) with contracts for pulses for human consumption (Qualisol in the Gers with organic lentil and chickpea for Ethiquable: https://www.reussir.fr/lesmarches/ethiquable-choisit-qualisol-pour-ses-legumineuses [S]; Euralis with Bonduelle [S]; Sabarot in Haute-Loire [NV]).
- **Decisions**, in order of plausibility:
  1. **Collection forecast**: how many tonnes come in, for logistics, storage and cleaning (the bruchid forces treatment or sorting).
  2. **Sales commitments**: how much to sell in advance to the canner or processor (Bonduelle, Roquette) before harvest.
  3. **Contracting for the next season**: how many hectares to contract, which is where the "farmer income" story comes in.
  4. **Insurance**: not very plausible for the MVP; parametric insurance uses its own indices.
- **Timing**: spring pea and lentil are harvested in July and August, so a cutoff on 15 June gives 3 to 6 weeks of lead time. It needs confirming with a mentor: does the cooperative already have this information from its field technicians? If it does, the value lies in the **regional scale and consistency**, not in "knowing earlier".

---

## 5. Evaluation of the ideas

### Idea 4: early departmental yield estimate

| Criterion | Evaluation |
|---|---|
| **Viability in 20 h** | **6/10 with pea** (healthy data, ~38 departments, test 2019-24); 4/10 with faba bean as second crop; **3/10 if the main label is lentil** (4 to 9 departments, half imputed). The technical risk is in the climate ETL (extract, transform, load) (SAFRAN at 2 GB, or the Open-Meteo limits), not in the model. |
| **Essential AI** | Moderate. Ridge or GBM on climate anomalies is classic, legitimate ML and "appropriate" if well validated and it beats the baseline. The jury may see it as "a regression". To reinforce it: a pooled model across departments with fixed effects, intervals via quantile regression or conformal prediction, and feature importance (heat at flowering, rain at harvest). An LLM adds nothing to the core. |
| **Innovation** | Low-medium: MARS and Agreste already estimate. What is new is the departmental scale, pulses for human consumption, open code and honest uncertainty. |
| **Link to human consumption** | Indirect if trained on pea (you have to argue with the ingredients and casserie share, figure still [NV]). Direct if proven on lentil, but with a quality warning. |
| **Impact story** | "In 2021 lentil yielded 8 q/ha in Champagne against 27 expected. A cooperative that had seen this in mid-June could have adjusted its commitments with the canner and avoided penalties." It has to be quantified carefully (without verified prices, no euro figures are invented). |
| **Business model** | SaaS for cooperatives and grain collectors (OS), by collection basin, or a service for an interprofessional body (Terres Univia) financed as a public good for the filière (supply chain). With commercial Open-Meteo there is a cost; with SAFRAN, there is none. A plausible revenue per client is low; the value is in reducing contract risk. It is a hypothesis. |
| **Risks** | (1) That it does not beat the "department mean" or "trend" baseline; with 9 train years this is very possible. (2) Low effective n: 6 test years. (3) Information leakage: revised and back-extrapolated SAA, normalization using future years. (4) Regional imputations. (5) That departmental yield is not the cooperative's decision variable. (6) Climate scale. |
| **MVP** | Pea, 10 to 15 departments with statut 1 and ≥1000 ha; cutoff 15 June; SAFRAN variables per department (sum of rain, days >30 °C, ETP-P and SWI in April-June, in monthly windows); baseline 1 = department mean in train, baseline 2 = linear trend; model = pooled Ridge on anomalies; metric = MAE per year in 2019-2024, with the effective n made explicit. |
| **Demo** | Department and test-season selector → yield series 2010-2024, point estimate with interval, baseline and "revealed" actual value. Error panel by year (so that 2020 and 2024 stand out). A "lentil (experimental)" tab with the imputation warning. |
| **Stopping rule** | Saturday at 14:00: if Ridge does not improve MAE versus the best baseline by ≥10% **in at least 4 of the 6 test years**, stop iterating the model and move the narrative to idea 2 (analogs with honest evaluation). If the climate ETL is not ready by Saturday at 11:00, switch to Open-Meteo `era5_seamless` with one point per department and fewer variables. |

### Idea 2: climate analog seasons (kNN)

| Criterion | Evaluation |
|---|---|
| **Viability in 20 h** | **7/10.** Technically simple (aggregate the climate and compute distances). But **there are only yields from 2010 to 2025**: for a test year there are ≤15 candidates, and in the temporal backtest even fewer (for 2019, only 2010-2018). The climate data goes back to 1958 (SAFRAN), so climate analogs from 1958-2009 can be shown, but **without departmental SAA yield** in this file. There are older series at Agreste, which I did not check [NV]. |
| **Essential AI** | Low if it is plain Euclidean kNN and nothing else. It rises if: (a) the metric is learned, weighting variables by their relation to yield in the train set, which is simple metric learning; (b) embeddings of the daily curves are used; (c) uncertainty is calibrated with the spread of the neighbors. It should be framed as "explainable AI based on cases" (case-based reasoning), which is a strong argument before a non-technical jury. |
| **Innovation** | Medium. Analogs are classic in meteorology, but I do not know of a season-analog tool for French pulses aimed at cooperatives [NV]. |
| **Link to human consumption** | Same as in A. It works better with lentil, because the analog can be explained qualitatively even though the yields are regional. |
| **Impact story** | "This spring looks like 2016 and 2021, two seasons in which lentil and pea collapsed. Prepare your backup supply plan." It is intuitive for a buyer. |
| **Business model** | The same as idea 4; it could be the free or lead-generation version, with idea 4 being the paid one. |
| **Risks** | Few candidates; "similar climate" does not imply "similar yield" (varieties, bruchid, prices that change the area); curse of dimensionality if daily curves are used; temptation to select analogs using future information. |
| **MVP** | Same variables as idea 4 (monthly vector from April to June, z-score against prior years). k=3. Show the 3 most similar years, their overlaid curves and their yields. Evaluation: mean yield of the k neighbors vs. historical mean, in 2019-2024, with candidates only from earlier years. |
| **Demo** | Pick a department and a year → cumulative rain and temperature curve up to 15 June against those of the 3 analogs → their yields → at the end, "reveal" the actual one. For 2026 live: analogs of the current season, since SIM2 runs up to today. |
| **Stopping rule** | If the analogs' mean does not beat the historical mean in the backtest, it is presented only as an exploration tool (without claiming predictive ability) and the ambition is cut back. If idea 4's MVP already has a working model, idea 2 is added as an explanation layer in ≤3 h; if it is not done in 3 h, it is dropped. |

### 5.1 Recommended combination
1. **One single pipeline**: SAA (pea + faba bean + lentil) → SAFRAN aggregated to department → matrix of variables at the cutoff. Ideas 4 and 2 share 80% of the work.
2. **Product**: "Météo de campagne légumineuses" [pulse season weather]. For a department and a date: (a) estimate with interval (idea 4); (b) "similar seasons" with their yields (idea 2) as explanation; (c) **risk drivers** with flags (heat at flowering, rain at harvest, water deficit).
3. **Bridge to the bruche idea**: the same daily variables (maximum temperatures at flowering, degree-days) feed a bruchid risk indicator. That the flight of *Bruchus* depends on temperature thresholds (~20 °C) is from my own memory [NV]; it must be checked with Terres Inovia. This connects quality (≤1% bruchid-damaged grains for human consumption and for Egypt [S]) with climate. It is the strongest "human consumption" argument that the time-series ideas have.
4. **Crops**: train and evaluate on **pea** (and faba bean); show **lentil** in experimental mode, with the imputation table as proof of rigor (it adds points for "scientific rigor").

---

## 6. Checklist for Friday (at the start of the event)
- [ ] Download the SAA ZIP again (there may be a new version) and pin the version in the README.
- [ ] Decide the climate source: **SIM2** (download 2010-2026 in parallel, ~2,2 GB) or Open-Meteo `era5_seamless` (not `era5_land` if you want rain).
- [ ] Exclude Oise (pea 2010-2019) and flag the duplicated department pairs.
- [ ] Questions for the mentor: does the cooperative need the data at department or basin level? On what date does it decide? Does it already have estimates from its technicians? What share of pea actually goes to human consumption (confirm 140 kt of 349)?
- [ ] Confirm whether MARS publishes field peas by country (if it does, use it as the national benchmark).

## 7. Generated files (scratch, not part of the solution)
- Data: `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/ts_data/` (`saa/`, `meth/`, `meteo/`, `sim/`, `count_pulses_out.txt`, `top_deps_out.txt`, `dups_out.txt`, `statut_out.txt`)
- Inspection scripts (counts only): `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/ts_scripts/`

## 8. Not verified / could not be done
- Pea 2025/26 balance (140 kt for human consumption): the Terres Inovia PDF returned 403 and the FranceAgriMer sheet blocked automatic download.
- Whether MARS publishes field peas by country (I only saw the EU figure via Reuters and Capital.com).
- RPG v2 crop codes and the package list by year.
- Departmental SAA series before 2010.
- The bruchid temperature thresholds.
- Whether Terres Inovia or Arvalis have an unpublished departmental pulse forecast.
