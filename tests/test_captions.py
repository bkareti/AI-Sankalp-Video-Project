import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import app
from ai_sankalp.captions import (
    LINE_CHARS, Cue, chunk_caption_text, emit_subcaptions, estimate_cues_from_lesson, estimate_cues_from_package,
    export_captions, format_srt, format_vtt, parse_srt, timed_chunks, validate_cues,
)
from ai_sankalp.config_io import load_config
from ai_sankalp.narration import standard_script

ROOT = Path(__file__).resolve().parents[1]
TEXT = ("Welcome to AI Sankalp. Imagine you have the marks of five students, and you want to keep "
        "all of them together in one program without repeating yourself again and again.")


class ChunkingTests(unittest.TestCase):
    def test_chunks_fit_two_lines(self):
        chunks = chunk_caption_text(TEXT)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), LINE_CHARS * 2 + 1)
        self.assertEqual(" ".join(TEXT.split()), " ".join(chunks))

    def test_timed_chunks_cover_the_duration(self):
        cues = timed_chunks(TEXT, start=2.0, duration=10.0)
        self.assertAlmostEqual(2.0, cues[0].start)
        self.assertLessEqual(cues[-1].end, 12.0)
        self.assertGreater(cues[-1].end, 11.5)
        for first, second in zip(cues, cues[1:]):
            self.assertLessEqual(first.end, second.start)
        for cue in cues:
            self.assertLessEqual(len(cue.text.split("\n")), 2)

    def test_empty_inputs(self):
        self.assertEqual([], timed_chunks("", 0, 5))
        self.assertEqual([], timed_chunks("Hi.", 0, 0))


class FakeScene:
    def __init__(self, now):
        self.time = now
        self.added = []

    def add_subcaption(self, content, duration=1, offset=0):
        self.added.append((self.time + offset, self.time + offset + duration, content))


class EmitTests(unittest.TestCase):
    def test_voiceover_block_starts_now(self):
        scene = FakeScene(now=10.0)
        emit_subcaptions(scene, TEXT, duration=8.0)
        self.assertAlmostEqual(10.0, scene.added[0][0])
        self.assertLessEqual(scene.added[-1][1], 18.0)

    def test_silent_block_uses_negative_offset(self):
        scene = FakeScene(now=15.0)  # the action already ran from 12.0 to 15.0
        emit_subcaptions(scene, "One short line.", duration=3.0, offset=-3.0)
        start, end, text = scene.added[0]
        self.assertAlmostEqual(12.0, start)
        self.assertLessEqual(end, 15.0)
        self.assertEqual("One short line.", text)


class EmitClampTests(unittest.TestCase):
    def test_first_cue_never_starts_before_the_scene(self):
        scene = FakeScene(now=3.0)
        emit_subcaptions(scene, "Welcome to AI Sankalp. In this lesson we start.", duration=3.0000001, offset=-3.0000001)
        self.assertEqual(0.0, scene.added[0][0])
        self.assertEqual("Welcome to AI Sankalp.", scene.added[0][2])


class FormatTests(unittest.TestCase):
    CUES = [Cue(0.0, 1.5, "First line"), Cue(1.6, 3725.25, "Second\nline")]

    def test_srt_round_trip(self):
        text = format_srt(self.CUES)
        self.assertIn("00:00:01,500", text)
        self.assertIn("01:02:05,250", text)
        self.assertEqual(self.CUES, parse_srt(text))

    def test_vtt_round_trip(self):
        text = format_vtt(self.CUES)
        self.assertTrue(text.startswith("WEBVTT\n"))
        self.assertIn("00:00:01.600 --> 01:02:05.250", text)
        self.assertEqual(self.CUES, parse_srt(text))

    def test_malformed_srt_raises(self):
        with self.assertRaises(ValueError):
            parse_srt("1\nnot a timing line\nhello\n")

    def test_validate_cues(self):
        self.assertEqual([], validate_cues(self.CUES[:1], video_duration=2.0))
        self.assertEqual(["no caption cues"], validate_cues([]))
        fast = [Cue(0.0, 0.5, "x" * 40)]
        self.assertTrue(any("too fast" in problem for problem in validate_cues(fast)))
        self.assertTrue(any("after the video ends" in problem for problem in validate_cues(self.CUES[:1], 0.2)))
        overlap = [Cue(0, 2, "a"), Cue(1, 3, "b")]
        self.assertTrue(any("overlaps" in problem for problem in validate_cues(overlap)))


class EstimateTests(unittest.TestCase):
    def test_estimate_from_package_covers_every_scene(self):
        package = json.loads((ROOT / "examples" / "arrays_in_cpp" / "lesson_package.json").read_text(encoding="utf-8"))
        cues = estimate_cues_from_package(package)
        spoken = " ".join(" ".join(scene["voiceover"].split()) for scene in package["scenes"])
        self.assertEqual(spoken, " ".join(cue.text.replace("\n", " ") for cue in cues))
        planned = package["duration_minutes"] * 60
        self.assertLess(abs(cues[-1].end - planned) / planned, 0.25)
        self.assertEqual([], validate_cues(cues))

    def test_estimate_from_lesson_matches_standard_script(self):
        lesson = load_config(ROOT / "examples" / "python_for_loops.json")
        cues = estimate_cues_from_lesson(lesson)
        spoken = " ".join(segment.text for segment in standard_script(lesson))
        self.assertEqual(spoken, " ".join(cue.text.replace("\n", " ") for cue in cues))

    def test_standard_script_segments(self):
        lesson = load_config(ROOT / "examples" / "python_for_loops.json")
        ids = [segment.id for segment in standard_script(lesson)]
        self.assertEqual(["intro", "section_01", "section_02", "section_03", "code", "summary", "outro"], ids)

    def test_export_writes_both_files(self):
        with tempfile.TemporaryDirectory() as directory:
            files = export_captions(FormatTests.CUES, Path(directory), "lesson", "estimated")
            self.assertTrue(files.srt.read_text(encoding="utf-8").startswith("1\n"))
            self.assertTrue(files.vtt.read_text(encoding="utf-8").startswith("WEBVTT"))
            self.assertEqual(2, files.cue_count)


class CaptionsCliTests(unittest.TestCase):
    def test_captions_command_writes_files(self):
        with tempfile.TemporaryDirectory() as directory:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = app.main(["captions", "--config", str(ROOT / "examples" / "python_for_loops.json"),
                                 "--output-dir", directory])
            self.assertEqual(0, code)
            self.assertTrue((Path(directory) / "python_for_loops.srt").exists())
            self.assertTrue((Path(directory) / "python_for_loops.vtt").exists())

    def test_captions_command_will_not_replace_render_captions(self):
        with tempfile.TemporaryDirectory() as directory:
            export_captions([Cue(0, 1, "Timed by a render.")], Path(directory), "python_for_loops", "render")
            config = str(ROOT / "examples" / "python_for_loops.json")
            with contextlib.redirect_stderr(io.StringIO()) as stderr, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, app.main(["captions", "--config", config, "--output-dir", directory]))
            self.assertIn("--force", stderr.getvalue())
            self.assertIn("Timed by a render.", (Path(directory) / "python_for_loops.srt").read_text(encoding="utf-8"))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, app.main(["captions", "--config", config, "--output-dir", directory, "--force"]))

    def test_export_records_the_source(self):
        from ai_sankalp.captions import read_caption_source

        with tempfile.TemporaryDirectory() as directory:
            export_captions([Cue(0, 1, "x")], Path(directory), "lesson", "render")
            self.assertEqual("render", read_caption_source(Path(directory), "lesson"))
            self.assertIsNone(read_caption_source(Path(directory), "missing"))

    def test_burn_flag_parses(self):
        self.assertTrue(app.build_parser().parse_args(["sample", "--burn-captions"]).burn_captions)
        self.assertTrue(app.build_parser().parse_args(["generate", "--config", "x", "--burn-captions"]).burn_captions)


if __name__ == "__main__":
    unittest.main()
