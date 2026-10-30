# Dossier Idea 5: Yield of pea and chickpea trials from drone imagery (full dossier)

Date: 30/10/2026 (Friday morning of the event). Base: `archive/research/idea5_drone.md`, re-verified.

Legend: **[V]** I verified it myself on the file, the API or the primary source in this session. **[F]** read from an open source in this session (by me or by a subagent that opened the page). **[NV]** not verified, estimate or hypothesis.

Rule followed: I did not fit any predictive model, did not run cross-validation and did not compute prediction metrics. What I did was exploration: download data, read metadata, descriptive statistics, check joins, fit a plot grid for registration QA, and measure displacements between dates. The exploration scripts are **not reused** at the event (see section 11).

---

## 1. Summary in 5 lines + verdict

1. The WSU/USDA dataset (Zenodo 8280431, CC BY 4.0) is real, downloadable in parts in 11 minutes for Genesee 2018+2019 (2.04 GB, 45 TIFF, CRC ok), and the plot grid is detected almost on its own: 9 strips x 20 positions (2018) and 9 x 26 (2019), period 2.0 m x 6.1 m, consistent with the plans in the PDF. [V]
2. But there are three traps that were not stated: (a) the mosaics from different dates are shifted relative to each other by 0.2 to 0.55 m (the grid has to be re-aligned per date), (b) there are border rows at the ends that shift the plot mapping if they are not counted, and (c) the values are uncalibrated DN with soil NDVI varying from -0.28 to -0.05 between dates. [V]
3. The scientific ceiling is low, and that is a finding in itself: the repeatability (H² of entry means) of 1801 Genesee 2018 is **0.12** with a block gradient from 3,278 to 3,933 kg/ha, and the ranking of the 18 common peas between 2018 and 2019 correlates only 0.41 (Spearman; chickpea 0.20 with 15 entries). [V]
4. The prior art with these same data gives an R² **within Genesee** of only 0.33 (chickpea 2018) and 0.51 (chickpea 2019); the 0.89 and 0.91 come from combined sites, inflated by the site effect. Nobody validated across years. [F]
5. France: there is no French data, the user is a plant breeder or the variety evaluation network (not the farmer the track asks about), GEVES only tests drones for height in maize, sunflower and alfalfa, and Pea4Ever (Limagrain + Florimond Desprez + RAGT) already does drone phenotyping. [F]

**Verdict: do not choose it as the main idea (5.2/10 weighted).** It is technically feasible and eye-catching, but it loses on impact (30%) and on economic viability (20%) against ideas with a farmer user and French data. It serves as a plan B only if the team wants a pure vision project and accepts presenting it as "a methodology transferable to the French variety evaluation network". If chosen, the honest framing is "triage of lines with calibrated uncertainty and a low-confidence alert", not "we predict the yield".

---

## 2. Problem, user and decision

**Concrete user:** the person in charge of evaluation in a pea or chickpea breeding program (for example the trials engineer at PeaBoost / Pea4Ever, the GIE of Limagrain, Florimond Desprez and RAGT [F]), or the Terres Inovia engineer who coordinates the post-registration chickpea network (13 trials sown in 2024, 9 validated [F]).

**Decision they make:** in July, before harvest, which lines to advance to the following year (or to more sites) and which to discard, and whether a trial is so heterogeneous that it must be discarded or spatially corrected.

- **When:** between flowering and grain filling (flights from late June to mid-July in the dataset; in France, spring pea harvested in July [NV]).
- **With what information today:** visual scores, occasional manual measurements, and the harvest with a plot combine and plot-by-plot weighing. The final decision is made with the harvested yield, in autumn, when seed for the next sowing must already be ordered [NV].
- **Cost of getting it wrong:** discarding a good line costs years of breeding (each pea variety takes ~10 years, prior research [F, not reopened]); advancing a bad one costs a year of multi-site trials. A heterogeneous trial read badly (such as 1801 Genesee 2018, H² 0.12 [V]) can invert rankings.

**What the track asks for and does not quite fit:** the track asks how AI helps "farmers and regions" produce plant protein for human food and make money from it. The plant breeder is an indirect link: better varieties → more yield and stability for the farmer. This has to be said that way in the pitch, and we should not pretend the user is the farmer.

---

## 3. Hypotheses

| # | Hypothesis | Type | Status | Evidence | If false |
|---|---|---|---|---|---|
| H1 | The ZIP can be downloaded in parts and decompressed | Data | [V] | Range requests on `Images.zip`, Deflate64 with `inflate64`, 45/45 Genesee TIFF with correct CRC, 2.04 GB in 671 s | Download the whole ZIP (10.8 GB) on AWS and extract with `7zz` [NV that 7zz extracts Deflate64, known to support it] |
| H2 | Genesee 2018 and 2019 are complete (5 bands x all dates) | Data | [V] | 2018: 5 dates x 5 bands; 2019: 4 dates x 5 bands; no empty files; same dimensions across bands of one date | n/a |
| H3 | Bands of the same date share a grid | Data | [V] | Same width, height, resolution and bounds per date | n/a |
| H4 | Dates of the same site are co-registered | Data | **Partly false** [V] | Displacements of 0.2 to 0.55 m between dates (profile correlation and phase correlation). See 4.3 | Re-align the grid per date with 1D profile correlation (seconds of compute) and shrink polygons to 0.4 m |
| H5 | The rotated grid can be fitted without QGIS | Technique | [V] | Angle from profile sharpness + strips + gaps between plots; correct visual overlay on 2018 Jul9 and 2019 Jul05 | Draw the 4 corners by hand in QGIS per date (this is what Zhang et al. did [F]) |
| H6 | The angle in the Description sheet is usable | Data | [V] | 2018: Description 39°, fitted 50.2° from east = 39.8° from north. 2019: 16° vs 74.6° from east = 15.4° from north. It is an azimuth | n/a |
| H7 | The PDF plan maps 1 to 1 onto the visible cells | Data | [V] with caveat | 2018: 9 x 20 cells = 18 rows + 2 borders; chickpea in 7 rows at the SW end (visible on Aug6, when the pea is already senescent). 2019: 9 strips, 24 rows + borders, chickpea at the south end | **Column orientation (column 1 at NW or SE) unresolved**. Resolve with the overlay figure from the Data in Brief [F, exists] or with the block gradient |
| H8 | Quotient indices are comparable across dates | Data | **False** [V] | Raw soil NDVI: -0.28 to -0.05 depending on date; soil DN in red > NIR (impossible in real reflectance) | Relative features: standardise per date and trial, normalise by alley soil, use rankings |
| H9 | The image signal does not saturate | Data | **Partly false** [V] | Canopy fraction 0.95 to 1.00 in almost all pea plots on Jul9 2018 and Jul05 2019 | Use intensity (NDRE, relative NIR), early dates, and senescence (Aug6) |
| H10 | The harvested yield is a reliable ground truth | Data | **Weak** [V] | H² of entry means: 1801 G18 0.12; 1881 G18 0.59; 1901 G19 0.65; 1901B G19 0.68; 1981 G19 0.68 | Report the repeatability ceiling; primary metric on trials with H² ≥ 0.5 |
| H11 | There are common entries across years to evaluate transfer | Data | [V] | Pea 1801 vs 1901: 18 common; chickpea 1881 vs 1981: 15 common; 1901B vs 1801: 1 | Evaluate only ranking within a year |
| H12 | The problem is real for French plant breeders | User | [F] partial | CTPS lists "intégration d'outils pour améliorer l'efficacité de l'évaluation" (integration of tools to improve evaluation efficiency) as a prospect; Pea4Ever already uses drones | If they already solve it (Hiphen, Pea4Ever), the value shrinks to a module |
| H13 | Someone pays for this | Market | [NV] | No public prices for per-plot phenotyping | Position as a component for Hiphen or as a public tool (Terres Inovia) |
| H14 | Pea is human food | Market | [F] partial | Pea + faba bean, domestic use 2024/25: 146 kt human vs 62 kt animal (FranceAgriMer, prior [V]); chickpea 100% human | Put chickpea first |
| H15 | It can be done in 20 hours of work | Technique | [NV] | Exploration: grid and QA of two site-years took me ~75 min knowing what to look for | Cut to one site-year and to chickpea |

---

## 4. Datasets

### 4.1 Images: `Images.zip` (Zenodo 8280431) [V]

- URL: https://zenodo.org/records/8280431 ; file: `https://zenodo.org/api/records/8280431/files/Images.zip/content` (10,761,585,218 B). Licence CC BY 4.0 (API). DOI 10.5281/zenodo.8280431.
- Compression: Deflate64 (method 9) on all TIFF files. Python's `zipfile` does not open it. It is ZIP64 (central directory at an offset > 4 GB).
- Access tested: HTTP Range works. I parsed the central directory (345 entries) and downloaded only Genesee: **2.044 GB compressed in 671 s with 6 threads (~3 MB/s)**, CRC32 verified on the 45 files.
- Format: one TIFF per band (`blue`, `green`, `red`, `red edge`, `nir`), uint16, 2 bands (DN + alpha 0/255), EPSG:32611, LZW, `pix4dmapper`. **Exception:** `Genesee_Pea-Chickpea_Aug6_..._green.tif` has only 1 band (no alpha). Use `DN>0` as a fallback mask.
- Resolution: 1.62 to 1.79 cm/px (Genesee), ~5,000 x 5,000 px per band, ~40 to 54 MB per file.

| Site-year | Folder | Dates (flight) | Compressed size | Approx. extent |
|---|---|---|---|---|
| Genesee 2018 | `Images2018/Genesee_1801_1881/` | Jun8, Jun26, Jul9, Jul23, Aug6 | 1.03 GB | 83 x 92 m, centre ~503,850 E, 5,163,172 N |
| Genesee 2019 | `Images2019/Genesee_1901_1901B_1981/` | June05, June18, July05, July16 | 1.01 GB | 89 x 88 m, centre ~502,975 E, 5,161,945 N |

Name gotchas [V]: folder `GeneseeJ_Pea_Chickpea_June18`; file `Genesee_Adv_ Pea-Chickpea_Jun05_..._blue.tif` with a space; folder `July05` but file `Genesee_Pea_Jul05`; `red edge` with a space. The two fields are ~1.3 km apart (crop rotation), they are not the same lot.

### 4.2 Yield spreadsheets (Zenodo 10456829, v2) [V]

- URL: https://zenodo.org/records/10456829 ; files `2018PulseDataset.xlsx`, `2019PulseDataset.xlsx` (`/api/records/10456829/files/<f>/content`). CC BY 4.0. Use v2 (v1 says `grams/hectare`, a labelling error).
- `Description` sheet: trial, site, GPS, type, n varieties, replicates, n plots, sowing, **rotation (azimuth in degrees)**, flight dates.

| Sheet | n | Entries | Columns | Mean kg/ha (sd) | Missing | H² of means | Block means |
|---|---|---|---|---|---|---|---|
| 1801 Genesee (2018, green pea) | 96 | 32 | plot, block, entry, entry name, seedyield, plotseedwt | 3,600 (460) | plotseedwt 2 | **0.12** | 3,278 / 3,588 / 3,933 |
| 1881 Genesee (2018, kabuli chickpea) | 63 | 21 | plot, block, entry, entry name, seedyield | 3,035 (599) | 0 | 0.59 | 3,005 / 2,998 / 3,101 |
| 1901 Genesee (2019, green pea) | 87 | 29 | record, block, entry, plot, entry name, seedyield, datesown, plotseedwt | 3,118 (427) | 0 | 0.65 | 2,917 / 3,310 / 3,129 |
| 1901B Genesee (2019, NZ pea) | 48 | 16 | record, **bloc**, entry, plot, entry name, seedyield, plotseedwt | 3,283 (394) | 0 | 0.68 | 3,101 / 3,523 / 3,226 |
| 1981 Genesee (2019, kabuli chickpea) | 72 | 24 | record, block, entry, plot, **checks**, entry name, seedyield, datesown, plotseedwt, hundseedwt | 2,484 (394) | 0 | 0.68 | 2,275 / 2,570 / 2,608 |

- Total Genesee: 159 plots (2018) + 207 (2019) = **366 plots**. [V]
- `seedyield` = `plotseedwt` / 0.9672 exactly in all sheets: effective harvested area **9.67 m²** and yield quantised in steps of ~10 kg/ha (weighings rounded to 10 g). [V]
- `plot` runs 1..N with no duplicates; consecutive blocks (1801: 1-32, 33-64, 65-96). [V]
- H² = genetic variance / (genetic variance + residual/3), one-way ANOVA without block; it is descriptive. [V]
- The 2018 `Description` labels 1881 Genesee as "Advanced Green Pea": it is chickpea (code 88x, names CA/SR/NAH). [V]
- Common entries across years: pea 18 (Spearman of means 0.41), chickpea 15 (0.20). [V]

### 4.3 Plot map `PulsePlotMaps_2017-2019.pdf` [V]

- `https://zenodo.org/api/records/8280431/files/PulsePlotMaps_2017-2019.pdf/content`, 13 pages. Read with `pdftotext -layout`.
- Genesee 2018: 9 columns x 18 rows; rows 1-11 = 1801 (order by column: col 1 = 1-11, col 2 = 12-22, col 3 = 23-32 + "c"), rows 12-18 = 1881 (7 per column). "c" in row 11, columns 3, 6, 9 (filler with no data). Border at top and bottom.
- Genesee 2019: 9 columns x 24 rows; rows 1-10 = 1901, 11-16 = 1901B (with "c"), 17-24 = 1981. Border "a" at top and "b" at bottom.

**Grid QA done by me (without QGIS):**

| Check | 2018 (Jul9) | 2019 (Jul05) |
|---|---|---|
| Fitted angle (from east) | 50.2° (azimuth 39.8°, Description 39°) | 74.6° (azimuth 15.4°, Description 16°) |
| Strips detected | 9, canopy width 4.8-5.3 m, period 6.1-6.45 m | 9 (plus one spurious at the edge), period 5.85-6.35 m |
| Plots per strip | period 2.0 m; 20 positions = 18 rows + 2 borders | period 2.0 m; 24 rows + borders |
| Cells | 180 (9 x 20) = 162 from the plan + 18 border | 216 (9 x 24) = 90 + 54 + 72 from the plan |
| Visual overlay | Fits well on Jul9 | Fits well on Jul05 |
| Row orientation | Chickpea (7 green rows on Aug6) at the SW end, positions 2-8; position 1 = border | Chickpea (lower canopy) at the south end |
| Column orientation | **Unresolved** | **Unresolved** |

Gotcha that happened to me: with 18 positions instead of 20, the automatic selector picked different runs in different strips and mixed plots (strips 4 and 5 changed values). **Always count the borders and verify with the overlay.**

Geometry: Umani et al. 2024 say plots are 6.1 x 1.5 m trimmed to 4.9 m with 1.2 m alleys [F]; this matches what I measured (canopy strip ~5 m, period 6.1 m, plot 1.5 m + ~0.5 m gap = 2.0 m) [V].

**Co-registration between dates (2018, reference Jul9)** [V]:

| Date | 1D profile correlation: Δ along strip / across | Phase correlation (NIR gradient) |
|---|---|---|
| Jun8 | -0.30 m / -0.20 m | 0.15 / 0.25 m |
| Jun26 | +0.20 m / 0.00 m | 0.10 / 0.09 m |
| Jul23 | -0.40 m / -0.20 m | 0.46 / 0.19 m (blue: 0.55 m) |
| Aug6 | 0.00 m / -0.05 m | 0.15 / 0.37 m |

In 2019, the overlay of the Jul05 grid on Jun18 looks shifted by about half a metre along the strip. With gaps of ~0.5 m between plots, a 0.4 m shift pulls in pixels from the neighbouring plot. Solution: base grid per site-year + offset per date (profile correlation, seconds) + a negative buffer of 0.4 m.

On Jun8 2018 the alleys between strips are not yet trimmed, so automatic strip detection fails on that date; the shifted peak-date grid has to be used there. [V]

### 4.4 Radiometry (descriptive) [V]

Median soil DN (pixels with raw NDVI below the 15th percentile) per date:

| Date | Blue | Green | Red | RE | NIR | Soil NDVI | Veg NDVI (p90+) | CV of soil NIR across quadrants |
|---|---|---|---|---|---|---|---|---|
| G18 Jun8 | 36,518 | 35,216 | 38,684 | 34,518 | 25,652 | -0.19 | 0.37 | 0.07 |
| G18 Jun26 | 38,820 | 38,157 | 42,267 | 34,362 | 23,967 | -0.27 | 0.51 | 0.07 |
| G18 Jul9 | 36,372 | 35,475 | 39,214 | 34,696 | 21,807 | -0.28 | 0.51 | 0.03 |
| G18 Jul23 | 38,790 | 33,404 | 37,503 | 33,775 | 23,456 | -0.23 | 0.52 | 0.05 |
| G18 Aug6 | 36,707 | 34,196 | 33,389 | 26,308 | 23,458 | -0.17 | 0.46 | 0.12 |
| G19 Jun05 | 31,692 | 29,350 | 35,951 | 36,998 | 31,845 | -0.06 | 0.27 | 0.05 |
| G19 Jun18 | 33,375 | 32,176 | 37,415 | 37,384 | 28,748 | -0.12 | 0.48 | 0.03 |
| G19 Jul05 | 34,508 | 32,980 | 37,267 | 34,197 | 23,611 | -0.22 | 0.53 | 0.05 |
| G19 Jul16 | 38,092 | 35,920 | 40,216 | 35,931 | 26,367 | -0.20 | 0.52 | 0.06 |

Reading: soil DN is similar across dates (each band seems stretched separately), soil has red > NIR (in real reflectance it is the other way round), and soil NDVI moves 0.23 between dates, of the same order as the differences between plots. **Absolute values are not usable across dates or across years.** There is visible vignetting (bright patches at the edges of the mosaic) and gradients within a date (CV of 3 to 12% of soil across quadrants). Source conflict: Zhang et al. 2021 say they used a reflectance panel with the Pix4D "Alternative" method [F], but the Data in Brief describes the published mosaics as "uncalibrated" [F] and the DN values confirm it [V].

### 4.5 Auxiliary (not core)

- Prior art: Zhang et al. 2021 (Front. Plant Sci. 12:640259) [F]. Useful for the jury baseline.
- French data for context (not for training): Terres Univia, chiffres clés 2024 [F]; CTPS 2025 [F]; myVar chickpea network 2024 [F].
- There is no open French dataset of drone + yield for pulses (prior research [F], not searched again).

### 4.6 Quick download on Friday

Option A (fast, tested in this session, 11 min): a script of ~50 lines that (1) downloads the last 200 kB of the ZIP, (2) parses the ZIP64 record and the central directory, (3) for each entry matching `Genesee`, requests the local header (30 B) and then `bytes=start-(start+cs-1)`, (4) decompresses with `inflate64.Inflater().inflate(data)` and checks CRC32. Parallelise with 6 threads. It has to be **written again at the event** (or declared as a prior generic utility; it is a download tool, not the solution).

```bash
uv run --with inflate64 python -I fetch_zip_subset.py Genesee   # ~2 GB, ~11 min at 3 MB/s
curl -L -o 2018.xlsx https://zenodo.org/api/records/10456829/files/2018PulseDataset.xlsx/content
curl -L -o 2019.xlsx https://zenodo.org/api/records/10456829/files/2019PulseDataset.xlsx/content
curl -L -o maps.pdf  https://zenodo.org/api/records/8280431/files/PulsePlotMaps_2017-2019.pdf/content
```

Option B (if option A fails): on an AWS EC2 instance, `curl -L -o Images.zip .../Images.zip/content` (10.8 GB) and `7zz x Images.zip 'Images2018/Genesee*' 'Images2019/Genesee*'` [NV: speed from AWS and Deflate64 support in 7zz not tested].

---

## 5. AI method

**Target:** `seedyield` (kg/ha) per plot; derived and more useful for the user: **mean per entry** and **ranking within the trial**.

**Decision dates** (days after sowing, DAS):

| Use | 2018 (sown 8/5) | 2019 (sown 3/5) |
|---|---|---|
| Early | Jun8 (31 DAS) | Jun05 (33 DAS) |
| Pre-flowering / flowering | Jun26 (49) | Jun18 (46) |
| Peak | Jul9 (62) | Jul05 (63) |
| Filling | Jul23 (76) | Jul16 (74) |
| Senescence | Aug6 (90) | no flight |

"Decision in July" scenario: use only flights up to ~63 DAS. Aug6 has no pair in 2019: do not use it in the model that is transferred.

**Features per plot and date (all relative per date and trial):** canopy fraction (adaptive threshold per date), mean and percentiles of NDVI, GNDVI, NDRE, and band/soil ratios (plot DN divided by the median of nearby alleys, which corrects lighting gradients), simple texture (NDVI standard deviation), and slope between dates (growth). Spatial covariates: row, column, block.

**Leakage to avoid:**
1. Pooling sites or years with a random split (the model learns the site; this is how the 0.89 in the paper comes about).
2. Random split of plots with replicates of the same entry in train and test (split by entry or by year).
3. Thresholds or normalisations computed with test data (compute per date within each set, without looking at yield).
4. Selecting the "best" date by looking at the test set.
5. Using Aug6 or dates after the decision.
6. Pixels from neighbouring plots due to poor co-registration (0.4 m buffer).

**Baselines:** (b0) trial mean; (b1) block mean (captures the spatial gradient); (b2) mean of the entry in the other year (only for common entries); (b3) a single raw index (mean NDVI at peak) with linear regression. The AI has to beat b1 and b3.

**Model family justified by n:** 366 plots in total, 48 to 96 per trial, 16 to 32 entries. No CNN trained from scratch. Regularised regression (ridge/LASSO) or a small gradient boosting model with few features; optionally, features from a frozen pretrained backbone on per-plot crops, reduced with PCA. Mixed model (entry + block/row-column) for the experimental design part.

**Uncertainty:** split conformal per trial (prediction intervals with a target coverage of 80%), and for the ranking, probability of being in the top-k via bootstrap over replicates.

**Validation:** (V1) train 2018 → test 2019 per crop (pea 1801→1901, chickpea 1881→1981), (V2) the reverse, (V3) leave-one-block-out within a trial to see how much the image adds within one environment, and (V4) curve by cumulative date. Always report the ceiling: H² of the test trial.

**Metrics:** MAE kg/ha, R² within trial, Spearman of entry means, overlap of the top 30%, "good lines discarded" (false negatives of the top 30%), empirical coverage of the intervals.

**What the AI adds (the jury test):** without it you have to wait for harvest or look at photos by eye. With it: (1) computer vision to turn 2 GB of mosaics into a plot x date table, robust to shifts and without calibration, (2) a July ranking forecast with an interval, and (3) an alert "this trial does not allow a decision" (when uncertainty or spatial heterogeneity is high). Without the AI there is no product. Risk: if V1 does not beat b1, the honest thing is to show the negative result and the alert.

**Explainability:** trial map with the predicted plot and its interval, feature importance per date, and for each line, the canopy curve versus reference lines (registered varieties such as Aragorn, Banner, Sierra).

---

## 6. MVP and demo

**Screens (Streamlit):**
1. **Trial:** map of the mosaic (eligible date) with the plot grid coloured by predicted yield; clicking a plot shows the crop, the time curve and the interval.
2. **Flight date slider:** moving from June to July changes the ranking, the width of the intervals and the "discardable with 80% confidence" list.
3. **Decision:** table of lines with P(top 30%), recommendation (advance / discard / doubtful) and, as validation, the harvested actual yield (2019, marked as measured).
4. **Trial quality:** H², detected spatial gradient, low-confidence alert.

**Live demo script (75 s within the 4 min):**
1. "This is the chickpea trial of Genesee 2019, 72 plots, the model never saw this year." (map)
2. Slider at 5 June: wide intervals, "still cannot decide".
3. Slider at 5 July: the ranking stabilises; show the 5 discardable lines and their probability.
4. Turn on "show harvest": compare with what happened (hits and misses, nothing hidden).
5. Quality screen: "in this other trial (1801, 2018) the heterogeneity is such that not even the harvest allows ranking: the system flags it".

**Stack:** Python, rasterio, geopandas/shapely, numpy, scikit-learn, statsmodels (mixed model), MAPIE or conformal by hand, Streamlit + folium/pydeck or matplotlib. Precompute everything to parquet + PNG quicklooks so the demo does not read the TIFF files live.

**Where AWS fits:** EC2 to download and process the 2 GB (or the whole ZIP), S3 to store mosaics, features and quicklooks (and backup before the accounts are closed), optionally SageMaker for a pretrained backbone. Bedrock only if a natural-language explanation of the trial report is added; it is not the core.

**Repo structure:**
```
i5-trials/
  README.md            # data, licences, declared prior resources
  data/README.md       # how to download (do not upload data)
  src/download.py      # ZIP subset via range requests + inflate64
  src/grid.py          # rotated grid, border rows, per-date offsets, overlay QA
  src/features.py      # per-plot and per-date features, soil normalisation
  src/model.py         # baselines, model, conformal
  src/evaluate.py      # V1-V4, metrics, figures
  app/streamlit_app.py
  outputs/             # parquet, png, geojson
```

---

## 7. Work plan (Fri 20:45 to Sun 9:30)

Roles: **A** data/evaluation, **B** modelling/imagery (the one with the ML/CV master's), **C** product/business/pitch.

| Block | A | B | C | Checkpoint |
|---|---|---|---|---|
| Fri 20:45-21:30 | Start Genesee download (EC2 or laptop), download xlsx/PDF | Repo setup, environment, read TIFF | Declare track, draft prior resources doc | Download in progress |
| Fri 21:30-23:00 | Clean yield tables + map flat plan → (row, col, plot) for 5 trials | 2018 grid on Jul9 (angle, strips, 20 positions), overlay | Deck skeleton, questions for mentors (see 11) | **Go/no-go 23:00:** 2018 grid with correct overlay. If not, tomorrow we switch to another idea |
| Sat 9:30-10:15 | Workshop | Workshop | Workshop | |
| Sat 10:15-13:00 | Resolve column orientation, join cells ↔ plot; 2018 per-date offsets | 2019 grid + per-date offsets; QA overlays | Interviews with mentors about user and price; Streamlit screen 1 with PNG | **13:00:** plot x date x features table for 2018 and 2019 |
| Sat 14:00-16:00 | Baselines b0-b3, V1-V4 protocol fixed before looking at test | Relative features, soil normalisation, V1 model | Screens 2 and 3 with real data | **16:00 go/no-go:** V1 run. If the model does not beat b1, change the story to "reliability alert + H² ceiling" |
| Sat 16:00-18:00 | Conformal, top-k, curve by date | Importances, per-plot crops for the demo | Business, impact, deck v1 | Backup on S3 |
| Sat night (off-site) | Final figures, results table with measured/assumed labels | Freeze model and export parquet | Pitch, timed rehearsal | GitHub repo, stable local demo |
| Sun 8:30-9:30 | Check numbers on slides | Demo on the pitch machine | Deck PDF in template, online profile | **Submission 9:30** |

**Fallback:** if the 2019 grid gets stuck, stay with one site-year (2018) and validate with leave-one-block-out; if everything gets stuck, present only chickpea (2 trials, 135 plots).

**Cut list (in order):** pretrained backbone → spatial mixed model → pea 1901B → full curve by date → V2 → screen 4.

---

## 8. Business

**Value proposition:** "Decide in July which pea and chickpea lines to advance, with a confidence interval and an alert when the trial does not support a decision, from 2 or 3 drone flights you already do."

**Who pays:** breeding programmes (PeaBoost/Pea4Ever: Limagrain, Florimond Desprez, RAGT [F]; chickpea breeders listed in the myVar network: ID Grain, Lidea, Arterris, Top Semence [F]) and the evaluation network (Terres Inovia, GEVES). Realistic alternative: a pulses module inside an existing platform (Hiphen Cloverfield).

**Reference prices:** there is no public price per plot. Hiphen only offers "Request a Demo" [F]. The only data point: savings of £4.11 per plot versus manual measurement in wheat (Holman 2020, Rothamsted) [F]. Tardieu et al. 2019: vehicles/sensors are 5-26% of total phenotyping cost [S]. Any price in the pitch is an **[NV] assumption**: for example 2 to 5 € per plot-season.

**Market size (all estimates except where marked):**
- VATE sites 2024/25: spring pea 13, winter pea 14 + 10, chickpea 6 [F]. Chickpea post-registration network: 13 trials in 2024 [F]. Spring pea 2023: 19 varieties in 18-28 trials (prior [F]).
- Plots per year in France (VATE + post-registration + breeders, pea + chickpea): on the order of 10,000 to 50,000 [NV assumption]. At 3 €/plot: 30 to 150 k€/year [NV]. **It is a small market**: the business only closes as a module of a platform or extended to all pulses and to Europe.
- Public funding: FranceAgriMer call "Obtention variétale d'espèces légumineuses" (variety breeding of pulse species), 10 M€, priority to high-throughput phenotyping, digital and AI [F]; **closed on 27/08/2026** [F]. It serves as a signal of political priority, not as an immediate channel.

**Adoption:** (1) free pilot with Terres Inovia on the chickpea network (the CTPS lists "envirotypage (pois, pois chiche)" (envirotyping, pea and chickpea) and "intégration d'outils pour améliorer l'efficacité de l'évaluation" as prospects [F]); (2) licence to PeaBoost; (3) integration into Cloverfield (Hiphen).

**Competitors:** Hiphen (Avignon; PhenoScale for drones, Cloverfield, bought Aurea's drone phenotyping in January 2025 and SlantRange in 2023; lists "Soy/Pulses" [F]); Arvalis PhénoField [S]; INRAE PHENOME (drones and Phenomobile) [S]; GEVES testing drones for height in maize, sunflower and alfalfa [F]. **Possible differentiation:** focus on pulses, validation across years, calibrated uncertainty and trial quality diagnostics. It is a fine-grained differentiator against Hiphen.

---

## 9. Impact and sustainability

- Protein pea (protéagineux) 2024: 123,500 ha, 27.9 q/ha, 345,000 t (Terres Univia, chiffres clés 2024) [F]. Fell to ~98,000 ha in 2025 [S].
- Chickpea: 27,500 ha declared under the CAP in 2024, 9,581 ha organic in 2023; exports 17,499 t and imports 12,829 t in 2023/24 [F]. Average yield in 2024 barely above 20 q/ha [F]. Chickpea is 100% human food.
- Pea + faba bean, domestic use 2024/25: 146 kt human vs 62 kt animal (FranceAgriMer, prior [V], not reopened today).
- Impact mechanism: genetic gain per year = selection intensity x accuracy x variability / years per cycle. If July triage allows more lines to be evaluated with the same budget or a decision to be brought forward by a year, genetic gain rises [NV, not quantified with these data].
- **Illustrative estimate [NV]:** +0.5% yield per extra year of genetic gain over 100,000 ha of pea at 30 q/ha = 1,500 t/year more protein crop. It is small and slow: the real impact is in stability (more robust varieties against drought and Aphanomyces) and in attracting farmers to sow more.
- Sustainability: fewer plots harvested by hand (plot combine hours) [NV]; drones are already available in the networks.
- Honesty: the whole demo is on US trials (Palouse, WA/ID). Zero French validation.

---

## 10. Pitch

**4-minute script:**

| Time | Content |
|---|---|
| 0:00-0:40 | Problem: French pea fell from 150,000 to ~100,000 ha; Pea4Ever says genetic progress is not enough; the breeder decides which lines to advance without data until harvest. User: trials engineer at PeaBoost or at the Terres Inovia chickpea network. |
| 0:40-1:20 | Solution: from drone mosaics to a ranking of lines with an interval and a trial quality alert. Data: 366 real plots (WSU/USDA, measured), 9 flights. |
| 1:20-2:35 | Live demo (script in section 6). |
| 2:35-3:20 | Rigour: train 2018 → test 2019, sites not mixed; H² ceiling; comparison with the block baseline; what it cannot do (no calibration, one site only, US). |
| 3:20-4:00 | Scaling: pilot with the Terres Inovia chickpea network, module for PeaBoost or Hiphen, extension to faba bean and lentil. |

**Slides:** 1 title; 2 problem + user; 3 data and pipeline (mosaic → grid → features); 4 demo (backup screenshot); 5 results with measured/assumed labels; 6 limits; 7 business; 8 impact; 9 team + declared resources + repo link.

**Likely questions:**
- *Why US data?* There is no open French dataset of drone + yield for pulses; we show the methodology and what a French pilot would need (mosaics + plan + one year of yield from a network).
- *Zhang et al. already got R² 0.9.* That number pools sites with a random split; within Genesee it is 0.33-0.51 and nobody validated across years [F]. We do.
- *And radiometric calibration?* It is not in the dataset; we use relative features per date and a soil reference; we show that raw soil NDVI varies by 0.23 between dates.
- *What does the AI do that an NDVI does not?* Robust plot registration, multi-date combination, calibrated uncertainty and detection of unreliable trials; we compare against the baseline of a single NDVI.
- *Who pays and how much?* No public price; assumption of 2-5 €/plot; small market, hence the route is a module or a public service.
- *Does this help the farmer?* Indirectly, through varieties. We say so.
- *Doesn't Hiphen do this?* In general, yes; our focus is pulses, transfer across years and uncertainty.

---

## 11. Risks, mentors, prior resources, checklist

**Risks and mitigations:**

| Risk | Prob. | Mitigation |
|---|---|---|
| Grid mis-mapped (borders, column orientation) | Medium | Count 20/26 positions; resolve columns with the Data in Brief figure or the block gradient; overlay mandatory |
| Shift between dates | High (measured) | Per-date offset + 0.4 m buffer |
| Radiometry | High (measured) | Relative features, soil normalisation |
| Low ceiling (H² 0.12 in 1801 G18) | High (measured) | Report it as a finding; metrics on trials with H² ≥ 0.5 |
| The model does not beat the block baseline | Medium | "Reliability alert" storyline |
| Jury: "not France, not a farmer" | High | Say it first; chickpea focus; concrete pilot with Terres Inovia |
| Slow download on the event network | Low | EC2 + S3; 11 min measured from France |

**Questions for mentors:**
1. Is a project with US trial data considered in scope for track 3 if the user is the French evaluation network?
2. Is there a mentor from Terres Inovia, GEVES or a breeder who can say how many pea/chickpea plots they evaluate per year and whether they already fly drones?
3. Does the jury value an honest negative result (does not transfer across years) more than a demo with a good number?
4. Can we declare a generic partial ZIP download script as a prior resource?

**Prior resources to declare:** desk research (this dossier and `idea5_drone.md`), data exploration on 29-30/10 (partial download, metadata, descriptive statistics, grid QA and co-registration), knowledge that the ZIP is Deflate64 and of the offsets between dates. The exploration scripts stay out of the event repo.

**Deliverables checklist:**
- [ ] Track declared before 23:00 on Friday
- [ ] Public repo with README (data, CC BY 4.0 licences, citation of Umani et al. 2024 and Zhang et al. 2021, prior resources)
- [ ] Streamlit demo running locally and with backup screenshots
- [ ] Deck PDF in the official template with link to repo/demo
- [ ] Online project profile
- [ ] Every number labelled: measured / source / assumption / synthetic
- [ ] Backup of S3 and repo before 12:00 on Sunday

---

## 12. Rubric

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Impact and sustainability | 30% | 4 | Indirect user (breeder, not farmer), US data, slow impact not quantifiable with the data; chickpea helps |
| Scientific and technical rigour | 20% | 7 | Cross-year validation, H² ceiling, baselines and conformal are defensible; uncalibrated radiometry and small n limit it |
| AI appropriate/essential | 20% | 7 | Vision + prediction + uncertainty are the core; without AI there is no product |
| Economic viability | 20% | 4 | Small market, no public prices, Hiphen established |
| Execution and pitch | 10% | 6 | Visual and powerful demo, but the engineering risk is real (grid, offsets) |
| **Weighted total** | | **5.4** | 0.3x4 + 0.2x7 + 0.2x7 + 0.2x4 + 0.1x6 = 5.4 |

---

## 13. Sources (opened in this session)

- Zenodo API, record 8280431 (files, sizes, licence): https://zenodo.org/api/records/8280431 [V]
- Zenodo record 10456829, xlsx v2: https://zenodo.org/records/10456829 [V]
- `Images.zip` (range requests, central directory, 45 Genesee TIFF): https://zenodo.org/api/records/8280431/files/Images.zip/content [V]
- `PulsePlotMaps_2017-2019.pdf`: https://zenodo.org/api/records/8280431/files/PulsePlotMaps_2017-2019.pdf/content [V]
- Zhang et al. 2021, Front. Plant Sci. 12:640259: https://www.frontiersin.org/articles/10.3389/fpls.2021.640259/full [F]
- Umani et al. 2024, Data in Brief 53:110013: https://pmc.ncbi.nlm.nih.gov/articles/PMC10907176/ [F]
- Participant guide: `event/participant_guide.txt` [V]
- Opened by the research subagent in this session [F]:
  - GEVES at UPOV TC/61 (drones for height in DUS): https://www.upov.int/edocs/mdocs/upov/en/tc_61/tc_61_newtech_ppt_3.pdf
  - CTPS section on protein pulses, INRAE seminar 7/10/2025: https://groupes-filieres.hub.inrae.fr/Media/Files/gf-legumineuse/4_pilet-nayel-ml_ctps_leggraines
  - Pea4Ever / PeaBoost: https://www.pleinchamp.com/actualite/pois-proteagineux-pea4ever-or-never
  - Chickpea post-registration network 2024 (myVar): https://www.myvar.fr/uploads/media/document/0001/02/e7a2696c88f183a6ea9787e7d91a6648500babd6.pdf
  - Hiphen and UMT CAPTE: https://www.inrae.fr/en/news/3-questions-start-hiphen
  - Hiphen, site: https://www.hiphen-plant.com/
  - Hiphen buys Aurea's drone phenotyping: https://www.fertilizerdaily.com/20250114-hiphen-acquires-aureas-drone-unit-to-boost-agri-tech-edge
  - Holman 2020, Rothamsted: https://repository.rothamsted.ac.uk/item/97q41
  - Terres Univia, chiffres clés 2024: https://www.terresunivia.fr/fichiers/publications/chiffres-cles-2024.pdf
  - FranceAgriMer pulses call: https://www.franceagrimer.fr/aides/appel-projets-obtention-varietale-despeces-legumineuses ; https://www.franceagrimer.fr/sites/default/files/2026-07/06072026_CP_FranceAgriMer_AAP_Obtention_vari%C3%A9tale_l%C3%A9gumineuses_2026.pdf ; https://agriculture.gouv.fr/ouverture-dun-appel-a-projets-en-faveur-de-linnovation-varietale-des-legumineuses ; https://demarche.numerique.gouv.fr/commencer/appel-a-projets-obtention-varietale-d-especes-legu
- Single snippet [S]: Pea4Ever slides Terres Inovia (multi-stage drones, 101 lines): https://www.terresinovia.fr/sites/default/files/2026-01/3_rtti_bruz_22012026_pea4ever_am.pdf (403); PHENOME-EMPHASIS: https://infrastructures-recherche.inrae.fr/en/search-engine/irs/phenome-emphasis-phenome-inrae ; Tardieu et al. 2019: https://ueaeprints.uea.ac.uk/68074
