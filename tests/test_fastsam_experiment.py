"""Exercise crop geometry, ambiguity and grain-level aggregation without model weights."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/fastsam'))
import analyze_fastsam_grains as experiment


class FastSamExperimentTests(unittest.TestCase):
    """Verify coordinate mapping and detector association on synthetic masks."""

    def test_padded_crop_mask_and_ambiguous_overlap(self):
        mask=np.zeros((10,10),np.uint8); mask[2:8,2:8]=1
        cropped=experiment.crop_mask(mask,[-2,-2],10,(10,10,3))
        self.assertEqual(cropped[4,4],1)
        self.assertEqual(cropped[0,0],0)
        single=experiment.associate_predictions([{'box':[4,4,6,6],'confidence':.8}],cropped,[-2,-2],[mask],(10,10,3))
        self.assertEqual(single[0]['box_original'],[2,2,4,4])
        self.assertTrue(single[0]['accepted'])
        ambiguous=experiment.associate_predictions([{'box':[4,4,6,6],'confidence':.8}],cropped,[-2,-2],[mask,mask],(10,10,3))
        self.assertEqual(ambiguous[0]['rejection_reason'],'centre_in_overlapping_masks')
        outside=experiment.associate_predictions([{'box':[0,0,1,1],'confidence':.8}],cropped,[-2,-2],[mask],(10,10,3))
        self.assertEqual(outside[0]['rejection_reason'],'centre_outside_image')

    def test_multiple_hole_boxes_flag_one_grain_and_save_masks(self):
        class FakeDetector:
            def __init__(self,*args): pass
            def predict(self,images):
                return [[{'box':[image.shape[1]/2-1,image.shape[0]/2-1,image.shape[1]/2+1,image.shape[0]/2+1],
                          'confidence':.9},
                         {'box':[image.shape[1]/2-2,image.shape[0]/2-2,image.shape[1]/2+2,image.shape[0]/2+2],
                          'confidence':.8}] for image in images]
        mask=np.zeros((50,50),np.uint8); mask[15:35,15:35]=1
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); image=root/'image.png'; weights=root/'weights.pt'
            Image.fromarray(np.full((50,50,3),200,np.uint8)).save(image); weights.write_bytes(b'test')
            with patch.object(experiment,'generate_masks',return_value=([mask],{'inference':0,'filtering':0},(50,50),1)), patch.object(experiment,'YoloDetector',FakeDetector):
                experiment.run(image,root/'output',weights,weights,.4,1)
            manifest=json.loads((root/'output/manifest.json').read_text())
            self.assertEqual(manifest['counts']['flagged_grains'],1)
            self.assertEqual(len(manifest['components'][0]['detections']),2)
            self.assertTrue(all(d['accepted'] for d in manifest['components'][0]['detections']))
            self.assertTrue((root/'output'/manifest['components'][0]['crop_mask_path']).is_file())
            self.assertTrue((root/'output/crop_comparison.png').is_file())

if __name__=='__main__': unittest.main()
