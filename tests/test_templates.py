import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from ai_sankalp.generator import LessonGenerator, check_template_prerequisites
from ai_sankalp.models import LessonConfig, LessonValidationError
from ai_sankalp.package import PackageValidationError

ROOT = Path(__file__).resolve().parents[1]
ARRAYS_PACKAGE = ROOT / "examples" / "arrays_in_cpp" / "lesson_package.json"


def make_root(directory: str) -> Path:
    root = Path(directory)
    (root / "templates").mkdir()
    shutil.copy(ROOT / "templates" / "generated_scene.py.tmpl", root / "templates")
    return root


def lesson(**overrides) -> LessonConfig:
    data = {
        "topic": "Arrays in C++", "title": "C++ Arrays", "language": "C++",
        "sections": [{"title": "Index", "bullets": ["Indexes begin at zero."]}],
        "code_example": "int values[2] = {1, 2};",
        "output_video_name": "arrays_in_cpp",
        "visual_template": "futuristic_array",
        "voiceover": False,
    }
    data.update(overrides)
    return LessonConfig.from_dict(data)


def copy_package(root: Path, slug: str = "arrays_in_cpp", mutate=None) -> Path:
    target = root / "examples" / slug / "lesson_package.json"
    target.parent.mkdir(parents=True)
    data = json.loads(ARRAYS_PACKAGE.read_text(encoding="utf-8"))
    if mutate:
        mutate(data)
    target.write_text(json.dumps(data), encoding="utf-8")
    return target


class FuturisticPrerequisiteTests(unittest.TestCase):
    def test_futuristic_without_package_fails_before_writing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)
            with self.assertRaises(LessonValidationError) as ctx:
                LessonGenerator(root).generate(lesson())
            message = str(ctx.exception)
            self.assertIn("needs a rich lesson package", message)
            self.assertIn("examples/arrays_in_cpp/lesson_package.json", message)
            self.assertIn("generated/packages/arrays_in_cpp/lesson_package.json", message)
            self.assertIn("visual_template 'standard'", message)
            self.assertFalse((root / "generated" / "configs").exists())
            self.assertFalse((root / "generated" / "scenes").exists())

    def test_non_array_topics_render_from_package_data(self):
        # #7 replaced the temporary C++-arrays-only rule with capability checks:
        # any topic works when its package scenes plan into valid primitives.
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)

            def strip_visuals(data):
                for scene in data["scenes"]:
                    scene.pop("visuals", None)

            copy_package(root, "sql_joins", mutate=strip_visuals)
            sql = lesson(topic="SQL joins", title="Joins", language="SQL", output_video_name="sql_joins")
            result = LessonGenerator(root).generate(sql)
            self.assertTrue(result.scene_path.exists())

    def test_invalid_primitive_params_fail_with_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)
            copy_package(root, mutate=lambda data: data["scenes"][5]["visuals"][0].update(values=[]))
            with self.assertRaises(LessonValidationError) as ctx:
                LessonGenerator(root).generate(lesson())
            self.assertIn("scenes[5].visuals[0]: values must have 1 to 8 items", str(ctx.exception))
            self.assertFalse((root / "generated" / "scenes").exists())

    def test_fewer_scenes_still_generate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)

            def keep_three(data):
                data["scenes"] = data["scenes"][:3]
                data["voiceover_segments"] = data["voiceover_segments"][:3]

            copy_package(root, mutate=keep_three)
            self.assertTrue(LessonGenerator(root).generate(lesson()).scene_path.exists())

    def test_invalid_package_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)
            copy_package(root, mutate=lambda data: data["scenes"][0].pop("voiceover"))
            with self.assertRaises(PackageValidationError) as ctx:
                LessonGenerator(root).generate(lesson())
            self.assertIn("scenes[0].voiceover: is required", str(ctx.exception))
            self.assertFalse((root / "generated" / "scenes").exists())

    def test_valid_example_package_fallback_generates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)
            package = copy_package(root)
            result = LessonGenerator(root).generate(lesson())
            self.assertEqual(package.resolve(), result.package_path.resolve())
            source = result.scene_path.read_text(encoding="utf-8")
            self.assertIn("LESSON_PACKAGE_PATH = None", source)

    def test_explicit_package_is_pinned_repo_relative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)
            package = copy_package(root, "custom_dir")
            result = LessonGenerator(root).generate(lesson(), package_path=package)
            source = result.scene_path.read_text(encoding="utf-8")
            self.assertIn("LESSON_PACKAGE_PATH = PROJECT_ROOT / 'examples/custom_dir/lesson_package.json'", source)

    def test_standard_lessons_need_no_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)
            standard = lesson(visual_template="standard", topic="SQL joins", language="SQL")
            self.assertIsNone(check_template_prerequisites(standard, root))
            result = LessonGenerator(root).generate(standard)
            self.assertIsNone(result.package_path)


class GeneratedSceneCompileTests(unittest.TestCase):
    def test_generated_scenes_py_compile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)
            copy_package(root)
            for item in (lesson(), lesson(visual_template="standard", output_video_name="plain")):
                result = LessonGenerator(root).generate(item)
                py_compile.compile(str(result.scene_path), doraise=True)

    def test_out_of_root_package_compiles_with_absolute_path(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as elsewhere:
            root = make_root(directory)
            outside = copy_package(Path(elsewhere))
            result = LessonGenerator(root).generate(lesson(), package_path=outside)
            source = result.scene_path.read_text(encoding="utf-8")
            self.assertIn(f"LESSON_PACKAGE_PATH = Path({str(outside.resolve())!r})", source)
            py_compile.compile(str(result.scene_path), doraise=True)


if __name__ == "__main__":
    unittest.main()
