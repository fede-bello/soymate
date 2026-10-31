"""Write ~480 px JPEG gallery thumbnails next to the demo examples (<stem>.thumb.jpg).

Run on the box after build_examples.py:  cd ~/soymate && .venv/bin/python app/api/make_thumbs.py
Thumbnails are for the gallery only; /api/analyze always gets the original file (re-encoding moves class shares).
Idempotent: a thumbnail newer than its original is skipped.
"""
import json
from pathlib import Path

from PIL import Image, ImageOps

EXAMPLES = Path(__file__).resolve().parent / "examples"
SIZE = 480


def main() -> None:
    meta = EXAMPLES / "examples.json"
    if not meta.exists():
        print("no examples.json, nothing to do")
        return
    for ex in json.loads(meta.read_text()):
        src = EXAMPLES / ex["url"].rsplit("/", 1)[-1]
        dst = EXAMPLES / f"{src.stem}.thumb.jpg"
        if not src.exists():
            print(f"missing {src.name}")
            continue
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            continue
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((SIZE, SIZE), Image.Resampling.LANCZOS)
            im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
        print(f"{dst.name}: {dst.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
