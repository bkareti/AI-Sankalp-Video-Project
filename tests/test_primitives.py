import copy
import json
import re
import unittest
from pathlib import Path
from unittest import mock

from ai_sankalp import brand
from ai_sankalp.models import LessonConfig, LessonValidationError
from ai_sankalp.package import validate_package
from ai_sankalp.primitives import runner, specs
from ai_sankalp.primitives.base import BuiltVisual, PrimitiveContext
from ai_sankalp.primitives.fixtures import fixture_paths, fixture_scene, load_fixture, smoke_class_name
from ai_sankalp.primitives.planner import PlanError, assign_beats, plan_lesson, split_sentences
from ai_sankalp.primitives.registry import BUILDERS
from ai_sankalp.schema_validation import load_schema

ROOT = Path(__file__).resolve().parents[1]
ARRAYS = ROOT / "examples" / "arrays_in_cpp" / "lesson_package.json"
FONTS = brand.BrandFonts(sans="Sans", mono="Monospace")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class RegistryTests(unittest.TestCase):
    def test_registry_has_at_least_five_and_matches_specs(self):
        self.assertGreaterEqual(len(BUILDERS), 5)
        self.assertEqual(set(specs.SPEC_TYPES), set(BUILDERS))
        self.assertTrue(set(specs.STANDARD_COMPATIBLE) <= set(specs.SPEC_TYPES))

    def test_schema_enums_match_specs(self):
        package_defs = load_schema("lesson_package.schema.json")["$defs"]
        self.assertEqual(list(specs.SPEC_TYPES), package_defs["sceneVisual"]["properties"]["type"]["enum"])
        for name in ("lesson.schema.json", "lesson_package.schema.json"):
            section_enum = load_schema(name)["$defs"]["visual"]["properties"]["type"]["enum"]
            self.assertEqual(list(specs.STANDARD_COMPATIBLE), section_enum, name)

    def test_specs_and_planner_are_manim_free(self):
        for name in ("specs.py", "planner.py", "fixtures.py"):
            source = (ROOT / "ai_sankalp" / "primitives" / name).read_text(encoding="utf-8")
            self.assertNotRegex(source, r"^\s*(from|import) manim", name)


class FlagshipDataDrivenTests(unittest.TestCase):
    def test_flagship_scene_has_no_lesson_literals(self):
        sources = [ROOT / "ai_sankalp" / "futuristic_array_scene.py"]
        sources += sorted((ROOT / "ai_sankalp" / "primitives").glob("*.py"))
        whole = r"(?<![\d.]){}(?![\d.])"  # a whole number, not part of a decimal like 0.88
        banned = [whole.format(70), whole.format(85), whole.format(90), whole.format(75), whole.format(88), r"\bmarks\b", r"\bscores\b", r"std::array",
                  r"ARRAYS", r"MEMORY", r"WHY ARRAYS", r"OUTPUT STREAM", r"UNDEFINED", r"\b4096\b"]
        for path in sources:
            source = path.read_text(encoding="utf-8")
            for pattern in banned:
                with self.subTest(file=path.name, pattern=pattern):
                    self.assertIsNone(re.search(pattern, source))

    def test_flagship_package_plans_all_scenes(self):
        package = load(ARRAYS)
        plans = plan_lesson(package)
        self.assertEqual([scene["id"] for scene in package["scenes"]], [plan.scene_id for plan in plans])
        self.assertTrue(all("visuals" in scene for scene in package["scenes"]))
        types = [visual.type for plan in plans for visual in plan.visuals]
        self.assertEqual([
            "title_card", "card_merge", "array_lane", "token_breakdown", "index_access", "code_walkthrough",
            "loop_trace", "bounds_check", "practice_reveal", "concept_map", "outro_card",
        ], types)
        self.assertGreaterEqual(len(set(types)), 5)

    def test_after_narration_visual_planned_separately(self):
        plan = plan_lesson(load(ARRAYS))[3]
        self.assertEqual(["narrated", "after_narration"], [visual.timing for visual in plan.visuals])


class PlannerTests(unittest.TestCase):
    def test_assign_beats(self):
        self.assertEqual([[0], [1], [2], []], assign_beats(4, 3))
        self.assertEqual([[i] for i in range(8)], assign_beats(8, 8))
        self.assertEqual([[0], [1], [2], [3], [4], [5], [6, 7, 8]], assign_beats(7, 9))
        self.assertEqual([[], []], assign_beats(2, 0))
        self.assertEqual([], assign_beats(0, 3))

    def test_every_beat_is_assigned_once(self):
        for sentences in range(1, 10):
            for beats in range(0, 12):
                flat = [beat for group in assign_beats(sentences, beats) for beat in group]
                self.assertEqual(list(range(beats)), flat)

    def test_split_sentences(self):
        self.assertEqual(["Hello there.", "i plus plus moves on!", "Done"], split_sentences("Hello there. i plus plus moves on! Done"))

    def test_default_primitive_by_scene_type(self):
        package = {"title": "SQL Joins", "topic": "Joins", "language": "SQL",
                   "code_examples": [{"id": "code_01", "code": "SELECT 1;"}]}
        expected = {"intro": "title_card", "outro": "outro_card", "code_walkthrough": "code_walkthrough",
                    "summary": "concept_map", "motivation": "bullet_card", "visual_trace": "bullet_card"}
        for scene_type, primitive in expected.items():
            scene = {"type": scene_type, "title": "T", "on_screen_text": ["one", "two"], "code_example_ids": []}
            with self.subTest(scene_type=scene_type):
                spec = specs.default_visual_for_scene(scene, package)
                self.assertEqual(primitive, spec["type"])
                self.assertEqual([], specs.validate_visual(spec, "scene"))

    def test_defaults_clip_long_on_screen_text(self):
        scene = {"type": "explanation", "title": "T", "on_screen_text": ["x" * 90]}
        spec = specs.default_visual_for_scene(scene, {})
        self.assertEqual([], specs.validate_visual(spec, "scene"))

    def test_package_without_visuals_plans_with_defaults(self):
        package = load(ARRAYS)
        for scene in package["scenes"]:
            scene.pop("visuals")
        plans = plan_lesson(package)
        self.assertEqual(10, len(plans))
        self.assertEqual("title_card", plans[0].visuals[0].type)
        self.assertEqual("code_walkthrough", plans[4].visuals[0].type)

    def test_invalid_params_report_paths(self):
        package = load(ARRAYS)
        package["scenes"][5]["visuals"][0]["values"] = []
        package["scenes"][7]["visuals"][0]["highlight_index"] = 9
        package["scenes"][2]["visuals"].append({"type": "sparkle"})
        with self.assertRaises(PlanError) as ctx:
            plan_lesson(package)
        text = str(ctx.exception)
        self.assertIn("scenes[5].visuals[0]: values must have 1 to 8 items", text)
        self.assertIn("scenes[7].visuals[0]: highlight_index must be between 0 and 3", text)
        self.assertIn("scenes[2].visuals[1]: type must be one of", text)
        # validate_package reports the unknown type through the schema enum, then
        # plan issues (with field paths) once the schema passes.
        self.assertIn("scenes[2].visuals[1].type", {issue.path for issue in validate_package(package)})
        package["scenes"][2]["visuals"].pop()
        paths = {issue.path for issue in validate_package(package)}
        self.assertIn("scenes[5].visuals[0]", paths)
        self.assertIn("scenes[7].visuals[0]", paths)

    def test_malformed_packages_report_issues_instead_of_raising(self):
        cases = {
            "on_screen_text not a list": lambda p: (p["scenes"][1].pop("visuals"), p["scenes"][1].update(on_screen_text=5)),
            "code_examples not a list": lambda p: p.update(code_examples=5),
            "code_example_ids not a list": lambda p: (p["scenes"][4].pop("visuals"), p["scenes"][4].update(code_example_ids=7)),
        }
        for name, mutate in cases.items():
            with self.subTest(case=name):
                package = load(ARRAYS)
                mutate(package)
                issues = validate_package(package)
                self.assertTrue(issues)
                self.assertTrue(any("must be of type" in issue.message for issue in issues), [str(i) for i in issues])

    def test_long_summary_lines_fall_back_to_bullet_card(self):
        scene = {"type": "summary", "title": "Recap",
                 "on_screen_text": ["Variable changes each pass", "range: start in, stop out"]}
        spec = specs.default_visual_for_scene(scene, {"topic": "Loops"})
        self.assertEqual("bullet_card", spec["type"])
        self.assertEqual(scene["on_screen_text"], spec["bullets"])

    def test_highlight_index_requires_values(self):
        problems = specs.validate_visual({
            "type": "token_breakdown", "tokens": [{"text": "a", "role": "b"}, {"text": "c", "role": "d"}],
            "code_line": "a c", "highlight_index": 5}, "scene")
        self.assertIn("highlight_index needs values to highlight", problems)

    def test_voiceover_without_sentence_breaks_is_one_sentence(self):
        package = load(ARRAYS)
        package["scenes"][0]["voiceover"] = "..."
        package["voiceover_segments"][0]["text"] = "..."
        self.assertEqual(["..."], plan_lesson(package)[0].sentences)

    def test_unknown_code_example_is_reported(self):
        package = load(ARRAYS)
        package["scenes"][4]["visuals"][0]["code_example_id"] = "code_99"
        with self.assertRaisesRegex(PlanError, "code_example_id 'code_99' does not match"):
            plan_lesson(package)


class FixtureTests(unittest.TestCase):
    def test_every_primitive_has_valid_fixture(self):
        kinds = {path.stem for path in fixture_paths()}
        self.assertEqual(set(specs.SPEC_TYPES), kinds)
        for path in fixture_paths():
            with self.subTest(fixture=path.stem):
                fixture = load_fixture(path)
                self.assertEqual(path.stem, fixture["visual"]["type"])
                _scene, package = fixture_scene(fixture)
                plan_lesson(package)

    def test_smoke_scene_names(self):
        self.assertEqual("LoopTraceSmoke", smoke_class_name("loop_trace"))

    def test_fixture_builds_within_safe_area(self):
        """Builds real mobjects (no rendering) for every primitive."""
        for path in fixture_paths():
            with self.subTest(fixture=path.stem):
                fixture = load_fixture(path)
                scene, package = fixture_scene(fixture)
                visual = plan_lesson(package)[0].visuals[0]
                ctx = PrimitiveContext(fonts=FONTS, package=package, scene_data=scene, language=fixture.get("language", ""))
                built, header = runner.prepare_visual(visual, ctx)
                self.assertEqual(visual.beat_count, len(built.beats))
                extent = built.extent
                self.assertGreaterEqual(extent.get_bottom()[1], brand.CONTENT_SAFE_BOTTOM_Y - 1e-6)
                self.assertLessEqual(extent.get_top()[1], brand.LOGO_ZONE_MIN_Y)
                half = brand.FRAME_WIDTH / 2 - brand.SAFE_MARGIN_X
                self.assertGreaterEqual(extent.get_left()[0], -half - 1e-6)
                self.assertLessEqual(extent.get_right()[0], half + 1e-6)
                if header is not None:
                    self.assertLess(extent.get_top()[1], header.get_bottom()[1])

    def test_flagship_visuals_build_within_safe_area(self):
        package = load(ARRAYS)
        for scene, plan in zip(package["scenes"], plan_lesson(package)):
            for visual in plan.visuals:
                with self.subTest(scene=plan.scene_id, visual=visual.type):
                    ctx = PrimitiveContext(fonts=FONTS, package=package, scene_data=scene, language="C++")
                    built, _header = runner.prepare_visual(visual, ctx)
                    self.assertEqual(visual.beat_count, len(built.beats))
                    self.assertGreaterEqual(built.extent.get_bottom()[1], brand.CONTENT_SAFE_BOTTOM_Y - 1e-6)


class FakeScene:
    def __init__(self):
        self.mobjects = []
        self.foreground_mobjects = []
        self.calls = []

    def play(self, *animations, run_time=None, **kwargs):
        self.calls.append(("play", run_time))

    def wait(self, duration=None):
        self.calls.append(("wait", duration))


class PlaySceneTests(unittest.TestCase):
    def test_play_scene_runs_every_beat_including_extras(self):
        package = load(ARRAYS)
        plan = plan_lesson(package)[6]  # 7 sentences, 9 beats
        ran = []

        def fake_build(spec, ctx):
            return BuiltVisual([], [lambda scene, d, i=i: ran.append((i, d)) for i in range(plan.visuals[0].beat_count)])

        with mock.patch.object(runner, "build_visual", side_effect=fake_build):
            runner.play_scene(FakeScene(), plan, PrimitiveContext(fonts=FONTS), voiceover=False)
        self.assertEqual(list(range(9)), [index for index, _ in ran])
        self.assertTrue(all(duration == runner.SILENT_BEAT for _, duration in ran))

    def test_after_narration_beats_use_fixed_timing(self):
        package = load(ARRAYS)
        plan = plan_lesson(package)[3]
        ran = []

        def fake_build(spec, ctx):
            return BuiltVisual([], [lambda scene, d, t=spec["type"]: ran.append((t, d)) for _ in range(2)])

        scene = FakeScene()
        with mock.patch.object(runner, "build_visual", side_effect=fake_build):
            runner.play_scene(scene, plan, PrimitiveContext(fonts=FONTS), voiceover=False)
        self.assertEqual([("index_access", runner.AFTER_NARRATION_BEAT)] * 2, [item for item in ran if item[0] == "index_access"])
        self.assertIn(("wait", runner.AFTER_NARRATION_HOLD), scene.calls)


class StandardCompatibilityTests(unittest.TestCase):
    BASE = {
        "topic": "Loops", "title": "Loops", "language": "Python",
        "code_example": "for i in range(3):\n    print(i)", "output_video_name": "loops", "voiceover": False,
    }

    def lesson(self, visual):
        return LessonConfig.from_dict(dict(self.BASE, sections=[{"title": "S", "bullets": ["b"], "visual": visual}]))

    def test_standard_accepts_compatible_primitives_and_rejects_others(self):
        from ai_sankalp import manim_scene

        compatible = {
            "array_lane": {"type": "array_lane", "values": ["1", "2", "3"]},
            "loop_trace": {"type": "loop_trace", "values": ["1", "2"], "variable": "n"},
            "concept_map": {"type": "concept_map", "center": "LOOP", "nodes": ["repeat", "stop"]},
        }
        for kind, visual in compatible.items():
            with self.subTest(kind=kind):
                parts = manim_scene.build_section_slide(self.lesson(visual).sections[0], 1, 1, FONTS)
                self.assertTrue(parts.visual_beats)
                self.assertLessEqual(parts.visual.get_right()[0], parts.visual_panel.get_right()[0] + 1e-6)
                self.assertGreaterEqual(parts.visual.get_bottom()[1], parts.visual_panel.get_bottom()[1] - 1e-6)
        for kind in ("title_card", "code_walkthrough", "bounds_check"):
            with self.subTest(rejected=kind):
                with self.assertRaisesRegex(LessonValidationError, "type must be one of"):
                    self.lesson({"type": kind})

    def test_section_rejects_scene_only_keys(self):
        with self.assertRaisesRegex(LessonValidationError, "unknown key"):
            self.lesson({"type": "flow", "items": ["a", "b"], "timing": "after_narration"})

    def test_python_sample_uses_loop_trace(self):
        from ai_sankalp.config_io import load_config

        lesson = load_config(ROOT / "examples" / "python_for_loops.json")
        self.assertEqual("loop_trace", lesson.sections[1].visual["type"])


if __name__ == "__main__":
    unittest.main()
