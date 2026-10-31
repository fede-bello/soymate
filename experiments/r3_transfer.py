"""R3: transfer between the two soybean datasets (d97rjyk2tz <-> Lin v6vzvfszj6) with few target labels.

Run on the box:  cd ~/soymate-next && OMP_NUM_THREADS=4 uv run python experiments/r3_transfer.py [--draws 10] [--jobs 4] [--model logreg]
Writes results/r3_transfer.json, results/r3_transfer__curve.csv and results/r3_transfer.png.

Shared classes: sound vs broken. The "broken" definitions differ (soybean = Testa cracking, i.e. seed-coat
cracks; Lin = separated pieces or skin-damaged), so Lin is mapped two ways and both are reported:
  a) Lin broken = broken + skin-damaged      b) Lin broken = skin-damaged only (Lin "broken" pieces dropped)
Arms per direction and k (labelled target groups per class, one image per group, drawn from target train):
  source+k (pooled training on source train + k target), target-only k, ceiling (full target train).
Test = target test, eval_rep rows (Lin: one per near-duplicate group; soybean: one per photo), CIs resample
groups (soybean groups = capture bursts). multi_seed crops are excluded. Repeated over --draws random draws
of the k examples.
Runs once per cached feature set (dinov2-small; dinov2-base too if its cache exists).
"""
import argparse

import numpy as np
import pandas as pd

from harness import FEATS, MODELS, RESULTS, grouped_bootstrap_f1, load, predict, write_result

SOY, LIN = "soybean_d97rjyk2tz", "lin_v6vzvfszj6"
LABELS = ["sound", "broken"]
KS = [0, 10, 50]
MAPPINGS = {"a_broken+skin": {"intact": "sound", "broken": "broken", "skin-damaged": "broken"},
            "b_skin_only": {"intact": "sound", "skin-damaged": "broken"}}


def two_class(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    df = df[df.multi_seed.astype(str) != "True"]  # label belongs to the image, not the kept seed region
    soy = df[(df.dataset == SOY) & df["class"].isin(LABELS)].copy()
    soy["y"] = soy["class"]
    lin = df[(df.dataset == LIN) & df.source_label.isin(mapping)].copy()
    lin["y"] = lin.source_label.map(mapping)
    return pd.concat([soy, lin])


def draw_k(pool: pd.DataFrame, k: int, rng) -> pd.DataFrame:
    """k examples per class from the target train pool (eval_rep rows only), spread over groups: groups are
    visited in random order taking one unused image each, cycling only when k exceeds the number of groups
    (soybean groups are capture bursts: 27-28 per class in train, so k=50 reuses bursts)."""
    if k == 0:
        return pool.iloc[:0]
    out = []
    for _, c in pool.groupby("y"):
        left = {g: list(rng.permutation(ix)) for g, ix in c.groupby("group").groups.items()}
        order, picked = list(rng.permutation(list(left))), []
        while len(picked) < k:
            for g in order:
                if left[g] and len(picked) < k:
                    picked.append(left[g].pop())
        out.append(c.loc[picked])
    return pd.concat(out)


def score(model_cls, train: pd.DataFrame, test: pd.DataFrame) -> dict:
    m = model_cls().fit(train, train["y"].to_numpy())
    return grouped_bootstrap_f1(test["y"], predict(m, test), test["group"], LABELS)


def job(model_cls, base: dict, arm: str, k: int, draw: int, train: pd.DataFrame, test: pd.DataFrame) -> dict:
    kk = train[train.dataset == test.dataset.iloc[0]]  # the target examples in this training set
    return base | {"arm": arm, "k": k, "draw": draw, "k_groups": int(kk.group.nunique()) if k > 0 else 0,
                   **flat(score(model_cls, train, test))}


def jobs(df: pd.DataFrame, draws: int):
    """Yield (base, arm, k, draw, train, test) lazily so joblib does not hold every training frame at once."""
    for mname, mapping in MAPPINGS.items():
        d = two_class(df, mapping)
        for src, tgt in [(SOY, LIN), (LIN, SOY)]:
            direction = f"{'soybean' if src == SOY else 'lin'}->{'lin' if tgt == LIN else 'soybean'}"
            s_train = d[(d.dataset == src) & (d.split == "train")]
            t = d[d.dataset == tgt]
            t_pool = t[(t.split == "train") & t.eval_rep.astype(str).eq("True")]
            t_test = t[(t.split == "test") & t.eval_rep.astype(str).eq("True")]
            base = {"mapping": mname, "direction": direction, "n_source_train": len(s_train),
                    "n_target_test_images": len(t_test),
                    "n_target_test_groups": int(t_test.group.nunique()),
                    "target_test_per_class": t_test.y.value_counts().to_dict(),
                    "target_test_groups_per_class": t_test.groupby("y").group.nunique().to_dict()}
            yield base, "ceiling_target_full", -1, 0, t[t.split == "train"], t_test
            for k in KS:
                for i in range(draws if k else 1):
                    kk = draw_k(t_pool, k, np.random.default_rng(1000 * k + i))
                    yield base, "source+k", k, i, pd.concat([s_train, kk]), t_test
                    if k:
                        yield base, "target_only_k", k, i, kk, t_test


def run(df: pd.DataFrame, model_cls, draws: int, n_jobs: int) -> list[dict]:
    from joblib import Parallel, delayed
    return Parallel(n_jobs=n_jobs, verbose=5)(delayed(job)(model_cls, *j) for j in jobs(df, draws))


def flat(r: dict) -> dict:
    out = {}
    for c in ["macro", *LABELS]:
        out[f"f1_{c}"], (out[f"lo_{c}"], out[f"hi_{c}"]) = r[c]["f1"], r[c]["ci95"]
    return out


def summarise(raw: pd.DataFrame) -> pd.DataFrame:
    keys = ["features", "mapping", "direction", "arm", "k"]
    agg = {"n_draws": ("draw", "size"), "k_groups_mean": ("k_groups", "mean")}
    for c in ["macro", *LABELS]:
        agg |= {f"f1_{c}_mean": (f"f1_{c}", "mean"), f"f1_{c}_sd": (f"f1_{c}", "std"),
                f"f1_{c}_min": (f"f1_{c}", "min"), f"f1_{c}_max": (f"f1_{c}", "max"),
                f"ci_lo_{c}_mean": (f"lo_{c}", "mean"), f"ci_hi_{c}_mean": (f"hi_{c}", "mean")}
    return raw.groupby(keys, sort=False).agg(**agg).reset_index().round(4)


def plot(curve: pd.DataFrame, features: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    c = curve[curve.features == features]
    dirs, maps = ["soybean->lin", "lin->soybean"], list(MAPPINGS)
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharey=True)
    for i, dr in enumerate(dirs):
        for j, mp in enumerate(maps):
            ax, s = axes[i, j], c[(c.direction == dr) & (c.mapping == mp)]
            for arm, col, lab in [("source+k", "#1f77b4", "source train + k target"),
                                  ("target_only_k", "#d62728", "target only, k labels")]:
                a = s[s.arm == arm].sort_values("k")
                ax.fill_between(a.k, a.ci_lo_macro_mean, a.ci_hi_macro_mean, color=col, alpha=0.15)
                ax.errorbar(a.k, a.f1_macro_mean, yerr=a.f1_macro_sd.fillna(0), color=col, marker="o",
                            capsize=3, label=lab)
            ceil = s[s.arm == "ceiling_target_full"].iloc[0]
            ax.axhline(ceil.f1_macro_mean, color="k", ls="--", label="in-domain ceiling (full target train)")
            ax.axhspan(ceil.ci_lo_macro_mean, ceil.ci_hi_macro_mean, color="k", alpha=0.07)
            ax.axhline(0.5, color="grey", ls=":", lw=0.8)
            ax.set_xticks(KS)
            ax.set_title(f"{dr}, Lin 'broken' = {'broken + skin-damaged' if mp.startswith('a') else 'skin-damaged only'}",
                         fontsize=10)
            ax.set_xlabel("k labelled target examples per class")
            ax.set_ylabel("macro F1, sound vs broken (target test)")
            ax.set_ylim(0, 1)
            ax.grid(alpha=0.3)
    axes[0, 0].legend(fontsize=8, loc="lower right")
    fig.suptitle(f"R3 transfer soybean d97rjyk2tz <-> Lin v6vzvfszj6 ({features} + logreg)\nPoints: mean over "
                 "draws, bars: SD over draws, bands: grouped bootstrap 95% CI (mean over draws)", fontsize=10)
    fig.tight_layout()
    fig.savefig(RESULTS / "r3_transfer.png", dpi=150)
    print("wrote", RESULTS / "r3_transfer.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=10)
    ap.add_argument("--jobs", type=int, default=4, help="parallel runs (each uses OMP_NUM_THREADS threads)")
    ap.add_argument("--model", default="logreg", choices=list(MODELS))
    a = ap.parse_args()
    feats = [f for f in ["dinov2-small", "dinov2-base"] if (FEATS / f"{f}__crops.parquet").exists()]
    raw = pd.concat([pd.DataFrame(run(load(f), MODELS[a.model], a.draws, a.jobs)).assign(features=f) for f in feats])
    curve = summarise(raw)
    result = {"features": feats, "draws": a.draws, "ks": KS, "mappings": MAPPINGS,
              "curve": curve.to_dict(orient="records"),
              "per_draw": raw.drop(columns=["target_test_per_class", "target_test_groups_per_class"]).to_dict(orient="records"),
              "test_sets": raw.drop_duplicates(["features", "mapping", "direction"])[
                  ["features", "mapping", "direction", "n_source_train", "n_target_test_images",
                   "n_target_test_groups", "target_test_per_class", "target_test_groups_per_class"]].to_dict(orient="records")}
    how = (f"Data: data/crops/manifest.csv masked seed crops, datasets {SOY} and {LIN}, grouped splits from "
           "pipeline/make_splits.py. Two classes: sound vs broken. Soybean: class sound (Healthy) and broken "
           "(any box with Testa cracking); insect_hole dropped. Lin source_label mapped two ways: a) intact->sound, "
           "broken+skin-damaged->broken; b) intact->sound, skin-damaged->broken, Lin 'broken' (separated pieces) "
           "dropped from train and test. Directions soybean->lin and lin->soybean. Arms: source+k = model fitted "
           "on all source-train images pooled with k target-train examples per class; target_only_k = fitted on "
           "the k examples only; ceiling = fitted on all target-train images. k examples: k distinct groups per "
           "class from target-train eval_rep rows (Lin: one per near-duplicate group; soybean: one per photo), visiting "
           "groups in random order one image each and cycling only when k exceeds the number of groups (soybean "
           "groups are capture bursts, 27/28 broken/sound bursts in train, so k=50 reuses bursts; k_groups_mean "
           "in the curve gives the distinct groups used), "
           f"{a.draws} draws per k (seeds 1000*k+draw), k=0 is deterministic (1 run). Test: target test split, eval_rep rows "
           "(Lin: one per near-duplicate group; soybean: one per photo); multi_seed crops excluded everywhere. Model: frozen features (" + ", ".join(feats) + " CLS+mean-patch) + "
           f"harness '{a.model}' (standardised, class-balanced logistic regression, C=0.5). Metric: per-class and "
           "macro F1 over sound/broken with grouped bootstrap 95% percentile CIs (2000 resamples of test groups; soybean test has only 9 broken and 10 sound "
           "capture bursts, so its CIs are wide; "
           "seed 0) per run; curve reports mean/SD/min/max of F1 over draws and the mean of per-draw CI bounds. "
           "Pooled-source variant = source+k (only two labelled soybean sets exist, so no larger pool). Caveat: "
           "the two 'broken' definitions differ, so the drop mixes label shift with domain shift.")
    write_result("r3_transfer", result, how, tables={"curve": curve})
    plot(curve, feats[0])


if __name__ == "__main__":
    main()
