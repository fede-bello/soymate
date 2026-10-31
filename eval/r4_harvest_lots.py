"""R4b: real lot-level "% crushed" error on held-out Mechanical-harvest originals (hwdtghttp7).

Run on the box:  cd ~/soymate/eval && OMP_NUM_THREADS=4 uv run python r4_harvest_lots.py [--no-loo]
Reads data/crops/manifest.csv (dataset harvest_hwdtghttp7), data/features/dinov2-small__crops.parquet and
data/splits/harvest_images.csv; writes results/r4_harvest_lots.json and results/r4_harvest_lots__lots.csv
(+ __loo.csv when the leave-one-original-out view runs).

ORACLE SEGMENTATION: seeds are located with the dataset's own instance masks (make_crops.py harvest step), so this
measures classification error only, at lot level. Segmentation error is not included. The masks are "dataset
masks" (they look hand-drawn, a third-party card says model output), not verified human ground truth.

Main protocol: crushed (manifest class broken) vs intact (sound), impurity excluded. FrozenLogReg trained on the 28
train originals (augs 01/06/10), C and the P(crushed) threshold picked on the 6 val originals (aug 01) by crushed F1,
sensitivity / specificity measured on val at that threshold, then the 6 test originals (aug 01) are scored once.
"""
import argparse

import numpy as np
import pandas as pd

from harness import N_BOOT, ROOT, SEED, FrozenLogReg, grouped_bootstrap_f1, load, wilson, write_result

POS, NEG = "broken", "sound"
C_GRID = [0.01, 0.03, 0.1, 0.3, 1.0]
THR_GRID = np.round(np.arange(0.05, 0.96, 0.01), 2)
DECISION_T = 0.05  # illustrative pass/fail threshold on % crushed (no public food spec, critique M4)


def f1_pos(y, pred):
    tp = int(((y == POS) & pred).sum()); fp = int(((y != POS) & pred).sum()); fn = int(((y == POS) & ~pred).sum())
    return 2 * tp / max(2 * tp + fp + fn, 1)


def rg(p, se, sp):
    """Rogan-Gladen corrected prevalence, clipped to [0, 1]."""
    return float(np.clip((p + sp - 1) / (se + sp - 1), 0, 1))


def rg_boot_ci(k, n, se, sp, n_pos, n_neg, rng, n_boot=N_BOOT):
    """Parametric bootstrap of the corrected % that also carries Se/Sp uncertainty (binomial redraws on val counts)."""
    ks = rng.binomial(n, k / n, n_boot) / n
    ses = rng.binomial(n_pos, se, n_boot) / n_pos
    sps = rng.binomial(n_neg, sp, n_boot) / n_neg
    den = ses + sps - 1
    v = np.clip((ks + sps - 1) / np.where(den > 0, den, np.nan), 0, 1)
    v = v[~np.isnan(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def decide(lo, hi, t=DECISION_T):
    return "pass" if hi < t else "fail" if lo > t else "inconclusive"


def seeds_needed(p_obs, se, sp, t=DECISION_T, n_max=20000):
    """Smallest n at which the RG-transformed Wilson interval at the same observed rate excludes t (sampling only)."""
    if abs(rg(p_obs, se, sp) - t) < 1e-9:
        return None
    for n in np.unique(np.round(np.geomspace(20, n_max, 400)).astype(int)):
        lo, hi = (rg(x, se, sp) for x in wilson(int(round(p_obs * n)), int(n)))
        if hi < t or lo > t:
            return int(n)
    return None


def lot_table(df, proba, thr, se, sp, n_pos, n_neg, gt, rng):
    rows = []
    for g, d in df.assign(p=proba).groupby("group"):
        n = len(d); k_true = int((d["class"] == POS).sum()); k_pred = int((d["p"] >= thr).sum())
        raw = k_pred / n; cor = rg(raw, se, sp)
        w = wilson(k_pred, n); w_rg = [rg(x, se, sp) for x in w]
        b = rg_boot_ci(k_pred, n, se, sp, n_pos, n_neg, rng)
        rows.append({
            "group": g, "n_seeds": n, "n_crushed_true": k_true, "n_crushed_pred": k_pred,
            "true_pct": 100 * k_true / n, "true_pct_count_index": gt.loc[g, "pct_crushed_count"],
            "true_pct_area": gt.loc[g, "pct_crushed_area"],
            "raw_pct": 100 * raw, "raw_wilson_lo": 100 * w[0], "raw_wilson_hi": 100 * w[1],
            "rg_pct": 100 * cor, "rg_wilson_lo": 100 * w_rg[0], "rg_wilson_hi": 100 * w_rg[1],
            "rg_boot_lo": 100 * b[0], "rg_boot_hi": 100 * b[1],
            "abs_err_raw_pp": abs(100 * raw - 100 * k_true / n), "abs_err_rg_pp": abs(100 * cor - 100 * k_true / n),
            "true_in_raw_wilson": w[0] <= k_true / n <= w[1], "true_in_rg_boot": b[0] <= k_true / n <= b[1],
            "decision_true": "pass" if k_true / n < DECISION_T else "fail",
            "decision_raw": decide(*w), "decision_rg": decide(*w_rg), "decision_rg_boot": decide(*b),
            "seeds_needed_rg": seeds_needed(raw, se, sp)})
    return pd.DataFrame(rows).round(3)


def boot_mean_ci(x, rng, n_boot=N_BOOT):
    x = np.asarray(x, float)
    m = [rng.choice(x, len(x)).mean() for _ in range(n_boot)]
    return {"mean": round(float(x.mean()), 3), "ci95": [round(float(np.percentile(m, 2.5)), 3),
                                                       round(float(np.percentile(m, 97.5)), 3)], "n_lots": len(x)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-loo", action="store_true")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    df = load()
    df = df[(df["dataset"] == "harvest_hwdtghttp7") & df["class"].isin([POS, NEG])].copy()
    df["group"] = df["group"].astype(str).str.zfill(4)
    df["aug"] = df["aug"].astype(float).astype(int)
    gt = pd.read_csv(ROOT / "data" / "splits" / "harvest_images.csv", dtype={"group": str})
    gt = gt[gt["aug"] == 1].set_index("group")
    tr = df[df["split"] == "train"]
    va = df[(df["split"] == "val") & (df["aug"] == 1)]
    te = df[(df["split"] == "test") & (df["aug"] == 1)]
    assert va["group"].nunique() == 6 and te["group"].nunique() == 6 and tr["group"].nunique() == 28, \
        (tr["group"].nunique(), va["group"].nunique(), te["group"].nunique())
    print(f"train {len(tr)} crops / val {len(va)} / test {len(te)}", flush=True)

    # --- model selection on val
    yv = va["class"].to_numpy()
    sel, best = [], None
    for C in C_GRID:
        m = FrozenLogReg(C=C).fit(tr, tr["class"].to_numpy())
        pv = m.predict_proba(va)[:, list(m.classes_).index(POS)]
        f = [f1_pos(yv, pv >= t) for t in THR_GRID]
        i = int(np.argmax(f))
        sel.append({"C": C, "best_thr": float(THR_GRID[i]), "val_f1_crushed": round(f[i], 4),
                    "val_f1_at_0.5": round(f1_pos(yv, pv >= 0.5), 4)})
        if best is None or f[i] > best[0]:
            best = (f[i], C, float(THR_GRID[i]), m, pv)
        print(sel[-1], flush=True)
    _, C, thr, model, pv = best
    predv = pv >= thr
    n_pos, n_neg = int((yv == POS).sum()), int((yv == NEG).sum())
    tp = int((predv & (yv == POS)).sum()); tn = int((~predv & (yv == NEG)).sum())
    se, sp = tp / n_pos, tn / n_neg
    print(f"chosen C={C} thr={thr} val Se={se:.3f} ({tp}/{n_pos}) Sp={sp:.3f} ({tn}/{n_neg})", flush=True)

    # --- test lots
    pt = model.predict_proba(te)[:, list(model.classes_).index(POS)]
    lots = lot_table(te, pt, thr, se, sp, n_pos, n_neg, gt, rng)
    print(lots.to_string(), flush=True)
    yt = te["class"].to_numpy(); predt = np.where(pt >= thr, POS, NEG)
    f1_test = grouped_bootstrap_f1(yt, predt, te["group"].to_numpy(), [POS, NEG])
    vt = pd.concat([va, te]); pvt = np.where(np.r_[pv, pt] >= thr, POS, NEG)
    f1_vt = grouped_bootstrap_f1(vt["class"].to_numpy(), pvt, vt["group"].to_numpy(), [POS, NEG])
    test_se = float(((pt >= thr) & (yt == POS)).sum() / (yt == POS).sum())
    test_sp = float(((pt < thr) & (yt == NEG)).sum() / (yt == NEG).sum())
    pooled_true = (yt == POS).mean(); pooled_raw = (pt >= thr).mean()

    result = {
        "oracle_segmentation": True,
        "selection": {"grid": sel, "C": C, "threshold": thr, "criterion": "max crushed F1 on val originals (aug 01)"},
        "val_rates": {"sensitivity": round(se, 4), "specificity": round(sp, 4), "n_pos": n_pos, "n_neg": n_neg,
                      "se_wilson": wilson(tp, n_pos), "sp_wilson": wilson(tn, n_neg)},
        "test_rates_for_reference": {"sensitivity": round(test_se, 4), "specificity": round(test_sp, 4)},
        "test_lots": {
            "n_lots": len(lots), "n_seeds": int(lots["n_seeds"].sum()),
            "mae_raw_pp": boot_mean_ci(lots["abs_err_raw_pp"], rng),
            "mae_rg_pp": boot_mean_ci(lots["abs_err_rg_pp"], rng),
            "pooled_true_pct": round(100 * pooled_true, 3), "pooled_raw_pct": round(100 * pooled_raw, 3),
            "pooled_rg_pct": round(100 * rg(pooled_raw, se, sp), 3),
            "coverage_raw_wilson": int(lots["true_in_raw_wilson"].sum()),
            "coverage_rg_boot": int(lots["true_in_rg_boot"].sum())},
        "per_seed_f1_crushed_test6": f1_test[POS] | {"n_items": f1_test["n_items"], "n_groups": f1_test["n_groups"]},
        "per_seed_f1_crushed_valtest12_secondary": f1_vt[POS] | {
            "n_items": f1_vt["n_items"], "n_groups": f1_vt["n_groups"],
            "note": "val originals were used to pick C and threshold, so this view is optimistic"},
        "decision_demo": {"threshold_pct": 100 * DECISION_T, "illustrative": True,
                          "counts_rg_wilson": lots["decision_rg"].value_counts().to_dict(),
                          "counts_rg_boot": lots["decision_rg_boot"].value_counts().to_dict(),
                          "counts_raw_wilson": lots["decision_raw"].value_counts().to_dict()},
    }
    tables = {"lots": lots}

    # --- optional: leave-one-original-out, different protocol
    if not args.no_loo:
        a1 = df[df["aug"] == 1]
        loo = []
        for g in sorted(a1["group"].unique()):
            trg, teg = a1[a1["group"] != g], a1[a1["group"] == g]
            m = FrozenLogReg(C=C).fit(trg, trg["class"].to_numpy())
            p = m.predict_proba(teg)[:, list(m.classes_).index(POS)]
            k_true = int((teg["class"] == POS).sum()); k_pred = int((p >= thr).sum()); n = len(teg)
            loo.append({"group": g, "split": teg["split"].iloc[0], "n_seeds": n, "true_pct": 100 * k_true / n,
                        "raw_pct": 100 * k_pred / n, "rg_pct": 100 * rg(k_pred / n, se, sp),
                        "abs_err_raw_pp": abs(k_pred - k_true) / n * 100,
                        "abs_err_rg_pp": abs(rg(k_pred / n, se, sp) - k_true / n) * 100})
        loo = pd.DataFrame(loo).round(3)
        result["loo40_different_protocol"] = {
            "protocol": "train on aug-01 crops of the other 39 originals, C and threshold fixed from the main "
                        "protocol (picked on the 6 val originals, slight leakage for those 6), RG with main val Se/Sp",
            "mae_raw_pp": boot_mean_ci(loo["abs_err_raw_pp"], rng),
            "mae_rg_pp": boot_mean_ci(loo["abs_err_rg_pp"], rng),
            "max_abs_err_raw_pp": float(loo["abs_err_raw_pp"].max()),
            "mean_signed_err_raw_pp": round(float((loo["raw_pct"] - loo["true_pct"]).mean()), 3),
            "corr_true_vs_raw": round(float(np.corrcoef(loo["true_pct"], loo["raw_pct"])[0, 1]), 3)}
        tables["loo"] = loo
        print(result["loo40_different_protocol"], flush=True)

    how = (f"Oracle segmentation: seeds located with the hwdtghttp7 dataset masks (not human-verified), so only "
           f"classification error is measured. Crushed vs intact, impurity excluded. FrozenLogReg (DINOv2-small "
           f"frozen features of masked crops, balanced weights) trained on 28 train originals (augs 01/06/10); C in "
           f"{C_GRID} and P(crushed) threshold in 0.05..0.95 picked on 6 val originals (aug 01) by crushed F1 "
           f"(C={C}, thr={thr}); val Se/Sp at that threshold feed Rogan-Gladen. 6 test originals (aug 01) scored once. "
           f"Per lot: true % = crushed/(crushed+intact) over the classified crops; raw % = predicted crushed / seeds; "
           f"Wilson 95 % on raw; corrected interval two ways: RG applied to the Wilson endpoints (sampling only, Se/Sp "
           f"treated as known) and a parametric bootstrap redrawing the lot count and val Se/Sp binomially ({N_BOOT} "
           f"draws). MAE CI: bootstrap over lots. Per-seed F1 CI: grouped bootstrap over originals. Decision demo at an "
           f"illustrative {100 * DECISION_T:.0f} % threshold; seeds needed = smallest n at which the RG-transformed "
           f"Wilson interval at the same observed rate excludes the threshold. LOO-40 is a separate protocol.")
    write_result("r4_harvest_lots", result, how, tables)


if __name__ == "__main__":
    main()
