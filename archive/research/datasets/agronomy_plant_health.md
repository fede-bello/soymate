# Agronomy and plant health datasets for pulses (Track 3)

Audit done on 29/10/2026. Conventions: **[V]** I verified it myself (downloaded the file or queried the API and counted), **[F]** I read it at the source (metadata, README, official page), **[NV]** not verified. Relevance 1-10 for Track 3 (pulses for human food in France, producer income).

I am not repeating what has already been audited: INRAE bruchid (doi 10.57745/HPEMYW, see `../idea3_bruchids.md`), WSU/USDA drone (`../idea5_drone.md`), Agreste SAA and SAFRAN/Open-Meteo (`../ideas2_4_time_series.md`). I only reference them when they are combined.

Hackathon rule respected: download only, counts and distributions. No model fitted. Downloaded data was deleted at the end (see last section).

---

## 0. Summary table

| # | Dataset | Owner | Coverage | Granularity | License | Access | Rel. | Main limitation |
|---|---|---|---|---|---|---|---|---|
| 1 | **Pea_dataset** (doi 10.57745/FW78RE) | INRAE + Terres Inovia/GEVES | France, 158 sites, harvests 2002-2024 (95% in 2013-2024) | site × genotype × year (4,450 situations) + daily climate per site | Etalab 2.0 | direct download, 10 MB | **9** | anonymized genotypes (`Genotype_74`); pea only; no diseases/pests |
| 2 | **RPG parcel register 2015-2024 via IGN WFS** | IGN / ASP | All of France, annual | parcel (polygon) with fine crop code (LEC, PCH, FVL, PPR, PHI, SOJ, LDH/LDP...) | Licence Ouverte | WFS without login, 5,000 features per page | **8** | `id_parcel` not stable across years: rotations require crossing geometries |
| 3 | **Indicateurs sur les successions culturales 2015-2023** (crop succession indicators, doi 10.57745/WQ4MIF) | INRAE (ODR) | Metropolitan France | commune / dept / region, organic (AB) vs conventional | Etalab 2.0 | download, CSV 77 MB | 6 | "legumbre" (pulse) mixes forage crops (alfalfa, grasslands) with grain pulses |
| 4 | **37 cereal-pulse intercropping trials** (Zenodo 14160885) | INRAE/ReMIX and partners | FR (Angers, Auzeville, Grignon), DK, IT, DE, UK, 2001-2017 | plot × date × variable (long format) | CC-BY 4.0 | direct download, ~8 MB | 7 | 37 trials, almost all experimental from the 2000s; little site variability |
| 5 | **V.faba.Multi_Cla_Field_LeafFragments** (doi 10.57745/H7JVFN) | INRAE (IGEPP) | Brittany and Gironde, Feb-Jul 2024 | image (2,110 faba bean leaf photos) | no license declared in the API | download, zip 6.7 GB | 6 | 60% of images with several causes (`Zmu`); 3 localities; 1 year |
| 6 | **BSV OCR archive** (data.gouv, "Archive en agro-écologie de BSV") | PestObserver (INRA/IRSTEA) | France, 1946-2016 | document (40,829 bulletins in txt/xml) | CC-BY | download, zip 173 MB | 6 | only up to 2016; 257 pulse files; noisy OCR |
| 7 | Chickpea × service plants, ascochyta (doi 10.57745/05KBPZ) | INRAE / ESA Angers | Angers, 2023-2024 | block × treatment × date (503 rows) | Etalab 2.0 | download, 34 kB | 5 | single site, 84 yields |
| 8 | Epiphyt (via TEMPO portal) | DGAL (ministry), distributed by INRAE TEMPO | France, BSV network | plot observation (phenological stage; pests [NV]) | Etalab on TEMPO [F]; Epiphyt-Extract restricted | web portal, no public API found | 5 | could not download data automatically; pests probably not exposed |
| 9 | Catalogue of marketed oilseed and protein crop varieties (data.gouv, Terres Inovia) | Terres Inovia | France, 2023 | variety (620 rows) | CC-BY | CSV 51 kB | 5 | no yields; 2023 snapshot |
| 10 | myVar (post-registration results) | Terres Inovia | France, by region | variety × region, synthetic | [NV] | interactive web, no download | 4 | no raw data or API |
| 11 | Eurostat `apro_cpsh1` | Eurostat | EU, national, annual, provisional up to 2026 | country × crop × year | Eurostat free reuse | JSON API | 5 | national; Eurostat pea ≠ Terres Inovia figures |
| 12 | GBIF (Bruchus, Sitona, Aphanomyces...) | GBIF | global | point occurrence | varies per record | API | 2 | very few occurrences in France (Aphanomyces: 4) |
| 13 | Lentil Disease Classification (HF Project-AgML, origin Mendeley 10.17632/7vb77bz2st.2) | Mahamud et al. (Bangladesh) | Bangladesh | image 224×224 (5,349) | CC-BY 4.0 | parquet 74 MB | 3 | augmented images (`aug_*`), not France, likely train/test leakage |
| 14 | XMR hyperspectral lentils, foreign bodies (HF cubert-gmbh) | Cubert GmbH | laboratory | hyperspectral frame | Apache-2.0 | HF, proprietary `.cu3s` format | 4 | does not detect bruchid, does detect stones/insects; laboratory |
| 15 | Pea ascochyta: segmentation and sequences (doi 10.57745/5B1XGU, 10.57745/MQXKCP) | INRAE IGEPP | biotests in chamber | stipule image | Etalab 2.0 | download, 13 MB images | 3 | laboratory, 2 cultivars |
| 16 | Crop Suitability *Pisum sativum* ERA5 2006-2020 (doi 10.57745/EYAMIF) | INRAE | Europe | grid 0.25° | Etalab 2.0 | txt 0.5 MB | 4 | static index, not validated against yields |
| 17 | LCA of lentil and chickpea (doi 10.57745/HKQIYX, 10.57745/LXAQRN) | INRAE / ADEME (Agribalyse) | France, national average | system (conv. / organic) | Etalab 2.0 | CSV | 4 | national average, not per parcel |
| 18 | Rés0Pest yields 2013-2023 (doi 10.57745/FPKPPC) | INRAE | pesticide-free trial network | plot × year (360 rows) | Etalab 2.0 | CSV | 3 | ~55 rows with pulses |
| 19 | PKGC 2021 nitrogen fertilization (doi 10.57745/ZF8RK1) | INRAE (SYAGRIC) | France, NUTS0-3 | crop × region | Etalab 2.0 | CSV | 3 | useful for the "N saved" argument, not for prediction |
| 20 | PHETEC / TEMPO phenology (doi 10.15454/TC90O9, 10.15454/CLYPS4) + BBCH-Terres Inovia scales (doi 10.57745/PLM9LJ, GNV0C7, CSVTE4) | INRAE | Auzeville 1997-2008 / ontologies | stage observation | Etalab 2.0 | xlsx / RDF | 3 | old and single-site |
| 21 | DiverIMPACTS: diversification experiences (Zenodo 3966842) and barriers (Zenodo 3249967) | DiverIMPACTS H2020 | 25 European cases | survey | CC-BY / CC-BY-NC | CSV | 3 | qualitative |
| 22 | Agrosyst / DEPHY | INRAE / Ecophyto | >2,000 farms | intervention | restricted | on request (Datagrosyst) | 3 | not accessible in 20 h |
| 23 | EVA Aphanomyces (Terres Inovia DSS) | Terres Inovia | northern half of France | plot (780 + 120 validation) | closed | web tool only | 5 as benchmark | the 780-plot base is not public |

---

## 1. Pea_dataset: 4,450 site × genotype × year combinations of pea in France

- **URL:** https://doi.org/10.57745/FW78RE (Recherche Data Gouv). Published 2026-08-05 [V].
- **Owner:** INRAE with data from "Terres Inovia GEVES and partners" (3,936 rows), Burstin et al. 2021 (425), Vocanson & Jeuffroy 2008 (54), Gaudio et al. 2024 (35) [V].
- **License:** Etalab 2.0 [V via API].
- **Files [V]:** `trials_data.tab` (1.5 MB), `crop_traits_data.tab` (4.6 MB, long format), `metadata.tab` (dictionary with units), `weather_data.zip` (158 daily CSVs, one per site).
- **Coverage [V]:** 158 sites, 117 genotypes, 302 site-years, harvests 2002-2024 but 95% between 2013 and 2024 (2015: 551, 2017: 534, 2022-2023: 496 each). 2,705 spring pea situations and 1,745 winter ones. 40 départements (by postal code): 28 Eure-et-Loir (394), 49 Maine-et-Loire (339), 18 Cher (309), 80 Somme (300), 91 Essonne (269), 17, 10, 59, 32, 31...
- **Input variables [V]:** coordinates and postal code, soil (USDA class, depth, clay/silt/sand, AWC in mm, C/N, CaCO3, total N; **0% missing**), preceding crop (41% missing; winter wheat 1,185), pea type, genotype, Hr allele (60.8% missing), grain colour (yellow 4,087, green 264), protein declared by the breeder (14% missing), flowering earliness, lodging and cold tolerance, TSW, sowing date and density, up to 3 irrigations (100 irrigated situations), `management` (87.7% missing, heterogeneous codes).
- **Targets [V]:** `yield_14` (q/ha at 14% moisture) in 4,230 situations: mean 49.5, median 49.1, range 14-100. Winter 53.9 vs spring 46.9 q/ha. `protein_content` in 3,326 situations: mean 22.9%, range 16.1-31.4%. Also flowering start date (4,450, complete), `tsw_14` (3,369), height (2,762), end of flowering (2,640), and rare variables: biomass (998), LAI (172), **N fixed by symbiosis** (`N_abs_shoot_fixation`, only 53).
- **Mean yield per year [V]:** 2015: 55.1; 2019: 57.7; 2020: 45.3; **2021: 40.9**; 2022: 45.7; 2023: 45.0; 2024: 47.4. The recent drop, also described by Terres Inovia, shows up here.
- **Quality [V]:** no duplicates, 1 yield row per situation, all `situation_id` values join across tables, all `weather_file` entries exist in the zip. Climate: 186,179 daily rows 2001-2024 with Penman ETP, mean temperature, radiation, rain, Tmax, Tmin; only 1 NaN in TX/TN/RR. Heads up: radiation comes in J/cm², and the columns are in French (AN, MOIS, JOUR).
- **Joinability:** postal code → department (first 2 digits) [V]; lat/lon → SAFRAN cell; year → departmental SAA. There is no INSEE commune, but it can be derived from the postal code with the La Poste database [NV].
- **Gotchas:**
  - **Anonymized genotypes** (`Genotype_98`...), so a variety cannot be recommended by name. Its traits can be used (earliness, Hr, cold tolerance, colour, TSW). 30 genotypes have ≥50 situations.
  - Mixed networks: Terres Inovia/GEVES post-registration (variety evaluation network, protected management) plus research trials with treatments. The yield is trial potential, not farm yield.
  - No pest or disease damage (neither aphanomyces nor bruchid). Only the `management` field hints at treatments.
  - Protein measured in 75% of situations: enough for a "fit for fractionation/human food" target (industrial protein threshold [NV]).
- **Relevance: 9/10.** The best open dataset of yield and protein for a pulse in France, with daily climate and soil already joined. Very recent (August 2026), so probably few teams know it.

## 2. RPG parcel register 2015-2024 with fine crop code, via the IGN Géoplateforme WFS

- **URL:** `https://data.geopf.fr/wfs/ows`, layers `RPG.2015:parcelles_graphiques` ... `RPG.2024:parcelles_graphiques`, `RPG.LATEST`, plus `RPG.20xx:codes_cultures` [V with GetCapabilities].
- **Owner / license:** IGN / ASP, Licence Ouverte [F].
- **Fields [V]:** `id_parcel`, `surf_parc` (ha), `code_cultu` (fine CAP code), `code_group`, `culture_d1`, `culture_d2` (derived/secondary crops), `cat_cult_p`.
- **RPG 2024 counts by code (numberMatched) [V]:** lentil LEC 8,077 parcels; chickpea PCH 6,373; faba bean FVL 16,049 (+ FEV 260); spring pea PPR 17,347; winter pea PHI 7,196; soybean SOJ 35,891; lupin LDH 850 / LDP 406; protein pea-cereal mix MPC 9,365.
- **2024 area (downloading all parcels with pagination) [V]:** lentil **34,226 ha** in 87 départements; chickpea **27,491 ha** in 79 départements. Lentil matches Eurostat 2025 (33,930 ha) [V].
  - Top lentil (ha, dept by representative point): Aube 10: 3,825; Haute-Loire 43: 2,678 (AOP Puy); Marne 51: 2,553; Yonne 89: 2,490; Indre 36: 1,837; Vendée 85: 1,551.
  - Top chickpea: Gers 32: 4,277; Charente 16: 3,452; Charente-Maritime 17: 2,888; Vendée 85: 2,329; Haute-Garonne 31: 1,629.
- **Gotchas [V]:** the server cuts at 5,000 features per request (you must paginate with `startIndex` + `sortBy`). It does not carry department or commune: you have to do point-in-polygon (I did it with shapely). `surf_parc` rounded to 0.01 ha (some parcels come out as 0). `id_parcel` is anonymous and does not allow following a parcel across years [F, see ideas2_4_time_series.md]: for rotations, geometries have to be overlaid.
- **Relevance: 8/10.** Gives where each food pulse is grown, per parcel and per year since 2015. Basis for maps, for weighting climate, and for estimating pea return intervals (aphanomyces risk).

## 3. Crop succession indicators 2015-2023 (RPG processed by INRAE)

- **URL:** https://doi.org/10.57745/WQ4MIF (earlier versions 2015-2021 and 2015-2022). Etalab 2.0 [V].
- **Files [V]:** `indicateurs_successions_2015-2023.csv` (77 MB, 74,328 rows × 213 columns), xlsx dictionary (212 variables), crop code mapping table 2015-2022 → 2023 (374 rows, with botanical family and season).
- **Levels [V]:** 32,022 communes, départements (rows with `insee_com == 'DEP'`), regions, France; each one in "Ensemble" (all), conventional (0) and AB (1).
- **Useful variables:** number of crops, inverse Simpson, number of families, maize monoculture, **N_LEG** (mean number of pulses in the 9-year sequence) and areas with 0..9 pulses, return intervals.
- **Figures [V]:** France: 14.7 M ha of sequences, 34.5% of the area with at least one pulse in 9 years, mean N_LEG 0.74. Minimum Seine-Saint-Denis 93 (13%), Seine-Maritime 76 (14.5%), Finistère 29 (15.8%). Maximum Hautes-Alpes 05 (89.8%), Alpes-de-Haute-Provence 04 (79%): **inflated by alfalfa and temporary grasslands**.
- **Key gotcha [F, dictionary]:** "legumbres" includes CAP categories 1.3 protéagineux (protein crops), 1.6 legumbres (pulses), 1.7 forage legumes, soy, faba bean, dry bean, garden pea, forage lentil and legume-grass mixes. It cannot be used as is for "grain pulses for human food"; for that you have to go back to the RPG with fine codes.
- **Relevance: 6/10.** Good as territorial context and for an indicator of "room to put pulses in the rotation".

## 4. 37 European cereal-pulse intercropping trials (with their monocultures)

- **URL:** https://doi.org/10.5281/zenodo.14160885 (v2.0.0, 2024-11-14), CC-BY 4.0 [V]. Methodology in Peer Community Journal (Mahmoud et al. 2024) [F].
- **Files [V]:** `data_trials.csv` (37 trials with lat/lon, soil, preceding crop, residual N), `data_traits.csv` (34,737 rows, long format), `data_management.csv`, `data_climate.csv` (2.3 MB, daily), metadata and references.
- **Content [V]:** France (Angers 10 trials, Auzeville 12+, Grignon), Denmark, Italy, Germany, England, 2001-2017. Pulse species: pea (7,605 rows), faba bean (5,244), **lentil (2,368)**, chickpea (544), lupin (240). Mixtures: durum wheat-pea, durum wheat-faba bean, **soft wheat-lentil (4,038 rows)**, durum wheat-chickpea, barley-pea/faba bean/lupin. 21,309 rows in intercropping (IC) and 13,428 in monoculture (SC). Relative densities (0.5/0.5 most common), N doses 0-210.
- **Variables [V]:** height, cover, BBCH, biomass, absorbed N, LAI, grain biomass, TSW, grain N, etc. No exact duplicates.
- **Gotchas:** few sites; grain yield is stored as `biomass_seed` (916 rows), so pivoting needs care by measurement date; no commercial quality data (bruchid, sorting).
- **Relevance: 7/10.** Allows computing the LER (land equivalent ratio) and checking whether intercropping stabilizes the pulse, which is exactly the argument for intercropped lentil (a common practice against lodging and weeds).

## 5. V.faba.Multi_Cla_Field_LeafFragments: field photos of faba bean diseases

- **URL:** https://doi.org/10.57745/H7JVFN, published 2025-05-22. The API does not return a license [V]; assume Etalab like the rest of the collection [NV].
- **Files [V]:** index `00_Contents...tab` (2,110 rows), README, `V.faba.zip` of **6.7 GB** (I did not download it).
- **Content [V]:** 2,110 RGB smartphone images, 14 dates between Feb and Jul 2024, 3 localities (Le Rheu 35: 1,938; Frontenac 33: 88; Loyat 56: 84), with Lambert93 and WGS84 coordinates. Labels: several causes `Zmu` 1,262, rust `Rou` 256, chocolate spot `Bot` 174, downy mildew `Mil` 146, Cercospora 84, healthy 62, other symptoms 49, virus 42, Ascochyta 35. Category `Mo` (single cause) 737.
- **Gotchas:** only ~850 images with a single cause; strong imbalance; one year and almost a single site (spatial leakage). It does not decide food vs feed (that is the bruchid).
- **Relevance: 6/10** for a field diagnosis demo; low for the economic argument.

## 6. BSV OCR archive (PestObserver)

- **URL:** https://www.data.gouv.fr/datasets/archive-en-agro-ecologie-de-bsv-bulletins-de-sante-du-vegetal ; `reportsOCR.zip` 173 MB, CC-BY [V].
- **Content [V]:** 40,829 files (txt/xml) from 1946 to 2016, 457 MB uncompressed. 257 file names with protéagineux/féverole/lentille; the pulse ones with a year in the name: 2011 (11), 2012 (20), 2013 (13), 2014 (19), 2016 (2). Files containing the word "bruche": 597; "aphanomyces": 135; "sitone": 1,789 (includes other crops and alfalfa) [V with grep].
- **Example [V]:** BSV Pois Protéagineux n°14 (Centre, 18-24/6/2014): number of plots observed, stages, aphid threshold (20-40 per plant), list of observers (Axéréal, chambers, cooperatives).
- **Gotchas:** only up to 2016; BSV 2017-2026 are PDFs on DRAAF and chamber websites (must be scraped); OCR with spaces between letters; the information is regional and qualitative.
- **Relevance: 6/10.** Ideal material for LLM extraction (essential AI) to rebuild a region × week × pest series.

## 7. Chickpea with service plants, weeds and ascochyta (Angers)

- **URL:** https://doi.org/10.57745/05KBPZ, Etalab 2.0 [V].
- **Content [V]:** 503 rows, 2023-2024, 4 blocks, service species (alone, Egyptian clover, faba bean, oat, Sudan grass) × termination. Variables: DAS, GDD (base 6 °C), stage, chickpea biomass, service plant (19% missing), weeds, **MDS** (ascochyta 0-4, only 108 rows), **yield** (84 rows, g/m², median 14, maximum 539: many zeros).
- **Relevance: 5/10.** Useful as agronomic evidence (chickpea is the expanding human-food crop), small for modelling.

## 8. Epiphyt (epidemiological surveillance network, BSV) via TEMPO portal

- **What it is [F]:** the DGAL database where observations from the BSV network are uploaded. Epiphyt-Extract allowed csv/API export to authorized actors, only for data under the national protocol and "not sensitive" (2017 service note) (https://info.agriculture.gouv.fr/boagri/instruction-2017-539/telechargement).
- **Open part [F]:** the TEMPO portal (https://tempo.pheno.fr, doi 10.57745/NQ9HRV, Etalab) exposes the **phenology** of Epiphyt (stage by date and site) for 13 crops, including *Lathyrus oleraceus* (= pea) and *Phaseolus vulgaris* (https://agrostacwiki.containers.wur.nl/index.php/TEMPO1).
- **What I could not do [NV]:** download data automatically (the portal is a web app with CSRF, with no documented API); confirm whether Epiphyt's pest observations (bruchid, sitona, aphid) are public. My reading is that they are not.
- **Relevance: 5/10.** If a DGAL mentor or Terres Inovia gets us an Epiphyt extract for protein crops, it would be the gold dataset for pest risk.

## 9 and 10. Varieties: Terres Inovia catalogue and myVar

- **Catalogue [V]:** https://www.data.gouv.fr/datasets/catalogue-des-varietes-doleoproteagineux-declarees-commercialisees-en-france , CSV 51 kB, CC-BY, 620 varieties (March 2023), `;` separator, non-UTF-8 encoding (latin-1) and column names with spaces. Pulses: yellow spring pea 39, winter pea 30, green spring pea 14, spring faba bean 17, winter faba bean 10, chickpea 13, lentil 11, lupin 15, soybean 98. Columns: GNIS code, GEVES code, year of registration, breeder, organic availability, Terres Inovia evaluation.
- **myVar [F]:** https://www.myvar.fr post-registration results by region (e.g. lentil: 8 varieties in 11 trials in 2021; spring pea 2023: 19 varieties in 18-28 trials). It is an interactive web with reCAPTCHA, no download [V that reCAPTCHA is in the HTML]. License [NV].
- **GEVES VATE:** I found no open data on registration trials [NV]. GEVES data is already "inside" Pea_dataset (anonymized).
- **Relevance: 5 and 4.**

## 11. Eurostat `apro_cpsh1` (crop production)

- **API [V]:** `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apro_cpsh1?geo=FR&crops=P1100...` (updated 27/10/2026). Units: `AR_THS_HA`, `HPRD_HUMD_EU_THS_T`, `YLD_HUMD_EU_T_HA`.
- **France [V]:** total pulses and protein crops 308 kha (2018) and 321 kha (2024); pea 175 kha (2018), 166 (2024), 162 (2025), **150 (2026, provisional)**; faba bean 57 → 80 → 112 → 118 kha (2018 → 2026); lupin 3-5 kha; lentil 33.9 kha and 51.6 kt (2025).
- **Gotcha:** Eurostat pea (166 kha in 2024) does not match the 124 kha from Terres Inovia cited in `idea5_drone.md` (different definitions, probably including mixtures or forage pea). The regional table `apro_cpshr` returned no values for pea 2023 in my query [NV].
- **Relevance: 5/10**, context for the pitch (faba bean doubling, pea falling).

## 12. GBIF: occurrences of pulse pests and pathogens

Counts [V] (country FR / FR with coordinates 2015-2026 / Europe with coordinates): *Bruchus rufimanus* 205 / 80 / 2,828; *B. pisorum* 154 / 83 / 571; *B. signaticornis* (lentil) 31 / 15 / 54; *Sitona lineatus* 2,161 / 1,218 / 24,605; *Aphanomyces euteiches* 4 / 0 / 5; *Acyrthosiphon pisum* 294 / 95 / 1,677; *Cydia nigricana* 103 / 36 / 2,119; *Orobanche crenata* 386 / 86 / 3,037; *Ascochyta fabae* and *Botrytis fabae* 0 in France.
**Conclusion:** these are naturalist records, with no sampling effort or abundance. Useless as a target. Relevance 2/10.

## 13. Lentil Disease Classification (Hugging Face / Mendeley)

- https://huggingface.co/datasets/Project-AgML/lentil_disease_classification, CC-BY 4.0, cites Mahamud et al. 2025, Data in Brief 58:111224 [V].
- **[V]:** 5,349 images, all 224×224, 4 balanced classes (ascochyta 1,229, rust 1,248, healthy 1,569, powdery mildew 1,303). No exact duplicates or near-duplicates with 8×8 aHash, but **the file names are `aug_*.jpeg`**: they are augmentations of a smaller original set, so any random split leaks.
- Bangladesh, foliar diseases that do not define human vs feed destination in France. Relevance 3/10.
- Others on HF [V listing]: dry bean Uganda/Tanzania (AgML, 1,295 images), soybean Brazil. No interest for France.

## 14. Hyperspectral lentils, foreign bodies (Cubert)

- https://huggingface.co/datasets/cubert-gmbh/XMR_Industrial_Foreign_Object_Detection_Lentils, Apache-2.0 [V]. Beluga and marbled green lentils, 7 contaminant classes (stem, stone, aluminium, paper, fly, rubber), COCO annotations, `.cu3s` format (cuvis SDK) [F README]. Laboratory. Does not include bruchid-damaged grains [F].
- **Relevance: 4/10.** Interesting for "smart sorting", but the format and the lack of bruchid make it harder.

## 15 to 23. Rest (brief)

- **Pea ascochyta (10.57745/5B1XGU, MQXKCP)** [V metadata]: biotest images with segmentation ground truth and Weka classifiers. Laboratory. 3/10.
- **Crop Suitability *Pisum* ERA5 (10.57745/EYAMIF)** [V]: txt lat/lon/index, 36,801 cells, 0.25°, two versions (Feb-Jun and full year). Could be checked against Pea_dataset. 4/10.
- **LCA lentil/chickpea Agribalyse (10.57745/HKQIYX, LXAQRN)** [V metadata]: conv./organic inventories with average technical itinerary. Useful to quantify environmental impact for the pitch. 4/10.
- **Rés0Pest (10.57745/FPKPPC)** [V]: 360 yield rows 2013-2023 in pesticide-free systems; ~55 pulse mentions (spring faba bean, winter pea, chickpea, soybean, lupin). 3/10.
- **PKGC 2021 N (10.57745/ZF8RK1)** [V metadata]: N dose per crop and NUTS3. To estimate the mineral N a pulse avoids in the rotation. 3/10.
- **PHETEC phenology and Terres Inovia BBCH scales** [F]: pea/wheat/sunflower in Auzeville 1997-2008; stage ontologies for pea, faba bean, chickpea, soybean. 3/10.
- **Legumes' traits dictionary BELIS (10.57745/9IIWVW)** [V metadata]: ontology of ~700 traits for 14 species. 2/10.
- **DiverIMPACTS (Zenodo 3966842, 3249967)** [V metadata]: survey of diversification experiences and barriers in 25 European cases. 3/10.
- **Agrosyst / DEPHY** [F]: technical itineraries of >2,000 farms, access on request to Datagrosyst. Not viable in 20 h. 3/10.
- **Terres Inovia EVA Aphanomyces** [F]: free DSS that classifies risk using dept, soil type, pea history and irrigation; built on 780 plots in the north and validated on 120 (https://www.terresinovia.fr/en/oad/aphanomyces-risk-assessment, https://www.reussir.fr/grandes-cultures/pois-proteagineuxmaladie-loutil-eva-evalue-le-risque-aphanomyces). Closed base. Serves as a benchmark and as proof that the problem matters.
- **Ecolab, pulse area (data.gouv)** [V metadata]: 2010-2024 series by dept, derived from Agreste. Duplicates what has already been audited.

---

## 24. Idea seeds (user + decision)

1. **"Winter or spring pea, and when to sow?" so the lot reaches food quality.** Data: Pea_dataset (yield + protein + flowering + daily climate + soil) + SAFRAN for the current year + RPG to know where pea is grown. User: cooperative technician or farmer in a given dept. Decision: pea type, trait profile (earliness, Hr, cold tolerance) and sowing window that maximize P(yield ≥ X and protein ≥ fractionation threshold). AI: genotype × environment model with climate per stage (heat and drought at flowering), with uncertainty quantiles. This is the strongest and newest data point I found. Risk: anonymous genotypes, trial yields.

2. **Producer recruitment map for lentil and chickpea.** Data: RPG 2015-2024 per parcel (LEC, PCH), INRAE successions, SAFRAN, Agreste. User: grain collector or brand (Berry/Puy lentil, Southwest chickpea) that wants to add hectares under contract. Decision: which communes to look for new producers in (rotations compatible with wheat/sunflower, climate analogous to areas where it already works, infrequent pulses = less disease pressure). AI: agroclimatic niche similarity, ranking. Risk: no yield target per parcel.

3. **Aphanomyces risk per parcel from RPG history.** Data: RPG 2015-2024 (overlay geometries to rebuild each parcel's sequence and count previous peas/lentils/faba beans), soil (BDGSF/RRP), climate. User: cooperative that assigns pea contracts. Decision: exclude or test (infectious potential test) parcels with return of host legumes < 5-6 years. Moderate AI (more rules + prioritization), but automatable at basin scale, which EVA does not do (EVA asks the farmer for data). Risk: no disease data to validate.

4. **LLM-based BSV extractor to rebuild pest pressure region × week.** Data: BSV OCR archive 2011-2016 (257 pulse bulletins) + DRAAF PDFs 2017-2026 + HPEMYW (bruchid) + SAFRAN. User: Terres Inovia / BSV coordinators / cooperatives. Decision: anticipate the monitoring window for bruchid and aphid and the % of lots that will not reach human quality. Essential AI: structured extraction (number of plots, % with pest, threshold exceedance) from unstructured text. Fits the "AI essential" criterion and combines well with bruchid idea 3. Risk: time to scrape the new PDFs.

5. **Cereal-pulse intercropping assistant (wheat-lentil, durum wheat-chickpea).** Data: 37 European trials (LER calculable), chickpea service plant trial, climate. User: producer who hesitates to sow lentil because of fear of lodging and weeds. Decision: monoculture vs intercrop and relative densities. Risk: few trials, separating the intercropped grain adds sorting cost.

Discarded ideas: leaf diagnosis of faba bean or lentil from photos (small data or from Bangladesh, and foliar disease does not decide human destination); GBIF (no abundances).

## 25. Housekeeping

- Scripts in `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/ds_agro/scripts/` (pea.py, succ.py, succ2.py, rpg.py, lentil.py). Run with `uv run ... python -I`.
- Data folder `.../scratchpad/ds_agro/data` **deleted** at the end (see the report).
