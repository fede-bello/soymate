"""Demo smoke numbers: the API pipeline end to end on held-out images, written to results/demo_smoke.json.

Run on the box:  cd ~/soymate && uv run python -m app.api.smoke
a) Ghana: the 7 gt_status=ok photos (complete published counts), original resolution, mode auto.
   Also re-run each photo after the example treatment (2000 px INTER_AREA + JPEG q95) to see how stable the
   class shares are under re-encoding (counts should not move; shares on this unseen setup may).
b) d97rjyk2tz: 20 test-split single-seed images (eval_rep, not multi-seed), stratified over the 3 classes with a
   fixed seed, mode auto and mode single; accuracy of the dominant seed's class vs the dataset label.
"""
import io
import sys
import time

import cv2
import pandas as pd
from PIL import Image

from app.api.pipeline import MAX_PX, ROOT, Pipeline, analyze, load_image

sys.path.insert(0, str(ROOT / "eval"))
from harness import wilson, write_result  # noqa: E402

GHANA = ROOT / "data" / "raw" / "ghana_soybean"
SOY_V2 = ROOT / "data" / "raw" / "soybean_v2" / "Soybean_Seed_Dataset" / "Soybean_Seed_Dataset"
N_SOY = 20


def reencode(data: bytes) -> bytes:
    rgb = load_image(data)
    s = MAX_PX / max(rgb.shape[:2])
    if s < 1:
        rgb = cv2.resize(rgb, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    buf = io.BytesIO()
    Image.fromarray(rgb).save(buf, "JPEG", quality=95)
    return buf.getvalue()


def main():
    pipe = Pipeline()
    p = pd.read_csv(ROOT / "results" / "r4_ghana_counts__photos.csv")
    rows = []
    for _, r in p[p["gt_status"] == "ok"].iterrows():
        data = (GHANA / r["photo"]).read_bytes()
        t = time.perf_counter()
        a = analyze(pipe, data)
        sec = round(time.perf_counter() - t, 2)
        b = analyze(pipe, reencode(data))
        rows.append({"photo": r["photo"], "published_count": int(r["n_boxes"]), "api_count": a["summary"]["n_seeds"],
                     "mode": a["mode"], "n_instances": len(a["seeds"]), "defect_pct": a["summary"]["defect"]["pct"],
                     "verdict": a["verdict"]["status"], "seconds": sec, "reencoded_count": b["summary"]["n_seeds"],
                     "reencoded_defect_pct": b["summary"]["defect"]["pct"]})
        print(rows[-1], flush=True)
    g = pd.DataFrame(rows)
    err = g["api_count"] - g["published_count"]

    m = pd.read_csv(ROOT / "data" / "crops" / "manifest.csv", keep_default_na=False)
    m = m[(m["dataset"] == "soybean_d97rjyk2tz") & (m["split"] == "test") & (m["eval_rep"].astype(str) == "True")
          & (m["multi_seed"].astype(str) != "True")]
    per = {c: n for c, n in zip(["sound", "broken", "insect_hole"], [7, 7, 6])}
    sample = pd.concat([m[m["class"] == c].sample(n, random_state=0) for c, n in per.items()])
    srows = []
    for _, r in sample.iterrows():
        data = (SOY_V2 / r["source_image"]).read_bytes()
        out = {"image": r["source_image"], "label": r["class"]}
        for mode in ("auto", "single"):
            t = time.perf_counter()
            a = analyze(pipe, data, mode)
            top = max(a["seeds"], key=lambda s: (s["bbox"][2] - s["bbox"][0]) * (s["bbox"][3] - s["bbox"][1]))
            out |= {f"{mode}_mode": a["mode"], f"{mode}_n_instances": len(a["seeds"]), f"{mode}_pred": top["class"],
                    f"{mode}_seconds": round(time.perf_counter() - t, 3)}
        srows.append(out)
        print(out, flush=True)
    s = pd.DataFrame(srows)

    def acc(col):
        k, n = int((s[col] == s["label"]).sum()), len(s)
        return {"correct": k, "n": n, "accuracy": round(k / n, 3), "wilson95": [round(x, 3) for x in wilson(k, n)]}

    result = {
        "ghana_gt_ok": {"n_photos": len(g), "mae_seeds": round(float(err.abs().mean()), 2),
                        "mean_signed_error": round(float(err.mean()), 2),
                        "mape_pct": round(float(100 * (err.abs() / g["published_count"]).mean()), 2),
                        "max_abs_error": int(err.abs().max()), "modes": g["mode"].value_counts().to_dict(),
                        "median_seconds": float(g["seconds"].median()),
                        "reencode_abs_change_defect_pp": {
                            "mean": round(float((g["defect_pct"] - g["reencoded_defect_pct"]).abs().mean()), 2),
                            "max": round(float((g["defect_pct"] - g["reencoded_defect_pct"]).abs().max()), 2)},
                        "reencode_count_changes": int((g["api_count"] != g["reencoded_count"]).sum()),
                        "photos": rows},
        "soybean_test_single": {"n_images": len(s), "per_class": per, "auto": acc("auto_pred"),
                                "single": acc("single_pred"),
                                "auto_mode_counts": s["auto_mode"].value_counts().to_dict(),
                                "median_seconds_auto": float(s["auto_seconds"].median()),
                                "confusion_auto": pd.crosstab(s["label"], s["auto_pred"]).to_dict()},
    }
    how = ("app/api/pipeline.analyze (the code behind POST /api/analyze) run in-process on the box with model "
           "soymate-pooled-v1. Ghana: the 7 gt_status=ok photos at original resolution, mode auto, count = "
           "summary.n_seeds vs the complete published box count. Soybean d97rjyk2tz: 20 test-split images (eval_rep, "
           "not multi-seed), 7 sound / 7 broken / 6 insect_hole sampled with random_state=0; prediction = class of "
           "the largest returned seed, in mode auto and mode single; Wilson 95 % CI (ignores burst clustering). "
           "Seconds are wall-clock per call including JPEG decode, on c7i.4xlarge. Re-encode check: the same Ghana photo "
           "downscaled to 2000 px (INTER_AREA) and saved as JPEG q95, like the demo examples; defect share = any class "
           "except sound.")
    write_result("demo_smoke", result, how, {"ghana": g, "soybean": s})
    print(result["ghana_gt_ok"] | {"photos": None}, result["soybean_test_single"], flush=True)


if __name__ == "__main__":
    main()
