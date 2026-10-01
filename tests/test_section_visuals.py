import copy
import json
import unittest
from pathlib import Path

from manim import Text

from ai_sankalp import brand, manim_scene
from ai_sankalp.config_io import load_config
from ai_sankalp.models import LessonConfig, LessonValidationError
from ai_sankalp.primitives import specs
from ai_sankalp.schema_validation import load_schema, validate

ROOT = Path(__file__).resolve().parents[1]
FONTS = brand.BrandFonts(sans="Sans", mono="Monospace")

# The Python sample as it was before section visuals existed.
OLD_SAMPLE = {
    "topic": "Python for loops", "title": "Mastering Python For Loops", "language": "Python",
    "sections": [
        {"title": "Why loops matter", "bullets": [
            "A loop repeats an action without duplicating code.",
            "For loops are useful when working with a sequence of items.",
            "The loop body runs once for every item."]},
        {"title": "Follow the iteration", "bullets": [
            "Python takes the first item from the sequence.",
            "The loop variable stores the current item.",
            "After the body runs, Python moves to the next item."]},
    ],
    "code_example": "for number in range(1, 6):\n    print(number)",
    "output_video_name": "python_for_loops", "voiceover": False,
}
VISUALS = {
    "flow": {"type": "flow", "title": "One pass", "items": ["Take item", "Run body", "Repeat"]},
    "steps": {"type": "steps", "items": ["Declare", "Read", "Loop"]},
    "compare": {"type": "compare", "left": {"title": "Wrong", "items": ["i <= 5"]},
                "right": {"title": "Right", "items": ["i < 5"]}},
    "table": {"type": "table", "columns": ["n", "n*n"], "rows": [["1", "1"], ["2", "4"], ["3", "9"]]},
}


def texts(mobject):
    return {item.text for item in mobject.get_family() if isinstance(item, Text)}


def lesson_with(visual=None, bullets=None):
    data = copy.deepcopy(OLD_SAMPLE)
    if bullets is not None:
        data["sections"][0]["bullets"] = bullets
    if visual is not None:
        data["sections"][0]["visual"] = visual
    return LessonConfig.from_dict(data)


def within_content_area(test, mobject):
    test.assertGreaterEqual(mobject.get_bottom()[1], brand.CONTENT_SAFE_BOTTOM_Y - 1e-6)
    test.assertLessEqual(mobject.get_top()[1], brand.SAFE_TOP_Y + 1e-6)
    test.assertGreaterEqual(mobject.get_left()[0], -brand.FRAME_WIDTH / 2 + brand.SAFE_MARGIN_X - 1e-6)
    test.assertLessEqual(mobject.get_right()[0], brand.FRAME_WIDTH / 2 - brand.SAFE_MARGIN_X + 1e-6)


class FabricatedLabelTests(unittest.TestCase):
    def test_keywords_helper_removed(self):
        self.assertFalse(hasattr(manim_scene, "_keywords"))
        self.assertNotIn("VISUAL MODEL", (ROOT / "ai_sankalp" / "manim_scene.py").read_text(encoding="utf-8"))

    def test_no_bullet_derived_labels(self):
        lesson = lesson_with()
        section = lesson.sections[0]
        parts = manim_scene.build_section_slide(section, 1, 2, FONTS)
        rendered = {" ".join(value.split()) for value in texts(parts.group)}
        expected_bullets = {"".join(bullet.split()) for bullet in section.bullets}
        allowed = {"STEP1OF2", "".join(section.title.split())} | expected_bullets
        # Text.text drops whitespace inside wrapped lines; compare without spaces.
        self.assertEqual(allowed, {"".join(value.split()) for value in rendered})


class BackwardCompatibilityTests(unittest.TestCase):
    def test_old_config_without_visual_loads_and_is_full_width(self):
        lesson = LessonConfig.from_dict(copy.deepcopy(OLD_SAMPLE))
        self.assertTrue(all(section.visual is None for section in lesson.sections))
        self.assertEqual(["full", "full"], [manim_scene.section_layout(s) for s in lesson.sections])
        self.assertEqual([], validate(OLD_SAMPLE, load_schema("lesson.schema.json")))

    def test_round_trip_save_load(self):
        import tempfile

        from ai_sankalp.config_io import save_config

        lesson = load_config(ROOT / "examples" / "python_for_loops.json")
        with tempfile.TemporaryDirectory() as directory:
            path = save_config(lesson, Path(directory) / "x.json")
            self.assertEqual(lesson, load_config(path))

    def test_visual_stays_on_first_chunk_when_split(self):
        lesson = lesson_with(VISUALS["flow"], bullets=[f"Point {i}" for i in range(6)])
        self.assertEqual("flow", lesson.sections[0].visual["type"])
        self.assertIsNone(lesson.sections[1].visual)

    def test_sample_uses_full_and_split_layouts(self):
        lesson = load_config(ROOT / "examples" / "python_for_loops.json")
        self.assertEqual(["full", "split", "split"], [manim_scene.section_layout(s) for s in lesson.sections])


class SectionVisualTests(unittest.TestCase):
    def test_each_visual_type_parses_and_builds(self):
        self.assertEqual(set(VISUALS), set(specs.SPEC_TYPES))
        for kind, visual in VISUALS.items():
            with self.subTest(kind=kind):
                section = lesson_with(visual).sections[0]
                self.assertEqual("split", manim_scene.section_layout(section))
                parts = manim_scene.build_section_slide(section, 1, 2, FONTS)
                self.assertIsNotNone(parts.visual)
                within_content_area(self, parts.group)
                self.assertTrue(parts.visual_panel.get_left()[0] < parts.visual.get_left()[0])
                self.assertTrue(parts.visual.get_right()[0] < parts.visual_panel.get_right()[0])

    def test_bullets_share_one_type_size(self):
        section = lesson_with(VISUALS["flow"], bullets=[
            "Python takes the first item from the sequence.",
            "The loop variable stores the current item.",
            "Short."]).sections[0]
        parts = manim_scene.build_section_slide(section, 1, 2, FONTS)
        sizes = {round(row[1].font_size, 3) for row in parts.bullets}
        self.assertEqual(1, len(sizes))

    def test_visual_text_comes_only_from_spec(self):
        section = lesson_with(VISUALS["flow"]).sections[0]
        parts = manim_scene.build_section_slide(section, 1, 2, FONTS)
        self.assertEqual({"Takeitem", "Runbody", "Repeat"}, {"".join(t.split()) for t in texts(parts.visual)})

    def test_full_width_slide_within_safe_area(self):
        section = lesson_with(bullets=["A long bullet " * 6, "Second", "Third", "Fourth"]).sections[0]
        parts = manim_scene.build_section_slide(section, 1, 1, FONTS)
        self.assertEqual("full", parts.layout)
        within_content_area(self, parts.group)
        self.assertGreater(parts.bullet_panel.width, 11)

    def test_invalid_visuals_raise_with_section_index(self):
        cases = {
            "unknown type": {"type": "chart"},
            "too many items": {"type": "flow", "items": ["a", "b", "c", "d", "e", "f"]},
            "ragged table": {"type": "table", "columns": ["a", "b"], "rows": [["1"]]},
            "compare missing right": {"type": "compare", "left": {"title": "L", "items": ["x"]}},
            "unknown key": {"type": "steps", "items": ["a", "b"], "colour": "red"},
            "long title": {"type": "steps", "items": ["a", "b"], "title": "x" * 60},
        }
        for name, visual in cases.items():
            with self.subTest(case=name):
                with self.assertRaisesRegex(LessonValidationError, "section 1 visual"):
                    lesson_with(visual)

    def test_schema_enum_matches_spec_types(self):
        for name in ("lesson.schema.json", "lesson_package.schema.json"):
            enum = load_schema(name)["$defs"]["visual"]["properties"]["type"]["enum"]
            self.assertEqual(list(specs.SPEC_TYPES), enum)

    def test_specs_module_is_manim_free(self):
        source = (ROOT / "ai_sankalp" / "primitives" / "specs.py").read_text(encoding="utf-8")
        self.assertNotIn("manim", source.replace("Manim", ""))


if __name__ == "__main__":
    unittest.main()
