import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

from ai_sankalp import brand
from ai_sankalp.caption_burn import (
    VIDEO_SIZES, CaptionBurnError, build_burn_command, burn_captions, render_cue_image,
)
from ai_sankalp.captions import Cue

CUES = [Cue(0.0, 1.5, "Welcome to AI Sankalp."), Cue(1.6, 4.0, "Imagine you have the marks of five\nstudents, and you want to keep all of them")]


class CueImageTests(unittest.TestCase):
    def test_cue_image_alpha_bbox_inside_caption_band(self):
        for quality in ("low", "high"):
            size = VIDEO_SIZES[quality]
            with self.subTest(quality=quality), tempfile.TemporaryDirectory() as directory:
                path = render_cue_image(CUES[1], size, Path(directory) / "cue.png", brand.caption_font_file())
                with Image.open(path) as image:
                    self.assertEqual(size, image.size)
                    left, top, right, bottom = image.getchannel("A").getbbox()
                band_top, band_bottom = brand.caption_band_pixels(size[1])
                self.assertGreaterEqual(top, band_top)
                self.assertLessEqual(bottom, band_bottom)
                self.assertGreater(left, 0)
                self.assertLess(right, size[0])

    def test_default_font_fallback_still_fits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = render_cue_image(CUES[1], (854, 480), Path(directory) / "cue.png", font_file=None)
            with Image.open(path) as image:
                _, top, _, bottom = image.getchannel("A").getbbox()
            band_top, band_bottom = brand.caption_band_pixels(480)
            self.assertTrue(band_top <= top and bottom <= band_bottom)


class BurnCommandTests(unittest.TestCase):
    def test_command_has_overlay_per_cue_and_keeps_audio(self):
        command = build_burn_command("ffmpeg", Path("in.mp4"), [Path("a.png"), Path("b.png")], CUES, Path("out.mp4"))
        graph = command[command.index("-filter_complex") + 1]
        self.assertEqual(2, graph.count("overlay="))
        self.assertIn("enable='between(t,0.000,1.500)'", graph)
        self.assertIn("[v1][2:v]overlay", graph)
        self.assertEqual("[v2]", command[command.index("-map") + 1])
        self.assertIn("0:a?", command)
        self.assertEqual("out.mp4", command[-1])

    def test_burn_failure_raises_render_error(self):
        failed = subprocess.CompletedProcess([], 1, stdout="", stderr="Invalid filtergraph")
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch("ai_sankalp.caption_burn.shutil.which", return_value="/usr/bin/ffmpeg"):
            with self.assertRaisesRegex(CaptionBurnError, "Invalid filtergraph"):
                burn_captions(Path(directory) / "in.mp4", CUES, Path(directory) / "out.mp4",
                              run=lambda *args, **kwargs: failed)

    def test_burn_requires_cues_and_ffmpeg(self):
        with self.assertRaises(CaptionBurnError):
            burn_captions(Path("in.mp4"), [], Path("out.mp4"))
        with mock.patch("ai_sankalp.caption_burn.shutil.which", return_value=None):
            with self.assertRaisesRegex(CaptionBurnError, "ffmpeg is missing"):
                burn_captions(Path("in.mp4"), CUES, Path("out.mp4"))


if __name__ == "__main__":
    unittest.main()
