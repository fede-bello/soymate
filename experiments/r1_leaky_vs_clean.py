"""R1: how much of the "as published" score on d97rjyk2tz is leakage and shortcut, not seed damage.

Run on the box:  cd ~/soymate-next && OMP_NUM_THREADS=4 uv run python experiments/r1_leaky_vs_clean.py [--features dinov2-small]
Writes results/r1_leaky_vs_clean[__<features>].json and CSV tables (see write_result in experiments/harness.py).

Same model, same images, six arms, so each fix is separable (critique.md M6, m1; findings.md 2.3, 2.5, 5):
  A  published v2 split + full uncropped image (black background and printed date visible)  "as published"
  B  published v2 split + masked seed crop
  C  photo-level split (split_photo) + full image
  D  photo-level split + masked seed crop
  E  burst-level split (split, 30 s capture bursts) + full image
  F  burst-level split + masked seed crop                                                    our pipeline
Images: every non-dropped soybean.csv row whose class (make_crops.soy_class: insect_hole / broken / sound; Egg
without Hole dropped) is defined and that has a single-seed crop (multi_seed crops excluded), so all arms see
exactly the same images. Train on the train split only (no tuning, so val is unused). Test: one image per
original photo (eval_rep); published arms also on all test images. F1 CIs: grouped bootstrap over the arm's
split unit (photo for A-D, burst for E-F). A_raw: published split as distributed (md5 duplicates kept).
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

from harness import MODELS, ROOT, grouped_bootstrap_f1, confusion, load, predict, wilson, write_result

sys.path.insert(0, str(ROOT / "pipeline"))
from make_crops import soy_class  # noqa: E402

CLASSES = ["insect_hole", "broken", "sound"]
# arm: (split column, input, bootstrap unit)
ARMS = {"A": ("published_split", "full", "photo"), "B": ("published_split", "crop", "photo"),
        "C": ("split_photo", "full", "photo"), "D": ("split_photo", "crop", "photo"),
        "E": ("split", "full", "group"), "F": ("split", "crop", "group")}


def one_per_photo(df: pd.DataFrame) -> pd.DataFrame:
    """One image per original photo: the eval_rep image when it survived filtering, else the first by name."""
    rep = df["eval_rep"].astype(str).eq("True")
    return df.assign(_r=~rep).sort_values(["photo", "_r", "image"]).drop_duplicates("photo").drop(columns="_r")


def run_arm(df: pd.DataFrame, split_col: str, unit: str, model_name: str, all_test: bool) -> dict:
    tr, te = df[df[split_col] == "train"], df[df[split_col] == "test"]
    model = MODELS[model_name]().fit(tr, tr["class"].to_numpy())
    out = {"split_col": split_col, "bootstrap_unit": "burst" if unit == "group" else unit,
           "n_train": len(tr), "n_train_photos": int(tr["photo"].nunique()), "n_train_bursts": int(tr["group"].nunique())}
    views = {"one_per_photo": one_per_photo(te)} | ({"all_test": te} if all_test else {})
    for v, t in views.items():
        yp = predict(model, t)
        out[v] = grouped_bootstrap_f1(t["class"], yp, t[unit], CLASSES) | {
            "n_test_bursts": int(t["group"].nunique()), "confusion": confusion(t["class"], yp, CLASSES)}
    return out


def main(features: str, model_name: str) -> None:
    full = load(features, "soybean_full")
    full["class"] = full["labels"].map(soy_class)
    crops = load(features, "crops")
    crops = crops[(crops["dataset"] == "soybean_d97rjyk2tz") & (crops["multi_seed"].astype(str) != "True")]
    crops = crops.rename(columns={"source_image": "image"})

    keep = full[(full["drop_reason"] == "") & full["class"].notna() & full["image"].isin(crops["image"])]
    meta = keep[["image", "photo", "group", "published_split", "split_photo", "split", "eval_rep", "class"]]
    mismatch = int((crops.set_index("image")["class"].reindex(meta["image"]).to_numpy() != meta["class"]).sum())
    assert mismatch == 0, f"{mismatch} images where manifest class != soy_class(labels)"
    fcols = [c for c in full.columns if c.startswith("f") and c[1:].isdigit()]
    inputs = {"full": keep[["image"] + fcols], "crop": crops[["image"] + fcols]}

    res = {}
    for arm, (split_col, inp, unit) in ARMS.items():
        df = meta.merge(inputs[inp], on="image", how="inner")
        res[arm] = {"input": inp} | run_arm(df, split_col, unit, model_name, all_test=split_col == "published_split")
        print(arm, split_col, inp, {v: res[arm][v]["macro"] for v in ("all_test", "one_per_photo") if v in res[arm]},
              flush=True)
    raw = full[full["class"].notna()]  # as distributed: md5 duplicates kept
    res["A_raw"] = {"input": "full"} | run_arm(raw, "published_split", "photo", model_name, all_test=True)
    res["A_raw"]["split_col"] = "published_split (as distributed, md5 duplicates kept)"

    def leak(df, unit):
        tr = set(df.loc[df["published_split"] == "train", unit])
        te = df[df["published_split"] == "test"]
        k, n = int(te[unit].isin(tr).sum()), len(te)
        return {"k": k, "n": n, "share": round(k / n, 4), "wilson95": [round(x, 4) for x in wilson(k, n)]}
    s = pd.read_csv(ROOT / "data" / "splits" / "soybean.csv", keep_default_na=False)
    res["published_test_in_train"] = {f"{name}__by_{u}": leak(d, col) for name, d in
                                      [("all_v2_images", s), ("r1_image_set", meta)]
                                      for u, col in [("photo", "photo"), ("burst", "group")]}
    res["n_images"], res["class_counts"] = len(meta), meta["class"].value_counts().to_dict()
    res["n_photos"], res["n_bursts"] = int(meta["photo"].nunique()), int(meta["group"].nunique())
    if res["F"]["one_per_photo"]["macro"]["f1"] > 0.95:
        res["flag"] = "F macro F1 > 0.95: suspicious, check for residual shortcuts or leakage"

    rows = []
    for arm in [*ARMS, "A_raw"]:
        for v in ("one_per_photo", "all_test"):
            if v not in res[arm]:
                continue
            r = res[arm][v]
            rows.append({"arm": arm, "split": res[arm]["split_col"], "input": res[arm]["input"], "test_view": v,
                         "bootstrap_unit": res[arm]["bootstrap_unit"], "n_test": r["n_items"],
                         "n_boot_units": r["n_groups"], "n_test_bursts": r["n_test_bursts"]}
                        | {f"{k}_f1": r[k]["f1"] for k in ["macro"] + CLASSES}
                        | {f"{k}_ci95": f"[{r[k]['ci95'][0]:.3f}, {r[k]['ci95'][1]:.3f}]" for k in ["macro"] + CLASSES})
    how = (f"Soybean d97rjyk2tz v2, classes from make_crops.soy_class on soybean.csv labels (Hole->insect_hole; "
           f"else Egg->dropped; else Testa cracking->broken; Healthy-only->sound; others dropped). Image set: "
           f"non-dropped rows (md5 duplicates and unlabeled removed) with a defined class and a single-seed masked "
           f"crop (manifest multi_seed=True excluded), n={len(meta)}, identical in all arms. Model: {model_name} "
           f"({MODELS[model_name].__name__}, default params) on frozen {features} features (CLS + mean patch); full "
           f"image = data/features/{features}__soybean_full.parquet, crop = {features}__crops.parquet. Splits: "
           f"published_split (A,B), split_photo = photo-level grouped split (C,D), split = 30 s capture-burst-level "
           f"grouped split (E,F); trained on train only. Test: one image per original photo (eval_rep, else first by "
           f"name); published arms also all test images. Metric: per-class and macro F1, 95% percentile CI from "
           f"{res['F']['one_per_photo']['n_boot']} grouped bootstrap resamples, seed 0, resampling photos (A-D, A_raw) "
           f"or bursts (E,F). A_raw: published split as distributed (md5 duplicates kept). Leak share: published-test "
           f"images whose photo / burst also appears in published train, Wilson 95% CI.")
    suffix = "" if features == "dinov2-small" else f"__{features}"
    write_result(f"r1_leaky_vs_clean{suffix}", res, how, {"arms": pd.DataFrame(rows)})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="dinov2-small")
    ap.add_argument("--model", default="logreg", choices=list(MODELS))
    a = ap.parse_args()
    main(a.features, a.model)
