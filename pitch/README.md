# Pitch

4 minutes, then 2 minutes of questions, strictly timed. Structure required by the guide: problem, solution, live demo, scaling. Submission (PDF on the official template, with the link to the code or demo) before Sunday 1/11, 9:30.

**Deck online:** https://claude.ai/artifact/AiZ254A4Y2tTDnwKEr5GH2

**Deck in this repo (anyone can view and edit):** open [`deck/index.html`](deck/index.html) in a browser. It is
self-contained: slides, images and the demo video are in `deck/` (`deck/assets/`); fonts load from Google Fonts.
Keys: ← → (or click) to move, `N` speaker notes, `F` full screen; `#8` in the URL opens slide 8. Print to PDF from
the browser (one slide per page, 1920×1080) for the submission.

**To edit it** (text, slides, images, the demo video, keeping the online deck in sync): see
[`EDITING.md`](EDITING.md). In short: change the slide in `slides/`, run `python3 pitch/build_deck.py` from the
repo root, reload `deck/index.html`, commit both.

## Outline (11 slides, ~4:00 spoken)

Order: cover, problem, measurement, stakes, chain, whysoy, solution, demo (45 s), conditions, market, close.
Timings are in each slide's speaker notes. All numbers on the slides come from `results/README.md` or the sources
named on each slide. Team: Federico Bello, Juan Pedro Maestrone, Pedro Pertusso (soymate.team@gmail.com).

**Demo video:** `deck/assets/demo.mp4` (27 s, recorded from the live app), played on the demo slide: the Ghana
farmer-saved example (all 164 seeds found, 18 broken, 11 %, fail at 5 %), then the single seed labelled insect
hole (insect hole, 100 %, matches the label).

**Live demo script:** open http://18.206.176.19, click the Ghana farmer-saved example (counting: 164 of 164),
then the single bean "labelled insect hole". Do not present the Ghana defect % as calibrated (uncalibrated on
that camera setup); the count is the strong claim.

## Rules for the numbers

- Never say a number we did not measure: every `[X]`, `[N]` is filled from our own results or the line is cut.
- Say "1 seed in 4 **in an average truckload**" (the survey gives a mean per lot, not a share of all lentils).
- Say Cropify was judged worth "commercial consideration" by Grain Trade Australia, not "endorsed".
- No subscription prices or ROI numbers in the pitch; they are in the brief (`docs/soymate_viability_brief.pdf`, section 6) for Q&A.

## Q&A prep

| Question | Answer |
|---|---|
| Is the model just recognising which dataset a seed came from? | It can: a probe tells the two datasets apart 100 % of the time, even from the seed surface alone. That is why we score each dataset on its own, and why holes were checked on the days with both classes (F1 0.97; 0.96 when trained on other days). |
| Have you tried it on lentils? | Not yet: there is no public labelled lentil data. Our transfer test says local labels matter most: 50 seeds per type from the new setup scored 0.93 macro F1, 1,000 from another dataset scored 0.52. |
| Isn't this Inarix or Cropify? | Cropify proves buyers pay, in Australia, with a unit at the sample stand. Inarix grades cereals. Nobody covers French soy or pulses, and we need only a phone. |
| Grading isn't what holds French pulses back. | Agreed: demand and price matter more. We don't claim more demand. We give farmers a grade they can check, which protects their income (the Track 3 question). |
| Is this animal feed? | No. We target food-grade soy and lentils; the decision is about keeping lots in the food outlet. |
| How wrong is it on one seed? | Often: broken vs sound is F1 0.67 across all capture sessions, and on packed lots crushed seeds are found at F1 0.48 per seed. The lot share is closer (within 1.5 points) because errors partly cancel, which is why we always show the range and say "not sure yet". |
| Does it see the larvae? | No, and neither does the visual reference method: cutting pea seeds open found about 3 times more damage than looking (LABOSEM). |
| Isn't a better grade just money moved from farmer to collector? | Partly, yes. The value comes from decisions that change (clean first, which buyer, which storage), fewer disputes, and speed at harvest. A pilot measures how often that happens. |

Before the pitch: get written confirmation from the organisers on the "Insects" and "animal feed" exclusions.
