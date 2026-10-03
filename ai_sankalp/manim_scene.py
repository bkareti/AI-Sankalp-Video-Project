from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from manim import (
    DOWN, LEFT, ORIGIN, RIGHT, UP, Create, Dot, FadeIn, FadeOut, GrowFromCenter, Line, VGroup,
)
from manim_voiceover import VoiceoverScene

from . import brand
from .brand import BrandFonts, brand_fonts
from .captions import emit_subcaptions
from .config_io import load_config
from .models import LessonSection
from .narration import standard_script
from .primitives.base import Beat, PrimitiveContext
from .primitives.diagrams import SECTION_BUILDERS, build_section_visual
from .primitives.registry import build_visual
from .primitives.runner import fit_into_box
from .primitives.frame import add_brand_frame
from .primitives.layout import code_block, fit, header, panel, text, wrap_text
from .speech import build_speech_service

# Layout constants (Manim units). Content stays above brand.CONTENT_SAFE_BOTTOM_Y.
SLIDE_CENTER_Y = -0.3
SLIDE_HEIGHT = 4.6
FULL_PANEL_WIDTH = 11.6
FULL_WRAP = 62
FULL_FONT = 26
SPLIT_PANEL_WIDTH = 6.25
SPLIT_WRAP = 46
SPLIT_FONT = 23
VISUAL_PANEL_WIDTH = 5.4
CODE_MAX_WIDTH = 11.5
CODE_MAX_HEIGHT = 4.0
CODE_CENTER_Y = 0.05
SECTION_BEAT = 0.45


def section_layout(section: LessonSection) -> str:
    """"split" when the section supplies an explicit visual, else "full"."""
    return "split" if section.visual else "full"


@dataclass
class SlideParts:
    layout: str
    header: VGroup
    bullet_panel: VGroup
    bullets: VGroup
    visual_panel: Optional[VGroup] = None
    visual_label: Optional[VGroup] = None
    visual: Optional[VGroup] = None
    # Animated primitives reveal in beats; static diagrams fade in at once.
    visual_beats: Optional[List[Beat]] = None

    @property
    def group(self) -> VGroup:
        parts = [self.header, self.bullet_panel, self.bullets]
        parts += [part for part in (self.visual_panel, self.visual_label, self.visual) if part is not None]
        return VGroup(*parts)


def bullet_group(bullets: List[str], fonts: BrandFonts, wrap: int, size: float, max_width: float) -> VGroup:
    lines = [text(wrap_text(bullet, wrap), fonts, size, line_spacing=0.86) for bullet in bullets[:4]]
    # One shared scale keeps every bullet the same type size.
    scale = min([1.0] + [max_width / line.width for line in lines])
    rows = VGroup()
    for line in lines:
        line.scale(scale)
        dot = Dot(radius=0.055, color=brand.MINT)
        rows.add(VGroup(dot, line).arrange(RIGHT, buff=0.18, aligned_edge=UP))
    return rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)


def build_section_slide(section: LessonSection, number: int, total: int, fonts: BrandFonts) -> SlideParts:
    """Build one explanation slide without a Scene (testable offline)."""
    slide_header = header(f"Step {number} of {total}", section.title, fonts)
    layout = section_layout(section)
    if layout == "full":
        bullet_panel = panel(FULL_PANEL_WIDTH, SLIDE_HEIGHT).move_to(UP * SLIDE_CENTER_Y)
        bullets = bullet_group(section.bullets, fonts, FULL_WRAP, FULL_FONT, FULL_PANEL_WIDTH - 1.2)
        fit(bullets, FULL_PANEL_WIDTH - 1.0, SLIDE_HEIGHT - 0.6)
        bullets.move_to(bullet_panel).align_to(bullet_panel, LEFT).shift(RIGHT * 0.5)
        return SlideParts(layout, slide_header, bullet_panel, bullets)

    bullet_panel = panel(SPLIT_PANEL_WIDTH, SLIDE_HEIGHT).move_to(LEFT * 3.35 + UP * SLIDE_CENTER_Y)
    bullets = bullet_group(section.bullets, fonts, SPLIT_WRAP, SPLIT_FONT, SPLIT_PANEL_WIDTH - 0.95)
    fit(bullets, SPLIT_PANEL_WIDTH - 0.7, SLIDE_HEIGHT - 0.5)
    bullets.move_to(bullet_panel).align_to(bullet_panel, LEFT).shift(RIGHT * 0.38)

    visual_panel = panel(
        VISUAL_PANEL_WIDTH, SLIDE_HEIGHT, stroke_color=brand.CYAN, stroke_opacity=0.45, fill_opacity=0.82,
    ).move_to(RIGHT * 3.05 + UP * SLIDE_CENTER_Y)
    title = section.visual.get("title")
    visual_label = None
    top_reserved = 0.3
    if title:
        # Shown as written: titles often hold code (range(1, 6), marks[i]).
        visual_label = VGroup(fit(text(title, fonts, 15, color=brand.MUTED, bold=True), VISUAL_PANEL_WIDTH - 0.5))
        visual_label.move_to(visual_panel.get_top() + DOWN * 0.3)
        top_reserved = 0.6
    width, height = VISUAL_PANEL_WIDTH - 0.6, SLIDE_HEIGHT - top_reserved - 0.3
    beats = None
    if section.visual["type"] in SECTION_BUILDERS:
        visual = build_section_visual(section.visual, fonts, width, height)
    else:
        built = build_visual(section.visual, PrimitiveContext(fonts=fonts))
        visual, beats = built.extent, built.beats
        fit_into_box(visual, _box_around(ORIGIN, width, height), center=True)
    visual.move_to(visual_panel).shift(DOWN * (top_reserved - 0.3) / 2)
    return SlideParts(layout, slide_header, bullet_panel, bullets, visual_panel, visual_label, visual, beats)


def _box_around(center, width: float, height: float) -> Tuple[float, float, float, float]:
    return (center[0] - width / 2, center[0] + width / 2, center[1] - height / 2, center[1] + height / 2)


class ConfigDrivenLesson(VoiceoverScene):
    """One visual template driven entirely by a saved lesson configuration."""

    LESSON_CONFIG_PATH: Path
    LESSON_PACKAGE_PATH: Optional[Path] = None

    def construct(self) -> None:
        self.lesson = load_config(Path(self.LESSON_CONFIG_PATH))
        self.voiceover_enabled = self.lesson.voiceover.enabled
        self.fonts = brand_fonts()
        self.script = {segment.id: segment.text for segment in standard_script(self.lesson)}
        if self.voiceover_enabled:
            project_root = Path(__file__).resolve().parents[1]
            # Captions come from emit_subcaptions, in both voiceover modes.
            self.set_speech_service(
                build_speech_service(self.lesson.voiceover, project_root), create_subcaption=False,
            )

        add_brand_frame(self, self.fonts, style="calm")
        self._show_intro()
        for number, section in enumerate(self.lesson.sections, 1):
            self._show_explanation(number, section)
        self._show_code()
        self._show_summary()
        self._show_outro()

    def _narrate(self, text_value: str, action: Callable[[], None]) -> None:
        narration = " ".join(text_value.split())
        if self.voiceover_enabled:
            with self.voiceover(text=narration) as tracker:
                emit_subcaptions(self, narration, tracker.duration)
                action()
        else:
            start = self.time
            action()
            self.wait(min(1.4, max(0.35, len(narration.split()) * 0.025)))
            elapsed = self.time - start
            emit_subcaptions(self, narration, elapsed, offset=-elapsed)

    def _show_intro(self) -> None:
        pill_text = fit(
            text(f"{self.lesson.language.upper()}  •  {self.lesson.topic.upper()}", self.fonts, 16, color=brand.CYAN),
            5.8,
        )
        pill_box = panel(pill_text.width + 0.55, 0.46, corner_radius=0.22, stroke_opacity=1)
        pill = VGroup(pill_box, pill_text)
        title = fit(text(self.lesson.title, self.fonts, 52, bold=True), 11.0)
        title.set_color_by_gradient(brand.CYAN, brand.ACCENT)
        topic = fit(text(self.lesson.topic, self.fonts, 31), 10.0)
        underline = Line(LEFT, RIGHT, color=brand.CYAN, stroke_width=5).set_width(2.2)
        group = VGroup(pill, title, topic, underline).arrange(DOWN, buff=0.28)

        def animate() -> None:
            self.play(FadeIn(pill, shift=DOWN * 0.12), FadeIn(title, shift=UP * 0.18), run_time=0.8)
            self.play(FadeIn(topic), GrowFromCenter(underline), run_time=0.65)

        self._narrate(self.script["intro"], animate)
        self.wait(0.3)
        self.play(FadeOut(group, shift=UP * 0.1), run_time=0.55)

    def _show_explanation(self, number: int, section: LessonSection) -> None:
        parts = build_section_slide(section, number, len(self.lesson.sections), self.fonts)
        narration = self.script[f"section_{number:02d}"]

        def animate() -> None:
            self.play(FadeIn(parts.header, shift=DOWN * 0.12), run_time=0.45)
            panels = [FadeIn(parts.bullet_panel)]
            if parts.visual_panel is not None:
                panels.append(FadeIn(parts.visual_panel))
            if parts.visual_label is not None:
                panels.append(FadeIn(parts.visual_label))
            self.play(*panels, run_time=0.5)
            self.play(*[FadeIn(row, shift=RIGHT * 0.12) for row in parts.bullets], run_time=0.8)
            if parts.visual_beats:
                for beat in parts.visual_beats:
                    beat(self, SECTION_BEAT)
            elif parts.visual is not None:
                self.play(FadeIn(parts.visual, shift=UP * 0.1), run_time=0.8)

        self._narrate(narration, animate)
        self.wait(0.25)
        self.play(FadeOut(parts.group), run_time=0.5)

    def _pygments_language(self) -> str:
        value = self.lesson.language.lower().strip()
        aliases = {
            "c++": "cpp", "cplusplus": "cpp", "c plus plus": "cpp",
            "c#": "csharp", "javascript": "javascript", "js": "javascript",
            "python": "python", "sql": "sql", "java": "java", "c": "c",
        }
        return aliases.get(value, "text")

    def _show_code(self) -> None:
        code_header = header("Code walkthrough", f"{self.lesson.language} Example", self.fonts)
        code = fit(code_block(self.lesson.code_example, self._pygments_language(), self.fonts), CODE_MAX_WIDTH, CODE_MAX_HEIGHT)
        code.move_to(UP * CODE_CENTER_Y)
        callout_text = text("Read the code from top to bottom", self.fonts, 18, color=brand.MINT, bold=True)
        callout_box = panel(
            callout_text.width + 0.5, 0.46, stroke_color=brand.MINT, corner_radius=0.12,
            stroke_opacity=1, fill_color=brand.PANEL_2, fill_opacity=1,
        ).move_to(callout_text)
        callout = VGroup(callout_box, callout_text).next_to(code, DOWN, buff=0.18)
        content = VGroup(code_header, code, callout)

        def animate() -> None:
            self.play(FadeIn(code_header), run_time=0.4)
            self.play(Create(code), run_time=1.0)
            self.play(FadeIn(callout, shift=UP * 0.1), run_time=0.4)

        self._narrate(self.script["code"], animate)
        self.wait(0.35)
        self.play(FadeOut(content), run_time=0.55)

    def _show_summary(self) -> None:
        summary_header = header("Quick recap", "What You Learned", self.fonts)
        rows = bullet_group(self.lesson.summary, self.fonts, SPLIT_WRAP + 10, SPLIT_FONT, 9.4)
        summary_panel = panel(10.6, 4.5, stroke_color=brand.MINT, stroke_width=2, stroke_opacity=1, corner_radius=0.2)
        summary_panel.move_to(UP * SLIDE_CENTER_Y)
        rows.move_to(summary_panel).align_to(summary_panel, LEFT).shift(RIGHT * 0.65)
        content = VGroup(summary_header, summary_panel, rows)

        def animate() -> None:
            self.play(FadeIn(summary_header), FadeIn(summary_panel, scale=0.98), run_time=0.55)
            self.play(*[FadeIn(row, shift=RIGHT * 0.15) for row in rows], run_time=0.85)

        self._narrate(self.script["summary"], animate)
        self.wait(0.35)
        self.play(FadeOut(content), run_time=0.55)

    def _show_outro(self) -> None:
        thanks = text("Keep Learning. Keep Building.", self.fonts, 43, bold=True)
        thanks.set_color_by_gradient(brand.CYAN, brand.ACCENT)
        brand_name = text("AI SANKALP", self.fonts, 27, color=brand.MINT, bold=True)
        line = Line(LEFT, RIGHT, color=brand.CYAN, stroke_width=4).set_width(2.1)
        group = VGroup(thanks, line, brand_name).arrange(DOWN, buff=0.3)

        def animate() -> None:
            self.play(FadeIn(thanks, shift=UP * 0.15), GrowFromCenter(line), run_time=0.75)
            self.play(FadeIn(brand_name), run_time=0.4)

        self._narrate(self.script["outro"], animate)
        self.wait(0.6)
