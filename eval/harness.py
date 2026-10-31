"""Shared evaluation harness: data loading, the model interface, metrics with grouped CIs, result writing.

Every experiment script (eval/r1_*.py, eval/r2_*.py, ...) uses only this module, so a different model can be
plugged in without touching them.

Plugging in a model (teammate B): write a class with
    fit(train: pd.DataFrame, y: np.ndarray) -> self
    predict_proba(df: pd.DataFrame) -> np.ndarray   # (n, len(classes_)), columns ordered as classes_
    classes_: np.ndarray
`df` rows are manifest rows (column `crop` = path under data/crops/, plus `dataset`, `group`, `split`, `class`)
with the cached feature columns f0..fN attached. A model can use the features or open the crop images itself.
Register it in MODELS below and pass --model <name> to the experiment scripts.
"""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parents[1]
CROPS = ROOT / "data" / "crops"
FEATS = ROOT / "data" / "features"
RESULTS = ROOT / "results"
SEED = 0
N_BOOT = 2000


# --------------------------------------------------------------------------- data
def load(features: str = "dinov2-small", kind: str = "crops") -> pd.DataFrame:
    """Manifest rows (kind='crops') or soybean split rows (kind='soybean_full') joined with cached features."""
    f = pd.read_parquet(FEATS / f"{features}__{kind}.parquet")
    if kind == "crops":
        m = pd.read_csv(CROPS / "manifest.csv", keep_default_na=False)
        m = m[m["crop"] != ""]
        return m.merge(f, left_on="crop", right_on="key", how="inner").drop(columns="key")
    s = pd.read_csv(ROOT / "data" / "splits" / "soybean.csv", keep_default_na=False)
    return s.merge(f, left_on="image", right_on="key", how="inner").drop(columns="key")


def feature_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("f") and c[1:].isdigit()]


# --------------------------------------------------------------------------- models
class FrozenLogReg:
    """Default model: standardised frozen DINOv2 features + multinomial logistic regression."""

    def __init__(self, C: float = 0.5, balanced: bool = True):
        self.C, self.balanced = C, balanced

    def fit(self, train: pd.DataFrame, y: np.ndarray):
        self.cols = feature_cols(train)
        self.clf = make_pipeline(StandardScaler(), LogisticRegression(
            C=self.C, max_iter=3000, class_weight="balanced" if self.balanced else None))
        self.clf.fit(train[self.cols].to_numpy(), y)
        self.classes_ = self.clf.classes_
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        return self.clf.predict_proba(df[self.cols].to_numpy())


MODELS = {"logreg": FrozenLogReg}


def predict(model, df: pd.DataFrame) -> np.ndarray:
    return model.classes_[model.predict_proba(df).argmax(1)]


# --------------------------------------------------------------------------- metrics
def per_class_f1(y_true, y_pred, labels) -> dict:
    f = f1_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    out = {str(c): float(v) for c, v in zip(labels, f)}
    out["macro"] = float(np.mean(f))
    return out


def grouped_bootstrap_f1(y_true, y_pred, groups, labels, n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    """Per-class and macro F1 with 95 % percentile CIs, resampling whole groups (original photos)."""
    y_true, y_pred, groups = map(np.asarray, (y_true, y_pred, groups))
    uniq = np.unique(groups)
    idx_by_group = {g: np.nonzero(groups == g)[0] for g in uniq}
    rng = np.random.default_rng(seed)
    point = per_class_f1(y_true, y_pred, labels)
    draws = {k: [] for k in point}
    for _ in range(n_boot):
        idx = np.concatenate([idx_by_group[g] for g in rng.choice(uniq, len(uniq), replace=True)])
        for k, v in per_class_f1(y_true[idx], y_pred[idx], labels).items():
            draws[k].append(v)
    return {k: {"f1": round(point[k], 4), "ci95": [round(float(np.percentile(draws[k], 2.5)), 4),
                                                  round(float(np.percentile(draws[k], 97.5)), 4)]}
            for k in point} | {"n_items": int(len(y_true)), "n_groups": int(len(uniq)), "n_boot": n_boot}


def confusion(y_true, y_pred, labels) -> dict:
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return {"labels": [str(c) for c in labels], "rows_true_cols_pred": cm.tolist()}


def wilson(k: int, n: int, alpha: float = 0.05) -> list[float]:
    lo, hi = proportion_confint(k, n, alpha=alpha, method="wilson")
    return [float(lo), float(hi)]


# --------------------------------------------------------------------------- results
def git_rev() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown (box copy is not a git checkout)"


def write_result(name: str, result: dict, how: str, tables: dict[str, pd.DataFrame] | None = None) -> Path:
    """results/<name>.json with the numbers, how they were obtained, and provenance; optional CSV tables."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    payload = {"name": name, "how": how, "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "code_rev": git_rev(), "result": result}
    path = RESULTS / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    for tname, t in (tables or {}).items():
        t.to_csv(RESULTS / f"{name}__{tname}.csv", index=False)
    print(f"wrote {path}", flush=True)
    return path
