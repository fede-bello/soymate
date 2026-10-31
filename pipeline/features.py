"""Frozen DINOv2 features for every crop in data/crops/manifest.csv, cached for all experiments.

Run on the box:  cd ~/soymate-next && uv run python pipeline/features.py [--model facebook/dinov2-small] [--full-soybean]
Writes data/features/<model_tag>__crops.parquet (key = crop path; CLS + mean-patch features). Re-running
embeds only crops not cached yet.
--full-soybean also embeds the uncropped d97rjyk2tz images (background and printed date included), which is
the "as published" input for the leaky arm of R1: data/features/<model_tag>__soybean_full.parquet.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel

ROOT = Path(__file__).resolve().parents[1]
CROPS = ROOT / "data" / "crops"
FEATS = ROOT / "data" / "features"
SOY_V2 = ROOT / "data" / "raw" / "soybean_v2" / "Soybean_Seed_Dataset" / "Soybean_Seed_Dataset"


@torch.inference_mode()
def embed(paths: list[Path], model_name: str, batch: int = 64) -> np.ndarray:
    proc = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).eval()
    out = []
    for i in range(0, len(paths), batch):
        ims = [Image.open(p).convert("RGB") for p in paths[i:i + batch]]
        h = model(**proc(images=ims, return_tensors="pt")).last_hidden_state
        out.append(torch.cat([h[:, 0], h[:, 1:].mean(1)], dim=1).numpy())  # CLS + mean patch token
        print(f"{model_name}: {min(i + batch, len(paths))}/{len(paths)}", flush=True)
    return np.concatenate(out).astype(np.float32)


def update(keys: pd.Series, root: Path, model_name: str, path: Path) -> None:
    """Embed only keys not already cached in path, then rewrite it."""
    old = pd.read_parquet(path) if path.exists() else None
    todo = keys[~keys.isin(old["key"])] if old is not None else keys
    if len(todo):
        X = embed([root / k for k in todo], model_name)
        new = pd.DataFrame(X, columns=[f"f{j}" for j in range(X.shape[1])])
        new.insert(0, "key", todo.to_numpy())
        old = new if old is None else pd.concat([old, new], ignore_index=True)
        FEATS.mkdir(parents=True, exist_ok=True)
        old.to_parquet(path, index=False)
    print(f"{path.name}: {len(old)} rows ({len(todo)} new)", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="facebook/dinov2-small")
    ap.add_argument("--full-soybean", action="store_true")
    a = ap.parse_args()
    tag = a.model.split("/")[-1]
    m = pd.read_csv(CROPS / "manifest.csv", keep_default_na=False)
    m = m[m["crop"] != ""].drop_duplicates("crop")
    update(m["crop"], CROPS, a.model, FEATS / f"{tag}__crops.parquet")
    if a.full_soybean:
        s = pd.read_csv(ROOT / "data" / "splits" / "soybean.csv", keep_default_na=False)
        update(s["image"], SOY_V2, a.model, FEATS / f"{tag}__soybean_full.parquet")
