import json
import tempfile
import unittest
from pathlib import Path

from ai_sankalp.config_io import load_config, load_lesson_input
from ai_sankalp.models import LessonValidationError
from ai_sankalp.package import PackageValidationError

ROOT = Path(__file__).resolve().parents[1]


class LoadLessonInputTests(unittest.TestCase):
    def test_package_input_autodetected(self):
        path = ROOT / "examples" / "arrays_in_cpp" / "lesson_package.json"
        loaded = load_lesson_input(path)
        self.assertEqual(path.resolve(), loaded.package_path)
        self.assertEqual("arrays_in_cpp", loaded.lesson.slug)
        self.assertEqual("futuristic_array", loaded.lesson.visual_template)
        self.assertEqual(load_config(ROOT / "examples" / "arrays_in_cpp" / "config.json"), loaded.lesson)

    def test_reduced_config_has_no_package(self):
        loaded = load_lesson_input(ROOT / "examples" / "python_for_loops.json")
        self.assertIsNone(loaded.package)
        self.assertIsNone(loaded.package_path)
        self.assertEqual("python_for_loops", loaded.lesson.slug)

    def test_invalid_package_raises_package_error(self):
        data = json.loads((ROOT / "examples" / "arrays_in_cpp" / "lesson_package.json").read_text())
        del data["slug"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lesson_package.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(PackageValidationError) as ctx:
                load_lesson_input(path)
            self.assertIn("slug: is required", str(ctx.exception))

    def test_missing_file(self):
        with self.assertRaises(LessonValidationError):
            load_lesson_input(ROOT / "examples" / "does_not_exist.json")


if __name__ == "__main__":
    unittest.main()
