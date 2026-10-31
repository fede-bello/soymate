#!/usr/bin/env python3
"""Review Hole predictions on the fixed grouped validation images only."""

import argparse
import csv
import html
import hashlib
import json
import os
import random
from urllib.parse import quote
from collections import Counter
from pathlib import Path

from PIL import Image
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


def match_boxes(ground_truth, predictions, threshold, match_iou=MATCH_IOU):
    """Match confidence-ordered predictions to the best unclaimed target."""
    available = set(range(len(ground_truth)))
    matches, unmatched_predictions = [], []
    for prediction in sorted(predictions, key=lambda item: -item["confidence"]):
        if prediction["confidence"] < threshold:
            continue
        candidates = [(intersection_over_union(prediction["box"], ground_truth[index]), index)
                      for index in sorted(available)]
        overlap, index = max(candidates, default=(0.0, -1))
        if overlap >= match_iou:
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


def summarize(records, threshold, match_iou=MATCH_IOU):
    """Count box matches and apparent errors against the existing labels."""
    counts = Counter()
    for record in records:
        matches, false_positives, false_negatives = match_boxes(record["truth"], record["predictions"], threshold, match_iou)
        counts.update(images=1, positive_images=bool(record["truth"]), targets=len(record["truth"]),
                      matched=len(matches), apparent_fp=len(false_positives), apparent_fn=len(false_negatives))
    matched, false_positives, false_negatives = counts["matched"], counts["apparent_fp"], counts["apparent_fn"]
    return dict(counts) | {"confidence": threshold,
                           "precision": matched / (matched + false_positives) if matched + false_positives else None,
                           "recall": matched / (matched + false_negatives) if matched + false_negatives else None}


def write_gallery(records, args, output):
    """Build a self-contained viewer using the existing full-resolution images."""
    random_images = set(random.Random(args.seed).sample(
        [record["image"] for record in records], min(args.sample_size, len(records))))
    items = []
    for record in records:
        matches, unmatched, missed = match_boxes(
            record["truth"], record["predictions"], args.review_confidence, args.match_iou)
        match_by_prediction = {id(prediction): (index, overlap) for index, prediction, overlap in matches}
        predictions = []
        for index, prediction in enumerate(sorted(
                (prediction for prediction in record["predictions"]
                 if prediction["confidence"] >= args.review_confidence),
                key=lambda prediction: -prediction["confidence"]), 1):
            match = match_by_prediction.get(id(prediction))
            best_iou = max((intersection_over_union(prediction["box"], box)
                            for box in record["truth"]), default=None)
            predictions.append({"id": f"P{index}", "box": prediction["box"],
                                "confidence": prediction["confidence"],
                                "annotation": f"A{match[0] + 1}" if match else None,
                                "iou": match[1] if match else best_iou})
        items.append({"image": record["image"], "group": record["group"],
                      "background": record["background"], "width": record["width"],
                      "height": record["height"],
                      "src": quote(os.path.relpath(record["path"], output), safe="/"),
                      "annotations": [{"id": f"A{index + 1}", "box": box, "missed": index in missed}
                                      for index, box in enumerate(record["truth"])],
                      "predictions": predictions, "matches": len(matches),
                      "unmatched": len(unmatched), "missed": len(missed),
                      "random": record["image"] in random_images})
    settings = html.escape(
        f"Dataset: Mendeley d97rjyk2tz v2, grouped hole-only validation. Checkpoint: {args.weights}. "
        f"Confidence ≥ {args.review_confidence}; matching IoU ≥ {args.match_iou}. "
        f"Inference: 640 pixels, collection confidence 0.001, NMS IoU 0.7, max 300 detections, "
        f"batch 16, device {args.device}. Random sample: {min(args.sample_size, len(records))}, seed {args.seed}.")
    data = json.dumps(items, ensure_ascii=True).replace("<", "\\u003c")
    page = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SoyMate validation review</title><style>
body{font:16px system-ui;color:#20242c;max-width:1500px;margin:auto;padding:1rem}h1{margin-bottom:.3rem}h2{margin:.5rem 0}button,select,input,textarea{font:inherit}button,select,input{padding:.35rem}button{cursor:pointer}button:disabled{cursor:default} .legend{background:#f2f5f8;padding:.7rem 1rem;line-height:1.5} .controls{display:flex;gap:.7rem;flex-wrap:wrap;align-items:end;margin:1rem 0}.controls label,.review label{display:flex;flex-direction:column;gap:.2rem}.navigation{display:flex;align-items:center;gap:.7rem;flex-wrap:wrap}article{border:1px solid #aaa;border-radius:6px;padding:1rem;margin-top:1rem}.panels{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.panel{min-width:0}.panel h3{margin:.5rem 0}.viewport{overflow:auto;max-height:85vh;background:#eee}.picture{position:relative;line-height:0;width:100%}.picture img{display:block;width:100%;height:auto}.picture svg{position:absolute;inset:0;width:100%;height:100%}rect{fill:none;stroke-width:3;vector-effect:non-scaling-stroke}.annotation{stroke:#0767d1}.missed{stroke:#a000a0;stroke-dasharray:8 4}.matched{stroke:#00824b}.unmatched{stroke:#d05a00;stroke-dasharray:8 4}text{font:bold 18px sans-serif;paint-order:stroke;stroke:#111;stroke-width:4px;fill:white}table{border-collapse:collapse;width:100%;margin-top:.5rem}td,th{padding:.35rem;text-align:left;border-bottom:1px solid #ddd}.review{display:flex;gap:1rem;flex-wrap:wrap;margin-top:1rem}.review textarea{width:min(40rem,80vw)}.muted{color:#4c5260}.status{font-weight:600}details{margin:.7rem 0}#empty{padding:1rem} @media(max-width:760px){.panels{grid-template-columns:1fr}}
</style></head><body><h1>SoyMate validation review</h1>
<div class="legend"><strong>How to read the boxes:</strong> Left: blue solid = annotation with a matching prediction; purple dashed = missed annotation (no prediction matched it). Right: green solid = matched prediction; orange dashed = unmatched prediction. IDs connect boxes to the table. A match only means the boxes overlap enough under the rule below. An unmatched prediction may be a real hole missing from the labels, a duplicate, a bad prediction, or a localization mismatch. A missed annotation also needs human review. “No annotated hole” does not mean verified hole-free.</div>
<details><summary>Settings and limitations</summary><p>SETTINGS</p><p>Predictions are considered in descending confidence and matched one-to-one to the best still-unmatched annotation if IoU meets the threshold. The table shows matched IoU; for unmatched predictions it shows the best overlap with any annotation, even one already matched. This is a review rule and need not match Ultralytics evaluation. Fixed-confidence review counts are not the reported Ultralytics precision and recall at its validation-selected F1 operating point. Images with original filenames beginning “test” are in the new grouped validation split. Keep this file in its output directory so relative image links work.</p></details>
<div class="controls"><label>Filter<select id="filter"><option value="all">All images</option><option value="random">Random sample</option><option value="missed">Missed annotations</option><option value="unmatched">Unmatched predictions</option><option value="negative">No annotated hole, with predictions</option><option value="matched">Images with matches</option></select></label><label>Search filename or group<input id="search" type="search" placeholder="e.g. test_0013 or IMG_..."></label><button id="export">Export reviews as CSV</button></div>
<div class="navigation"><button id="previous">← Previous</button><button id="next">Next →</button><strong id="position"></strong><label>Zoom <select id="zoom"><option value="100">100%</option><option value="150">150%</option><option value="200">200%</option><option value="300">300%</option></select></label></div>
<p id="storage" class="muted"></p><div id="empty" hidden>No images match this filter and search.</div><article id="card" hidden><h2 id="name"></h2><p id="meta"></p><p id="summary" class="status"></p><div class="panels"><section class="panel"><h3>Dataset annotations</h3><div class="viewport"><div id="left" class="picture"></div></div></section><section class="panel"><h3>Model predictions</h3><div class="viewport"><div id="right" class="picture"></div></div></section></div><p><a id="original" target="_blank" rel="noopener">Open original image</a> · Zoom enlarges each panel; scroll within it to inspect detail.</p><details><summary>Box details and prediction confidence</summary><div id="box-details"></div></details><div class="review"><label>Status<select id="review-status"><option>Not reviewed</option><option>Looks correct</option><option>Possible annotation issue</option><option>Possible model issue</option><option>Uncertain</option></select></label><label>Notes<textarea id="notes" rows="3" placeholder="Your observations"></textarea></label></div></article>
<script>
const items=DATA;
const $=id=>document.getElementById(id), filter=$('filter'), search=$('search');
let current=0, visible=[], reviews={}, storageOK=false;
const storageKey='soymate-review-v2:'+location.pathname;
try{let saved=localStorage.getItem(storageKey); reviews=saved?JSON.parse(saved):{}; localStorage.setItem(storageKey,JSON.stringify(reviews)); storageOK=true;}catch(error){reviews={};}
function storageMessage(){ $('storage').textContent=storageOK?'Reviews save in this browser for this local gallery. Export CSV for a portable backup; clearing browser data can remove them.':'Browser storage is unavailable: reviews last only while this page is open. Export CSV before closing.'; }
storageMessage();
function esc(value){return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function noun(n,one,many){return n+' '+(n===1?one:many);}
function applyFilter(){const query=search.value.trim().toLowerCase(), f=filter.value; visible=items.filter(item=>{const category=f==='all'||(f==='random'&&item.random)||(f==='missed'&&item.missed)||(f==='unmatched'&&item.unmatched)||(f==='negative'&&!item.annotations.length&&item.predictions.length)||(f==='matched'&&item.matches); return category&&(item.image+' '+item.group).toLowerCase().includes(query);}); current=0; render();}
function boxSvg(box,kind){const [x1,y1,x2,y2]=box.box; return `<g><rect class="${kind}" x="${x1}" y="${y1}" width="${x2-x1}" height="${y2-y1}"/><text x="${x1}" y="${Math.max(18,y1-4)}">${box.id}</text></g>`;}
function panel(item,boxes,side){const shapes=boxes.map(box=>boxSvg(box,side==='left'?(box.missed?'missed':'annotation'):(box.annotation?'matched':'unmatched'))).join(''); return `<img src="${esc(item.src)}" alt="${esc(item.image)}"><svg viewBox="0 0 ${item.width} ${item.height}" aria-label="${side==='left'?'Annotation':'Prediction'} boxes">${shapes}</svg>`;}
function render(){const item=visible[current], label=filter.options[filter.selectedIndex].text; $('position').textContent=label+' · '+visible.length+' matching images'+(item?' · '+(current+1)+' of '+visible.length:''); $('previous').disabled=!item||current===0; $('next').disabled=!item||current===visible.length-1; $('card').hidden=!item; $('empty').hidden=!!item; if(!item)return;
 $('name').textContent=item.image; $('meta').textContent='Validation · group '+item.group+' · background '+item.background; $('summary').textContent=[noun(item.annotations.length,'annotated hole','annotated holes'),noun(item.predictions.length,'prediction','predictions'),noun(item.matches,'match','matches'),noun(item.unmatched,'unmatched prediction','unmatched predictions'),noun(item.missed,'missed annotation','missed annotations')].join(' · ');
 $('left').innerHTML=panel(item,item.annotations,'left'); $('right').innerHTML=panel(item,item.predictions,'right'); $('original').href=item.src; setZoom();
 const annotationRows=item.annotations.map(a=>`<tr><td>${a.id}</td><td>${a.missed?'Missed annotation':'Matched annotation'}</td></tr>`).join('');
 const predictionRows=item.predictions.map(p=>`<tr><td>${p.id}</td><td>${p.confidence.toFixed(3)}</td><td>${p.annotation?'Matched to '+p.annotation:'Unmatched'}</td><td>${p.iou===null?'—':p.iou.toFixed(3)+(p.annotation?'':' (best overlap)')}</td></tr>`).join('');
 $('box-details').innerHTML='<h3>Annotations</h3>'+(annotationRows?'<table><tr><th>ID</th><th>Status</th></tr>'+annotationRows+'</table>':'No annotated hole.')+'<h3>Predictions</h3>'+(predictionRows?'<table><tr><th>ID</th><th>Confidence</th><th>Match</th><th>IoU</th></tr>'+predictionRows+'</table>':'No predictions at the selected confidence.');
 const review=reviews[item.image]||{}; $('review-status').value=review.status||'Not reviewed'; $('notes').value=review.notes||'';
}
function setZoom(){for(const id of ['left','right']) $(id).style.width=$('zoom').value+'%';}
function save(){if(!visible[current])return; reviews[visible[current].image]={status:$('review-status').value,notes:$('notes').value}; if(storageOK){try{localStorage.setItem(storageKey,JSON.stringify(reviews));}catch(error){storageOK=false;storageMessage();}}}
filter.addEventListener('change',applyFilter); search.addEventListener('input',applyFilter); $('previous').onclick=()=>{current--;render();}; $('next').onclick=()=>{current++;render();}; $('zoom').onchange=setZoom; $('review-status').onchange=save; $('notes').oninput=save;
$('export').onclick=()=>{const quote=value=>'"'+String(value).replaceAll('"','""')+'"'; const rows=[['image_id','group','status','notes'],...items.filter(item=>reviews[item.image]).map(item=>[item.image,item.group,reviews[item.image].status,reviews[item.image].notes])]; const blob=new Blob([rows.map(row=>row.map(quote).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}); const link=document.createElement('a'); link.href=URL.createObjectURL(blob);link.download='soymate-reviews.csv';link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);};
applyFilter();
</script></body></html>'''.replace("SETTINGS", settings).replace("DATA", data)
    (output / "review.html").write_text(page)


def main():
    """Run reproducible validation-only inference and write metrics and an HTML review."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--review-confidence", type=float, default=0.10)
    parser.add_argument("--match-iou", type=float, default=0.5)
    parser.add_argument("--sample-size", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, help="Only process the first N validation images for a smoke check")
    parser.add_argument("--predictions", type=Path, help="Reuse predictions.jsonl with its adjacent metrics.json")
    parser.add_argument("--refresh", action="store_true", help="Refresh an existing gallery in place using cached predictions")
    args = parser.parse_args()
    if not 0.001 <= args.review_confidence <= 1:
        parser.error("review confidence must be between 0.001 and 1")
    if not 0 < args.match_iou <= 1 or args.sample_size < 0 or (args.limit is not None and args.limit < 1):
        parser.error("match IoU must be in (0, 1], sample size nonnegative, and limit positive")
    output = args.output.resolve()
    if output.exists():
        expected_files = {"review.html", "metrics.json", "predictions.jsonl", "apparent_errors.csv"}
        if not args.refresh or not args.predictions or not output.is_dir() or {path.name for path in output.iterdir()} != expected_files:
            raise SystemExit(f"Output exists: {output}; choose a fresh directory or refresh an unmodified gallery with --refresh and --predictions")
        previous = json.loads((output / "metrics.json").read_text())
        if previous.get("split") != "validation" or previous.get("weights_sha256") != hashlib.sha256(args.weights.read_bytes()).hexdigest():
            raise SystemExit("Existing gallery metadata does not match the checkpoint")
        if args.predictions.resolve().parent == output:
            raise SystemExit("Cached predictions must be outside the gallery being refreshed")
    elif args.refresh:
        parser.error("--refresh requires an existing gallery")
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
    if args.limit is not None:
        selected, paths = selected[:args.limit], paths[:args.limit]
    records = []
    if args.predictions:
        source_metrics = json.loads((args.predictions.parent / "metrics.json").read_text())
        if source_metrics.get("split") != "validation" or source_metrics.get("selection_sha256") != hashlib.sha256((DATA / "selected_images.csv").read_bytes()).hexdigest() or source_metrics.get("weights_sha256") != hashlib.sha256(args.weights.read_bytes()).hexdigest():
            raise ValueError("Cached prediction metadata does not match the validation manifest and checkpoint")
        if any(source_metrics.get(key) != value for key, value in {"collection_confidence": 0.001, "nms_iou": 0.7, "imgsz": 640, "batch": 16, "max_det": 300}.items()):
            raise ValueError("Cached inference settings differ from those supported by this review")
        if args.review_confidence < source_metrics["collection_confidence"]:
            raise ValueError("Review confidence is below the cached prediction collection confidence")
        cached = [json.loads(line) for line in args.predictions.read_text().splitlines()]
        if args.limit is not None:
            cached = cached[:args.limit]
        for row, path, record in zip(selected, paths, cached, strict=True):
            with Image.open(path) as image:
                size = image.size
            if (record["image"] != path.name or record["group"] != row["group"] or
                    (record["width"], record["height"]) != size or
                    record["truth"] != load_ground_truth(label_dir / f"{path.stem}.txt", *size)):
                raise ValueError(f"Cached image, group, dimensions or labels differ: {path.name}")
            records.append(record | {"path": path})
        args.device = source_metrics["device"]
    else:
        torch.set_num_threads(2)
        model = YOLO(str(args.weights.resolve()))
        results = model.predict(source=[str(path) for path in paths], conf=0.001, iou=0.7,
                                imgsz=640, batch=16, device=args.device, max_det=300, verbose=False, stream=True)
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
                            "path": path, "width": width, "height": height, "truth": truth, "predictions": predictions})
    output.mkdir(parents=True, exist_ok=args.refresh)
    overall = [summarize(records, threshold, args.match_iou) for threshold in sorted(set(THRESHOLDS + (args.review_confidence,)))]
    backgrounds = {background: summarize([record for record in records if record["background"] == background], args.review_confidence, args.match_iou)
                   for background in sorted({record["background"] for record in records})}
    (output / "metrics.json").write_text(json.dumps({"weights": str(args.weights), "dataset": "Mendeley d97rjyk2tz v2, grouped hole-only selection", "split": "validation", "device": args.device, "matching_iou": args.match_iou,
        "review_confidence": args.review_confidence, "collection_confidence": 0.001, "nms_iou": 0.7, "imgsz": 640, "batch": 16, "max_det": 300, "sample_size": args.sample_size, "seed": args.seed, "limit": args.limit, "prediction_source": str(args.predictions) if args.predictions else "new inference", "prediction_source_sha256": hashlib.sha256(args.predictions.read_bytes()).hexdigest() if args.predictions else None, "selection_sha256": hashlib.sha256((DATA / "selected_images.csv").read_bytes()).hexdigest(), "weights_sha256": hashlib.sha256(args.weights.read_bytes()).hexdigest(), "thresholds": overall, "backgrounds": backgrounds}, indent=2) + "\n")
    with (output / "predictions.jsonl").open("w") as file:
        for record in records:
            file.write(json.dumps({key: value for key, value in record.items() if key != "path"}) + "\n")
    errors = []
    for record in records:
        matches, false_positives, false_negatives = match_boxes(record["truth"], record["predictions"], args.review_confidence, args.match_iou)
        if false_positives or false_negatives:
            errors.append((record, len(matches), len(false_positives), len(false_negatives)))
    with (output / "apparent_errors.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["image", "group", "background", "matched", "apparent_fp", "apparent_fn"])
        writer.writerows((r["image"], r["group"], r["background"], matched, fp, fn) for r, matched, fp, fn in errors)
    write_gallery(records, args, output)
    print(json.dumps({"thresholds": overall, "backgrounds": backgrounds, "images": len(records), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
