"""Real lot-level ground truth: images and a Label Studio project for hand-labelling seeds (critique C2).

Run on the box:  cd ~/soymate-next && uv run python labelling/prepare_labelling.py
Writes data/labels/images/*.jpg (the photos or regions to label), data/labels/tasks.json (Label Studio import)
and data/labels/regions.csv (where each region comes from, so labels map back to the source photo).

Labelling rule: one point on the centre of every seed whose centre is inside the image and that is at least
half visible (in the packed Lin photos the half-hidden lower layer is skipped), with its class.
Points, not our segmentation, so the count and class ground truth do not depend on our own pipeline.
"""
import json
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "labels"
LIN_ORIG = RAW / "soybean_seeds_5classes" / "Part of the original soybean images"
# (name, source path, crop box x1, y1, x2, y2 or None for the whole photo)
REGIONS = [
    ("ghana_farmersaved_g17", RAW / "ghana_soybean/seed_data/Soyabean/group_capture/FarmerSaved/PXL_20260315_135711992.jpg", None),
    ("lin_orig_20220426214755980_centre", LIN_ORIG / "Image_20220426214755980.jpg", (636, 374, 2436, 1674)),
    ("lin_orig_20220430064718171_centre", LIN_ORIG / "Image_20220430064718171.jpg", (636, 374, 2436, 1674)),
]

if __name__ == "__main__":
    (OUT / "images").mkdir(parents=True, exist_ok=True)
    rows, tasks = [], []
    for name, src, box in REGIONS:
        im = Image.open(src).convert("RGB")
        if box:
            im = im.crop(box)
        im.save(OUT / "images" / f"{name}.jpg", quality=95)
        rows.append({"name": name, "source": src.relative_to(RAW).as_posix(),
                     "x1": box[0] if box else 0, "y1": box[1] if box else 0, "width": im.width, "height": im.height})
        tasks.append({"data": {"image": f"/data/local-files/?d=images/{name}.jpg", "name": name}})
    pd.DataFrame(rows).to_csv(OUT / "regions.csv", index=False)
    (OUT / "tasks.json").write_text(json.dumps(tasks, indent=1))
    print(pd.DataFrame(rows).to_string())
