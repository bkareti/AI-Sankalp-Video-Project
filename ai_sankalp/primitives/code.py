"""code_walkthrough: the package's code example with numbered stage cards."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from manim import DOWN, LEFT, RIGHT, UP, Arrow, Create, FadeIn, Flash, GrowArrow, VGroup, there_and_back

from .. import brand
from .base import BuiltVisual, PrimitiveContext, play, with_header
from .layout import code_block, fit, glass_card, pygments_language

Spec = Dict[str, Any]
STAGE_COLORS = (brand.CYAN, brand.GOLD, brand.MINT, brand.VIOLET)


def resolve_code_example(spec: Spec, ctx: PrimitiveContext) -> Dict[str, Any]:
    """The code example named by the spec, else the scene's first, else the package's first."""
    package = ctx.package or {}
    examples = {example.get("id"): example for example in package.get("code_examples", [])}
    wanted: Optional[str] = spec.get("code_example_id")
    if wanted is None and ctx.scene_data and ctx.scene_data.get("code_example_ids"):
        wanted = ctx.scene_data["code_example_ids"][0]
    if wanted is not None:
        if wanted not in examples:
            raise KeyError(f"code example '{wanted}' not found in the package")
        return examples[wanted]
    if not examples:
        raise KeyError("the package has no code_examples")
    return next(iter(examples.values()))


def code_walkthrough(spec: Spec, ctx: PrimitiveContext) -> BuiltVisual:
    example = resolve_code_example(spec, ctx)
    language = spec.get("language") or pygments_language(ctx.language)
    code = code_block(example["code"], language, ctx.fonts)
    steps = spec.get("steps") or []
    if steps:
        fit(code, 8.2, 4.6)
        code.move_to(LEFT * 2.1 + DOWN * 0.1)
        stages = VGroup(*[
            glass_card(label, ctx.fonts, color=STAGE_COLORS[index % len(STAGE_COLORS)], width=2.55, mono=True)
            for index, label in enumerate(steps)
        ]).arrange(DOWN, buff=0.35).move_to(RIGHT * 4.6 + DOWN * 0.1)
        connectors = VGroup(*[
            Arrow(code.get_right(), stage.get_left(), buff=0.18, color=stage[0].get_stroke_color(), stroke_width=2)
            for stage in stages
        ])
        parts: List[Any] = [code, stages, connectors]
    else:
        fit(code, brand.CONTENT_MAX_WIDTH - 0.6, 4.6)
        code.move_to(DOWN * 0.1)
        parts = [code]

    beats = [
        lambda scene, d: play(scene, with_header(ctx, []), d),
        lambda scene, d: play(scene, [Create(code)], d),
    ]
    if steps:
        for index in range(len(steps)):
            beats.append(lambda scene, d, i=index: play(
                scene, [FadeIn(stages[i], shift=LEFT * 0.15), GrowArrow(connectors[i])], d,
            ))
        beats.append(lambda scene, d: play(scene, [
            Flash(stages[-1].get_center(), color=stages[-1][0].get_stroke_color(), flash_radius=0.8),
        ], d))
        beats.append(lambda scene, d: play(scene, [stages.animate(rate_func=there_and_back).shift(UP * 0.06)], d))
    beats.append(lambda scene, d: play(scene, [Flash(code.get_center(), color=brand.ELECTRIC, flash_radius=1.1)], d))
    return BuiltVisual(parts, beats)
