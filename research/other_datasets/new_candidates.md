# Additional dataset search (31/10/2026)

Second search, run at the event, after the pivot to soybean as the product. Goal: more soybean defect data from other capture setups, real multi-seed photos with per-seed labels, and any damaged-legume data. Tags: [V] opened the page or API, [S] search snippet only.

## Result in one line

No new insect-hole data and still no damaged pea, lentil, faba bean, chickpea or bean RGB dataset. Two new sources of real multi-seed photos with per-seed ground truth, and one new source for the foreign-material class.

## Shortlist (ranked)

1. **Ghana seed varieties, Mendeley t94nzy4ptz v2** (CC BY 4.0 [V]). Soybean: 105 group photos (~123 MB) and 14,626 crops [V]. Google Pixel 9a, blue paper, daylight, ~150 seeds per photo; `_crop_metadata.csv` has a box per seed [V]. Use: segmentation and count test, false-positive test on sound seeds. Risks: variety labels only (4 varieties); boxes come from colour segmentation plus manual audit; "FarmerSaved" may hold unlabelled defects; hard shadows.
2. **Mechanical-harvest soybean, Mendeley hwdtghttp7 v2** (CC BY 4.0 [V]), also on Hugging Face as `Project-AgML/soybean_harvest_damage_segmentation` (330 MB parquet, not gated [V]). 800 images + masks: background, crushed, intact, impurity [V]. Use: multi-seed segmentation, broken and foreign-material classes. Risks: only 40 originals, each augmented 20 times [V], so **split by the 4-digit ID prefix**; a third-party HF card says the masks are model output, not human-verified [S, contradicts the paper].
3. **Indonesian soybean varieties, Mendeley c733bjz4m3 v3** (CC BY 4.0 [V]). 974 MB, flatbed scans of many seeds plus single-seed crops, 3 varieties [V]; 119 raw scans [S]. Use: second multi-seed segmentation test, sound class from another setup. Variety labels only.
4. **Healthy soybean seeds, Kaggle drgayatridhakad/soybean-seeds-healthy-dataset** (CC BY-SA 4.0 [V]). 1,197 images, 77 MB [V]. Sound class only, third setup; images not inspected; Kaggle login needed.
5. **Soybean Seeds (Lin) v6vzvfszj6 v6**: now includes "Part of the original soybean images", 5 multi-seed originals, 7.7 MB [V]. In-domain multi-seed test at almost no cost.
6. **Pea seed viability, Zenodo 18041269 / HF `Project-AgML/pea_seed_viability_classification`** (CC BY 4.0 [V]). 3,000 images, dead vs live [V]. Weak cross-species check only: viability is not a visible defect.

## Low value or unverified

- PulseLibrary, Mendeley kw7x5xyprh (CC BY 4.0, 3,123 images, 6.9 GB [V]): 6 pulse species, no defect labels.
- Bangladesh pulses, Mendeley skd9w9g5jm (CC BY 4.0, 2,956 images [V]): pulse type only; description claims ~17,500 images.
- Kaggle gonzaloferrermena lentils (CC BY 4.0, ~180 images, YOLO [V]): classes unknown without login.
- Roboflow Universe soybean projects (rafiullah-7lefe/soybean-damaged-seeds-detection, rafies-workspace-ul2aa/defect-soybean, fababeans/soyabeanseeddefect1, newideas/soybean-quality, ppe-detector/soybeans-feift): licence and counts unknown, pages returned 403; ppe-detector looks like a copy of Lin [S].

## Discarded

- Chickpea "Good and Bad", Mendeley zgph46p46f: sample images show plants, not seeds; byte-identical copies (md5).
- "Soyachans", Mendeley mzh9x3v2hd: looks like textured soy protein chunks, not soybeans; duplicates.
- 65rzpcgbp4 v3 (14/9/2026): still no annotation files (1,511 images listed).
- Copies of Lin (Kaggle aryashah2k, warcoder; HF Project-AgML/soybean_damage_classification), figshare 14305331 (paper figures), Kaggle mahbubahaque (opaque tfrecords), SoyNet w2r855hpx8 (leaves).

## Searched, nothing found

Damaged pea, lentil, faba bean, chickpea, common bean, cowpea, mung bean on Mendeley, Zenodo, figshare, Kaggle, Hugging Face, GitHub, Data in Brief and Scientific Data. No bruchid image set besides d97rjyk2tz. Papers with possibly unreleased data: Agronomy 2024 14(6):1098 (7 classes incl. insect-bitten; MDPI 403), Springer 2025 high-magnification soybean damage (~9,866 images [S], paywalled), Applied Sciences 2023 13(11):6425 (403).
