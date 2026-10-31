# Viability of SoyMate in France: synthesis (31/10/2026)

Desk research done at the event to answer: is a phone-photo grader for soybean (and later French pulses) useful and economically viable in France, and what would it take? This file is the synthesis. The evidence is in three files, each with its own source list:

- [`soy_market.md`](soy_market.md): French soybean, food vs feed, prices, food-grade criteria. Cited here as **[soy S#]**.
- [`pulses_market.md`](pulses_market.md): lentil, chickpea, pea, faba bean for human food. Cited as **[pul S#]**.
- [`grading_and_competition.md`](grading_and_competition.md): how grading is done, costs, competitors. Cited as **[gra S#]**.

Tags as in `CONTEXT.md`: **[V]** read on the primary source, **[F]** secondary source or snippet, **[NV]** own calculation or inference (inputs given). Not yet merged into `CONTEXT.md`: see "Corrections" at the end.

---

## 1. Verdict

1. **The technology has a paying market, but not in France yet.** Cropify (Australia) sells AI lentil and chickpea grading at receival to GrainCorp, Louis Dreyfus and others, plans up to 25 units for the 2026 harvest, and was judged worth "commercial consideration" by the Grain Trade Australia Trading Standards Committee in August 2026 [gra S1, S2 V; S3 F]. Nobody publicly covers French soy or pulses: Inarix stops at wheat, durum, barley and maize [gra S4, S5 V].
2. **Soy is the right crop to build on (data exists) but the weakest crop to sell on.** The French food-vs-feed price gap for soy is "très faible" [soy S11 V], under 25 €/t in conventional (2019/20 and 2022/23) [soy S12 F], with one article quoting ~70 €/t for 2021 [soy S5 V]. Food soy is ~45 kt/yr, bought by six plants [soy S1, S5 V].
3. **Lentil is where a tonne is worth defending, but the crop is small and the problem is sorting, not food vs feed.** Food lentil 806-873 €/t [CONTEXT S23 V] vs a feed proxy of 200-260 €/t [pul S22 V]; the highest bruchid damage of the 2021-2025 survey series in 2025 (24.4 % mean per lot, 40 lots) [pul S4 V]; but national lentil value is only ~32-51 M€ [pul NV] and packers sort damaged lots back to standard rather than downgrading them [pul S13 V].
4. **As a France-only standalone company it is not viable.** The value pool is a few M€ a year across soy and pulses [NV, sections 2-3]. The realistic paths are a pulse/soy module with an incumbent channel (Inarix-type), or EU expansion before Cropify arrives. For the hackathon, that is a defensible "scaling" slide if stated honestly.

## 2. Your hypothesis, tested

> "Soy is mostly used as animal feed which is cheaper, so if we could have the exact same product but for lentils it would be profitable."

| Part of the hypothesis | What the sources say | Verdict |
|---|---|---|
| Soy is mostly feed | French soy: 402 kt produced, 45 kt (~11 %) human food, averages 2020/21-2024/25 [soy S1 V]. France also imports 544 kt of beans and 2.9 Mt of soymeal a year, for feed [soy S1 V] | True |
| Feed soy is much cheaper than food soy | Gap "très faible", <25 €/t (2019/20, 2022/23) [soy S11 V, S12 F]; ~70 €/t in 2021 [soy S5 V] | **False**: food soy barely pays more, so misgrading soy costs little |
| Lentil has a large food vs feed gap | 806-873 €/t food [CONTEXT S23 V] vs 200-260 €/t feed proxy (pea/faba feed price; no feed-lentil price exists) [pul S22 V]: ~550-620 €/t [NV] | True, with a proxy |
| So lentil would be profitable | Per tonne yes. In total, the lentil crop is ~34 kha (2024) vs ~153 kha soy [pul S1, S3 V], worth ~32-51 M€ vs ~159 M€ [pul NV]. Damaged lentil is sorted, not downgraded [pul S13 V], so the tool prices the sorting loss rather than deciding food vs feed | **Partly**: better unit economics, small market, different decision |

**Value per truck, own calculation** [NV; 28 t truck is an assumption]:

| Crop | Price gap at stake | One 28 t truck sent to the wrong outlet as a whole |
|---|---|---|
| Soy | <25 to ~70 €/t | ~560-1,960 € [soy NV]; how often this happens is undocumented |
| Pea | ~30 €/t (indicative) [CONTEXT S22 V] | ~840 € |
| Lentil | ~550-620 €/t | not how it works: lots are sorted, not downgraded |

**Correction after review (`research/critique.md`, C3):** an earlier version priced "one percentage point of grading error" on a lentil truck at ~150-175 € and derived a payback in trucks. That does not hold: at 24 % damage a 200-grain count is ±6 points and 1,000 grains still ±2.7, so a 1-point correction is not measurable; and if manual grading is unbiased, corrections only move money between farmer and collector. Value comes from decisions that change (sort, cell, contract), disputes avoided, speed at the harvest peak, and a grade the farmer can check. See the brief, section 5.

## 3. Key numbers by crop

| | Soy | Lentil | Pea | Faba bean |
|---|---|---|---|---|
| Area | 150 kha (2025), down from 187 kha (2020) [soy S4 V] | 34,216 ha (2024) [pul S1 V] | | |
| Production | ~400 kt; 298 kt forecast for 2026 [soy S8 F] | 40-59 kt (2024, estimate, no official figure) [pul NV] | 502 kt pea + faba collected (5-season average) [CONTEXT S20 V] | |
| Human food | 45 kt/yr, almost all French, under contract [soy S1, S5, S7 V] | ~45-55 % of French consumption imported [pul NV]; 2024/25 net deficit 38,282 t, up from 22,030 t in 2020/21 [pul S1 V] | 136 kt "human food and non-food ingredients" (2024/25), mostly fractionation [pul S1 V] | 11 kt domestic human food [pul S1 V] |
| Price | 596-617 €/t conventional (2022/23) [soy S12 F] | 806-873 €/t [CONTEXT S23 V] | 250 vs 280 €/t (indicative) [CONTEXT S22 V] | |
| Quality problem, 2025 | 37 % of lots >1 % green (immature) seeds, vs 11 % in 2024, "pénalisant pour le débouché en alimentation humaine"; protein 39.8 % DM, lowest in 10+ years [soy S2 V] | Mean 24.4 % bruchid-damaged (40 lots), highest of 2021-2025; 36.8 % in Centre-Ouest [pul S4 V] | Broken grains exclude the most lots [CONTEXT S9 V] | Exports to Egypt (food) fell from 245 kt to 87 kt, mainly over bruchids [pul S14 F] |
| Visible to a photo? | Green seeds: **yes** (our "immature" class). Protein: no (NIR) | Exit holes yes; larvae inside no | Broken: yes | Holes yes; larvae no |

## 4. Critiques we must be able to answer

**Market and economics**
1. **Small and seasonal.** Few M€ of value at stake across soy and pulses in France [NV]. Grading happens in a few harvest weeks.
2. **Food soy barely pays a premium** (<25 €/t, [soy S11, S12]). Soy grading is a weak business on its own.
3. **Few soy buyers who already control quality** (six plants; Olga buys 8-9 kt) [soy S5, S15 V] with variety lists, contracts and their own sorting. The grading need may sit inside a handful of plants, not hundreds of silos.
4. **Labour saved is not the value.** A manual count costs roughly 2-4 € of labour [gra NV, from ~12 €/h seasonal wages, gra S16 F]; an arbitration-lab impurity analysis is 130 € HT per lot [gra S15 V]. The value must be throughput at the harvest peak, consistency between sites, and a documented réfaction.
5. **The documented brakes on French pulses are price vs imports, yield risk, missing sorting/storage equipment and low demand** (1.6 kg/adult/yr vs ~5 kg for the PNNS guideline) [pul S7, S9, S10, S16 V]. No source names grading as the barrier.
6. **Competition.** Cropify is the same product, already recognised by Grain Trade Australia, expanding to Canada and the US [gra S1 V]. Inarix is in ~600 silos and could add soy or pulses on its licence-plus-credits model [gra S5, S7 V]. Ground Truth Ag has peas, lentils, soybean and faba "in development" (~CAD 15k + 1.5k/yr) [gra S8, S9 V].

**Science and measurement**
7. **A photo undercounts bruchid damage:** LABOSEM found 3.8-4.1 % visual vs 11.8-13.5 % by dissection in pea [gra S14 V]. It measures emergence, not infestation.
8. **The contractual reference stays human.** In the US, the FGIS approved Cgrain for a single rice factor with heavy QA, and appeals are still handpicked [gra S13 V]. A phone tool is a pre-screen until an Incograin-type body accepts it.
9. **No French numeric spec for food soy defects** (broken, split, stained, hilum) is public [soy S6 V], and the national observatory does not measure broken or stained soy [soy S2 V]. There is no French baseline showing those defects are common.
10. **Phones vary.** Inarix restricts wheat broken-grain analysis to two phone models and runs daily calibration sites [gra S5, S17 V].
11. **2025 was an extreme year** for both lentil bruchids and soy green seeds. A business case built only on 2025 overstates a normal year.

**Hackathon fit**
12. **Soy reads as feed.** ~89 % of French soy and nearly all imports are feed [soy S1, S3 V]. Say "food-grade soy" in the first sentence.

## 5. What would make it really useful

1. **Pick the defect that decides money and is visible.** For soy: green/immature seeds (2025's food-limiting factor [soy S2]). For lentil: pricing the bruchid sorting loss at reception. For pea: broken grains.
2. **Real French data:** labelled photos from intake desks across several harvests and sites, labelled by graders (agréeurs).
3. **Calibration against the reference method** (LABOSEM visual count, and dissection or X-ray for infestation), reported as bias and interval, per crop.
4. **A fixed capture protocol:** a cheap light box or mat, a short list of supported phones, daily check samples (as FGIS and Inarix do).
5. **Industry acceptance:** Incograin or Terres Inovia recognition, the route Cropify took with GTA.
6. **Combine with what buyers price on:** protein and moisture come from NIR at the same desk, so integrate with the intake software or the Inarix-type app, rather than being one more device.
7. **A channel:** a partner already at the intake desk (Inarix, cooperative software vendors) or the six soy-food plants as a first, concentrated customer base.

## 6. What changes for the pitch

- **Drop "no tool exists for pulses".** Say: "AI grading of pulses already sells in Australia (Cropify, judged worth "commercial consideration" by Grain Trade Australia in 2026). Nobody covers French soy or pulses." That turns a weakness into market proof.
- **Soy hook:** 37 % of 2025 French soy lots had >1 % green seeds, penalising for the food outlet [soy S2]. "Immature" is one of our classes.
- **Lentil as the scaling case:** the price gap (~550-620 €/t), the import gap (38 kt), the highest bruchid damage of the 2021-2025 survey series; value framed as decisions changed, disputes avoided and a grade the farmer can check, not € per point (see the correction in section 2).
- **Value proposition:** consistency and speed at the harvest peak, a documented réfaction the producer can check, not labour saved.
- **Limits slide:** photo undercounts infestation; not a contractual reference; no French field data yet.

## 7. Corrections to make in `CONTEXT.md` and the README (not applied yet)

| Where | Current claim | Correction |
|---|---|---|
| README "Why"; CONTEXT §11 pitch row 3:10, §11 Q&A "Inarix", §12, claim #48 | "we found no tool doing it for pulses" | Cropify grades lentil and chickpea commercially in Australia [gra S1, S2]; Ground Truth Ag has pulses in development [gra S8] |
| CONTEXT §12 competitor table | No Cropify, Ground Truth Ag; Cgrain "not verified" | Add both; Cgrain small grains only, FGIS approval for one rice factor [gra S10, S13] |
| CONTEXT §3 "Soybean for human food" | Only 402/45 kt | Add the thin food premium [soy S11, S12], six plants [soy S5], 2025 green seeds and protein [soy S2] |
| CONTEXT §3 "We did not find the cost of manual inspection" | Not found | Arbitration-lab impurity analysis 130 € HT per lot [gra S15 V]; labour per count ~2-4 € [gra NV] |
| Track context, 2030 target | "double ~4 %" (guide) | The guide's wording stands for the pitch; note the 2020 strategy said 8 % of UAA (2 Mha) and FranceAgriMer (July 2026) says 10 % (~2.7 Mha) [pul S10, S11 V] |

## 8. Still open

- Current food-grade thresholds in Incograin contracts for pulses and soy (members only) [gra S21].
- A French price for downgraded or feed lentil, and any réfaction grid [pul].
- Official 2024-2025 lentil and chickpea tonnage [pul].
- LABOSEM and Eurofins analysis prices [gra].
- Whether Inarix has a pulse or soy defect product in the pipeline (ask a mentor or Inarix directly).
