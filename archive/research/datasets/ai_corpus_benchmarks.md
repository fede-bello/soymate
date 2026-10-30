# "AI-ready" assets for Track 3 (pulses for human food)

Survey done 29/10/2026. Corpus for RAG, variety/genetic data, image and tabular benchmarks, intercropping and surveys.
Legend: **[V]** verified by me (downloaded the file, queried the API or read the record at the source), **[F]** secondary source (article, search result), **[NV]** not verified.
We respect the hackathon rule: exploration only (counts, classes, label quality). No model was trained or fitted. Everything was downloaded to `scratchpad/ds_ai/data/` and deleted at the end.

## Summary table

| # | Dataset | Owner | Size (verified) | License | Access | Rel. T3 | Main limitation |
|---|---|---|---|---|---|---|---|
| 1 | **BSV archive / Avertissements agricoles (agricultural warnings, OCR)** | data.gouv.fr (VESPA/PestObserver project, INRA) | 40,828 OCR texts (173 MB zip), 1950-2016; **3,077 docs** mention protéagineux (protein crops)/féverole (faba bean)/lentille (lentil) | **CC-BY** | direct download | **9** | Ends around 2016; old medium-quality OCR; nothing from 2017-2026 |
| 2 | Recent BSV (DRAAF/Chambres) | Regional DRAAF + Chambres + Terres Inovia | ~3,400 BSV/year nationally [F]; DRAAF Centre-Val de Loire (CVL): ~9 annual pages "BSV Protéagineux", 15-22 PDFs each [V] | No explicit license (public State site) [NV] | Loose PDFs, one site per region, no national index | 8 | Scattered; you have to scrape region by region |
| 3 | **Pea_dataset (French pea trials 2002-2024)** | INRAE + Terres Inovia + GEVES (Recherche Data Gouv, doi:10.57745/FW78RE) | 4,450 site×genotype×year situations, 158 sites, 117 genotypes, 4,230 yields, 3,326 proteins, daily weather | **Etalab 2.0** | direct download (9 MB) | **9** | **Anonymized** genotypes ("Genotype_27"): not useful for recommending varieties by name |
| 4 | **Cereal-pulse intercropping (37 trials)** | INRAE (Gaudio, Justes, Bedoussac), Zenodo 14160885 | 37 trials (26 in France), 34,737 trait rows, 5 pulses | **CC-BY 4.0** | direct download (8 MB) | 8 | Trials 2001-2017 at stations, not on farms; few economic variables |
| 5 | **Soybean pulse-beetle infestation (eggs/holes)** | Mendeley Data d97rjyk2tz (v2, 2026) | 2,726 images 640×640 (1,181 originals), 14,475 YOLO boxes, 5 classes | **CC-BY 4.0** | direct download (80 MB) | **8** | It is **soybean** and *Callosobruchus* (storage beetle), not faba/lentil with *Bruchus*; likely train/test leakage |
| 6 | Soybean Seeds (5 quality classes) | Mendeley v6vzvfszj6 (Kaggle mirror warcoder) | 5,513 crops 227×227: intact 1,201, immature 1,125, skin-damaged 1,127, spotted 1,058, broken 1,002 | CC-BY 4.0 | Kaggle without login | 6 | Soybean; Chinese standard GB1352; 290 groups of exact duplicates |
| 7 | **V.faba Multi_Cla_Field_LeafFragments** | INRAE (doi:10.57745/H7JVFN) | 2,110 smartphone photos of faba bean leaves, Le Rheu/Loyat/Frontenac 2024, 8 classes | **CC-BY-NC** | direct download (6.7 GB zip) | 7 | 60% multi-cause images; small classes (Asc 35, Vir 42); NC |
| 8 | Lentil disease (AgML) | Project-AgML / HF (orig. Mendeley 7vb77bz2st) | 5,349 images 224×224, 4 balanced classes | CC-BY 4.0 | HF parquet | 4 | Augmented images, Bangladesh origin, leaves not grains |
| 9 | Pea seed viability (AgML) | HF Project-AgML | 3,000 images (1,500 dead / 1,500 live) | CC-BY 4.0 | HF parquet (270 MB) | 5 | Lab in Beijing; viability is not insect damage [NV content] |
| 10 | Ascochyta on pea stipules | INRAE (doi:10.57745/5B1XGU) | 210 MB: RGB images + segmentation ground truth | Etalab 2.0 | direct | 5 | Laboratory biotest, few images |
| 11 | Faba Bean Seed Image Dataset | Zenodo 18226381 (AAFC Canada) | photos of 6 MB each of 554 lines, with colour chart and ruler, + trait Excel | CC-BY 4.0 | direct | 4 | Phenotyping (size/shape), **no damage labels** |
| 12 | Lentils: "skinned/split/whole" | Kaggle killa92 | 297 images 224×224 (99/99/99) | CC BY-NC-SA | Kaggle without login | 3 | Very small; processing classes, not quality classes |
| 13 | Lentils YOLO (TFG, final degree project) | Kaggle gonzaloferrermena | 180 images 1920×432, 1,146 boxes, 1 class | CC-BY 4.0 | Kaggle without login | 3 | Only "lentil" detection/counting |
| 14 | Indian Lentils (20 pulses) | Kaggle pratikprakhar | 10,000 images (500 × 20 classes), 127 px | Apache 2.0 | Kaggle without login | 2 | Thumbnail-like, 305 duplicate groups, dubious provenance |
| 15 | Dry Bean Dataset (Koklu) | UCI / Kaggle | 13,611 grains, 16 geometric features, 7 varieties | CC0 | direct | 3 | Tabular features only; Turkish varieties |
| 16 | Hyperspectral dry bean cooking time | Zenodo 4937364 (USDA/MSU) | 1.8 GB HSI of 14 *Phaseolus* genotypes | CC0 | direct | 5 | Large; not downloaded [NV content] |
| 17 | X-ray faba bean (GEVES + LARIS) | Plant Methods 2024 | 7,210 RAGT seeds, 353 X-rays, damaged/undamaged classes | paper CC-BY; **data not public** | on request | 7 (if they share it) | No availability statement: must be requested from GEVES |
| 18 | HAL (pulses) | CCSD / INRAE | 5,084 records, **1,494 with PDF**, 721 INRAE, 614 in French | 991 "HAL authorisation", 289 CC-BY, rest various CC | open API | 7 | Mixed licenses; scientific text, not a "field manual" |
| 19 | Legume Hub (Legumes Translated) | Donau Soja (H2020) | 268 articles + 336 images (WP sitemap) | "All rights reserved", **non-commercial** reproduction with citation | web / WP API | 6 | English, European; much of it forage/animal feed |
| 20 | GECO (EcophytoPIC) | Acta, INRAE, Chambres | sitemap only 102 pages; sheets rendered in JS | sheets **CC BY-NC-SA 3.0 FR** | web | 5 | Focused on reducing plant protection products; not very pulse-specific |
| 21 | Terres Inovia crop guides | Terres Inovia | crop guides (pois chiche 2026 exists [F]) | robots.txt: `ai-train=no`, `use=reference`, AI bots blocked | PDF, Cloudflare blocks automatic fetch | 9 (content) / 3 (license) | **Cannot be scraped or redistributed**; requires an agreement |
| 22 | EIP-AGRI practice abstracts | EU CAP Network | 16,790 abstracts total [V via web] | EC legal notice [NV] | web, no bulk export | 5 | No bulk download; keyword filter unreliable |
| 23 | CY-Bench | WUR / JRC (Zenodo 17279151) | maize and wheat only | EUPL-1.2 / CC-BY | direct | **1** | **Does not include pulses** |
| 24 | Eurostat apro_cpshr (NUTS2) | Eurostat | P0000 dry pulses, 83 geos FR, 2000-2024: area 1,176, production 1,176, published yield 5 | reuse Eurostat | API | 6 | Yield almost never published: you have to derive it as production/area |
| 25 | CropHarvest labels | Zenodo 10251170 | 113,893 points; 1,951 "leguminous", **618 in Île-de-France** (pois, féverole, lentille) | CC-BY-SA 4.0 | direct | 4 | Crop type labels, not yield |
| 26 | Legumes' traits dictionary (BELIS) | INRAE doi:10.57745/9IIWVW | 15 files, ~700 traits, 7 grain pulses | Etalab 2.0 | direct | 4 | Ontology, not data |
| 27 | Lentil consumption survey 2022 | INRAE doi:10.57745/KMGODH | 607 responses | Etalab 2.0 | direct | 4 | Consumer side, not farmer side |
| 28 | Global grain legume experiments (Cernay) | Zenodo 4937951 | 173 articles, 39 species, 9 tables | CC0 | direct | 5 | Global meta-dataset, 2017 |
| 29 | Pulse genomics (KnowPulse, LIS, URGI) | USask, USDA, INRAE | portals accessible (HTTP 200); LIS with folders Cicer, Lens, Pisum, Vicia | various | direct | 2 | Useful for breeding, not for a 20 h product |
| 30 | GEVES catalogue / EU Plant Variety DB | GEVES / EC | ~9,000 varieties in FR catalogue [F] | public consultation | web UI with export button; no documented API | 5 | No counts per species obtained (programmatic access blocked) |

## Key findings (the specific questions you asked)

**(a) Are there images of pulse seeds damaged by bruchids vs healthy ones?**
- **There is no open dataset of faba, lentil or pea with *Bruchus* damage.** I searched Kaggle (public API, 16 queries), HuggingFace, Zenodo, Mendeley and Recherche Data Gouv. [V]
- The closest usable one: **Mendeley d97rjyk2tz**, soybean infested by "pulse beetle" (*Callosobruchus*), with eggs, exit holes, cracked testa, non-insect damage and healthy. CC-BY 4.0. Smartphone photos (Redmi 13C), one seed per image, close-up. See section 5. [V]
- The only **faba bean with insect damage** dataset is the GEVES X-ray set (7,210 RAGT seeds, damaged/undamaged), but it is not public: you have to request it. [V paper, NV availability]
- For a faba/lentil demo you will have to take your own photos (a couple of kilos of "bruchée" (bruchid-damaged) faba bean from a coop or Terres Inovia are enough for a small validation set) or do transfer learning from soybean.

**(b) Does CY-Bench include French pulses?** **No.** The README of `WUR-AI/AgML-CY-Bench` covers **only maize and wheat** (EU via Eurostat: "Grain Maize" and "Soft Wheat"). [V]
Alternatives for yields: the **Pea_dataset** (trials, plot level) and Eurostat `apro_cpshr` (P0000, area + production NUTS2 for France 2000-2024; published yield is almost never there, you have to derive it). [V]

**(c) Is there an open, credible corpus for a RAG advisor?** **Yes, if you build it:**
1. **BSV OCR archive on data.gouv (CC-BY)**: 40,828 bulletins, 3,077 on pulses, with literal advisory text (thresholds, sensitive stages). [V]
2. **BSV 2017-2026** from the DRAAF sites (Word-generated PDFs, clean extractable text). [V sample]
3. **HAL**: ~290 CC-BY PDFs + 991 under HAL authorisation (reading/citation OK, redistribution to check). [V]
4. **Terres Inovia** is the richest source, but its robots.txt declares `ai-train=no`, `use=reference` and blocks ClaudeBot, GPTBot, etc. For the demo: **cite and link, do not ingest in bulk** (or ask for permission, which is also a good gesture for the jury). [V]

---

## 1. Document corpora for RAG

### 1.1 BSV / Avertissements agricoles archive (data.gouv.fr) [V]
- **URL**: data.gouv.fr, dataset "Archive en agro-écologie de BSV (Bulletins de Santé du Végétal, plant health bulletins)" (id `583eac9ac751df6321c0bb7e`). Resource `reportsOCR.zip`: https://static.data.gouv.fr/resources/archive-en-agro-ecologie-de-bsv-bulletins-de-sante-du-vegetal/20161130-222606/reportsOCR.zip
- **Owner**: VESPA / PestObserver project (INRA, LIRMM). License **CC-BY**. Created 30/11/2016, last modified 12/10/2023.
- **Format**: 23,542 `.txt` (BSV 2009-2016 from the DRAAF/Chambres sites) + 17,286 `.xml` TEI (Avertissements Agricoles, agricultural warnings, 1950-2009, OCR). The zip of original PDFs (32 GB, pestobserver.eu) **does not respond** (HTTP 000). [V]
- **Audit** (script `bsv_audit.py`):
  - 40,828 files, 596 empty (<50 B).
  - By five-year period: 1960-2005 ~1,000-2,400 docs every 5 years; **2010-2014: 10,583**; 2015-2016: 3,867.
  - Mentions: "pois" 5,511 docs, "protéagineux" 2,109, "féverole" 1,687, **"bruche" 597**, "lentille" 171, "pois chiche" 11.
  - **3,077 docs** mention protéagineux/féverole/lentille (866 from 2010-2014).
  - Text quality is good in the BSV 2010+, for example Normandie 2013: *"Le seuil de nuisibilité est atteint lorsque l'on cumule plus de 2 journées avec des températures dépassant 20°C"* (the damage threshold is reached when more than 2 days with temperatures above 20°C accumulate) for bruches (bruchids) in féverole. The old TEI XML files have title/date/region in the header.
- **Metadata according to the record**: region, crops, diseases, insects, risk, pesticides (27 zones, 389 insects, 279 diseases, 727 pesticides, 122 crops). I did not find them as a separate file in the zip [NV].
- **Limitations**: ends in 2016. Some pesticides cited there are banned today, so the RAG has to filter by date or flag it. File names carry region/year inconsistently (for 839 pulse docs I could not extract the year from the file name).
- **Relevance: 9/10.** It is the only large, open French corpus with a clear license for field plant-health advisory.

### 1.2 Recent BSV (2017-2026) on DRAAF sites [V partial]
- Example: DRAAF Centre-Val de Loire, "BSV Protéagineux" articles (a261, a335, a556, a782, a976, a1157, a1348, a1511, a1617...). One page per campaign, with **15-22 PDFs each** (for example, 2023 has 14 bulletins plus the annual review (bilan)).
- Sample: `bsv_proteagineux_01_du_11-03-25.pdf`, 11 pages, Word→PDF, 1,487 words, clean extraction with `pdftotext`. The writing is by **Terres Inovia** with the Chambre d'Agriculture (regional farm chamber); the observers include Axéréal, Agro Centre, CA18/28/36/37/41/45 and UCATA. It includes a disclaimer ("ne peut pas être transposée telle quelle à la parcelle", it cannot be applied as is to a plot).
- National volume: ~3,400 BSV/year, all crops ([F] D2KAB/INRAE presentation).
- **There is no national index.** The D2KAB project (ANR, French National Research Agency) has an RDF-annotated corpus, but it is small test corpora (230 and 497 BSVs) [F].
- **License**: I did not see an explicit license mention in the PDF (I searched for "reproduc", "licen" and "propriét" with no results). They are public documents from the Ecophyto plan (national plan to reduce pesticide use). For a demo, citing with a link is reasonable [NV on the legal side].
- **Idea**: combining 1.1 and 1.2 gives a 1980-2026 series of bruchid, ascochyta blight (ascochytose) and aphid (pucerons) alerts by region.

### 1.3 Terres Inovia (crop guides, sheets) [V robots, NV content]
- `robots.txt`: `Content-Signal: search=yes,ai-train=no,use=reference`, with an explicit reference to art. 4 of EU Directive 2019/790 (text and data mining reservation). It blocks ClaudeBot, GPTBot, CCBot, Google-Extended, MistralAI-Training, etc. **Cloudflare returns 403** to automated fetches (I verified with curl and WebFetch, and did not try to get around it).
- `ai-input` (RAG) is not declared: neither allowed nor prohibited. The cautious reading is that you can **cite and link**, but not copy the corpus into a redistributable index.
- `guide_culture_pois-chiche_2026_terresinovia.pdf` exists [F], and there are also guides for pea, féverole and lentille [F].
- **Recommendation**: for the demo, download 4-5 guides by hand (pea, féverole, lentille, pois chiche), use them only locally for the prototype, and say so in the pitch ("in production: agreement with Terres Inovia"). Better still: email them before the event to ask for permission.

### 1.4 GECO (geco.ecophytopic.fr) [V]
- Publisher: **Acta**, with INRAE and the Chambres Nouvelle-Aquitaine and BFC (Bourgogne-Franche-Comté). Knowledge sheets and forum under **CC BY-NC-SA 3.0 FR**, attribution "GECO-EcophytoPIC". The site itself (structure, software) cannot be reproduced without authorization.
- `robots.txt` allows everything. The sitemap has only 102 URLs (crop category pages); the concept sheets load via JS (Liferay), so scraping is awkward.
- **Relevance 5**: useful for general agroecology (rotations, service plants, protein autonomy), not specific to pulses. NC (non-commercial): fine for a hackathon, problematic for a commercial product.

### 1.5 HAL / OpenAlex [V]
- HAL API (`api.archives-ouvertes.fr`), query FR+EN (féverole, pois protéagineux, légumineuses à graines (grain legumes), grain legume(s), faba bean, field pea, lentil/lentille, chickpea/pois chiche):
  - 5,084 records; **1,494 with PDF**; 721 in the INRAE collection; 614 in French; 1,054 since 2015.
  - Types (with PDF): 672 articles, **366 theses**, 215 conference papers, 89 posters, 69 dissertations.
  - Licenses (with PDF): 991 "HAL authorisation", **289 CC-BY 4.0**, 91 BY-NC-ND, 45 copyright, 38 BY-NC, 17 BY-SA, 10 BY-NC-SA, 8 CC0.
  - Intercropping (intercrop / cultures associées) with PDF: 754.
- OpenAlex (phrase search, all dates; "OA + French author"): grain legume 57,064 (1,739); faba bean 62,623 (1,722); lentil 93,321 (1,930); field pea 24,016 (494); chickpea 130,947 (2,196); intercropping legume cereal 19,180 (1,078). The totals are inflated by full-text search; use them only as an order of magnitude.
- **Use**: "scientific evidence" layer of the RAG (for example, the effect of intercropping on bruchids), with a link to the DOI.

### 1.6 Legume Hub (legumehub.eu) [V]
- Output of the H2020 Legumes Translated project, edited by Donau Soja. **268 articles** (`legume_article`), 336 images and 5 discussions (WP sitemap).
- License: "© All rights reserved. Reproduction and dissemination for non-commercial purposes are authorised provided the source is fully acknowledged."
- English-language content with a European focus. There are useful articles (*bean weevil in faba bean*, *establishing high-yielding faba bean*), but much of it deals with animal feed (excluded from the track).

### 1.7 EIP-AGRI practice abstracts [V partial]
- EU CAP Network, search at `projects/practice-abstracts/search_en`: **16,790 abstracts**. It has no bulk export, and the keyword parameter I tried did not filter. Some projects publish their PAs (practice abstracts) as xlsx/Zenodo (for example agroBRIDGES at WUR).
- License: EC legal notice (reuse with attribution) [NV exact wording].
- **Relevance 5**: short and practical format, ideal for RAG, but hard to extract the pulse part.

### 1.8 Chambres d'agriculture (regional farm chambers) [F/NV]
- There are loose sheets (for example a "Fiche protéagineux" from the Creuse department), generally without an open license. There is no consolidated corpus. Relevance 4.

---

## 2. Varieties and genetics

### 2.1 GEVES / CTPS / EU Plant Variety Database [F/NV]
- FR catalogue: ~9,000 varieties in total (SEMAE [F]). The GEVES UI (`geves.fr/catalogue-france/`) has an export button (`kc_geves_catalogue_angular_export.php`) and uses Algolia behind it. **I did not get counts per species**: programmatic access was blocked by my environment's policy, so at the event it is best to export it by hand from the browser.
- EU Plant Variety Portal (`ec.europa.eu/food/plant-variety-portal/`) responds with HTTP 200. It has Excel export from the UI [F].
- **Use**: variety lookup table (year of registration, breeder, list A/B) for a variety-choice assistant.

### 2.2 Pea_dataset (doi:10.57745/FW78RE) [V], the best tabular asset
- Published 05/08/2026, **Etalab 2.0**. Sources: "Terres Inovia GEVES and partners" 3,936 situations, Burstin et al. 2021 425, Vocanson & Jeuffroy 54, Gaudio et al. 35.
- `trials_data` (4,450 × 33): site, postal code (CP), lat/lon, soil (USDA class, depth, clay/silt/sand, AWC, C/N, CaCO3, N), previous crop (41% NA), type (2,705 spring / 1,745 winter), genotype (**anonymized**), varietal traits (Hr allele, seed colour, protein class, earliness, lodging, cold, TSW), sowing date/density, irrigation.
- `crop_traits_data` (27,168 long rows): `yield_14` 4,230 (mean 49.5, median 49.1, range 14-100, presumably q/ha at 14% moisture), `protein_content` 3,326, `tsw_14` 3,369, flowering 4,450, height 2,762, biomass 998, LAI 172, N fixation 53.
- Daily weather per site (158 CSVs: ETP (potential evapotranspiration), mean temperature, global radiation (RG), rain (RR), Tmax, Tmin).
- Years: bulk 2013-2024 (2015: 551, 2017: 534, 2022/2023: 496 each).
- **Limitations**: anonymous genotypes; these are trials (not farms); no prices or profitability.
- **Relevance 9**: allows predicting yield and protein by site, climate, sowing and varietal type, and analysing the climate risk for pea in France.

### 2.3 Legumes' traits dictionary (BELIS, doi:10.57745/9IIWVW) [V]
CropOntology ontology, ~700 harmonized traits across 7 grain pulses. Useful to normalize variables, adds no data.

### 2.4 Genomic resources [V accessibility]
- Legume Information System (`data.legumeinfo.org`): folders Cicer, Lens, Pisum, Vicia, Phaseolus, etc. KnowPulse (USask) and pulsedb.org respond with 200. URGI (INRAE) has pea downloads (Cameor genome).
- **Relevance 2**: out of reach in 20 h and for the farmer-impact criterion.

---

## 3. Vision benchmarks (seeds and diseases)

### 3.1 Soybean seed infestation (pulse beetle), Mendeley d97rjyk2tz v2 [V], the closest to bruchid
- CC-BY 4.0, published 17/07/2026. Zip of 80 MB. README: 2,726 images (**1,181 originals**), native resolution 8160×6144 delivered at 640×640, YOLO.
- Classes: Egg, Hole (larval exit hole), Testa cracking, Normal_Damage (non-insect discolouration), Healthy.
- Box counts (I verified them myself):
  - train 2,180 imgs: Egg 7,536, Hole 1,417, Testa 1,051, Normal 193, Healthy 1,148 (34 unlabelled).
  - val 272: Egg 1,059, Hole 182, Testa 90, Normal 23, Healthy 130.
  - test 274: Egg 1,134, Hole 249, Testa 124, Normal 24, Healthy 115.
- **Quality**: I reviewed 8 images with the boxes drawn. The egg and hole boxes are precise, and Healthy encloses the whole seed. The photos are close-ups of **one seed** on white paper or a black background, with a camera watermark and date (Redmi 13C, 2025).
- **Leakage**: 53 perceptual hashes (aHash 8×8) of test match train, and 47 of val match train. As there are 2.3 images per original, the split was probably done after augmentation. If you use it, **re-split by original**.
- **Limitations for France**: (1) it is soybean, not faba bean or lentil; (2) *Callosobruchus* lays eggs on the grain (storage beetle), while *Bruchus rufimanus/signaticornis* lays on the pod in the field, so on French grain you will **not see eggs** but the "window" (operculum) and the exit hole; (3) one seed per photo, not a tray of lots.
- **Relevance 8** as pretraining and proof of concept for "hole/window detection".

### 3.2 Soybean Seeds 5 classes (Mendeley v6vzvfszj6 / Kaggle warcoder/soyabean-seeds) [V]
- 5,513 crops 227×227 from industrial images 3072×2048, classified under the Chinese standard GB1352-2009: Intact 1,201, Immature 1,125, Skin-damaged 1,127, Spotted 1,058, Broken 1,002. 290 groups of exact duplicates (none across classes).
- In the montage the classes look well differentiated (broken, skin-damaged, purple spots).
- Use: generic **grading** classifier (broken / immature / spotted), which is exactly what a coop checks on reception.

### 3.3 V.faba Multi_Cla_Field_LeafFragments (INRAE, doi:10.57745/H7JVFN) [V metadata]
- 2,110 smartphone photos of faba bean leaf fragments, field, 14/02 to 01/07/2024, in Le Rheu (35) 1,938, Loyat (56) 84 and Frontenac (33) 88. Georeferenced (Lambert93/WGS84).
- Tags: Zmu (multi-cause) **1,262**, Rou (rust) 256, Bot (botrytis) 174, Mil (downy mildew) 146, Cer (cercospora) 84, Syl (healthy) 62, Oth (other) 49, Vir (virus) 42, Asc (ascochyta) 35. Category: Mu 1,262, Mo 737, Syl 62.
- Terms of use **CC-BY-NC**, zip of 6.7 GB (not downloaded).
- Use: faba bean disease diagnosis in France with real photos. With only 737 single-cause images, the imbalance is strong.

### 3.4 Other vision datasets (summary)
- **Lentil disease** (AgML/HF, from Mendeley 7vb77bz2st): 5,349 images 224×224 (Ascochyta 1,229, Rust 1,248, Normal 1,569, Powdery 1,303); 0 exact duplicates and 0 aHash duplicates. But the source declares augmentation (rotation, zoom, brightness), so the images are not independent. CC-BY. [V]
- **Pea seed viability** (AgML/HF): 3,000 images, dead/live 1,500/1,500, fixed CCD camera in Beijing. CC-BY. [V record]
- **Ascochyta on pea stipules** (INRAE): RGB + masks + Weka classifier, Etalab 2.0. [V record]
- **Faba Bean Seed Image Dataset** (Zenodo 18226381, AAFC): photos of 554 SSD lines with a 24-patch colour chart, ruler and coin; + Excel with TGW (thousand-grain weight), area and roundness per seed. Useful for measuring size grading, **does not include damage**. [V record]
- **Pea seed instance segmentation demo** (Zenodo 21110940): 5 images, the full set (100) only on request. [V]
- **Good/Bad chickpea** (Mendeley zgph46p46f): Bad and Good folders with ≥1,000 files each (API cap), **HEIC**, ~4 GB, names with duplicate suffixes; the description seems generic. Not downloaded. [V partial]
- **Soybean healthy vs damaged** (Mendeley 65rzpcgbp4): 1,511 smartphone images, Roboflow, CC-BY. [V record]
- **Hyperspectral dry bean cooking time** (Zenodo 4937364, CC0, 1.8 GB): predict **cooking time** (quality for human consumption) from HSI (hyperspectral imaging). Interesting, but it requires hyperspectral hardware. [V record]
- **XMR lentils (Cubert, HF, Apache-2.0)**: hyperspectral, foreign-body detection in lentils (stone, stem, fly, paper...). Industrial. [V record]
- **Kaggle lentils** (killa92 297 imgs; gonzaloferrermena 180 YOLO imgs; pratikprakhar 10,000 thumbnails): low value. [V]
- **Dry Bean Dataset** (Koklu, 13,611 grains, CC0): classic tabular dataset, only useful as an example. [V record]

---

## 4. Agri-ML benchmarks

### 4.1 CY-Bench [V]
- GitHub `WUR-AI/AgML-CY-Bench`, Zenodo 17279151 (EUPL-1.2) and 20456376 (v1.0.0, CC-BY). **Maize and wheat only.** For Europe it uses Eurostat grain maize / soft wheat. Relevance 1 for pulses (at most, the climate/soil/NDVI feature pipeline could be reused).

### 4.2 Eurostat apro_cpshr [V]
- P0000 (dry pulses) France: 83 geos (NUTS1/2, old and new), 2000-2024. Values: moisture 1,763, area 1,176, production 1,176, harvested area 710, **published yield: only 5**. By species (P1100 pea, P1200 féverole), YI_HU_EU has no values for FR. Regional yield is derived as production/area.

### 4.3 CropHarvest [V]
- Zenodo 10251170, CC-BY-SA 4.0. 113,893 points; 1,951 `leguminous`, of which **618 are in Île-de-France** (RPG: "pois de printemps", "pois d'hiver", "féverole", "lentille cultivée", "mélange protéagineux + céréales", ~100 each). Useful for classifying crop type with Sentinel-2, not for yield.

### 4.4 AgriFieldNet [NV]
- India, with lentil, gram (chickpea) and green pea classes. The site `agrifieldnet.github.io` returns 404. Relevance 1 for France.

---

## 5. Intercropping

### 5.1 Global dataset of 37 cereal-pulse trials (Zenodo 14160885) [V]
- CC-BY 4.0 (Gaudio, Mahmoud, Bedoussac, Justes; methodology in Peer Community Journal 2024).
- 37 trials: **France 26** (Angers 11, Auzeville 10, Grignon 5), Denmark 7, Italy 2, Germany 1, UK 1. 2001-2017.
- 34,737 trait rows (IC = intercrop 21,309, SC = sole crop 13,428); 32,327 are from France.
- Mixtures: durum wheat-pea 5,939, durum wheat-faba bean 5,428, soft wheat-lentil 4,038, soft wheat-pea 3,105, barley-pea 1,539, durum wheat-chickpea 620, barley-faba bean 320, barley-lupin 320.
- Variables: height, cover, BBCH, biomass, absorbed N, LAI, `biomass_seed` 916, `nitrogen_seed` 785, `tkw` 757...
- Use: LER (land equivalent ratio) and protein of the cereal in the mixture, by management and climate.
- **ReMIX**: I found no open dataset under that name on Zenodo or RDG [V search]; much of the French trial data is in this dataset.

### 5.2 Others
- PROMISE (Zenodo 15591393): pea-barley in Switzerland, sqlite 1.4 MB, CC-BY. [V record]
- Chickpea + mowed service plant, Angers (doi:10.57745/05KBPZ, Etalab 2.0): 2 years, weed and ascochyta control. [V record]
- CARINA (Zenodo, 2026): chickpea intercropping in Italy. [V title]

---

## 6. Surveys and farmer knowledge

- **I did not find an open microdata set** of farmer surveys on why they do not grow pulses. What exists are reports from the LEGITIMES project (INRAE, `legitimes.hub.inrae.fr`): a SWOT (strengths, weaknesses, opportunities, threats) of barriers and levers, and a report on Midi-Pyrénées with the Qualisol coop. They are PDFs, not data. [F]
- Barriers cited in these sources: productivity and yield instability, aphanomyces in pea, bruchids, lack of market and contracts, less aid since 1992. [F]
- Lentil consumption survey 2022 (INRAE, 607 responses, Etalab 2.0) [V record] and "Survey on Legumes in Institutional Food Services" (doi:10.15454/QR1XMS) [V title]. Both are on the demand side.
- **Implication**: a RAG over these LEGITIMES reports plus the BSVs can answer "why not?" with evidence, but there is no tabular data to train anything on.

---

## 7. Seed ideas

1. **"BruchiScan": bruchid damage control at coop reception with a phone** (CV = computer vision).
   - **User**: reception technician at a coop (Axéréal, InVivo/Soufflet, Cavac).
   - **Decision**: whether a lot is fit for human food or export vs downgraded, and its price.
   - **Why AI is essential**: counting "grains bruchés" (bruchid-damaged grains) by hand over 100-500 grains is slow and subjective; detecting windows/holes from a tray photo does it in seconds and leaves a traceable record.
   - **Data**: pretrain on soybean d97rjyk2tz (Hole class) and Soybean 5 classes; validate with your own faba/lentil photos; anchor the field risk with the INRAE bruchid dataset (see `idea3_bruchids.md`).
   - **Honesty**: there is no public faba bean data, so say so and show the capture plan.

2. **"protéagineux" RAG advisor (protein crops) with citations** (LLM + RAG).
   - **User**: farmer or adviser who hesitates to add pea/faba bean/lentil.
   - **Decision**: should I sow? When do I treat for bruchids? What risk do I face in my region?
   - **Corpus**: BSV 1980-2016 (CC-BY, 3,077 pulse docs) + BSV 2017-2026 from the DRAAF + ~290 HAL CC-BY PDFs + Legume Hub (non-commercial) + Terres Inovia guides, cited with a link only.
   - **Why AI is essential**: 40 years of scattered regional bulletins are impossible to consult by hand. The RAG answers with the citation of the BSV from their region and its date, and distinguishes current recommendations from obsolete ones.

3. **Pea yield and protein simulator by site** (tabular ML on Pea_dataset).
   - **User**: coop or farmer evaluating spring vs winter pea in their area.
   - **Decision**: varietal type (winter/spring, earliness), sowing date and density.
   - **Data**: 4,450 situations with daily weather and soil.
   - **Why AI is essential**: the G×E×M (genotype × environment × management) interaction with daily climate is not solved by a table; a model gives the yield distribution (risk), not just the mean.
   - **Economic bonus**: convert yield × price (FranceAgriMer) into expected margin vs wheat.

4. **Cereal-pulse mixture optimizer** (ML + optimization over the 37 intercropping trials).
   - **User**: organic or low-input farmer.
   - **Decision**: which mixture (durum wheat-pea, wheat-lentil...), with which relative densities and how much N to apply.
   - **Why AI is essential**: estimating the LER and grain protein as a function of management and climate.
   - **Link to human food**: lentil intercropped with wheat is a real case in France (the cereal acts as a support against lodging, with fewer weeds).

5. **Regional bruchid alert** (time series + NLP).
   - Extract from the BSVs (archive + recent) the dates of first catches and of the sensitive stage by region and year.
   - Cross them with weather (the rule of 2 days >20 °C at the young pod stage, "jeune gousse", appears verbatim in the BSVs) to give plot-by-plot early warning.
   - **Why AI is essential**: NLP turns thousands of PDFs into a structured series that does not exist today.

---

## 8. Audit notes

- Scripts in `scratchpad/ds_ai/scripts/`: `audit_imgs.py` (sizes and md5 duplicates), `audit_parquet.py` (HF parquet + aHash), `yolo.py` (box counts and aHash leakage), `bsv_audit.py`, `pea_audit*.py`, `ic*.py`, `ch.py`, `hal.py`, `dv.py`.
- Kaggle: the public endpoint `api/v1/datasets/list` and `.../download` worked **without login** from this machine.
- **All of** `scratchpad/ds_ai/data/` **was deleted** at the end.
