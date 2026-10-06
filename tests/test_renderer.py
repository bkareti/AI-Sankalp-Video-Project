import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ai_sankalp import renderer
from ai_sankalp.captions import Cue, format_srt
from ai_sankalp.config_io import load_config
from ai_sankalp.generator import GeneratedLesson, SceneSyntaxError
from ai_sankalp.renderer import ManimRenderer, RenderError

ROOT = Path(__file__).resolve().parents[1]
RENDER_SRT = format_srt([Cue(0.0, 2.0, "Welcome to AI Sankalp."), Cue(2.1, 4.0, "Let us begin.")])


class RendererCaptionTests(unittest.TestCase):
    def render(self, write_srt: bool, burn: bool = False, burn_ok: bool = True):
        lesson = load_config(ROOT / "examples" / "python_for_loops.json")
        lesson.voiceover.enabled = False
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        self.last_root = root

        def fake_run(command, cwd=None, capture_output=True, text=True):
            media = Path(command[command.index("--media_dir") + 1])
            out = media / "videos" / "x" / "480p15"
            out.mkdir(parents=True)
            (out / f"{lesson.slug}.mp4").write_bytes(b"mp4")
            if write_srt:
                (out / f"{lesson.slug}.srt").write_text(RENDER_SRT, encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

        def fake_burn(video, cues, output, quality):
            if not burn_ok:
                from ai_sankalp.caption_burn import CaptionBurnError
                raise CaptionBurnError("ffmpeg failed")
            output.write_bytes(b"captioned")
            return output

        (root / "s.py").write_text("x = 1\n", encoding="utf-8")
        generated = GeneratedLesson(root / "s.py", root / "s.py", lesson.scene_class)
        with mock.patch.object(renderer, "_python_with_manim", return_value=Path("python")), \
                mock.patch.object(renderer.shutil, "which", return_value="/usr/bin/ffmpeg"), \
                mock.patch.object(renderer.subprocess, "run", side_effect=fake_run), \
                mock.patch.object(renderer, "burn_caption_video", side_effect=fake_burn):
            result = ManimRenderer(root).render(generated, lesson, root / "out", "low", burn_captions=burn)
        history = [json.loads(line) for line in (root / "generated" / "history.jsonl").read_text().splitlines()]
        return result, history, root

    def test_copies_render_srt_and_writes_vtt(self):
        result, history, root = self.render(write_srt=True)
        self.assertEqual("render", result.captions.source)
        self.assertEqual(RENDER_SRT, result.captions.srt.read_text(encoding="utf-8"))
        self.assertTrue(result.captions.vtt.read_text(encoding="utf-8").startswith("WEBVTT"))
        self.assertEqual(result.video_path.parent, result.captions.srt.parent)
        succeeded = history[-1]
        self.assertEqual("render", json.loads((result.video_path.parent / "python_for_loops.captions.json").read_text())["source"])
        self.assertEqual("render_succeeded", succeeded["event"])
        self.assertEqual({"srt", "vtt", "source", "cue_count"}, set(succeeded["captions"]))
        self.assertEqual(2, succeeded["captions"]["cue_count"])

    def test_estimates_when_cache_has_no_srt(self):
        result, history, _root = self.render(write_srt=False)
        self.assertEqual("estimated", result.captions.source)
        self.assertGreater(result.captions.cue_count, 5)
        self.assertEqual("estimated", history[-1]["captions"]["source"])

    def test_burn_writes_captioned_copy(self):
        result, history, _root = self.render(write_srt=True, burn=True)
        self.assertEqual("python_for_loops_captioned.mp4", result.captioned_video_path.name)
        self.assertEqual("captions_burned", history[-1]["event"])
        self.assertTrue(history[-1]["captioned_video"].endswith("python_for_loops_captioned.mp4"))

    def test_burn_failure_is_a_render_error_but_the_render_is_recorded(self):
        with self.assertRaisesRegex(RenderError, "ffmpeg failed"):
            self.render(write_srt=True, burn=True, burn_ok=False)
        history = [json.loads(line) for line in (self.last_root / "generated" / "history.jsonl").read_text().splitlines()]
        events = [record["event"] for record in history]
        self.assertEqual(["render_started", "render_succeeded", "caption_burn_failed"], events)
        self.assertIn("video", history[-1])


class RendererSceneCheckTests(unittest.TestCase):
    """A scene that cannot compile never reaches Manim."""

    def render_scene(self, source):
        lesson = load_config(ROOT / "examples" / "python_for_loops.json")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        scene = root / "scene.py"
        if source is not None:
            scene.write_text(source, encoding="utf-8")
        generated = GeneratedLesson(scene, scene, lesson.scene_class)
        with mock.patch.object(renderer, "_python_with_manim", return_value=Path("python")), \
                mock.patch.object(renderer.shutil, "which", return_value="/usr/bin/ffmpeg"), \
                mock.patch.object(renderer.subprocess, "run") as run:
            try:
                ManimRenderer(root).render(generated, lesson, root / "out", "low")
            finally:
                self.run_mock = run
                self.history = root / "generated" / "history.jsonl"

    def test_syntax_error_stops_before_manim_and_history(self):
        with self.assertRaisesRegex(SceneSyntaxError, r"scene\.py has a syntax error at line 2"):
            self.render_scene("class A:\n    def broken(:\n        pass\n")
        self.run_mock.assert_not_called()
        self.assertFalse(self.history.exists())

    def test_missing_scene_is_a_render_error_not_a_manim_run(self):
        with self.assertRaisesRegex(RenderError, "scene file cannot be read"):
            self.render_scene(None)
        self.run_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
