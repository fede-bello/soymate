"""Segment separated grains and associate visible-hole detector predictions."""

import csv
import hashlib
import html
import json
import math
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps


REVIEW_THRESHOLDS = (0.10, 0.20, 0.40, 0.60)


def sha256_file(path):
    """Hash a file without loading its contents into memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_upright_image(path):
    """Read the full-resolution image with its EXIF orientation applied."""
    with Image.open(path) as image:
        return np.asarray(ImageOps.exif_transpose(image).convert("RGB"))


def segment_grains(image, min_area, border_fraction, distance_threshold=None):
    """Find filled foreground components using distance from border colour.

    Pixels are compared in OpenCV's 8-bit Lab space. The returned label map
    contains accepted components only; rejected components are recorded as well.
    """
    height, width = image.shape[:2]
    border = max(1, min(round(min(height, width) * border_fraction), min(height, width) // 2))
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    border_pixels = np.concatenate((lab[:border].reshape(-1, 3), lab[-border:].reshape(-1, 3),
                                    lab[border:-border, :border].reshape(-1, 3),
                                    lab[border:-border, -border:].reshape(-1, 3)))
    background = np.median(border_pixels, axis=0)
    distance = np.linalg.norm(lab.astype(np.float32) - background, axis=2)
    distance_image = np.clip(distance, 0, 255).astype(np.uint8)
    if distance_threshold is None:
        threshold, foreground = cv2.threshold(distance_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    else:
        threshold, foreground = cv2.threshold(distance_image, distance_threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda contour: (cv2.boundingRect(contour)[1], cv2.boundingRect(contour)[0]))
    labels = np.zeros((height, width), dtype=np.uint16)
    filled_foreground = np.zeros((height, width), dtype=np.uint8)
    components, excluded = [], []
    for contour in contours:
        x, y, component_width, component_height = cv2.boundingRect(contour)
        local_contour = contour - np.array([[[x, y]]], dtype=contour.dtype)
        local_mask = np.zeros((component_height, component_width), dtype=np.uint8)
        cv2.drawContours(local_mask, [local_contour], -1, 255, cv2.FILLED)
        area = int(cv2.countNonZero(local_mask))
        filled_foreground[y:y + component_height, x:x + component_width] |= local_mask
        boundary = x == 0 or y == 0 or x + component_width == width or y + component_height == height
        reason = "below_min_area" if area < min_area else "image_boundary" if boundary else None
        record = {"bbox": [x, y, x + component_width, y + component_height], "area": area}
        if reason:
            excluded.append(record | {"reason": reason})
            continue
        if len(components) >= 65534:
            raise ValueError("More than 65534 accepted components; increase minimum area")
        identifier = len(components) + 1
        region = labels[y:y + component_height, x:x + component_width]
        region[local_mask != 0] = identifier
        moments = cv2.moments(local_mask, binaryImage=True)
        centre = [x + moments["m10"] / moments["m00"], y + moments["m01"] / moments["m00"]]
        components.append(record | {"id": identifier, "centroid": centre})
    return labels, foreground, filled_foreground, components, excluded, {
        "background_lab": background.tolist(), "border_pixels": border,
        "distance_threshold": float(threshold), "min_area_pixels": min_area,
    }


def make_crop(image, bbox, background_rgb, padding_factor=1.5):
    """Make a square crop, padding off-image pixels and returning its origin."""
    x1, y1, x2, y2 = bbox
    side = max(1, math.ceil(max(x2 - x1, y2 - y1) * padding_factor))
    origin_x = math.floor((x1 + x2 - side) / 2)
    origin_y = math.floor((y1 + y2 - side) / 2)
    height, width = image.shape[:2]
    left, top = max(0, origin_x), max(0, origin_y)
    right, bottom = min(width, origin_x + side), min(height, origin_y + side)
    crop = np.empty((side, side, 3), dtype=np.uint8)
    crop[:] = background_rgb
    if right > left and bottom > top:
        crop[top - origin_y:bottom - origin_y, left - origin_x:right - origin_x] = image[top:bottom, left:right]
    return crop, [origin_x, origin_y]


def map_and_associate(predictions, origin, labels, target_id=None):
    """Map crop-space boxes and assign centres to a single source instance."""
    height, width = labels.shape
    results = []
    for prediction in predictions:
        box = [float(prediction["box"][0] + origin[0]), float(prediction["box"][1] + origin[1]),
               float(prediction["box"][2] + origin[0]), float(prediction["box"][3] + origin[1])]
        centre_x, centre_y = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        instance_id = 0
        if not (0 <= centre_x < width and 0 <= centre_y < height):
            reason = "centre_outside_image"
        else:
            instance_id = int(labels[int(centre_y), int(centre_x)])
            if not instance_id:
                reason = "centre_outside_accepted_instance"
            elif target_id is not None and instance_id != target_id:
                reason = "different_crop_instance"
            else:
                reason = None
        clipped = [max(0.0, min(width, box[0])), max(0.0, min(height, box[1])),
                   max(0.0, min(width, box[2])), max(0.0, min(height, box[3]))]
        results.append({"box": clipped, "unclipped_box": box, "confidence": float(prediction["confidence"]),
                        "instance_id": instance_id if reason is None else None,
                        "centre_instance_id": instance_id or None, "crop_instance_id": target_id,
                        "rejection_reason": reason})
    return results


def summarize_predictions(components, detections, threshold):
    """Count unique accepted instances with at least one high-confidence box."""
    flagged = {item["instance_id"] for item in detections
               if item["instance_id"] is not None and item["confidence"] >= threshold}
    total = len(components)
    return {"grain_candidates": total, "flagged_grains": len(flagged),
            "flagged_percentage": 100 * len(flagged) / total if total else None,
            "flagged_ids": sorted(flagged)}


class YoloDetector:
    """Load the local YOLO checkpoint once and return source-coordinate boxes."""

    def __init__(self, weights, device, batch_size):
        from ultralytics import YOLO
        self.model = YOLO(str(weights))
        if self.model.names != {0: "Hole"}:
            raise ValueError(f"Expected a single Hole class, got {self.model.names}")
        self.device = device
        self.batch_size = batch_size

    def predict(self, images):
        """Run bounded batches, returning xyxy boxes for each supplied RGB image."""
        predictions = []
        for start in range(0, len(images), self.batch_size):
            batch = images[start:start + self.batch_size]
            # Ultralytics interprets NumPy inputs as BGR.
            bgr_batch = [cv2.cvtColor(image, cv2.COLOR_RGB2BGR) for image in batch]
            results = self.model.predict(source=bgr_batch, conf=0.05, iou=0.7, imgsz=640,
                                         max_det=300, device=self.device, verbose=False)
            if len(results) != len(batch):
                raise RuntimeError("Detector returned a different number of images")
            for result in results:
                predictions.append([{"box": box.tolist(), "confidence": float(confidence)}
                                    for box, confidence, class_id in zip(result.boxes.xyxy.cpu().numpy(),
                                        result.boxes.conf.cpu().numpy(), result.boxes.cls.cpu().numpy(), strict=True)
                                    if int(class_id) == 0])
        return predictions


def render_report(output, summary, images):
    """Write a standalone local HTML report referencing assets in the run."""
    image_sections = "".join(f'<section><h2>{html.escape(title)}</h2><a href="{html.escape(path)}">'
                             f'<img src="{html.escape(path)}" alt="{html.escape(title)}"></a></section>'
                             for title, path in images)
    rows = "".join(f'<tr><td>{html.escape(mode)}</td><td>{item["grain_candidates"]}</td>'
                   f'<td>{item["flagged_grains"]}</td><td>'
                   f'{item["flagged_percentage"]:.2f}%</td></tr>' if item["flagged_percentage"] is not None
                   else f'<tr><td>{html.escape(mode)}</td><td>0</td><td>0</td><td>—</td></tr>'
                   for mode, item in summary["results"].items())
    threshold_rows = "".join(
        f'<tr><td>{html.escape(mode)}</td><td>{html.escape(threshold)}</td><td>{counts["flagged_grains"]}</td></tr>'
        for mode, item in summary["results"].items() for threshold, counts in item["threshold_comparison"].items())
    grain_links = ", ".join(f'<a href="grains_{html.escape(mode)}.csv">{html.escape(mode)} per-grain CSV</a>'
                            for mode in summary["results"])
    content = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>SoyMate sample review</title><style>body{{font:16px system-ui;max-width:1100px;margin:auto;padding:1rem;color:#243323}}
img{{max-width:100%;height:auto}}section{{margin:2rem 0}}table{{border-collapse:collapse}}td,th{{border:1px solid #bbb;padding:.45rem}}
.notice{{background:#fff4cf;padding:1rem}}code{{overflow-wrap:anywhere}}</style></head><body>
<h1>SoyMate sample review</h1><p class="notice">Experimental visible-hole candidates; inspect every instance.
Touching grains can merge. The percentage applies only to accepted grain candidates and is not a lot assessment.</p>
<p>Species: {html.escape(summary['metadata']['species'])}; provenance: {html.escape(summary['metadata']['provenance'])};
flagging threshold: {summary['configuration']['flag_confidence']:.2f}; device: {html.escape(summary['device'])}.</p>
<p>Excluded components: {len(summary['excluded_components'])}. Detection boxes: green = flagged,
yellow = review candidate, red = unassigned/rejected. Candidate scores are not calibrated probabilities.</p>
<table><tr><th>Mode</th><th>Grain candidates</th><th>Flagged grains</th><th>Flagged percentage</th></tr>{rows}</table>
<p>Download <a href="sample.json">sample JSON</a>, {grain_links}.</p>
<h2>Threshold comparison</h2><table><tr><th>Mode</th><th>Confidence</th><th>Flagged grains</th></tr>{threshold_rows}</table>
{image_sections}</body></html>'''
    (output / "report.html").write_text(content, encoding="utf-8")


def _draw_overlay(image, labels, components, excluded, detections=None, flag_confidence=0.4, review_confidence=0.1):
    """Draw numbered components and optional detection boxes over the image."""
    canvas = Image.fromarray(image.copy())
    draw = ImageDraw.Draw(canvas)
    for component in components:
        identifier = component["id"]
        x1, y1, x2, y2 = component["bbox"]
        region = (labels[y1:y2, x1:x2] == identifier).astype(np.uint8)
        contours, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            points = [(int(point[0][0] + x1), int(point[0][1] + y1)) for point in contour]
            if len(points) > 1:
                draw.line(points + [points[0]], fill="cyan", width=2)
        draw.text((x1, y1), str(identifier), fill="cyan", stroke_width=1, stroke_fill="black")
    for component in excluded:
        draw.rectangle(component["bbox"], outline="magenta", width=2)
    for detection in detections or []:
        if detection["confidence"] < review_confidence:
            continue
        colour = "red" if detection["rejection_reason"] else "lime" if detection["confidence"] >= flag_confidence else "yellow"
        draw.rectangle(detection["box"], outline=colour, width=2)
        draw.text((detection["box"][0], detection["box"][1]), f'{detection["confidence"]:.2f}',
                  fill=colour, stroke_width=1, stroke_fill="black")
    return canvas


def run_analysis(image, detector, output, configuration, metadata, input_path, weights_path, device):
    """Run all requested stages and write reproducible local artifacts."""
    start = time.perf_counter()
    height, width = image.shape[:2]
    minimum_area = max(1, round(configuration["min_area_fraction"] * width * height))
    labels, foreground, filled, components, excluded, segmentation = segment_grains(
        image, minimum_area, configuration["border_fraction"], configuration["distance_threshold"])
    segmentation_seconds = time.perf_counter() - start
    Image.fromarray(image).save(output / "input.png")
    Image.fromarray(foreground).save(output / "foreground.png")
    Image.fromarray(filled).save(output / "filled_foreground.png")
    Image.fromarray(labels).save(output / "instances.png")
    _draw_overlay(image, labels, components, excluded).save(output / "instances_overlay.png")
    # Use the same border pixels' median RGB for padding, without altering crops.
    border = segmentation["border_pixels"]
    border_rgb = np.concatenate((image[:border].reshape(-1, 3), image[-border:].reshape(-1, 3),
                                 image[border:-border, :border].reshape(-1, 3), image[border:-border, -border:].reshape(-1, 3)))
    background_rgb = np.median(border_rgb, axis=0).astype(np.uint8)
    crops, crop_origins = [], []
    for component in components:
        crop, origin = make_crop(image, component["bbox"], background_rgb, configuration["crop_padding"])
        crops.append(crop)
        crop_origins.append(origin)
        component["crop_origin"] = origin
        component["crop_size"] = [crop.shape[1], crop.shape[0]]
    thumb_size, columns = 160, 6
    contact = Image.new("RGB", (thumb_size * columns, max(1, math.ceil(len(crops) / columns)) * (thumb_size + 24)), "white")
    contact_draw = ImageDraw.Draw(contact)
    if not crops:
        contact_draw.text((5, 5), "No accepted grain crops", fill="black")
    for index, crop in enumerate(crops):
        thumb = Image.fromarray(crop)
        thumb.thumbnail((thumb_size, thumb_size))
        x, y = (index % columns) * thumb_size, (index // columns) * (thumb_size + 24)
        contact.paste(thumb, (x, y))
        contact_draw.text((x + 2, y + thumb_size), f'Grain {components[index]["id"]}', fill="black")
    contact.save(output / "crops.png")
    inference_start = time.perf_counter()
    all_detections = {}
    if configuration["mode"] in ("crops", "compare"):
        batches = detector.predict(crops) if crops else []
        if len(batches) != len(crops):
            raise ValueError("Detector returned an unexpected number of crop results")
        all_detections["crops"] = [detection for component, origin, predictions in zip(components, crop_origins, batches, strict=True)
                                   for detection in map_and_associate(predictions, origin, labels, component["id"])]
    if configuration["mode"] in ("full", "compare"):
        batches = detector.predict([image])
        if len(batches) != 1:
            raise ValueError("Detector returned an unexpected number of full-image results")
        all_detections["full"] = map_and_associate(batches[0], [0, 0], labels)
    inference_seconds = time.perf_counter() - inference_start
    results, report_images = {}, [("Upright input", "input.png"), ("Raw foreground", "foreground.png"),
                                  ("Filled silhouettes", "filled_foreground.png"),
                                  ("Numbered instances and excluded components (magenta)", "instances_overlay.png"),
                                  ("Crops", "crops.png")]
    for mode, detections in all_detections.items():
        results[mode] = summarize_predictions(components, detections, configuration["flag_confidence"])
        results[mode]["threshold_comparison"] = {
            str(threshold): summarize_predictions(components, detections, threshold) for threshold in REVIEW_THRESHOLDS}
        overlay_name = f"detections_{mode}.png"
        _draw_overlay(image, labels, components, excluded, detections,
                      configuration["flag_confidence"], configuration["review_confidence"]).save(output / overlay_name)
        report_images.append((f"{mode.title()} detections", overlay_name))
        with (output / f"grains_{mode}.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["id", "bbox", "centroid", "area", "status", "accepted_boxes", "max_confidence"])
            writer.writeheader()
            for component in components:
                associated = [item for item in detections if item["instance_id"] == component["id"]]
                matches = [item for item in associated if item["confidence"] >= configuration["flag_confidence"]]
                writer.writerow({key: component[key] for key in ("id", "bbox", "centroid", "area")} | {
                    "status": "hole candidate" if matches else "no hole detected", "accepted_boxes": len(matches),
                    "max_confidence": max((item["confidence"] for item in associated), default="")})
    summary = {"schema_version": 1, "input": {"path": str(input_path), "sha256": sha256_file(input_path),
               "width": width, "height": height, "orientation": "EXIF-upright"},
               "checkpoint": {"path": str(weights_path), "sha256": sha256_file(weights_path)},
               "metadata": metadata, "configuration": configuration, "segmentation": segmentation,
               "components": components, "excluded_components": excluded, "detections": all_detections,
               "results": results, "device": device,
               "timings_seconds": {"segmentation": segmentation_seconds, "inference": inference_seconds},
               "limitations": ["Separated grains on a uniform contrasting background only.",
                               "Counts and visible-hole candidates require human inspection.",
                               "Flagged percentage describes accepted candidates, not hidden infestation or lot suitability."]}
    render_report(output, summary, report_images)
    summary["timings_seconds"]["total"] = time.perf_counter() - start
    (output / "sample.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return summary
