#!/usr/bin/env python3
"""Review Hole predictions on the fixed grouped validation images only."""

import argparse
import csv
import html
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import torch
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/soybean_hole"
THRESHOLDS = (0.05, 0.10, 0.20, 0.245, 0.40, 0.60)
MATCH_IOU = 0.5


def intersection_over_union(first, second):
    """Compute IoU for two xyxy boxes."""
    left, top = max(first[0], second[0]), max(first[1], second[1])
    right, bottom = min(first[2], second[2]), min(first[3], second[3])
    intersection = max(0, right - left) * max(0, bottom - top)
    first_area = max(0, first[2] - first[0]) * max(0, first[3] - first[1])
    second_area = max(0, second[2] - second[0]) * max(0, second[3] - second[1])
    union = first_area + second_area - intersection
    return intersection / union if union else 0.0


def match_boxes(ground_truth, predictions, threshold):
    """Match confidence-ordered predictions to the best unclaimed target at IoU 0.5."""
    available = set(range(len(ground_truth)))
    matches, unmatched_predictions = [], []
    for prediction in sorted(predictions, key=lambda item: -item["confidence"]):
        if prediction["confidence"] < threshold:
            continue
        candidates = [(intersection_over_union(prediction["box"], ground_truth[index]), index)
                      for index in sorted(available)]
        overlap, index = max(candidates, default=(0.0, -1))
        if overlap >= MATCH_IOU:
            matches.append((index, prediction, overlap))
            available.remove(index)
        else:
            unmatched_predictions.append(prediction)
    return matches, unmatched_predictions, sorted(available)


def load_ground_truth(path, width, height):
    """Read the prepared normalized Hole labels into pixel xyxy boxes."""
    boxes = []
    for line in path.read_text().splitlines():
        class_id, x, y, box_width, box_height = map(float, line.split())
        if class_id != 0:
            raise ValueError(f"Unexpected class in {path}")
        boxes.append([(x-box_width/2)*width, (y-box_height/2)*height,
                      (x+box_width/2)*width, (y+box_height/2)*height])
    return boxes


def summarize(records, threshold):
    """Count box matches and apparent errors against the existing labels."""
    counts = Counter()
    for record in records:
        matches, false_positives, false_negatives = match_boxes(record["truth"], record["predictions"], threshold)
        counts.update(images=1, positive_images=bool(record["truth"]), targets=len(record["truth"]),
                      matched=len(matches), apparent_fp=len(false_positives), apparent_fn=len(false_negatives))
    matched, false_positives, false_negatives = counts["matched"], counts["apparent_fp"], counts["apparent_fn"]
    return dict(counts) | {"confidence": threshold,
                           "precision": matched / (matched + false_positives) if matched + false_positives else None,
                           "recall": matched / (matched + false_negatives) if matched + false_negatives else None}


def make_thumbnail(record, output_path, threshold):
    """Draw green ground-truth boxes and red confidence-labelled predictions."""
    with Image.open(record["path"]) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=19)
    for box in record["truth"]:
        draw.rectangle(box, outline="lime", width=3)
    for prediction in record["predictions"]:
        if prediction["confidence"] >= threshold:
            box = prediction["box"]
            draw.rectangle(box, outline="red", width=3)
            label = f'{prediction["confidence"]:.2f}'
            label_x, label_y = box[0], max(0, box[1] - 22)
            bounds = draw.textbbox((label_x, label_y), label, font=font)
            draw.rectangle(bounds, fill="white")
            draw.text((label_x, label_y), label, fill="red", font=font)
    image.thumbnail((400, 400))
    image.save(output_path, quality=85)


def main():
    """Run reproducible validation-only inference and write metrics and an HTML review."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--review-confidence", type=float, default=0.10)
    args = parser.parse_args()
    if not 0.001 <= args.review_confidence <= 1:
        parser.error("review confidence must be between 0.001 and 1")
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"Output exists: {output}; choose a fresh directory")
    with (DATA / "selected_images.csv").open(newline="") as file:
        selected = sorted((row for row in csv.DictReader(file) if row["new_split"] == "val"), key=lambda row: row["image_v2"])
    if not selected or len({row["image_v2"] for row in selected}) != len(selected) or len({row["group"] for row in selected}) != len(selected):
        raise ValueError("Validation selection is empty, duplicated, or has duplicate groups")
    image_dir = DATA / "validation/images"
    label_dir = DATA / "validation/labels"
    paths = [image_dir / row["image_v2"] for row in selected]
    if {path.name for path in image_dir.glob("*.jpg")} != {path.name for path in paths}:
        raise ValueError("Validation images differ from the selected manifest")
    for row, path in zip(selected, paths):
        if not path.is_file() or not (label_dir / f"{path.stem}.txt").is_file():
            raise ValueError(f"Missing image or label: {row['image_v2']}")
    torch.set_num_threads(2)
    model = YOLO(str(args.weights.resolve()))
    # Same collection confidence and NMS IoU as the recorded validation run.
    results = model.predict(source=[str(path) for path in paths], conf=0.001, iou=0.7,
                            imgsz=640, batch=16, device=args.device, max_det=300, verbose=False, stream=True)
    records = []
    for row, path, result in zip(selected, paths, results, strict=True):
        if Path(result.path).name != path.name:
            raise ValueError(f"Prediction order mismatch: {path.name} / {result.path}")
        height, width = result.orig_shape
        truth = load_ground_truth(label_dir / f"{path.stem}.txt", width, height)
        if len(truth) != int(row["hole_boxes"]):
            raise ValueError(f"Manifest/label count mismatch: {path.name}")
        predictions = [{"box": box.tolist(), "confidence": float(confidence)}
                       for box, confidence, class_id in zip(result.boxes.xyxy.cpu().numpy(), result.boxes.conf.cpu().numpy(), result.boxes.cls.cpu().numpy())
                       if int(class_id) == 0]
        records.append({"image": path.name, "group": row["group"], "background": row["background"],
                        "path": path, "truth": truth, "predictions": predictions})
    output.mkdir(parents=True)
    (output / "images").mkdir()
    overall = [summarize(records, threshold) for threshold in THRESHOLDS]
    backgrounds = {background: summarize([record for record in records if record["background"] == background], args.review_confidence)
                   for background in sorted({record["background"] for record in records})}
    (output / "metrics.json").write_text(json.dumps({"weights": str(args.weights), "device": args.device, "matching_iou": MATCH_IOU,
        "review_confidence": args.review_confidence, "selection_sha256": hashlib.sha256((DATA / "selected_images.csv").read_bytes()).hexdigest(), "weights_sha256": hashlib.sha256(args.weights.read_bytes()).hexdigest(), "thresholds": overall, "backgrounds": backgrounds}, indent=2) + "\n")
    with (output / "predictions.jsonl").open("w") as file:
        for record in records:
            file.write(json.dumps({key: value for key, value in record.items() if key != "path"}) + "\n")
    errors = []
    for record in records:
        matches, false_positives, false_negatives = match_boxes(record["truth"], record["predictions"], args.review_confidence)
        if false_positives or false_negatives:
            errors.append((record, len(matches), len(false_positives), len(false_negatives)))
    with (output / "apparent_errors.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["image", "group", "background", "matched", "apparent_fp", "apparent_fn"])
        writer.writerows((r["image"], r["group"], r["background"], matched, fp, fn) for r, matched, fp, fn in errors)
    # Up to 12 of each type, sorted by filename; include overlaps only once.
    chosen = {entry[0]["image"]: entry for entry in ([e for e in errors if e[2]][:12] + [e for e in errors if e[3]][:12])}
    cards = []
    for record, matched, fp, fn in sorted(chosen.values(), key=lambda entry: entry[0]["image"]):
        image_name = Path(record["image"]).stem + ".jpg"
        make_thumbnail(record, output / "images" / image_name, args.review_confidence)
        image_id = html.escape(record["image"], quote=True)
        group = html.escape(record["group"], quote=True)
        cards.append(f'''<article data-key="{image_id}" data-group="{group}"><h3>{image_id}</h3><p>Group: {group} · background: {html.escape(record["background"])}<br>matched {matched} · apparent FP {fp} · apparent FN {fn}</p><img src="images/{image_name}" alt="Ground truth and predictions"><label>Assessment <select><option value="">Unreviewed</option><option>Model error</option><option>Likely annotation issue</option><option>Uncertain</option><option>Mixed issues</option></select></label><label>Notes <textarea rows="2"></textarea></label></article>''')
    text = '''<!doctype html><meta charset="utf-8"><title>Soybean validation review</title><style>body{font:15px system-ui;max-width:1300px;margin:auto;padding:1em}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1em}article{border:1px solid #aaa;padding:1em}img{width:100%;max-width:400px}label{display:block;margin-top:.5em}textarea{width:100%}</style><h1>Validation error review</h1><p>Green = annotated Hole; red = prediction with confidence. Apparent errors are unmatched at IoU ≥ 0.50 and confidence ≥ CONFIDENCE. Unmatched does not establish biological error: inspect labels and image. Shown: first 12 filenames with apparent false positives and first 12 with apparent false negatives, deduplicated. The CSV lists all apparent-error images. Assessments are per image, can be mixed, and stay in this browser until exported or cleared.</p><button id="export">Download assessments as CSV</button><section>CARDS</section><script>
const storageKey='soy-review:WEIGHT_HASH:'+location.pathname;
let saved={}; try { saved=JSON.parse(localStorage.getItem(storageKey)||'{}'); } catch(e) {}
const cards=[...document.querySelectorAll('article')];
for(const card of cards){const select=card.querySelector('select'), note=card.querySelector('textarea'), key=card.dataset.key; select.value=saved[key]?.assessment||''; note.value=saved[key]?.note||''; for(const el of [select,note]) el.addEventListener('input',()=>{saved[key]={assessment:select.value,note:note.value}; localStorage.setItem(storageKey,JSON.stringify(saved));});}
document.querySelector('#export').onclick=()=>{const quote=x=>'"'+String(x).replaceAll('"','""')+'"'; const rows=[['image','group','assessment','note'],...cards.map(c=>[c.dataset.key,c.dataset.group,c.querySelector('select').value,c.querySelector('textarea').value])]; const blob=new Blob([rows.map(r=>r.map(quote).join(',')).join('\\n')],{type:'text/csv'}); const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='soybean-review.csv';a.click();URL.revokeObjectURL(a.href);};
</script>'''.replace('CONFIDENCE', str(args.review_confidence)).replace('CARDS', '\n'.join(cards)).replace('WEIGHT_HASH', hashlib.sha256(args.weights.read_bytes()).hexdigest())
    (output / "review.html").write_text(text)
    print(json.dumps({"thresholds": overall, "backgrounds": backgrounds, "examples": len(chosen), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
