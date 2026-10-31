"""Run a frozen FastSAM-small comparison against full-resolution pea polygons."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from ultralytics import FastSAM

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from grain_pipeline import load_upright_image, make_crop


def main():
    """Generate automatic masks, evaluate one-to-one IoU, and save review artifacts."""
    parser = argparse.ArgumentParser()
    parser.add_argument('stem')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = ROOT / 'data/raw/pea_zenodo_21110940'
    image = load_upright_image(data / 'images' / f'{args.stem}.jpg')
    height, width = image.shape[:2]
    shapes = json.loads((data / 'annotations' / f'{args.stem}.json').read_text())['shapes']
    ground_truth = np.zeros((height, width), np.int32)
    for index, shape in enumerate(shapes, 1):
        cv2.fillPoly(ground_truth, [np.rint(shape['points']).astype(np.int32)], index)
    weights = ROOT / 'outputs/multigrain-experiment/weights/FastSAM-s.pt'
    start = time.perf_counter()
    model = FastSAM(str(weights))
    load_seconds = time.perf_counter() - start
    scale = 1024 / max(height, width)
    small_width, small_height = int(width * scale), int(height * scale)
    small = cv2.resize(image, (small_width, small_height))
    start = time.perf_counter()
    result = model(cv2.cvtColor(small, cv2.COLOR_RGB2BGR), device='cpu', retina_masks=True,
                   imgsz=640, conf=0.4, iou=0.9, verbose=False)[0]
    inference_seconds = time.perf_counter() - start
    start = time.perf_counter()
    masks = []
    if result.masks is not None:
        for tensor in result.masks.data:
            mask = tensor.cpu().numpy().astype(np.uint8)
            if mask.shape != (small_height, small_width):
                mask = cv2.resize(mask, (small_width, small_height), interpolation=cv2.INTER_NEAREST)
            area = int(mask.sum())
            if not 300 <= area <= small_height * small_width * 0.03:
                continue
            if any(np.logical_and(mask, previous).sum() / max(np.logical_or(mask, previous).sum(), 1) > 0.5 for previous in masks):
                continue
            masks.append(mask)
    filter_seconds = time.perf_counter() - start
    gt_area = np.bincount(ground_truth.ravel(), minlength=len(shapes)+1)
    candidates = []
    for pred_index, mask in enumerate(masks, 1):
        full_mask = cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST).astype(bool)
        intersections = np.bincount(ground_truth[full_mask], minlength=len(shapes)+1)
        union = gt_area + full_mask.sum() - intersections
        for gt_index in np.flatnonzero(intersections[1:]) + 1:
            iou = float(intersections[gt_index] / union[gt_index])
            if iou >= .5:
                candidates.append((iou, int(gt_index), pred_index))
    pairs, used_gt, used_pred = [], set(), set()
    for iou, gt_index, pred_index in sorted(candidates, reverse=True):
        if gt_index not in used_gt and pred_index not in used_pred:
            used_gt.add(gt_index); used_pred.add(pred_index)
            pairs.append({'ground_truth_id':gt_index, 'prediction_id':pred_index, 'iou':iou})
    args.output.mkdir(parents=True, exist_ok=False)
    overlay = Image.fromarray(small.copy()); draw = ImageDraw.Draw(overlay)
    crops = []
    for index, mask in enumerate(masks, 1):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: continue
        xs, ys = np.where(mask)[1], np.where(mask)[0]
        x1, y1, x2, y2 = int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)
        for contour in contours:
            pts = [(int(p[0][0]), int(p[0][1])) for p in contour]
            if len(pts)>1: draw.line(pts+[pts[0]], fill='lime' if index in used_pred else 'red', width=2)
        draw.text((x1,y1),str(index),fill='white',stroke_width=2,stroke_fill='black')
        bbox = [int(x1/scale), int(y1/scale), min(width, int(np.ceil(x2/scale))), min(height, int(np.ceil(y2/scale)))]
        crop, _ = make_crop(image, bbox, [235,235,235])
        crops.append((index, Image.fromarray(crop)))
    overlay.save(args.output / 'numbered_masks.png')
    contact = Image.new('RGB', (960, max(1,(len(crops)+5)//6)*184), 'white'); draw = ImageDraw.Draw(contact)
    for position, (index, crop) in enumerate(crops):
        crop.thumbnail((160,160)); x=(position%6)*160; y=(position//6)*184
        contact.paste(crop, (x,y)); draw.text((x,y+160), f'{index} '+('match' if index in used_pred else 'extra'), fill='black')
    contact.save(args.output / 'crops.png')
    gt_view = Image.fromarray(small.copy()); draw = ImageDraw.Draw(gt_view)
    for index, shape in enumerate(shapes, 1):
        points = [(round(x*scale),round(y*scale)) for x,y in shape['points']]
        draw.line(points+[points[0]], fill='lime' if index in used_gt else 'red', width=2)
        draw.text(points[0],str(index),fill='white',stroke_width=2,stroke_fill='black')
    gt_view.save(args.output / 'ground_truth_matches.png')
    metrics = {'image':args.stem,'ground_truth':len(shapes),'predictions':len(masks),'matched_iou_50':len(pairs),
               'missed':len(shapes)-len(pairs),'extra':len(masks)-len(pairs),'count_error':len(masks)-len(shapes),
               'matches':pairs,'missed_ground_truth_ids':sorted(set(range(1,len(shapes)+1))-used_gt),
               'extra_prediction_ids':sorted(set(range(1,len(masks)+1))-used_pred),
               'inference_seconds':inference_seconds,'filter_seconds':filter_seconds,'model_load_seconds':load_seconds,
               'settings':{'resize_long_side':1024,'imgsz':640,'conf':0.4,'nms_iou':0.9,'retina_masks':True,'min_area':300,'max_area_fraction':.03,'duplicate_iou':.5,'device':'cpu'},
               'checkpoint_sha256':hashlib.sha256(weights.read_bytes()).hexdigest()}
    (args.output / 'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('matches','missed_ground_truth_ids','extra_prediction_ids')},indent=2),flush=True)


if __name__ == '__main__':
    main()
