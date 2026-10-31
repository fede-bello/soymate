#!/usr/bin/env python3
"""Build the audited grouped, hole-only YOLO dataset without changing raw data."""

import csv
import math
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/Soybean_Seed_Dataset"
MANIFEST = ROOT / "research/soybean_bruchid/resplit_by_original.csv"
OUTPUT = ROOT / "data/processed/soybean_hole"
SPLITS = {"train": "train", "val": "validation", "test": "test"}
PUBLISHED = {"train", "validation", "test"}


def read_labels(path, names, hole_id):
    """Validate every YOLO annotation and return remapped Hole lines."""
    if not path.is_file():
        raise ValueError(f"Missing label file: {path}")
    holes = []
    lines = path.read_text().splitlines()
    for number, line in enumerate(lines, 1):
        fields = line.split()
        try:
            if len(fields) != 5:
                raise ValueError("expected class and four coordinates")
            class_id = int(fields[0])
            x, y, width, height = map(float, fields[1:])
            if class_id not in names or not all(math.isfinite(v) for v in (x, y, width, height)):
                raise ValueError("unknown class or non-finite coordinate")
            if not (0 < width <= 1 and 0 < height <= 1 and 0 <= x <= 1 and 0 <= y <= 1
                    and x - width / 2 >= -1e-6 and x + width / 2 <= 1 + 1e-6
                    and y - height / 2 >= -1e-6 and y + height / 2 <= 1 + 1e-6):
                raise ValueError("out-of-bounds box")
        except ValueError as error:
            raise ValueError(f"{path}:{number}: {error}") from error
        if class_id == hole_id:
            holes.append("0 " + " ".join(fields[1:]))
    return lines, holes


def main():
    """Validate source and manifest, then write a fresh derived dataset."""
    if OUTPUT.exists():
        raise SystemExit(f"Output already exists: {OUTPUT}. Move it aside before rebuilding.")
    config = yaml.safe_load((RAW / "data.yaml").read_text())
    names = {int(key): value for key, value in config["names"].items()}
    hole_ids = [key for key, value in names.items() if value.lower() == "hole"]
    if len(hole_ids) != 1:
        raise ValueError("Expected exactly one Hole class in data.yaml")
    with MANIFEST.open(newline="") as file:
        reader = csv.DictReader(file)
        required = {"image_v2", "original_split", "group", "new_split", "discard", "n_labels"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Manifest is missing required columns")
        rows = list(reader)
    image_paths = defaultdict(list)
    for published_split in sorted(PUBLISHED):
        for image in (RAW / published_split / "images").glob("*.jpg"):
            image_paths[image.name].append((published_split, image))
    names_seen = Counter(row["image_v2"] for row in rows)
    duplicates = [name for name, count in names_seen.items() if count != 1]
    if duplicates or set(names_seen) != set(image_paths):
        raise ValueError(f"Manifest/image coverage mismatch or duplicate manifest names: {duplicates[:5]}; "
                         f"missing={sorted(set(names_seen) - set(image_paths))[:5]}, "
                         f"unlisted={sorted(set(image_paths) - set(names_seen))[:5]}")
    groups = defaultdict(set)
    retained = []
    for row in rows:
        name = row["image_v2"]
        if len(image_paths[name]) != 1 or image_paths[name][0][0] != row["original_split"]:
            raise ValueError(f"Ambiguous image or published split mismatch: {name}")
        if row["discard"]:
            if row["new_split"]:
                raise ValueError(f"Discarded image has a new split: {name}")
            continue
        if not row["group"] or row["new_split"] not in SPLITS:
            raise ValueError(f"Missing group or invalid split: {name}")
        groups[row["group"]].add(row["new_split"])
        image = image_paths[name][0][1]
        label = RAW / row["original_split"] / "labels" / f"{image.stem}.txt"
        lines, holes = read_labels(label, names, hole_ids[0])
        if str(len(lines)) != row["n_labels"]:
            raise ValueError(f"Manifest label count mismatch: {name}")
        retained.append((row, image, holes))
    crossing = [group for group, splits in groups.items() if len(splits) != 1]
    if crossing:
        raise ValueError(f"Groups cross splits: {crossing[:10]}")
    # The v2 filename does not identify the unaugmented image. Choose the
    # lexicographically smallest retained v2 filename in each evaluation group.
    selected, seen_eval_groups = [], set()
    for row, image, holes in sorted(retained, key=lambda item: item[0]["image_v2"]):
        if row["new_split"] != "train":
            if row["group"] in seen_eval_groups:
                continue
            seen_eval_groups.add(row["group"])
        selected.append((row, image, holes))
    OUTPUT.mkdir(parents=True)
    counts = defaultdict(lambda: {"images": 0, "groups": set(), "hole_boxes": 0, "candidate_negatives": 0})
    with (OUTPUT / "selected_images.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["image_v2", "original_split", "group", "new_split", "hole_boxes", "background", "type"])
        writer.writeheader()
        for row, image, holes in selected:
            split = SPLITS[row["new_split"]]
            image_dir, label_dir = OUTPUT / split / "images", OUTPUT / split / "labels"
            image_dir.mkdir(parents=True, exist_ok=True)
            label_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(image, image_dir / image.name)
            (label_dir / f"{image.stem}.txt").write_text("".join(line + "\n" for line in holes))
            writer.writerow({key: row[key] for key in ("image_v2", "original_split", "group", "new_split", "background", "type")} | {"hole_boxes": len(holes)})
            count = counts[split]
            count["images"] += 1
            count["groups"].add(row["group"])
            count["hole_boxes"] += len(holes)
            count["candidate_negatives"] += not holes
    summary = {split: {**counts[split], "groups": len(counts[split]["groups"])} for split in SPLITS.values()}
    (OUTPUT / "counts.yaml").write_text(yaml.safe_dump(summary, sort_keys=False))
    (OUTPUT / "data.yaml").write_text(yaml.safe_dump({"path": str(OUTPUT), "train": "train/images", "val": "validation/images", "test": "test/images", "names": {0: "Hole"}}, sort_keys=False))
    examples = [(row, image, holes) for row, image, holes in selected if row["new_split"] == "train" and holes][:6]
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    for axis, (row, image, holes) in zip(axes.flat, examples):
        with Image.open(image) as picture:
            axis.imshow(picture.convert("RGB"))
            width, height = picture.size
        for line in holes:
            _, x, y, box_width, box_height = map(float, line.split())
            axis.add_patch(Rectangle(((x-box_width/2)*width, (y-box_height/2)*height), box_width*width, box_height*height, fill=False, edgecolor="lime", linewidth=1.5))
        axis.set_title(row["image_v2"])
        axis.axis("off")
    fig.tight_layout()
    fig.savefig(OUTPUT / "prepared_examples.png", dpi=120)
    plt.close(fig)
    print(yaml.safe_dump(summary, sort_keys=False))
    print(f"Dataset written to {OUTPUT}. Empty Hole labels are candidate negatives, not confirmed hole-free.")


if __name__ == "__main__":
    main()
