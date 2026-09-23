import tempfile
import unittest
from pathlib import Path

from ai_sankalp.futuristic_array_scene import resolve_package_path


class ResolvePackagePathTests(unittest.TestCase):
    def test_prefers_generated_package_when_present(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated = root / "generated" / "packages" / "arrays_in_cpp"
            generated.mkdir(parents=True)
            (generated / "lesson_package.json").write_text("{}", encoding="utf-8")
            example = root / "examples" / "arrays_in_cpp"
            example.mkdir(parents=True)
            (example / "lesson_package.json").write_text("{}", encoding="utf-8")

            resolved = resolve_package_path(root, "arrays_in_cpp")
            self.assertEqual(generated / "lesson_package.json", resolved)

    def test_falls_back_to_tracked_example_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            example = root / "examples" / "arrays_in_cpp"
            example.mkdir(parents=True)
            (example / "lesson_package.json").write_text("{}", encoding="utf-8")

            resolved = resolve_package_path(root, "arrays_in_cpp")
            self.assertEqual(example / "lesson_package.json", resolved)

    def test_raises_actionable_error_when_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError) as ctx:
                resolve_package_path(root, "missing_topic")
            self.assertIn("missing_topic", str(ctx.exception))

    def test_flagship_example_package_is_tracked_in_repo(self):
        # A clean clone has no generated/packages output, so the flagship
        # sample must resolve from the tracked examples/ fixture alone.
        project_root = Path(__file__).resolve().parents[1]
        example_package = project_root / "examples" / "arrays_in_cpp" / "lesson_package.json"
        self.assertTrue(example_package.exists())


if __name__ == "__main__":
    unittest.main()
