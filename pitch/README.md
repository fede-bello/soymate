# Pitch

4 minutes, then 2 minutes of questions, strictly timed. Structure required by the guide: problem, solution, live demo, scaling. Submission (PDF on the official template, with the link to the code or demo) before Sunday 1/11, 9:30.

**Deck (draft, editable):** https://claude.ai/artifact/AiZ254A4Y2tTDnwKEr5GH2 (private to Fede until shared). `slides/` holds a backup copy of its files (one HTML per slide, `deck.json` gives the order); the online deck is the one to edit. Port the content to the official template when the organisers send it.

## Outline (13 slides, ~5.5 min: must be cut to 4)

| # | Slide | Message | To fill |
|---|---|---|---|
| 1 | Cover | A seed grade from a phone photo, that the farmer can check too | Team names |
| 2 | Problem: damage | 1 seed in 4 damaged in an average French lentil truckload (2025), from 1 % to 75 % between trucks | |
| 3 | Problem: counted by eye | Counted by hand, different people get different results, the farmer can't check | |
| 4 | Problem: money | ~550 €/t food vs feed; up to 5-8 M€ lost to sorting in 2025; 38 kt net imports | |
| 5 | How a better count changes things | Damage → sets the price → counted by eye → SoyMate: same photo count for both sides | |
| 6 | Why soybean first | Soy has public data, lentil has the money (20-70 vs ~550 €/t) | |
| 7 | What we built | Photo → find → check → answer (pass / more photos / fail) | App screenshot |
| 8 | Live demo | Upload, look, be strict | Live app, backup video link |
| 9 | How much you can trust it | We found a flaw in the public data; what a photo can't see; how many seeds are enough | Error on real photos, dataset check |
| 10 | What changes | Today vs with SoyMate | |
| 11 | Four conditions for lentil | Lentil photos, enough seeds, tested against experts, a trial with one cooperative | N seeds per class (from the transfer curve) |
| 12 | Room to make money | People pay in Australia, nobody in France, every tonne counts, phone only | |
| 13 | Next step | One cooperative, one lentil harvest | Contact, repo or demo link |

**Proposed cuts to reach 4 minutes:** drop slide 10 (keep the table for Q&A), merge slides 3 and 4, shorten slide 6 to its first and last rows. The demo keeps its full minute.

## Rules for the numbers

- Never say a number we did not measure: every `[X]`, `[N]` is filled from our own results or the line is cut.
- Say "1 seed in 4 **in an average truckload**" (the survey gives a mean per lot, not a share of all lentils).
- Say Cropify was judged worth "commercial consideration" by Grain Trade Australia, not "endorsed".
- No subscription prices or ROI numbers in the pitch; they are in the brief (`docs/soymate_viability_brief.pdf`, section 6) for Q&A.

## Q&A prep

| Question | Answer |
|---|---|
| Is the model just recognising which dataset a seed came from? | We tested it: [result]. That is why we report each class within its own dataset and measure error on real photos. |
| Have you tried it on lentils? | Not yet: there is no public labelled lentil data. That is the next step, and our transfer curve says how many labelled seeds it needs: [N] per class. |
| Isn't this Inarix or Cropify? | Cropify proves buyers pay, in Australia, with a unit at the sample stand. Inarix grades cereals. Nobody covers French soy or pulses, and we need only a phone. |
| Grading isn't what holds French pulses back. | Agreed: demand and price matter more. We don't claim more demand. We give farmers a grade they can check, which protects their income (the Track 3 question). |
| Is this animal feed? | No. We target food-grade soy and lentils; the decision is about keeping lots in the food outlet. |
| Does it see the larvae? | No, and neither does the visual reference method: cutting pea seeds open found about 3 times more damage than looking (LABOSEM). |
| Isn't a better grade just money moved from farmer to collector? | Partly, yes. The value comes from decisions that change (clean first, which buyer, which storage), fewer disputes, and speed at harvest. A pilot measures how often that happens. |

Before the pitch: get written confirmation from the organisers on the "Insects" and "animal feed" exclusions, and record the demo video.
