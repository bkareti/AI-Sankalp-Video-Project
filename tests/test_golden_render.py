import json
import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from ai_sankalp.qa import golden

ROOT = Path(__file__).resolve().parents[1]
SLUG = "arrays_in_cpp"


class PlanGoldenTests(unittest.TestCase):
    def test_flagship_plan_matches_golden(self):
        package = json.loads((ROOT / "examples" / SLUG / "lesson_package.json").read_text(encoding="utf-8"))
        expected = json.loads(golden.golden_path(SLUG, "plan").read_text(encoding="utf-8"))
        self.assertEqual(
            expected, golden.plan_snapshot(package),
            "The flagship plan changed. If intentional, run: "
            "python -m ai_sankalp.qa.golden update-plan --slug arrays_in_cpp",
        )
        self.assertEqual(10, expected["scene_count"])


class HashTests(unittest.TestCase):
    def image(self, box):
        image = Image.new("RGB", (160, 90), "black")
        ImageDraw.Draw(image).rectangle(box, fill="white")
        return image

    def test_dhash_and_hamming_on_synthetic_images(self):
        left = golden.dhash(self.image((10, 10, 60, 80)))
        nearly = golden.dhash(self.image((11, 10, 61, 80)))
        right = golden.dhash(self.image((100, 10, 150, 80)))
        self.assertEqual(16, len(left))
        self.assertEqual(0, golden.hamming(left, left))
        self.assertLessEqual(golden.hamming(left, nearly), golden.MAX_HAMMING)
        self.assertGreater(golden.hamming(left, right), golden.MAX_HAMMING)

    def test_frame_times_are_evenly_spaced(self):
        self.assertEqual([5.0, 15.0, 25.0, 35.0, 45.0, 55.0, 65.0, 75.0, 85.0, 95.0], golden.frame_times(100.0))

    def test_compare_frames(self):
        snapshot = {"duration_seconds": 100.0, "max_hamming": 10, "duration_tolerance": 0.1,
                    "frames": [{"t": 5.0, "dhash": "0" * 16}]}
        self.assertEqual([], golden.compare_frames(snapshot, dict(snapshot)))
        changed = dict(snapshot, duration_seconds=130.0, frames=[{"t": 5.0, "dhash": "f" * 16}])
        problems = golden.compare_frames(snapshot, changed)
        self.assertEqual(2, len(problems))


@unittest.skipUnless(os.environ.get("AI_SANKALP_GOLDEN_RENDER") == "1",
                     "set AI_SANKALP_GOLDEN_RENDER=1 to render and compare frames (slow; needs Manim and ffmpeg)")
class FrameGoldenTests(unittest.TestCase):
    def test_flagship_frames_match_golden(self):
        expected = json.loads(golden.golden_path(SLUG, "frames").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            current = golden.frames_snapshot(golden.render_silent_video(SLUG, work), work / "frames")
        self.assertEqual([], golden.compare_frames(expected, current))


if __name__ == "__main__":
    unittest.main()
