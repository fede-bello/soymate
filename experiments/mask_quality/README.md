# experiments/mask_quality/ (experiment B)

Question: does a better seed mask than the chroma mask (`pipeline/make_crops.seed_mask`) improve soybean
classification, especially the weak "broken" class? Data: the 2121 soybean d97rjyk2tz single-seed images
of R2, same burst-level split, same test reps (one crop per photo, multi-seed excluded).

## Run (on the box, in `~/soymate-exp`, venv from `uv sync --locked --group baseline`)

```bash
mkdir -p weights && curl -fL https://github.com/ultralytics/assets/releases/download/v8.3.0/FastSAM-s.pt -o weights/FastSAM-s.pt
# sha256 c9f78716a81c7aff0d608ccc73e1b82ab3aaad86005049f6a92106a0be6d0844 (docs/fastsam_grain_experiment.md)
export OMP_NUM_THREADS=6
.venv/bin/python experiments/mask_quality/make_masks.py     # masks + crops under data/exp_masks/ (~7 min)
.venv/bin/python experiments/mask_quality/contact_sheet.py  # data/exp_masks/qc/*.png
.venv/bin/python experiments/mask_quality/embed.py          # dinov2-small features per arm
.venv/bin/python experiments/mask_quality/evaluate.py       # results/mask_quality.json + CSVs
```

Ultralytics needs libGL on Amazon Linux (`sudo dnf install -y mesa-libGL`). Everything new is written under
`data/exp_masks/`; `data/crops/` and `data/features/` are only read.

| File | What |
|---|---|
| `make_masks.py` | Chroma and FastSAM-s masks per image, crops for the arms `fastsam`, `fastsam_dil`, `nomask`, `masks.csv` (IoU, areas, latency) |
| `embed.py` | Frozen dinov2-small CLS + mean patch (`pipeline/features.embed`) for each new arm |
| `contact_sheet.py` | Eye check: 16 lowest-IoU images, 16 broken disagreements, 16 random broken seeds |
| `evaluate.py` | R2 fixed split and grouped 5-fold CV over bursts per arm; paired burst bootstrap and McNemar vs the current arm |

## Arms

1. `current`: chroma mask, existing crops and features.
2. `fastsam`: FastSAM-s (imgsz 640, conf 0.4, retry 0.1, NMS IoU 0.9, retina masks). Among masks covering
   0.5-90 % of the image, the one with the highest IoU against the chroma mask; holes filled, largest
   component. Background painted FILL. Images with no FastSAM mask of IoU >= 0.2 fall back to chroma.
3. `fastsam_dil`: arm 2 dilated by 4 % of the seed's equivalent diameter.
4. `nomask`: the same square crop around the FastSAM seed, real background kept (control; background
   differs by capture session, so this arm can use a shortcut).

Arm 5 (another segmenter, e.g. Cellpose or MobileSAM) was not run.

## Results

`results/mask_quality.json` (+ `__f1`, `__paired`, `__masks`, `__predictions` CSVs).

**Mask quality.** FastSAM vs chroma IoU: median 0.92, mean 0.89, 5th percentile 0.72. 38.8 % of images
disagree by more than 10 % (1 - IoU > 0.10). There were 0 fallbacks to chroma. Eye check of the lowest-IoU images:
chroma is usually the wrong one (it cuts off bright desaturated seed areas and the hilum and takes in soft
shadows), and FastSAM is wrong on hard dark shadows and on notches at the photo border. FastSAM latency: 0.062 s
median, 0.105 s p95 per 640 px image (CPU, 6 threads).

**Classification** (F1 [95 % CI]; R2 = fixed split, 132 test reps in 19 bursts; CV = grouped 5-fold over
bursts, 985 eval reps in 131 bursts):

| Arm | R2 broken | R2 sound | R2 macro | CV broken | CV sound | CV macro |
|---|---|---|---|---|---|---|
| current | 0.82 [0.77, 0.88] | 0.82 [0.73, 0.93] | 0.88 [0.85, 0.93] | 0.67 [0.60, 0.74] | 0.82 [0.79, 0.85] | 0.83 [0.80, 0.85] |
| fastsam | 0.80 [0.69, 0.87] | 0.77 [0.69, 0.88] | 0.86 [0.81, 0.91] | 0.69 [0.62, 0.76] | 0.83 [0.80, 0.86] | 0.84 [0.81, 0.86] |
| fastsam_dil | 0.83 [0.69, 0.90] | 0.85 [0.79, 0.91] | 0.89 [0.84, 0.93] | 0.68 [0.61, 0.75] | 0.83 [0.80, 0.85] | 0.83 [0.80, 0.86] |
| nomask | 0.77 [0.67, 0.86] | 0.74 [0.66, 0.87] | 0.84 [0.79, 0.90] | 0.67 [0.60, 0.74] | 0.82 [0.78, 0.86] | 0.83 [0.80, 0.86] |

Insect_hole is 1.00 in R2 and 0.99 in CV for every arm.

**Paired vs current** (difference [95 % CI], burst bootstrap; McNemar exact p):

| Arm | R2 broken | R2 macro | R2 McNemar | CV broken | CV macro | CV McNemar |
|---|---|---|---|---|---|---|
| fastsam | -0.02 [-0.15, 0.03] | -0.02 [-0.09, 0.02] | 0.66 | +0.02 [-0.01, 0.04] | +0.01 [-0.01, 0.02] | 0.36 |
| fastsam_dil | +0.01 [-0.15, 0.07] | +0.01 [-0.08, 0.06] | 0.81 | +0.01 [-0.03, 0.04] | +0.01 [-0.02, 0.02] | 0.60 |
| nomask | -0.05 [-0.15, 0.03] | -0.04 [-0.10, 0.02] | 0.31 | -0.00 [-0.04, 0.04] | +0.00 [-0.02, 0.03] | 0.75 |

**Reading.** Headline protocol: grouped 5-fold CV, because the fixed test has only 19 bursts. No arm has a
paired CI that excludes 0 in either protocol. FastSAM gains at most about +0.02 broken F1 under CV, and that is
within noise. Removing the mask (nomask) does not lose broken-edge information either. Decision rule not met:
keep the chroma mask in the demo. The broken class is limited by something other than the mask (label noise
or within-class variety; CV broken 0.67 vs 0.82 on the fixed test also shows how optimistic the 19-burst
test is).

## Licence

FastSAM and Ultralytics are AGPL-3.0 (the FastSAM README separately says Apache 2.0 for the model; see
`docs/fastsam_grain_experiment.md`). Shipping it in the demo API would put the served code under AGPL terms.
