import json
import tempfile
import unittest
from pathlib import Path

from ai_sankalp.generator import LessonGenerator
from ai_sankalp.models import LessonConfig, LessonValidationError, safe_slug


class LessonConfigTests(unittest.TestCase):
    def test_plain_explanation_becomes_sections(self):
        lesson = LessonConfig.from_dict({
            "topic": "Pointers",
            "title": "C Pointers",
            "language": "C",
            "explanation": "Memory address\nA pointer stores an address.\n\nDereference\nThe star reads the value.",
            "code_example": "int *p = &value;",
            "output_video_name": "C pointers.mp4",
            "voiceover": False,
        })
        self.assertEqual(2, len(lesson.sections))
        self.assertEqual("c_pointers", lesson.output_video_name)
        self.assertFalse(lesson.voiceover.enabled)

    def test_missing_code_is_rejected(self):
        with self.assertRaises(LessonValidationError):
            LessonConfig.from_dict({"topic": "Loops", "title": "Loops", "language": "C"})

    def test_slug_drops_path_characters(self):
        self.assertEqual("unsafe_name", safe_slug("../../unsafe name"))

    def test_long_sections_are_split_for_readable_slides(self):
        lesson = LessonConfig.from_dict({
            "topic": "Recursion", "title": "Recursion", "language": "Python",
            "sections": [{"title": "Call stack", "bullets": [str(i) for i in range(6)]}],
            "code_example": "def f(): pass", "output_video_name": "recursion",
        })
        self.assertEqual(2, len(lesson.sections))
        self.assertEqual("Call stack (continued)", lesson.sections[1].title)


class GeneratorTests(unittest.TestCase):
    def test_generator_writes_config_and_scene(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "templates").mkdir()
            (root / "templates" / "generated_scene.py.tmpl").write_text(
                "class __SCENE_CLASS__:\n    path = '__CONFIG_RELATIVE_PATH__'\n", encoding="utf-8"
            )
            lesson = LessonConfig.from_dict({
                "topic": "SQL joins", "title": "Understanding joins", "language": "SQL",
                "explanation": ["Match rows from two tables"],
                "code_example": "SELECT * FROM a JOIN b ON a.id = b.id;",
                "output_video_name": "sql_joins", "voiceover": False,
            })
            result = LessonGenerator(root).generate(lesson)
            self.assertTrue(result.scene_path.exists())
            self.assertTrue(result.config_path.exists())
            self.assertEqual("sql_joins", json.loads(result.config_path.read_text())["output_video_name"])
            self.assertIn("SqlJoinsScene", result.scene_path.read_text())

    def test_futuristic_array_template_selects_specialized_scene(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "templates").mkdir()
            (root / "templates" / "generated_scene.py.tmpl").write_text(
                "from __SCENE_MODULE__ import __SCENE_BASE__\n"
                "class __SCENE_CLASS__(__SCENE_BASE__):\n"
                "    path = '__CONFIG_RELATIVE_PATH__'\n",
                encoding="utf-8",
            )
            lesson = LessonConfig.from_dict({
                "topic": "Arrays", "title": "Arrays", "language": "C++",
                "sections": [{"title": "Index", "bullets": ["Indexes begin at zero."]}],
                "code_example": "int values[2] = {1, 2};",
                "output_video_name": "arrays",
                "visual_template": "futuristic_array",
                "voiceover": {
                    "provider": "edge", "voice": "en-IN-NeerjaNeural",
                    "rate": "-4%", "pitch": "+1Hz",
                },
            })
            result = LessonGenerator(root).generate(lesson)
            source = result.scene_path.read_text(encoding="utf-8")
            self.assertIn("from ai_sankalp.futuristic_array_scene import FuturisticArrayLesson", source)
            self.assertIn("class ArraysScene(FuturisticArrayLesson)", source)
            self.assertEqual("edge", lesson.voiceover.provider)


if __name__ == "__main__":
    unittest.main()
