# SoyMate (formerly "idea 9"): photo-based quality control of pulse samples at intake (desk research findings)

Desk research, 30/10/2026. Complements `archive/research/plans/3_bruchids.md` and `archive/research/idea1_pea_protein_market.md` (I do not repeat what is already verified there except to correct it).

**Convention:** **[V]** I opened and read the source (page or PDF). **[F]** secondary source (press, commercial sheet, old note) or a figure I saw in a search-engine snippet without opening the page. **[NV]** not verified, hypothesis or my own calculation. I only cite as a source the pages I opened. Terres Inovia keeps blocking bots (403): I used the terresunivia.fr mirror, SEMAE, FranceAgriMer and the specifications on info.agriculture.gouv.fr.

---

## 0. TL;DR

1. **The problem exists and is well defined.** Today defects are counted **by eye, grain by grain**: the Codex for pulses literally says "Method of analysis: visual examination" for defects and discoloration [V]. The LABOSEM lab (SEMAE) counts bruchid-damaged grains over **200 lentil grains or 250-500 grains of protein crops**, with "trained staff with annual competence checks" [V]. Australia measures on **200 g** per truck [V]. A photo system that segments and counts replaces a task that is already visual: the fit is natural.
2. **But the photo has a physical ceiling that must be stated in the pitch.** The lentil and faba bean bruchid (bruche) is a **field** pest: the larva stays inside the grain and can emerge months later in the silo [V, Chery-Lagrange 2026]. In pea, the visual count detected **4.1% versus 11.8%** by dissection in the same lot (3.8% vs 13.5% in another) [V, LABOSEM 2022]. The photo sees holes and opercula, **not internal larvae**. Say "we detect visible damage", never "infestation".
3. **The direct competitor is Inarix (French, smartphone photo).** It does wheat, barley, maize; it claims to cover ~40% of French barley and >600 silos [V, Meta 2024]. **It already works on soybean**: a project in Canada with Grain Discovery and Sevita, 1.24 M CAD, March 2025 to March 2026, smartphone photo of soybean with a result in <20 s [V]. I found nothing from Inarix on pea, lentil or faba bean [V negative search]. Lab equipment (EyeFoss, Cgrain) is calibrated for cereals [V EyeFoss; F Cgrain]. **The "pulses for human consumption" gap is still open, but it is narrow and Inarix could close it.**
4. **Soybean as the PoC dataset is defensible only if framed well.** French soybean for human food exists (45 kt out of a total of 402 kt produced, FranceAgriMer 2026) [V], but the pest in the Indian dataset (pulse beetle, *Callosobruchus*) is tropical and a storage pest; I found no evidence that it matters in France [NV]. Honest framing: "soybean lets us train the mechanics (segment, classify, count); the product targets lentil, pea and faba bean, and we test it with photos taken here". There is also a **second, more useful soybean dataset** (5 classes: intact, stained, immature, broken, skin-damaged; 5513 images, CC BY 4.0) [V].
5. **Watch out for two hackathon rules.** (a) The topic list excludes "Insects" [V guide]. It probably refers to insects as food, but an idea that talks about "insects" should be clarified with a mentor on Friday. (b) The whole deliverable (code, model, own dataset, deck) is produced during the event; prior work is declared [V guide]. Buying pulses beforehand is buying supplies, not producing deliverables, but **do not take or label photos beforehand**, and declare it anyway [NV, interpretation].

---

## 1. Quality criteria and how they are measured today

### 1.1 Reference standard: Codex CXS 171-1989 (pulses for direct human consumption)

I read the Spanish version (adopted 1989, revised 1995) [V]. It covers lentil, pea, chickpea, faba bean (*Vicia faba*), beans (*Phaseolus*) and cowpea. **It does not cover soybean** (it defines it as an oilseed because of its fat content) nor "pulses intended to be graded and packed in a factory" (that is, the raw grain arriving at the cooperative is not formally under this standard) [V].

| Factor | Limit | Method |
|---|---|---|
| Max. moisture (temperate climate / long term) | lentil 16/15%, pea 18/15%, chickpea 16/14%, faba bean 19/15% | n/a |
| Foreign matter | ≤1%, of which ≤0.25% mineral and ≤0.10% dead insects or fragments | n/a |
| Seeds with serious defects (cotyledon attacked by pests, mold, cotyledon stain) | max. 1.0% | **Visual examination** |
| Seeds with minor defects (immature, extensive seed-coat stain, shriveled, broken) | max. 7.0%, of which broken ≤3.0% | **Visual examination** |
| Discolored seeds | max. 3.0% | **Visual examination** |
| Seeds of a different color | max. 6.0% | **Visual examination** |

Note: there may be amendments after 1995 that I did not review [NV].

### 1.2 France: Terres Inovia quality survey (pois, féverole, lentille, pois chiche: pea, faba bean, lentil, chickpea)

- Since 2015 Terres Univia has commissioned Terres Inovia to run a quality survey of pea and faba bean **at collection**, with samples sent by the collecting organizations [V, Biarnès/SEMAE presentation 2019].
- Criteria measured: protein (NIR for pea, Dumas for faba bean), moisture, color, **broken and "splittés" (split) grains, stained grains, insect-attacked grains, sprouted grains, foreign material before sorting** [V].
- Lots are classified into 4 classes by visual criterion: **0 / <1% / 1-10% / >10%** [V]. The 1% threshold is the one the 2025 pea sheet associates with "utilisables en alimentation humaine" (usable for human food) [V via `idea1_pea_protein_market.md`].
- Faba bean 2025: "La majorité des lots reçus présentent moins de 1 % de graines bruchées" (most lots received have less than 1% bruchid-damaged seeds); foreign material <1% in 80% of lots; lots "sont systématiquement nettoyés" (are systematically cleaned) before being sold; analysis at the Ardon laboratory (Orléans) [V, terresunivia.fr 9/4/2026].
- Lentil 2025: 60 samples (98% green), bruchid damage measured in 40, lots with >30% and up to 50% [F, search-engine snippet of the Terres Inovia note]; mean 24.4% [V via `3_bruchids.md`].
- Chickpea 2025: 58 samples, mostly Kabuli; visual criteria "attaqués, tâchés, splittés, impuretés" (attacked, stained, split, foreign material); size (>7 mm) is a key commercial criterion; the destination is 100% human food [F, snippet of the sheet, I could not open the PDF].
- I did not find whether Terres Inovia uses X-rays for bruchids [NV]. The literature review on X-rays and NIR describes them as expensive [F].

### 1.3 How bruchid damage is counted: visual vs dissection (LABOSEM / SEMAE, 2022) [V]

| | Visual method | Dissection |
|---|---|---|
| Sample | lentil: 200 grains; protein crops: 250 or 500 grains | 200 (4×50) or 400 (8×50) grains, soaked |
| What counts as bruchid-damaged | hole without bruchid, hole with bruchid, **unopened operculum** | the above + non-emerged bruchids + larvae |
| Result | "taux d'émergence à un instant T" (emergence rate at a given time T) | "taux d'infestation du lot" (lot infestation rate) |
| Drawback | does not see non-emerged bruchids | destructive, slow |

Comparison on the same lots: pea 4.1 vs 11.8% and 3.8 vs 13.5%; faba bean 4.8 vs 6.8% and 3.9 vs 6.4%; lentil 0.4 vs 0.5% and 0.5 vs 1.1% [V]. Bruchid damage also has to be distinguished from that of "tordeuses" (tortrix moths) [V].

Biology that explains the gap: in Europe bruchids are univoltine; some of the larvae complete development and emerge at the end of summer, and others "remain in the grains for several months until emergence in silos" [V, Chery-Lagrange et al. 2026, PMC13158440]. That paper measured damage in lentil by crushing and in faba bean by dissecting 25 grains per point (100 per field) [V].

**Consequence for SoyMate:** the photo can replace the visual method (which is the one used at intake), not dissection. The closed operculum (the circular "window") is visible and is the most valuable and hardest class.

### 1.4 Specifications and sheets for finished product (after sorting)

| Product | Criterion | Source |
|---|---|---|
| IGP Lentilles vertes du Berry (17/11/2025) | moisture <16%; foreign matter ≤0.2%; "brisées ou cassées" (chipped or broken) grains <0.8%; brisures (fragments) <0.2%; damaged grains (oxidized, degenerated, sprouted) <0.8%; **unacceptable (bruchid-damaged, stained, moldy) <0.1%**. Definitions: "brisée" = more than 1/8 of the grain missing; "cassée" = cotyledons separated. Non-compliant lots "sont retriés ou déclassés" (are re-sorted or downgraded) | [V] |
| AOP Lentille verte du Puy (2018) | 3.25-5.75 mm; moisture ≤16%; ridées (shriveled) and germées (sprouted) excluded; corps étrangers (foreign bodies) ≤0.5%; organoleptic check "examen visuel et olfactif" (visual and olfactory examination) | [V] |
| Sabarot, Lentilles vertes du Berry (PF02978, 2025) | unacceptable (bruchées, tachées, blanches: bruchid-damaged, stained, white) <0.1%; brisures <0.2% | [V, technical sheet on a mirror] |
| Sabarot, Lentille verte du Puy (PF02965, 2022) | brisures <2 mm <1%; graines impropres (unfit seeds) <1% | [V] |
| Sabarot, Lentilles vertes ZRP (PF03486, 2021) | brisures <0.5%; impropres <1% | [V] |
| Sabarot, Méli-mélo (PF01616, 2024) | impropres <1%; brisures <3%; insects: none | [V] |

Note: the "<1% Sabarot" is a specification of the **packaged product**, not of raw grain intake [V]. Sabarot's generic green lentil lists origin "France, Canada, Espagne, Ukraine" [V, Pomona sheet 34404].

### 1.5 Commercial intake thresholds (what I found)

- **I did not find any public Incograin or Synacomex text** with tolerances for pulses [NV, negative search]. This has to be asked of a mentor or a cooperative.
- Cap Seine (2017): for faba bean for human consumption "il faut moins de 5 % de grains bruchés ou operculés, c'est très difficile à faire en France" (you need less than 5% bruchid-damaged or operculated grains, which is very hard to achieve in France), and that is why they sold all their faba bean as animal feed [F, Réussir 1/5/2017, opened]. Noriap: "Nos clients veulent du pois sans aucune trace de céréale" (our customers want peas without any trace of cereal) [F, same article].
- Egypt requires 1% bruchid-damaged in faba bean and France "ne peut garantir que 3 % d'habitude" (can usually only guarantee 3%) [F, La Dépêche/Réussir 1/3/2016, opened]. Today the top destination of exported faba bean is Norway (44 kt, 72% of the total exported) [V, FranceAgriMer 2026]; I did not find whether it is for human consumption [NV].
- **Australia (process reference, not market):** lentil intake 2025/26 at T-Ports: 200 g sample; total defective ≤4% (grade 1), 5% or 8% by weight; "severely damaged" max. 1 per 200 g; foreign material ≤3%; poor color ≤1%; large insects ≤15 per 200 g; foreign seeds counted by type [V]. It is exactly the kind of count a photo can assist.
- Canada (CGC, lentil): "split" = less than 3/4 of the grain or less than half of the seed coat intact; stains and "heated" are assessed by eye against visual standards; the page does not give a sample size [V].

### 1.6 Who does it and how long it takes

- At French intake, the "agent de silo" (silo operator) or réceptionnaire (intake officer) does the agréage (grading): moisture, test weight, foreign material and protein (NIR, "infralyseur") [F, snippets of the RNCP sheet and of a presentation by the Creully coop; I did not open the pages].
- **I did not find times per sample or analysis costs** for pulses at intake [NV]. Hypothesis to check with a mentor: separating and counting 200-500 grains by hand takes on the order of 5-15 min, and at peak harvest it is done on composite samples rather than truck by truck [NV].
- The machine-vision literature on pea says that current grading is "subjective" and based on appearance (McDonald et al. 2016) [V, abstract on Europe PMC].

---

## 2. Soybean for human food in France

- Production 2024/25: **402 kt** (7% of oilseeds); **consumption as human food: 45 kt** [V, FranceAgriMer, fiche filière oléagineux (oilseed sector sheet) 2026]. That is ~11% of the volume [NV, calculation]. The Veblen institute says that market is almost entirely French-origin soybean [F, snippet].
- Oilseed collectors: 418, of which 124 cooperatives (2024/25) [V].
- Triballat Noyal (Sojasun) set up its own non-GMO French soybean filière (supply chain) in 1995 [F, search-engine snippet]; the company is now called Olga [F]. I did not verify Nutrition & Santé or "Sojinal" [NV].
- Food-grade soybean specifications: I did not find a public French spec. References: the US standard defines "split" as more than 1/4 of the grain missing and measures the % of grains with a clear hilum (relevant for tofu and soy drinks) [F, USDA snippet]; the East African standard limits pest-damaged grains to 0.3/0.8/1.5% by grade [F, snippet].
- **Dataset pest vs France:** the Mendeley dataset (VIT Pune, India) is about "pulse beetle", without naming the species; version 2 from July 2026, CC BY 4.0, healthy vs infested classes, annotations of eggs and holes [V]. *Callosobruchus* is a warm-climate storage pest; the soybean pests reported in French bulletins are field pests (pyrale du haricot (bean pod borer), stink bugs, heliothis) [F]. I found no mention of bruchids in stored soybean in France [NV, negative search]. **Conclusion: the "bruchid hole" damage looks visually similar across species, but the biological context does not transfer.**
- **More useful alternative soybean dataset for the PoC:** "Soybean Seeds" (Mendeley, Lin et al., Jiangsu Univ. of Sci. & Tech. + Nanjing Agricultural Univ., v6 30/5/2023): 5513 single-seed images (227×227) in 5 classes according to GB1352-2009: intact, spotted, immature, broken, skin-damaged; CC BY 4.0 [V]. It covers broken and stained, which in pea are the limiting criteria (broken <1% in only 55% of lots) [V via idea 1].

---

## 3. Competitors and prior work

| Player | What it does | Pulses | Price | Status |
|---|---|---|---|---|
| **Inarix** (France) | PocketLab app: smartphone photo of a sample, variety, protein, test weight, moisture, broken grains | Wheat, barley, maize; **soybean in development** (Canada, 2025-26) | Not public | [V] inarix.com, Meta 6/12/2024 (DINOv2, ~40% of French barley, >600 silos in >10 countries), Protein Industries Canada, Terre-net advertorial 26/5/2025 (5 years with coops and négoces (grain traders): EMC2, Ceresia, Bodin, Calipso) |
| **FOSS EyeFoss** | Lab image analyzer: 10,000 grains or half a liter in 4 min, damaged grains and foreign matter | Wheat, barley, durum | On quotation | [V] fossanalytics.com |
| **Cgrain Value** (Sweden, 30% Lantmännen) | Imaging for visual quality | Wheat, rye, barley, oat | Not found | [F] |
| **GrainSense** (Finland) | Handheld NIR: protein, moisture, oil | Wheat, barley, rapeseed (2019-22) | 3900 € excl. VAT + 250 €/year | [V] Terre-net |
| SeedCount, VIBE QM3, Videometer, Seed-X (GeNee) | Lab image or multispectral analyzers, or AI sorters | SeedCount lists lentil; the others have no evidence on pulses | n/a | [F] or [NV] |
| Agriculture Victoria / GRDC "Pulse Bio" | Image algorithms for size, shape, color and defects in lentil, chickpea, pea, faba bean | Yes | n/a (research) | [F], GRDC pages returned 403 |

Academic literature:
- McDonald, Panozzo, Salisbury, Ford (PLoS ONE 2016): pea, multispectral camera + laser on a belt; LDA by market grade 87% (calibration) and 77% (validation); >97% sound vs defective [V, abstract].
- arXiv 2507.20531 (2025): green lentil, YOLOv8 detection + classification into 6 classes (Good, Yellow, Broken, Peeled, Dotted, Reject), 87.2% separation, but only 8 g/min [V, abstract].
- Shahin & Symons (2001): machine vision with a flatbed scanner for lentil grading [F, snippet].
- I found no public dataset of **defects** in lentil, pea, faba bean or chickpea (the lentil ones are about varieties or plant diseases) [V negative search on Mendeley].

**Possible positioning:** "Inarix for pulses for human consumption, focused on the criteria that decide human food vs animal feed (broken, bruchid-damaged, stained) rather than protein" [NV]. Risk: Inarix already has the silo base and is moving into soybean.

---

## 4. Business

- **Protein-crop collectors: 477 (117 cooperatives, 360 négociants (traders)) in 2024/25**; ~12,400 delivering producers in 2024; **502 kt of pea and faba bean collected** (64% of production) [V, FranceAgriMer fiche protéagineux (protein crop sheet) 2026].
- Domestic uses 2024/25: **146 kt for human consumption** (5-season average: 155 kt) against 62 kt for animal feed [V]. Exports: 200 kt of pea (74% to the EU, Belgium 45%) and 61 kt of faba bean (Norway 72%) [V].
- Value of grading a lot correctly (illustrative calculation, [NV]):
  - Pea: human food premium +30 €/t (250 vs 280 €/t, Terres Inovia 2025 guide) [V via idea 1]. A wrongly graded 28 t truck: ~840 €.
  - Lentil: T4 price 806-873 €/t [V via plan 3]. If the reject is worth ~231 €/t (faba bean proxy, [NV]), sending 1 t of food-grade lentil to animal feed costs ~575 €/t; mixing 28 t of heavily bruchid-damaged grain with a clean lot can force re-sorting the whole silo [NV].
- **Who pays:** the cooperative's quality or collecte (collection) manager (allotissement (lot allocation) at intake) and, later, the packer (Sabarot, etc.) who today checks after sorting. I did not find current costs of manual inspection [NV]. Tool price reference: GrainSense 3900 € + 250 €/year [V]; Inarix does not publish a price.
- Counterargument for the Q&A: lentil and faba bean are always cleaned and sorted before being sold [V faba bean; V Berry specification], so the value is not "detect in order to throw away" but **quickly deciding which cell and which contract each truck goes to**, and documenting the réfaction (price deduction) with the grower [NV].

---

## 5. Event logistics

### 5.1 Rules

- Venue: Agro Paris-Saclay campus, 22 Place de l'Agronomie, Palaiseau. Opens Friday 30/10 17:30, closes Sunday 1/11 14:00; the campus closes at 23:00 on Friday and at 18:00 on Saturday [V guide].
- "Things you cannot do before the start": build the solution, the code, the model, the prototype, specific results or the deck; every deliverable is produced during the event; prior datasets or research are declared [V guide].
- **Buying pulses beforehand:** the guide does not mention it. It is a supply, not a deliverable [NV, interpretation]. Recommendation: buy, yes, but **do not photograph or label anything before Friday 17:30**, declare "materials bought on X at Y" in the submission and, if in doubt, ask the organizers on Friday (the guide itself asks for that) [V guide for the last point].
- Sunday 1/11 is a public holiday (Toussaint, All Saints' Day) and on Saturday the campus closes at 18:00: purchases have to be done on Friday before arriving or early on Saturday [NV calendar].

### 5.2 Where to buy (I did not verify specific shops, all [NV])

| Pulse | Most likely place |
|---|---|
| Green lentil (incl. du Puy / Berry), red lentil, split pea (pois cassés), chickpea | Any supermarket (Carrefour, Monoprix) or Biocoop/Naturalia; in vrac (bulk) at organic shops |
| Whole dried pea (pois secs entiers) | Rare in supermarkets; Indian shops (matar, dried green/white peas) in La Chapelle or Faubourg Saint-Denis |
| Dried faba bean (fèves sèches, whole or peeled) | North African or Middle Eastern shops (Belleville, Barbès), sometimes at Biocoop |
| Dried yellow soybean | Asian supermarkets (Paris 13e) or organic shops in vrac (bulk) |
| Split red lentil, chana dal (split chickpea) | Indian shops |

Key detail: lentils packed in France have already been sorted (<0.1% to <1% unacceptable depending on the product) [V Sabarot sheets], so **in a 500 g bag of green lentils (~10,000 grains, thousand-grain weight ~50 g [NV]) you will find a few dozen bruchid-damaged grains at most**. The best yield: organic lentils in vrac (bulk), of smaller size or "ZRP", and checking grains one by one.

### 5.3 Getting real bruchid damage

- **Antoine Gardarin** (contact author of the INRAE dataset of bruchids in lentil and faba bean) is a maître de conférences (associate professor) at AgroParisTech, **UMR Agronomie, Palaiseau**: the same campus as the hackathon [V INRAE page "Mots de l'agronomie"; V authorship in `idea3_bruchids.md`]. He is the best request: samples of bruchid-damaged grains kept from the trials [NV whether they exist].
- Terres Inovia is listed as a track resource [V guide]; if there is a Terres Inovia mentor, ask for grains from the quality survey (Ardon laboratory) [NV].
- Plan B: synthetic damage (hole with a needle or a mini drill of ~1-2 mm in lentil and faba bean). **It must go in a separate "synthetic_hole" class, never mixed with the real test set, and be declared in the deck** [NV, recommendation]. Broken grains (cutting or splitting grains), stained grains (hard to simulate well) and foreign material (adding wheat, small stones, seeds of another species) are easy to get and are honest because they are real damage made by hand; it still has to be stated.

### 5.4 Photo protocol (~2 h for 2-3 people) [NV, own design]

1. **Setup (15 min):** matte background of a contrasting, uniform color (dark blue or black for green lentil and pea; if only one is used, blue card works for all). Phone fixed on a stand or stack of books at ~25-30 cm, perpendicular. Diffuse light: a window without direct sun or two lamps at 45° with baking paper; no flash. Lock exposure and focus in the camera app. **Scale reference**: a 1 € coin (23.25 mm) or a ruler in a corner, plus a color or gray card if available.
2. **Grains per photo:** 30-80 separated grains that do not touch (classic segmentation with threshold + contours works well like that); a few photos with touching grains to test watershed. For the final demo, one "realistic" photo of ~200 grains (the LABOSEM visual sample for lentil) [V size].
3. **Classes** (aligned with the standards): sound, broken/cassé (separated cotyledons), brisé (chipped, >1/8 missing), bruchid-hole, bruchid-operculum (window), stained, foreign material/other species, (synthetic kept separate). Each training photo with **a single class** speeds up labeling: the label is inherited from the folder and automatic segmentation provides the boxes.
4. **Quantity:** aim for 100-200 grains per class and per species (2-5 photos per class), plus 5-10 mixed evaluation photos with a reference manual count. With 2 species (green lentil and pea) × 6 classes × 4 photos ≈ 50 photos, ~1 h of photos with two people separating grains.
5. **Labeling (30-45 min):** since the photos are single-class, a script is enough (segment and crop). To fix errors or label the mixed ones: **Label Studio** or **CVAT** locally (free, private data). **Roboflow** on the free plan makes projects public on Roboflow Universe [F, snippets from Roboflow docs and pricing]: use it only if the team accepts publishing the dataset.
6. **Split:** test by photo (or by source bag), never by grain, to avoid leakage.

Infrastructure note: the AWS sandbox has no GPU (see skill `aws-hackathon-sandbox`), so a lightweight pipeline (classic segmentation + embeddings from a pretrained model + linear classifier) is better than training a large detector [NV].

---

## 6. Questions for mentors (Friday evening)

1. Does the excluded "Insects" topic cover a project detecting insect damage on grains? (almost certainly not, but ask).
2. At a French cooperative, are broken and bruchid-damaged grains counted **truck by truck** or on composite samples per cell? How long does it take and who does it?
3. What intake tolerances do the contracts for food-grade pea and lentil set (Incograin, contracts with packers)? Is there a réfaction (price deduction) grid by % bruchid-damaged?
4. Does Gardarin or someone at UMR Agronomie have real bruchid-damaged grains to lend?
5. Does Inarix already do pulses? (if a mentor knows, it changes the positioning).

---

## 7. Sources opened

- Codex CXS 171-1989, Spanish version, 1995 revision: https://www.fao.org/input/download/standards/56/CXS_171s.pdf
- LABOSEM/SEMAE, "Analyse de grains bruchés", JIT 10/3/2022: https://www.semae.fr/uploads/10-2022-jitcerpro_methode-grains-bruches_FP_CEK_MB.pdf
- Terres Inovia (Biarnès), bilan qualité pois et féverole (pea and faba bean quality review), 2019: https://www.semae.fr/uploads/16-Enquete-qualite-pois-et-feverole-2018.pdf
- Terres Univia, faba bean quality 2025: https://www.terresunivia.fr/l-interprofession/actualites/qualite-des-graines-de-feverole-une-bonne-teneur-en-proteines-en-2025
- IGP Lentilles vertes du Berry specification: https://info.agriculture.gouv.fr/boagri/document_administratif-40f9105a-26b0-47e0-9799-f0161c3a8df5/telechargement
- AOP Lentille verte du Puy specification: https://info.agriculture.gouv.fr/boagri/document_administratif-3b601fa7-0c84-48e9-b94b-bffff44295fb/telechargement
- Sabarot sheets (mirror): https://wyapkgisccvpsoiyfieb.supabase.co/storage/v1/object/public/mirror-documents/docs/ft/3111952029784.pdf , .../3111952029654.pdf , .../3111952034863.pdf , .../3111952016166.pdf ; Pomona sheet: https://cdn.api.groupe-pomona.fr/public/products/0034404/branch/es/medias/lentilles-vertes-en-sac-10-kg-sabarot_0034404_es_technical.pdf
- T-Ports, Lentil Receival Standards 2025/26: https://tports.com/wp-content/uploads/2025/09/12.TEM_.47-Lentil-Receival-Standards-2025_2026.pdf
- CGC, lentil grading factors: https://www.canada.ca/en/grain-commission/services/grain-quality/official-grain-grading-guide/18-lentils/grading-factors.html
- Chery-Lagrange et al. 2026 (Europe PMC full text): https://pmc.ncbi.nlm.nih.gov/articles/PMC13158440/
- Réussir 1/5/2017 (Cap Seine, Noriap): https://www.reussir.fr/grandes-cultures/lalimentation-humaine-pour-relancer-des-productions-hesitantes
- La Dépêche/Réussir 1/3/2016 (Egypt): https://www.reussir.fr/ladepeche/la-feverole-francaise-en-difficulte-sur-legypte
- FranceAgriMer, fiche filière protéagineux 2026: https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf
- FranceAgriMer, fiche filière oléagineux 2026: https://www.franceagrimer.fr/sites/default/files/2026-02/18_FICHE_FILIERE_OLEAGINEUX_2026.pdf
- Mendeley, soybean pulse beetle: https://data.mendeley.com/datasets/d97rjyk2tz
- Mendeley, Soybean Seeds (5 classes): https://data.mendeley.com/datasets/v6vzvfszj6
- Inarix: https://www.inarix.com/ ; Meta/DINOv2: https://ai.meta.com/blog/inarix-agricultural-supply-chain-meta-dino-v2/ ; Protein Industries Canada: https://proteinindustriescanada.ca/projects/phone-grain-quality-tool ; Terre-net 2025: https://www.terre-net.fr/publi-information/article/882858/qualifier-les-grains-des-la-sortie-de-moissonneuse
- FOSS EyeFoss: https://www.fossanalytics.com/products/eyefoss
- GrainSense (Terre-net): https://www.terre-net.fr/materiel-agricole/recolte-fenaison/article/grainsense-connaitre-la-teneur-en-proteines-directement-au-champ-208-148616.html
- McDonald et al. 2016, PLoS ONE (metadata and abstract via Europe PMC): PMC4866801
- arXiv 2507.20531 (abstract)
- INRAE, Mots de l'agronomie, Antoine Gardarin: https://mots-agronomie.inrae.fr/index.php/Antoine_Gardarin
- Roboflow (public plan): search-engine snippets only, not opened
- Participant guide: `event/participant_guide.txt`
