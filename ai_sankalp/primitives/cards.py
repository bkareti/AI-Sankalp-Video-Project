"""Card primitives: title_card, outro_card, bullet_card, card_merge, concept_map."""
from __future__ import annotations

import math
from typing import Any, Dict, List

from manim import (
    DOWN, LEFT, RIGHT, UP, Circle, Create, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate,
    LaggedStart, Line, MoveAlongPath, Transform, VGroup, linear, there_and_back,
)

from .. import brand
from .base import BuiltVisual, PrimitiveContext, accent, build_lane, play, with_header
from .layout import fit, glass_card, panel, text, wrap_text

Spec = Dict[str, Any]
CONCEPT_COLORS = (brand.CYAN, brand.VIOLET, brand.GOLD, brand.MINT)


def title_card(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    fonts = ctx.fonts
    eyebrow = text(spec["eyebrow"], fonts, 16, color=brand.CYAN, bold=True) if spec.get("eyebrow") else None
    heading = fit(text(spec["heading"], fonts, 84, bold=True), 11.0, 1.5)
    heading.set_color_by_gradient(brand.CYAN, brand.ELECTRIC, brand.VIOLET)
    subtitle = fit(text(spec["subtitle"], fonts, 27, color=brand.MUTED), 11.0) if spec.get("subtitle") else None
    title_group = VGroup(*[part for part in (eyebrow, heading, subtitle) if part is not None]).arrange(DOWN, buff=0.18)
    parts: List[Any] = [title_group]
    beats = []

    first = eyebrow if eyebrow is not None else heading
    rest = [part for part in (heading, subtitle) if part is not None and part is not first]
    beats.append(lambda scene, d: play(scene, with_header(ctx, [FadeIn(first, shift=DOWN * 0.12)]), d))
    if rest:
        beats.append(lambda scene, d: play(scene, [FadeIn(part, shift=UP * 0.12) for part in rest], d))
    else:
        beats.append(lambda scene, d: play(scene, [Indicate(heading, color=brand.CYAN)], d))

    if spec.get("lane_values"):
        title_group.shift(UP * 1.2)
        lane = build_lane(spec["lane_values"], fonts, show_indexes=False, scale=0.88).shift(DOWN * 1.15)
        rail = Line(
            lane.get_left() + LEFT * 0.4, lane.get_right() + RIGHT * 0.4,
            color=brand.CYAN, stroke_width=2, stroke_opacity=0.42,
        ).next_to(lane, DOWN, buff=0.18)
        signal = Dot(rail.get_start(), radius=0.07, color=brand.MINT)
        parts += [lane, rail, signal]
        beats.append(lambda scene, d: play(scene, [
            LaggedStart(*[FadeIn(cell, shift=UP * 0.18) for cell in lane], lag_ratio=0.1), Create(rail),
        ], d))
        beats.append(lambda scene, d: play(scene, [MoveAlongPath(signal, rail)], d, rate_func=linear))
    return BuiltVisual(parts, beats)


def outro_card(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    fonts = ctx.fonts
    heading = fit(text(spec["heading"], fonts, 37, bold=True), 11.0)
    heading.set_color_by_gradient(brand.CYAN, brand.ELECTRIC, brand.VIOLET)
    subtitle = fit(text(spec["subtitle"], fonts, 23, color=brand.MUTED), 11.0) if spec.get("subtitle") else None
    next_step = (
        glass_card(spec["next_step"], fonts, color=brand.MINT, width=4.1, height=0.72, font_size=20)
        if spec.get("next_step") else None
    )
    outro = VGroup(*[part for part in (heading, subtitle, next_step) if part is not None]).arrange(DOWN, buff=0.32)
    parts: List[Any] = [outro]
    beats = [lambda scene, d: play(scene, with_header(ctx, [FadeIn(heading, scale=0.92)]), d)]
    if subtitle is not None:
        beats.append(lambda scene, d: play(scene, [FadeIn(subtitle, shift=UP * 0.12)], d))
    if next_step is not None:
        beam = Line(LEFT * 3.4, RIGHT * 3.4, color=brand.CYAN, stroke_width=2, stroke_opacity=0.6)
        beam.next_to(outro, DOWN, buff=0.5)
        packet = Dot(beam.get_start(), radius=0.075, color=brand.MINT)
        parts += [beam, packet]
        beats.append(lambda scene, d: play(scene, [FadeIn(next_step, shift=UP * 0.12), Create(beam)], d))
        beats.append(lambda scene, d: play(scene, [MoveAlongPath(packet, beam)], d, rate_func=linear))
    return BuiltVisual(parts, beats)


def bullet_card(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    fonts = ctx.fonts
    rows = VGroup()
    lines = [text(wrap_text(item, 58), fonts, 26, line_spacing=0.86) for item in spec["bullets"]]
    scale = min([1.0] + [10.2 / line.width for line in lines])
    for line in lines:
        line.scale(scale)
        rows.add(VGroup(Dot(radius=0.06, color=brand.MINT), line).arrange(RIGHT, buff=0.2, aligned_edge=UP))
    rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
    card = panel(max(rows.width + 1.2, 6.0), rows.height + 0.9)
    rows.move_to(card)
    group = VGroup(card, rows).shift(DOWN * 0.3)
    beats = [lambda scene, d: play(scene, with_header(ctx, [
        FadeIn(card), LaggedStart(*[FadeIn(row, shift=RIGHT * 0.12) for row in rows], lag_ratio=0.15),
    ]), d)]
    return BuiltVisual([group], beats)


def card_merge(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    fonts = ctx.fonts
    cards = VGroup(*[
        glass_card(label, fonts, color=accent(index), width=2.25)
        for index, label in enumerate(spec["cards"])
    ])
    columns = math.ceil(len(cards) / 2)
    cards.arrange_in_grid(rows=2, cols=columns, buff=(0.35, 0.3)).shift(DOWN * 0.45)
    lane = build_lane(spec["target_values"], fonts, show_indexes=False).shift(DOWN * 0.3)
    name = glass_card(spec["target_name"], fonts, color=brand.MINT, width=1.7, height=0.62, font_size=21)
    name.next_to(lane, UP, buff=0.35)
    parts: List[Any] = [cards, lane, name]
    callout = None
    if spec.get("callout"):
        callout = text(spec["callout"], fonts, 26, color=brand.GOLD, bold=True).next_to(cards, DOWN, buff=0.4)
        parts.append(callout)

    beats = [
        lambda scene, d: play(scene, with_header(ctx, []), d),
        lambda scene, d: play(scene, [LaggedStart(*[FadeIn(card, scale=0.9) for card in cards], lag_ratio=0.1)], d),
    ]
    if callout is not None:
        beats.append(lambda scene, d: play(scene, [
            FadeIn(callout, shift=UP * 0.1), cards.animate(rate_func=there_and_back).scale(1.03),
        ], d))
    beats.append(lambda scene, d: play(scene, [cards.animate(rate_func=there_and_back).scale(0.88)], d))
    beats.append(lambda scene, d: play(scene, [
        Transform(cards, lane), FadeIn(name, shift=DOWN * 0.12),
        *([FadeOut(callout)] if callout is not None else []),
    ], d))
    beats.append(lambda scene, d: play(scene, [Flash(name.get_center(), color=brand.MINT, flash_radius=0.8)], d))
    return BuiltVisual(parts, beats)


CONCEPT_POSITIONS = {
    2: [(-3.35, 0.0), (3.35, 0.0)],
    3: [(-3.35, 1.35), (3.35, 1.35), (0.0, -1.9)],
    4: [(-3.35, 1.35), (3.35, 1.35), (-3.35, -1.35), (3.35, -1.35)],
}


def concept_map(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    fonts = ctx.fonts
    core = VGroup(
        Circle(radius=1.0, color=brand.CYAN, stroke_width=3, fill_color=brand.PANEL_2, fill_opacity=0.96),
        fit(text(spec["center"], fonts, 28, bold=True), 1.7, 0.9),
    )
    nodes = VGroup(*[
        glass_card(label, fonts, color=CONCEPT_COLORS[index % len(CONCEPT_COLORS)], width=2.35)
        for index, label in enumerate(spec["nodes"])
    ])
    for node, (x, y) in zip(nodes, CONCEPT_POSITIONS[len(nodes)]):
        node.move_to(RIGHT * x + UP * y)
    links = VGroup(*[
        Line(core.get_center(), node.get_center(), color=node[0].get_stroke_color(), stroke_width=2, stroke_opacity=0.6)
        for node in nodes
    ])
    # Links stay behind the core and nodes but in front of any panel (z 0).
    core.set_z_index(1)
    nodes.set_z_index(1)

    beats = [lambda scene, d: play(scene, with_header(ctx, [GrowFromCenter(core)]), d)]
    for index in range(len(nodes)):
        beats.append(lambda scene, d, i=index: play(scene, [Create(links[i]), FadeIn(nodes[i])], d))
        if index >= len(nodes) - 2:
            beats.append(lambda scene, d, i=index: play(
                scene, [Flash(nodes[i].get_center(), color=nodes[i][0].get_stroke_color(), flash_radius=0.8)], d,
            ))
    return BuiltVisual([links, core, nodes], beats)
