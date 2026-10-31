#!/usr/bin/env python3
"""Compare saved crop masks to LabelMe pea polygons at full resolution."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image


def evaluate(manifest_path, annotation_path):
    """Greedily match candidate masks and polygons at IoU >= 0.5."""
    manifest=json.loads(manifest_path.read_text())
    shapes=json.loads(annotation_path.read_text())['shapes']
    height,width=manifest['input']['height'],manifest['input']['width']
    labels=np.zeros((height,width),np.int32)
    for index,shape in enumerate(shapes,1):
        cv2.fillPoly(labels,[np.rint(shape['points']).astype(np.int32)],index)
    areas=np.bincount(labels.ravel(),minlength=len(shapes)+1)
    candidates=[]
    for component in manifest['components']:
        mask=np.asarray(Image.open(manifest_path.parent/component['crop_mask_path']))>0
        origin_x,origin_y=component['crop_origin_xy']; side_y,side_x=mask.shape
        left,top=max(0,origin_x),max(0,origin_y)
        right,bottom=min(width,origin_x+side_x),min(height,origin_y+side_y)
        if right<=left or bottom<=top: continue
        region=mask[top-origin_y:bottom-origin_y,left-origin_x:right-origin_x]
        intersection=np.bincount(labels[top:bottom,left:right][region],minlength=len(shapes)+1)
        predicted_area=int(region.sum())
        for gt_id in np.flatnonzero(intersection[1:])+1:
            iou=float(intersection[gt_id]/(areas[gt_id]+predicted_area-intersection[gt_id]))
            if iou>=.5: candidates.append((iou,int(gt_id),component['id']))
    used_gt=set(); used_pred=set(); matches=[]
    for iou,gt_id,pred_id in sorted(candidates,reverse=True):
        if gt_id not in used_gt and pred_id not in used_pred:
            used_gt.add(gt_id); used_pred.add(pred_id)
            matches.append({'polygon_id':gt_id,'candidate_id':pred_id,'iou':iou})
    return {'annotation':str(annotation_path),'ground_truth':len(shapes),'predictions':len(manifest['components']),
            'matched':len(matches),'missed':len(shapes)-len(matches),'extra':len(manifest['components'])-len(matches),
            'count_error':len(manifest['components'])-len(shapes),'matches':matches,
            'missed_polygon_ids':sorted(set(range(1,len(shapes)+1))-used_gt),
            'extra_candidate_ids':sorted({item['id'] for item in manifest['components']}-used_pred)}


def main():
    """Write polygon comparison beside the existing experiment manifest."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path); parser.add_argument('annotation',type=Path)
    args=parser.parse_args(); output=args.manifest.parent/'polygon_metrics.json'
    if output.exists(): parser.error(f'Refusing to overwrite {output}')
    metrics=evaluate(args.manifest,args.annotation)
    output.write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps({key:metrics[key] for key in ('ground_truth','predictions','matched','missed','extra','count_error')},indent=2))

if __name__=='__main__': main()
