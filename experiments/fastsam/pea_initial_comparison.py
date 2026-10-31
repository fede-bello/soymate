"""Exploratory polygon comparison and distance-marker watershed; CPU only."""
import json, sys, time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'grain_counting'))
from grain_pipeline import load_upright_image, segment_grains, make_crop, _draw_overlay

root = Path('data/raw/pea_zenodo_21110940')
prior = Path('outputs/multigrain-experiment')
if len(sys.argv) != 2:
    raise SystemExit('Usage: pea_initial_comparison.py FRESH_OUTPUT_DIRECTORY_UNDER_outputs')
out = Path(sys.argv[1]).resolve()
if not out.is_relative_to(Path('outputs').resolve()) or out == Path('outputs').resolve():
    raise SystemExit('Output must be a fresh directory under outputs/')
out.mkdir(parents=True, exist_ok=False)
for stem, count in [('20210406_145931', 40), ('20210406_150838', 187)]:
    image = load_upright_image(root / 'images' / (stem + '.jpg'))
    height, width = image.shape[:2]
    annotation = json.loads((root / 'annotations' / (stem + '.json')).read_text())
    gt = np.zeros((height, width), np.int32)
    sizes = []
    for index, shape in enumerate(annotation['shapes'], 1):
        points = np.rint(shape['points']).astype(np.int32)
        sizes.append(np.ptp(points, axis=0).max())
        cv2.fillPoly(gt, [points], index)
    default = np.asarray(Image.open(prior / f'pea-{count}-default/instances.png')).astype(np.int32)
    configs = [('default', default)]
    if count == 40:
        configs.append(('threshold60', np.asarray(Image.open(prior / 'pea-40-threshold60/instances.png')).astype(np.int32)))
    start = time.perf_counter()
    labels, foreground, filled, components, excluded, info = segment_grains(image, round(height * width * .00005), .01)
    foreground = (labels > 0).astype(np.uint8)
    distance = cv2.distanceTransform(foreground, cv2.DIST_L2, 5)
    peaks = (distance == cv2.dilate(distance, np.ones((91, 91), np.uint8))) & (distance >= 30)
    num, peak_labels, stats, centroids = cv2.connectedComponentsWithStats(peaks.astype(np.uint8))
    markers = np.zeros((height, width), np.int32)
    markers[foreground == 0] = 1
    for index in range(1, num):
        x, y = np.rint(centroids[index]).astype(int)
        markers[y, x] = index + 1
    surface = np.uint8(np.clip(255 - distance * 2, 0, 255))
    cv2.watershed(cv2.cvtColor(surface, cv2.COLOR_GRAY2BGR), markers)
    watershed = np.where((markers > 1) & (foreground > 0), markers - 1, 0).astype(np.int32)
    elapsed = time.perf_counter() - start
    configs.append(('watershed', watershed))
    for name, prediction in configs:
        pred_count = int(prediction.max())
        paired = gt.astype(np.int64) * (pred_count + 1) + prediction
        overlap = np.bincount(paired.ravel(), minlength=(count + 1) * (pred_count + 1)).reshape(count + 1, pred_count + 1)
        intersection = overlap[1:, 1:]
        gt_area = overlap[1:, :].sum(axis=1)
        pred_area = overlap[:, 1:].sum(axis=0)
        union = gt_area[:, None] + pred_area[None, :] - intersection
        iou = np.divide(intersection, union, out=np.zeros_like(intersection, dtype=float), where=union > 0)
        matched = int((iou >= .5).sum())
        merges = int(((intersection / np.maximum(gt_area[:, None], 1)) >= .2).sum(axis=0).__ge__(2).sum())
        splits = int(((intersection / np.maximum(gt_area[:, None], 1)) >= .2).sum(axis=1).__ge__(2).sum())
        result = dict(photo=stem, annotated=count, predicted=pred_count, matched_iou_50=matched, unmatched_gt=count-matched, unmatched_predictions=pred_count-matched, merge_candidates=merges, split_candidates=splits, median_gt_long_side_pixels=float(np.median(sizes)), segmentation_seconds=elapsed if name == 'watershed' else None)
        print(name, json.dumps(result), flush=True)
        (out / f'pea-{count}-{name}-metrics.json').write_text(json.dumps(result, indent=2)+'\n')
        if name == 'watershed':
            destination = out / f'pea-{count}-watershed'
            destination.mkdir(exist_ok=False)
            Image.fromarray(watershed.astype(np.uint16)).save(destination / 'instances.png')
            components = []
            crops = []
            for identifier in range(1, pred_count+1):
                ys, xs = np.where(watershed == identifier)
                if not len(xs): continue
                bbox = [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]
                components.append(dict(id=identifier,bbox=bbox))
                crop,_ = make_crop(image,bbox,[235,235,235])
                crops.append((identifier,Image.fromarray(crop)))
            _draw_overlay(image, watershed, components, []).save(destination / 'instances_overlay.png')
            from PIL import ImageDraw
            contact = Image.new('RGB',(960, ((len(crops)+5)//6)*184),'white')
            draw = ImageDraw.Draw(contact)
            for index,(identifier,crop) in enumerate(crops):
                crop.thumbnail((160,160)); x=(index%6)*160; y=(index//6)*184
                contact.paste(crop,(x,y)); draw.text((x,y+160),str(identifier),fill='black')
            contact.save(destination / 'crops.png')
