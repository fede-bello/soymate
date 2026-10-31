"""Dataset-ID check (critique C1 fixes 1 and 2): does the representation encode the source dataset?

Run on the box:  cd ~/soymate && OMP_NUM_THREADS=4 uv run python eval/dataset_id.py [--features dinov2-small]
Writes results/dataset_id.json (+ CSVs).

(1) Probe: soybean d97rjyk2tz vs Lin v6vzvfszj6 from features of SOUND seeds only (and, as a second check, BROKEN
    seeds only, the other class both sets share). Same protocol as R2: fit on train, C on val reps, test reps.
    Accuracy with Wilson CI, AUC with grouped bootstrap CI.
    Texture-only variant: Lin crops touch the frame and fill more of it, so the outline alone separates datasets.
    The sound probe is repeated on features of the central 50 % x 50 % patch of each sound crop (outline gone),
    embedded on the fly and cached in data/features/<model>__sound_center50.parquet.
(2) Cross-dataset false positives: the pooled 5-class R2 model applied to test sound seeds of each dataset;
    % predicted as any defect (Wilson CI), and how many land in a class that exists only in the other dataset.
"""
import argparse

import numpy as np
import pandas as pd

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel

import harness as H
from r2_per_class import LIN, SOY, C_GRID, boot_auc, fit_select, rep

ONLY_SOY, ONLY_LIN = {"insect_hole"}, {"stained", "immature"}


def boot_mean(x, groups, n_boot: int = H.N_BOOT, seed: int = H.SEED) -> list[float]:
    """95 % percentile CI of a mean, resampling whole groups (soybean bursts, Lin clusters)."""
    x, groups = np.asarray(x, float), np.asarray(groups)
    uniq = np.unique(groups)
    idx_by = {g: np.nonzero(groups == g)[0] for g in uniq}
    rng = np.random.default_rng(seed)
    d = [x[np.concatenate([idx_by[g] for g in rng.choice(uniq, len(uniq), replace=True)])].mean()
         for _ in range(n_boot)]
    return [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]


def probe(df: pd.DataFrame, cls: str) -> dict:
    d = df[df["class"] == cls].assign(source=lambda x: x.dataset)
    m, c, val = fit_select(d, "source")
    te = rep(d[d.split == "test"])
    pred = H.predict(m, te)
    k, n = int((pred == te.source).sum()), len(te)
    p = m.predict_proba(te)[:, list(m.classes_).index(SOY)]
    return {"C": c, "val_macro_f1_by_C": val, "n_test_reps": n, "test_counts": te.source.value_counts().to_dict(),
            "accuracy": round(k / n, 4), "accuracy_wilson95": [round(x, 4) for x in H.wilson(k, n)],
            "accuracy_grouped_boot95": boot_mean(pred == te.source.to_numpy(), te.group.to_numpy()),
            "n_test_groups": int(te.group.nunique()),
            "auc": boot_auc(te.source.to_numpy() == SOY, p, te.group.to_numpy()),
            "confusion": H.confusion(te.source, pred, [SOY, LIN])}


HF = {"dinov2-small": "facebook/dinov2-small", "dinov2-base": "facebook/dinov2-base"}


@torch.inference_mode()
def center_features(keys: pd.Series, feats: str, frac: float = 0.5) -> pd.DataFrame:
    """CLS + mean-patch DINOv2 features of the central frac x frac patch of each crop (same recipe as features.py)."""
    path = H.FEATS / f"{feats}__sound_center{int(frac * 100)}.parquet"
    old = pd.read_parquet(path) if path.exists() else pd.DataFrame({"key": []})
    todo = keys[~keys.isin(old["key"])].drop_duplicates()
    if len(todo):
        proc, model = AutoImageProcessor.from_pretrained(HF[feats]), AutoModel.from_pretrained(HF[feats]).eval()
        out = []
        for i in range(0, len(todo), 64):
            ims = []
            for k in todo.iloc[i:i + 64]:
                im = Image.open(H.CROPS / k).convert("RGB")
                w, h = im.size
                dw, dh = int(w * (1 - frac) / 2), int(h * (1 - frac) / 2)
                ims.append(im.crop((dw, dh, w - dw, h - dh)))
            hs = model(**proc(images=ims, return_tensors="pt")).last_hidden_state
            out.append(torch.cat([hs[:, 0], hs[:, 1:].mean(1)], dim=1).numpy())
        X = np.concatenate(out).astype(np.float32)
        new = pd.DataFrame(X, columns=[f"f{j}" for j in range(X.shape[1])]).assign(key=todo.to_numpy())
        old = pd.concat([old, new], ignore_index=True) if len(old) else new
        old.to_parquet(path, index=False)
    return old


def center_fill(keys: pd.Series, frac: float = 0.5) -> list[float]:
    """Share of central-patch pixels that are not the neutral grey fill, per dataset (sanity: patch is all seed)."""
    vals = []
    for k in keys:
        a = np.asarray(Image.open(H.CROPS / k).convert("RGB")).astype(int)
        h, w = a.shape[:2]
        c = a[int(h * (1 - frac) / 2):h - int(h * (1 - frac) / 2), int(w * (1 - frac) / 2):w - int(w * (1 - frac) / 2)]
        vals.append(float((np.abs(c - np.array([124, 116, 104])).sum(-1) > 6).mean()))
    return vals


def texture_probe(df: pd.DataFrame, feats: str) -> dict:
    meta = df[df["class"] == "sound"].drop(columns=H.feature_cols(df))
    f = center_features(meta["crop"], feats)
    d = meta.merge(f, left_on="crop", right_on="key", how="inner").drop(columns="key")
    res = probe(d, "sound")
    te = rep(d[d.split == "test"]).copy()
    te["fill"] = center_fill(te["crop"])
    res["central_patch_seed_fraction_test"] = {ds: {"mean": round(g.fill.mean(), 4), "min": round(g.fill.min(), 4)}
                                               for ds, g in te.groupby("dataset")}
    return res


def cross_fp(df: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    m, c, _ = fit_select(df)
    te = rep(df[(df.split == "test") & (df["class"] == "sound")])
    te = te.assign(pred=H.predict(m, te))
    out, rows = {"C": c}, []
    for ds, g in te.groupby("dataset"):
        n, k = len(g), int((g.pred != "sound").sum())
        other = ONLY_LIN if ds == SOY else ONLY_SOY
        ko = int(g.pred.isin(other).sum())
        out[ds] = {"n_sound_test_reps": n, "pct_pred_defect": round(100 * k / n, 2),
                   "pct_pred_defect_wilson95": [round(100 * x, 2) for x in H.wilson(k, n)],
                   "pct_pred_defect_grouped_boot95": [round(100 * v, 2) for v in
                                                      boot_mean(g.pred != "sound", g.group.to_numpy())],
                   "n_groups": int(g.group.nunique()),
                   "pct_pred_other_dataset_only_class": round(100 * ko / n, 2),
                   "pct_pred_other_dataset_only_class_wilson95": [round(100 * x, 2) for x in H.wilson(ko, n)],
                   "pred_counts": g.pred.value_counts().to_dict()}
        rows += [{"dataset": ds, "pred": p, "n": v} for p, v in g.pred.value_counts().items()]
    return out, pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", nargs="+", default=["dinov2-small"])
    args = ap.parse_args()
    feats = [f for f in args.features if (H.FEATS / f"{f}__crops.parquet").exists()]
    res, probe_rows, fp_tabs = {}, [], []
    for f in feats:
        df = H.load(f)
        res[f] = {"probe_sound": probe(df, "sound"), "probe_broken": probe(df, "broken"),
                  "probe_sound_texture_center50": texture_probe(df, f)}
        res[f]["cross_dataset_false_positive"], t = cross_fp(df)
        fp_tabs.append(t.assign(features=f))
        for cls in ("sound", "broken", "sound_texture_center50"):
            r = res[f][f"probe_{cls}"]
            probe_rows.append({"features": f, "class": cls, "n_test": r["n_test_reps"], "accuracy": r["accuracy"],
                               "acc_lo": r["accuracy_grouped_boot95"][0], "acc_hi": r["accuracy_grouped_boot95"][1],
                               "auc": r["auc"]["auc"], "auc_lo": r["auc"]["ci95"][0], "auc_hi": r["auc"]["ci95"][1]})
        print(f, probe_rows[-3:], res[f]["cross_dataset_false_positive"], flush=True)
    H.write_result("dataset_id", res, (
        f"Frozen {'/'.join(feats)} features of masked seed crops, harness.FrozenLogReg. Probe: binary source "
        "label (soybean_d97rjyk2tz vs lin_v6vzvfszj6) using only crops of one shared class (sound; broken as a "
        f"second check); texture-only variant: sound crops cut to their central 50%x50% patch (outline and "
        "frame contact removed), re-embedded with the same DINOv2 recipe (CLS + mean patch); fit on split=train, C from {C_GRID} by macro F1 on split=val eval_rep, refit on train, "
        "scored on split=test eval_rep (one crop per group). Accuracy with Wilson 95% CI and a group bootstrap CI (soybean groups = 30 s bursts); AUC with percentile "
        "bootstrap over groups (2000, seed 0). Cross-dataset false positives: pooled 5-class model (same protocol "
        "as r2_per_class pooled_5class) applied to test eval_rep sound crops of each dataset; % predicted as any "
        "non-sound class and % predicted as a class that exists only in the other dataset, Wilson 95% CIs. "
        "multi_seed=True rows excluded from val/test scoring."),
        {"probe": pd.DataFrame(probe_rows), "cross_fp_pred_counts": pd.concat(fp_tabs)})


if __name__ == "__main__":
    main()
