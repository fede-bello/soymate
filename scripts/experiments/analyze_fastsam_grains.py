#!/usr/bin/env python3
"""Experimental FastSAM grain masks and crop-based visible-hole smoke test."""
import argparse
import html
import json
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from grain_pipeline import YoloDetector, load_upright_image, make_crop, sha256_file


def render_review(output, summary):
    """Write a local review page without changing the original inference manifest."""
    rows = []
    for component in summary['components']:
        candidate_id = component['id']
        warnings = ', '.join(component['warnings']) or 'none'
        flag = 'Visible-hole flag' if component['flagged'] else 'No visible-hole flag'
        rows.append(f'''<article data-flagged="{str(component['flagged']).lower()}">
<label><input type="checkbox" checked data-id="{candidate_id}"> Keep candidate {candidate_id}</label>
<a href="{html.escape(component['crop_path'], quote=True)}"><img src="{html.escape(component['crop_path'], quote=True)}" alt="Candidate {candidate_id} crop"></a>
<p>{flag}<br>Warnings: {html.escape(warnings)}</p></article>''')
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>FastSAM candidate review</title>
<style>body{font:16px system-ui;max-width:1100px;margin:auto;padding:1rem} .overview{max-width:100%}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:1rem}
article{border:1px solid #aaa;padding:.6rem} article img{display:block;width:100%;margin-top:.5rem}
article:has(input:not(:checked)){opacity:.45} button{padding:.5rem}</style></head><body>
<h1>FastSAM candidate review</h1><p>Uncheck obvious false candidates. Inspect all outlines and crops; missed or merged grains cannot be added here.</p>
<p><strong>Original model output: MODEL_COUNTS</strong></p>
<p><strong id="totals"></strong></p><p id="storage"></p>
<button id="export" type="button">Download review decisions</button>
<p>Flags are experimental visible-hole predictions, not confirmed damage. Associations were computed before review: rejecting a mask does not reassign detections. A detection whose centre overlaps masks remains rejected even if one mask is unchecked. Inspect the annotated image and manifest for rejected boxes and warnings.</p>
<p>Run warnings: WARNINGS</p><p><a href="annotated.png">Annotated image with detection boxes</a> · <a href="manifest.json">Original manifest</a></p>
<a href="numbered_masks.png"><img class="overview" src="numbered_masks.png" alt="Numbered candidate outlines"></a>
<div class="grid">ROWS</div>
<script>
const boxes = [...document.querySelectorAll('input[data-id]')];
const storageKey = 'fastsam-review:' + location.href;
const storage = document.querySelector('#storage');
let persistent = false;
try {
  const saved = JSON.parse(localStorage.getItem(storageKey) || '[]');
  if (Array.isArray(saved)) boxes.forEach(box => box.checked = !saved.includes(Number(box.dataset.id)));
  localStorage.setItem(storageKey, JSON.stringify(boxes.filter(box => !box.checked).map(box => Number(box.dataset.id))));
  persistent = true;
} catch (error) { storage.textContent = 'Browser storage unavailable; download decisions before closing.'; }
function update() {
  const kept = boxes.filter(box => box.checked);
  const rejected = boxes.filter(box => !box.checked).map(box => Number(box.dataset.id));
  const flagged = kept.filter(box => box.closest('article').dataset.flagged === 'true').length;
  document.querySelector('#totals').textContent = `Human review: ${kept.length} retained candidates · ${flagged} retained with model visible-hole flags · ${rejected.length} rejected`;
  if (persistent) {
    try { localStorage.setItem(storageKey, JSON.stringify(rejected)); storage.textContent = 'Review stored in this browser at this report location. Download a backup before moving or clearing browser data.'; }
    catch (error) { persistent = false; storage.textContent = 'Browser storage unavailable; download decisions before closing.'; }
  }
}
boxes.forEach(box => box.addEventListener('change', update));
document.querySelector('#export').addEventListener('click', () => {
  const review = {input_sha256: INPUT_HASH, rejected_candidate_ids: boxes.filter(box => !box.checked).map(box => Number(box.dataset.id))};
  const link = document.createElement('a'); link.href = URL.createObjectURL(new Blob([JSON.stringify(review, null, 2) + '\\n'], {type:'application/json'}));
  link.download = 'review-decisions.json'; link.click(); setTimeout(() => URL.revokeObjectURL(link.href), 1000);
});
update();</script></body></html>'''
    page = page.replace('WARNINGS', html.escape(', '.join(summary['warnings']) or 'none'))
    page = page.replace('MODEL_COUNTS', f"{len(summary['components'])} grain candidates · "
                        f"{sum(component['flagged'] for component in summary['components'])} visible-hole flags")
    page = page.replace('ROWS', '\n'.join(rows)).replace('INPUT_HASH', json.dumps(summary['input']['sha256']))
    (output/'review.html').write_text(page, encoding='utf-8')


def generate_masks(image, weights):
    """Generate and filter masks using the previously tested benchmark settings."""
    from ultralytics import FastSAM
    height, width = image.shape[:2]
    scale = 1024 / max(height, width)
    small_width, small_height = int(width * scale), int(height * scale)
    small = cv2.resize(image, (small_width, small_height))
    model = FastSAM(str(weights))
    started = time.perf_counter()
    result = model(cv2.cvtColor(small, cv2.COLOR_RGB2BGR), device='cpu', retina_masks=True,
                   imgsz=640, conf=0.4, iou=0.9, max_det=300, verbose=False)[0]
    inference_seconds = time.perf_counter() - started
    started = time.perf_counter()
    masks = []
    if result.masks is not None:
        for tensor in result.masks.data:
            mask = tensor.cpu().numpy().astype(np.uint8)
            if mask.shape != (small_height, small_width):
                mask = cv2.resize(mask, (small_width, small_height), interpolation=cv2.INTER_NEAREST)
            area = int(mask.sum())
            if not 300 <= area <= small_width * small_height * 0.03:
                continue
            if any(np.logical_and(mask, prior).sum() / max(np.logical_or(mask, prior).sum(), 1) > .5 for prior in masks):
                continue
            masks.append(mask)
    # IDs are spatially ordered after the benchmark's order-dependent filtering.
    def spatial_key(mask):
        ys, xs = np.nonzero(mask)
        return (int(ys.min()), int(xs.min()), float(ys.mean()), float(xs.mean()))
    masks.sort(key=spatial_key)
    return masks, {'inference': inference_seconds, 'filtering': time.perf_counter()-started}, (small_width, small_height), len(result.boxes)


def crop_mask(mask, origin, side, image_shape):
    """Map a resized-image mask to a padded crop in upright source coordinates."""
    height, width = image_shape[:2]
    small_height, small_width = mask.shape
    x = np.arange(origin[0], origin[0]+side)
    y = np.arange(origin[1], origin[1]+side)
    valid_x, valid_y = (x >= 0) & (x < width), (y >= 0) & (y < height)
    crop = np.zeros((side, side), np.uint8)
    source_x = np.floor(x[valid_x] * small_width / width).astype(int)
    source_y = np.floor(y[valid_y] * small_height / height).astype(int)
    crop[np.ix_(valid_y, valid_x)] = mask[np.ix_(source_y, source_x)]
    return crop


def associate_predictions(predictions, target_mask, origin, all_masks, image_shape):
    """Map crop boxes to original pixels and accept centres unique to the target."""
    height, width = image_shape[:2]
    mapped = []
    for prediction in predictions:
        x1,y1,x2,y2 = prediction['box']
        centre_x, centre_y = (x1+x2)/2, (y1+y2)/2
        pixel_x, pixel_y = int(math.floor(centre_x)), int(math.floor(centre_y))
        original_x, original_y = centre_x+origin[0], centre_y+origin[1]
        reason = None
        if not (0 <= original_x < width and 0 <= original_y < height):
            reason = 'centre_outside_image'
        elif not (0 <= pixel_y < target_mask.shape[0] and 0 <= pixel_x < target_mask.shape[1] and target_mask[pixel_y,pixel_x]):
            reason = 'centre_outside_target_mask'
        else:
            sy = min(all_masks[0].shape[0]-1, int(original_y*all_masks[0].shape[0]/height))
            sx = min(all_masks[0].shape[1]-1, int(original_x*all_masks[0].shape[1]/width))
            if sum(bool(mask[sy,sx]) for mask in all_masks) > 1:
                reason = 'centre_in_overlapping_masks'
        box = [x1+origin[0], y1+origin[1], x2+origin[0], y2+origin[1]]
        clipped = [max(0.,min(width,box[0])),max(0.,min(height,box[1])),
                   max(0.,min(width,box[2])),max(0.,min(height,box[3]))]
        mapped.append({'box_original':clipped,'box_original_unclipped':box,'box_crop':prediction['box'],
                       'confidence':prediction['confidence'],'accepted':reason is None,'rejection_reason':reason})
    return mapped


def run(image_path, output, segmentation_weights, detector_weights, confidence, compare_masked):
    """Write masks, crops, association records and review images for one photo."""
    started = time.perf_counter()
    image = load_upright_image(image_path)
    height,width = image.shape[:2]
    masks, timing, (small_width,small_height), raw_candidates = generate_masks(image,segmentation_weights)
    coverage = np.zeros((small_height,small_width),np.uint16)
    for mask in masks: coverage += mask
    border = np.concatenate((image[0],image[-1],image[:,0],image[:,-1]))
    background = np.median(border,axis=0).astype(np.uint8)
    detector = YoloDetector(detector_weights,'cpu',8)
    output.mkdir(parents=True,exist_ok=False)
    (output/'crops').mkdir(); (output/'masks').mkdir()
    components=[]; crops=[]; crop_masks=[]
    overlay=Image.fromarray(image.copy()); draw=ImageDraw.Draw(overlay)
    for index,mask in enumerate(masks,1):
        ys,xs=np.nonzero(mask)
        x1=int(xs.min()*width/small_width); y1=int(ys.min()*height/small_height)
        x2=min(width, math.ceil((int(xs.max())+1)*width/small_width)); y2=min(height, math.ceil((int(ys.max())+1)*height/small_height))
        bbox=[x1,y1,x2,y2]
        crop,origin=make_crop(image,bbox,background,1.5)
        target=crop_mask(mask,origin,crop.shape[0],image.shape)
        crop_name=f'crops/grain-{index:04d}.png'; mask_name=f'masks/grain-{index:04d}.png'
        Image.fromarray(crop).save(output/crop_name); Image.fromarray(target*255).save(output/mask_name)
        warnings=[]
        if xs.min()==0 or ys.min()==0 or xs.max()==small_width-1 or ys.max()==small_height-1: warnings.append('image_edge')
        if np.any((mask>0)&(coverage>1)): warnings.append('overlaps_another_mask')
        if xs.max()-xs.min()<10 or ys.max()-ys.min()<10: warnings.append('small_mask_dimension')
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            points=[(round(p[0][0]*width/small_width),round(p[0][1]*height/small_height)) for p in contour]
            if len(points)>1: draw.line(points+[points[0]],fill='orange' if warnings else 'cyan',width=3)
        draw.text((x1,y1),str(index),fill='white',stroke_width=2,stroke_fill='black')
        components.append({'id':index,'bbox_original_xyxy':bbox,'crop_origin_xy':origin,'crop_size':list(crop.shape[:2][::-1]),
                           'crop_path':crop_name,'crop_mask_path':mask_name,'mask_area_resized':int(mask.sum()),'warnings':warnings})
        crops.append(crop); crop_masks.append(target)
    overlay.save(output/'numbered_masks.png')
    started_detector=time.perf_counter()
    predictions=detector.predict(crops) if crops else []
    for component,target,origin,prediction in zip(components,crop_masks,(item['crop_origin_xy'] for item in components),predictions,strict=True):
        component['detections']=associate_predictions(prediction,target,origin,masks,image.shape)
        component['flagged']=any(item['accepted'] and item['confidence']>=confidence for item in component['detections'])
    selected=min(compare_masked,len(crops))
    suppressed=[np.where(crop_masks[i][:,:,None]>0,crops[i],background).astype(np.uint8) for i in range(selected)]
    masked_predictions=detector.predict(suppressed) if suppressed else []
    detector_seconds=time.perf_counter()-started_detector
    comparison=Image.new('RGB',(640,max(1,selected)*180),'white'); compare_draw=ImageDraw.Draw(comparison)
    for position in range(selected):
        component=components[position]
        mapped=associate_predictions(masked_predictions[position],crop_masks[position],component['crop_origin_xy'],masks,image.shape)
        component['masked_crop_detections']=mapped
        Image.fromarray(suppressed[position]).save(output/'crops'/f'grain-{position+1:04d}-suppressed.png')
        for column,(crop,items,title) in enumerate(((crops[position],component['detections'],'padded'),(suppressed[position],mapped,'outside mask suppressed'))):
            thumb=Image.fromarray(crop.copy()); thumbnail_draw=ImageDraw.Draw(thumb)
            for det in items:
                color='lime' if det['accepted'] and det['confidence']>=confidence else 'red'
                thumbnail_draw.rectangle(det['box_crop'],outline=color,width=2)
            thumb.thumbnail((280,155)); x=column*320; y=position*180
            comparison.paste(thumb,(x,y)); compare_draw.text((x,y+157),f"grain {component['id']} {title}: {len(items)} boxes",fill='black')
    comparison.save(output/'crop_comparison.png')
    annotated=Image.open(output/'numbered_masks.png').convert('RGB'); draw=ImageDraw.Draw(annotated)
    for component in components:
        for detection in component['detections']:
            if detection['confidence'] < confidence: continue
            box=detection['box_original']; color='lime' if detection['accepted'] else 'red'
            draw.rectangle(box,outline=color,width=3)
            draw.text((box[0],box[1]),f"G{component['id']} {detection['confidence']:.2f}"+(' rejected' if not detection['accepted'] else ''),fill=color,stroke_width=2,stroke_fill='black')
    annotated.save(output/'annotated.png')
    summary={'experimental':True,'input':{'path':str(image_path.resolve()),'sha256':sha256_file(image_path),'width':width,'height':height},
             'settings':{'segmentation':'FastSAM-small','device':'cpu','long_side':1024,'image_size':640,'confidence':.4,'nms_iou':.9,'max_detections':300,'min_mask_area':300,'max_mask_area_fraction':.03,'duplicate_mask_iou':.5,'crop_padding':1.5,'hole_confidence':confidence,'hole_collection_confidence':.05,'masked_comparison_count':selected},
             'weights':{'segmentation_sha256':sha256_file(segmentation_weights),'detector_sha256':sha256_file(detector_weights)},
             'warnings': ['max_detections_reached'] if raw_candidates >= 300 else [],
             'counts':{'raw_candidates':raw_candidates,'candidates':len(components),'flagged_grains':sum(item['flagged'] for item in components),'edge_candidates':sum('image_edge' in item['warnings'] for item in components),'overlapping_candidates':sum('overlaps_another_mask' in item['warnings'] for item in components)},
             'timings_seconds':timing|{'hole_detector_including_masked_comparison':detector_seconds,'total':time.perf_counter()-started},
             'limitations':['Experimental visible-hole candidates require review; damage accuracy is unmeasured.','Mask overlaps and rectangular crops can affect association.','IDs are spatially ordered for the accepted masks, not persistent object identities.'],
             'components':components}
    (output/'manifest.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    render_review(output, summary)
    print(json.dumps({'output':str(output),'counts':summary['counts'],'timings_seconds':summary['timings_seconds']},indent=2))


def main():
    """Parse paths and prevent accidental overwrites outside the ignored output tree."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path); parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--segmentation-weights',type=Path,default=ROOT/'outputs/multigrain-experiment/weights/FastSAM-s.pt')
    parser.add_argument('--detector-weights',type=Path,default=ROOT/'runs/soybean_hole/long40/weights/best.pt')
    parser.add_argument('--confidence',type=float,default=.4); parser.add_argument('--compare-masked',type=int,default=5)
    args=parser.parse_args(); output=args.output.resolve()
    if not output.is_relative_to((ROOT/'outputs').resolve()) or output==(ROOT/'outputs').resolve() or output.exists(): parser.error('Output must be a fresh directory inside outputs/')
    if not args.image.is_file(): parser.error(f'Input image not found: {args.image}')
    missing = [str(path) for path in (args.segmentation_weights,args.detector_weights) if not path.is_file()]
    if missing: parser.error('Missing local checkpoint(s): ' + ', '.join(missing) + '. See docs/fastsam_grain_experiment.md for setup; checkpoints are Git-ignored.')
    if not .05<=args.confidence<=1 or args.compare_masked<0: parser.error('Confidence must be 0.05–1; comparison count must be nonnegative')
    run(args.image,output,args.segmentation_weights,args.detector_weights,args.confidence,args.compare_masked)

if __name__=='__main__': main()
