import copy
import json
import unittest
from pathlib import Path

from ai_sankalp.models import LessonConfig, LessonSection, LessonValidationError, VoiceoverConfig
from ai_sankalp.schema_validation import load_schema, validate
from ai_sankalp.template_registry import TEMPLATE_NAMES

ROOT = Path(__file__).resolve().parents[1]


def reduced_config_paths():
    return sorted(ROOT.glob("examples/*.json")) + sorted(ROOT.glob("examples/*/config.json"))


VALID = {
    "topic": "Loops", "title": "Loops", "language": "Python",
    "sections": [{"title": "Repeat", "bullets": ["Run the body again."]}],
    "code_example": "for i in range(3):\n    print(i)",
    "output_video_name": "loops",
}


class TrackedExampleTests(unittest.TestCase):
    def test_every_tracked_reduced_config_validates(self):
        schema = load_schema("lesson.schema.json")
        paths = reduced_config_paths()
        self.assertGreaterEqual(len(paths), 2)
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual([], [str(issue) for issue in validate(data, schema)])
                LessonConfig.from_dict(data)


class SchemaModelAgreementTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema("lesson.schema.json")
        self.defs = self.schema["$defs"]

    def test_top_level_properties_match_model_fields(self):
        self.assertEqual(set(LessonConfig.ACCEPTED_FIELDS), set(self.schema["properties"]))

    def test_voiceover_properties_match_model_fields(self):
        voiceover_object = next(form for form in self.defs["voiceover"]["oneOf"] if form["type"] == "object")
        expected = set(VoiceoverConfig.ACCEPTED_FIELDS) | set(VoiceoverConfig.INFORMATIONAL_FIELDS)
        self.assertEqual(expected, set(voiceover_object["properties"]))

    def test_section_properties_match_model_fields(self):
        section_object = next(form for form in self.defs["section"]["oneOf"] if form["type"] == "object")
        self.assertEqual(set(LessonSection.ACCEPTED_FIELDS), set(section_object["properties"]))

    def test_visual_template_enum_matches_registry(self):
        self.assertEqual(list(TEMPLATE_NAMES), self.schema["properties"]["visual_template"]["enum"])

    def test_legacy_alias_forms_accepted_by_both(self):
        legacy = {
            "topic": "Pointers", "lesson_title": "C Pointers", "programming_language": "C",
            "explanation": "Memory address\nA pointer stores an address.",
            "code": "int *p = &value;", "output": "c_pointers.mp4", "voiceover": None,
        }
        self.assertEqual([], validate(legacy, self.schema))
        LessonConfig.from_dict(legacy)
        string_forms = dict(VALID, sections=["Just one idea"], voiceover=False)
        self.assertEqual([], validate(string_forms, self.schema))
        LessonConfig.from_dict(string_forms)

    def test_invalid_inputs_rejected_by_schema_and_model(self):
        cases = {
            "missing code": {key: value for key, value in VALID.items() if key != "code_example"},
            "speed too high": dict(VALID, voiceover={"speed": 3.0}),
            "speed not a number": dict(VALID, voiceover={"speed": "fast"}),
            "enabled not a bool": dict(VALID, voiceover={"enabled": "yes"}),
            "unknown provider": dict(VALID, voiceover={"provider": "polly"}),
            "bad rate": dict(VALID, voiceover={"provider": "edge", "rate": "fast"}),
            "bad pitch": dict(VALID, voiceover={"provider": "edge", "pitch": "1"}),
            "unknown template": dict(VALID, visual_template="fancy"),
            "section without bullets": dict(VALID, sections=[{"title": "Empty"}]),
        }
        for name, data in cases.items():
            with self.subTest(case=name):
                self.assertTrue(validate(copy.deepcopy(data), self.schema), "schema accepted it")
                with self.assertRaises(LessonValidationError):
                    LessonConfig.from_dict(copy.deepcopy(data))

    def test_model_error_messages_are_actionable(self):
        with self.assertRaisesRegex(LessonValidationError, "provider must be one of: gtts, edge"):
            LessonConfig.from_dict(dict(VALID, voiceover={"provider": "polly"}))
        with self.assertRaisesRegex(LessonValidationError, "speed must be a number"):
            LessonConfig.from_dict(dict(VALID, voiceover={"speed": "fast"}))
        with self.assertRaisesRegex(LessonValidationError, "standard, futuristic_array"):
            LessonConfig.from_dict(dict(VALID, visual_template="fancy"))


if __name__ == "__main__":
    unittest.main()
