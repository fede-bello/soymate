"""Experiment B, step 3: does a FastSAM seed mask beat the chroma mask for soybean classification?

Run on the box after make_masks.py and embed.py:
    cd ~/soymate-exp && OMP_NUM_THREADS=6 .venv/bin/python experiments/mask_quality/evaluate.py
Writes results/mask_quality.json (+ CSVs) via harness.write_result.

Arms (same 2121 soybean d97rjyk2tz rows as R2, same split, same test reps):
  current      chroma mask, existing data/features/dinov2-small__crops.parquet
  fastsam      FastSAM-s mask, background FILL
  fastsam_dil  FastSAM-s mask dilated by 4 % of the seed's equivalent diameter
  nomask       square crop around the FastSAM seed, real background kept
Protocols: (1) R2 exactly (experiments/r2_per_class.evaluate: fit train, C on val reps, test reps, multi_seed
excluded); (2) grouped 5-fold CV over bursts on all rows, C chosen inside folds (r2_per_class.cv_evaluate logic,
out-of-fold predictions kept for pairing). Paired comparisons vs current on identical eval crops: bootstrap over
bursts (both arms scored on the same resample) for every per-class F1 and macro F1, plus exact McNemar on
per-crop correctness.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from statsmodels.stats.contingency_tables import mcnemar

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
import harness as H  # noqa: E402
import r2_per_class as R2  # noqa: E402

EXP = ROOT / "data" / "exp_masks"
ARMS = ["current", "fastsam", "fastsam_dil", "nomask"]
LABELS = ["broken", "insect_hole", "sound"]


def load_arm(arm: str, base: pd.DataFrame) -> pd.DataFrame:
    if arm == "current":
        return base
    f = pd.read_parquet(EXP / "features" / f"dinov2-small__{arm}.parquet")
    meta = base[[c for c in base.columns if c not in H.feature_cols(base)]]
    d = meta.merge(f, left_on="crop", right_on="key", how="inner").drop(columns="key")
    assert len(d) == len(base), (arm, len(d), len(base))
    return d.set_index("crop").loc[base["crop"]].reset_index()  # identical row order -> identical CV folds


def cv_oof(d: pd.DataFrame, k: int = 5) -> tuple[pd.DataFrame, list]:
    """r2_per_class.cv_evaluate, returning the pooled out-of-fold predictions on eval reps."""
    d = d.reset_index(drop=True)
    outer = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=H.SEED)
    oof, cs = [], []
    for fold, (tri, tei) in enumerate(outer.split(d, d["class"], d["group"])):
        tr, te = d.iloc[tri], R2.rep(d.iloc[tei])
        inner = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=H.SEED)
        score = {c: [] for c in R2.CV_GRID}
        for a, b in inner.split(tr, tr["class"], tr["group"]):
            ia, ib = tr.iloc[a], R2.rep(tr.iloc[b])
            for c in R2.CV_GRID:
                m = H.MODELS["logreg"](C=c).fit(ia, ia["class"].to_numpy())
                score[c].append(H.per_class_f1(ib["class"], H.predict(m, ib), LABELS)["macro"])
        c = max(R2.CV_GRID, key=lambda c: (round(float(np.mean(score[c])), 4), -c))
        m = H.MODELS["logreg"](C=c).fit(tr, tr["class"].to_numpy())
        oof.append(te[["crop", "group", "class", "background"]].assign(pred=H.predict(m, te), fold=fold))
        cs.append(c)
    return pd.concat(oof, ignore_index=True), cs


def paired(a: pd.DataFrame, b: pd.DataFrame, n_boot: int = H.N_BOOT, seed: int = H.SEED) -> dict:
    """Arm b minus arm a on the same crops: per-class and macro F1 differences, burst bootstrap, McNemar."""
    m = a[["crop", "group", "class", "pred"]].merge(b[["crop", "pred"]], on="crop", suffixes=("_a", "_b"))
    assert len(m) == len(a) == len(b)
    y, pa, pb, g = (m[c].to_numpy() for c in ("class", "pred_a", "pred_b", "group"))
    uniq = np.unique(g)
    idx_by = {u: np.nonzero(g == u)[0] for u in uniq}
    fa, fb = H.per_class_f1(y, pa, LABELS), H.per_class_f1(y, pb, LABELS)
    rng, draws = np.random.default_rng(seed), {k: [] for k in fa}
    for _ in range(n_boot):
        idx = np.concatenate([idx_by[u] for u in rng.choice(uniq, len(uniq), replace=True)])
        da, db = H.per_class_f1(y[idx], pa[idx], LABELS), H.per_class_f1(y[idx], pb[idx], LABELS)
        for k in draws:
            draws[k].append(db[k] - da[k])
    out = {k: {"diff": round(fb[k] - fa[k], 4),
               "ci95": [round(float(np.percentile(draws[k], 2.5)), 4), round(float(np.percentile(draws[k], 97.5)), 4)],
               "p_boot_le0": round(float(np.mean(np.asarray(draws[k]) <= 0)), 4)} for k in fa}
    ca, cb = pa == y, pb == y
    n01, n10 = int((ca & ~cb).sum()), int((~ca & cb).sum())  # a right b wrong, a wrong b right
    out["mcnemar"] = {"a_right_b_wrong": n01, "a_wrong_b_right": n10, "both_right": int((ca & cb).sum()),
                      "both_wrong": int((~ca & ~cb).sum()),
                      "p_exact": round(float(mcnemar([[0, n01], [n10, 0]], exact=True).pvalue), 4)}
    out["acc"] = {"a": round(float(ca.mean()), 4), "b": round(float(cb.mean()), 4)}
    out |= {"n_items": int(len(m)), "n_groups": int(len(uniq)), "n_boot": n_boot}
    return out


def mask_quality() -> tuple[dict, pd.DataFrame]:
    q = pd.read_csv(EXP / "masks.csv")
    q["disagree_gt10"] = (1 - q.iou_chroma_fastsam) > 0.10

    def summ(x: pd.DataFrame) -> dict:
        return {"n": int(len(x)), "iou_mean": round(float(x.iou_chroma_fastsam.mean()), 4),
                "iou_median": round(float(x.iou_chroma_fastsam.median()), 4),
                "iou_p05": round(float(x.iou_chroma_fastsam.quantile(0.05)), 4),
                "share_disagree_gt10pct": round(float(x.disagree_gt10.mean()), 4),
                "share_fastsam_larger_gt10pct": round(float((x.area_ratio > 1.1).mean()), 4),
                "share_fastsam_smaller_gt10pct": round(float((x.area_ratio < 0.9).mean()), 4),
                "area_ratio_median": round(float(x.area_ratio.median()), 4),
                "iou_chroma_vs_dilated_median": round(float(x.iou_chroma_fastsam_dil.median()), 4),
                "fallback_to_chroma": int(x.fastsam_fallback.sum()), "conf_0.1_retry": int((x.conf_used < 0.4).sum())}

    out = {"all": summ(q), "by_class": {k: summ(g) for k, g in q.groupby("class")},
           "by_background": {k: summ(g) for k, g in q.groupby("background")},
           "fastsam_latency_s_per_image": {"median": round(float(q.fastsam_s.median()), 4),
                                           "p95": round(float(q.fastsam_s.quantile(0.95)), 4),
                                           "setting": "640x640 input, imgsz 640, CPU, 6 torch threads, EC2 box, model "
                                                      "loaded once, excludes chroma mask and cropping"}}
    return out, q


def f1_table(arm: str, protocol: str, f1: dict) -> list[dict]:
    return [{"arm": arm, "protocol": protocol, "class": k, "f1": v["f1"], "ci_lo": v["ci95"][0], "ci_hi": v["ci95"][1],
             "n_items": f1["n_items"], "n_groups": f1["n_groups"]} for k, v in f1.items() if isinstance(v, dict)]


def diff_table(arm: str, protocol: str, p: dict) -> list[dict]:
    return [{"arm": arm, "vs": "current", "protocol": protocol, "class": k, "diff": v["diff"], "ci_lo": v["ci95"][0],
             "ci_hi": v["ci95"][1], "p_boot_le0": v["p_boot_le0"], "mcnemar_p": p["mcnemar"]["p_exact"],
             "a_right_b_wrong": p["mcnemar"]["a_right_b_wrong"], "a_wrong_b_right": p["mcnemar"]["a_wrong_b_right"]}
            for k, v in p.items() if isinstance(v, dict) and "diff" in v]


def main():
    base = H.load("dinov2-small")
    base = base[base.dataset == R2.SOY].reset_index(drop=True)
    res = {"mask_quality": None, "r2_fixed_split": {}, "cv5_bursts": {}}
    res["mask_quality"], q = mask_quality()
    f1_rows, diff_rows, preds = [], [], []
    r2p, cvp = {}, {}
    for arm in ARMS:
        d = load_arm(arm, base)
        r, p = R2.evaluate(d)
        r.pop("soybean_by_mask_frac", None)
        res["r2_fixed_split"][arm] = r
        r2p[arm] = p
        f1_rows += f1_table(arm, "r2_fixed_split", r["f1"])
        o, cs = cv_oof(d)
        cvp[arm] = o
        res["cv5_bursts"][arm] = {"C_per_fold": cs, "f1": H.grouped_bootstrap_f1(o["class"], o["pred"], o["group"], LABELS),
                                  "confusion": H.confusion(o["class"], o["pred"], LABELS),
                                  "eval_bursts_per_class": o.groupby("class").group.nunique().to_dict()}
        f1_rows += f1_table(arm, "cv5_bursts", res["cv5_bursts"][arm]["f1"])
        preds += [p.assign(arm=arm, protocol="r2_fixed_split"), o.assign(arm=arm, protocol="cv5_bursts")]
        print(arm, "R2", {k: v["f1"] for k, v in r["f1"].items() if isinstance(v, dict)},
              "CV", {k: v["f1"] for k, v in res["cv5_bursts"][arm]["f1"].items() if isinstance(v, dict)}, flush=True)
    res["paired_vs_current"] = {"r2_fixed_split": {}, "cv5_bursts": {}}
    for arm in ARMS[1:]:
        for proto, pp in (("r2_fixed_split", r2p), ("cv5_bursts", cvp)):
            pr = paired(pp["current"], pp[arm])
            res["paired_vs_current"][proto][arm] = pr
            diff_rows += diff_table(arm, proto, pr)
            print("paired", proto, arm, {k: (v["diff"], v["ci95"]) for k, v in pr.items() if isinstance(v, dict) and "diff" in v},
                  pr["mcnemar"], flush=True)
    how = ("Soybean d97rjyk2tz single-seed images, the 2121 R2 rows (data/crops/manifest_soybean.csv). Four crop arms, "
           "all 224 px with pipeline/make_crops.masked_crop geometry (square, seed bbox 85 % of the side) and embedded "
           "with frozen facebook/dinov2-small (CLS + mean patch, pipeline/features.embed): current = chroma mask "
           "(existing features); fastsam = FastSAM-s (Ultralytics v8.3.0 weights, SHA-256 c9f78716...0844, AGPL-3.0) "
           "imgsz 640, conf 0.4 (retry 0.1), NMS IoU 0.9, retina masks, mask with the highest IoU vs the chroma mask "
           "among masks covering 0.5-90 % of the image, holes filled, largest component, background painted FILL; "
           "fastsam_dil = that mask dilated by 4 % of the seed's equivalent diameter; nomask = same square crop "
           "around the FastSAM seed with the real background kept. Mask quality: IoU of the FastSAM mask vs the "
           "chroma mask on every image; disagree = 1 - IoU > 0.10. Classifier: harness.FrozenLogReg. Protocol "
           "r2_fixed_split = experiments/r2_per_class.evaluate unchanged (fit split=train, C from "
           f"{R2.C_GRID} by macro F1 on val eval_rep, refit, score test eval_rep, multi_seed excluded, 19 test "
           "bursts). Protocol cv5_bursts = StratifiedGroupKFold(5, shuffle, seed 0) over bursts on all rows "
           f"(train+val+test), C from {R2.CV_GRID} by inner grouped 3-fold CV, out-of-fold predictions on eval_rep "
           "non-multi-seed crops pooled; folds identical across arms. F1 CIs: percentile bootstrap over bursts, "
           "2000 resamples, seed 0. Paired comparisons (arm minus current) on identical eval crops: the same burst "
           "resample scores both arms (2000, seed 0), 95 % percentile CI of the difference; McNemar exact test on "
           "per-crop correctness.")
    H.write_result("mask_quality", res, how, {"f1": pd.DataFrame(f1_rows), "paired": pd.DataFrame(diff_rows),
                                              "masks": q, "predictions": pd.concat(preds, ignore_index=True)})


if __name__ == "__main__":
    main()
