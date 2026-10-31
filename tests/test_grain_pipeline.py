"""Focused geometry, aggregation and evaluation checks for the grain MVP."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "grain_counting"))
from grain_pipeline import (load_upright_image, make_crop, map_and_associate,
                            run_analysis, segment_grains, summarize_predictions)
from evaluate_grain_samples import check_manifest, evaluate_manifest, evaluate_photo, summarize_group


class GeometryTests(unittest.TestCase):
    """Check coordinate handling using known, synthetic grain silhouettes."""

    def setUp(self):
        self.image = np.full((100, 200, 3), 255, dtype=np.uint8)
        cv2.circle(self.image, (50, 50), 12, (50, 80, 110), -1)
        cv2.circle(self.image, (50, 50), 3, (255, 255, 255), -1)
        cv2.circle(self.image, (120, 50), 10, (50, 80, 110), -1)
        cv2.rectangle(self.image, (0, 5), (10, 20), (50, 80, 110), -1)
        self.labels, self.foreground, _, self.components, self.excluded, _ = segment_grains(
            self.image, min_area=20, border_fraction=0.01)

    def test_components_holes_and_boundary(self):
        self.assertEqual(len(self.components), 2)
        self.assertEqual(self.labels[50, 50], 1)
        self.assertEqual(self.foreground[50, 50], 0)
        self.assertEqual([item["reason"] for item in self.excluded], ["image_boundary"])

    def test_crop_padding_and_offset_association(self):
        crop, origin = make_crop(self.image, [2, 3, 12, 13], [255, 255, 255], 2)
        self.assertEqual(origin, [-3, -2])
        self.assertEqual(crop.shape, (20, 20, 3))
        self.assertEqual(crop[0, 0].tolist(), [255, 255, 255])
        result = map_and_associate([{"box": [51, 50, 55, 54], "confidence": 0.9}], origin, self.labels, 1)
        self.assertEqual(result[0]["box"], [48.0, 48.0, 52.0, 52.0])
        self.assertEqual(result[0]["instance_id"], 1)
        outside = map_and_associate([{"box": [0, 0, 2, 2], "confidence": 0.9}], origin, self.labels, 1)
        self.assertEqual(outside[0]["rejection_reason"], "centre_outside_image")

    def test_neighbour_rejected_and_duplicates_count_once(self):
        boxes = [{"box": [118, 48, 122, 52], "confidence": 0.9},
                 {"box": [48, 48, 52, 52], "confidence": 0.8},
                 {"box": [49, 49, 51, 51], "confidence": 0.7}]
        results = map_and_associate(boxes, [0, 0], self.labels, 1)
        self.assertEqual(results[0]["rejection_reason"], "different_crop_instance")
        summary = summarize_predictions(self.components, results, 0.4)
        self.assertEqual((summary["grain_candidates"], summary["flagged_grains"]), (2, 1))
        self.assertEqual(summary["flagged_percentage"], 50)
        self.assertIsNone(summarize_predictions([], [], 0.4)["flagged_percentage"])

    def test_exif_orientation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rotated.jpg"
            image = Image.new("RGB", (30, 10), "white")
            exif = image.getexif()
            exif[274] = 6
            image.save(path, exif=exif)
            self.assertEqual(load_upright_image(path).shape, (30, 10, 3))

    def test_compare_outputs_keep_modes_independent(self):
        class FakeDetector:
            def predict(self, images):
                if len(images) == 2:
                    # First crop centre maps to grain 1; second has no detections.
                    side = images[0].shape[0]
                    centre = side / 2
                    return [[{"box": [centre-1, centre-1, centre+1, centre+1], "confidence": 0.8}], []]
                return [[{"box": [118, 48, 122, 52], "confidence": 0.8}]]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, weights_path = root / "input.png", root / "weights.pt"
            Image.fromarray(self.image).save(input_path)
            weights_path.write_bytes(b"fake checkpoint")
            output = root / "run"
            output.mkdir()
            config = {"mode": "compare", "min_area_fraction": 0.001, "border_fraction": .01,
                      "distance_threshold": None, "crop_padding": 1.5, "flag_confidence": .4,
                      "review_confidence": .1}
            summary = run_analysis(self.image, FakeDetector(), output, config,
                                   {"species": "test", "provenance": "synthetic"}, input_path, weights_path, "cpu")
            self.assertEqual(summary["results"]["crops"]["flagged_ids"], [1])
            self.assertEqual(summary["results"]["full"]["flagged_ids"], [2])
            self.assertTrue((output / "report.html").is_file())
            self.assertEqual(json.loads((output / "sample.json").read_text())["input"]["width"], 200)

    def test_empty_image_does_not_call_crop_detector(self):
        class NeverCalledDetector:
            def predict(self, images):
                raise AssertionError("No crops should be sent for inference")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = np.full((40, 60, 3), 255, dtype=np.uint8)
            input_path, weights_path = root / "input.png", root / "weights.pt"
            Image.fromarray(image).save(input_path)
            weights_path.write_bytes(b"fake checkpoint")
            output = root / "run"
            output.mkdir()
            config = {"mode": "crops", "min_area_fraction": 0.001, "border_fraction": .01,
                      "distance_threshold": None, "crop_padding": 1.5, "flag_confidence": .4,
                      "review_confidence": .1}
            summary = run_analysis(image, NeverCalledDetector(), output, config,
                                   {"species": "test", "provenance": "synthetic"}, input_path, weights_path, "cpu")
            self.assertEqual(summary["results"]["crops"]["grain_candidates"], 0)
            self.assertIsNone(summary["results"]["crops"]["flagged_percentage"])


class EvaluationTests(unittest.TestCase):
    """Check metrics against hand-counted centre and label examples."""

    def setUp(self):
        self.photo = {"sample_json": "run/sample.json", "species": "pea", "physical_set_id": "pea-1",
                      "split": "final", "provenance": "natural", "manual_total": 3, "damage_complete": True,
                      "grains": [{"x": 2, "y": 2, "status": "hole"},
                                 {"x": 3, "y": 2, "status": "no_hole"},
                                 {"x": 8, "y": 2, "status": "hole"}]}
        self.labels = np.zeros((10, 12), dtype=np.uint16)
        self.labels[1:4, 1:5] = 1
        self.labels[1:4, 7:10] = 2
        self.labels[6:8, 9:11] = 3
        self.sample = {"input": {"width": 12, "height": 10},
                       "components": [{"id": 1, "centroid": [2, 2]}, {"id": 2, "centroid": [8, 2]},
                                      {"id": 3, "centroid": [9, 6]}],
                       "results": {"crops": {"flagged_ids": [1, 3]}}}

    def test_merge_extra_and_damage_metrics(self):
        check_manifest([self.photo])
        row = evaluate_photo(self.photo, self.sample, self.labels, "crops")
        self.assertEqual((row["matched_grains"], row["missed_grains"], row["merged_instances"]), (2, 1, 1))
        self.assertEqual(row["extra_or_split_instances"], 1)
        self.assertEqual((row["tp"], row["fp"], row["fn"]), (1, 1, 1))
        self.assertEqual(row["percentage_point_error"], 0)
        self.assertEqual(summarize_group([row])["count_mae"], 0)

    def test_incomplete_truth_and_split_leakage(self):
        photo = self.photo | {"damage_complete": False, "grains": []}
        check_manifest([photo])
        self.assertIsNone(evaluate_photo(photo, self.sample, self.labels, "crops")["tp"])
        with self.assertRaisesRegex(ValueError, "cross"):
            check_manifest([photo, photo | {"split": "development"}])
        with self.assertRaisesRegex(ValueError, "Complete damage"):
            check_manifest([photo | {"damage_complete": True}])

    def test_zero_denominators(self):
        photo = self.photo | {"manual_total": 0, "grains": [], "damage_complete": True}
        sample = self.sample | {"components": [], "results": {"crops": {"flagged_ids": []}}}
        check_manifest([photo])
        row = evaluate_photo(photo, sample, self.labels * 0, "crops")
        self.assertIsNone(row["predicted_percentage"])
        self.assertIsNone(row["true_percentage"])
        self.assertIsNone(row["f1"])

    def test_identical_input_bytes_cannot_cross_splits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photos = []
            for split in ("development", "final"):
                folder = root / split
                folder.mkdir()
                Image.fromarray(self.labels).save(folder / "instances.png")
                sample = self.sample | {"metadata": {"species": "pea", "provenance": "natural"},
                                        "checkpoint": {"sha256": "weights"}, "configuration": {},
                                        "input": self.sample["input"] | {"sha256": "same-image"}}
                (folder / "sample.json").write_text(json.dumps(sample))
                photos.append(self.photo | {"sample_json": f"{split}/sample.json", "split": split,
                                            "physical_set_id": split})
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"photos": photos}))
            with self.assertRaisesRegex(ValueError, "identical input"):
                evaluate_manifest(manifest, "crops")


if __name__ == "__main__":
    unittest.main()
