import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import app


class CliParserTests(unittest.TestCase):
    def test_generate_no_voiceover_flag_parses(self):
        args = app.build_parser().parse_args(["generate", "--config", "x.json", "--no-voiceover", "--render"])
        self.assertTrue(args.no_voiceover)
        self.assertTrue(args.render)
        args = app.build_parser().parse_args(["generate", "--config", "x.json"])
        self.assertFalse(args.no_voiceover)

    def test_generate_passes_package_path_and_disables_voiceover(self):
        package = Path(app.PROJECT_ROOT) / "examples" / "arrays_in_cpp" / "lesson_package.json"
        with mock.patch.object(app, "generate_and_maybe_render", return_value=0) as run:
            self.assertEqual(0, app.main(["generate", "--config", str(package), "--no-voiceover"]))
        lesson, render, quality, output_dir, package_path, burn = run.call_args[0]
        self.assertFalse(lesson.voiceover.enabled)
        self.assertEqual(package.resolve(), package_path)

    def test_invalid_config_prints_error_not_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "bad.json"
            config.write_text(
                '{"topic": "x", "title": "x", "language": "C", "explanation": ["a"], '
                '"code_example": "x", "output_video_name": "x", "voiceover": {"speed": "fast"}}',
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(1, app.main(["generate", "--config", str(config)]))
            self.assertIn("Error: voiceover.speed must be a number", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
