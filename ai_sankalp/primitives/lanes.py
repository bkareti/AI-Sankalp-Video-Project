"""Array-lane primitives: array_lane, token_breakdown, index_access,
loop_trace, bounds_check, practice_reveal."""
from __future__ import annotations

from typing import Any, Dict, List

from manim import (
    DOWN, LEFT, PI, RIGHT, UP, Arrow, Create, DashedLine, Dot, FadeIn, FadeOut, Flash, GrowArrow,
    GrowFromCenter, Indicate, LaggedStart, Line, MoveAlongPath, RoundedRectangle, Transform, Triangle,
    VGroup, linear, there_and_back,
)

from .. import brand
from .base import (
    CELL_INDEX, CELL_SHELL, BuiltVisual, PrimitiveContext, accent, build_lane, play, swap_text, with_header,
)
from .layout import fit, glass_card, text

Spec = Dict[str, Any]
CHIP_COLORS = (brand.CYAN, brand.VIOLET, brand.MINT)
TOKEN_COLORS = (brand.CYAN, brand.GOLD, brand.MINT, brand.VIOLET, brand.ELECTRIC)


def _card(label: str, ctx: PrimitiveContext, color: str, min_width: float, height: float = 0.82,
          font_size: float = 22, mono: bool = False):
    width = max(min_width, text(label, ctx.fonts, font_size, bold=True, mono=mono).width + 0.6)
    return glass_card(label, ctx.fonts, color=color, width=width, height=height, font_size=font_size, mono=mono)


def _pulse(mobject, shift=UP * 0.06):
    return mobject.animate(rate_func=there_and_back).shift(shift)


def array_lane(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    lane = build_lane(spec["values"], ctx.fonts, show_indexes=spec.get("show_indexes", True)).shift(UP * 0.45)
    parts: List[Any] = [lane]
    anchor = lane
    name = None
    if spec.get("name"):
        name = _card(spec["name"], ctx, brand.MINT, 1.7, height=0.62, font_size=21).next_to(lane, UP, buff=0.35)
        parts.append(name)

    addresses = bus = packet = None
    if spec.get("addresses"):
        start, step = spec["addresses"]["start"], spec["addresses"]["step"]
        addresses = VGroup(*[
            text(str(start + index * step), ctx.fonts, 14, color=brand.MUTED, mono=True).next_to(cell, DOWN, buff=0.38)
            for index, cell in enumerate(lane)
        ])
        bus = Line(lane.get_left() + LEFT * 0.3, lane.get_right() + RIGHT * 0.3,
                   color=brand.CYAN, stroke_width=3, stroke_opacity=0.5).next_to(addresses, DOWN, buff=0.22)
        packet = Dot(bus.get_start(), radius=0.08, color=brand.MINT)
        parts += [addresses, bus, packet]
        anchor = bus

    chips = VGroup(*[
        _card(label, ctx, CHIP_COLORS[index % len(CHIP_COLORS)], 2.5)
        for index, label in enumerate(spec.get("chips") or [])
    ])
    if len(chips):
        chips.arrange(RIGHT, buff=0.25).next_to(anchor, DOWN, buff=0.45)
        parts.append(chips)

    beats = [
        lambda scene, d: play(scene, with_header(ctx, [FadeIn(name)] if name is not None else []), d),
        lambda scene, d: play(scene, [LaggedStart(*[GrowFromCenter(cell) for cell in lane], lag_ratio=0.1)], d),
    ]
    for index in range(len(chips) - 1):
        beats.append(lambda scene, d, i=index: play(scene, [FadeIn(chips[i], shift=UP * 0.12)], d))
    if addresses is not None:
        beats.append(lambda scene, d: play(scene, [FadeIn(addresses), Create(bus)], d))
        last_chip = [FadeIn(chips[-1], shift=UP * 0.12)] if len(chips) else []
        beats.append(lambda scene, d: play(scene, [MoveAlongPath(packet, bus, rate_func=linear)] + last_chip, d))
    elif len(chips):
        beats.append(lambda scene, d: play(scene, [FadeIn(chips[-1], shift=UP * 0.12)], d))
    beats.append(lambda scene, d: play(scene, [_pulse(lane)], d))
    return BuiltVisual(parts, beats)


def token_breakdown(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    tokens = VGroup(*[
        _card(token["text"], ctx, TOKEN_COLORS[index % len(TOKEN_COLORS)], 1.35, mono=True)
        for index, token in enumerate(spec["tokens"])
    ]).arrange(RIGHT, buff=0.2).shift(UP * 0.7)
    fit(tokens, brand.CONTENT_MAX_WIDTH)
    captions = VGroup(*[
        text(token["role"], ctx.fonts, 16, color=TOKEN_COLORS[index % len(TOKEN_COLORS)]).next_to(card, UP, buff=0.17)
        for index, (token, card) in enumerate(zip(spec["tokens"], tokens))
    ])
    code_line = text(spec["code_line"], ctx.fonts, 29, mono=True)
    fit(code_line, brand.CONTENT_MAX_WIDTH - 1.0)
    code_panel = RoundedRectangle(
        width=code_line.width + 0.75, height=0.95, corner_radius=0.16,
        stroke_color=brand.ELECTRIC, fill_color=brand.PANEL, fill_opacity=0.96,
    ).move_to(code_line)
    code_group = VGroup(code_panel, code_line).shift(UP * 0.55)
    parts: List[Any] = [tokens, captions, code_group]

    beats = [
        lambda scene, d: play(scene, with_header(ctx, []), d),
        lambda scene, d: play(scene, [LaggedStart(*[FadeIn(card, shift=UP * 0.15) for card in tokens], lag_ratio=0.1)], d),
    ]
    for index in range(len(tokens)):
        beats.append(lambda scene, d, i=index: play(scene, [
            FadeIn(captions[i]), Indicate(tokens[i], color=TOKEN_COLORS[i % len(TOKEN_COLORS)]),
        ], d))
    beats.append(lambda scene, d: play(scene, [FadeOut(captions), Transform(tokens, code_group)], d))

    if spec.get("values"):
        lane = build_lane(spec["values"], ctx.fonts, show_indexes=False, scale=0.9).shift(DOWN * 1.2)
        span = code_panel.width / 2 - 0.3
        arrows = VGroup(*[
            Arrow(
                code_group.get_bottom() + RIGHT * max(-span, min(span, cell.get_x() * 0.86)), cell.get_top(),
                buff=0.12, color=brand.CYAN, stroke_width=1.6, max_tip_length_to_length_ratio=0.12,
            )
            for cell in lane
        ])
        parts += [lane, arrows]
        beats.append(lambda scene, d: play(scene, [
            FadeIn(lane), LaggedStart(*[GrowArrow(arrow) for arrow in arrows], lag_ratio=0.08),
        ], d))
        highlight = spec.get("highlight_index")
        if highlight is not None:
            beats.append(lambda scene, d: play(scene, [
                Flash(lane[highlight].get_center(), color=brand.CYAN, flash_radius=0.7),
            ], d))
    return BuiltVisual(parts, beats)


def index_access(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    index = spec["index"]
    lane = build_lane(spec["values"], ctx.fonts).shift(UP * 0.35)
    for cell in lane:
        cell[CELL_INDEX].set_opacity(0)
    access = _card(spec["access_label"], ctx, brand.GOLD, 2.5, height=0.88, font_size=28, mono=True)
    access.shift(DOWN * 1.45 + LEFT * 2.2)
    result = _card(spec["result_label"], ctx, brand.MINT, 2.7, height=0.88, font_size=26).shift(DOWN * 1.45 + RIGHT * 2.2)
    path = Arrow(access.get_right(), lane[index].get_bottom(), buff=0.16, color=brand.CYAN, stroke_width=3)
    path2 = Arrow(lane[index].get_bottom(), result.get_left(), buff=0.16, color=brand.MINT, stroke_width=3)
    scan = RoundedRectangle(width=1.58, height=1.48, corner_radius=0.2, color=brand.CYAN, stroke_width=4).move_to(lane[0])
    parts: List[Any] = [lane, access, result, path, path2, scan]
    offset = None
    if spec.get("offset_label"):
        offset = text(spec["offset_label"], ctx.fonts, 19, color=brand.CYAN, mono=True).next_to(lane, DOWN, buff=0.3)
        parts.append(offset)

    beats = [
        lambda scene, d: play(scene, with_header(ctx, []), d),
        lambda scene, d: play(scene, [FadeIn(lane)], d),
        lambda scene, d: play(scene, [
            LaggedStart(*[cell[CELL_INDEX].animate.set_opacity(1) for cell in lane], lag_ratio=0.1),
        ], d),
        lambda scene, d: play(scene, [Create(scan)], d),
        lambda scene, d: play(scene, [scan.animate.move_to(lane[index])] + ([FadeIn(offset)] if offset else []), d),
        lambda scene, d: play(scene, [FadeIn(access), GrowArrow(path)], d),
        lambda scene, d: play(scene, [Indicate(lane[index], color=brand.CYAN), GrowArrow(path2), FadeIn(result)], d),
        lambda scene, d: play(scene, [Flash(result.get_center(), color=brand.MINT, flash_radius=0.8)], d),
    ]
    return BuiltVisual(parts, beats)


def loop_trace(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    values = spec["values"]
    variable = spec.get("variable", "i")
    shown = spec.get("variable_values") or [str(index) for index in range(len(values))]
    outputs = spec.get("outputs") or values
    lane = build_lane(values, ctx.fonts, scale=0.9).shift(UP * 0.75)
    pointer = Triangle(fill_color=brand.CYAN, fill_opacity=1, stroke_color=brand.CYAN).scale(0.13).rotate(PI)
    pointer.next_to(lane[0], UP, buff=0.12)
    label = _card(f"{variable} = {shown[0]}", ctx, brand.CYAN, 1.45, height=0.58, font_size=19, mono=True)
    label.next_to(pointer, UP, buff=0.12)
    output_title = text(spec.get("output_title", "OUTPUT"), ctx.fonts, 15, color=brand.MUTED, bold=True)
    output_title.next_to(lane, DOWN, buff=0.55)
    slots = VGroup(*[
        _card(value, ctx, accent(index), 1.15, height=0.68, font_size=22, mono=True)
        for index, value in enumerate(outputs)
    ]).arrange(RIGHT, buff=0.17).next_to(output_title, DOWN, buff=0.22)
    for slot in slots:
        slot.set_opacity(0)
    parts: List[Any] = [lane, pointer, label, output_title, slots]
    stop = None
    if spec.get("stop_label"):
        stop = _card(spec["stop_label"], ctx, brand.CORAL, 3.0, height=0.75, font_size=22, mono=True)
        stop.next_to(slots, DOWN, buff=0.3)
        stop.set_opacity(0)
        parts.append(stop)

    def step(scene, duration: float, index: int) -> None:
        label[1].become(swap_text(label[1], f"{variable} = {shown[index]}", ctx.fonts, 19, bold=True, mono=True))
        animations = [
            pointer.animate.next_to(lane[index], UP, buff=0.12),
            label.animate.next_to(lane[index], UP, buff=0.12 + pointer.height + 0.12),
            slots[index].animate.set_opacity(1),
            lane[index][CELL_SHELL].animate.set_stroke(brand.CYAN, width=4),
        ]
        if index > 0:
            animations.append(lane[index - 1][CELL_SHELL].animate.set_stroke(accent(index - 1), width=2.2))
        play(scene, animations, duration)

    beats = [
        lambda scene, d: play(scene, with_header(ctx, [FadeIn(lane), FadeIn(output_title)]), d),
        lambda scene, d: play(scene, [FadeIn(pointer), FadeIn(label)], d),
    ]
    for index in range(len(values)):
        beats.append(lambda scene, d, i=index: step(scene, d, i))
    if stop is not None:
        beats.append(lambda scene, d: play(scene, [
            stop.animate.set_opacity(1), pointer.animate.set_opacity(0), label.animate.set_opacity(0),
        ], d))
        beats.append(lambda scene, d: play(scene, [Flash(stop.get_center(), color=brand.CORAL, flash_radius=0.9)], d))
    beats.append(lambda scene, d: play(scene, [_pulse(slots)], d))
    return BuiltVisual(parts, beats)


def bounds_check(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    lane = build_lane(spec["values"], ctx.fonts, scale=0.82)
    ghost_box = RoundedRectangle(
        width=1.2, height=1.08, corner_radius=0.16, stroke_color=brand.CORAL, stroke_width=2.5,
        stroke_opacity=0.75, fill_color=brand.CORAL, fill_opacity=0.07,
    ).next_to(lane, RIGHT, buff=0.2)
    ghost_label = text(spec["ghost_label"], ctx.fonts, 18, color=brand.CORAL, bold=True, mono=True).move_to(ghost_box)
    ghost = VGroup(ghost_box, ghost_label)
    row = VGroup(lane, ghost)
    row.move_to(UP * 0.45)
    barrier = DashedLine(ghost.get_left() + DOWN * 1.0, ghost.get_left() + UP * 1.0, color=brand.CORAL, dash_length=0.09)
    wrong = _card(spec["wrong_label"], ctx, brand.CORAL, 3.15, height=0.8, font_size=23, mono=True)
    wrong.shift(DOWN * 1.45 + LEFT * 2.3)
    correct = _card(spec["correct_label"], ctx, brand.MINT, 3.15, height=0.8, font_size=23, mono=True)
    correct.shift(DOWN * 1.45 + RIGHT * 2.3)
    warning = text(spec["warning"], ctx.fonts, 20, color=brand.CORAL, bold=True).next_to(ghost, DOWN, buff=0.32)
    beats = [
        lambda scene, d: play(scene, with_header(ctx, [FadeIn(lane)]), d),
        lambda scene, d: play(scene, [FadeIn(wrong, shift=UP * 0.12)], d),
        lambda scene, d: play(scene, [Create(barrier), FadeIn(ghost)], d),
        lambda scene, d: play(scene, [Indicate(lane[-1], color=brand.GOLD)], d),
        lambda scene, d: play(scene, [Flash(ghost.get_center(), color=brand.CORAL, flash_radius=0.85), FadeIn(warning)], d),
        lambda scene, d: play(scene, [ghost.animate(rate_func=there_and_back).shift(RIGHT * 0.08)], d),
        lambda scene, d: play(scene, [Indicate(warning, color=brand.CORAL)], d),
        lambda scene, d: play(scene, [FadeIn(correct, shift=UP * 0.12), wrong.animate.set_opacity(0.25)], d),
        lambda scene, d: play(scene, [Flash(correct.get_center(), color=brand.MINT, flash_radius=0.8)], d),
    ]
    return BuiltVisual([row, barrier, wrong, correct, warning], beats)


def practice_reveal(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    index = spec["highlight_index"]
    lane = build_lane(spec["values"], ctx.fonts).shift(UP * 0.35)
    question = _card(spec["question"], ctx, brand.GOLD, 6.6, height=0.9, font_size=25, mono=True).shift(DOWN * 1.35)
    answer = _card(spec["answer"], ctx, brand.MINT, 6.6, height=0.9, font_size=25, mono=True).move_to(question)
    answer.set_opacity(0)
    highlight = RoundedRectangle(width=1.6, height=1.5, corner_radius=0.2, stroke_color=brand.MINT, stroke_width=4)
    highlight.move_to(lane[index]).set_stroke(opacity=0)
    parts: List[Any] = [lane, question, answer, highlight]
    count = spec.get("countdown", 3)
    countdown = None
    if count:
        countdown = text(str(count), ctx.fonts, 54, color=brand.VIOLET, bold=True).next_to(question, RIGHT, buff=0.6)
        parts.append(countdown)

    def think(scene, duration: float) -> None:
        play(scene, [FadeIn(countdown)], min(0.4, duration))
        for number in range(count, 0, -1):
            countdown.become(swap_text(countdown, str(number), ctx.fonts, 54, color=brand.VIOLET, bold=True))
            play(scene, [countdown.animate(rate_func=there_and_back).scale(1.12)], 0.35)
            scene.wait(0.45)
        play(scene, [FadeOut(countdown)], 0.3)

    beats = [
        lambda scene, d: play(scene, with_header(ctx, []), d),
        lambda scene, d: play(scene, [FadeIn(lane), FadeIn(question, shift=UP * 0.12)], d),
        lambda scene, d: play(scene, [question.animate(rate_func=there_and_back).scale(1.03)], d),
    ]
    if countdown is not None:
        beats.append(think)
    beats += [
        lambda scene, d: play(scene, [
            question.animate.set_opacity(0), answer.animate.set_opacity(1), highlight.animate.set_stroke(opacity=1),
        ], d),
        lambda scene, d: play(scene, [Indicate(lane[index], color=brand.MINT)], d),
    ]
    return BuiltVisual(parts, beats)
