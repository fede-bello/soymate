"""Experiment B, step 2: dinov2-small features (CLS + mean patch, pipeline/features.embed) for the new crop arms.

Run on the box after make_masks.py:  cd ~/soymate-exp && OMP_NUM_THREADS=6 .venv/bin/python experiments/mask_quality/embed.py
Writes data/exp_masks/features/dinov2-small__<arm>.parquet (key = crop path, same naming as data/crops/).
"""
import sys
from pathlib import Path

import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))
from features import embed  # noqa: E402

EXP = ROOT / "data" / "exp_masks"
ARMS = ["fastsam", "fastsam_dil", "nomask"]

if __name__ == "__main__":
    torch.set_num_threads(6)
    keys = pd.read_csv(EXP / "masks.csv")["exp_crop"]
    for arm in sys.argv[1:] or ARMS:
        out = EXP / "features" / f"dinov2-small__{arm}.parquet"
        if out.exists():
            print("exists", out, flush=True)
            continue
        X = embed([EXP / "crops" / arm / k for k in keys], "facebook/dinov2-small")
        df = pd.DataFrame(X, columns=[f"f{j}" for j in range(X.shape[1])])
        df.insert(0, "key", keys.to_numpy())
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out, index=False)
        print("wrote", out, len(df), flush=True)
