# SoyMate: pulse quality control from a single photo. Full project context

Self-contained document for tackling the project at Hack the Fork Paris 2026. The project is **SoyMate** (internally "idea 9"). This document is meant to let an AI agent or a team member answer any question about the project without reading other files. It is the **single source of truth**: every fact has its source next to it (`[S#]`, full list in §17) and its confidence tag. Fine details (audits, plots) are in `research/`.

Written: 30/10/2026, before the event. Last source review: 30/10/2026.

**Confidence tags:**
- **[V]** verified today by opening the primary source (PDF, official page, API, dataset file) and reading the exact figure.
- **[F]** comes from a secondary source, from a source that was only partially read, or from our own audit that was not recomputed today.
- **[NV]** not verified: estimate, interpretation or own calculation. Own calculations say "own calculation" and list their inputs.

**Rule for agents:** if a question cannot be answered with a tagged fact from this document, say so; do not fill in from memory. When quoting in the pitch, use the wording here (it says exactly what the source says: sample, year, crop, country).

### Changes in this revision (30/10/2026)

- 30/10/2026: document translated to English; content unchanged.
- Lentil: "one in four lentils had a bruchid" → "the analysed lots had on average 24.4 % bruchid-damaged grains (40 samples, min. 1.0, max. 75.5)". The 2021-2025 series was checked by eye on the PDF chart (before, it was an inferred ordering).
- Insecticides: "no authorised insecticide is left for lentil" → "no insecticide remains authorised **in the field** against beetles (bruche) on dry pulses since 31/7/2024; **in storage** there are authorised products" (ANSES e-phy catalogue).
- Human/feed thresholds: the "1-3 %, feed 10 %" from the Teagasc poster (faba bean, Ireland) was separated from the French sources: Incograin/RUFRA contracts (2003): addendum VII bis human food max. 1 % bruchid-damaged; human-food export pea 3 %, faba bean 1.5-3 %; animal feed has no specific limit for bruchid-damaged grains, only 10 % for "cassés + bruchés + pelliculés" combined. Egypt (1 %) and the Frontiers article (France: 3 % / 10 % in faba bean) were added.
- "French intake contracts: no public text found" → there is a 2003 text (Perspectives Agricoles n°292); the current ones are still not found.
- FranceAgriMer: 502 kt collected and soybean (402 kt produced, 45 kt human food) are **2020/21-2024/25 averages**, not "per year" or "2026". 146 kt human food and 477 grain collectors are indeed 2024/25.
- Pea premium: it is the **indicative price** used by the Terres Inovia 2025 guide in its margin calculation (250 vs 280 €/t), not an observed premium.
- Lentil price: 806-873 €/t = average price paid to the producer (conventional, cumulative to Q4) in 2025/26 and 2024/25.
- Australia: "200 g per truck" → intake standard of T-Ports (South Australia) that expresses tolerances per 200 g; sampling per truck does not appear in the document.
- LABOSEM: no longer called "official laboratory"; the visual vs dissection comparison is 2 pea lots of 200 grains each.
- AOP Puy: the specification is the one approved by arrêté of 31/3/2017 (it used to say 2018).
- Sabarot: the <1 % is "graines impropres à la consommation" in 3 product sheets (Puy, ZRP, Méli-mélo); in the Berry one the limit is <0.1 % unacceptable grains.
- Inarix: the soybean project in Canada is to identify soybean **variety** by photo, not damage. EyeFoss is not "lab bench": the page talks about intake stations.
- Hackathon: "Insects (as food)" becomes an interpretation [NV]; "no agronomist on the 2025 jury" was removed (no source). Venue and date of the 2025 edition were added.
- "There is no public dataset of damaged pulses" goes from [V] to [NV, own negative search].

---

## 1. Summary

**What it is:** a tool for the intake technician of a cooperative or grain collector. They take a phone photo of a sample of pea, lentil or faba bean on a plain background, and the system:
1. separates each grain in the photo;
2. classifies each grain: sound, broken/split, insect-holed (bruchid), stained, foreign material;
3. computes the percentage of each defect with its confidence interval;
4. says whether the lot meets a selectable human-food threshold or goes to animal feed.

**Why:** pulse defects are assessed by visual examination (that is what the Codex pulses standard sets [S5] [V]) and in the laboratory they are counted grain by grain on 200 to 500 grains [S6] [V]. The limit on bruchid-damaged grains (grains bruchés) for human food is low (1 to 3 % depending on contract and destination [S16] [V]) and French lentil had in 2025 its worst bruche (bruchid beetle) year since the survey began [S8] [V]. That this is "the decision that weighs most on the producer's income" is our hypothesis [NV]. Track 3 asks to produce more pulses for human food and for producers to make money from it [S1] [V].

**How it is built without pulse data:** we found no public dataset of damaged pulses in RGB photos [S38] [NV, own negative search]. It is trained on the best open dataset of insect damage (soybean), which we audited and re-split [S36], plus cereals (GrainSet) [S31], and transferred to pea and lentil with about 50 of our own photos taken at the event. The centrepiece of the pitch is a **transfer curve**: how well it works without fine-tuning and how much it improves with 5, 10, 25 and 50 labelled grains per class.

**Framing:** the product and the demo are about **French pea and lentil**. Soybean appears only as training data, on the "how we built it" slide.

---

## 2. Hackathon context

**Event:** Hack the Fork Paris 2026, organised by Hack the Fork and hosted by AgroParisTech, at Campus Agro Paris-Saclay, 22 Place de l'Agronomie, 91120 Palaiseau. From Friday 30/10 17:30 to Sunday 1/11 14:00 [S1] [V]. Teams of 2 to 5 people [S1] [V]. Ours has 3; one is a master's student in ML and computer vision (MVA, ENS Paris-Saclay) [team fact].

**Chosen track:** Track 3, "Protein sovereignty, from French fields to the proteins of tomorrow". Question: how can AI help producers and regions produce the plant proteins the French will eat, and generate income from them? Track context: pulses cover ~4 % of French agricultural area and the goal is to double it by 2030 [S1] [V].

**Schedule** [S1] [V]:

| Day | Time | What happens |
|---|---|---|
| Fri 30/10 | 17:45-18:45 | Welcome and team building (Forum) |
| Fri 30/10 | 18:45-20:45 | Talks; Workshop #1 "The Alternative Protein Sector" from 20:00 to 20:45 |
| Fri 30/10 | 20:45-23:00 | Team brainstorming. **Declare the track before 23:00.** The campus closes at 23:00 |
| Sat 31/10 | 8:30-9:30 | Welcome and breakfast |
| Sat 31/10 | 9:30-10:15 | Workshop #2 "AI at the heart of innovation" |
| Sat 31/10 | 10:15-13:00 and 14:00-18:00 | Team work. **The campus closes at 18:00**; at night work happens off-site |
| Sun 1/11 | 8:30-10:00 | Work and submission. **Submit before 9:30**: pitch PDF (official template) with a link to the code or demo, plus the online project sheet |
| Sun 1/11 | 10:15-12:00 | Pitches: **strictly 4 minutes + 2 of questions**. Structure: problem, solution, live demo or prototype, scaling |
| Sun 1/11 | 12:00-12:30 | **Back up everything** (AWS accounts are closed after the event) |

Sunday 1/11 is a public holiday in France (Toussaint) [S4] [V].

**Jury criteria (each juror scores 1 to 10 per criterion, weighted)** [S1] [V]:

| Criterion | Weight | What it looks at |
|---|---|---|
| Impact and sustainability | 30 % | Contribution to a more sustainable and resilient food system; benefits proportional to the evidence |
| Scientific and technical rigour | 20 % | Data, sources, quality of assumptions; acknowledging limits |
| Appropriate use of AI | 20 % | AI is essential, not an add-on; the team explains what the model does |
| Economic viability | 20 % | Concrete user or customer, value proposition, business model, adoption path |
| Execution and pitch | 10 % | Solid demo, coherent narrative, firm answers |

**Rules that matter** [S1] [V unless stated]:
- Nothing may be built before the start: solution, code, model, prototype, challenge-specific results or final deck. Researching the sector and exploring open resources is allowed (and recommended).
- Every prior resource (code, research, datasets, designs, pretrained models) is declared at submission.
- Separate what is measured or sourced, what is assumed and what is synthetic. Citations invented by an LLM are detected and lower the rigour score.
- Excluded topics: "Insects", products with animal-origin ingredients, **animal feed** (including replacing imported soybean for livestock) and projects without a working demo. The guide does not clarify the scope of "Insects"; that it refers to insects as food and not to detecting insect damage is our interpretation [NV]: confirm with a mentor on Friday.
- Intellectual property is 100 % the team's.
- Prizes: $2,000, $1,000 and $500 [S1] [V].

**What the jury rewarded in 2025** (first edition, École 42, Paris, 13-14/12/2025, 21 teams) [S3] [V]: 1st Ardoise (AI platform to help public canteens adopt plant-based menus and comply with EGAlim), 2nd ReaKt (bioreactor autopilot with predictive control for fermentation; the 2026 guide confirms it is the runner-up and that it is incubated at Genopole [S1] [V]), 3rd BlendIn (AI recipe redesign to lower cost, emissions and animal ingredients). Our reading: all three have a concrete user and a legal or economic pain; none is on the farm side [NV, interpretation; the official 2025 report was not accessible].

**AWS infrastructure (event sandbox)** [S2] [V]: us-east-1 region only, account lasting up to 72 h and destroyed at the end with no recovery, **no GPU instances** (EC2 below 6xlarge), closed list of Bedrock models, uploading personal or sensitive data forbidden, backup required. Design consequence: the pipeline has to train on CPU.

---

## 3. The problem and domain data

**How it is measured today:**
- **Codex Alimentarius CXS 171-1989 (pulses for direct human consumption; adopted 1989, revised 1995):** method for analysing defects and discolouration: "visual examination". Serious defects (cotyledon attacked by pests, traces of mould, stained cotyledon) max. 1.0 %; minor defects max. 7.0 %, of which broken max. 3.0 %; foreign matter max. 1 % (≤0.25 % mineral, ≤0.10 % dead insects or fragments) [S5] [V]. Note: the standard **does not apply** to pulses "intended for further sorting and packing in a factory" nor to those for animal feed, so it does not govern the raw grain entering the cooperative; it is a reference [S5] [V]. We did not review amendments after 1995 [NV].
- **LABOSEM** (seed testing laboratory; presentation at the cereals and protein crops technical day of 10/3/2022, hosted on semae.fr): offers two analyses of bruchid-damaged grains. Visual: 200 grains for lentil, 250 or 500 for protein crops (protéagineux); counts holes without bruche, holes with bruche and **unopened opercula**; gives the "emergence rate at a time T". Dissection: 200 or 400 soaked grains; additionally counts non-emerged bruches and larvae; gives the "infestation rate of the lot". It is done by "trained staff with annual competence checks" [S6] [V].
- **Terres Inovia quality survey** (samples taken at the producer's delivery to the grain collector): for visual criteria, each lot is put into 4 classes: absent, <1 %, 1-10 %, >10 % [S7] [V for pea and faba bean, 2019] [S8] [V for lentil, 2025].
- **Australia, as a process reference:** the 2025/26 lentil receival standard of T-Ports (South Australian operator) sets tolerances in % by weight (total defective max. 4 %, 5 % or 8 % depending on grade; poor seed coat colour max. 1 %) and in counts per 200 g ("severely damaged" max. 1 per 200 g; large insects max. 15 per 200 g) [S10] [V]. The document refers to another standard for sampling; it does not say "per truck" [S10] [V].
- How long manual counting takes in a cooperative and whether it is done truck by truck: not found [NV]. Ask a mentor (§13).

**How much damage there is:**
- **Lentil (Terres Inovia survey, 2025 harvest):** 60 samples analysed (98 % green lentil); the % of bruchid-damaged grains was measured on 40. **Mean 24.4 % bruchid-damaged grains per lot**, min. 1.0 %, max. 75.5 %, standard deviation 18.7. It is "the highest since the launch of the lentil quality surveys". By basin: Centre-Ouest 36.8 %, Sud-Ouest 22.3 %, Nord-Est 18.6 %, Sud-Est 15.4 %. There are samples above 30 % and up to 50 % that pull the mean up [S8] [V]. Series of means from the sheet's chart: 11.6 % (2021), 15.3 % (2022), 10.3 % (2023), 14.5 % (2024), 24.4 % (2025) [S8] [V, read from the chart]. The same sheet gives 2.8 % broken grains ("cassées") in 2025 [S8] [V].
- **Insecticides on lentil:** in the e-phy catalogue (ANSES), the only insecticide authorised in the field for "Légumineuses potagères (sèches) / Coléoptères phytophages" (CYTHRINE MAX, cypermethrin) is withdrawn, with a use deadline of 31/7/2024; no other remains for that use. In **storage** there are authorised products for beetles on dry pulses: deltamethrin + piperonyl butoxide "sur lentilles" (K-OBIOL ULV 6, BANK, DELTAGRAIN ULV) and CO2 in a closed enclosure [S19] [V, catalogue of 27/10/2026]. That the lentil bruche falls under the "phytophagous beetles" use is our interpretation [NV, reasonable].
- **Pea (Terres Inovia survey, 2025 harvest, 85 samples):** 55 % of lots have <1 % broken or "splittés" grains and "are usable in human food"; 86 % have <1 % insect-attacked grains; 96 % have <1 % stained grains. The sheet's conclusion: "around 60 % of lots could meet the criteria required in human food" and all are fit for animal feed. Of the half of the lots with a declared destination, 90.5 % went to animal feed and 9.5 % to human food [S9] [V]. Our reading: in pea 2025 the criterion that excludes the most lots is broken grains, not insects [NV, derived from S9 figures].

**Thresholds separating human food from animal feed (each with its scope):**
- **France, contracts (Perspectives Agricoles n°292, July-August 2003):** Incograin/RUFRA contracts, addendum VII (animal feed, pea and faba bean): "grains cassés, bruchés et pelliculés" tolerance 5 %, max. 10 %, **no specific limit for bruchid-damaged grains**. Addendum VII bis (human food): max. 1 % bruchid-damaged grains. Export to third countries for human consumption (2002/03 season, according to exporters): yellow pea max. 3 % bruchid-damaged; faba bean (Egypt) 1.5 to 3 % [S16] [V]. It is a 23-year-old text: we did not find the current contracts in public [NV].
- **France, faba bean (Hamidi, Taupin and Frérot, Frontiers in Insect Science, 2021):** "economically accepted damage should not exceed 3 % for human consumption and 10 % for animal products", citing the Arvalis/UNIP 2011-2012 faba bean crop guide [S15] [V].
- **Egypt, faba bean:** requires 1 % bruchid-damaged grains, "while France can usually guarantee no better than 3 %" (La Dépêche/Réussir, 1/3/2016) [S17] [V, press].
- **Ireland / "European market", faba bean (Teagasc poster, Pichon et al., Ento24, 2024):** "for the European market, a lot cannot be sold for human consumption with more than 1-3 % damaged grains, and 10 % for animal feed". The poster cites no source [S14] [V].
- **IGP Lentilles vertes du Berry (specification approved on 17/11/2025):** product: unacceptable grains (bruchid-damaged, stained or mouldy) <0.1 %; "brisées ou cassées" grains <0.8 %; brisures (fragments) <0.2 %; foreign matter ≤0.2 %; moisture <16 %. "Brisée" = more than 1/8 of the grain missing; "cassée" = cotyledons separated. Non-compliant lots "are re-sorted or downgraded" [S11] [V].
- **AOP Lentille verte du Puy (specification approved by arrêté of 31/3/2017):** foreign bodies, dust and mineral debris ≤0.5 % of total weight; the organoleptic check is "visual and olfactory examination" [S12] [V].
- **Sabarot (packer), finished-product sheets:** "graines impropres à la consommation" (grains unfit for consumption) <1 % in green lentil du Puy (PF02965), green lentils ZRP (PF03486, 2021) and Méli-mélo (PF01616); in Lentilles vertes du Berry (PF02978, 9/5/2025) unacceptable grains (bruchid-damaged, stained, white) <0.1 % [S13] [V]. These are specifications of the packed product, after sorting, not intake tolerances.

**Physical limit of the photo:** LABOSEM compared the visual method with dissection on the same lots (one lot per row, 4×50 = 200 grains): pea 4.1 % visual vs 11.8 % by dissection, and 3.8 % vs 13.5 %; faba bean 4.8 vs 6.8 % and 3.9 vs 6.4 %; lentil 0.4 vs 0.5 % and 0.5 vs 1.1 % [S6] [V]. That is 6 lots in total: a small sample. The cause: in Europe bruches are univoltine and some larvae "stay in the grains for several months until emerging in the silos" [S18] [V]. **The photo measures visible damage (holes and opercula), not infestation.** Dissection (or X-rays, used by Terres Inovia's Radio_lentille dataset [S33]) does see the larva.

**Useful biology:** after mating, *Bruchus* females lay eggs on developing pods; the larvae enter the pod and develop inside the grain [S18] [V]. On exiting, the adult leaves a characteristic round hole [S14] [V]; before exit an operculum can be seen, a slightly translucent circular "little window" behind which the bruche is visible [S16] [V] [S6] [V]. That is why "egg on the grain" (a class in the soybean dataset) does not apply to French pulses, but "exit hole" does [NV, inference].

**Soybean for human food in France:** on average over 2020/21-2024/25, French soybean production was 402 kt and human food consumption 45 kt [S21] [V]. The pest in the soybean dataset ("pulse beetle", dataset from India) [S29] [V] does not seem relevant in France [NV]. Soybean is the proof of the method, not of the French problem.

**Economic value:**
- Protein crops (pea, faba bean, lupin), FranceAgriMer: 477 grain collectors in 2024/25 (117 cooperatives and 360 négociants (private grain traders)); ~12,400 delivering producers in 2024; 502 kt of pea and faba bean collected per year on average over 2020/21-2024/25 (64 % of production); domestic uses for human food: 146 kt in 2024/25 (5-season average: 155 kt) vs 62 kt processed by the compound feed industry [S20] [V].
- Pea, Terres Inovia 2025 guide: the margin calculation uses an indicative price of 250 €/t for animal-feed destination and 280 €/t for human food (+30 €/t) [S22] [V]. Own calculation: a 28 t truck (assumption) × 30 €/t = **~840 €** difference if a suitable lot goes to animal feed [NV, own calculation with inputs from S22].
- Lentil, FranceAgriMer: average price paid to the producer (conventional, "complet", cumulative to end of season Q4): 873 €/t in 2024/25 and 806 €/t in 2025/26 [S23] [V]. We did not find what a downgraded lentil is worth; so "in lentil the error costs more than in pea" remains a hypothesis [NV].
- We did not find the cost of manual inspection per sample [NV].

---

## 4. User and decision

This whole section is product design [NV, hypothesis to validate with mentors], except where marked.
- **Main user:** intake technician (agréeur, grain quality grader) of a cooperative or grain collector (organisme stockeur) receiving pea, lentil or faba bean.
- **Decision:** for each truck or lot, whether it goes to the human-food bin or to animal feed, and whether a réfaction (price discount) for defects applies.
- **Today:** sample, count by hand or by eye, technician's judgement. Reference methods are visual [S5] [S6] [V]; how it is done in each cooperative we do not know [NV].
- **Cost of a mistake:** sending a suitable lot to animal feed loses the price difference; sending an unsuitable lot to human food risks rejection by the buyer or re-sorting (in IGP Berry non-compliant lots are re-sorted or downgraded [S11] [V]).
- **Secondary users:** packers (Sabarot [S13], Vivien Paille [NV]), the producer themselves before delivery, laboratories.

---

## 5. Product: what needs to be built

**Input:** phone photo of a grain sample on an A4 sheet or a matte background.

**Output:**
- The photo with each grain marked by colour according to its class.
- Percentage of each class with a binomial confidence interval.
- Decision against a selectable threshold (default: bruchid-damaged/damaged ≤1 % or ≤3 % → human food; see thresholds and their sources in §3).
- Low-confidence warning if there are few grains or the photo is bad.

**Target classes for pulses:**

| Class | Training source | Easy to obtain at the event |
|---|---|---|
| Sound | Soybean (Healthy), own photos | Yes, from the supermarket |
| Broken / split | GrainSet "broken", Soybean Seeds "broken", own photos | Yes: you break them yourselves; it is real damage, not synthetic |
| Insect hole | Soybean "Hole", GrainSet "attacked by pests" | Hard: packed product is already sorted (≤0.1 to <1 % unfit according to the sheet [S13]). Ask for real samples (see §13) |
| Stained / discoloured | Soybean Seeds "spotted", Brazilian soybean | Partly |
| Foreign material / other species | GrainSet "impurity", own photos | Yes: small stones, other grains |

**Must have (without this there is no project):**
1. Per-grain classifier trained on soybean with the **clean split** and evaluated on its clean test set.
2. Own photos of pea and lentil (~50) with at least sound and broken, labelled by folder.
3. **Transfer curve** soybean → pea/lentil: without fine-tuning and with 5, 10, 25 and 50 grains per class.
4. Grain separation in photos with many grains (threshold and contours on a plain background).
5. Lot-level aggregation: % per class with interval and decision against the threshold.
6. Working demo (Streamlit or Gradio): upload photo → marked grains, percentages, decision.
7. Data provenance table (measured / sourced / assumed / synthetic) and list of prior resources (required by the guide [S1]).

**Nice to have:**
- "Hole" class in pea or lentil with real damaged grains.
- Separation of touching grains with a pretrained model (SAM or Cellpose) and count validation on corn1000.
- Validation with Radio_lentille (X-rays of bruchid-damaged lentils from Terres Inovia [S33]), for example to show the difference between visible damage and infestation.
- Per-class probability calibration.
- Demo on the phone (public URL from an AWS instance).
- Faba bean and chickpea in addition to pea and lentil.

**Out of scope:** detecting the larva inside the grain (X-ray or dissection), predicting future infestation, treatment recommendations, measuring protein or moisture, integrating with silo software.

---

## 6. Datasets

Content figures come from our audits (cited as "own audit") and metadata (title, authors, licence, date) from the dataset page or API, reopened today.

### 6.1 Main: soybean with beetle damage (Mendeley d97rjyk2tz)

| Field | Value |
|---|---|
| URL | https://data.mendeley.com/datasets/d97rjyk2tz (public API: https://data.mendeley.com/public-api/datasets/d97rjyk2tz?version=2) |
| Citation | Shinde, Nagale, Abin, Joshi, Parashar (2026). *A dataset for soybean seed infestation and quality damage* (v2, published 17/7/2026). Mendeley Data. doi:10.17632/d97rjyk2tz.2. v1 (3/6/2026) was called *Soybean Seed Infestation Dataset for Pulse Beetle Damage Analysis* [S29] [V] |
| Licence | CC BY 4.0 (cite, link the licence and indicate changes) [S29] [V] |
| Files | v2: `Soybean_Seed_Dataset.zip` (80 MB). v1: `Train.zip`, `Validation.zip`, `Test.zip`. **Download both versions**: v1 keeps the original file names that allow grouping by photo [S36] [F] |
| Content | 2,726 JPEG 640×640, **one seed per photo** (97.8 %), boxes in YOLO format. Boxes per class: Egg 9,729, Hole 1,848, Testa cracking 1,265, Normal_Damage 240, Healthy 1,393 [S36] [F, own audit] |
| Published splits | train 2,180, validation 272, test 274 [S36] [F, own audit] |
| Associated paper | We found none [S36] [NV, negative search] |

**Problems found in our own audit [S36] [F]:**
1. **Leakage:** 80 % of validation (217/272) and 84 % of test (229/274) are variants (rotation, flip, crop) of an original photo that is also in train; 15-17 % are exact copies (md5). There are 1,169 original photos in v1, each repeated 1 to 3 times. **Do not use the published split.**
2. **Shortcuts:** 505 of the 513 photos with a black background have beetle damage, and no sound-only photo has a black background. The date is printed on the photo, and days 9-11/08 are bruchid only. **Each seed must be cropped (and the background masked) before classifying.**
3. **Labels:** in 100 photos reviewed by hand, ~15 with a clear error (7 missing boxes, 5 wrong classes, 3 badly drawn boxes) and 9 doubtful (manual estimate). 26 % of photos with a "Healthy" box (353 of 1,376) also have defects. 32 of the 33 new v2 photos have no labels even though they show damage.
4. **Transfer:** "Hole" resembles the *Bruchus* hole in faba bean; "Testa cracking" only partly resembles "broken"; "Egg" and "Normal_Damage" are not used [NV, visual judgement].

**Clean split already computed:** `research/soybean_bruchid/resplit_by_original.csv`. Columns: `image_v2, original_split, group, new_split, discard, n_labels, background, type`. It groups by original photo, discards 249 exact copies and 43 unlabelled (32 new from v2 + 11 empty from v1), and splits 70/15/15 stratified by type and background: train 1,715 images (816 originals), validation 354 (175), test 365 (175). No original is in two splits [V, recounted today on the CSV]. **It is a prior resource: declare it or regenerate it at the event.**

### 6.2 Support: other datasets

| Dataset | URL | Licence | Content | Use |
|---|---|---|---|---|
| **GrainSet** (Scientific Data 2023, doi 10.1038/s41597-023-02660-8) | Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC10632488/ · repo: https://github.com/hellodfan/GrainSet · figshare 22989029 (tiny, 695 MB), 24137472 (raw, 3.4 GB) | CC BY 4.0 [S31] [V] | More than 350,000 images of individual grains of wheat, maize, sorghum and rice, from more than 20 regions in 5 countries, annotated by inspectors [S31] [V]. Classes according to own audit: sound, fusarium/shrivelled, sprouted, mould, **attacked by pests**, **broken**, black tip, **impurity**; each image = top and bottom view side by side [S37] [F] | Broken and pest hole, with the best label quality; pretraining. **Split by capture batch (timestamp)**, not at random |
| **corn1000** | https://huggingface.co/datasets/SmartFarmingLab/corn1000 | CC BY-NC 4.0 (non-commercial) [S32] [V] | 836 phone photos with 170 to 1,000 cereal grains on an A4 sheet and their exact count; 158 with one point per grain and 101 points for broken grains [S37] [F, own audit] | Measure the counting error of grain separation in the real cooperative case |
| **Radio_lentille** (Terres Inovia) | https://huggingface.co/datasets/JeanEudesH/Radio_lentille | MIT; access "gated: auto" (you must log in to HuggingFace and accept) [S33] [V] | 807 JPG X-rays of bruchid-damaged lentils from trials (BRI_21, KAIROL, QAL 2021-2023) + 2 Excel files of counts, 1.47 GB [S37] [F, metadata read by our own audit; content not opened, NV] | French validation, argument for the pitch and link with Terres Inovia |
| **Segmented pea** (Ünal and Gulzar) | https://zenodo.org/records/21110940 | CC BY 4.0 [S34] [V] | Demonstration subset of 5 photos (from a dataset of 100) with LabelMe polygons per pea [S34] [V]; 2,155 peas drawn in total [S37] [F, own audit] | Test grain separation on pea |
| **Faba bean Lethbridge (Canada)** | https://zenodo.org/records/18226381 | CC BY 4.0 [S35] [V] | 78 photos of faba bean seeds from greenhouse lines, with a 24-patch colour chart [S35] [V]; 3 to 10 faba beans per photo, blue background, no damage labels [S37] [F] | Unlabelled test photos |
| **Soybean Seeds 5 classes** (Lin et al., v6, 30/5/2023) | https://data.mendeley.com/datasets/v6vzvfszj6 (mirror on Kaggle) | CC BY 4.0 [S30] [V] | 5,513 crops 227×227: intact, spotted, immature, broken, skin-damaged, according to Chinese standard GB1352-2009 [S30] [V]; 290 duplicate groups [S37] [F, own audit] | Broken and stained |

**Discarded** (own audit [S37] [F]): WheatVision (massive train/test leakage, unnamed classes), phone soybean Mendeley 65rzpcgbp4 (the zip does not include the labels it promises), Brazilian soybean Mendeley xnx9bfbh6b (its "damaged" class is stains, not holes), CornViT (blurry crops), coffee 17 defects (unknown licence). Roboflow Universe could not be audited (requires an account; there are small lentil and soybean projects).

**We found no** public RGB-photo dataset of pea, lentil, faba bean or chickpea with damage, nor of pea weevil or dry bean weevil [S37] [S38] [NV, own negative search].

### 6.3 Own data (to be generated at the event)

See the protocol in §9. Target: ~50 photos, 2 species (green lentil and pea), 6 classes, 4 photos per class, plus 5-10 mixed photos counted by hand for lot-level evaluation.

---

## 7. Method

This section is our own design [NV], except where marked.

**Pipeline:**
1. **Separate the grains.**
   - Non-touching grains on a plain background: threshold + contours (OpenCV).
   - Touching grains: watershed, or a pretrained segmentation model (SAM, Cellpose) used without training.
   - Validate with the 5 pea photos and with corn1000.
2. **Crop each grain** with its mask (background removed, to eliminate the soybean dataset shortcut) and normalise size.
3. **Classify each grain:** features from a pretrained frozen model (DINOv2 or similar) plus a linear classifier (logistic regression).
   - Why: trains in minutes on CPU, works well with little data and makes the transfer curve natural [NV, expectation to be measured].
   - A YOLO trained on CPU would be slow and fragile (the sandbox has no GPU [S2] [V]).
   - Training: soybean (clean split) + GrainSet (broken, pest, impurity) + own photos for fine-tuning.
4. **Aggregate at lot level:** % per class with binomial interval (Wilson) and decision against the threshold.

**Why AI is essential (for the jury):** without the model there is no product. Separating and classifying hundreds of grains per photo is what a person does today by eye (reference methods are visual [S5] [S6] [V]). The guide counts computer vision as a real use of AI [S1] [V].

**Details that matter:**
- Cropping the seed is mandatory: otherwise the model learns the black background or the printed date [S36].
- In soybean, classes must be mapped: Hole → hole; Testa cracking → broken/seed coat damage (with care); Healthy → sound, only if the photo has no other defect boxes; Egg and Normal_Damage out.
- With 1 % thresholds, in a sample of 200 grains a single misclassified grain moves 0.5 points (own calculation: 1/200). Always show the interval and recommend the number of grains per photo.

---

## 8. Evaluation

| Level | Metric | On which data |
|---|---|---|
| Per grain | F1 per class, confusion matrix | Clean soybean test set; own photos split **by photo**, never by grain |
| Transfer | F1 on pea/lentil without fine-tuning and with 5, 10, 25, 50 grains per class | Own photos |
| Per lot | Absolute error of defect % vs manual count; accuracy of human/feed decision | 5-10 mixed photos counted by hand |
| Grain separation | Count error (%) | corn1000, Zenodo pea |

**Checkpoints (go / no-go):**
- **Saturday 13:00:** the classifier works reasonably on the clean soybean test set and grain separation works on our own photos. If not, review crops, classes and leakage before continuing.
- **Saturday 16:00:** the transfer curve exists with at least sound and broken in pea. If the hole could not be photographed in pulses, show it on soybean and say so.
- **Saturday 18:00:** the demo runs end to end on a laptop.

---

## 9. Photo protocol (~2 h for 2-3 people)

Our own design [NV], except where marked.

1. **Setup (15 min):**
   - Matte, uniform background: dark blue or black card (works for green lentil and pea).
   - Phone fixed at 25-30 cm, perpendicular (stand or stack of books).
   - Diffuse light: window without direct sun, or two lamps at 45° with baking paper. No flash.
   - Lock exposure and focus in the camera app.
   - Scale: a 1 € coin (23.25 mm diameter [NV, general fact]) or a ruler in a corner; if available, a grey or colour card.
2. **Grains per photo:** 30-80, not touching. Some photos with touching grains to test separation. For the final demo, one "realistic" photo of ~200 grains (the size of LABOSEM's visual analysis for lentil [S6] [V]).
3. **One class per photo** for training photos: the label comes from the folder and segmentation gives the crops.
4. **Quantity:** 100-200 grains per class and species (2-5 photos per class), plus 5-10 mixed photos with manual count. 2 species × 6 classes × 4 photos ≈ 50 photos, ~1 h with two people sorting grains.
5. **Labelling (30-45 min):** segmentation and cropping script; corrections and mixed photos with local Label Studio or CVAT (free, private). Roboflow's free plan makes projects public [F, snippets of Roboflow documentation, not opened].
6. **Synthetic damage:** if grains are drilled by hand, they go in a separate class and are declared as synthetic (the guide allows synthetic data only if identified [S1] [V]).
7. **Split:** by photo (or by source bag), never by grain.

**Shopping (before the event):** green and red lentil, split and whole pea, faba bean, chickpea, soybean. The guide does not mention buying supplies; what is forbidden is building the solution, code, model, prototype, results or deck before the start [S1] [V]. Buying is an input, not a deliverable [NV, interpretation]: still confirm with the organisers. Photos and labels only during the event.

---

## 10. Work plan

**Roles:**
- **A (data and evaluation):** soybean dataset, clean split, own photos, labelling, metrics.
- **B (model):** grain separation, features, classifier, transfer curve, lot aggregation.
- **C (product and pitch):** demo, business context, questions for mentors, deck, script and rehearsal.

| Block | A | B | C |
|---|---|---|---|
| **Fri 20:45-23:00** | Download soybean v1 and v2, apply the clean split, crop seeds | Download GrainSet tiny; test threshold-and-contour separation on a couple of photos | Questions for mentors and organisers (§13); declare the track; set up the photo station |
| **Sat 10:15-13:00** | Photo session (~50) and labelling by folder | DINOv2 features + classifier on soybean; clean test; transfer without fine-tuning | Demo skeleton; contact Antoine Gardarin for real damaged grains |
| **Sat 13:00** | **Checkpoint 1** | | |
| **Sat 14:00-18:00** | Mixed photos counted by hand; provenance table | 5/10/25/50 curve; lot aggregation with interval; threshold decision | Demo connected to the model; problem and business slides |
| **Sat night (off-site)** | Final metrics and figures | Robustness (bad photos, few grains); freeze the model | Full deck; backup video of the demo; 4-min rehearsal |
| **Sun 8:30-9:30** | README with prior resources | Clean repo | **Submit before 9:30**: PDF + online sheet |
| **Sun 12:00** | **Back up everything outside AWS** (GitHub + USB) | | |

**Cut list (in order, if time runs short):** faba bean and chickpea → Radio_lentille → SAM/Cellpose → demo on the phone → stained class. The clean split, the transfer curve and the demo are never cut.

---

## 11. Demo and pitch

**Demo script (~70 s):**
1. "I'm an intake technician and a truck of lentils just arrived." Live photo of a sample on the card.
2. The screen shows each grain coloured by class, the percentages with their interval and "SUITABLE / NOT SUITABLE for human food".
3. Change the threshold (1 % → 3 %) and watch the decision change.
4. Show the transfer curve.

**4-minute pitch** (each figure with the exact wording from §3):

| Time | Content |
|---|---|
| 0:00-0:40 | **Problem:** in the 2025 national quality survey, lentil lots had on average 24.4 % bruchid-damaged grains, the highest value since the survey exists [S8]; since July 2024 no insecticide remains authorised in the field against the bruche on dry pulses [S19]. For human food, contracts require at most 1 to 3 % bruchid-damaged grains depending on destination [S16]. Today these defects are assessed by eye, grain by grain [S5] [S6] |
| 0:40-1:20 | **Solution and user:** the intake technician takes a photo; the system separates, classifies and decides |
| 1:20-2:30 | **Live demo** with pea and lentil |
| 2:30-3:10 | **How we built it:** we found no public data on damaged pulses; soybean audited and re-split (80-84 % leakage in the original split [S36]); the transfer curve with our own photos |
| 3:10-4:00 | **Scaling and business:** 477 protein-crop grain collectors in France [S20]; Inarix shows that the photo grain-analysis market exists in cereals [S24], and we found nothing of theirs in pulses [NV]; the app collects data at every intake and improves with use. Limit: we see the hole, not the larva [S6] |

**Likely jury questions:**

| Question | Prepared answer |
|---|---|
| Why soybean? | It is the only public labelled dataset of insect damage on a legume that we found [NV, own search]. We use it for training, we audited it, and we measure transfer to pea and lentil with our own photos |
| Isn't this what Inarix already does? | Inarix analyses cereals by phone photo (wheat, barley, maize, according to Meta 2024) [S24] and took part in a project in Canada to identify soybean **variety** by photo [S25]. We found nothing of theirs in pea, lentil or faba bean [NV], where the criteria are different: broken and bruchid-damaged. We can be a complement or a partner |
| Does it see the larva? | No. We see visible damage. In two pea lots of 200 grains, the visual count gave 4.1 % and 3.8 % and dissection 11.8 % and 13.5 % [S6]. Infestation requires dissection or X-rays |
| How much data is needed for production? | The curve shows it: with N labelled grains you reach X. The app collects that data at every intake |
| What is it worth? | With the indicative price from the Terres Inovia guide (280 €/t human vs 250 €/t animal [S22]), a 28 t truck of pea wrongly sent to animal feed is ~840 € (own calculation). That this exceeds the cost of the tool per silo and season is an assumption to validate [NV] |
| Is it animal feed? | No: the goal is for more French pulses to reach human food, by correctly separating suitable lots. The guide excludes animal-feed projects [S1] |

---

## 12. Business and competition

**Competition:**

| Player | What it does | Pulses |
|---|---|---|
| **Inarix** (France) | Grain analysis by phone photo; the home page shows variety, protein, broken grains, specific weight and moisture in wheat [S26] [V]. According to Meta (6/12/2024): assesses barley, wheat and maize, soybean planned; covers "approximately 40 % of the French barley industry" and more than 600 silos in more than 10 countries; built on DINOv2 [S24] [V]. Project in Canada with Grain Discovery and Sevita: identify the variety of a soybean sample by photo in under 20 s; 1,237,145 $ (the page does not state the currency; Canadian body); March 2025 to March 2026 [S25] [V] | We found nothing [NV, negative search] |
| FOSS EyeFoss | Image analyser for intake stations (50 kg, indoor use): 10,000 grains or half a litre in 4 minutes; damaged grain and foreign matter [S27] [V] | Only wheat, barley and durum [S27] [V] |
| GrainSense | Portable NIR: protein, moisture, oil, carbohydrates; wheat, barley, rapeseed; 3,900 € excl. VAT + user account 250 €/year (Terre-net, 11/6/2019, updated 2022) [S28] [V] | Does not measure defects |
| Cgrain Value, Videometer, VIBE QM3 | Laboratory image analysers | Not verified; prices not verified [NV] |

**Possible business model** [NV]: subscription per silo or per intake point, sold to cooperatives and grain collectors. Willingness to pay is not validated; Inarix shows it exists in cereals [S24].

**Data value** [NV]: each intake generates photos labelled by the technician, which improves the model with use.

---

## 13. Risks and open questions

**Risks** [NV, own judgement]:
- The guide's "Insects" exclusion [S1]: probably refers to insects as food, but it must be confirmed.
- Not getting pulse grains with real holes: the hole class would remain soybean-only.
- Direct soybean → pea transfer being poor: that is not a failure, it is what the curve shows.
- Competition: the jury seeing the project as "Inarix for pulses".
- Different lighting and backgrounds between photos: fix the protocol.
- Fine thresholds (1 %) with small samples: show the interval.

**Questions for mentors and organisers (Friday before 23:00):**
1. Does the "Insects" exclusion cover detecting insect damage on grains?
2. Is a project that trains on soybean (for human food) in scope?
3. Can supplies be bought before the event?
4. In a French cooperative, are broken and bruchid-damaged grains counted truck by truck or on composite samples? How long does it take and who does it?
5. What intake tolerances do current pea and lentil contracts set for human food? Is the 1 % of Incograin addendum VII bis still in force? Is there a réfaction grid by % of bruchid-damaged grains?
6. Does anyone have real bruchid-damaged grains to lend? **Antoine Gardarin** (UMR Agronomie, AgroParisTech, Palaiseau [S39] [V]) is the contact for the INRAE dataset of bruchids on faba bean and lentil [S40] [V], on the same campus.
7. Does Inarix already work on pulses?

---

## 14. Prior resources to declare

- Soybean dataset (Mendeley d97rjyk2tz, CC BY 4.0), GrainSet (CC BY 4.0), corn1000 (CC BY-NC 4.0), Radio_lentille (MIT), Zenodo pea 21110940 and Zenodo faba bean 18226381 (CC BY 4.0), Soybean Seeds (CC BY 4.0). Licences verified today [S29]-[S35] [V].
- Pretrained models: DINOv2 (Meta) and, if used, SAM or Cellpose.
- The clean split `resplit_by_original.csv` and the analyses in `research/`, done before the event (exploration, no training).

---

## 15. Actions before Friday night

- [ ] Log in to HuggingFace, accept the terms of `JeanEudesH/Radio_lentille` and download it.
- [ ] Buy the pulses (§9).
- [ ] Get a blue or black card, a 1 € coin and a phone stand.
- [ ] Have the URLs from §6 at hand to download the datasets on Friday night.

---

## 16. Glossary (French → English)

| Term | Meaning |
|---|---|
| bruche / grain bruché | bruchid (seed beetle, *Bruchus*) / bruchid-damaged grain |
| grain cassé / brisé | in the IGP Berry specification: "cassée" = cotyledons separated; "brisée" = more than 1/8 of the grain missing [S11] |
| opercule | operculum: "little window" of seed coat covering the hole before the adult exits [S16] |
| réfaction | price discount for defects at intake |
| organisme stockeur (OS) | grain collector: cooperative or négociant (private grain trader) that receives the grain |
| agréeur | technician who assesses quality at intake |
| alimentation humaine / animale | human food / animal feed |
| protéagineux | protein crops (pea, faba bean, lupin) [S20] |

---

## 17. Sources

All opened on 30/10/2026 unless stated. "What was verified" says exactly what was read.

| Id | Source | What was verified |
|---|---|---|
| S1 | Hack the Fork, *Participant Guide, Hack the Fork Paris 2026* (local file `event/participant_guide.txt`) | Dates, venue, schedule, rules, exclusions, criteria and weights, submission, prizes, ReaKt 2025 runner-up, Track 3 |
| S2 | AWS, *AWS Participant Guide* and *AWS Webinar Notes* (PDFs sent by the organisers, in `~/Downloads/`; summarised in `.claude/skills/aws-hackathon-sandbox/SKILL.md`) | us-east-1, up to 72 h, no GPU (g*, p*), EC2 < 6xlarge, no personal data, backup |
| S3 | SIAL Paris, "SIAL Paris backs young talent at Hack the Fork 2025", 7/1/2026. https://www.sialparis.com/en/trends/News/sial-paris-hack-the-fork-2025-foodtech (opened with Chrome; 403 for bots) | 2025 podium (Ardoise, ReaKt, BlendIn), École 42, 13-14/12/2025, 21 teams. The official report https://hackthefork.org/reports/HtF%202025%20-%20report.pdf returns 404 |
| S4 | Service-public.gouv.fr, "Jours fériés et ponts dans le secteur privé". https://www.service-public.gouv.fr/particuliers/vosdroits/F2405 | Toussaint, Sunday 1/11/2026 |
| S5 | Codex Alimentarius, CXS 171-1989, *Norma del Codex para determinadas legumbres* (Codex standard for certain pulses; adopted 1989, revised 1995), Spanish version. https://www.fao.org/input/download/standards/56/CXS_171s.pdf | Scope, defect limits, foreign matter, "visual examination" |
| S6 | F. Pavy (LABOSEM), "Analyse de grains bruchés. Méthodes développées par LABOSEM", JIT Céréales et protéagineux, 10/3/2022. https://www.semae.fr/uploads/10-2022-jitcerpro_methode-grains-bruches_FP_CEK_MB.pdf | Sample sizes, definitions, visual vs dissection table by crop |
| S7 | V. Biarnès (Terres Inovia), "Bilan qualité protéagineux: analyse historique pois et féverole", JIT, 13/3/2019. https://www.semae.fr/uploads/16-Enquete-qualite-pois-et-feverole-2018.pdf | Survey since 2015, criteria measured, 4 classes |
| S8 | Terres Inovia / Terres Univia, *Lentille. Fiche qualité des graines, récolte 2025* (Feb. 2026). https://www.terresinovia.fr/sites/default/files/2026-02/fiche-qualite-graines-lentille_2025.pdf (403 for bots; text extracted with pdf.js in Chrome and chart read by eye) | 60 samples, 40 with bruchid-damaged grains, mean 24.4, min. 1.0, max. 75.5, std. dev. 18.7, basins, 2021-2025 series, methodology, 2.8 % cassées |
| S9 | Terres Inovia / Terres Univia, *Pois. Qualité des graines 2025* (Jan. 2026). https://www.terresinovia.fr/sites/default/files/2026-01/fiche_terres_inovia_qual_graines_pois2025.pdf (403 for bots; read with pdf.js in Chrome) | 85 samples, 55 / 86 / 96 %, "environ 60 %", 90.5 / 9.5 % |
| S10 | T-Ports, *Lentil Receival Standards 2025/2026*. https://tports.com/wp-content/uploads/2025/09/12.TEM_.47-Lentil-Receival-Standards-2025_2026.pdf | Tolerances by grade, counts per 200 g, reference to GTA for sampling |
| S11 | Cahier des charges IGP « Lentilles vertes du Berry », approved by arrêté of 17/11/2025 (JORF 21/11/2025). https://info.agriculture.gouv.fr/boagri/document_administratif-40f9105a-26b0-47e0-9799-f0161c3a8df5/telechargement | Product limits, brisée/cassée definitions, re-sorting or downgrading |
| S12 | Cahier des charges AOP « Lentille verte du Puy », approved by arrêté of 31/3/2017. https://info.agriculture.gouv.fr/boagri/document_administratif-3b601fa7-0c84-48e9-b94b-bffff44295fb/telechargement | Foreign bodies ≤0.5 %, visual and olfactory examination |
| S13 | Sabarot, technical sheets (mirror): PF02978 https://wyapkgisccvpsoiyfieb.supabase.co/storage/v1/object/public/mirror-documents/docs/ft/3111952029784.pdf , PF02965 …/3111952029654.pdf , PF03486 …/3111952034863.pdf , PF01616 …/3111952016166.pdf | Limits for unfit, unacceptable and brisures by product |
| S14 | A. Pichon, E. Nolan, S. Alves, L. McNamara (Teagasc / SETU), poster "Impact of bruchid beetle on the agronomic value of faba bean seeds", Ento24 (2024). https://royensoc.co.uk/wp-content/uploads/2024/09/P35-–-Antoine-Pichon-Ento24-Poster.pdf | "1-3 %" human and "10 %" animal for "the European market"; round hole; Ireland 2023 |
| S15 | R. Hamidi, P. Taupin, B. Frérot, "Physiological Synchrony of the Broad Bean Weevil, Bruchus rufimanus…", *Frontiers in Insect Science* 1 (6/8/2021), doi 10.3389/finsc.2021.707323. https://www.frontiersin.org/journals/insect-science/articles/10.3389/finsc.2021.707323/full | France: ≤3 % human, ≤10 % animal (faba bean), citing Arvalis/UNIP 2011-2012 guide |
| S16 | *Perspectives Agricoles* n°292, July-August 2003, "Export pour l'alimentation humaine: des critères de qualité spécifiques en pois jaune comme en féverole" (Arvalis / UNIP). https://www.perspectives-agricoles.com/sites/default/files/imported_files/292_1420355064180393423.pdf | Addendum VII (animal) and VII bis (human) Incograin/RUFRA; export 2002/03; definition of operculum |
| S17 | La Dépêche / Réussir, "La féverole française en difficulté sur l'Égypte", 1/3/2016. https://www.reussir.fr/ladepeche/la-feverole-francaise-en-difficulte-sur-legypte | Egypt 1 %, France "3 % d'habitude" |
| S18 | Chery-Lagrange et al., "Colonization and spatiotemporal distribution of bruchid pests in lentil and faba bean fields", *Pest Management Science* 2026, doi 10.1002/ps.70679. Full text via Europe PMC (PMC13158440; pmc.ncbi.nlm.nih.gov asks for a captcha) | Egg-laying on pods, larvae in the grain, univoltine, larvae "several months" until emerging in silos |
| S19 | ANSES, e-phy catalogue as open data (file of 27/10/2026). https://www.data.gouv.fr/fr/datasets/donnees-ouvertes-du-catalogue-e-phy-des-produits-phytopharmaceutiques-matieres-fertilisantes-et-supports-de-culture-adjuvants-produits-mixtes-et-melanges/ | "Légumineuses potagères (sèches)" uses: CYTHRINE MAX withdrawn, end of use 31/7/2024; authorised storage uses |
| S20 | FranceAgriMer, *Fiche filière protéagineux 2026* (Feb. 2026). https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf | 477 / 117 / 360 (2024/25), 12,400 delivering producers (2024), 502 kt 5-season average, 146 kt and 62 kt (2024/25) |
| S21 | FranceAgriMer, *Fiche filière oléagineux 2026* (Feb. 2026). https://www.franceagrimer.fr/sites/default/files/2026-02/18_FICHE_FILIERE_OLEAGINEUX_2026.pdf | Soybean 402 kt and 45 kt in human food, average 2020/21-2024/25 |
| S22 | Terres Inovia, *Pois protéagineux, guide de culture 2025* (Germinéo mirror). https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/POIS-PROTEAG.-2025-Guide-culture-TERRES-INOVIA.pdf | Margin table with 250 €/t (AA) and 280 €/t (AH) "prix indicatif" |
| S23 | FranceAgriMer, *Historique prix payés aux producteurs trimestriels* (data as of 30/6/2026). https://visionet.franceagrimer.fr/Pages/OpenDocument.aspx?fileurl=SeriesChronologiques%2fproductions%20vegetales%2fgrandes%20cultures%2fprix%20pay%c3%a9s%20aux%20producteurs%2fSCR-CER-HISTOPRIXTRIMESTRIELS-C25-26.xlsx&telechargersanscomptage=oui | Lentil Q4: 873 €/t (2024/25), 806 €/t (2025/26); conventional, "complet" price. Mandatory attribution: "Source : FranceAgriMer" |
| S24 | Meta AI blog, "Inarix… DINOv2", 6/12/2024. https://ai.meta.com/blog/inarix-agricultural-supply-chain-meta-dino-v2/ | ~40 % of French barley, >600 silos in >10 countries, barley/wheat/maize, soybean planned, DINOv2 |
| S25 | Protein Industries Canada, "Phone grain quality tool". https://proteinindustriescanada.ca/projects/phone-grain-quality-tool | Partners, soybean, variety, <20 s, 1,237,145 $, Mar. 2025-Mar. 2026 |
| S26 | Inarix, home page. https://www.inarix.com/ | Parameters shown (wheat); no mention of pulses or soybean |
| S27 | FOSS, EyeFoss. https://www.fossanalytics.com/products/eyefoss | Crops, 10,000 grains in 4 min, damaged grain and foreign matter, 50 kg, intake |
| S28 | Terre-net, "GrainSense: connaître la teneur en protéines directement au champ", 11/6/2019 (updated 27/7/2022). https://www.terre-net.fr/materiel-agricole/recolte-fenaison/article/grainsense-connaitre-la-teneur-en-proteines-directement-au-champ-208-148616.html | 3,900 € excl. VAT, 250 €/year, crops |
| S29 | Mendeley Data, d97rjyk2tz, API v1 and v2. https://data.mendeley.com/public-api/datasets/d97rjyk2tz?version=2 | Titles, authors, CC BY 4.0, dates, DOI |
| S30 | Mendeley Data, v6vzvfszj6 (Soybean Seeds, v6), API. https://data.mendeley.com/public-api/datasets/v6vzvfszj6 | 5,513 images, 5 classes, GB1352-2009, CC BY 4.0, 30/5/2023 |
| S31 | Fan et al., "An annotated grain kernel image database for visual quality inspection", *Scientific Data* 2023, doi 10.1038/s41597-023-02660-8 (abstract via Europe PMC) + figshare API 22989029 and 24137472 | >350K grains, 4 cereals, CC BY 4.0, file sizes |
| S32 | HuggingFace API, SmartFarmingLab/corn1000. https://huggingface.co/api/datasets/SmartFarmingLab/corn1000 | Licence CC BY-NC 4.0, not gated |
| S33 | HuggingFace API, JeanEudesH/Radio_lentille. https://huggingface.co/api/datasets/JeanEudesH/Radio_lentille | MIT, gated "auto" |
| S34 | Zenodo 21110940, "Pea Seed Instance Segmentation: Demonstration Subset" (1/7/2026). https://zenodo.org/api/records/21110940 | 5 photos of 100, LabelMe, CC BY 4.0, authors |
| S35 | Zenodo 18226381, "Faba Bean Seed Image Dataset for Computer Vision–Based Phenotyping Studies" (26/1/2026). https://zenodo.org/api/records/18226381 | 78 files, CC BY 4.0, Lethbridge Research and Development Centre |
| S36 | Own audit of the soybean dataset: `research/soybean_bruchid/findings.md` and `resplit_by_original.csv` | Counts, leakage, shortcuts, labels (not recomputed today, except the clean-split CSV, recounted) |
| S37 | Own audit of other datasets: `research/other_datasets/findings.md` | Content of corn1000, Radio_lentille, pea, faba bean, Soybean Seeds, GrainSet; discarded datasets; search for pulse datasets |
| S38 | Own desk research: `research/context/findings.md` | Negative searches (pulse datasets, Inarix in pulses, current contracts, manual inspection costs) |
| S39 | INRAE, *Mots de l'agronomie*, "Antoine Gardarin". https://mots-agronomie.inrae.fr/index.php/Antoine_Gardarin | AgroParisTech, UMR Agronomie, Palaiseau |
| S40 | Recherche Data Gouv, dataset doi:10.57745/HPEMYW (API). https://entrepot.recherche.data.gouv.fr/api/datasets/:persistentId/?persistentId=doi:10.57745/HPEMYW | Contact: Antoine Gardarin (Agronomie; INRAE, AgroParisTech, UPSaclay); licence Etalab 2.0 |

Full audits with plots: `research/README.md`, `research/soybean_bruchid/findings.md`, `research/other_datasets/findings.md`, `research/context/findings.md`.

---

## 18. Claims register

| # | Claim | Section | Value | Source | Status | Notes (scope) |
|---|---|---|---|---|---|---|
| 1 | Event dates and venue | §2 | 30/10 17:30 to 1/11 14:00, Palaiseau | S1 | [V] | |
| 2 | Schedule, campus closing | §2 | 23:00 Fri, 18:00 Sat | S1 | [V] | |
| 3 | Submission | §2 | Sun 1/11 before 9:30; PDF + sheet | S1 | [V] | |
| 4 | Pitch | §2 | 4 min + 2 of questions | S1 | [V] | |
| 5 | Criteria and weights | §2 | 30/20/20/20/10 | S1 | [V] | |
| 6 | Exclusions | §2 | Insects, animal ingredients, animal feed, no demo | S1 | [V] | Scope of "Insects": [NV] |
| 7 | 1/11 public holiday | §2 | Toussaint | S4 | [V] | |
| 8 | 2025 podium | §2 | Ardoise, ReaKt, BlendIn | S3, S1 | [V] | Edition at École 42, Dec. 2025 |
| 9 | No 2025 project on the farm side | §2 | | | [NV] | Interpretation; official report inaccessible |
| 10 | AWS sandbox limits | §2 | us-east-1, 72 h, no GPU, < 6xlarge | S2 | [V] | Event documents |
| 11 | Codex: serious / minor / broken / foreign defects | §3 | 1 / 7 / 3 / 1 % | S5 | [V] | Does not govern grain for factory sorting or animal feed |
| 12 | Codex: "visual examination" method | §3 | | S5 | [V] | |
| 13 | LABOSEM sample sizes | §3 | lentil 200; protein crops 250-500 | S6 | [V] | Laboratory service, not intake |
| 14 | 4 Terres Inovia visual classes | §3 | 0 / <1 / 1-10 / >10 % | S7, S8 | [V] | |
| 15 | T-Ports: tolerances per 200 g | §3 | defective ≤4/5/8 %; severely damaged ≤1 per 200 g | S10 | [V] | South Australia; "per truck" does not appear |
| 16 | Lentil 2025: mean bruchid-damaged | §3, §11 | 24.4 % (40 samples; 1.0-75.5) | S8 | [V] | Mean per lot, not "1 in 4 lentils" |
| 17 | Lentil 2025 by basin | §3 | CO 36.8; SO 22.3; NE 18.6; SE 15.4 | S8 | [V] | |
| 18 | 2021-2025 series | §3 | 11.6 / 15.3 / 10.3 / 14.5 / 24.4 | S8 | [V] | Read by eye from the PDF chart |
| 19 | No field insecticide since 31/7/2024 | §3, §11 | CYTHRINE MAX withdrawn | S19 | [V] | In storage there are products; "bruche ⊂ phytophagous beetles" [NV] |
| 20 | Pea 2025: broken <1 % | §3 | 55 % of 85 lots | S9 | [V] | |
| 21 | Pea 2025: insects <1 % / stained <1 % | §3 | 86 % / 96 % | S9 | [V] | |
| 22 | Pea 2025: ~60 % suitable for human food | §3 | ~60 % | S9 | [V] | "pourraient satisfaire" |
| 23 | Pea 2025: declared destination | §3 | 9.5 % human | S9 | [V] | Only half of lots declared a destination |
| 24 | Incograin contracts VII bis (human) | §3 | max. 1 % bruchid-damaged | S16 | [V] | 2003 text; current validity [NV] |
| 25 | Incograin contracts VII (animal feed) | §3 | no bruchid-damaged limit; 10 % cassés+bruchés+pelliculés | S16 | [V] | 2003 |
| 26 | Human-food export 2002/03 | §3 | pea 3 %; faba bean 1.5-3 % | S16 | [V] | According to exporters, 2002 |
| 27 | France, faba bean: 3 % human / 10 % animal | §3 | | S15 | [V] | Cites Arvalis/UNIP 2011-12 guide |
| 28 | Egypt, faba bean | §3 | 1 % | S17 | [V] | Press 2016 |
| 29 | Teagasc "European market" | §3 | 1-3 % human, 10 % animal | S14 | [V] | Irish poster, faba bean, no source |
| 30 | IGP Berry | §3 | unacceptable <0.1 %; brisées/cassées <0.8 % | S11 | [V] | Finished product |
| 31 | AOP Puy | §3 | foreign bodies ≤0.5 % | S12 | [V] | Arrêté 2017 |
| 32 | Sabarot | §3 | unfit <1 % (3 sheets); Berry <0.1 % | S13 | [V] | Packed product |
| 33 | Visual vs dissection | §3, §11 | pea 4.1 vs 11.8; 3.8 vs 13.5 | S6 | [V] | 2 lots of 200 grains; also faba bean and lentil |
| 34 | Larvae months in the grain | §3 | "several months" | S18 | [V] | |
| 35 | Egg-laying on pods | §3 | | S18 | [V] | |
| 36 | Round hole / operculum | §3 | | S14, S16, S6 | [V] | |
| 37 | Soybean France | §3 | 402 kt production; 45 kt human | S21 | [V] | Average 2020/21-2024/25 |
| 38 | Dataset pest not relevant in France | §3 | | S29 | [NV] | |
| 39 | Protein-crop grain collectors | §3, §11 | 477 (117 coops) | S20 | [V] | 2024/25 |
| 40 | Pea + faba bean collected | §3 | 502 kt (64 %) | S20 | [V] | 5-season average, not annual |
| 41 | Domestic human food consumption | §3 | 146 kt (average 155) | S20 | [V] | 2024/25, pea + faba bean |
| 42 | Pea indicative price | §3, §11 | 250 vs 280 €/t | S22 | [V] | Guide assumption, not observed premium |
| 43 | Pea truck | §3, §11 | ~840 € | S22 | [NV] | Own calculation: 28 t (assumption) × 30 €/t |
| 44 | Lentil producer price | §3 | 873 (24/25), 806 (25/26) €/t | S23 | [V] | Conventional, cumulative Q4 |
| 45 | Cost of manual inspection | §3 | not found | S38 | [NV] | |
| 46 | Inarix: barley, silos, DINOv2 | §12 | ~40 %, >600 silos, >10 countries | S24 | [V] | As stated by Meta/Inarix |
| 47 | Inarix: soybean Canada | §12 | 1,237,145 $, 2025-2026 | S25 | [V] | Variety identification, not damage; currency not stated |
| 48 | Inarix without pulses | §11, §12 | | S26, S38 | [NV] | Negative search |
| 49 | EyeFoss | §12 | wheat, barley, durum; 10,000 grains in 4 min | S27 | [V] | |
| 50 | GrainSense | §12 | 3,900 € excl. VAT + 250 €/year | S28 | [V] | 2019 price |
| 51 | Mendeley soybean: licence and citation | §6.1 | CC BY 4.0, v2 17/7/2026 | S29 | [V] | |
| 52 | Soybean: images, boxes, splits | §6.1 | 2,726; 2,180/272/274 | S36 | [F] | Own audit |
| 53 | Soybean: leakage | §6.1, §11 | 80 % val, 84 % test | S36 | [F] | Own audit |
| 54 | Soybean: label errors | §6.1 | ~15/100 | S36 | [F] | Manual estimate |
| 55 | Soybean: background shortcut | §6.1 | 505/513 | S36 | [F] | Own audit |
| 56 | Clean split | §6.1 | 1,715/354/365 images; 816/175/175 groups; 0 overlapping | S36 | [V] | Recounted today on the CSV |
| 57 | GrainSet | §6.2 | >350K grains, CC BY 4.0 | S31 | [V] | Classes: own audit [F] |
| 58 | corn1000 | §6.2 | CC BY-NC 4.0; 836 photos | S32, S37 | [V] licence / [F] counts | |
| 59 | Radio_lentille | §6.2 | MIT, gated; 807 X-rays | S33, S37 | [V] licence / [F] count | Content not opened |
| 60 | Zenodo pea | §6.2 | 5 photos, CC BY 4.0 | S34 | [V] | 2,155 grains [F] |
| 61 | Zenodo faba bean | §6.2 | 78 photos, CC BY 4.0 | S35 | [V] | |
| 62 | Soybean Seeds | §6.2 | 5,513, 5 classes, CC BY 4.0 | S30 | [V] | 290 dup. groups [F] |
| 63 | No public dataset of damaged pulses | §1, §6.2 | | S37, S38 | [NV] | Negative search |
| 64 | Gardarin, contact for the INRAE dataset | §13 | UMR Agronomie, Palaiseau | S39, S40 | [V] | |
| 65 | 1 grain in 200 = 0.5 points | §7 | | | [NV] | Trivial own calculation |
| 66 | Current intake contracts | §3, §13 | not found | S38 | [NV] | |
| 67 | Buying supplies beforehand is allowed | §9 | | S1 | [NV] | The guide does not mention it; ask |
