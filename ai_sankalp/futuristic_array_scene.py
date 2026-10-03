"""The flagship template: every scene of a rich lesson package, drawn with
data-driven primitives. No lesson content lives in this file; scenes choose
primitives through `scenes[].visuals` (or a default by scene type)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from manim_voiceover import VoiceoverScene

from .brand import brand_fonts
from .config_io import load_config
from .package import load_package, resolve_package_path  # noqa: F401  (re-exported)
from .primitives.base import PrimitiveContext
from .primitives.frame import add_brand_frame
from .primitives.planner import plan_lesson
from .primitives.runner import play_scene
from .speech import build_speech_service

FINAL_HOLD = 0.8


class FuturisticArrayLesson(VoiceoverScene):
    """A cinematic, diagram-first lesson driven entirely by the rich package."""

    LESSON_CONFIG_PATH: Path
    LESSON_PACKAGE_PATH: Optional[Path] = None

    def construct(self) -> None:
        self.lesson = load_config(Path(self.LESSON_CONFIG_PATH))
        project_root = Path(__file__).resolve().parents[1]
        package_path = self.LESSON_PACKAGE_PATH or resolve_package_path(project_root, self.lesson.slug)
        package = load_package(package_path)
        self.fonts = brand_fonts()
        voiceover = self.lesson.voiceover.enabled
        if voiceover:
            # Captions come from emit_subcaptions in the runner, in both voiceover modes.
            self.set_speech_service(build_speech_service(self.lesson.voiceover, project_root), create_subcaption=False)

        frame = add_brand_frame(self, self.fonts, style="grid")
        for scene_data, plan in zip(package["scenes"], plan_lesson(package)):
            ctx = PrimitiveContext(
                fonts=self.fonts, package=package, scene_data=scene_data,
                project_root=project_root, language=self.lesson.language,
            )
            play_scene(self, plan, ctx, voiceover=voiceover, ambient=frame.ambient)
        self.wait(FINAL_HOLD)
