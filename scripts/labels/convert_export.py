"""Convert a Label Studio JSON export of seed points into data/labels/points.csv and per-region counts.

Usage: uv run python scripts/labels/convert_export.py [data/labels/export.json]
points.csv: one row per point (region, x, y in region pixels, x_src, y_src in source-photo pixels, class).
counts.csv: one row per region with the count per class, total seeds and the % per class with Wilson 95 % CIs.
"""
import json
import sys
from pathlib import Path

import pandas as pd
from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parents[2]
LABELS = ROOT / "data" / "labels"

if __name__ == "__main__":
    export = Path(sys.argv[1]) if len(sys.argv) > 1 else LABELS / "export.json"
    regions = pd.read_csv(LABELS / "regions.csv").set_index("name")
    rows = []
    for task in json.loads(export.read_text()):
        # Uploaded files get a random prefix ("<hash>-<name>.jpg"); match on the known region names.
        src = task["data"]["image"]
        name = next(n for n in regions.index if n in src)
        ann = [a for a in task["annotations"] if not a.get("was_cancelled")]
        for r in (ann[-1]["result"] if ann else []):
            if r.get("type") != "keypointlabels":
                continue
            w, h = r["original_width"], r["original_height"]
            x, y = r["value"]["x"] / 100 * w, r["value"]["y"] / 100 * h
            rows.append({"region": name, "x": round(x, 1), "y": round(y, 1),
                         "x_src": round(x + regions.at[name, "x1"], 1), "y_src": round(y + regions.at[name, "y1"], 1),
                         "class": r["value"]["keypointlabels"][0]})
    pts = pd.DataFrame(rows)
    pts.to_csv(LABELS / "points.csv", index=False)
    seeds = pts[pts["class"] != "not_a_seed"]
    out = []
    for name, g in seeds.groupby("region"):
        n = len(g)
        rec = {"region": name, "n_seeds": n}
        for c, k in g["class"].value_counts().items():
            lo, hi = proportion_confint(k, n, method="wilson")
            rec |= {f"n_{c}": k, f"pct_{c}": round(100 * k / n, 2), f"ci95_{c}": f"[{100 * lo:.1f}, {100 * hi:.1f}]"}
        out.append(rec)
    pd.DataFrame(out).to_csv(LABELS / "counts.csv", index=False)
    print(pd.DataFrame(out).T.to_string())
