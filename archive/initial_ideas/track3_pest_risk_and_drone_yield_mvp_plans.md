# Two realistic Track 3 MVPs

## Pest-damage risk and drone-based yield estimation

*Hack the Fork Paris 2026 | Decision brief | 29 October 2026*

**Scope:** Idea 1 and Idea 5 from the latest five-option list. The aim is to choose a useful project for three people working for approximately 20 elapsed hours, including validation and presentation.

**Idea 1, in plain language:** Use information about a French lentil or faba-bean field to estimate its risk of insect-damaged grain. A cooperative uses the ranking to decide which fields or incoming harvests deserve inspection first. The prototype predicts damage; it does not prescribe pesticides or certify food quality.

**Idea 5, in plain language:** Use drone images taken before harvest to estimate the yield of pea or chickpea trial plots. Show which plots appear likely to produce less, and how predictions change when another image date becomes available. The initial demonstration is on US research trials, not French commercial farms.

| Question | Idea 1: pest damage | Idea 5: yield from imagery |
|---|---|---|
| Real measured outcome? | Yes: damaged and undamaged grain counts | Yes: harvested seed yield |
| Main input | Small field, weather and landscape tables | Multispectral images plus trial/plot metadata |
| Main AI task | Small-data regression or risk ranking | Image-feature extraction plus regression |
| Main uncertainty | Whether the available predictors generalize | Whether images can be calibrated and joined to plots in time |
| 20-hour judgment | More feasible; useful signal still unproven | Conditional and substantially riskier |

**What was actually checked:** all eight pest tables and the README were downloaded; three yield spreadsheets were opened; the image ZIP directory and the plot-map PDF were inspected. No predictive model was trained. Full TIFF pixels, radiometric calibration and image-to-plot joins were not validated.

**Recommendation:** investigate Idea 1 first. Choose Idea 5 only if a small image/label subset can be made usable within the first three hours. Neither is automatically a winning project because it has an open dataset. The contribution needs a useful decision and honest held-out evaluation.

---

## Data audit and project scope | 29 October 2026

### Idea 1: the data we would actually use

One core dataset, no external weather join needed.

French bruchid field dataset, version 2.0: https://doi.org/10.57745/HPEMYW. Collected across 2020-2022 harvest years in four French production regions. The catalogue covers 60 lentil and 45 faba-bean fields. Data are available under Etalab Open Licence 2.0. [P1]

| File / role | Contents and direct inspection findings |
|---|---|
| Yield_and_seed_damage.tab (target) | 481 rows at field/distance level. Damaged and undamaged grain counts, yield and grain weight. A valid target requires both counts present and their sum greater than zero. 397 rows across 100 fields pass this check: 57 lentil and 43 faba bean. [P2] |
| Meteorological_data.tab (predictors) | 420 rows, 105 fields, four stage labels: Vegetative, Flowering, Young pod, Mature pod. Temperature-day counts, cumulative/mean/maximum rainfall and maximum wind. These are stage summaries, not raw daily sequences. [P3] |
| Landscape.tab (predictors) | 315 rows: three buffer sizes per field (500, 1,000, 2,000 m). Crop, grassland, woodland, organic-area and hedgerow measures. [P4] |
| Agricultural_practice_characterization.tab (predictors) | 105 field records: crop/variety, practices, sowing information, field area and other farm descriptors. Its field identifier is called Parcelle, whereas other tables use Field. [P5] |
| Bruchids.tab (optional extra inputs) | 3,870 rows, 86 fields, three crop stages, distance, sex and insect counts. 85 fields overlap with usable damage labels. These are field observations, not camera counts. [P6] |
| Other downloaded tables | Flower cover, extrafloral nectar and parasitism. Keep out of the first model: more collection burden, missingness or timing concerns. [P1] |

**Target:** observed damaged-grain percentage = 100 x damaged / (damaged + undamaged). For a field-level prototype, pool the available sampled grain counts within each field and document this sampling-weighted definition.

**Effective sample size:** at most 100 damage-labelled fields before further cleaning; not 3,870 independent farms. Multiple rows from one field must stay in the same validation group.

**Metadata issues to audit:** sowing dates include spreadsheet-style numeric values; some variable names and units need checking. Post-harvest yield and parasitism must not become inputs to an earlier warning. Exact parcel coordinates were not present in the inspected tables, so a parcel-level satellite join is not ready-made.

### Idea 1: useful output, method and limitations

**Who benefits, and what changes?** The proposed user is a cooperative technician organizing limited inspection capacity for human-food pulses. The output is a ranked list of fields, an estimated damage level and the evidence available. Damage can restrict access to higher-value outlets; current Terres Inovia commentary identifies it as a practical problem. Whether predictive triage improves the operator's workflow remains a user-validation question. [P7]

**Minimum product:** An operator selects a field and the latest completed crop stage. The screen shows the damage estimate, a cautious uncertainty indication, its rank among fields and missing inputs. A comparison view shows what a fixed inspection budget would cover. Use a regional summary if helpful; do not invent precise field locations.

**Small, defensible modeling plan:** First define the decision date. Use only completed weather windows and practices known by then; exclude Mature pod inputs for an earlier warning. Pivot one landscape buffer and a small number of features into one row per field. Fit imputation and encoding inside training folds. Keep the initial feature count small.

Compare a crop-specific mean/median baseline with regularized regression and one shallow tree model. Treat the crop type explicitly and report results by crop. Add early insect counts as a separate comparison: otherwise a supposedly cheap warning may secretly require costly surveying of every field.

Evaluate by held-out harvest year where possible, keeping all observations from a field together. Report damage error in percentage points and ranking quality. If a buyer supplies an acceptance threshold, measure recall of high-damage fields at a fixed inspection budget; otherwise label the threshold as an exploratory scenario. Uncertainty estimates need coverage checks and will be unstable with so few fields.

**What could fail?** A related 2026 study found a positive but highly dispersed relationship between female pest abundance and grain damage. It also observed relatively uniform within-field distributions. Do not assume easy prediction or promise reliable edge-based hotspot detection. [P8]

Other risks include only three years of observations, changing regions and varieties, missing data, differences between surveyed plots and commercial lots, and the cost of obtaining current inputs. Historical associations do not prove an intervention reduces damage.

**20-hour scope and stopping rule:** Hours 0-3: validate the target, joins, input timing and customer decision. Hours 3-8: baselines and grouped evaluation. Hours 8-12: one improved model and optional insect-count comparison. Hours 12-16: interface and inspection-budget scenario. Hours 16-20: failure cases, results and pitch.

Continue only if the clean joins support a reproducible target and an improvement worth demonstrating. If performance fails to beat the baseline consistently, present that finding honestly and reconsider the product claim; do not hide it behind a dashboard.

### Idea 5: the data we would actually use

**The WSU / USDA pea and chickpea trial dataset.** Use the public pulse dataset with imagery from US trials in Fairfield, Pullman and Genesee during 2017-2019. It is listed under CC BY 4.0. Version 1 holds the imagery; version 2 provides updated tables. [Y1-Y2]

| Resource | Actual contents / what was checked |
|---|---|
| 2017PulseDataset.xlsx, v2 | 10 trial sheets plus Description. 630 rows with numeric seedyield values in the inspected sheets. [Y3] |
| 2018PulseDataset.xlsx, v2 | 11 trial sheets plus Description. 831 rows with numeric seedyield values. [Y4] |
| 2019PulseDataset.xlsx, v2 | 13 trial sheets plus Description. 954 rows with numeric seedyield values. [Y5] |
| Workbook columns | Trial/plot identifiers, blocks, entries/cultivars and seedyield. Additional traits vary: flowering, maturity, height and seed-weight fields. Description sheets include trial location, planting and flight dates. No ready-made NDVI or spectral-band feature columns were found in the inspected trial sheets. |
| Images.zip, version 1 | Approximately 10.8 GB. The central directory lists 275 TIFF entries: 241 nonempty and 34 zero-byte entries. Files are organized by year, site, date and spectral band. The index was inspected; full image pixels were not downloaded or checked. [Y1] |
| PulsePlotMaps_2017-2019.pdf, v1 | Downloaded and inspected. Thirteen pages of plot layouts, numbered plots and trial labels. These help establish plot identity, but they are not a verified set of georeferenced crop polygons. [Y6] |

**Important:** 2,415 spreadsheet rows are not 2,415 independent farms. These are trial plots, with repeated varieties, blocks and image dates. Numeric yield availability does not establish that every row has a usable corresponding image. Confirm target units and plot area before any tonnes calculation.

**Version trap:** the current version 2 file listing has three spreadsheets and no image ZIP. Use version 1 for imagery and plot maps, then confirm compatibility with the version 2 tables.

**Image-processing burden:** the dataset paper describes uncalibrated orthomosaics and a reflectance-panel procedure. The first data gate must verify calibration information, band order, alignment and usable pixels. Some TIFF entries are empty, so a complete five-band set cannot be assumed for every date. [Y7]

**No extra data required for the first benchmark.** Do not add satellite imagery, French weather or national parcel data until this basic image-to-yield pairing works.

### Idea 5: useful output, method and limitations

**Start with the user supported by the data.** A breeder or research agronomist is the most defensible first user: compare pea trial plots before harvest and identify candidates for closer measurement. A cooperative supply forecast is a future application, requiring validation on commercial farms. These are different deployment claims.

The interface shows an image, verified plot boundaries, estimated yield, acquisition date and a comparison to observed yield for held-out historical plots. A date selector can show how estimates change as more observations become available. Any example supply-shortfall calculation must be labelled as a scenario.

**Minimum technical approach:** Choose one crop, one site/year and one pre-harvest date. A 2018 subset is worth inspecting first because the archive directory did not list zero-byte TIFF entries for that year; this is not proof its pixels or labels are clean. Identify plot boundaries using the map and confirm plot numbering against the workbook before extracting features.

Convert bands to reflectance using a reproducible calibration procedure where possible. Extract a few simple spectral and canopy features for each plot, then use regularized regression or random forest regression. NDVI = (near-infrared - red) / (near-infrared + red) is a useful candidate only after band interpretation and calibration are checked. No deep neural network is necessary for the first benchmark.

Use a mean-yield baseline, then compare one-date versus two-date features if time permits. The original 2021 work already used image features and regression; the 2023 work examined sensor/date fusion. Novelty would need to come from the user decision, earlier useful prediction or credible uncertainty, not merely predicting yield from images. [Y8-Y9]

**Validation and claims:** For a within-trial demo, hold out blocks or spatial groups and keep all dates/crops of a plot together. State that this tests within-trial performance. A claim about new environments needs a held-out site/year; unseen-variety claims need variety-based grouping as well. Do not tune repeatedly on the final test split.

Report yield MAE/RMSE in verified units, relative error, R-squared and scatter plots. Compare dates at a clear pre-harvest cutoff. Exclude plotseedwt, other harvested-yield fields and late maturity measurements from an early forecast. More images of the same plot do not increase the independent sample count.

**20-hour scope and stopping rule:** Hours 0-3: obtain one usable band set, locate plots and match labels. Hours 3-8: validate crops/calibration and extract features. Hours 8-12: baseline and one model. Hours 12-16: visual interface and optional second date. Hours 16-20: evaluate, inspect errors and prepare the pitch.

Stop or switch by hour 3 if plot identity, image access or calibration cannot be resolved. A purely spreadsheet model can be a fallback, but must be described as such. A US breeding-trial result does not validate French farm yield, human-food quality or reduced sourcing costs.

---

## Choosing and organizing the weekend

**My recommendation after inspecting the files:** Idea 1 is easier to bring to a working prototype because its core files are small and the outcome is explicit. Its biggest risk is weak generalization from only 100 labelled fields. Idea 5 has a better visual demonstration but a substantial data-engineering gate and more established prior art. Neither has demonstrated cost savings yet.

| Criterion | Idea 1 | Idea 5 |
|---|---|---|
| Main value hypothesis | Better inspection prioritization | Earlier assessment of trial performance |
| Human-food connection | Reduce uncertainty around damage that can restrict food-market access | Support pulse breeding; commercial food sourcing needs later validation |
| Dataset preparation | Relatively light table joins | Heavy image/plot/calibration work |
| CV / time-series content | Primarily tabular ML with stage-based history | Multispectral CV; optional repeated-date features |
| Existing research overlap | Pest ecology and damage analysis already published | Yield prediction from these types of images already published |
| Credible weekend claim | Held-out damage ranking/error relative to a baseline | Held-out yield estimates for a defined trial subset |

### Three-person division of work

- **Person A, data and evaluation:** audit labels and timestamps, create independent splits, establish the baseline, own the final untouched evaluation.
- **Person B, modeling:** build the small prediction pipeline and investigate failures. For Idea 5, A and B should jointly resolve image-to-plot extraction first.
- **Person C, product and user problem:** build the interface, document assumptions, ask mentors about operational use and prepare the impact/business case.

### Must-have deliverables

One reproducible dataset subset; a documented target and decision date; a baseline; an honestly evaluated model; a reliable visual demonstration; a source/assumption sheet; and a narrow explanation of who would act differently. Include failures, missingness and the model's limitations.

### Cuts that protect the core

For Idea 1, cut satellite fusion, chemical-treatment advice, national coverage and profit guarantees. For Idea 5, cut multi-crop support, neural image fusion, satellite transfer and nationwide supply prediction. Keep one model and one useful decision.

### Questions for a mentor or potential user

What is the decision and how is it made today? What does it cost to obtain the proposed inputs? How early must the answer arrive? Which mistake is worse? What minimum improvement would make it worth using? Can a real example decision or specification be supplied?

**Preparation boundary:** this brief contains source review and dataset inspection, not a trained prototype. Follow the event's requirement to create challenge-specific code, models, results and the final deck during the hackathon.

---

## Sources and audit trail

All sources checked on 29 October 2026. Repository and file observations below are from direct inspection; model performance, calibration and commercial benefit remain untested. The related studies establish prior work within their own settings, not guaranteed MVP performance.

### Idea 1 sources

- **[P1]** French bruchid dataset, v2.0. Release 1 September 2026; Etalab 2.0. Metadata and all eight tables plus README downloaded. https://doi.org/10.57745/HPEMYW
- **[P2]** Yield_and_seed_damage.tab. Audit rule: both damaged and undamaged counts nonmissing and their sum positive. Result: 397 usable rows / 100 fields. https://entrepot.recherche.data.gouv.fr/api/access/datafile/722704
- **[P3]** Meteorological_data.tab. Four stage categories in the downloaded file, including Mature pod; do not automatically use all stages as early-warning inputs. https://entrepot.recherche.data.gouv.fr/api/access/datafile/722709
- **[P4]** Landscape.tab. Three buffers per field, 315 records. https://entrepot.recherche.data.gouv.fr/api/access/datafile/722708
- **[P5]** Agricultural_practice_characterization.tab. 105 rows; Parcelle is the field key. Some dates/units require interpretation. https://entrepot.recherche.data.gouv.fr/api/access/datafile/722703
- **[P6]** Bruchids.tab. 86 fields; 85 overlap usable damage labels. https://entrepot.recherche.data.gouv.fr/api/access/datafile/722705
- **[P7]** Dauguet and Gouyo / Terres Inovia, 2026. Public introduction identifies pest damage and access to remunerative outlets; full article is paywalled and was not reviewed. https://www.perspectives-agricoles.com/conduite-de-cultures/graines-legumineuses-bruches-stockage
- **[P8]** Chery-Lagrange et al., 2026. Colonization and spatiotemporal distribution of bruchid pests in lentil and faba bean fields. DOI: 10.1002/ps.70679. The abstract reports a dispersed count/damage relationship. Its analysis uses 104 fields; the broader dataset catalogue lists 105, so do not assume identical inclusion rules. https://pubmed.ncbi.nlm.nih.gov/41730720/

Background data paper: Herrera et al., 2026. DOI: 10.1016/j.dib.2026.112939. https://pmc.ncbi.nlm.nih.gov/articles/PMC13264089/

### Idea 5 sources

- **[Y1]** WSU / USDA pulse dataset, v1. Contains the image archive and plot-map PDF. ZIP-directory audit: 275 TIFF names, 241 nonempty, 34 zero-byte; this does not validate image pixels. https://zenodo.org/records/8280431
- **[Y2]** Pulse dataset, v2. Current listed files are three spreadsheets; downloaded for header/sheet inspection. https://zenodo.org/records/10456829
- **[Y3]** 2017 workbook. 630 numeric-yield rows across ten trial sheets. https://zenodo.org/api/records/10456829/files/2017PulseDataset.xlsx/content
- **[Y4]** 2018 workbook. 831 numeric-yield rows across eleven trial sheets. https://zenodo.org/api/records/10456829/files/2018PulseDataset.xlsx/content
- **[Y5]** 2019 workbook. 954 numeric-yield rows across thirteen trial sheets. https://zenodo.org/api/records/10456829/files/2019PulseDataset.xlsx/content
- **[Y6]** PulsePlotMaps_2017-2019.pdf. Thirteen pages; first-page layout visually inspected. Plot numbering/layout must still be registered to a selected image. https://zenodo.org/api/records/8280431/files/PulsePlotMaps_2017-2019.pdf/content
- **[Y7]** Umani et al., 2024. A pulse crop dataset of agronomic traits and multispectral images from multiple environments. DOI: 10.1016/j.dib.2023.110013. Dataset article describing acquisition, measurements and uncalibrated orthomosaics; indexed primary article text reviewed. https://pmc.ncbi.nlm.nih.gov/articles/PMC10907176/
- **[Y8]** Zhang et al., 2021. Crop Performance Evaluation of Chickpea and Dry Pea Breeding Lines Across Seasons and Locations Using Phenomics Data. Direct prior art for feature-based regression. DOI: 10.3389/fpls.2021.640259. https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2021.640259/full
- **[Y9]** Marzougui et al., 2023. Remote sensing for field pea yield estimation: A study of multi-scale data fusion approaches in phenomics. DOI: 10.3389/fpls.2023.1111575. Includes a separate 2020 trial; do not assume all its imagery is in the 2017-2019 archive. https://pmc.ncbi.nlm.nih.gov/articles/PMC10161932/

### Reproducibility of this inspection

Counts describe files retrieved on the review date, before model-specific cleaning. Pest counts are distinct Field identifiers satisfying the stated rule. Yield row counts are numeric seedyield entries across trial sheets, not independent environments. File access succeeded, but no claim is made that the full image pipeline has been reproduced. No predictive results or actual savings were generated.
