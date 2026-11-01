# Pitch

4 minutes, then 2 minutes of questions, strictly timed. Structure required by the guide: problem, solution, live demo, scaling. Submission (PDF on the official template, with the link to the code or demo) before Sunday 1/11, 9:30.

**Deck (draft, editable):** https://claude.ai/artifact/AiZ254A4Y2tTDnwKEr5GH2 (private to Fede until shared). `slides/` holds a backup copy of its files (one HTML per slide, `deck.json` gives the order); the online deck is the one to edit. Port the content to the official template when the organisers send it.

## Outline (12 slides + 1 backup, ~4:00 spoken)

Order: cover, problem, measurement, stakes, chain, whysoy, solution, demo (60 s), trust (30 s), conditions,
market, close; `change` moved after the close as a backup slide for questions. Timings are in each slide's
speaker notes. All numbers on the slides come from `results/README.md` or the sources named on each slide.

**Still to fill before submitting** (team names and contact are done): the code link (close; the GitHub
repo is private), and the backup video link (demo). Record the video from the live app while it runs.

**Demo script:** open http://18.206.176.19, click the Ghana farmer-saved example (counting: 164 of 164),
then "Harvester camera, packed lot 1" (opens in Bulk mode: 6.5 % defects, range 2.8 to 14.3 %, "not sure yet"
at 5 %), then move the limit to 15 % (pass) and 2 % (fail). Do not present the Ghana defect % (uncalibrated on
that camera setup); use Ghana for the count only.

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

Before the pitch: get written confirmation from the organisers on the "Insects" and "animal feed" exclusions, and record the demo video.
