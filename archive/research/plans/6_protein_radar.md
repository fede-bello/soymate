# Dossier Idea 6: "French protein radar" (combination of ideas 1, 2 and 4)

Dossier prepared on 30/10/2026, before the start of the event. Desk research and data exploration only (counts, joins, formats, descriptives on published figures). **No model was fitted, there was no cross-validation and no backtest.** The variance decomposition in section 3 is a descriptive on 11 published national figures, not a solution result.

Marks: **[V]** verified by me today on the file, the API or the primary source; **[F]** read in a secondary source, in a search engine snippet, or in the prior research in the repo without reopening it today; **[NV]** not verified, my own calculation or hypothesis.

Exploration scripts: `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/plan6/scripts/` (s1 to s7). The data was downloaded to `.../plan6/data/` and **deleted at the end** (see the end of the file).

---

## 1. Summary in 5 lines + verdict

1. **What it is:** an in-season estimate (from sowing to harvest) of how many tonnes of **pea protein fit for food use** France and each of the 5 Terres Inovia "bassins" (basins) will produce: area (Agreste notes since April) × yield (the idea 4 model) × grain protein (the idea 1 model) × fraction fit for human food (assumption with prior), with Monte Carlo and "twin seasons" (idea 2) to sample yield and protein together.
2. **Real gap, verified:** Agreste already publishes departmental area from **13/04** and departmental production from **13/07** [V]; Terres Univia publishes the balance in November and protein by bassin only in **December to March** [V, dates from the PDFs]. Nobody publishes "tonnes of food-grade protein" before harvest [NV, negative search].
3. **But the gap matters little at national scale:** in 2015-2025 the year-to-year variation in contained protein is explained ~68% by area, ~30% by yield and **~2% by protein content** (sum of log variances, descriptive) [V calculation on SAA + Terres Univia]. And the fit-for-use supply (60-80% of 348 kt = 209-278 kt in 2025) exceeds human food + ingredients use (140 kt, flat in 2023/24, 2024/25 and 2025/26) [V]. At country level there is no shortfall to forecast.
4. **The most uncertain layer (fit fraction) has no series:** only two years with an explicit number (~80% in 2024, ~60% in 2025) [V]; the rest is qualitative. It has to be modelled as an assumption, and the jury will see it.
5. **User and money:** the natural user of a **national** radar is the State or Terres Univia (little willingness to pay). The one who pays (the processor) wants **its basin and its contracts**, which is idea 1.

**Verdict: NO-GO as a separate idea. Estimated score 5.55/10 (section 12), below idea 1 (6.4), idea 2 (6.1) and idea 4 (5.9).** Combining does not raise impact or economics: it adds two links (area, fit fraction) that either Agreste already publishes or that have no data, and it dilutes execution. **What is worth salvaging for idea 1** (about 2-3 h of work): a "tonnes of protein in the basin" screen that takes the area from the latest Agreste note, multiplies it by the predicted yield and protein, and uses the 5 Terres Inovia bassins (35 bassin means × year 2019-2025 in the PDFs [V]) as an external check.

---

## 2. Problem, concrete user, decision

### 2.1 Candidate users and the decision they would take
| User | Decision | When | With what information today | Cost of getting it wrong | Needs a national radar? |
|---|---|---|---|---|---|
| Supply manager at a processor (Roquette Vic-sur-Aisne, Cosucra in Belgium) | How much to contract, where, whether to buy abroad | Contracts before sowing [F, Terres Univia 2022 via idea 1]; adjustment April-June | Previous year's areas, Agreste notes from April, NIRS on reception (July) | Underused plant or replacement purchases; Chinese protein now sells at 40.5-67.1% [V] | **No**: it needs its basin (radius 250-300 km [F]) and its portfolio. That is idea 1 |
| Cooperative / négoce selling to processors (Natup, Cérésia, Noriap, Axéréal) | Collection forecast, segregation of human/animal lots | May-June | Technicians, history, Agreste from mid-July | Lots wrongly assigned, broken commitments | Partly: its area. That is idea 4 |
| Terres Univia / FOP (interprofessional body) | Use balance, communication to the sector, programmes (Pea4Ever) | Balance in November [V] | Agreste + quality survey + customs | Low: it is public information, not operational | Yes, but it already produces it, after harvest |
| State (DGPE, monitoring of the protein strategy, target of 8% of UAA in pulses by 2030 [F]) | Policy monitoring | Annual | SAA, Agreste, FranceAgriMer | Low in the short term | Yes, but annual, not in-season |

### 2.2 The decision that would justify the product
"Before harvest, will French food-grade pea be enough to cover the demand for ingredients, and in which bassins is it short?" The problem: with the public numbers, the national answer is "there is a surplus" every recent year.

| Season | Pure production (kt) | % of lots fit for human food (Terres Inovia) | Estimated fit grain (kt) | "Human food and ingredients" use (kt) |
|---|---|---|---|---|
| 2024 | 346 (balance) / 348.4 (SAA) [V] | "Près de 80 %" (nearly 80%) [V] | ~277 [NV calculation] | 140 [V] |
| 2025 | 349 (balance) / 348.1 (SAA) [V] | "Environ 60 %" (about 60%) [V] | ~209 [NV] | 140 (forecast) [V] |
| 2026 | 291.9 (Agreste at 1/9/2026) [V] | no data (survey comes out in December) | 175-234 if 60-80% [NV] | no data |

Reading: human food + ingredients use appears **fixed at 140 kt** in the 2023/24, 2024/25 and 2025/26 balances [V, Terres Inovia PDFs 2024 and 2025]. That suggests the ceiling is set by plant capacity, not by grain supply [NV interpretation]. Counter-evidence in favour of the problem: in 2021 "la demande a souvent été confrontée à un manque de lots de belle qualité pour le débouché consommation humaine" (demand was often faced with a lack of good-quality lots for the human food outlet) [V, 2021 pea quality PDF]. In other words, the problem exists in some years and is one of **quality and location**, not national volume.

### 2.3 Does the anti-dumping create a quantified need?
- Facts [V, Commission press release 25/09/2026]: definitive duties of 40.5% to 67.1%, for 5 years; EU market "some €175m". Provisional since 29/04/2026 [F, search engine on Regulation 2026/916]. EU industry share 59% → 56% in the investigation period [F, secondary summary]. Definitive measures in force from 26/09/2026 [F, prior research; EUR-Lex blocks curl].
- What I did **not** find: any figure for how much extra pea the European plants will ask for. €175M at ~€4.15/kg of isolate [F, Expana via idea 1] is ~42 kt of isolate across the whole EU market [NV calculation]; if the EU industry gains, for example, 10 share points, that is ~4 kt more isolate [NV scenario], which with an unknown extraction yield (assumption 4-6 t of grain per t of isolate [NV, not verified]) is 17-25 kt of grain: **less than 10% of French production**. The anti-dumping is a good timing hook, not a quantified need for a national radar.

---

## 3. Hypotheses

| # | Hypothesis | Type | Status | Evidence | If false |
|---|---|---|---|---|---|
| H1 | There is demand for national/regional forecasts of protein supply in-season | Market | **[NV], probably weak** | Nobody publishes it (negative search). Those who publish balances do so after harvest: Terres Univia in November [V, "Sources : Terres Univia (novembre 2025)"], FranceAgriMer in oil and protein-crop balances updated in October, March and June [F, search engine; the PDF returns HTML to curl] and in its annual filière sheet (February 2026) [V] | Most likely: the product shrinks to a screen inside idea 1 |
| H2 | The current year's area can be known before harvest | Data | **[V]** | Agreste notes with departmental xlsx: 1/4/2026 (PDF of 13/04), 1/5, 1/6 (15/06), 1/7 (13/07), 1/9 (14/09) [V]. National pure area 2026: 102.9 kha (1/4 and 1/5) → 94.9 (1/6) → 95.4 (1/7 and 1/9) [V] | n/a |
| H3 | Early area is accurate | Data | **[V] false in April** | 2025: note of 1/4 = 111.7 kha vs final 97.9 (+14%) [V]; departmental (36 depts ≥500 ha) MAPE 23.7% [V, script s3]. 2026: 1/4 102.9 vs 1/9 95.4 (+8%). Faba bean 2025: 87.8 (1/4) vs 112.3 (1/9), -22% [V] | April area is a first-order uncertainty; its revision has to be modelled, with only 2 years of history (n=2) |
| H4 | Area can be estimated with Sentinel-2 in 20 h | Technique | **[NV], discarded** | RPG only up to 2024 in the WFS (`RPG.2024` is the last layer) [V]; there are no labels for the current year; separating pea from other winter crops in April requires time series and validation | Use Agreste, which is free and official |
| H5 | Protein content weighs in the uncertainty of protein tonnes | Science | **[V] false at national scale** | 2015-2025, log variance: area 0.0485, yield 0.0215, protein 0.0016 (68 / 30 / 2% of the sum) [V, script s7]. National protein: SD 0.91 points, CV 4.0%; yield CV ~15% [V] | This is the strongest finding against the idea: the "protein" layer (the novelty of idea 1) barely moves the tonnes. But within the season, with area already known (June), the 4% CV competes with the residual yield error |
| H6 | Yield and protein correlate and must be sampled together | Science | [V] weak descriptive | National log correlation -0.16 (n=11) [V]; Terres Inovia 2025 describes "dilution de l'azote dans un nombre important de graines" (nitrogen dilution across a large number of seeds) [V] | If there is no correlation, independent Monte Carlo is enough |
| H7 | The fit-for-human fraction can be estimated | Data | **[V] almost impossible** | Only 2024 (~80%) and 2025 (~60%) give a number; 2019-2023 say "la plupart" (most), "une grande partie" (a large part) [V, PDFs]. The charts by criterion (broken, bruchées/bruchid-damaged, stained) are images: digitisable by hand, no guarantee [V that they are charts; NV that they can be read well]. In 2025, 55% of lots had <1% broken/split [V] | Treat it as an assumption with a Beta prior and say so. It is the weakest layer |
| H8 | Protein by bassin can be used for validation | Data | **[V]** | The 2019-2025 PDFs carry "nb" and "moy." for 5 bassins (Normandie/Nord, Est, Centre-IDF, Ouest/Poitou-Charentes, Grand Sud): 35 bassin × year means [V]. The order in the extracted text does not follow the bassins: transcribe by hand looking at the map (20 min) | Validate only against the 11 national points |
| H9 | Pea_dataset and SAA remain as in ideas 1 and 4 | Data | **[V] today** | 4,450 situations, 3,326 with protein, 4,230 with yield, 256 site-year-type trials with protein, 33 depts [V]; the depts with protein trials hold 80% of 2024 area [V] | n/a |
| H10 | There is enough time for 4 components | Execution | [NV] | Ideas 1 and 4 are each a full weekend according to their plans | Cut to Agreste area + climatological yield + protein (idea 1); no own yield model |
| H11 | Faba bean enters | Market | **[V] no** | Human use 10 kt of 215 kt (2024/25 balance) [V]; export to third countries mainly Norway (fish farming) [V] | Pea only |
| H12 | The project is eligible (not feed) | Rules | [F] | Human destination + ingredients; but the 60-80% "fit" includes lots that end up as feed | Frame everything on the human fraction, confirm with the organisers |
| H13 | Anti-dumping creates a quantified need | Market | [V] the duties; [NV] the need | See 2.3: the order of magnitude is <10% of production | Use it as a hook, not as an impact figure |

---

## 4. Datasets (verified audit)

### 4.1 Agreste, "Infos rapides grandes cultures" notes with departmental xlsx (current-year area and yield)
- **URL pattern [V]:** `https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/<ID>/<AAAA>_<NN>donnees_grandescultures_departements.xlsx`. IDs downloaded today (HTTP 200): 2026: `IraGcu2639` (1/4), `IraGcu2653` (1/5), `IraGcu2674` (1/6), `IraGcu2688` (1/7), `IraGcu26114` (1/9); 2025: `IraGcu2540` (1/4), `IraGcu2591` (1/7), `IraGcu2599` (1/8), `IraGcu25115` (1/9). `IraGcu2698/2026_98` returned 404 (the name does not follow the pattern). PDF: `.../<ID>/<AAAA>_<NN>inforapgdescultures.pdf` (creation dates: 13/04, 15/06, 13/07, 14/09/2026) [V].
- **Licence:** Licence Ouverte (Agreste) [F].
- **Size:** 1.26 to 1.71 MB per xlsx [V].
- **Structure [V]:** sheet `grandes_cultures` (note 26114 also has a query sheet `diffusion_dep - Rappo - Requête`). Rows 0-3: title, methodological notes, source; the row with "Culture" = header; data starts 2 rows below. Columns: 0 region (old), 1 department ("017 - Charente-Maritime"), 2 crop, then 5 previous years of SAA × (Area 1000 ha, Yield q/ha, Production 1000 t) and the current year in columns 18, 19, 20.
- **Crop labels [V]:** `Pois protéagineux purs` (pure protein peas), `Pois protéagineux total`, `Mélanges à base de pois protéagineux` (2026) or `Mélange de pois` (April-July 2025), `Féveroles` (faba beans), `Lentilles` (lentils), `Pois chiches` (chickpeas).
- **Counts [V, script s4]:** pure pea 2026: 82-83 depts with area; 36-38 depts with ≥500 ha. Yield for the year: **empty in the April, May and June notes**, present from the 1/7 note (83 depts).
- **National pure pea series [V]:** 2025: 111.7 kha (1/4) → 97.9 kha, 33.2 q/ha, 324.9 kt (1/7) → 34.5 q/ha, 337.2 kt (1/8) → 34.4, 336.8 (1/9) → SAA 35.6, 348.1. 2026: 102.9 (1/4) → 102.9 (1/5) → 94.9 (1/6) → 95.4 kha, 29.9 q/ha, 285.1 kt (1/7) → 95.4, 30.6, 291.9 kt (1/9).
- **Gotchas [V]:** the sum of departments (97.3 kha in April 2026, 88.7 in September) is lower than the national total (102.9 and 95.4): there is area not assigned to a department (secrecy or rounding). Use the national total as the anchor and distribute. Headers change format between notes (years as int or as text with a line break). Yield is "à dire d'experts" (expert opinion) until September [F, idea 4, note text]. 51% of integer values in 2023 and 2025 [F, idea 4].
- **Download on Friday:**
```bash
B=https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie
mkdir -p data/raw/agreste && cd data/raw/agreste
for s in IraGcu2639:2026_39 IraGcu2653:2026_53 IraGcu2674:2026_74 IraGcu2688:2026_88 IraGcu26114:2026_114 \
         IraGcu2540:2025_40 IraGcu2591:2025_91 IraGcu2599:2025_99 IraGcu25115:2025_115; do
  id=${s%%:*}; f=${s#*:}; curl -sL -o ira_$f.xlsx "$B/$id/${f}donnees_grandescultures_departements.xlsx"; done
file ira_*.xlsx   # all of them have to say "Microsoft Excel 2007+"
```

### 4.2 Agreste SAA long series 2010-2025 (departmental history)
- **URL [V]:** `https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAA-SeriesLongues/SAA-SeriesLongues-2010-2025_DonneesProvisoires-DepartementalesRegionales.zip` (7.1 MB; inside, the departmental xlsx 11 MB and the regional one 3.6 MB, dated 10/07/2026).
- **Structure [V]:** sheet `COP`, `header=5`, `LIB_REG2, LIB_DEP, LIB_SAA, STATUT_QUALITE, SURF_2010..2025, REND_..., PROD_...` (ha, q/ha, quintals). Product `41 - Pois protéagineux`.
- **National series recomputed today [V, script s6]:** area (kha) 2015-2025: 155.5 / 188.0 / 186.2 / 145.4 / 153.8 / 202.7 / 194.3 / 133.5 / 151.6 / 123.1 / 97.9; yield (q/ha): 35.8 / 23.4 / 33.8 / 34.0 / 38.7 / 27.6 / 28.4 / 30.0 / 32.0 / 28.3 / 35.6.
- **Area by region 2025 [V]:** Grand Est 17.6 kha, Nouvelle-Aquitaine 16.4, Centre-Val de Loire 16.2, Hauts-de-France 12.6, Normandie 9.4, Bourgogne-Franche-Comté 6.6, Île-de-France 6.3, Occitanie 4.5.
- **Gotchas:** Oise 2010-2019 with yields of 9-16 q/ha (artefact) [F, ideas 1 and 4]; the series are revised, not what was known in real time.

### 4.3 Pea_dataset (INRAE / Terres Inovia), protein and yield from trials
- **URL:** https://doi.org/10.57745/FW78RE; files via `https://entrepot.recherche.data.gouv.fr/api/access/datafile/<id>?format=original` (764684 trials 1.4 MB; 764685 traits 4.8 MB; 764683 metadata 4.9 kB; 764686 climate zip) [V today]. Licence Etalab 2.0 [F, idea 1].
- **Counts [V today, script s6]:** 4,450 situations × 33 columns; 27,168 long-format rows; protein 3,326; yield 4,230; **256 site-year-type trials with protein**; years with protein 2003-2004 and 2013-2024; 33 depts with protein trials; those depts hold **80% of 2024 pea area**.
- **Protein trials by region [V]:** Hauts-de-France 46, Centre-Val de Loire 41, Île-de-France 35, Grand Est 32, Nouvelle-Aquitaine 30, Occitanie 30, Pays de la Loire 17, Bourgogne-Franche-Comté 9.
- Units, gotchas (wrong coordinates for AVANCON, DIOU, GRIGNON, GRIGNON_INRAE), leakage: see idea 1, section 4.1 [F, not re-verified today].

### 4.4 Pea quality survey (Terres Inovia for Terres Univia)
- **URLs that download with curl [V]:** `https://www.terresunivia.fr/fichiers/publications/qualite-graines-pois-2025.pdf` and `.../qg-pois-<AAAA>.pdf` for 2019-2024; `.../qualite-graines-feverole-2024.pdf`. The 2026 ones do not exist yet (404) [V]. Copy on terresinovia.fr: `.../2026-01/fiche_terres_inovia_qual_graines_pois2025.pdf` [F, search engine].
- **Publication dates (CreationDate of the PDF) [V]:** 2019: 12/12/2019; 2020: 26/01/2021; 2021: 04/01/2022; 2022: 08/03/2023; 2023: 18/12/2023; 2024: 27/02/2025; 2025: 09/12/2025. **Between 5 and 8 months after harvest.**
- **Content [V]:** national protein % DM (N×6.25, NIRS, Ardon laboratory) 2015-2025: 22.9 / 23.1 / 22.4 / 21.7 / 22.2 / 21.6 / 22.7 / 21.9 / 24.4 / 24.1 / 22.8; moisture at harvest; 75-102 samples per year; means by 5 bassins with "nb" and "moy." (2019-2025, 35 values); use balance (production, animal feed, "alimentation humaine et ingrédients", exports, Belgium). Visual quality classes (impurities, split/broken, stained, insect-damaged) only as **charts**.
- **Fit-for-human fraction [V]:** 2024 "Près de 80 % des lots ... utilisables en alimentation humaine" (nearly 80% of lots usable for human food); 2025 "Environ 60 % des lots pourraient satisfaire les critères exigés en alimentation humaine" (about 60% of lots could meet the criteria required for human food); other years only qualitative.
- **Gotcha:** in 2025 only 9.5% of lots with a declared destination went to human food; in 2023 "environ 1/4" (about a quarter) [V]. The "fit" fraction is not the "used" fraction.
- **Download on Friday:**
```bash
U=https://www.terresunivia.fr/fichiers/publications
mkdir -p data/raw/qualite && cd data/raw/qualite
curl -sL -O $U/qualite-graines-pois-2025.pdf
for y in 2019 2020 2021 2022 2023 2024; do curl -sL -O $U/qg-pois-$y.pdf; done
for f in *.pdf; do pdftotext -layout $f; done
```

### 4.5 SAFRAN / SIM2 (climate)
No changes from idea 1, section 4.2 and `archive/research/datasets/safran.md` [F, not re-verified today]: `https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/QUOT_SIM2_<AAAA>.csv.gz`, ~137 MB per year, Licence Ouverte, `num_dep` per cell in `SHP_SIM_FRANCE.dbf`.

### 4.6 Aggregated RPG (prior resource to declare)
- `archive/research/datasets/rpg_pulses_dept_year.csv` [V]: columns `year, code_dep, nom_dep, grp, n_parcelles, surface_ha`; 2015-2024; `pois_prot` 2023 149,984 ha, 2024 123,773 ha [V]. **Does not separate winter and spring** (PPR+PHI together) [V]. IGN WFS: last layer `RPG.2024` [V].

### 4.7 Market and context
- EU Commission, 25/09/2026: https://policy.trade.ec.europa.eu/news/commission-acts-against-imports-pea-protein-china-2026-09-25_en [V].
- FranceAgriMer, protein-crop filière sheet 2026 (February 2026): 146 kt of protein crops for human consumption in 2024/25 vs 155 kt 5-year average; 62 kt for industrial animal feed; ~12,400 producers; 502 kt collected (64%) [V, PDF].

### 4.8 Tested joins
| Join | Key | Result |
|---|---|---|
| Agreste note ↔ SAA | 3-character department code ("017") | direct; the 2026 notes carry SAA 2025 in the previous-year column [V] |
| April note ↔ final SAA | department | 36 depts ≥500 ha comparable in 2025 [V] |
| Pea_dataset ↔ dept | `postal_code[:2]` | 33 depts with protein [V]; 4-5 sites to correct [F, idea 1] |
| Dept ↔ Terres Inovia bassin | hand-made table (5 bassins, defined by the map in the PDFs) | **not tested**: the exact bassin boundaries are not in the text [NV] |
| Dept ↔ SAA region | `LIB_REG2` | direct [V] |

---

## 5. AI method (if it were done anyway, or as a module of idea 1)

### 5.1 Target and formula
Tonnes of protein fit for use in bassin b, season t:

`PROT_b,t = Σ_d∈b  A_d,t × Y_d,t × 0.86 × Pr_b,t × FG_t`

- `A`: pure area (ha). `Y`: yield (t/ha at standard moisture). `0.86`: dry matter at 14% moisture [NV standard assumption; measured moisture at harvest is 12.2-14.3% depending on the year, V]. `Pr`: protein % DM. `FG`: fraction fit for human food.
- Outputs: distribution of `PROT` by bassin and national, P(PROT < threshold), and the "fit grain" version (`A × Y × FG`).

### 5.2 Decision dates
| Date | Area | Yield | Protein | Fit fraction |
|---|---|---|---|---|
| D0 (sowing, Oct-Mar) | previous year's SAA × trend; empirical dispersion | departmental climatology (idea 4, B0) | bassin climatology (idea 1, B0) | prior |
| D1 (15/04) | Agreste note of 1/4 with revision error (n=2 years) | same + observed climate (idea 4) | same + observed climate (idea 1) | prior |
| D2 (15/06) | note of 1/6 (small error in 2026: 94.9 vs 95.4) | idea 4 model at 15/6 | idea 1 model at 15/6 | prior; adjustable with moisture and heat at harvest [NV] |
| D3 (13/07) | note of 1/7 | **Agreste 1/7** (official competitor, enters as data) | idea 1 model | prior |

### 5.3 Leakage to avoid
All those of ideas 1 and 4, plus: (a) using the final SAA area as if it were the April one (use the note available at the time); (b) calibrating `FG` with the year being shown (there are only 2 years); (c) normalising protein by bassin with the test year; (d) sampling analogues that include the test year.

### 5.4 Baselines
- **B0:** area from the note at the time × 5-year average yield of the dept × 10-year average protein (22.7%) × FG 0.7. This is what anyone would calculate in Excel with public data.
- **B1:** after 13/07, Agreste production × 0.86 × 22.7% × 0.7.
- The honest question: does the model beat B0 at D2? With 11 national years and 35 bassin-year protein values, the evidence will be weak no matter what.

### 5.5 Models (justified by n)
- Yield: the one from idea 4 (ridge or small LightGBM on ~38 depts × 16 years), or straight climatology if there is no time.
- Protein: the one from idea 1 (two levels, 256 trials), aggregated to bassin with area weights.
- Area: **no model**: lognormal distribution of the note → final revision, with a monthly SD estimated from 2025 and 2026 (n=2; say so). April: ~10-15%; June onward: ~1-2% [V the two cases, NV the generalisation].
- Fit fraction: Beta with mean 0.7 and 10th-90th percentiles at ~0.55-0.85 [NV assumption anchored on 60% and 80%].
- No new AI model: the "AI" of this idea is that of ideas 1 and 4.

### 5.6 Uncertainty propagation (Monte Carlo), is it tractable and honest?
- **Tractable, yes:** 10,000 samples × 5 bassins is instant with numpy.
- **The delicate point is the correlation** between yield and protein (nitrogen dilution in high-grain years [V, Terres Inovia 2025 text]; national log correlation -0.16, n=11 [V]). Sampling them separately overstates or understates the variance. Solution from idea 2: **sample "twin seasons"**: for each sample an analogous historical year is chosen and its yield and protein residuals are taken together (bootstrap by year). That way the correlation is preserved without estimating it.
- **Honesty:** the uncertainty in `FG` is a pure assumption and will dominate the interval of the "fit grain" at D2-D3. The contribution-by-link chart (tornado) has to be shown and we have to say that most of the width comes from one assumption. That is rigorous but takes strength away from the "AI" part.

### 5.7 Possible validation
- National: tonnes of contained protein 2015-2025 (11 points) calculated with SAA and the Terres Univia series: 68 to 121 kt [V descriptive calculation, script s7]. Leave-one-year-out over 11 points: descriptive only.
- Bassin: 35 protein means 2019-2025 (manual transcription).
- Interval coverage: with n this small, report the cases, not a percentage.
- The fit fraction **cannot be validated**.

### 5.8 Metrics
Absolute error in kt of protein (national and bassin), CRPS per year, width of the 80% interval, and the variance decomposition per link at each decision date.

### 5.9 What the AI adds and explainability
- Adds: yield and protein before July (ideas 4 and 1) and the choice of twin seasons (idea 2). Area is provided by Agreste; the fit fraction is an assumption.
- Explanation: tornado by link, twin years with their observed values, SHAP of the models from ideas 1 and 4.

---

## 6. MVP and demo

### 6.1 Screens (Streamlit)
1. **National radar:** map of the 5 bassins with expected fit-protein kt and 80% interval, date slider D0 → D3, season selector (2023, 2024, 2025, 2026).
2. **Cascade:** bars area → grain → protein → fit protein, with the origin label of each link (Agreste measured, model, assumption).
3. **Tornado:** which link adds how much width to the interval at the chosen date.
4. **Twins:** the 3 most similar years and what happened.

### 6.2 Demo script (≈ 80 s)
1. "15 April 2026. Agreste says 102.9 thousand ha of pea." National radar D1 with a wide interval (area + climate).
2. Slider to 15/06: Agreste drops to 94.9 kha [V]; the yield model sees a weak year; the radar narrows.
3. 13/07: Agreste's 29.9 q/ha comes in [V]; the grain interval almost collapses and what remains is protein and fit fraction: "we know the protein before; nobody knows the fit fraction".
4. Close: comparison with the use of 140 kt [V].
(The model values come out on Saturday.)

### 6.3 Stack and repo
Same as idea 1 (Python, uv, pandas, numpy, scikit-learn, lightgbm, streamlit, plotly, openpyxl; AWS EC2/S3 for SAFRAN and for hosting). Repo: `radar-proteina/` with `scripts/01_download.sh`, `src/{agreste.py, yield_model.py, protein_model.py, montecarlo.py}`, `app/`, `reports/`.

---

## 7. Hour-by-hour plan (if it were chosen, which I do not recommend)

Roles: **A** data (Agreste, SAA, SAFRAN, quality PDFs), **B** models (ML/CV: yield and protein), **C** product/pitch (Monte Carlo, app, deck, mentors).

### Friday 30/10
| Time | A | B | C |
|---|---|---|---|
| 20:45-21:15 | Launch SAFRAN 1991-2026 on EC2; download Agreste (9 xlsx), SAA, Pea, quality PDFs | Read plans 1 and 4 | **Mentors: would anyone buy a national radar? Is the bottleneck quality or volume?** Eligibility |
| 21:15-22:30 | Parser for Agreste notes (columns 18-20, crop "Pois protéagineux purs") | Climate by dept (idea 4) | Transcribe 35 bassin × year means and dept → bassin map |
| 22:30-23:00 | **Checkpoint 1:** table dept × year × (A note, A final, Y, P) | Climate by site (idea 1) | Declare track |
| 23:00-01:00 | Area revision table | Yield and protein baselines | Monte Carlo with B0 |

**Go/no-go 1 (23:00):** if the mentors say the user is the processor and not the country, **drop this idea and continue with idea 1**, using the radar screen as a module.

### Saturday 31/10
| Time | A | B | C |
|---|---|---|---|
| 08:30-10:15 | Aggregation to bassin | Protein model (idea 1) | App: cascade and tornado with B0 |
| 10:15-13:00 | National and bassin validation | Yield model (idea 4) | Twin seasons for joint sampling |
| **13:00** | **Go/no-go 2:** if either model does not beat its B0, stay with climatology + Agreste and sell the radar as "uncertainty accounting" | | |
| 14:00-18:00 | Replay 2024, 2025, 2026 | Integration | Deck v1 |
| 19:00-23:30 | AWS deploy, README | Leakage review | Rehearsal ×3, backup video |

### Sunday 1/11
07:30-08:30 last rehearsal; 08:30-09:15 upload PDF and profile; **09:30 deadline**; 10:15 pitch; 12:00 backup.

### Cut list
1. Own yield model (use climatology + Agreste). 2. Twins (independent Monte Carlo, state the bias). 3. Bassins (national only). 4. D0 and D1.

---

## 8. Business
- **Proposition:** "The only estimate of French protein fit for human food before harvest, with its uncertainty explained."
- **Who pays:** Terres Univia / FOP (study or observatory service), DGPE / FranceAgriMer (policy monitoring), and as a module for processors and cooperatives. Willingness to pay from the public sector and the interprofessional body: study contracts, on the order of tens of k€ per year [NV assumption, no source].
- **Price benchmarks:** the same as idea 1 (cooperative OAD 8-13 €/ha, Farmstar [F]); I did not find prices for pulse market observatories [NV].
- **Size:** EU pea protein market ~€175M [V]; human food + ingredients use of pea in France 140 kt/year [V]; producer price 250-300 €/t [F, idea 1 and terre-net 21/02/2025 "300 €/t"]. National information service: a handful of possible clients [NV].
- **Adoption:** presentation to Terres Univia as a layer of its balance, which today comes out in November.
- **Competition:** Agreste (area and production free from April and July), Terres Univia (balance in November, quality in December-March), FranceAgriMer (oil and protein-crop balances October/March/June [F]), JRC MARS (national yield for "field peas" [F, idea 4]). The real differential is only protein + fit fraction before harvest.
- **Conclusion:** the economics are **weaker** than idea 1's: it swaps a buyer with an operational pain (the plant) for institutional buyers with an information pain.

---

## 9. Quantified impact (labelled estimates)
1. Protein contained in French pea 2015-2025: 68 to 121 kt/year [V calculation with SAA + Terres Univia, DM 0.86 NV]. The area drop 2023 → 2025 took ~33 kt of contained protein (101.8 → 68.3) [V calculation].
2. Fit grain 2026: 175-234 kt if the fit fraction is 60-80% [NV scenario], against 140 kt of human food + ingredients use [V 2025/26].
3. Anti-dumping: plausible additional need of 17-25 kt of grain for the EU industry [NV scenario, see 2.3].
4. Climate and soil: same as idea 1 (nitrogen input, mitigation according to INRA 2013 [F]); depends on adoption.
Honest message: a national radar informs, it does not change decisions for a specific plant; its impact goes through policy (monitoring of the 8% UAA target [F]).

---

## 10. Pitch (if it were chosen)

| Time | Block | Content |
|---|---|---|
| 0:00-0:40 | Problem | "Europe has protected its pea protein since September. How much food-grade protein will France produce this year? Today it is known in December." |
| 0:40-1:20 | Solution | Cascade area × yield × protein × fit fraction, with dates and sources |
| 1:20-2:40 | Demo | Script 6.2 |
| 2:40-3:20 | Rigour | Tornado, national and bassin validation, what is assumption |
| 3:20-4:00 | Scale | Terres Univia, processors, other pulses |

Slides: title; problem (3 V numbers); timeline of who publishes what and when; cascade; demo; tornado and validation; limits (fit fraction = assumption); business; impact; team and resources.

Likely jury questions:
- **"Agreste already publishes production in July, what do you add?"** Protein and fit fraction before harvest. (Weak answer: the fit fraction is an assumption.)
- **"If 200 kt are fit and 140 are used, what is the problem?"** The honest answer is "quality and location in bad years", which is idea 1.
- **"Who pays?"** Institutional. It is the question that lowers the score the most.
- **"Why protein if it accounts for 2% of the variance?"** Because within the season, with area and yield already known, it is what remains; but it has to be shown.

---

## 11. Risks, mentors, resources, checklist

### Risks
| Risk | Prob. | Mitigation |
|---|---|---|
| The jury sees that national supply is in surplus | High | Do not use the national framing; go to basin (idea 1) |
| The fit fraction dominates the interval and is an assumption | Certain | Show it; separate "grain" from "fit grain" |
| 4 components in 20 h | High | Cuts from section 7 |
| Institutional buyer | High | Pivot to a module of idea 1 |
| April area with an 8-14% error and only 2 years to estimate it | Certain | State n=2 |

### Questions for mentors
1. Does anyone in the filière (Terres Univia, DGPE, a plant) want a national figure for fit protein before harvest? For what decision?
2. Is the 140 kt ceiling for human use plant capacity or lack of good lots?
3. What defines "fit for human food" in practice (split, bruchid damage, colour) and who measures it at reception?
4. Do the Terres Inovia bassins have published department boundaries?

### Prior resources to declare
Desk research (`research/`, including this dossier and plans 1, 2 and 4), aggregated RPG `rpg_pulses_dept_year.csv`, exploration scripts (not reused), open datasets (Agreste notes and SAA, Pea_dataset, SAFRAN, Terres Inovia/Univia PDFs, EU Commission, FranceAgriMer).

### Deliverables checklist
Same as idea 1: track before 23:00; repo with README and licences; app with URL + video; deck PDF with links before Sunday 9:30; online profile; label measured / source / assumption / synthetic on each number; backup at 12:00.

---

## 12. Rubric 1-10 and comparison

| Criterion | Weight | Idea 6 | Justification |
|---|---|---|---|
| Impact and sustainability | 30% | 6 | Attractive national protein sovereignty framing, but public numbers show fit supply > use; impact goes through policy, not through a decision |
| Scientific rigour | 20% | 6 | Honest propagation and well-designed twins; but the most uncertain link (FG) has no data, protein weighs 2% of national variance, and validation is on 11 points |
| Essential AI | 20% | 5.5 | AI sits in two links; area comes from Agreste and FG is an assumption: it looks like a spreadsheet with Monte Carlo |
| Economic viability | 20% | 4.5 | Institutional buyer, few clients, no reference price; the buyer with the pain (the plant) wants its basin |
| Execution and pitch | 10% | 5.5 | Four components in 20 h; nice demo (cascade + tornado) but fragile |
| **Total** | | **5.6** | 0.3×6 + 0.2×6 + 0.2×5.5 + 0.2×4.5 + 0.1×5.5 = 1.8 + 1.2 + 1.1 + 0.9 + 0.55 = **5.55** |

### Comparison with ideas 1, 2 and 4
| Criterion | Idea 1 | Idea 2 | Idea 4 | Idea 6 |
|---|---|---|---|---|
| Impact (30%) | 6 | 6 | 5.5 | 6 |
| Rigour (20%) | 7.5 | 7 | 7.5 | 6 |
| AI (20%) | 6.5 | 6 | 5.5 | 5.5 |
| Economics (20%) | 5.5 | 5 | 4.5 | 4.5 |
| Execution (10%) | 7 | 7 | 7.5 | 5.5 |
| **Total** | **6.4** | **6.1** | **5.9** | **5.55** |

(Scores for ideas 1, 2 and 4 taken from their dossiers [F].)

**Does combining raise the score?** No. The hopes were impact and economics:
- **Impact:** the national framing sounds bigger, but the data (fit supply 175-278 kt vs 140 kt of use) weakens it. It ends up level with idea 1.
- **Economics:** lower, because the buyer moves from the plant to institutions.
- **Rigour and AI:** lower, because two links are added without AI (Agreste area) or without data (fit fraction), and because the decomposition shows that protein barely moves national tonnes.
- **Execution:** lower, because of the four components.

**What is worth salvaging for idea 1 (recommended):**
1. A "tonnes of protein in your basin" screen = latest Agreste note area × yield × predicted protein (2-3 h). It gives idea 1 the tonnage figure the buyer understands.
2. The 35 bassin × year protein means 2019-2025 as external validation by region (stronger than the 11 national points).
3. "Twin seasons" as a way to sample yield and protein together across scenarios.
4. Prepare the answer to "protein weighs little in the tonnes": for the plant, with contracted area fixed, what remains is yield (CV ~15%) and protein (CV 4%), and protein also changes the extraction yield and isolate quality [NV, ask the mentors].

---

## 13. Sources (opened today unless stated)
- Agreste, departmental xlsx of the Infos rapides grandes cultures notes 2025 and 2026: `https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/IraGcu2639/2026_39donnees_grandescultures_departements.xlsx` (and IDs IraGcu2653, 2674, 2688, 26114, 2540, 2591, 2599, 25115) [V]. PDF of the notes: `.../IraGcu2639/2026_39inforapgdescultures.pdf`, `.../IraGcu2674/2026_74...`, `.../IraGcu2688/2026_88...`, `.../IraGcu26114/2026_114...` [V].
- Agreste SAA long series 2010-2025 (ZIP) [V].
- Pea_dataset, doi:10.57745/FW78RE, Recherche Data Gouv [V].
- Terres Inovia / Terres Univia, "Qualité des graines pois" 2019-2025 and "féverole" 2024: https://www.terresunivia.fr/fichiers/publications/qualite-graines-pois-2025.pdf , https://www.terresunivia.fr/fichiers/publications/qg-pois-2024.pdf (and 2019-2023), https://www.terresunivia.fr/fichiers/publications/qualite-graines-feverole-2024.pdf [V].
- European Commission, "Commission acts against imports of pea protein from China", 25/09/2026: https://policy.trade.ec.europa.eu/news/commission-acts-against-imports-pea-protein-china-2026-09-25_en [V].
- FranceAgriMer, protein-crop filière sheet 2026: https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf [V].
- IGN, WFS RPG: https://data.geopf.fr/wfs/ows (GetCapabilities, last layer RPG.2024) [V].
- Réussir, 17/05/2018, "Roquette poids lourd de la protéine de pois": https://www.reussir.fr/roquette-poids-lourd-de-la-proteine-de-pois (80 kt → 125 kt in 2020 in Vic-sur-Aisne; 250 kt with Canada) [V].
- Terre-net, 21/02/2025, "Quel avenir pour les protéagineux en France ?": https://www.terre-net.fr/pois-proteagineux/article/878925/quel-avenir-pour-les-proteagineux-en-france [V].
- Implementing Regulation (EU) 2026/916 (provisional), EU share 59 → 56%: search engine only, EUR-Lex blocks [F].
- FranceAgriMer oil and protein-crop balances (calendar October/March/June): search engine only [F].
- Target of 8% UAA in pulses by 2030 (Climate and resilience law): search engine only [F].
- Prior dossiers in the repo: `plans/1_pea_protein.md`, `plans/2_twin_season.md`, `plans/4_departmental_yield.md` [F].

---

## Cleanup
The data downloaded to `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/plan6/data/` (9 Agreste xlsx, SAA ZIP, Pea_dataset, 8 Terres Univia PDFs, FranceAgriMer sheet) was deleted at the end of 30/10/2026. The scripts remain in `.../plan6/scripts/`.
