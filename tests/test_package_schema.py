import copy
import json
import unittest
from pathlib import Path

from ai_sankalp.config_io import load_config
from ai_sankalp.package import (
    PackageValidationError, ensure_valid_package, is_lesson_package, package_to_config_dict,
    package_to_lesson, validate_package,
)
from ai_sankalp.schema_validation import load_schema

ROOT = Path(__file__).resolve().parents[1]
ARRAYS = ROOT / "examples" / "arrays_in_cpp" / "lesson_package.json"
PYTHON = ROOT / "examples" / "python_for_loops" / "lesson_package.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class TrackedPackageTests(unittest.TestCase):
    def test_tracked_packages_validate(self):
        paths = sorted(ROOT.glob("examples/*/lesson_package.json"))
        self.assertIn(ARRAYS, paths)
        self.assertIn(PYTHON, paths)
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertEqual([], [str(issue) for issue in validate_package(load(path))])

    def test_package_to_config_matches_tracked_reduced_config(self):
        pairs = [
            (ARRAYS, ROOT / "examples" / "arrays_in_cpp" / "config.json"),
            (PYTHON, ROOT / "examples" / "python_for_loops.json"),
        ]
        for package_path, config_path in pairs:
            with self.subTest(package=package_path.parent.name):
                self.assertEqual(load_config(config_path), package_to_lesson(load(package_path)))

    def test_conversion_is_byte_deterministic(self):
        first = json.dumps(package_to_config_dict(load(ARRAYS)), ensure_ascii=False)
        second = json.dumps(package_to_config_dict(load(ARRAYS)), ensure_ascii=False)
        self.assertEqual(first, second)
        self.assertEqual(
            ["topic", "title", "language", "sections", "code_example", "summary",
             "output_video_name", "voiceover", "visual_template"],
            list(package_to_config_dict(load(ARRAYS))),
        )

    def test_visual_template_falls_back_to_top_level_then_standard(self):
        package = load(PYTHON)
        package["generator_compatibility"].pop("visual_template")
        package["visual_template"] = "futuristic_array"
        self.assertEqual("futuristic_array", package_to_config_dict(package)["visual_template"])
        package.pop("visual_template")
        self.assertEqual("standard", package_to_config_dict(package)["visual_template"])

    def test_is_lesson_package(self):
        self.assertTrue(is_lesson_package(load(ARRAYS)))
        self.assertFalse(is_lesson_package(load(ROOT / "examples" / "python_for_loops.json")))
        reduced_with_note = dict(load(ROOT / "examples" / "python_for_loops.json"), scenes=[])
        self.assertFalse(is_lesson_package(reduced_with_note))

    def test_shared_defs_match_reduced_schema(self):
        reduced = load_schema("lesson.schema.json")["$defs"]
        package = load_schema("lesson_package.schema.json")["$defs"]
        for name in ("section", "voiceover", "visual"):
            self.assertEqual(reduced[name], package[name], name)


class InvalidPackageTests(unittest.TestCase):
    def assert_issue(self, package, path, fragment):
        issues = validate_package(package)
        matching = [issue for issue in issues if issue.path == path and fragment in issue.message]
        self.assertTrue(matching, f"expected {path}: {fragment}; got {[str(i) for i in issues]}")

    def test_missing_scene_voiceover(self):
        package = load(ARRAYS)
        del package["scenes"][3]["voiceover"]
        self.assert_issue(package, "scenes[3].voiceover", "is required")

    def test_unknown_segment_scene_id(self):
        package = load(ARRAYS)
        package["voiceover_segments"][2]["scene_id"] = "scene_99"
        self.assert_issue(package, "voiceover_segments[2].scene_id", "'scene_99' does not match any scenes[].id")

    def test_segment_text_must_match_scene(self):
        package = load(ARRAYS)
        package["voiceover_segments"][0]["text"] = "Different words."
        self.assert_issue(package, "voiceover_segments[0].text", "must exactly match")

    def test_unknown_code_example_and_asset(self):
        package = load(ARRAYS)
        package["scenes"][4]["code_example_ids"] = ["code_99"]
        package["scenes"][1]["visual_objects"].append("asset_missing")
        self.assert_issue(package, "scenes[4].code_example_ids[0]", "does not match any code_examples[].id")
        self.assert_issue(package, "scenes[1].visual_objects[3]", "does not match any assets[].id")

    def test_duplicate_scene_id(self):
        package = load(ARRAYS)
        package["scenes"][1]["id"] = package["scenes"][0]["id"]
        self.assert_issue(package, "scenes[1].id", "duplicate scene id")

    def test_slug_mismatch(self):
        package = load(ARRAYS)
        package["generator_compatibility"]["output_video_name"] = "other_name"
        self.assert_issue(package, "generator_compatibility.output_video_name", "must equal slug")

    def test_bad_logo_and_strategy(self):
        package = load(ARRAYS)
        package["branding"]["logo_asset_id"] = "asset_nope"
        package["assets"][0]["source_strategy"] = "download"
        self.assert_issue(package, "branding.logo_asset_id", "does not match any assets[].id")
        self.assert_issue(package, "assets[0].source_strategy", "must be one of")

    def test_errors_inside_generator_compatibility_name_the_field(self):
        package = load(ARRAYS)
        package["generator_compatibility"]["voiceover"]["provider"] = "polly"
        package["generator_compatibility"]["sections"][1]["title"] = ""
        self.assert_issue(package, "generator_compatibility.voiceover.provider", "must be one of")
        self.assert_issue(package, "generator_compatibility.sections[1].title", "at least 1 character")
        self.assertFalse([i for i in validate_package(package) if "must be of type" in i.message])

    def test_package_missing_generator_compatibility_is_still_a_package(self):
        package = load(ARRAYS)
        del package["generator_compatibility"]
        self.assertTrue(is_lesson_package(package))
        self.assert_issue(package, "generator_compatibility", "is required")

    def test_ensure_valid_package_lists_paths(self):
        package = load(ARRAYS)
        del package["scenes"][3]["voiceover"]
        with self.assertRaises(PackageValidationError) as ctx:
            ensure_valid_package(package, "examples/x/lesson_package.json")
        self.assertIn("examples/x/lesson_package.json is not a valid lesson package", str(ctx.exception))
        self.assertIn("scenes[3].voiceover: is required", str(ctx.exception))
        self.assertTrue(ctx.exception.issues)

    def test_error_list_is_capped(self):
        package = load(ARRAYS)
        for scene in package["scenes"]:
            scene.pop("voiceover")
            scene.pop("title")
            scene.pop("purpose")
        with self.assertRaises(PackageValidationError) as ctx:
            ensure_valid_package(copy.deepcopy(package))
        self.assertIn("... and", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
