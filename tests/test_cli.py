import contextlib
import io
import json
import shutil
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


class CliCompileTests(unittest.TestCase):
    """`generate` compiles packages and leaves reduced configs on the original path."""

    def project(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name).resolve()
        (root / "templates").mkdir()
        shutil.copy(Path(app.PROJECT_ROOT) / "templates" / "generated_scene.py.tmpl", root / "templates")
        return root

    def generate(self, root, *argv):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(app, "PROJECT_ROOT", root), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = app.main(["generate", *argv])
        return code, out.getvalue(), err.getvalue()

    def test_package_is_compiled_and_metadata_is_reported(self):
        root = self.project()
        package = Path(app.PROJECT_ROOT) / "examples" / "python_for_loops" / "lesson_package.json"
        code, out, err = self.generate(root, "--config", str(package), "--no-voiceover")
        self.assertEqual((0, ""), (code, err))
        metadata_path = root / "generated" / "scenes" / "python_for_loops.compile.json"
        self.assertIn(f"Metadata: {metadata_path}", out)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual({"voiceover_enabled": False}, metadata["options"])
        config = json.loads((root / "generated" / "configs" / "python_for_loops.json").read_text(encoding="utf-8"))
        self.assertFalse(config["voiceover"]["enabled"])

    def test_reduced_config_does_not_use_the_compiler(self):
        root = self.project()
        reduced = Path(app.PROJECT_ROOT) / "examples" / "python_for_loops.json"
        with mock.patch.object(app.PackageCompiler, "compile") as compile_package:
            code, out, err = self.generate(root, "--config", str(reduced), "--no-voiceover")
        self.assertEqual((0, ""), (code, err))
        compile_package.assert_not_called()
        self.assertNotIn("Metadata:", out)
        self.assertTrue((root / "generated" / "scenes" / "python_for_loops.py").exists())
        self.assertFalse((root / "generated" / "scenes" / "python_for_loops.compile.json").exists())

    def test_broken_template_prints_an_error_and_writes_nothing(self):
        root = self.project()
        template = root / "templates" / "generated_scene.py.tmpl"
        template.write_text("class Broken(:\n", encoding="utf-8")
        package = Path(app.PROJECT_ROOT) / "examples" / "python_for_loops" / "lesson_package.json"
        code, _out, err = self.generate(root, "--config", str(package))
        self.assertEqual(1, code)
        self.assertIn("Error: generated scene generated/scenes/python_for_loops.py has a syntax error", err)
        self.assertFalse((root / "generated" / "scenes").exists())


if __name__ == "__main__":
    unittest.main()
