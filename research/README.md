# SoyMate (formerly "idea 9"): photo-based quality control of pulses (data report)

> Project source of truth: [`../CONTEXT.md`](../CONTEXT.md), where every figure has its source. If anything here differs, that file wins.

Analysis done on 30/10/2026, before the event, by three subagents: an in-depth audit of the soybean pulse-beetle dataset, a survey of other seed and grain datasets, and context (standards, competition, business, photo protocol). **No model was trained or run on the images** (hackathon rule). The downloaded data was deleted; what remains is plots, three `findings.md` files and a CSV with the clean split of the soybean dataset.

PDF with the plots for the team: [`../docs/soymate_data_report.pdf`](../docs/soymate_data_report.pdf). Team plan: [`../docs/soymate_team_plan.pdf`](../docs/soymate_team_plan.pdf).

| Folder | Contents |
|---|---|
| [soybean_bruchid/](soybean_bruchid/findings.md) | Soybean pulse-beetle dataset (Mendeley d97rjyk2tz): 11 plots, manual label review, leakage between splits, clean split (`resplit_by_original.csv`) |
| [other_datasets/](other_datasets/findings.md) | 16 datasets reviewed (10 downloaded): GrainSet, corn1000, Radio_lentille, pea, faba bean, Brazilian soybean and more. 12 plots |
| [context/](context/findings.md) | Intake standards, soybean for human consumption in France, competition (Inarix and others), business, photo protocol for the event |

---

## 1. In one line

**The idea is viable as a 20-hour vision project:** there is good public data to train each piece (separating grains, detecting broken grains, detecting insect holes), although none of it is French pulses in phone photos. That is why the plan needs our own photos taken at the event. There is a strong French competitor in cereals (Inarix), but nobody does pulses. The photo only sees visible damage, not the larva inside the grain: we have to say so.

---

## 2. The data

| Dataset | Crop | What it contains | License | What it is good for | Main problem |
|---|---|---|---|---|---|
| **Soybean pulse beetle** (Mendeley d97rjyk2tz) | Soybean | 2,726 phone photos, one seed per photo, 14,475 boxes: Egg, Hole, Testa cracking, Normal_Damage, Healthy | CC BY 4.0 | Detecting the insect's **exit hole** | 80-84% leakage between splits, background and date give the damage away, ~15% of labels with errors |
| **GrainSet** (Scientific Data 2023) | Wheat, maize, sorghum, rice | 350,000 grains with expert labels: sound, broken, attacked by pests, mold, foreign material, etc. | CC BY 4.0 | **Broken** grains and **pest holes** with the best label quality; pretraining | Cereals; industrial camera; must split by capture batch |
| **corn1000** (HuggingFace, U. Leipzig) | Cereals | 836 phone photos of 170 to 1,000 grains on an A4 sheet, with the exact count; 158 with one point per grain and points for broken grains | CC BY-NC 4.0 (non-commercial) | **Counting and separating grains** in a photo with many of them, the real cooperative case | Cereals; points only, no contours |
| **Radio_lentille** (HuggingFace, Terres Inovia) | **French lentil** | 807 X-rays of bruchid-infested lentils from 2021-2023 trials + 2 Excel files of counts | MIT | French validation and an argument for the pitch | Access requires an HF account (automatic approval); it is X-ray, not photo; contents not opened |
| **Segmented pea** (Zenodo 21110940) | **Pea** | 5 photos with 2,155 peas outlined one by one (the other 95 are on request) | CC BY 4.0 | Testing grain separation on pea | Only 5 photos; no defects |
| **AAFC faba bean** (Zenodo 18226381) | **Faba bean** | 78 photos, 3 to 10 faba beans per photo | CC BY 4.0 | Test photos | No damage labels |
| Soybean Seeds 5 classes (Mendeley v6vzvfszj6) | Soybean | 5,513 crops: intact, immature, skin-damaged, stained, broken | CC BY 4.0 | Broken and stained | 290 duplicate groups |
| Discarded | | WheatVision (massive leakage), phone soybean 65rzpcgbp4 (labels missing), CornViT (blurry), coffee (unknown license), Brazilian soybean ("damaged" are stains, not holes) | | | |

**There is no public RGB photo dataset of pea, lentil, faba bean or chickpea with damage.** Nor of pea weevil or bean weevil. Roboflow Universe could not be audited (it requires an account).

---

## 3. The soybean dataset, in depth

1. **It really is one seed per photo** (97.8%), at 640×640, taken with a Redmi 13C with a watermark and the date printed on the image.
2. **Leakage between splits:** 80% of validation and 84% of test are variants (rotations, mirrors, crops) of a photo that is also in train; 15-17% are exact copies. With the published split, any metric comes out inflated. Perceptual hashing does not catch the rotated copies: the problem was found by tracing the original filenames from version 1.
3. **Dangerous shortcuts:** 505 of the 513 photos with a black background show bruchid damage, and no healthy-only photo has a black background. Photos from 9 to 11 August are 100% damaged, and the date is printed. A model can learn the background or the date instead of the hole.
4. **Label quality:** in a manual review of 100 photos, ~15 have a clear error (7 missing boxes, 5 wrong classes, 3 badly drawn boxes) and 9 are doubtful. 26% of the photos with a "Healthy" box also have defects.
5. **What transfers to French pulses:**
   - **"Hole":** the round hole with a "window" looks like the one *Bruchus* leaves in faba bean.
   - **"Testa cracking":** only partly resembles "broken".
   - **"Egg":** does not transfer, because *Bruchus* lays its eggs on the pod, not on the grain.
6. **A clean split already exists**, grouped by original photo (train 1,715, validation 354, test 365 images, with no original in two splits): `soybean_bruchid/resplit_by_original.csv`.

---

## 4. Context: standards, competition, business

- **Intake today is visual and manual.** The Codex (CXS 171) uses visual examination: serious defects ≤1%, minor ≤7% (broken ≤3%), foreign matter ≤1%. LABOSEM (SEMAE) counts bruchid-damaged grains over 200 grains for lentil.
- **Thresholds that decide human food vs animal feed:** French Incograin contracts (2003 text) allowed at most 1% bruchid-damaged grains for human consumption; for animal feed there is no specific limit (10% across broken, bruchid-damaged and dehulled). IGP Lentilles vertes du Berry: <0.1% unacceptable and <0.8% broken.
- **Physical limit of the photo:** in two pea lots of 200 grains (LABOSEM 2022), the visual count gave 4.1% and 3.8%, and dissection 11.8% and 13.5%. The photo measures visible damage (holes and "windows"), not the larva still inside.
- **Soybean for human consumption in France:** 45 kt of 402 kt produced, 2020/21-2024/25 average (FranceAgriMer, 2026 sheet). There is no evidence that the pest in the Indian dataset matters in France: soybean is the proof of concept for the method, not for the French problem.
- **Competition:**
  - **Inarix** (French, phone photo) does wheat, barley and maize, says it is in more than 600 silos, and has a project in Canada to identify soybean variety from a photo (2025-2026). We found nothing from Inarix on pea, lentil or faba bean.
  - EyeFoss: cereals only.
  - The gap exists but is narrow: the differentiator is pulses and their criteria (broken grains, bruchids).
- **Business:** 477 organizations that collect protein crops (117 cooperatives), 502 kt collected (2020/21-2024/25 average), 146 kt of pea and faba bean to human consumption (2024/25). Our own calculation: with the indicative prices of the Terres Inovia 2025 guide (280 vs 250 €/t), a 28 t truck of pea wrongly sent to animal feed is ~840 €. We did not find the cost of manual inspection per sample.

---

## 5. How to build the solution at the event

**Three-step pipeline:**
1. **Separate the grains** in a photo with many of them (plain background, A4 sheet): threshold and contours if the grains do not touch; a pretrained segmentation model (SAM or Cellpose) without training if they do. Validate with the 5 pea photos and with corn1000 (count error).
2. **Classify each cropped grain:** a pretrained model (for example DINOv2) to extract features from each grain, plus a simple classifier trained on soybean (clean split) + GrainSet (broken, pest) + our own pulse photos. The AWS sandbox has no GPU: this lightweight scheme trains on CPU.
3. **Aggregate at lot level:** % per class with a binomial confidence interval, and the human food / animal feed decision against the chosen threshold (1%, 3%).

**Metrics:**
- **Per grain:** F1 per class on the clean soybean test set and on our own photos.
- **Per lot:** error of the estimated % against the manual count on 5-10 mixed photos.
- **Transfer gap:** soybean → lentil/pea, without adaptation and with fine-tuning.
- **Grain separation:** count error on corn1000 and on pea.

**Photo protocol (~2 h for 2-3 people):**
- **Setup:** contrasting matte background (blue or black), phone fixed at 25-30 cm, diffuse light without flash, a 1 € coin as scale.
- **Grains per photo:** 30-80 not touching; for the final demo, one photo of ~200 (like the official lentil sample).
- **One class per photo** (sound, broken, holed, stained, foreign material), so the label comes from the folder.
- **Quantity:** 2 species × 6 classes × 4 photos ≈ 50 photos.
- **Labeling:** Label Studio or CVAT, local and free. Free Roboflow makes the dataset public.
- **Split:** by photo, never by grain.
- **Synthetic damage:** if grains are pierced by hand, they go in a separate class and it is declared.

---

## 6. Actions before and during Friday

1. **Request access to Radio_lentille now:** log in to HuggingFace, accept the terms on `JeanEudesH/Radio_lentille` and download it. It is data exploration, which is allowed.
2. **Buy** green lentils, red lentils, split peas, whole peas, faba beans, chickpeas and soybeans. Sunday 1/11 is a public holiday and on Saturday the campus closes at 18:00.
3. **Ask the mentors and the organizers:**
   - that the "insects" exclusion does not cover detecting insect damage on grains;
   - that a project with soybean for human consumption is in scope;
   - that buying supplies before the event is fine (photos and labels, only during the event).
4. **Contact Antoine Gardarin** (UMR Agronomie, on the same Palaiseau campus), contact person for the INRAE bruchid dataset, to get real bruchid-damaged grains.

---

## 7. How to present it (honestly)

- "We tested the method on public soybean data that we **audited and re-split** (the original split had 80% leakage), and transferred it to French lentils and peas with photos we took at the event."
- "We detect visible damage (exit hole, broken grains, stains). We do not see the larva still inside the grain: that takes X-rays, which is what the lab uses."
- "Inarix does this for cereals; we found nobody doing it for pulses, where broken grains and bruchids decide whether a lot goes to human consumption."
