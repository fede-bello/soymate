"""Contact sheet of source image | masked crop pairs, for checking seed masks by eye.

Usage: uv run python scripts/data/qc_sheet.py <manifest_csv> <raw_root> <out_jpg> [n=24] [pandas query]
"""
import sys

import pandas as pd
from PIL import Image

manifest, raw_root, out = sys.argv[1:4]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 24
m = pd.read_csv(manifest, keep_default_na=False)
m = m[m["crop"] != ""]
if len(sys.argv) > 5:
    m = m.query(sys.argv[5])
s = m.sample(min(n, len(m)), random_state=1)
sheet = Image.new("RGB", (448 * 4, 224 * ((len(s) + 3) // 4)))
for i, (_, r) in enumerate(s.iterrows()):
    src = Image.open(f"{raw_root}/{r.source_image}").convert("RGB")
    src.thumbnail((224, 224))
    sheet.paste(src, ((i % 4) * 448, (i // 4) * 224))
    sheet.paste(Image.open(f"data/crops/{r.crop}").convert("RGB"), ((i % 4) * 448 + 224, (i // 4) * 224))
sheet.save(out, quality=80)
