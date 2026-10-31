"""R2: per-class F1 on the clean (grouped) test split, plus the soybean session control (critique C1 fix 3, m1).

Run on the box:  cd ~/soymate && OMP_NUM_THREADS=4 uv run python eval/r2_per_class.py [--features dinov2-small]
Writes results/r2_per_class.json (+ CSVs) and results/r2_session_control.json (+ CSVs).

R2 protocol: fit on split=train (all crops), choose C on split=val (eval_rep, macro F1), refit on train, score
once on split=test eval_rep (soybean: one crop per original photo; Lin: one per near-duplicate cluster), excluding
multi_seed crops. CIs: harness.grouped_bootstrap_f1 over `group` (soybean: 30 s capture bursts; Lin: clusters).
Session control: the fixed split leaves 1-3 test bursts per class in the same-day subsets, so those arms and the
capture-date probes use grouped 5-fold CV over bursts (cv_evaluate) and the same burst bootstrap.
"""
import argparse

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

import harness as H

SOY, LIN = "soybean_d97rjyk2tz", "lin_v6vzvfszj6"
C_GRID = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0]
LIGHT = "white/light"
MF = 0.2  # mask_frac cut: black-background hole photos are zoomed out (median 0.15)


def rep(df: pd.DataFrame) -> pd.DataFrame:
    """Evaluation rows: one crop per group, multi-seed crops excluded."""
    ms = df["multi_seed"].astype(str) if "multi_seed" in df else pd.Series("", index=df.index)
    return df[(df["eval_rep"].astype(str) == "True") & (ms != "True")]


def by_mask_frac(preds: pd.DataFrame, label: str = "class") -> dict:
    """Soybean test reps scored separately for zoomed-out crops (mask_frac < 0.2, upsampled ~2x) and the rest."""
    p = preds[preds.dataset == SOY]
    out = {}
    for name, g in {"mask_frac_lt_0.2": p[p.mask_frac < MF], "mask_frac_ge_0.2": p[p.mask_frac >= MF]}.items():
        if len(g):
            out[name] = H.grouped_bootstrap_f1(g[label], g["pred"], g["group"], sorted(p[label].unique())) \
                | {"counts": g[label].value_counts().to_dict(),
                   "confusion": H.confusion(g[label], g["pred"], sorted(set(p[label]) | set(p["pred"])))}
    return out


def fit_select(df: pd.DataFrame, label: str = "class", model: str = "logreg"):
    """Fit on train, pick C by macro F1 on val reps, refit on train. Returns (model, best_C, val scores)."""
    tr, va = df[df.split == "train"], rep(df[df.split == "val"])
    labels = np.unique(tr[label])
    scores = {}
    for c in C_GRID:
        m = H.MODELS[model](C=c).fit(tr, tr[label].to_numpy())
        scores[c] = H.per_class_f1(va[label], H.predict(m, va), labels)["macro"]
    best = max(scores, key=lambda c: (round(scores[c], 4), -c))  # ties -> smaller C
    return H.MODELS[model](C=best).fit(tr, tr[label].to_numpy()), best, {str(k): round(v, 4) for k, v in scores.items()}


def evaluate(df: pd.DataFrame, label: str = "class", model: str = "logreg") -> tuple[dict, pd.DataFrame]:
    m, c, val = fit_select(df, label, model)
    te = rep(df[df.split == "test"])
    pred = H.predict(m, te)
    labels = list(m.classes_)
    out = {"C": c, "val_macro_f1_by_C": val,
           "n_train": int((df.split == "train").sum()), "n_test_reps": int(len(te)),
           "test_counts": te[label].value_counts().to_dict(),
           "f1": H.grouped_bootstrap_f1(te[label], pred, te["group"], labels),
           "confusion": H.confusion(te[label], pred, labels)}
    if len(labels) == 2:  # binary: also AUC with grouped bootstrap CI
        p = m.predict_proba(te)[:, 1]
        out["auc"] = boot_auc(te[label].to_numpy() == labels[1], p, te["group"].to_numpy())
    preds = te[["crop", "dataset", "group", label]].assign(pred=pred, mask_frac=te.mask_frac.astype(float))
    if (preds.dataset == SOY).any() and label == "class":
        out["soybean_by_mask_frac"] = by_mask_frac(preds)
    return out, preds


def boot_auc(y, score, groups, n_boot: int = H.N_BOOT, seed: int = H.SEED) -> dict:
    y, score, groups = map(np.asarray, (y, score, groups))
    uniq = np.unique(groups)
    idx_by = {g: np.nonzero(groups == g)[0] for g in uniq}
    rng, draws = np.random.default_rng(seed), []
    for _ in range(n_boot):
        idx = np.concatenate([idx_by[g] for g in rng.choice(uniq, len(uniq), replace=True)])
        if len(np.unique(y[idx])) == 2:
            draws.append(roc_auc_score(y[idx], score[idx]))
    return {"auc": round(float(roc_auc_score(y, score)), 4),
            "ci95": [round(float(np.percentile(draws, 2.5)), 4), round(float(np.percentile(draws, 97.5)), 4)]}


def f1_rows(tag: str, feats: str, res: dict) -> list[dict]:
    cnt = res.get("test_counts", res.get("eval_counts", {}))
    return [{"features": feats, "scope": tag, "class": k, "f1": v["f1"], "ci_lo": v["ci95"][0], "ci_hi": v["ci95"][1],
             "n_eval": cnt.get(k, ""), "n_groups": res["f1"]["n_groups"]} for k, v in res["f1"].items() if isinstance(v, dict)]


CV_GRID = [0.01, 0.1, 1.0]


def cv_evaluate(d: pd.DataFrame, label: str = "class", train_ok=None, test_ok=None, k: int = 5) -> dict:
    """Grouped k-fold CV over bursts for small subsets where the fixed split leaves 1-2 test bursts per class.

    Outer StratifiedGroupKFold(k) over `group`; C picked per fold by inner grouped 3-fold CV (macro F1 on reps);
    out-of-fold predictions on eval_rep rows are pooled and scored with the burst bootstrap. train_ok / test_ok
    are optional row filters applied inside each fold (used by the cross-session arm)."""
    d = d.reset_index(drop=True)
    labels = sorted(d[label].unique())
    outer = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=H.SEED)
    oof, cs = [], []
    for fold, (tri, tei) in enumerate(outer.split(d, d[label], d["group"])):
        tr, te = d.iloc[tri], rep(d.iloc[tei])
        tr = tr[train_ok(tr)] if train_ok else tr
        te = te[test_ok(te)] if test_ok else te
        if len(te) == 0 or tr[label].nunique() < 2:
            continue
        inner = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=H.SEED)
        score = {c: [] for c in CV_GRID}
        for a, b in inner.split(tr, tr[label], tr["group"]):
            ia, ib = tr.iloc[a], rep(tr.iloc[b])
            if ia[label].nunique() < 2 or len(ib) == 0:
                continue
            for c in CV_GRID:
                m = H.MODELS["logreg"](C=c).fit(ia, ia[label].to_numpy())
                score[c].append(H.per_class_f1(ib[label], H.predict(m, ib), labels)["macro"])
        c = max(CV_GRID, key=lambda c: (round(float(np.mean(score[c])) if score[c] else -1, 4), -c))
        m = H.MODELS["logreg"](C=c).fit(tr, tr[label].to_numpy())
        pr = m.predict_proba(te)
        oof.append(te.assign(pred=m.classes_[pr.argmax(1)], fold=fold,
                             p1=pr[:, list(m.classes_).index(labels[-1])] if labels[-1] in m.classes_ else 0.0))
        cs.append(c)
    o = pd.concat(oof)
    o["mask_frac"] = o.mask_frac.astype(float)
    out = {"protocol": f"grouped {k}-fold CV over bursts, inner 3-fold C selection from {CV_GRID}",
           "C_per_fold": cs, "n_eval_reps": int(len(o)),
           "eval_counts": o[label].value_counts().to_dict(),
           "eval_bursts_per_class": o.groupby(label).group.nunique().to_dict(),
           "f1": H.grouped_bootstrap_f1(o[label], o["pred"], o["group"], labels),
           "confusion": H.confusion(o[label], o["pred"], labels)}
    if len(labels) == 2 and o[label].nunique() == 2:
        out["auc_positive_" + str(labels[-1])] = boot_auc(o[label].to_numpy() == labels[-1], o.p1.to_numpy(),
                                                          o.group.to_numpy())
    if label == "class":
        out["soybean_by_mask_frac"] = by_mask_frac(o)
    return out


def date_probe(df: pd.DataFrame, cls: str, a: list[int], b: list[int], light_only: bool = True) -> dict:
    """Within one class: can features tell capture session A from session B? Binary probe, grouped CV."""
    d = df[df["class"] == cls].copy()
    if light_only:
        d = d[d.background == LIGHT]
    d["date"] = pd.to_numeric(d.capture_date, errors="coerce").astype("Int64") % 100
    d = d[d.date.isin(a + b)]
    d["session"] = np.where(d.date.isin(a), f"{'/'.join(map(str, a))}-08", f"{'/'.join(map(str, b))}-08")
    res = cv_evaluate(d, "session")
    res["bursts_per_session"] = d.groupby("session").group.nunique().to_dict()
    return res


def session_control(df: pd.DataFrame) -> tuple[dict, list[dict]]:
    s = df[(df.dataset == SOY) & df["class"].isin(["insect_hole", "sound"])].copy()
    s["day"] = pd.to_numeric(s.capture_date, errors="coerce").astype("Int64") % 100
    light = s[s.background == LIGHT]
    same_days = light[light.day.isin([13, 14])]
    arms = {
        "all_backgrounds": s,
        "light_background": light,
        "light_background_same_days_13_14": same_days,
        "all_backgrounds_mask_frac_ge_0.2": s[s.mask_frac.astype(float) >= MF],
        "light_background_same_days_13_14_mask_frac_ge_0.2": same_days[same_days.mask_frac.astype(float) >= MF],
    }
    out = {"subset_sizes": {n: {"crops_by_class": d["class"].value_counts().to_dict(),
                                "bursts_by_class": d.groupby("class").group.nunique().to_dict()}
                            for n, d in arms.items()}}
    rows = []
    for name, d in arms.items():
        r = cv_evaluate(d)
        out[name], rows = r, rows + f1_rows(name, "", r)
        print("session arm", name, r["f1"]["insect_hole"], flush=True)
    # cross-session: holes from 9-11/08 (any background) only ever in training, holes from 13-14/08 (light) only
    # ever in evaluation; sound (light) split by burst folds as usual.
    x = pd.concat([light, s[(s["class"] == "insect_hole") & s.day.isin([9, 10, 11]) & (s.background != LIGHT)]])
    x = x[(x["class"] == "sound") | x.day.isin([9, 10, 11, 13, 14])]
    r = cv_evaluate(x, train_ok=lambda t: (t["class"] == "sound") | t.day.isin([9, 10, 11]),
                    test_ok=lambda t: (t["class"] == "sound") | t.day.isin([13, 14]))
    out["cross_session_train_holes_9_11_test_holes_13_14"] = r
    rows += f1_rows("cross_session_train_holes_9_11_test_holes_13_14", "", r)
    soy = df[df.dataset == SOY]
    out["date_probe"] = {
        "insect_hole_9_11_vs_13_14_light": date_probe(soy, "insect_hole", [9, 10, 11], [13, 14]),
        "insect_hole_13_vs_14_light": date_probe(soy, "insect_hole", [13], [14]),
        "sound_13_vs_14_light": date_probe(soy, "sound", [13], [14]),
        "sound_13_14_vs_18_light": date_probe(soy, "sound", [13, 14], [18]),
    }
    return out, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", nargs="+", default=["dinov2-small"])
    ap.add_argument("--model", default="logreg")
    args = ap.parse_args()
    feats = [f for f in args.features if (H.FEATS / f"{f}__crops.parquet").exists()]
    r2, sc, rows, sc_rows, cms, preds_all = {}, {}, [], [], [], []
    for f in feats:
        df = H.load(f)
        r2[f] = {}
        for scope, d in {"soybean": df[df.dataset == SOY], "lin": df[df.dataset == LIN], "pooled_5class": df}.items():
            res, preds = evaluate(d, model=args.model)
            if scope == "pooled_5class":  # pooled model scored inside each source dataset
                labs = sorted(df["class"].unique())
                res["by_dataset"] = {ds: H.grouped_bootstrap_f1(p["class"], p["pred"], p["group"],
                                                                sorted(p["class"].unique()))
                                     | {"confusion": H.confusion(p["class"], p["pred"], labs)}
                                     for ds, p in preds.groupby("dataset")}
            r2[f][scope] = res
            rows += f1_rows(scope, f, res)
            cm = res["confusion"]
            cms += [{"features": f, "scope": scope, "true": t, **dict(zip(cm["labels"], row))}
                    for t, row in zip(cm["labels"], cm["rows_true_cols_pred"])]
            preds_all.append(preds.assign(features=f, scope=scope))
            print(f, scope, {k: v["f1"] for k, v in res["f1"].items() if isinstance(v, dict)}, flush=True)
        sc[f], r = session_control(df)
        sc_rows += [x | {"features": f} for x in r]
        print(f, "session control done", flush=True)
    s = H.load(feats[0])
    s = s[s.dataset == SOY]
    sc["capture_date_x_class"] = pd.crosstab(s.capture_date.replace("", "missing"), s["class"]).to_dict()
    sc["capture_date_background_x_class"] = {
        f"{d}|{b}": v for (d, b), v in pd.crosstab([s.capture_date, s.background], s["class"]).T.to_dict().items()}
    how_common = (f"Frozen {'/'.join(feats)} features (CLS + mean patch) of masked seed crops "
                  "(data/crops/manifest.csv), harness.FrozenLogReg (StandardScaler + balanced multinomial logistic "
                  f"regression). Fit on split=train (all crops), C chosen from {C_GRID} by macro F1 on split=val "
                  "eval_rep crops, refit on train, scored once on split=test eval_rep crops (one per original photo "
                  "for soybean, one per near-duplicate cluster for Lin). 95% CIs: percentile bootstrap over groups, "
                  "2000 resamples, seed 0. Groups: soybean = 30 s capture bursts (split is burst-level), Lin = "
                  "near-duplicate clusters. Rows with multi_seed=True are excluded "
                  "from val and test scoring (kept in train).")
    H.write_result("r2_per_class", r2, how_common + " Scopes: soybean only (insect_hole/broken/sound), Lin only "
                   "(sound/broken/stained/immature, broken includes skin-damaged), pooled 5-class model trained on "
                   "both (by_dataset = pooled predictions scored inside each source).",
                   {"f1": pd.DataFrame(rows), "confusion": pd.DataFrame(cms),
                    "test_predictions": pd.concat(preds_all)})
    H.write_result("r2_session_control", sc, how_common + " SESSION CONTROL OVERRIDES THE SPLIT: soybean insect_hole vs "
                   "sound only, binary, evaluated by grouped 5-fold CV over bursts (StratifiedGroupKFold, seed 0; C "
                   "from [0.01, 0.1, 1] by inner grouped 3-fold CV), out-of-fold predictions on eval_rep crops "
                   "pooled, burst bootstrap CIs. Arms: all "
                   "backgrounds; white/light background; light background and capture days 13-14/08 only (the "
                   "only days with both classes: the honest hole result); the same two arms restricted to "
                   "mask_frac >= 0.2 (zoomed-out black-background photos give upsampled, blurrier crops); every arm "
                   "also reports soybean_by_mask_frac (< 0.2 vs >= 0.2); cross-session (train holes from 9-11/08 only, test holes from "
                   "13-14/08 only, light background; 9-11/08 training holes "
                   "from any background; sound light background, burst folds). date_probe: within one class and light "
                   "background, binary probe predicting capture session, same grouped CV, AUC with "
                   "grouped bootstrap CI.", {"f1": pd.DataFrame(sc_rows)})


if __name__ == "__main__":
    main()
