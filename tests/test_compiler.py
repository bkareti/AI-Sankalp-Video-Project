import dataclasses
import hashlib
import json
import py_compile
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    import yaml
except ImportError:  # PyYAML is optional; JSON packages still work
    yaml = None

from ai_sankalp.compiler import COMPILER_VERSION, PackageCompiler, canonical_sha256
from ai_sankalp.config_io import load_config
from ai_sankalp.generator import LessonGenerator, SceneSyntaxError
from ai_sankalp.models import LessonConfig
from ai_sankalp.package import PackageValidationError, load_package, package_to_lesson, select_visual_template
from ai_sankalp.template_registry import TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
ARRAYS = "arrays_in_cpp"
LOOPS = "python_for_loops"
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def make_root(directory: str, *slugs: str) -> Path:
    """A throwaway project root with the scene template and the named fixture packages."""
    root = Path(directory).resolve()  # the compiler resolves its root (macOS /var is a symlink)
    (root / "templates").mkdir()
    shutil.copy(ROOT / "templates" / "generated_scene.py.tmpl", root / "templates")
    for slug in slugs:
        target = root / "examples" / slug
        target.mkdir(parents=True)
        shutil.copy(ROOT / "examples" / slug / "lesson_package.json", target)
    return root


def package_path(root: Path, slug: str) -> Path:
    return root / "examples" / slug / "lesson_package.json"


def edit_package(root: Path, slug: str, mutate) -> None:
    path = package_path(root, slug)
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data), encoding="utf-8")


def outputs(root: Path, slug: str):
    return (
        root / "generated" / "configs" / f"{slug}.json",
        root / "generated" / "scenes" / f"{slug}.py",
        root / "generated" / "scenes" / f"{slug}.compile.json",
    )


class CompileFixtureTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = make_root(directory.name, ARRAYS, LOOPS)

    def compile(self, slug, **options):
        return PackageCompiler(self.root).compile(package_path(self.root, slug), **options)

    def test_cpp_package_compiles_to_config_scene_and_metadata(self):
        compiled = self.compile(ARRAYS)
        config, scene, metadata = outputs(self.root, ARRAYS)
        for path in (config, scene, metadata):
            self.assertTrue(path.exists(), path)
        self.assertEqual((config, scene), (compiled.generated.config_path, compiled.generated.scene_path))
        self.assertEqual(metadata, compiled.metadata_path)
        py_compile.compile(str(scene), cfile=str(self.root / "scene.pyc"), doraise=True)
        self.assertIn("class ArraysInCppScene(FuturisticArrayLesson)", scene.read_text(encoding="utf-8"))
        self.assertEqual("futuristic_array", load_config(config).visual_template)
        self.assertEqual(compiled.metadata, json.loads(metadata.read_text(encoding="utf-8")))

    def test_python_package_compiles_with_the_standard_template(self):
        compiled = self.compile(LOOPS)
        _config, scene, metadata = outputs(self.root, LOOPS)
        py_compile.compile(str(scene), cfile=str(self.root / "scene.pyc"), doraise=True)
        self.assertIn("class PythonForLoopsScene(ConfigDrivenLesson)", scene.read_text(encoding="utf-8"))
        self.assertTrue(metadata.exists())
        self.assertEqual("standard", compiled.metadata["template"]["name"])
        self.assertEqual("standard_script", compiled.metadata["narration"]["source"])
        sections = compiled.metadata["plan"]
        self.assertEqual(len(compiled.lesson.sections), len(sections))
        self.assertEqual({"section", "visual"}, set(sections[0]))

    def test_config_is_the_packages_reduced_config(self):
        for slug in (ARRAYS, LOOPS):
            compiled = self.compile(slug)
            package = json.loads(package_path(self.root, slug).read_text(encoding="utf-8"))
            self.assertEqual(package_to_lesson(package), load_config(compiled.generated.config_path))

    def test_metadata_records_the_template_and_what_chose_it(self):
        metadata = self.compile(ARRAYS).metadata
        self.assertEqual(
            {
                "name": "futuristic_array",
                "selected_by": "generator_compatibility.visual_template",
                "scene_module": "ai_sankalp.futuristic_array_scene",
                "scene_base": "FuturisticArrayLesson",
            },
            metadata["template"],
        )
        self.assertEqual(COMPILER_VERSION, metadata["compiler_version"])
        self.assertEqual(ARRAYS, metadata["slug"])
        self.assertEqual("examples/arrays_in_cpp/lesson_package.json", metadata["source"]["path"])

    def test_metadata_records_explicit_primitives_per_scene(self):
        plan = self.compile(ARRAYS).metadata["plan"]
        package = json.loads(package_path(self.root, ARRAYS).read_text(encoding="utf-8"))
        self.assertEqual([scene["id"] for scene in package["scenes"]], [entry["scene_id"] for entry in plan])
        by_id = {entry["scene_id"]: entry for entry in plan}
        trace = by_id["scene_06_trace"]
        self.assertEqual("visual_trace", trace["type"])
        self.assertEqual(["loop_trace"], [visual["type"] for visual in trace["visuals"]])
        self.assertEqual({"scenes[].visuals"}, {visual["selected_by"] for visual in trace["visuals"]})
        self.assertGreater(trace["visuals"][0]["beats"], 0)
        self.assertIn("asset_trace_marker", trace["visual_objects"])
        self.assertEqual(["token_breakdown", "index_access"], [v["type"] for v in by_id["scene_04_indexing"]["visuals"]])

    def test_metadata_records_default_primitives_when_a_scene_has_no_visuals(self):
        def strip_intro_visuals(data):
            del data["scenes"][0]["visuals"]

        edit_package(self.root, ARRAYS, strip_intro_visuals)
        intro = self.compile(ARRAYS).metadata["plan"][0]
        self.assertEqual("intro", intro["type"])
        self.assertEqual(["title_card"], [visual["type"] for visual in intro["visuals"]])
        self.assertEqual(
            ["default for scene type 'intro'"], [visual["selected_by"] for visual in intro["visuals"]]
        )

    def test_narration_segments_are_the_caption_inputs(self):
        metadata = self.compile(ARRAYS).metadata
        package = json.loads(package_path(self.root, ARRAYS).read_text(encoding="utf-8"))
        self.assertEqual("package_scenes", metadata["narration"]["source"])
        self.assertEqual(
            [{"id": scene["id"], "text": scene["voiceover"]} for scene in package["scenes"]],
            metadata["narration"]["segments"],
        )
        self.assertGreater(metadata["captions"]["estimated_cue_count"], 10)
        self.assertGreater(metadata["captions"]["estimated_seconds"], 30)

    def test_compiling_does_not_write_captions_or_videos(self):
        self.compile(ARRAYS)
        self.assertFalse((self.root / "generated" / "videos").exists())

    def test_standard_template_warns_that_scene_visuals_are_not_drawn(self):
        def force_standard(data):
            data["visual_template"] = "standard"
            data["generator_compatibility"]["visual_template"] = "standard"

        edit_package(self.root, ARRAYS, force_standard)
        metadata = self.compile(ARRAYS).metadata
        self.assertEqual("standard", metadata["template"]["name"])
        self.assertEqual(1, len(metadata["warnings"]))
        self.assertIn("scenes[].visuals", metadata["warnings"][0])
        self.assertEqual([], self.compile(LOOPS).metadata["warnings"])


class DeterminismTests(unittest.TestCase):
    def compile_in_new_root(self, slug, **options):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = make_root(directory.name, slug)
        PackageCompiler(root).compile(package_path(root, slug), **options)
        return root, {path.name: path.read_bytes() for path in outputs(root, slug)}

    def test_unchanged_package_gives_byte_identical_outputs(self):
        for slug in (ARRAYS, LOOPS):
            with self.subTest(slug=slug):
                directory = tempfile.TemporaryDirectory()
                self.addCleanup(directory.cleanup)
                root = make_root(directory.name, slug)
                compiler = PackageCompiler(root)
                compiler.compile(package_path(root, slug))
                first = [path.read_bytes() for path in outputs(root, slug)]
                compiler.compile(package_path(root, slug))
                self.assertEqual(first, [path.read_bytes() for path in outputs(root, slug)])

    def test_outputs_do_not_depend_on_where_the_project_lives(self):
        root_a, first = self.compile_in_new_root(ARRAYS)
        root_b, second = self.compile_in_new_root(ARRAYS)
        self.assertNotEqual(root_a, root_b)
        self.assertEqual(first, second)
        for name, content in first.items():
            text = content.decode("utf-8")
            self.assertNotIn(str(root_a), text, name)
            self.assertNotIn(str(root_a.resolve()), text, name)

    def test_metadata_has_no_timestamps_or_random_ids(self):
        _root, written = self.compile_in_new_root(ARRAYS)
        text = written["arrays_in_cpp.compile.json"].decode("utf-8")
        self.assertIsNone(TIMESTAMP.search(text))
        self.assertTrue(text.endswith("}\n"))

    def test_a_changed_package_changes_the_hashes(self):
        _root, before = self.compile_in_new_root(ARRAYS)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = make_root(directory.name, ARRAYS)
        edit_package(root, ARRAYS, lambda data: data.update(title=data["title"] + " Updated"))
        PackageCompiler(root).compile(package_path(root, ARRAYS))
        after = {path.name: path.read_bytes() for path in outputs(root, ARRAYS)}
        old, new = (json.loads(group["arrays_in_cpp.compile.json"]) for group in (before, after))
        self.assertNotEqual(old["source"]["sha256"], new["source"]["sha256"])
        self.assertNotEqual(old["compile_key"], new["compile_key"])
        self.assertNotEqual(old["outputs"]["config"]["sha256"], new["outputs"]["config"]["sha256"])
        # The scene entry point does not embed lesson text, so it is unchanged.
        self.assertEqual(old["outputs"]["scene"]["sha256"], new["outputs"]["scene"]["sha256"])

    def test_formatting_and_key_order_do_not_change_the_hashes(self):
        _root, before = self.compile_in_new_root(ARRAYS)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = make_root(directory.name, ARRAYS)
        path = package_path(root, ARRAYS)
        data = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(json.dumps(data, indent=4, sort_keys=True), encoding="utf-8")
        PackageCompiler(root).compile(path)
        after = {item.name: item.read_bytes() for item in outputs(root, ARRAYS)}
        self.assertEqual(before, after)

    def test_output_hashes_describe_the_files_written(self):
        _root, written = self.compile_in_new_root(ARRAYS)
        metadata = json.loads(written["arrays_in_cpp.compile.json"])
        config_bytes, scene_bytes = written["arrays_in_cpp.json"], written["arrays_in_cpp.py"]
        self.assertEqual(hashlib.sha256(config_bytes).hexdigest(), metadata["outputs"]["config"]["sha256"])
        self.assertEqual(hashlib.sha256(scene_bytes).hexdigest(), metadata["outputs"]["scene"]["sha256"])

    def test_canonical_hash_ignores_key_order(self):
        self.assertEqual(canonical_sha256({"a": 1, "b": [1, 2]}), canonical_sha256({"b": [1, 2], "a": 1}))
        self.assertNotEqual(canonical_sha256({"a": 1}), canonical_sha256({"a": 2}))

    def test_silent_preview_is_recorded_and_changes_the_key(self):
        _root, loud = self.compile_in_new_root(LOOPS)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = make_root(directory.name, LOOPS)
        compiled = PackageCompiler(root).compile(package_path(root, LOOPS), voiceover_enabled=False)
        self.assertEqual({"voiceover_enabled": False}, compiled.metadata["options"])
        self.assertFalse(compiled.lesson.voiceover.enabled)
        self.assertFalse(load_config(compiled.generated.config_path).voiceover.enabled)
        self.assertNotEqual(json.loads(loud["python_for_loops.compile.json"])["compile_key"], compiled.metadata["compile_key"])


class CompileKeyTests(unittest.TestCase):
    """compile_key names everything that changes the outputs."""

    def key_in_new_root(self, slug=LOOPS, template_bytes=None):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = make_root(directory.name, slug)
        if template_bytes is not None:
            (root / "templates" / "generated_scene.py.tmpl").write_bytes(template_bytes(root))
        compiled = PackageCompiler(root).compile(package_path(root, slug))
        return compiled.metadata, compiled.generated.scene_path.read_bytes()

    def test_template_routing_is_part_of_the_key(self):
        before, _scene = self.key_in_new_root()
        rerouted = dataclasses.replace(TEMPLATES["standard"], scene_base="OtherLessonBase")
        with mock.patch.dict(TEMPLATES, {"standard": rerouted}):
            after, scene = self.key_in_new_root()
        self.assertIn(b"OtherLessonBase", scene)
        self.assertNotEqual(before["compile_key"], after["compile_key"])

    def test_crlf_checkout_of_the_template_changes_nothing(self):
        lf_metadata, lf_scene = self.key_in_new_root()

        def crlf(root):
            text = (ROOT / "templates" / "generated_scene.py.tmpl").read_text(encoding="utf-8")
            return text.replace("\n", "\r\n").encode("utf-8")

        crlf_metadata, crlf_scene = self.key_in_new_root(template_bytes=crlf)
        self.assertEqual(lf_scene, crlf_scene)
        self.assertEqual(lf_metadata["scene_template_sha256"], crlf_metadata["scene_template_sha256"])
        self.assertEqual(lf_metadata["compile_key"], crlf_metadata["compile_key"])


class OutOfRootPackageTests(unittest.TestCase):
    def test_package_outside_the_project_is_recorded_by_absolute_path(self):
        """Known limitation: a package outside the root cannot be repo-relative."""
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as elsewhere:
            root = make_root(directory)
            outside = make_root(elsewhere, LOOPS)
            compiled = PackageCompiler(root).compile(package_path(outside, LOOPS))
            absolute = str(package_path(outside, LOOPS).resolve())
            self.assertEqual(absolute, compiled.metadata["source"]["path"])
            self.assertIn(absolute, compiled.generated.scene_path.read_text(encoding="utf-8"))
            py_compile.compile(str(compiled.generated.scene_path), cfile=str(root / "scene.pyc"), doraise=True)


@unittest.skipIf(yaml is None, "PyYAML is not installed")
class YamlPackageTests(unittest.TestCase):
    """A YAML package generated before the compiler existed, so it must still."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = make_root(directory.name, LOOPS)
        data = json.loads(package_path(self.root, LOOPS).read_text(encoding="utf-8"))
        self.yaml_path = self.root / "examples" / LOOPS / "lesson_package.yaml"
        self.yaml_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
        self.package = data

    def test_load_package_reads_yaml(self):
        self.assertEqual(self.package, load_package(self.yaml_path))

    def test_yaml_package_compiles_to_the_same_outputs_as_json(self):
        from_json = PackageCompiler(self.root).compile(package_path(self.root, LOOPS))
        json_config = from_json.generated.config_path.read_bytes()
        from_yaml = PackageCompiler(self.root).compile(self.yaml_path)
        self.assertEqual(json_config, from_yaml.generated.config_path.read_bytes())
        self.assertEqual("standard", from_yaml.metadata["template"]["name"])
        self.assertEqual(self.package["slug"], from_yaml.metadata["slug"])
        self.assertEqual(from_json.metadata["source"]["sha256"], from_yaml.metadata["source"]["sha256"])

    def test_yaml_that_is_not_an_object_is_rejected(self):
        self.yaml_path.write_text("- just\n- a list\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "must be an object"):
            load_package(self.yaml_path)


class CompileFailureTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = make_root(directory.name, ARRAYS)

    def test_invalid_package_fails_before_anything_is_written(self):
        edit_package(self.root, ARRAYS, lambda data: data["scenes"][0].pop("voiceover"))
        with self.assertRaises(PackageValidationError) as ctx:
            PackageCompiler(self.root).compile(package_path(self.root, ARRAYS))
        self.assertIn("scenes[0]", str(ctx.exception))
        self.assertFalse((self.root / "generated").exists())

    def test_template_with_a_syntax_error_fails_before_anything_is_written(self):
        template = self.root / "templates" / "generated_scene.py.tmpl"
        template.write_text(template.read_text(encoding="utf-8") + "\nclass Broken(:\n", encoding="utf-8")
        with self.assertRaisesRegex(SceneSyntaxError, r"arrays_in_cpp\.py has a syntax error at line \d+"):
            PackageCompiler(self.root).compile(package_path(self.root, ARRAYS))
        self.assertFalse((self.root / "generated").exists())

    def test_missing_package_is_a_validation_error(self):
        with self.assertRaisesRegex(ValueError, "lesson package not found"):
            PackageCompiler(self.root).compile(self.root / "examples" / "nope" / "lesson_package.json")


class ReducedConfigTests(unittest.TestCase):
    def reduced_lesson(self) -> LessonConfig:
        return load_config(ROOT / "examples" / "python_for_loops.json")

    def test_reduced_config_still_generates_without_compiler_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory)
            lesson = self.reduced_lesson()
            result = LessonGenerator(root).generate(lesson)
            self.assertTrue(result.config_path.exists())
            self.assertTrue(result.scene_path.exists())
            self.assertFalse(outputs(root, lesson.slug)[2].exists())

    def test_reduced_generation_removes_stale_compiler_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_root(directory, LOOPS)
            PackageCompiler(root).compile(package_path(root, LOOPS))
            metadata = outputs(root, LOOPS)[2]
            self.assertTrue(metadata.exists())
            LessonGenerator(root).generate(self.reduced_lesson())
            self.assertFalse(metadata.exists())


class TemplateSelectionTests(unittest.TestCase):
    def package(self):
        return json.loads((ROOT / "examples" / ARRAYS / "lesson_package.json").read_text(encoding="utf-8"))

    def test_generator_compatibility_wins(self):
        package = self.package()
        package["visual_template"] = "standard"
        self.assertEqual(
            ("futuristic_array", "generator_compatibility.visual_template"), select_visual_template(package)
        )

    def test_top_level_template_is_next(self):
        package = self.package()
        package["generator_compatibility"].pop("visual_template")
        self.assertEqual(("futuristic_array", "visual_template"), select_visual_template(package))

    def test_standard_is_the_default(self):
        package = self.package()
        package["generator_compatibility"].pop("visual_template")
        package.pop("visual_template")
        self.assertEqual(("standard", "default"), select_visual_template(package))


if __name__ == "__main__":
    unittest.main()
