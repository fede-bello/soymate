# Idea 5: pre-harvest yield estimation for pea/chickpea trial plots with multispectral drone imagery

Independent verification and deepening of the brief `archive/initial_ideas/track3_pest_risk_and_drone_yield_mvp_plans.txt` (pages 4 to 6, sources Y1 to Y9). Date: 29/10/2026.

Rule followed: no model was trained or tuned, and there is no solution code. What was done was data inspection (Zenodo metadata, download of the xlsx files and the PDF, listing of the ZIP via HTTP range, download of **one** TIFF by range to check bands, dtype and georeferencing, and a quicklook). The inspection scripts are in the session scratchpad (`idea5_scripts/`), not in the repo.

Legend: **[V]** verified directly by me on the file or the API. **[F]** read in the cited source (by me or by a research subagent). **[NV]** not verified.

---

## 1. Executive summary

- The dataset exists, is CC BY 4.0, and the brief's numbers are right: 275 TIFF, 34 of 0 bytes, 630/831/954 rows with numeric `seedyield`, unit kg/ha. [V]
- What the brief **did not say** and that changes the plan: each TIFF is **a single band + alpha channel** (5 files per date), the ZIP is compressed with **Deflate64** (Python's `zipfile` cannot open it), the mosaics are **georeferenced** (UTM 11N, ~3,2 cm/px), and the 28 empty 2019 TIFF files are almost all Pullman 2019. [V]
- Strong prior art: Zhang et al. 2021, with **these same data**, already reached test R² of 0,89 (chickpea 2018) and up to 0,80 (green pea) with LASSO on vegetation indices. Repeating "predict yield from the image" is not innovation. [F]
- The real gap: nobody has evaluated **transfer across years/sites**, **early forecasting by flight date**, **uncertainty**, or a **breeder decision metric** (would they have picked the same lines?). [F]
- There is no open French or European drone/Sentinel-2 + yield dataset for legumes. The relevance to France is narrative (French breeders, Pea4Ever, Roquette), not data. [F]
- Verdict: **feasibility 5/10** for 20 h. It is flashier than Idea 3 but has more prior art and more data-engineering risk, and the link to France and to human food is indirect.

---

## 2. Dataset verification

### 2.1 Zenodo records (API) [V]

| | v1 | v2 |
|---|---|---|
| Record | https://zenodo.org/records/8280431 | https://zenodo.org/records/10456829 |
| DOI | 10.5281/zenodo.8280431 | 10.5281/zenodo.10456829 |
| Published | 2023-08-24 | 2024-01-03 |
| License | CC BY 4.0 | CC BY 4.0 |
| Files | `Images.zip` (10 761 585 218 B), `PulsePlotMaps_2017-2019.pdf` (13 976 474 B), 3 xlsx | only the 3 xlsx files |

Authors: Chongyuan Zhang, Kingsley Umani, Rebecca J. McGee, George J. Vandemark, Sindhuja Sankaran. There are only two versions (API `/versions`).

**Correction to the brief:** v1 **also** includes the 3 xlsx files. I did a cell-by-cell diff between v1 and v2: **the only difference** is the unit of `seedyield` in the Description sheet, which says `grams/hectare` in v1 (error) and `kg/hectare` in v2. The data in the trial sheets is identical. So there is no "compatibility trap" between versions, only a corrected unit label. [V]

### 2.2 xlsx spreadsheets (v2) [V]

| Year | Trial sheets | Rows with numeric `seedyield` | Pea | Chickpea |
|---|---|---|---|---|
| 2017 | 10 (+ Description) | 630 | 534 | 96 |
| 2018 | 11 (+ Description) | 831 | 576 | 255 |
| 2019 | 13 (+ Description) | 954 | 666 | 288 |
| **Total** | 34 | **2 415** | **1 776** | **639** |

- Unit: `seedyield` in **kg/ha** (v2). `plotseedwt` in grams. In the `1901 Fairfield` sheet there is also `yieldlbs` (lb/acre). The mean ratio 2269,5 / 2543,7 = 0,892 matches the kg/ha → lb/acre conversion, which confirms kg/ha. [V]
- Ranges: pea typically 1 000 to 4 000 kg/ha, with minimums of 134 (1902 Pullman) and 138 (1702 Pullman). Chickpea from 248 to 4 311 kg/ha. Means per trial and site are very different (for example 1801 green pea 2018: Fairfield 2 239, Pullman 2 740, Genesee 3 600), so **the site effect dominates the variance**. [V]
- Keys: `plot` is unique within each sheet (1..N). There are `block` columns (`bloc` in two sheets, absent in 1803/1804 Pullman 2018), `entry`, and `entry name`. 3 replicates in all trials. [V]
- Extra traits (flowering, maturity, height, etc.) **only in Pullman**. The Fairfield/Genesee 2018 sheets only include `seedyield`. [V]
- No NDVI column and no band columns. I confirm what the brief says. [V]
- Description sheet: GPS per site, sowing date, **plot rotation angle** (useful for aligning the grid) and **UAV flight dates**. [V]

Flight dates (Description sheet, v2) [V]:

| Site-year | Sowing | Flights |
|---|---|---|
| Fairfield 2017 | 11/05 | 24/07 (only one) |
| Pullman 2017 pea | 11/05 | 05/06, 26/06, 07/07, 21/07, 28/07 |
| Pullman 2017 chickpea | 11/05 | the above + 07/08, 16/08 |
| Fairfield 2018 | 21/05 | 12/06, 29/06, 12/07, 25/07, 07/08 (chickpea without 07/08) |
| Genesee 2018 | 08/05 | 08/06, 26/06, 09/07, 23/07, 06/08 |
| Pullman 2018 | 05/05 | 08/06, 22/06, 03/07, 19/07, 27/07 |
| Fairfield 2019 | 06/05 | 10/06, 28/06, 12/07 (+23/07 chickpea) |
| Genesee 2019 | 03/05 | 05/06, 18/06, 05/07, 16/07 |
| Pullman 2019 | 04/05 | advanced 05/06, 17/06, 05/07, 16/07; preliminary 17/06, 05/07, 17/07 |

Inconsistencies in Description that need to be kept in mind [V]:
- `1804 Pullman` 2018 says 20 plots, but the sheet has 60 rows (20 entries x 3).
- `1881 Genesee` 2018 is listed as "Advanced Green Pea", but the code 18**8**x and the sheet correspond to chickpea.
- `1883 Pullman` says 22 varieties and the sheet has 33 distinct entry names.
- The Fairfield file names say "PeaLentil": the flight also covers lentil trials that are **not** in the spreadsheets.

### 2.3 Images.zip (central directory via HTTP range, without downloading the 10.8 GB) [V]

- 345 entries: 275 `.tif` + 70 directories. **241 non-empty TIFF, 34 of 0 bytes.** Matches the brief.
- **Each TIFF is one band** (`blue`, `green`, `red`, `red edge`, `nir`), i.e. 55 date-block sets of 5 files, of which **44 are complete**.
- Empty by year: **2017: 6** (always `red edge` or `green` of Pullman chickpea), **2018: 0**, **2019: 28**. In 2019, Pullman preliminary trials are empty on all three dates, Pullman advanced is empty on 05/07 and 16/07, and on 17/06 it only has `nir`. **Pullman 2019 has only one complete set (05/06, very early)**: 519 plots from 2019 are practically left without a useful mid-cycle image.
- **Compression: method 9 = Deflate64** in all 241 files. Python's `zipfile` does not support it: you need `7z`, the `inflate64` package or `zipfile-deflate64`. I solved it with `inflate64`.
- Compressed size per site-year: 2017 Fairfield 0,12 GB, 2017 Pullman 1,45 GB, 2018 Fairfield 2,28 GB, **2018 Genesee 1,04 GB**, 2018 Pullman 3,4 GB, 2019 Fairfield 1,18 GB, **2019 Genesee 1,0 GB**, 2019 Pullman 0,29 GB.
- A single TIFF can be downloaded by range (without downloading the ZIP): I tested it and it works.

### 2.4 One real TIFF: `Pullman_Chickpea_Jul21_transparent_mosaic_nir.tif` (2017) [V]

- 14 510 010 bytes uncompressed (matches the directory).
- **2 bands**: band 1 = raw reflectance in `uint16` (0 to 65 520), band 2 = alpha mask (0/255). No declared nodata, LZW.
- **Georeferenced**: EPSG:32611 (UTM 11N), resolution 0,0325 m/px, ~107 x 68 m. Software `pix4dmapper`.
- 19 % of pixels are zero (outside the mosaic).
- Quicklook: the plots are sharp in a grid, with white markers on the ground. But there are **strong illumination gradients and circular stitching artifacts**: this confirms it is a mosaic that is **not radiometrically calibrated**. Comparing raw values across dates or years without normalizing would be an error.
- With ~1,5 x 4,9 m plots (Umani 2024) and 3,2 cm/px, each plot has on the order of 7 000 pixels. Resolution is more than enough.

### 2.5 PulsePlotMaps_2017-2019.pdf [V]

13 pages, generated from PowerPoint. These are **row/column grid tables → plot number** per trial (for example Fairfield 2017: rows 1 to 12 = 1701, 13 to 18 = 1701B, 19 to 25 = 1702, with borders and "NA"). They are not georeferenced polygons. To extract plots you have to draw or fit a rotated grid (the angle is in Description) over the mosaic, for example in QGIS, once per site-year. That the mosaics from different dates of the same site are well co-registered is likely (Pix4D georeferenced) but **[NV]**.

---

## 3. Prior art and the innovation gap

### 3.1 Zhang et al. 2021, Front. Plant Sci. 12:640259 [F]
https://www.frontiersin.org/articles/10.3389/fpls.2021.640259/full
- Same data (Pullman, Fairfield, Genesee 2017 to 2019), MicaSense RedEdge 5 bands, flights at 25/30/45 m.
- Features: canopy area + mean and sum per plot of NDVI, GNDVI, SAVI, NDRE, TVI. LASSO with 5-fold CV, 3:1 split at plot level and leave-one-out at cultivar level.
- Test R² (Table 2): chickpea 2018 combined 0,89 (plot) and 0,91 (cultivar); chickpea 2019 0,82 and 0,76; chickpea Pullman 2017 only 0,32; green pea up to 0,72 per site and 0,80 combining sites within the year. Pearson correlation up to 0,85 in yellow pea.
- It does not report RMSE/MAE, there is no yellow pea model, and it **does not validate across years**.
- Watch out: combining sites within a year with a random split inflates R², because the model learns the difference between sites (which in the spreadsheets is huge).

### 3.2 Marzougui et al. 2023, Front. Plant Sci. 14:1111575 [F]
https://www.frontiersin.org/articles/10.3389/fpls.2023.1111575/full
- Pea only. Site 1: Pullman 2019 advanced, 65 entries, 203 plots. Site 2: Johnson WA 2020 (outside the Zenodo dataset).
- My note: in Zenodo, 1901 + 1901B + 1902 Pullman 2019 add up to 68 entries and 204 plots, so it is very likely the same trial **[NV]**. And precisely the Pullman 2019 advanced TIFFs for 05/07 and 16/07 are empty in the ZIP, so **its analysis cannot be reproduced** with what was published.
- UAV RedEdge-MX + WorldView-2/3 pan-sharpened. Random forest, 80/20 split by entry, 10 seeds.
- A single UAV date: R² 0,46 ± 0,16 (RMSE 486 kg/ha). Best UAV + satellite fusion, two dates, site 1: R² 0,72 ± 0,08, RMSE 259 ± 53 kg/ha. Site 2: R² 0,50. There is no training on one site and testing on the other.

### 3.3 Umani et al. 2024, Data in Brief 53:110013 [F]
https://pmc.ncbi.nlm.nih.gov/articles/PMC10907176/
- MicaSense RedEdge 12 bit, bands B 465-485, G 550-570, R 663-673, RE 712-722, NIR 820-860 nm. Flights 10:00 to 15:00.
- Reflectance panel on every flight (MicaSense in 2017, Spectralon 99 % in 2018-19), but the published mosaics are explicitly "uncalibrated". **The panel values are not in the dataset** (there are no panel files in the ZIP) [V for the ZIP].
- Plots 6,1 x 1,5 m, trimmed to 4,9 m after emergence.

### 3.4 Later use of the dataset [F]
- 6 citations in Semantic Scholar and OpenAlex: https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.dib.2023.110013/citations
- The only one that uses the images: a chickpea GxE study (J. Crop Improvement 2025, doi 10.1080/15427528.2025.2489605), with AMMI/GGE on GNDVI/SAVI, without yield R². Abstract only: https://verso.uidaho.edu/esploro/outputs/journalArticle/Evaluation-of-genotype-x-environment-interaction/996802444501851
- **There is no published ML benchmark on this dataset.**

### 3.5 Other UAV legume studies [F, mostly abstract only]
| Study | Crop | Result |
|---|---|---|
| Quirós Vargas et al. 2019, Sensors 19:2031 (https://europepmc.org/search?query=DOI:10.3390/s19092031) | Winter and spring pea | High image-yield correlation at flowering; no yield R² in the abstract |
| Liu et al. 2024, Drones 8:227 (https://doaj.org/article/b231f81fe219492b8edc48be4ed8d084) | Pea, RGB + MS | R² 0,81 (Cubist) at grain filling |
| Ji et al. 2022, Plant Methods (https://plantmethods.biomedcentral.com/articles/10.1186/s13007-022-00861-7/tables/2) | Faba bean | SVM R² 0,72, RMSE 824 kg/ha |
| Norway 2024, Precision Agriculture (https://link.springer.com/article/10.1007/s11119-024-10121-4) | Faba bean, 38 cultivars | R² 0,83 at BBCH 60 (snippet) |
| AGILE lentil, Saskatchewan (https://knowpulse.usask.ca/bio_data/3680078) | Lentil | Optimal window R5-R6, no published R² |

No French or European paper on UAV pea yield was found (not finding one does not prove that none exists).

### 3.6 The gap
1. **Transfer across years or sites**: all R² values come from random splits within the year. The dataset (3 sites x 3 years) allows leave-one-site-year-out, and nobody has published it.
2. **Early forecast curve**: how accuracy rises flight by flight, and which is the earliest date that is "good enough".
3. **Calibrated uncertainty**: nobody gives prediction intervals.
4. **Breeder decision metric**: top-k overlap, ranking correlation, how many good lines would have been discarded.
5. **Radiometric normalization between dates/years** without a panel (for example normalized indices, normalization by bare soil or by common check varieties): without this there is no transfer.

---

## 4. French context

### 4.1 Open French/European data
- **There is no** open dataset of drone or Sentinel-2 + yield per plot for pulses in France or Europe. Searches on Recherche Data Gouv (https://entrepot.recherche.data.gouv.fr/api/search?q=pea%20UAV) and Zenodo returned nothing relevant. [F]
- Terres Inovia (the French technical institute for oilseeds and protein crops) on data.gouv.fr only publishes the variety catalog, without yields (https://www.data.gouv.fr/organizations/terres-inovia). Post-registration results appear on myvar.fr as per-variety summaries, without geometry or images. License of myvar [NV].
- Phenome-Emphasis, Arvalis, CASDAR projects (the French agricultural R&D funding account), and EU projects (LegValue, ProFaba, EUCLEG, LIVESEEDING, Radiant): nothing downloadable found [NV].
- RPG (Registre parcellaire graphique, the French geospatial parcel register): open polygons of PAC parcels (PAC: Politique agricole commune, the EU Common Agricultural Policy) (https://www.data.gouv.fr/datasets/rpg-2022-registre-parcellaire-graphique). The PAC codes include PCH (chickpea), LEC (lentil), FVL (faba bean) (https://www1.telepac.agriculture.gouv.fr/telepac/pdf/tas/2025/Dossier-PAC-2025_notice_cultures-precisions.pdf). Whether the public file keeps the fine code or only the group: [NV].
- **Sentinel-2 does not work at trial plot scale**: a plot of ~7,35 m² against a 100 m² pixel. It would only make sense for commercial fields, and there are no open field yields to validate it against.

### 4.2 Real user and willingness to pay
- Most defensible user: **legume breeders** and **Terres Inovia/GEVES** (the French official variety testing and seed control group) in their trial networks. France has about 6-7 active breeders of protein crops (https://www.reussir.fr/ladepeche/la-marge-de-progres-en-genetique-est-tres-importante-en-proteagineux). [F]
  - Agri Obtentions registers 3 to 8 varieties per year (https://groupes-filieres.hub.inrae.fr/Media/Files/gf-legumineuse/7-matthieu-floriot-agriobtentions). [F]
  - Lemaire Deffontaines: 5 pea varieties in 3 years, ~10 years per variety (https://www.terre-net.fr/observatoire-technique-culturale/appros-phytosanitaire/article/un-flux-varietal-dynamique-pour-ameliorer-les-performances-du-pois-proteagineux-216-208919.html). [F]
  - RAGT, Florimond Desprez, KWS in pea: [NV].
  - Scale: spring pea 2023, 19 varieties in 18 to 28 trials (https://www.terre-net.fr/pois-proteagineux/article/860289/proteagineux-de-printemps-hausse-des-rendements-grace-aux-progres-genetiques). [F]
  - Terres Inovia Pea4Ever targets 300 000 ha of pea and says genetic progress is insufficient (https://www.terresinovia.fr/sites/default/files/2026-01/3_rtti_bruz_22012026_pea4ever_am.pdf, search snippet only, the PDF blocked the download). [F partial]
- **Direct competitor: Hiphen** (Avignon), drone and satellite phenotyping, 15 M plots, more than 6 000 flights, use case "yield correction" (https://www.gcirc.org/fileadmin/documents/Proceedings/TM_2025/Presentations/GCIRC_HIPHEN.pdf). It bought the phenotyping activities of Aurea Imaging in 2025 (https://www.silicon.co.uk/press-release/hiphen-acquires-aurea-imagings-phenotyping-activities-cementing-its-position-as-the-global-leader-in-drone-based-image-analytics). Legume customers: [NV].
- Warning: Airinov (drones for farmers) closed in 2019 with ~200 k€ of quarterly revenue (https://futurefarming.com/tech-in-focus/parrot-pulls-plug-on-airinov). The buyer is the breeder or the technical institute, not the farmer.
- Prices: weak evidence. ~15 €/ha for a drone nitrogen map in 2014 (https://www.terre-net.fr/2014/article/99008/alexandre-villain-agriculteur-20-d-economie-a-l-hectare-en-colza); saving of ~4,11 £ per plot versus manual measurements (Rothamsted, https://repository.rothamsted.ac.uk/item/97q41). Current price per plot in France and total number of pea plots per year: [NV].

### 4.3 Is it human food?
- FranceAgriMer (the French national agency for agricultural and seafood products), 2026 pulse sheet (verified by me on the PDF: https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf) [V]:
  - Average 2020/21 to 2024/25: 282 800 ha, 800 800 t, of which **pea 604 kt (75 %)**.
  - Domestic use of **pea + faba bean combined** in 2024/25: **146 kt human food vs 62 kt animal feed** (5-year average: 155 vs 92 kt). On the domestic market, the human share already weighs more. Watch out: it is pea and faba bean added together, not pea alone.
  - Exports: 200 kt of pea (74 % to the EU, Belgium the first customer) and 61 kt of faba bean, with Norway as the first destination (feed for fish farming, that is, animal feed).
- Pea area is falling: ~150 000 ha in 2023, 124 000 in 2024, 98 000 in 2025 according to the Terres Inovia sheet (https://www.terresinovia.fr/sites/default/files/2026-01/fiche_terres_inovia_qual_graines_pois2025.pdf, snippet only, 403 when downloaded). An article published before harvest gave 159 000 ha for 2025 (https://www.pleinchamp.com/actualite/emblavements-2025-timide-embellie-des-surfaces-en-france): conflicting figures, **[NV]**.
- Roquette Vic-sur-Aisne: ~80 kt/year of pea in 2017, target 125 kt by 2020, 100 % French sourcing, more than 2 000 growers (https://www.reussir.fr/roquette-poids-lourd-de-la-proteine-de-pois, https://www.reussir.fr/grandes-cultures/roquette-developpe-une-filiere-pois-pour-le-marche-des-proteines-vegetales). Current figures: [NV].
- Chickpea in France: ~20 000 ha and 30 kt in 2021 (https://valenceromansagglo.fr/app/uploads/2024/11/CP_Mois-du-pois-chiche.pdf). Monitoring network of 75 plots in Occitanie (https://draaf.occitanie.agriculture.gouv.fr/IMG/pdf/bulletin_sante_du_vegetal_bilan_pois_chiche_2025.pdf). 2024-25 figure: [NV]. Chickpea is 100 % human food and is a cleaner story for the jury than pea.
- Plan Protéines (the French national protein plan): 8 % of the SAU (utilized agricultural area, ~2 Mha) in legumes by 2030 (https://agriculture.gouv.fr/telecharger/122407). [F]

---

## 5. Assessment

| Criterion | Score | Comment |
|---|---|---|
| Feasibility in 20 h | **5/10** | Real, accessible data, visible plots, georeferencing ready. But you have to download 1-2 GB with Deflate64, fit a plot grid per site-year, normalize without a panel, and only then model. If the grid gets stuck, it eats the weekend. |
| Essential AI | **Medium** | The vision part (segmenting the canopy, extracting features per plot) is necessary; the model can be LASSO or RF. A CNN is not justified with ~150-500 plots per site-year. "Essential AI" is defensible if the contribution is transfer + uncertainty, not the regressor. |
| Innovation | **Low-medium** | Within-year prediction is already published with R² 0,7-0,9 on the same data. What would be new: transfer across years, curve by date, calibrated intervals, breeder selection metric. |
| Impact France | **Weak-medium** | Indirect: speeding up the selection of pea/chickpea varieties (Pea4Ever, Plan Protéines, Roquette sourcing). Zero French data to validate against. |
| Scientific rigor | High potential | If leave-one-site-year-out is done honestly, the jury will value it. |
| Economic viability | **Medium-low** | Small market (6-7 breeders + Terres Inovia/GEVES), established competitor (Hiphen). |

### 5.1 Impact story for France
"French pea fell to ~100 000 ha and Terres Inovia says genetic progress is not keeping up. Each variety takes ~10 years; much of that is harvesting and weighing thousands of trial plots per year. If with 2 or 3 drone flights at mid-cycle a breeder can confidently discard the clearly bad lines, and know **when** the prediction is not reliable, it speeds up variety selection cycles for the human protein market (Roquette, chickpea in Occitanie)." It has to be stated explicitly that the demo uses US trials.

### 5.2 Business model
- B2B SaaS or a per-trial service for breeders and variety evaluation networks: the breeder (or their drone provider) uploads the orthomosaics and the plot layout, and receives a line ranking with intervals and low-confidence alerts.
- Indicative price: per plot per season (on the order of a few euros, anchored to the ~4 £ per plot saving reported by Rothamsted). **No verified French price.**
- Risk: Hiphen already sells phenotyping. Possible positioning: a legume-specific module, with transfer across environments and uncertainty measurement, or a partnership instead of competition.

### 5.3 Main risks
1. **Plot registration**: the rotated grid has to be drawn by hand; if the dates are not co-registered, it has to be repeated per date.
2. **Radiometry**: uncalibrated mosaics, with visible gradients; a different panel in 2017 vs 2018-19. Ratio indices (NDVI, GNDVI) soften this but do not solve it.
3. **Site effect**: the variance between sites is huge; a high combined R² can be pure site identification. R² has to be reported within site.
4. **Small effective N**: ~32 entries x 3 replicates per trial.
5. **Data gaps**: Pullman 2019 almost without images, Fairfield 2017 a single date, red edge missing for chickpea 2017.
6. **France / human food narrative**: the jury may read it as "a repackaged WSU paper".
7. **Deflate64**: silly, but blocking if nobody knows about it on Friday night.

### 5.4 Concrete MVP and demo
**Recommended cut: advanced green pea (1801/1901) + kabuli chickpea (1881/1981) at Genesee 2018 and Genesee 2019.** Reasons [V]: the two site-years have all the complete 5-band sets, are ~1 GB each, and are the same site with the same trial codes in two years, which enables **train 2018 / test 2019** (which nobody has published). Genesee 2018 = 96 + 63 plots, Genesee 2019 = 87 + 48 (1901B) + 72 plots. Plan B: add Fairfield 2018/2019 (2,3 + 1,2 GB) for leave-one-site-out.

Steps (all during the event):
1. Download only those folders from the ZIP by range (or the full ZIP if the event network can handle it) and decompress with 7z/inflate64.
2. Draw a grid per site-year in QGIS using the rotation angle from Description and the plot-map PDF; validate with 3-4 plots by eye. Export polygons with `trial`, `plot`.
3. Per plot and date: canopy mask (NDVI/SAVI threshold), cover fraction, mean NDVI, GNDVI, NDRE. Use only ratio indices to mitigate the lack of calibration.
4. Baselines: trial mean; the entry's mean in other years (if the variety is repeated).
5. Model: regularized regression or RF; intervals via split conformal prediction instead of ad hoc bootstrap.
6. Evaluation: train 2018 → test 2019 (and the reverse), by cumulative flight date (only flight 1, flights 1-2, ...). Report MAE in kg/ha, R² **within trial**, Spearman of the entry ranking, and top-30 % line overlap, plus interval coverage.
7. Demo: map of the trial with plots colored by predicted yield and interval; a flight-date slider showing how the ranking changes and how much the uncertainty shrinks; a table of "lines you would discard today at X % confidence" vs what happened at the real harvest.

### 5.5 Cut-off rule
- **Hour 3**: if there is no site-year with a validated plot grid and features extracted for at least one date, drop Idea 5 and move to Idea 3 (or to a spreadsheet-only model, presented as such).
- **Hour 8**: if the imagery model does not beat the trial-mean baseline on within-site MAE in the 2019 test, present the negative transfer finding as the result and do not promise a product.
- Do not add Sentinel-2, French data or neural networks before the one-site-year pipeline is working.

---

## 6. What was wrong or incomplete in the previous brief

| Brief claim | Status |
|---|---|
| 275 TIFFs, 241 non-empty, 34 at 0 bytes, ZIP ~10,8 GB | Correct [V] |
| 630/831/954 numeric rows, 10/11/13 sheets | Correct [V] |
| PDF of 13 pages, not georeferenced polygons | Correct [V]. Also: they are row/column tables, not layout images |
| "Version trap: v2 without images, confirm compatibility with v1" | Incomplete: v1 **also** has the xlsx files and the data are identical; only the unit changes from `grams/hectare` (v1, wrong) to `kg/hectare` (v2) |
| "Confirm target units" | Resolved: kg/ha, confirmed with the `yieldlbs` column |
| "Organized by year, site, date and band" | Correct, but it does not say that **each TIFF is one band + alpha** (55 sets, 44 complete) |
| "2018 has no empty TIFFs" | Correct [V]. Missing: **Pullman 2019 is almost entirely empty** (28 of the 34 empty files) |
| Does not mention compression | Missing: **Deflate64**, which Python's standard library cannot open |
| Does not mention georeferencing | Missing: the mosaics **are georeferenced** (UTM 11N, 3,2 cm/px); that simplifies plot registration quite a lot |
| Marzougui 2023 "includes a separate 2020 trial" | Correct. In addition, its site 1 (Pullman 2019, 203 plots) is almost certainly 1901/1901B/1902, whose July dates are **empty** in the ZIP: it is not reproducible with the public data |
| "Description sheets include flight dates" | Correct. But there are inconsistencies (1804 Pullman 20 vs 60 plots, 1881 Genesee labeled as pea, 1883 Pullman 22 vs 33 entries) |
| User: breeder or research agronomist | Agreed |

---

## 7. Not verified

- Co-registration between dates of the same site (I only opened one TIFF).
- Reflectance panel values (not in the ZIP; they would have to be requested from the authors).
- Current French price per phenotyped plot and number of pea trial plots per year in France.
- Hiphen's legume customers; pea breeding programs at RAGT, Florimond Desprez, KWS.
- 2025 pea area (98 000 vs 159 000 ha depending on the source) and current chickpea area.
- Whether the public RPG carries the fine crop code (PCH, LEC, FVL).
- Liu 2024, Ji 2022, Norway 2024 and Quirós Vargas 2019: abstract or snippet only.
