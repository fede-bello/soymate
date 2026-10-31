#!/usr/bin/env python3
"""Analyze a photo of separated grains and produce an inspectable local report."""

import argparse
import json
import time
from pathlib import Path

from grain_pipeline import YoloDetector, load_upright_image, run_analysis

ROOT = Path(__file__).resolve().parents[2]


def main():
    """Parse analysis settings, validate paths, and run the local pipeline."""
    command_start = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Photo of separated grains on a contrasting background")
    parser.add_argument("--output", type=Path, required=True, help="Fresh directory under outputs/")
    parser.add_argument("--weights", type=Path, default=ROOT / "runs/soybean_hole/long40/weights/best.pt")
    parser.add_argument("--species", required=True, help="Species recorded in the report")
    parser.add_argument("--provenance", default="unspecified", help="Natural, synthetic, composite, or other source")
    parser.add_argument("--device", choices=("auto", "cpu", "mps"), default="auto")
    parser.add_argument("--mode", choices=("crops", "full", "compare"), default="crops")
    parser.add_argument("--flag-confidence", type=float, default=0.4)
    parser.add_argument("--review-confidence", type=float, default=0.1)
    parser.add_argument("--min-area-fraction", type=float, default=0.00005,
                        help="Minimum filled component area as a fraction of image pixels")
    parser.add_argument("--border-fraction", type=float, default=0.01,
                        help="Width of background sampling border relative to shorter image dimension")
    parser.add_argument("--distance-threshold", type=int, help="Fixed 0–255 Lab colour-distance threshold; omit for Otsu")
    parser.add_argument("--crop-padding", type=float, default=1.5, help="Square crop side relative to longest grain dimension")
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()
    if not args.image.is_file() or not args.weights.is_file():
        parser.error("Both input image and checkpoint must exist")
    if not (0.05 <= args.review_confidence <= 1 and 0.05 <= args.flag_confidence <= 1):
        parser.error("Confidence thresholds must be between collection confidence 0.05 and 1")
    if args.review_confidence > args.flag_confidence:
        parser.error("Review confidence must not exceed flagging confidence")
    if not (0 < args.min_area_fraction < 1 and 0 < args.border_fraction <= 0.25 and args.crop_padding >= 1):
        parser.error("Invalid segmentation or crop settings")
    if args.distance_threshold is not None and not 0 <= args.distance_threshold <= 255:
        parser.error("Distance threshold must be in 0–255")
    if args.batch_size < 1:
        parser.error("Batch size must be positive")
    output = args.output.resolve()
    output_root = (ROOT / "outputs").resolve()
    if output == output_root or not output.is_relative_to(output_root):
        parser.error("Output must be a fresh subdirectory of the repository's outputs/")
    if output.exists():
        parser.error(f"Output already exists: {output}")
    import torch
    mps_available = torch.backends.mps.is_available()
    if args.device == "mps" and not mps_available:
        parser.error("MPS requested but unavailable; choose --device cpu or auto")
    device = "mps" if args.device == "auto" and mps_available else "cpu" if args.device == "auto" else args.device
    image = load_upright_image(args.image)
    detector = YoloDetector(args.weights, device, args.batch_size)
    output.mkdir(parents=True, exist_ok=False)
    configuration = {"mode": args.mode, "flag_confidence": args.flag_confidence,
                     "review_confidence": args.review_confidence, "collection_confidence": 0.05,
                     "nms_iou": 0.7, "image_size": 640, "max_detections": 300,
                     "min_area_fraction": args.min_area_fraction, "border_fraction": args.border_fraction,
                     "distance_threshold": args.distance_threshold, "crop_padding": args.crop_padding,
                     "batch_size": args.batch_size}
    summary = run_analysis(image, detector, output, configuration,
                           {"species": args.species, "provenance": args.provenance},
                           args.image.resolve(), args.weights.resolve(), device)
    summary["timings_seconds"]["command_including_model_load"] = time.perf_counter() - command_start
    (output / "sample.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "device": device, "results": summary["results"],
                      "timings_seconds": summary["timings_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
