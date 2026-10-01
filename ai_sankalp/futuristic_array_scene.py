from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Dict, List, Optional

from manim import (
    Arrow, BOLD, Circle, Create, DashedLine, Dot, DOWN, FadeIn, FadeOut, Flash,
    GrowArrow, GrowFromCenter, Indicate, LaggedStart, LEFT, Line, MoveAlongPath, PI,
    RIGHT, RoundedRectangle, Text, Transform, Triangle, UP, VGroup, linear, smooth,
    there_and_back,
)
from manim_voiceover import VoiceoverScene

from .brand import (
    ACCENT_CYCLE, CORAL, CYAN, ELECTRIC, GOLD, MINT, MUTED, PANEL, PANEL_2, SOFT_WHITE, VIOLET, brand_fonts,
)
from .config_io import load_config
from .package import load_package, resolve_package_path  # noqa: F401  (re-exported)
from .primitives.frame import add_brand_frame
from .primitives.layout import code_block, fit, glass_card, section_label, title_text
from .speech import build_speech_service


class FuturisticArrayLesson(VoiceoverScene):
    """A cinematic, diagram-first C++ array lesson driven by the rich package."""

    LESSON_CONFIG_PATH: Path
    LESSON_PACKAGE_PATH: Optional[Path] = None

    def construct(self) -> None:
        self.lesson = load_config(Path(self.LESSON_CONFIG_PATH))
        project_root = Path(__file__).resolve().parents[1]
        package_path = self.LESSON_PACKAGE_PATH or resolve_package_path(project_root, self.lesson.slug)
        package = load_package(package_path)
        self.script: Dict[str, str] = {scene["id"]: scene["voiceover"] for scene in package["scenes"]}

        self.fonts = brand_fonts()
        if self.lesson.voiceover.enabled:
            self.set_speech_service(
                build_speech_service(self.lesson.voiceover, project_root),
                create_subcaption=True,
            )

        frame = add_brand_frame(self, self.fonts, style="grid")
        self.logo = frame.logo
        self.ambient_orbit = frame.ambient
        self._show_intro()
        self._show_motivation()
        self._show_mental_model()
        self._show_declaration()
        self._show_indexing()
        self._show_code()
        self._show_trace()
        self._show_mistake()
        self._show_practice()
        self._show_summary_and_outro()

    @staticmethod
    def _fit(mobject, max_width: float, max_height: float | None = None):
        return fit(mobject, max_width, max_height)

    def _section_label(self, value: str):
        return section_label(value, self.fonts)

    def _title(self, value: str, size: int = 40):
        return title_text(value, self.fonts, size)

    def _sentences(self, scene_id: str) -> List[str]:
        return [piece.strip() for piece in re.findall(r"[^.!?]+(?:[.!?]+|$)", self.script[scene_id]) if piece.strip()]

    def _narrate(self, scene_id: str, actions: List[Callable[[float], None]]) -> None:
        sentences = self._sentences(scene_id)
        for index, sentence in enumerate(sentences):
            action = actions[index] if index < len(actions) else None
            if self.lesson.voiceover.enabled:
                with self.voiceover(text=sentence) as tracker:
                    duration = max(0.55, min(3.4, tracker.duration * 0.78))
                    if action is not None:
                        action(duration)
                    else:
                        self.play(self.ambient_orbit.animate.rotate(PI / 8), run_time=duration, rate_func=smooth)
            else:
                if action is not None:
                    action(0.75)
                else:
                    self.wait(0.5)

    def _array_cells(self, values, indexes=True, scale=1.0) -> VGroup:
        cells = VGroup()
        colors = ACCENT_CYCLE
        for index, value in enumerate(values):
            color = colors[index % len(colors)]
            glow = RoundedRectangle(
                width=1.48, height=1.38, corner_radius=0.18,
                stroke_color=color, stroke_width=8, stroke_opacity=0.10,
            )
            shell = RoundedRectangle(
                width=1.42, height=1.32, corner_radius=0.18,
                stroke_color=color, stroke_width=2.2,
                fill_color=PANEL_2, fill_opacity=0.96,
            )
            inner = RoundedRectangle(
                width=1.17, height=0.84, corner_radius=0.12,
                stroke_color=SOFT_WHITE, stroke_opacity=0.08,
                fill_color=PANEL, fill_opacity=0.8,
            ).shift(DOWN * 0.07)
            value_text = Text(str(value), font=self.fonts.sans, font_size=31, color=SOFT_WHITE, weight=BOLD).shift(DOWN * 0.08)
            index_text = Text(f"[{index}]", font=self.fonts.mono, font_size=15, color=color, weight=BOLD).shift(UP * 0.48)
            port = Dot(radius=0.045, color=color).next_to(shell, DOWN, buff=0.02)
            cell = VGroup(glow, shell, inner, value_text, index_text, port)
            if not indexes:
                index_text.set_opacity(0)
            cells.add(cell)
        cells.arrange(RIGHT, buff=0.12).scale(scale)
        return cells

    def _glass_card(self, text: str, color=CYAN, width=2.55, height=0.82, font_size=22) -> VGroup:
        return glass_card(text, self.fonts, color=color, width=width, height=height, font_size=font_size)

    def _clear(self, *groups) -> None:
        visible = [group for group in groups if group is not None]
        if visible:
            self.play(*[FadeOut(group, shift=UP * 0.08) for group in visible], run_time=0.55)

    def _show_intro(self) -> None:
        eyebrow = Text("C++  •  MEMORY VISUALIZED", font=self.fonts.sans, font_size=16, color=CYAN, weight=BOLD)
        title = Text("ARRAYS", font=self.fonts.sans, font_size=84, color=SOFT_WHITE, weight=BOLD)
        title.set_color_by_gradient(CYAN, ELECTRIC, VIOLET)
        subtitle = Text("Store  •  Access  •  Traverse", font=self.fonts.sans, font_size=27, color=MUTED)
        title_group = VGroup(eyebrow, title, subtitle).arrange(DOWN, buff=0.18).shift(UP * 1.2)
        lane = self._array_cells([70, 85, 90, 75, 88], indexes=False, scale=0.88).shift(DOWN * 1.15)
        rail = Line(lane.get_left() + LEFT * 0.4, lane.get_right() + RIGHT * 0.4, color=CYAN, stroke_width=2, stroke_opacity=0.42)
        rail.next_to(lane, DOWN, buff=0.18)
        signal = Dot(rail.get_start(), radius=0.07, color=MINT)
        group = VGroup(title_group, lane, rail, signal)

        actions = [
            lambda d: self.play(FadeIn(eyebrow, shift=DOWN * 0.12), run_time=d),
            lambda d: self.play(FadeIn(title, scale=0.92), FadeIn(subtitle, shift=UP * 0.12), run_time=d),
            lambda d: self.play(LaggedStart(*[FadeIn(cell, shift=UP * 0.18) for cell in lane], lag_ratio=0.1), Create(rail), run_time=d),
            lambda d: self.play(MoveAlongPath(signal, rail), run_time=d, rate_func=linear),
        ]
        self._narrate("scene_01_intro", actions)
        self._clear(group)

    def _show_motivation(self) -> None:
        label = self._section_label("01 / WHY ARRAYS")
        title = self._title("From scattered values to one data lane")
        loose = VGroup(*[
            self._glass_card(f"mark{i + 1}  =  {value}", color=ACCENT_CYCLE[i], width=2.25)
            for i, value in enumerate([70, 85, 90, 75, 88])
        ])
        loose.arrange_in_grid(rows=2, cols=3, buff=(0.35, 0.3)).shift(DOWN * 0.45)
        count = Text("5 names  →  1 array", font=self.fonts.sans, font_size=26, color=GOLD, weight=BOLD).to_edge(DOWN, buff=0.65)
        lane = self._array_cells([70, 85, 90, 75, 88], indexes=False).shift(DOWN * 0.3)
        array_name = self._glass_card("marks", color=MINT, width=1.7, height=0.62, font_size=21).next_to(lane, UP, buff=0.35)
        group = VGroup(label, title, loose, count)

        actions = [
            lambda d: self.play(FadeIn(label), FadeIn(title, shift=DOWN * 0.12), run_time=d),
            lambda d: self.play(LaggedStart(*[FadeIn(card, scale=0.9) for card in loose], lag_ratio=0.1), run_time=d),
            lambda d: self.play(FadeIn(count, shift=UP * 0.1), loose.animate.scale(1.03), run_time=d, rate_func=there_and_back),
            lambda d: self.play(loose.animate.scale(0.88), run_time=d, rate_func=there_and_back),
            lambda d: self.play(Transform(loose, lane), FadeIn(array_name, shift=DOWN * 0.12), FadeOut(count), run_time=d),
            lambda d: self.play(Flash(array_name.get_center(), color=MINT, flash_radius=0.8), run_time=d),
        ]
        self._narrate("scene_02_motivation", actions)
        self._clear(label, title, loose, array_name)

    def _show_mental_model(self) -> None:
        label = self._section_label("02 / MENTAL MODEL")
        title = self._title("A fixed-size lane in memory")
        lane = self._array_cells([70, 85, 90, 75, 88]).shift(UP * 0.45)
        addresses = VGroup(*[
            Text(str(4096 + i * 4), font=self.fonts.mono, font_size=14, color=MUTED)
            for i in range(5)
        ])
        for address, cell in zip(addresses, lane):
            address.next_to(cell, DOWN, buff=0.38)
        bus = Line(lane.get_left() + LEFT * 0.3, lane.get_right() + RIGHT * 0.3, color=CYAN, stroke_width=3, stroke_opacity=0.5)
        bus.next_to(addresses, DOWN, buff=0.22)
        packet = Dot(bus.get_start(), radius=0.08, color=MINT)
        chips = VGroup(
            self._glass_card("same type  •  int", color=CYAN, width=2.5),
            self._glass_card("fixed size  •  5", color=VIOLET, width=2.5),
            self._glass_card("consecutive storage", color=MINT, width=2.9),
        ).arrange(RIGHT, buff=0.25).to_edge(DOWN, buff=0.55)
        group = VGroup(label, title, lane, addresses, bus, packet, chips)

        actions = [
            lambda d: self.play(FadeIn(label), FadeIn(title), run_time=d),
            lambda d: self.play(LaggedStart(*[GrowFromCenter(cell) for cell in lane], lag_ratio=0.1), run_time=d),
            lambda d: self.play(FadeIn(chips[0], shift=UP * 0.12), run_time=d),
            lambda d: self.play(FadeIn(chips[1], shift=UP * 0.12), run_time=d),
            lambda d: self.play(FadeIn(addresses), Create(bus), run_time=d),
            lambda d: self.play(MoveAlongPath(packet, bus), FadeIn(chips[2], shift=UP * 0.12), run_time=d, rate_func=linear),
            lambda d: self.play(lane.animate.shift(UP * 0.06), run_time=d, rate_func=there_and_back),
        ]
        self._narrate("scene_03_explanation", actions)
        self._clear(group)

    def _show_declaration(self) -> None:
        label = self._section_label("03 / BUILD THE ARRAY")
        title = self._title("Watch the declaration assemble")
        tokens = VGroup(
            self._glass_card("int", color=CYAN, width=1.35),
            self._glass_card("marks", color=GOLD, width=1.8),
            self._glass_card("[5]", color=MINT, width=1.35),
            self._glass_card("{70, 85, 90, 75, 88}", color=VIOLET, width=4.35),
        ).arrange(RIGHT, buff=0.2).shift(UP * 0.7)
        captions = VGroup(*[
            Text(text, font=self.fonts.sans, font_size=16, color=color)
            for text, color in [("type", CYAN), ("name", GOLD), ("size", MINT), ("starting values", VIOLET)]
        ])
        for caption, token in zip(captions, tokens):
            caption.next_to(token, UP, buff=0.17)
        code_line = Text("int marks[5] = {70, 85, 90, 75, 88};", font=self.fonts.mono, font_size=29, color=SOFT_WHITE)
        code_panel = RoundedRectangle(
            width=code_line.width + 0.75, height=0.95, corner_radius=0.16,
            stroke_color=ELECTRIC, fill_color=PANEL, fill_opacity=0.96,
        ).move_to(code_line)
        code_group = VGroup(code_panel, code_line).shift(UP * 0.55)
        lane = self._array_cells([70, 85, 90, 75, 88], indexes=False, scale=0.9).shift(DOWN * 1.2)
        arrows = VGroup(*[
            Arrow(code_group.get_bottom() + RIGHT * offset, lane[i].get_top(), buff=0.12, color=CYAN, stroke_width=1.6, max_tip_length_to_length_ratio=0.12)
            for i, offset in enumerate([-2.4, -1.2, 0, 1.2, 2.4])
        ])
        group = VGroup(label, title, tokens, captions)

        actions = [
            lambda d: self.play(FadeIn(label), FadeIn(title), run_time=d),
            lambda d: self.play(LaggedStart(*[FadeIn(token, shift=UP * 0.15) for token in tokens], lag_ratio=0.1), run_time=d),
            lambda d: self.play(FadeIn(captions[0]), Indicate(tokens[0], color=CYAN), run_time=d),
            lambda d: self.play(FadeIn(captions[1]), Indicate(tokens[1], color=GOLD), run_time=d),
            lambda d: self.play(FadeIn(captions[2]), Indicate(tokens[2], color=MINT), run_time=d),
            lambda d: self.play(FadeOut(captions), Transform(tokens, code_group), run_time=d),
            lambda d: self.play(FadeIn(lane), LaggedStart(*[GrowArrow(arrow) for arrow in arrows], lag_ratio=0.08), run_time=d),
            lambda d: self.play(Flash(lane[2].get_center(), color=CYAN, flash_radius=0.7), run_time=d),
        ]
        self._narrate("scene_04_indexing", actions)
        self._clear(label, title, tokens, lane, arrows)

    def _show_indexing(self) -> None:
        label = self._section_label("04 / ZERO-BASED INDEX")
        title = self._title("The index is an offset from the start")
        lane = self._array_cells([70, 85, 90, 75, 88]).shift(UP * 0.35)
        access = self._glass_card("marks[2]", color=GOLD, width=2.5, height=0.88, font_size=28).shift(DOWN * 1.45 + LEFT * 2.2)
        result = self._glass_card("value  =  90", color=MINT, width=2.7, height=0.88, font_size=26).shift(DOWN * 1.45 + RIGHT * 2.2)
        path = Arrow(access.get_right(), lane[2].get_bottom(), buff=0.16, color=CYAN, stroke_width=3)
        path2 = Arrow(lane[2].get_bottom(), result.get_left(), buff=0.16, color=MINT, stroke_width=3)
        scan = RoundedRectangle(width=1.58, height=1.48, corner_radius=0.2, color=CYAN, stroke_width=4).move_to(lane[0])
        offset = Text("start  +  2 steps", font=self.fonts.mono, font_size=19, color=CYAN).next_to(lane, DOWN, buff=0.3)
        group = VGroup(label, title, lane, access, result, path, path2, scan, offset)

        actions = [
            lambda d: self.play(FadeIn(label), FadeIn(title), run_time=d),
            lambda d: self.play(FadeIn(lane), run_time=d),
            lambda d: self.play(LaggedStart(*[FadeIn(cell[4], shift=UP * 0.08) for cell in lane], lag_ratio=0.1), run_time=d),
            lambda d: self.play(Create(scan), run_time=d),
            lambda d: self.play(scan.animate.move_to(lane[2]), FadeIn(offset), run_time=d),
            lambda d: self.play(FadeIn(access), GrowArrow(path), run_time=d),
            lambda d: self.play(Indicate(lane[2], color=CYAN), GrowArrow(path2), FadeIn(result), run_time=d),
            lambda d: self.play(Flash(result.get_center(), color=MINT, flash_radius=0.8), run_time=d),
        ]
        for action in actions:
            action(0.7)
        self.wait(0.4)
        self._clear(group)

    def _show_code(self) -> None:
        label = self._section_label("05 / CODE TO MACHINE")
        title = self._title("A tiny program, three clear jobs")
        code = code_block(self.lesson.code_example, "cpp", self.fonts)
        self._fit(code, 8.2, 5.15)
        code.shift(LEFT * 2.1 + DOWN * 0.25)
        stages = VGroup(
            self._glass_card("01  DECLARE", color=CYAN, width=2.55),
            self._glass_card("02  READ [2]", color=GOLD, width=2.55),
            self._glass_card("03  REPEAT", color=MINT, width=2.55),
        ).arrange(DOWN, buff=0.35).shift(RIGHT * 4.6 + DOWN * 0.15)
        connector = VGroup(*[
            Arrow(code.get_right(), stage.get_left(), buff=0.18, color=stage[0].get_stroke_color(), stroke_width=2)
            for stage in stages
        ])
        group = VGroup(label, title, code, stages, connector)

        actions = [
            lambda d: self.play(FadeIn(label), FadeIn(title), run_time=d),
            lambda d: self.play(Create(code), run_time=d),
            lambda d: self.play(FadeIn(stages[0], shift=LEFT * 0.15), GrowArrow(connector[0]), run_time=d),
            lambda d: self.play(FadeIn(stages[1], shift=LEFT * 0.15), GrowArrow(connector[1]), run_time=d),
            lambda d: self.play(FadeIn(stages[2], shift=LEFT * 0.15), GrowArrow(connector[2]), run_time=d),
            lambda d: self.play(Flash(stages[2].get_center(), color=MINT, flash_radius=0.8), run_time=d),
            lambda d: self.play(stages.animate.shift(UP * 0.06), run_time=d, rate_func=there_and_back),
            lambda d: self.play(Flash(code.get_center(), color=ELECTRIC, flash_radius=1.1), run_time=d),
        ]
        self._narrate("scene_05_code", actions)
        self._clear(group)

    def _show_trace(self) -> None:
        label = self._section_label("06 / LIVE TRACE")
        title = self._title("Follow i as the data flows")
        lane = self._array_cells([70, 85, 90, 75, 88], scale=0.9).shift(UP * 0.55)
        pointer = Triangle(fill_color=CYAN, fill_opacity=1, stroke_color=CYAN).scale(0.13).rotate(PI)
        pointer.next_to(lane[0], UP, buff=0.12)
        i_label = self._glass_card("i = 0", color=CYAN, width=1.45, height=0.58, font_size=19).next_to(pointer, UP, buff=0.12)
        output_title = Text("OUTPUT STREAM", font=self.fonts.sans, font_size=15, color=MUTED, weight=BOLD)
        output_title.shift(DOWN * 1.0)
        output_slots = VGroup(*[
            self._glass_card(str(value), color=ACCENT_CYCLE[i], width=1.15, height=0.68, font_size=22)
            for i, value in enumerate([70, 85, 90, 75, 88])
        ]).arrange(RIGHT, buff=0.17).next_to(output_title, DOWN, buff=0.25)
        for slot in output_slots:
            slot.set_opacity(0)
        stop = self._glass_card("i = 5  →  STOP", color=CORAL, width=3.0, height=0.75, font_size=22).to_edge(DOWN, buff=0.4)
        stop.set_opacity(0)
        group = VGroup(label, title, lane, pointer, i_label, output_title, output_slots, stop)

        def step(index: int, duration: float) -> None:
            animations = [
                pointer.animate.next_to(lane[index], UP, buff=0.12),
                i_label.animate.next_to(lane[index], UP, buff=0.52),
                output_slots[index].animate.set_opacity(1),
                lane[index][1].animate.set_stroke(CYAN, width=4),
            ]
            if index > 0:
                animations.append(lane[index - 1][1].animate.set_stroke(ACCENT_CYCLE[index - 1], width=2.2))
            i_label[1].become(Text(f"i = {index}", font=self.fonts.sans, font_size=19, color=SOFT_WHITE, weight=BOLD).move_to(i_label[0]))
            self.play(*animations, run_time=duration)

        actions = [
            lambda d: self.play(FadeIn(label), FadeIn(title), FadeIn(lane), FadeIn(output_title), run_time=d),
            lambda d: self.play(FadeIn(pointer), FadeIn(i_label), run_time=d),
            lambda d: step(0, d),
            lambda d: step(1, d),
            lambda d: step(2, d),
            lambda d: step(3, d),
            lambda d: step(4, d),
            lambda d: self.play(stop.animate.set_opacity(1), pointer.animate.set_opacity(0), i_label.animate.set_opacity(0), run_time=d),
            lambda d: self.play(Flash(stop.get_center(), color=CORAL, flash_radius=0.9), run_time=d),
            lambda d: self.play(output_slots.animate.shift(UP * 0.06), run_time=d, rate_func=there_and_back),
        ]
        self._narrate("scene_06_trace", actions)
        self._clear(group)

    def _show_mistake(self) -> None:
        label = self._section_label("07 / SAFETY CHECK")
        title = self._title("The invisible wall after index 4")
        lane = self._array_cells([70, 85, 90, 75, 88], scale=0.82).shift(LEFT * 0.75 + UP * 0.45)
        ghost_box = RoundedRectangle(
            width=1.2, height=1.08, corner_radius=0.16,
            stroke_color=CORAL, stroke_width=2.5, stroke_opacity=0.75,
            fill_color=CORAL, fill_opacity=0.07,
        ).next_to(lane, RIGHT, buff=0.2)
        ghost_label = Text("[5]", font=self.fonts.mono, font_size=18, color=CORAL, weight=BOLD).move_to(ghost_box)
        ghost = VGroup(ghost_box, ghost_label)
        barrier = DashedLine(ghost.get_left() + DOWN * 1.0, ghost.get_left() + UP * 1.0, color=CORAL, dash_length=0.09)
        wrong = self._glass_card("WRONG   i <= 5", color=CORAL, width=3.15, height=0.8, font_size=23).shift(DOWN * 1.45 + LEFT * 2.3)
        correct = self._glass_card("SAFE   i < 5", color=MINT, width=3.15, height=0.8, font_size=23).shift(DOWN * 1.45 + RIGHT * 2.3)
        warning = Text("UNDEFINED BEHAVIOR", font=self.fonts.sans, font_size=20, color=CORAL, weight=BOLD).next_to(ghost, DOWN, buff=0.32)
        group = VGroup(label, title, lane, ghost, barrier, wrong, correct, warning)

        actions = [
            lambda d: self.play(FadeIn(label), FadeIn(title), FadeIn(lane), run_time=d),
            lambda d: self.play(FadeIn(wrong, shift=UP * 0.12), run_time=d),
            lambda d: self.play(Create(barrier), FadeIn(ghost), run_time=d),
            lambda d: self.play(Indicate(lane[4], color=GOLD), run_time=d),
            lambda d: self.play(Flash(ghost.get_center(), color=CORAL, flash_radius=0.85), FadeIn(warning), run_time=d),
            lambda d: self.play(ghost.animate.shift(RIGHT * 0.08), run_time=d, rate_func=there_and_back),
            lambda d: self.play(Indicate(warning, color=CORAL), run_time=d),
            lambda d: self.play(FadeIn(correct, shift=UP * 0.12), wrong.animate.set_opacity(0.25), run_time=d),
            lambda d: self.play(Flash(correct.get_center(), color=MINT, flash_radius=0.8), run_time=d),
        ]
        self._narrate("scene_07_mistake", actions)
        self._clear(group)

    def _show_practice(self) -> None:
        label = self._section_label("08 / YOUR TURN")
        title = self._title("Can you predict the access?")
        lane = self._array_cells([12, 18, 21, 15], scale=1.0).shift(UP * 0.35)
        question = self._glass_card("scores[3] = ?      loop bound: i < ?", color=GOLD, width=6.6, height=0.9, font_size=25).shift(DOWN * 1.35)
        countdown = Text("3", font=self.fonts.sans, font_size=54, color=VIOLET, weight=BOLD).to_edge(RIGHT, buff=1.0).shift(DOWN * 1.3)
        answer = self._glass_card("scores[3] = 15      and      i < 4", color=MINT, width=6.6, height=0.9, font_size=25).move_to(question)
        answer.set_opacity(0)
        highlight = RoundedRectangle(width=1.6, height=1.5, corner_radius=0.2, color=MINT, stroke_width=4).move_to(lane[3])
        highlight.set_opacity(0)
        group = VGroup(label, title, lane, question, countdown, answer, highlight)

        def think(duration: float) -> None:
            self.play(FadeIn(countdown), run_time=min(0.4, duration))
            for number in [3, 2, 1]:
                countdown.become(Text(str(number), font=self.fonts.sans, font_size=54, color=VIOLET, weight=BOLD).move_to(countdown))
                self.play(countdown.animate.scale(1.12), run_time=0.35, rate_func=there_and_back)
                self.wait(0.45)
            self.play(FadeOut(countdown), run_time=0.3)

        actions = [
            lambda d: self.play(FadeIn(label), FadeIn(title), run_time=d),
            lambda d: self.play(FadeIn(lane), FadeIn(question, shift=UP * 0.12), run_time=d),
            lambda d: self.play(question.animate.scale(1.03), run_time=d, rate_func=there_and_back),
            think,
            lambda d: self.play(question.animate.set_opacity(0), answer.animate.set_opacity(1), highlight.animate.set_opacity(1), run_time=d),
            lambda d: self.play(Indicate(lane[3], color=MINT), run_time=d),
        ]
        self._narrate("scene_08_practice", actions)
        self._clear(group)

    def _show_summary_and_outro(self) -> None:
        label = self._section_label("09 / MEMORY MAP")
        title = self._title("One picture to remember it all")
        core = VGroup(
            Circle(radius=1.0, color=CYAN, stroke_width=3, fill_color=PANEL_2, fill_opacity=0.96),
            Text("ARRAY", font=self.fonts.sans, font_size=28, color=SOFT_WHITE, weight=BOLD),
        )
        nodes = VGroup(
            self._glass_card("fixed size", color=CYAN, width=2.15),
            self._glass_card("same type", color=VIOLET, width=2.15),
            self._glass_card("index 0 → n-1", color=GOLD, width=2.35),
            self._glass_card("loop i < size", color=MINT, width=2.35),
        )
        nodes[0].move_to(LEFT * 3.35 + UP * 1.35)
        nodes[1].move_to(RIGHT * 3.35 + UP * 1.35)
        nodes[2].move_to(LEFT * 3.35 + DOWN * 1.35)
        nodes[3].move_to(RIGHT * 3.35 + DOWN * 1.35)
        links = VGroup(*[
            Line(core.get_center(), node.get_center(), color=node[0].get_stroke_color(), stroke_width=2, stroke_opacity=0.6)
            for node in nodes
        ])
        group = VGroup(label, title, links, core, nodes)
        actions = [
            lambda d: self.play(FadeIn(label), FadeIn(title), GrowFromCenter(core), run_time=d),
            lambda d: self.play(Create(links[0]), FadeIn(nodes[0]), run_time=d),
            lambda d: self.play(Create(links[1]), FadeIn(nodes[1]), run_time=d),
            lambda d: self.play(Create(links[2]), FadeIn(nodes[2]), run_time=d),
            lambda d: self.play(Flash(nodes[2].get_center(), color=GOLD, flash_radius=0.8), run_time=d),
            lambda d: self.play(Create(links[3]), FadeIn(nodes[3]), run_time=d),
            lambda d: self.play(Flash(nodes[3].get_center(), color=MINT, flash_radius=0.8), run_time=d),
        ]
        self._narrate("scene_09_summary", actions)
        self._clear(group)

        end = Text("YOU CAN SEE THE MEMORY NOW", font=self.fonts.sans, font_size=37, color=SOFT_WHITE, weight=BOLD)
        end.set_color_by_gradient(CYAN, ELECTRIC, VIOLET)
        sub = Text("Declare  •  Access  •  Traverse safely", font=self.fonts.sans, font_size=23, color=MUTED)
        next_step = self._glass_card("NEXT SIGNAL  →  std::array", color=MINT, width=4.1, height=0.72, font_size=20)
        outro = VGroup(end, sub, next_step).arrange(DOWN, buff=0.32)
        beam = Line(LEFT * 3.4, RIGHT * 3.4, color=CYAN, stroke_width=2, stroke_opacity=0.6).next_to(outro, DOWN, buff=0.5)
        packet = Dot(beam.get_start(), radius=0.075, color=MINT)
        actions = [
            lambda d: self.play(FadeIn(end, scale=0.92), run_time=d),
            lambda d: self.play(FadeIn(sub, shift=UP * 0.12), run_time=d),
            lambda d: self.play(FadeIn(next_step, shift=UP * 0.12), Create(beam), run_time=d),
            lambda d: self.play(MoveAlongPath(packet, beam), run_time=d, rate_func=linear),
        ]
        self._narrate("scene_10_outro", actions)
        self.wait(0.8)
