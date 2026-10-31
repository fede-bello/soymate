"""Train the pooled demo model soymate-pooled-v1 (frozen dinov2-small features + logistic regression).

Run on the box:  cd ~/soymate-next && uv run python models/train_models.py
Trains on the train split only of soybean d97rjyk2tz, Lin v6vzvfszj6 and harvest hwdtghttp7 (multi-seed crops
excluded), picks C on val (mean of per-dataset macro F1, one crop per photo), and reports per-dataset test macro F1
(eval_rep rows, grouped bootstrap). Writes data/models/soymate-pooled-v1.joblib and soymate-pooled-v1.json
(model card), then backs both up to S3.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from harness import FrozenLogReg, grouped_bootstrap_f1, load, per_class_f1, predict  # noqa: E402

NAME = "soymate-pooled-v1"
OUT = ROOT / "data" / "models"
S3 = "s3://fb-soymate-team4-258601136235/derived/models/"
CLASSES = ["sound", "broken", "stained", "immature", "insect_hole", "impurity"]
DATASETS = {"soybean_d97rjyk2tz": "soybean d97rjyk2tz", "lin_v6vzvfszj6": "soybean Lin v6vzvfszj6",
            "harvest_hwdtghttp7": "harvest hwdtghttp7"}
C_GRID = [0.01, 0.03, 0.1, 0.3, 1.0]


def warning_text() -> str:
    d = json.loads((ROOT / "results" / "dataset_id.json").read_text())["result"]["dinov2-small"]
    acc = d["probe_sound"]["accuracy"]
    return ("Classes come from different datasets; on photos from a new camera setup the class shares are "
            f"uncalibrated (dataset-ID check: {100 * acc:.0f} %).")


def per_dataset_f1(model, df) -> dict:
    out = {}
    for ds, g in df.groupby("dataset"):
        labels = sorted(g["class"].unique())
        out[ds] = per_class_f1(g["class"], predict(model, g), labels)["macro"]
    return out


def main():
    df = load()
    df = df[df["dataset"].isin(DATASETS) & df["class"].isin(CLASSES)]
    df = df[df["multi_seed"].astype(str) != "True"]
    rep = df["eval_rep"].astype(str) == "True"
    train = df[df["split"] == "train"]
    val, test = df[(df["split"] == "val") & rep], df[(df["split"] == "test") & rep]
    y = train["class"].to_numpy()

    val_by_c = {}
    for c in C_GRID:
        m = FrozenLogReg(C=c).fit(train, y)
        f = per_dataset_f1(m, val)
        val_by_c[c] = round(float(np.mean(list(f.values()))), 4)
        print(f"C={c}: val mean macro F1 {val_by_c[c]}  {f}", flush=True)
    best = max(val_by_c, key=val_by_c.get)
    model = FrozenLogReg(C=best).fit(train, y)

    test_f1 = {}
    for ds, g in test.groupby("dataset"):
        labels = sorted(g["class"].unique())
        r = grouped_bootstrap_f1(g["class"], predict(model, g), g["group"].astype(str), labels)
        test_f1[ds] = {"macro": r["macro"], "per_class": {c: r[c] for c in labels},
                       "n_items": r["n_items"], "n_groups": r["n_groups"]}

    OUT.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUT / f"{NAME}.joblib")
    card = {
        "name": NAME,
        "features": "facebook/dinov2-small, CLS + mean patch token on 224 px masked crops (pipeline/make_crops.py)",
        "classifier": f"StandardScaler + multinomial logistic regression, class_weight=balanced, C={best}",
        "classes": [c for c in CLASSES if c in model.classes_],
        "model_class_order": [str(c) for c in model.classes_],
        "trained_on": list(DATASETS.values()),
        "train_split_only": True,
        "train_counts": {ds: g["class"].value_counts().to_dict() for ds, g in train.groupby("dataset")},
        "val_mean_macro_f1_by_C": val_by_c,
        "test_macro_f1": test_f1,
        "test_protocol": "test split, eval_rep rows (one crop per photo / original image only), "
                         "multi-seed crops excluded, 95 % CI from 2000 bootstrap resamples over groups",
        "warning": warning_text(),
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (OUT / f"{NAME}.json").write_text(json.dumps(card, indent=2, default=int))
    print(json.dumps({k: card[k] for k in ["classifier", "train_counts", "test_macro_f1"]}, indent=1, default=int))
    for ext in ("joblib", "json"):
        subprocess.run(["aws", "s3", "cp", str(OUT / f"{NAME}.{ext}"), S3, "--quiet"], check=True)
    print(f"backed up to {S3}")


if __name__ == "__main__":
    main()
