"""Explore distance-surface watershed using the pea experiment foreground."""
import json
import sys
import time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from skimage.segmentation import watershed

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'experiments'/'grain_counting'))
from grain_pipeline import load_upright_image, segment_grains, make_crop, _draw_overlay


def split_foreground(foreground, neighborhood, minimum_distance):
    """Split the filled foreground at distance maxima, restricted to its pixels."""
    distance = cv2.distanceTransform((foreground > 0).astype(np.uint8), cv2.DIST_L2, 5)
    peaks = (distance == cv2.dilate(distance, np.ones((neighborhood, neighborhood), np.uint8))) & (distance >= minimum_distance)
    _, markers = cv2.connectedComponents(peaks.astype(np.uint8))
    return watershed(-distance, markers, mask=foreground > 0).astype(np.int32)


def main():
    """Check the synthetic failure and evaluate the development photograph."""
    synthetic = np.zeros((200,300),np.uint8)
    cv2.circle(synthetic,(110,100),55,1,-1); cv2.circle(synthetic,(190,100),55,1,-1)
    synthetic_labels = split_foreground(synthetic, 51, 10)
    assert set(np.unique(synthetic_labels)) == {0,1,2}
    assert np.all(synthetic_labels[synthetic > 0] > 0)
    data=ROOT/'data/raw/pea_zenodo_21110940'; stem=sys.argv[1]; output=Path(sys.argv[2])
    image=load_upright_image(data/'images'/f'{stem}.jpg'); height,width=image.shape[:2]
    shapes=json.loads((data/'annotations'/f'{stem}.json').read_text())['shapes']
    gt=np.zeros((height,width),np.int32)
    for index,shape in enumerate(shapes,1): cv2.fillPoly(gt,[np.rint(shape['points']).astype(np.int32)],index)
    start=time.perf_counter()
    _,_,filled,_,_,_=segment_grains(image,round(height*width*.00005),.01)
    labels=split_foreground(filled,91,30)
    elapsed=time.perf_counter()-start
    count=int(labels.max())
    overlap=np.bincount((gt.astype(np.int64)*(count+1)+labels).ravel(),minlength=(len(shapes)+1)*(count+1)).reshape(len(shapes)+1,count+1)
    intersections=overlap[1:,1:]; union=overlap[1:,:].sum(axis=1)[:,None]+overlap[:,1:].sum(axis=0)[None,:]-intersections
    iou=np.divide(intersections,union,out=np.zeros_like(intersections,dtype=float),where=union>0)
    pairs=[(float(iou[g,p]),int(g)+1,int(p)+1) for g,p in zip(*np.where(iou>=.5))]
    used_gt=set(); used_pred=set(); matches=[]
    for score,g,p in sorted(pairs,reverse=True):
        if g not in used_gt and p not in used_pred:
            used_gt.add(g); used_pred.add(p); matches.append({'ground_truth_id':g,'prediction_id':p,'iou':score})
    output.mkdir(parents=True,exist_ok=False)
    Image.fromarray(labels.astype(np.uint16)).save(output/'instances.png')
    components=[]; crops=[]
    for index in range(1,count+1):
        ys,xs=np.where(labels==index)
        if not len(xs): continue
        bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
        components.append({'id':index,'bbox':bbox})
        crop,_=make_crop(image,bbox,[235,235,235]); crops.append((index,Image.fromarray(crop)))
    _draw_overlay(image,labels,components,[]).save(output/'numbered_masks.png')
    contact=Image.new('RGB',(960,max(1,(len(crops)+5)//6)*184),'white'); draw=ImageDraw.Draw(contact)
    for position,(index,crop) in enumerate(crops):
        crop.thumbnail((160,160)); x=position%6*160; y=position//6*184
        contact.paste(crop,(x,y)); draw.text((x,y+160),f'{index} '+('match' if index in used_pred else 'extra'),fill='black')
    contact.save(output/'crops.png')
    gt_view=Image.fromarray(image.copy()); draw=ImageDraw.Draw(gt_view)
    for index,shape in enumerate(shapes,1):
        points=[(round(x),round(y)) for x,y in shape['points']]
        draw.line(points+[points[0]],fill='lime' if index in used_gt else 'red',width=3)
        draw.text(points[0],str(index),fill='white',stroke_width=2,stroke_fill='black')
    gt_view.save(output/'ground_truth_matches.png')
    metrics={'image':stem,'ground_truth':len(shapes),'predictions':count,'matched_iou_50':len(matches),'missed':len(shapes)-len(matches),'extra':count-len(matches),'count_error':count-len(shapes),'segmentation_seconds':elapsed,'matches':matches,'missed_ground_truth_ids':sorted(set(range(1,len(shapes)+1))-used_gt),'extra_prediction_ids':sorted(set(range(1,count+1))-used_pred),'settings':{'neighborhood':91,'min_distance':30,'foreground':'filled Otsu Lab border distance; includes edge components'}}
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('matches','missed_ground_truth_ids','extra_prediction_ids')},indent=2),flush=True)

if __name__=='__main__': main()
