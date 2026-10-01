from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import Callable, List

from manim import (
    BLUE, BOLD, DOWN, FadeIn, FadeOut, GrowArrow, GrowFromCenter, LEFT, Line,
    ORIGIN, RIGHT, RoundedRectangle, Scene, SVGMobject, Text, UP, UR, VGroup,
    WHITE, Write, Arrow, Circle, Code, Create, Dot, config,
)
from manim_voiceover import VoiceoverScene

from .config_io import load_config
from .speech import build_speech_service


BG = "#071321"
PANEL = "#10243A"
PANEL_2 = "#16324F"
ACCENT = "#1473E6"
CYAN = "#21D4FD"
MINT = "#55E6C1"
GOLD = "#FFC857"
SOFT_WHITE = "#F5F9FF"
MUTED = "#9EB3C7"
CORAL = "#FF6B6B"


def _wrap(value: str, width: int) -> str:
    return textwrap.fill(" ".join(value.split()), width=width, break_long_words=False)


def _keywords(lines: List[str], limit: int = 3) -> List[str]:
    stop = {
        "about", "after", "also", "and", "because", "before", "from", "have",
        "into", "that", "the", "their", "then", "this", "through", "using", "when",
        "where", "which", "with", "your", "will", "each", "value", "values",
    }
    result: List[str] = []
    for line in lines:
        words = [word for word in re.findall(r"[A-Za-z_][A-Za-z0-9_+.#-]*", line) if word.lower() not in stop]
        label = " ".join(words[:3]).strip() or f"Idea {len(result) + 1}"
        label = label[:28]
        if label.lower() not in {item.lower() for item in result}:
            result.append(label)
        if len(result) == limit:
            break
    while len(result) < min(3, max(1, len(lines))):
        result.append(f"Concept {len(result) + 1}")
    return result


class ConfigDrivenLesson(VoiceoverScene):
    """One visual template driven entirely by a saved lesson configuration."""

    LESSON_CONFIG_PATH: Path

    def construct(self) -> None:
        self.lesson = load_config(Path(self.LESSON_CONFIG_PATH))
        self.voiceover_enabled = self.lesson.voiceover.enabled
        self.camera.background_color = BG
        if self.voiceover_enabled:
            project_root = Path(__file__).resolve().parents[1]
            self.set_speech_service(
                build_speech_service(self.lesson.voiceover, project_root), create_subcaption=True,
            )

        self._add_background()
        self._add_branding()
        self._show_intro()
        for number, section in enumerate(self.lesson.sections, 1):
            self._show_explanation(number, section)
        self._show_code()
        self._show_summary()
        self._show_outro()

    def _narrate(self, text: str, action: Callable[[], None]) -> None:
        narration = " ".join(text.split())
        if self.voiceover_enabled:
            with self.voiceover(text=narration):
                action()
        else:
            action()
            self.wait(min(1.4, max(0.35, len(narration.split()) * 0.025)))

    @staticmethod
    def _fit(mobject, max_width: float, max_height: float | None = None):
        if mobject.width > max_width:
            mobject.scale_to_fit_width(max_width)
        if max_height is not None and mobject.height > max_height:
            mobject.scale_to_fit_height(max_height)
        return mobject

    def _add_background(self) -> None:
        ambience = VGroup(
            Circle(radius=3.2, color=ACCENT, stroke_width=2, stroke_opacity=0.08).shift(LEFT * 6 + DOWN * 3),
            Circle(radius=2.4, color=CYAN, stroke_width=2, stroke_opacity=0.07).shift(RIGHT * 6 + UP * 3),
            Line(LEFT * 7, RIGHT * 7, color=ACCENT, stroke_width=1, stroke_opacity=0.16).to_edge(DOWN, buff=0.38),
        )
        self.add(ambience)

    def _add_branding(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        logo_path = project_root / "assets" / "ai_sankalp_logo.svg"
        if logo_path.exists():
            logo = SVGMobject(str(logo_path)).set(width=0.67)
        else:
            logo = Text("AS", font_size=24, weight=BOLD, color=ACCENT)
        badge = RoundedRectangle(
            width=0.98, height=0.86, corner_radius=0.12,
            stroke_color=ACCENT, stroke_width=1, fill_color=WHITE, fill_opacity=1,
        ).move_to(logo)
        brand = VGroup(badge, logo).to_corner(UR, buff=0.18)
        footer = Text(
            "AI SANKALP  •  VISUAL LEARNING", font_size=13, color=MUTED, weight=BOLD,
        ).to_edge(DOWN, buff=0.13).to_edge(LEFT, buff=0.3)
        self.add_foreground_mobjects(brand, footer)

    def _header(self, eyebrow: str, title: str) -> VGroup:
        eyebrow_text = Text(eyebrow.upper(), font_size=15, color=CYAN, weight=BOLD)
        title_text = self._fit(Text(title, font_size=36, color=SOFT_WHITE, weight=BOLD), 11.2)
        accent = Line(LEFT, RIGHT, color=CYAN, stroke_width=4).set_width(1.65)
        group = VGroup(eyebrow_text, title_text, accent).arrange(DOWN, buff=0.11, aligned_edge=LEFT)
        group.to_edge(UP, buff=0.24).to_edge(LEFT, buff=0.48)
        return group

    def _show_intro(self) -> None:
        pill_text = Text(f"{self.lesson.language.upper()}  •  {self.lesson.topic.upper()}", font_size=16, color=CYAN)
        self._fit(pill_text, 5.8)
        pill_box = RoundedRectangle(
            width=pill_text.width + 0.55, height=0.46, corner_radius=0.22,
            stroke_color=ACCENT, fill_color=PANEL, fill_opacity=0.96,
        )
        pill = VGroup(pill_box, pill_text)
        title = self._fit(Text(self.lesson.title, font_size=52, weight=BOLD, color=SOFT_WHITE), 11.0)
        title.set_color_by_gradient(CYAN, ACCENT)
        topic = self._fit(Text(self.lesson.topic, font_size=31, color=SOFT_WHITE), 10.0)
        underline = Line(LEFT, RIGHT, color=CYAN, stroke_width=5).set_width(2.2)
        group = VGroup(pill, title, topic, underline).arrange(DOWN, buff=0.28)

        def animate() -> None:
            self.play(FadeIn(pill, shift=DOWN * 0.12), FadeIn(title, shift=UP * 0.18), run_time=0.8)
            self.play(FadeIn(topic), GrowFromCenter(underline), run_time=0.65)

        self._narrate(
            f"Welcome to AI Sankalp. In this lesson, we will learn {self.lesson.topic} using {self.lesson.language}, step by step.",
            animate,
        )
        self.wait(0.3)
        self.play(FadeOut(group, shift=UP * 0.1), run_time=0.55)

    def _bullet_group(self, bullets: List[str]) -> VGroup:
        rows = VGroup()
        for bullet in bullets[:4]:
            dot = Dot(radius=0.055, color=MINT)
            text = Text(_wrap(bullet, 43), font_size=23, color=SOFT_WHITE, line_spacing=0.86)
            self._fit(text, 5.3)
            row = VGroup(dot, text).arrange(RIGHT, buff=0.18, aligned_edge=UP)
            rows.add(row)
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        return rows

    def _visual_flow(self, bullets: List[str]) -> VGroup:
        labels = _keywords(bullets)
        nodes = VGroup()
        arrows = VGroup()
        colors = [CYAN, GOLD, MINT]
        for index, label in enumerate(labels):
            text = Text(_wrap(label, 16), font_size=20, color=SOFT_WHITE, weight=BOLD)
            self._fit(text, 2.65, 0.55)
            box = RoundedRectangle(
                width=3.15, height=0.92, corner_radius=0.13,
                stroke_color=colors[index % len(colors)], stroke_width=2,
                fill_color=PANEL_2, fill_opacity=1,
            )
            nodes.add(VGroup(box, text))
        nodes.arrange(DOWN, buff=0.55)
        for index in range(len(nodes) - 1):
            arrows.add(Arrow(
                nodes[index].get_bottom(), nodes[index + 1].get_top(), buff=0.08,
                color=ACCENT, stroke_width=2.5, max_tip_length_to_length_ratio=0.18,
            ))
        return VGroup(nodes, arrows)

    def _show_explanation(self, number, section) -> None:
        header = self._header(f"Step {number} of {len(self.lesson.sections)}", section.title)
        bullet_group = self._bullet_group(section.bullets)
        bullet_panel = RoundedRectangle(
            width=6.25, height=4.65, corner_radius=0.18,
            stroke_color=ACCENT, stroke_opacity=0.55, fill_color=PANEL, fill_opacity=0.96,
        )
        bullet_group.move_to(bullet_panel).align_to(bullet_panel, LEFT).shift(RIGHT * 0.38)
        left = VGroup(bullet_panel, bullet_group).move_to(LEFT * 3.35 + DOWN * 0.4)

        visual_label = Text("VISUAL MODEL", font_size=14, color=MUTED, weight=BOLD)
        flow = self._visual_flow(section.bullets)
        visual_panel = RoundedRectangle(
            width=5.4, height=4.65, corner_radius=0.18,
            stroke_color=CYAN, stroke_opacity=0.45, fill_color=PANEL, fill_opacity=0.82,
        )
        flow.move_to(visual_panel).shift(DOWN * 0.12)
        visual_label.move_to(visual_panel.get_top() + DOWN * 0.3)
        right = VGroup(visual_panel, visual_label, flow).move_to(RIGHT * 3.05 + DOWN * 0.4)
        content = VGroup(header, left, right)
        narration = section.narration or f"{section.title}. " + " ".join(section.bullets)

        def animate() -> None:
            self.play(FadeIn(header, shift=DOWN * 0.12), run_time=0.45)
            self.play(FadeIn(bullet_panel), FadeIn(visual_panel), FadeIn(visual_label), run_time=0.5)
            self.play(*[FadeIn(row, shift=RIGHT * 0.12) for row in bullet_group], run_time=0.8)
            self.play(*[FadeIn(node, shift=UP * 0.1) for node in flow[0]], run_time=0.7)
            if len(flow[1]):
                self.play(*[GrowArrow(arrow) for arrow in flow[1]], run_time=0.5)

        self._narrate(narration, animate)
        self.wait(0.25)
        self.play(FadeOut(content), run_time=0.5)

    def _pygments_language(self) -> str:
        value = self.lesson.language.lower().strip()
        aliases = {
            "c++": "cpp", "cplusplus": "cpp", "c plus plus": "cpp",
            "c#": "csharp", "javascript": "javascript", "js": "javascript",
            "python": "python", "sql": "sql", "java": "java", "c": "c",
        }
        return aliases.get(value, "text")

    def _show_code(self) -> None:
        header = self._header("Code walkthrough", f"{self.lesson.language} Example")
        try:
            code = Code(
                code_string=self.lesson.code_example,
                language=self._pygments_language(),
                formatter_style="monokai",
                add_line_numbers=True,
                background="window",
            )
        except Exception:
            code = Text(_wrap(self.lesson.code_example, 70), font="Monospace", font_size=19, color=SOFT_WHITE)
        self._fit(code, 11.5, 4.9)
        code.move_to(DOWN * 0.32)
        callout_text = Text("Read the code from top to bottom", font_size=18, color=MINT, weight=BOLD)
        callout_box = RoundedRectangle(
            width=callout_text.width + 0.5, height=0.46, corner_radius=0.12,
            stroke_color=MINT, fill_color=PANEL_2, fill_opacity=1,
        ).move_to(callout_text)
        callout = VGroup(callout_box, callout_text).next_to(code, DOWN, buff=0.22)
        content = VGroup(header, code, callout)

        def animate() -> None:
            self.play(FadeIn(header), run_time=0.4)
            self.play(Create(code), run_time=1.0)
            self.play(FadeIn(callout, shift=UP * 0.1), run_time=0.4)

        self._narrate(
            f"Now let us connect the idea to code. This {self.lesson.language} example demonstrates {self.lesson.topic}. Read each line and connect it to the steps we just learned.",
            animate,
        )
        self.wait(0.35)
        self.play(FadeOut(content), run_time=0.55)

    def _show_summary(self) -> None:
        header = self._header("Quick recap", "What You Learned")
        rows = self._bullet_group(self.lesson.summary)
        panel = RoundedRectangle(
            width=10.6, height=4.5, corner_radius=0.2,
            stroke_color=MINT, stroke_width=2, fill_color=PANEL, fill_opacity=0.97,
        )
        rows.move_to(panel).align_to(panel, LEFT).shift(RIGHT * 0.65)
        content = VGroup(header, panel, rows)

        def animate() -> None:
            self.play(FadeIn(header), FadeIn(panel, scale=0.98), run_time=0.55)
            self.play(*[FadeIn(row, shift=RIGHT * 0.15) for row in rows], run_time=0.85)

        self._narrate("Let us recap. " + " ".join(self.lesson.summary), animate)
        self.wait(0.35)
        self.play(FadeOut(content), run_time=0.55)

    def _show_outro(self) -> None:
        thanks = Text("Keep Learning. Keep Building.", font_size=43, weight=BOLD, color=SOFT_WHITE)
        thanks.set_color_by_gradient(CYAN, ACCENT)
        brand = Text("AI SANKALP", font_size=27, color=MINT, weight=BOLD)
        line = Line(LEFT, RIGHT, color=CYAN, stroke_width=4).set_width(2.1)
        group = VGroup(thanks, line, brand).arrange(DOWN, buff=0.3)

        def animate() -> None:
            self.play(FadeIn(thanks, shift=UP * 0.15), GrowFromCenter(line), run_time=0.75)
            self.play(FadeIn(brand), run_time=0.4)

        self._narrate("Thank you for learning with AI Sankalp. Keep learning, and keep building.", animate)
        self.wait(0.6)
