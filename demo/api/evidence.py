"""Evidence cards for GET /api/evidence, built from results/*.json at startup (numbers copied by code).

Headlines and caveats follow the wording of results/README.md; every number in them is read from the JSON.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
PROVENANCE_URL = "https://github.com/fede-bello/soymate/blob/main/results/README.md"


def res(name: str) -> dict:
    return json.loads((RESULTS / f"{name}.json").read_text())["result"]


def f3(x) -> str:
    return f"{x:.3f}"


def ci(lo_hi, fmt=f3) -> str:
    return f"[{fmt(lo_hi[0])}, {fmt(lo_hi[1])}]"


def pct(x) -> str:
    return f"{x:.1f} %"


def num(label, value, ci95=None) -> dict:
    return {"label": label, "value": value, "ci95": ci95}


def card_r1() -> dict:
    r = res("r1_leaky_vs_clean")
    leak = r["published_test_in_train"]["all_v2_images__by_photo"]
    burst = r["published_test_in_train"]["all_v2_images__by_burst"]
    a, f = r["A"]["one_per_photo"], r["F"]["one_per_photo"]
    raw = r["A_raw"]["all_test"]  # as distributed: every published test image, duplicates kept
    return {"id": "r1", "title": "The published split leaks",
            "headline": f"{leak['k']}/{leak['n']} published test images ({100 * leak['share']:.1f} %) share an "
                        f"original photo with published train ({100 * burst['share']:.1f} % share a capture burst). "
                        f"A clean burst-level split drops macro F1 from {f3(raw['macro']['f1'])} to "
                        f"{f3(f['macro']['f1'])}.",
            "numbers": [num("macro F1, as distributed (published split, duplicates kept)", f3(raw["macro"]["f1"]), ci(raw["macro"]["ci95"])),
                        num("macro F1, published split, full image", f3(a["macro"]["f1"]), ci(a["macro"]["ci95"])),
                        num("macro F1, burst-level split, masked crop (ours)", f3(f["macro"]["f1"]), ci(f["macro"]["ci95"])),
                        num("insect_hole F1, ours", f3(f["insect_hole"]["f1"]), ci(f["insect_hole"]["ci95"]))],
            "caveat": "Leakage inflates macro F1 by a few points and the intervals overlap. insect_hole F1 near 1.00 in "
                      "every arm is not credible as hole detection on its own: most hole photos come from sessions "
                      "with no other class (see the session control).",
            "source": "results/r1_leaky_vs_clean.json"}


def card_r2() -> dict:
    r = res("r2_per_class")["dinov2-small"]
    s, l = r["soybean"], r["lin"]
    nums = [num(f"soybean {c.replace('_', ' ')} F1", f3(s["f1"][c]["f1"]), ci(s["f1"][c]["ci95"]))
            for c in ("broken", "sound", "insect_hole")]
    nums += [num("soybean macro F1", f3(s["f1"]["macro"]["f1"]), ci(s["f1"]["macro"]["ci95"])),
             num("Lin macro F1", f3(l["f1"]["macro"]["f1"]), ci(l["f1"]["macro"]["ci95"]))]
    return {"id": "r2", "title": "Per-class accuracy, within each dataset",
            "headline": f"On a clean split, broken vs sound reaches F1 {f3(s['f1']['broken']['f1'])} on soybean "
                        f"({s['n_test_reps']} test seeds, {s['f1']['n_groups']} bursts) and macro F1 "
                        f"{f3(l['f1']['macro']['f1'])} on Lin's four classes.",
            "numbers": nums,
            "caveat": "Soybean test has only " + str(s["f1"]["n_groups"]) + " independent bursts, so intervals are "
                      "wide. Errors are mostly sound seeds called broken.",
            "source": "results/r2_per_class.json"}


def card_session() -> dict:
    r = res("r2_session_control")["dinov2-small"]
    same = r["light_background_same_days_13_14"]
    cross = r["cross_session_train_holes_9_11_test_holes_13_14"]
    nb = same["eval_bursts_per_class"]["insect_hole"]
    return {"id": "r2_session", "title": "Is hole detection real? Session control",
            "headline": f"On the only days with both holes and sound seeds, hole F1 is "
                        f"{f3(same['f1']['insect_hole']['f1'])}; a model that never saw a hole from those days still "
                        f"finds them (F1 {f3(cross['f1']['insect_hole']['f1'])}).",
            "numbers": [num("hole F1, same days and background", f3(same["f1"]["insect_hole"]["f1"]),
                            ci(same["f1"]["insect_hole"]["ci95"])),
                        num("hole F1, trained on other sessions only", f3(cross["f1"]["insect_hole"]["f1"]),
                            ci(cross["f1"]["insect_hole"]["ci95"])),
                        num("hole bursts evaluated", str(nb))],
            "caveat": f"Features do encode the capture session. With {nb} hole bursts this is indicative, not conclusive.",
            "source": "results/r2_session_control.json"}


def card_dataset_id() -> dict:
    d = res("dataset_id")["dinov2-small"]
    ps, pb, pt = d["probe_sound"], d["probe_broken"], d["probe_sound_texture_center50"]
    fp = d["cross_dataset_false_positive"]
    lin, soy = fp["lin_v6vzvfszj6"], fp["soybean_d97rjyk2tz"]
    pc = lambda lo_hi: f"[{lo_hi[0]:.1f}, {lo_hi[1]:.1f}]"
    return {"id": "dataset_id", "title": "A model can tell which dataset a seed came from",
            "headline": f"A probe tells soybean d97rjyk2tz from Lin with {100 * ps['accuracy']:.0f} % accuracy on "
                        f"sound seeds, also from a texture-only central patch ({100 * pt['accuracy']:.0f} %). "
                        "Pooled class shares are uncalibrated on a new camera setup.",
            "numbers": [num("accuracy, sound seeds", f3(ps["accuracy"]), ci(ps["accuracy_wilson95"])),
                        num("accuracy, broken seeds", f3(pb["accuracy"]), ci(pb["accuracy_wilson95"])),
                        num("accuracy, central texture patch", f3(pt["accuracy"]), ci(pt["accuracy_wilson95"])),
                        num("Lin sound seeds flagged defective by the pooled model", pct(lin["pct_pred_defect"]),
                            pc(lin["pct_pred_defect_wilson95"])),
                        num("soybean sound seeds flagged defective", pct(soy["pct_pred_defect"]),
                            pc(soy["pct_pred_defect_wilson95"]))],
            "caveat": "Per-class numbers are reported within each dataset; a pooled model is not evidence of defect "
                      "recognition across setups.",
            "source": "results/dataset_id.json"}


def card_r3() -> dict:
    r = res("r3_transfer")
    cur = {(c["mapping"], c["direction"], c["arm"], c["k"]): c for c in r["curve"]}
    m = "a_broken+skin"
    z = cur[(m, "soybean->lin", "source+k", 0)]
    sk = cur[(m, "soybean->lin", "source+k", 10)]
    tk = cur[(m, "soybean->lin", "target_only_k", 10)]
    ceil = cur[(m, "soybean->lin", "ceiling_target_full", -1)]
    back = cur[(m, "lin->soybean", "source+k", 0)]
    return {"id": "r3", "title": "Another setup's data does not replace local labels",
            "headline": f"On Lin, 10 local labels per class alone reach macro F1 {tk['f1_macro_mean']:.2f}, against "
                        f"{sk['f1_macro_mean']:.2f} for ~1,000 soybean images plus the same 10 labels.",
            "numbers": [num("soybean -> Lin, no target labels", f"{z['f1_macro_mean']:.2f}",
                            ci([z["ci_lo_macro_mean"], z["ci_hi_macro_mean"]], lambda x: f"{x:.2f}")),
                        num("soybean -> Lin, source + 10 per class", f"{sk['f1_macro_mean']:.2f}"),
                        num("Lin, 10 per class only", f"{tk['f1_macro_mean']:.2f}"),
                        num("Lin, all target labels (ceiling)", f"{ceil['f1_macro_mean']:.2f}",
                            ci([ceil["ci_lo_macro_mean"], ceil["ci_hi_macro_mean"]], lambda x: f"{x:.2f}")),
                        num("Lin -> soybean, no target labels", f"{back['f1_macro_mean']:.2f}")],
            "caveat": "Mean over 10 random draws. Part of the drop is label shift: Lin 'broken' includes skin damage, "
                      "soybean 'broken' is testa cracking. For a new crop or camera, budget for labelled target data.",
            "source": "results/r3_transfer.json"}


def card_r4a() -> dict:
    r = res("r4_ghana_counts")
    a = r["a_vs_published_boxes_gt_ok"]["overall"]
    b = r["b_vs_n_seeds_est_SEMI_AUTOMATIC_ESTIMATE"]["overall"]
    p = lambda lo_hi: f"[{lo_hi[0]:.1f}, {lo_hi[1]:.1f}]"
    return {"id": "r4a", "title": "Counting seeds on real farmer photos",
            "headline": f"On Ghana phone photos (sun and hard shadow), our training-free segmenter is off by "
                        f"{a['mae']['value']:.1f} seeds on average ({a['mape_pct']['value']:.1f} %) against the "
                        f"{a['n_photos']} complete published counts.",
            "numbers": [num("mean absolute error, seeds", f"{a['mae']['value']:.1f}", p(a["mae"]["ci95"])),
                        num("mean absolute % error", pct(a["mape_pct"]["value"]), p(a["mape_pct"]["ci95"])),
                        num(f"% error vs semi-automatic estimate ({b['n_photos']} photos, not ground truth)",
                            pct(b["mape_pct"]["value"]), p(b["mape_pct"]["ci95"]))],
            "caveat": "Only 7 photos have complete published counts, all FarmerSaved/Favor and mostly in sun. Failure "
                      "modes: seeds cut by the photo border, dark table edges, single seeds counted as two.",
            "source": "results/r4_ghana_counts.json"}


def card_r4b() -> dict:
    r = res("r4_harvest_lots")
    t, f = r["test_lots"], r["per_seed_f1_crushed_test6"]
    dd = r["decision_demo"]["counts_raw_wilson"]
    p = lambda lo_hi: f"[{lo_hi[0]:.1f}, {lo_hi[1]:.1f}]"
    return {"id": "r4b", "title": "Lot-level % crushed: right for the wrong reasons",
            "headline": f"On {t['n_lots']} held-out harvest lots the % crushed is off by "
                        f"{t['mae_raw_pp']['mean']:.1f} points on average, but per-seed crushed F1 is only "
                        f"{f3(f['f1'])}: errors cancel near {t['pooled_true_pct']:.0f} % prevalence.",
            "numbers": [num("lot % error, mean absolute (pp)", f"{t['mae_raw_pp']['mean']:.1f}", p(t["mae_raw_pp"]["ci95"])),
                        num("per-seed crushed F1", f3(f["f1"]), ci(f["ci95"])),
                        num("true % inside the raw Wilson interval (sampling error only)",
                            f"{t['coverage_raw_wilson']}/{t['n_lots']} lots"),
                        num("lots at an illustrative 5 % threshold (raw Wilson)",
                            ", ".join(f"{v} {k}" for k, v in dd.items()))],
            "caveat": "Intervals are raw Wilson: they cover sampling error only, not classifier bias. Per-seed "
                      f"crushed F1 is only {f['f1']:.2f}, so the accurate lot % comes from errors cancelling. "
                      "Oracle segmentation (the dataset's own masks): this measures classification only. On a clean "
                      "lot the same classifier would report a few % crushed. Show both sampling error and classifier "
                      "bias, and say 'inconclusive' when the interval straddles the threshold.",
            "source": "results/r4_harvest_lots.json"}


def card_robustness() -> dict:
    r = res("demo_smoke")["ghana_gt_ok"]
    ch = r["reencode_abs_change_defect_pp"]
    return {"id": "robustness", "title": "Robustness to image quality",
            "headline": f"Seed counts are stable ({r['reencode_count_changes']} of {r['n_photos']} counts changed), "
                        f"but class shares move by {ch['mean']:.1f} pp on average (up to {ch['max']:.1f} pp) when the "
                        "same photo is downscaled and re-compressed.",
            "numbers": [num("count error vs published count, mean (seeds)", f"{r['mae_seeds']:.1f}"),
                        num("defect share change after re-compression, mean (pp)", f"{ch['mean']:.1f}"),
                        num("defect share change, max (pp)", f"{ch['max']:.1f}"),
                        num("photos", str(r["n_photos"]))],
            "caveat": "Class shares on Ghana photos are uncalibrated: this camera setup was never seen in training. "
                      "Re-compression = downscale to 2000 px and save as JPEG quality 95.",
            "source": "results/demo_smoke.json"}


def build() -> dict:
    cards = []
    for fn in (card_r1, card_r2, card_session, card_dataset_id, card_r3, card_r4a, card_r4b, card_robustness):
        try:
            cards.append(fn())
        except (KeyError, FileNotFoundError) as e:
            print(f"evidence: skipped {fn.__name__}: {e!r}", flush=True)
    return {"cards": cards, "provenance_url": PROVENANCE_URL}


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
