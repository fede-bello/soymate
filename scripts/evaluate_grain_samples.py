#!/usr/bin/env python3
"""Evaluate sample reports against manually counted, grouped photographs."""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def divide(numerator, denominator):
    """Return a ratio or None when it is undefined."""
    return numerator / denominator if denominator else None


def check_manifest(photos):
    """Validate annotation completeness and prevent physical-set split leakage."""
    if not isinstance(photos, list) or not photos:
        raise ValueError("Manifest photos must be a nonempty list")
    splits = defaultdict(set)
    for photo in photos:
        for field in ("sample_json", "species", "physical_set_id", "split", "provenance", "manual_total", "damage_complete"):
            if field not in photo:
                raise ValueError(f"Missing required photo field: {field}")
        if any(not isinstance(photo[field], str) or not photo[field].strip()
               for field in ("sample_json", "species", "physical_set_id", "provenance")):
            raise ValueError("Path, species, physical set and provenance must be nonempty strings")
        if photo["split"] not in ("development", "final"):
            raise ValueError("Split must be development or final")
        if type(photo["manual_total"]) is not int or photo["manual_total"] < 0:
            raise ValueError("manual_total must be a nonnegative integer")
        if type(photo["damage_complete"]) is not bool:
            raise ValueError("damage_complete must be boolean")
        grains = photo.get("grains", [])
        if not isinstance(grains, list):
            raise ValueError("grains must be a list")
        if grains and len(grains) != photo["manual_total"]:
            raise ValueError("Provide either no centres or exactly manual_total centres")
        for grain in grains:
            if grain.get("status") not in ("hole", "no_hole", "uncertain"):
                raise ValueError("Grain status must be hole, no_hole, or uncertain")
            if any(type(grain.get(axis)) not in (int, float) or not math.isfinite(grain[axis]) for axis in ("x", "y")):
                raise ValueError("Grain centres must have finite numeric x and y")
        if photo["damage_complete"] and (len(grains) != photo["manual_total"] or
                                          any(grain["status"] == "uncertain" for grain in grains)):
            raise ValueError("Complete damage truth requires a known status for every grain")
        splits[photo["physical_set_id"]].add(photo["split"])
    crossing = sorted(identifier for identifier, values in splits.items() if len(values) > 1)
    if crossing:
        raise ValueError(f"Physical-set IDs cross development/final: {crossing}")


def evaluate_photo(photo, sample, labels, mode):
    """Evaluate counts and one-to-one centre containment for one photograph.

    Multiple centres inside an instance reveal a merge. Unmatched predictions are
    extras or possible splits: centre-only truth cannot distinguish those cases.
    """
    if mode not in sample["results"]:
        raise ValueError(f"Mode {mode} missing from {photo['sample_json']}")
    if labels.shape != (sample["input"]["height"], sample["input"]["width"]):
        raise ValueError("Instance image dimensions do not match sample metadata")
    components = {component["id"]: component for component in sample["components"]}
    flagged = set(sample["results"][mode]["flagged_ids"])
    if not flagged <= set(components):
        raise ValueError("Flagged IDs do not match instance components")
    predicted_total, true_total = len(components), photo["manual_total"]
    error = predicted_total - true_total
    result = {"sample_json": photo["sample_json"], "species": photo["species"],
              "physical_set_id": photo["physical_set_id"], "split": photo["split"],
              "capture_id": photo.get("capture_id", ""), "source_bag": photo.get("source_bag", ""),
              "provenance": photo["provenance"], "mode": mode, "manual_total": true_total,
              "predicted_total": predicted_total, "count_error": error, "absolute_count_error": abs(error),
              "count_absolute_percentage_error": 100 * abs(error) / true_total if true_total else None,
              "matched_grains": None, "missed_grains": None, "extra_or_split_instances": None,
              "merged_instances": None, "manual_holed": None, "predicted_holed": None,
              "damage_count_error": None, "absolute_damage_count_error": None,
              "true_percentage": None, "predicted_percentage": None, "percentage_point_error": None,
              "percentage_with_manual_denominator": None, "tp": None, "fp": None, "fn": None,
              "precision": None, "recall": None, "f1": None}
    grains = photo.get("grains", [])
    matches, containing = {}, defaultdict(list)
    if grains:
        height, width = labels.shape
        for index, grain in enumerate(grains):
            x, y = grain["x"], grain["y"]
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"Manual grain centre outside upright image: {x}, {y}")
            identifier = int(labels[int(y), int(x)])
            if identifier in components:
                centroid = components[identifier]["centroid"]
                containing[identifier].append(((centroid[0] - x) ** 2 + (centroid[1] - y) ** 2, index))
        for identifier, candidates in containing.items():
            _, index = min(candidates)
            matches[identifier] = index
        result.update(matched_grains=len(matches), missed_grains=true_total - len(matches),
                      extra_or_split_instances=predicted_total - len(matches),
                      merged_instances=sum(len(values) > 1 for values in containing.values()))
    elif true_total == 0:
        result.update(matched_grains=0, missed_grains=0, extra_or_split_instances=predicted_total, merged_instances=0)
    if photo["damage_complete"]:
        true_holed = sum(grain["status"] == "hole" for grain in grains)
        predicted_holed = len(flagged)
        true_percentage = 100 * true_holed / true_total if true_total else None
        predicted_percentage = 100 * predicted_holed / predicted_total if predicted_total else None
        true_positive = sum(grains[index]["status"] == "hole" and identifier in flagged
                            for identifier, index in matches.items())
        false_positive = sum(identifier in flagged and grains[index]["status"] == "no_hole"
                             for identifier, index in matches.items()) + len(flagged - set(matches))
        false_negative = true_holed - true_positive
        precision = divide(true_positive, true_positive + false_positive)
        recall = divide(true_positive, true_positive + false_negative)
        result.update(manual_holed=true_holed, predicted_holed=predicted_holed,
                      damage_count_error=predicted_holed - true_holed,
                      absolute_damage_count_error=abs(predicted_holed - true_holed),
                      true_percentage=true_percentage, predicted_percentage=predicted_percentage,
                      percentage_point_error=abs(predicted_percentage - true_percentage)
                      if true_percentage is not None and predicted_percentage is not None else None,
                      percentage_with_manual_denominator=100 * predicted_holed / true_total if true_total else None,
                      tp=true_positive, fp=false_positive, fn=false_negative, precision=precision, recall=recall,
                      f1=divide(2 * true_positive, 2 * true_positive + false_positive + false_negative))
    return result


def summarize_group(rows):
    """Summarize per-photo metrics and pooled grain counts for one metadata group."""
    def average(key):
        values = [row[key] for row in rows if row[key] is not None]
        return sum(values) / len(values) if values else None
    def average_by_set(key):
        values_by_set = defaultdict(list)
        for row in rows:
            if row[key] is not None:
                values_by_set[row["physical_set_id"]].append(row[key])
        averages = [sum(values) / len(values) for values in values_by_set.values()]
        return sum(averages) / len(averages) if averages else None
    labelled = [row for row in rows if row["tp"] is not None]
    totals = {key: sum(row[key] for row in labelled) for key in ("tp", "fp", "fn")}
    return {"photos": len(rows), "physical_sets": len({row["physical_set_id"] for row in rows}),
            "fully_damage_labelled_photos": len(labelled),
            "mean_count_error": average("count_error"), "count_mae": average("absolute_count_error"),
            "mean_count_absolute_percentage_error": average("count_absolute_percentage_error"),
            "mean_absolute_damage_count_error": average("absolute_damage_count_error"),
            "mean_absolute_percentage_point_error": average("percentage_point_error"),
            "set_weighted_count_mae": average_by_set("absolute_count_error"),
            "set_weighted_count_absolute_percentage_error": average_by_set("count_absolute_percentage_error"),
            "set_weighted_absolute_damage_count_error": average_by_set("absolute_damage_count_error"),
            "set_weighted_absolute_percentage_point_error": average_by_set("percentage_point_error"),
            "pooled_tp": totals["tp"] if labelled else None, "pooled_fp": totals["fp"] if labelled else None,
            "pooled_fn": totals["fn"] if labelled else None,
            "pooled_precision": divide(totals["tp"], totals["tp"] + totals["fp"]) if labelled else None,
            "pooled_recall": divide(totals["tp"], totals["tp"] + totals["fn"]) if labelled else None,
            "pooled_f1": divide(2 * totals["tp"], 2 * totals["tp"] + totals["fp"] + totals["fn"]) if labelled else None}


def evaluate_manifest(manifest_path, mode):
    """Read manifest and artifacts, returning per-photo rows and grouped results."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    photos = manifest["photos"]
    check_manifest(photos)
    rows, fingerprints, image_splits = [], defaultdict(set), defaultdict(set)
    for photo in photos:
        sample_path = Path(photo["sample_json"])
        if not sample_path.is_absolute():
            sample_path = manifest_path.parent / sample_path
        sample = json.loads(sample_path.read_text(encoding="utf-8"))
        image_splits[sample["input"]["sha256"]].add(photo["split"])
        with Image.open(sample_path.parent / "instances.png") as label_image:
            labels = np.asarray(label_image)
        if photo["species"] != sample["metadata"]["species"] or photo["provenance"] != sample["metadata"]["provenance"]:
            raise ValueError(f"Manifest species/provenance differs from sample: {sample_path}")
        row = evaluate_photo(photo, sample, labels, mode)
        rows.append(row)
        config = sample["configuration"].copy()
        config.pop("mode", None)
        fingerprint = json.dumps({"checkpoint": sample["checkpoint"]["sha256"], "settings": config}, sort_keys=True)
        fingerprints[photo["species"]].add(fingerprint)
    if any(len(splits) > 1 for splits in image_splits.values()):
        raise ValueError("An identical input image occurs in both development and final splits")
    if any(len(settings) > 1 for settings in fingerprints.values()):
        raise ValueError("Inconsistent checkpoint or settings within a species; evaluate frozen configurations separately")
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["split"], row["species"], row["provenance"])].append(row)
    groups = [{"split": key[0], "species": key[1], "provenance": key[2]} | summarize_group(group)
              for key, group in sorted(grouped.items())]
    return rows, {"schema_version": 1, "mode": mode, "groups": groups,
                  "limitations": ["Centres alone cannot distinguish extra instances from splits.",
                                  "Repeated photographs are not independent; see physical_sets per group.",
                                  "Pooled grain scores and photo means can overweight repeated photographs; set-weighted errors are also reported.",
                                  "Bag/lot independence and label correctness are not established by this evaluator.",
                                  "Metrics with complete damage truth describe the visible surface only."]}


def main():
    """Write a fresh evaluation directory with per-photo and grouped results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--mode", choices=("crops", "full"), required=True)
    parser.add_argument("--output", type=Path, required=True, help="Fresh subdirectory under outputs/")
    args = parser.parse_args()
    output, output_root = args.output.resolve(), (ROOT / "outputs").resolve()
    if output == output_root or not output.is_relative_to(output_root) or output.exists():
        parser.error("Output must be a fresh subdirectory of outputs/")
    rows, summary = evaluate_manifest(args.manifest.resolve(), args.mode)
    output.mkdir(parents=True, exist_ok=False)
    with (output / "photos.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
