"""Play a planned package scene: header, primitives, and narration timing."""
from __future__ import annotations

from dataclasses import replace
from typing import Any, List, Optional, Sequence, Tuple

from manim import PI, UP, FadeOut, VGroup, smooth

from .. import brand
from ..captions import emit_subcaptions
from .base import Beat, BuiltVisual, PrimitiveContext
from .layout import section_label, title_text
from .planner import ScenePlan, VisualPlan, assign_beats
from .registry import build_visual
from .specs import NO_HEADER_TYPES

# (left, right, bottom, top) in Manim units.
Box = Tuple[float, float, float, float]

NARRATED_BEAT_FACTOR = 0.78
MIN_NARRATED_BEAT = 0.55
MAX_NARRATED_BEAT = 3.4
MIN_SHARED_BEAT = 0.35
SILENT_BEAT = 0.75
SILENT_IDLE = 0.5
AFTER_NARRATION_BEAT = 0.7
AFTER_NARRATION_HOLD = 0.4
CLEAR_TIME = 0.55


def build_header(spec: dict, fonts) -> Optional[VGroup]:
    if spec["type"] in NO_HEADER_TYPES or not (spec.get("label") or spec.get("title")):
        return None
    parts = []
    if spec.get("label"):
        parts.append(section_label(spec["label"], fonts))
    if spec.get("title"):
        parts.append(title_text(spec["title"], fonts))
    return VGroup(*parts)


def body_box(header: Optional[VGroup]) -> Box:
    half_width = brand.FRAME_WIDTH / 2 - brand.SAFE_MARGIN_X
    top = header.get_bottom()[1] - 0.25 if header is not None else brand.LOGO_ZONE_MIN_Y - 0.05
    return (-half_width, half_width, brand.CONTENT_SAFE_BOTTOM_Y, top)


def fit_into_box(group: VGroup, box: Box, center: bool = False) -> VGroup:
    """Scale `group` down to fit `box`, then nudge it inside (or center it)."""
    left, right, bottom, top = box
    if group.width > right - left:
        group.scale_to_fit_width(right - left)
    if group.height > top - bottom:
        group.scale_to_fit_height(top - bottom)
    if center:
        return group.move_to([(left + right) / 2, (bottom + top) / 2, 0])
    dx = max(0.0, left - group.get_left()[0]) - max(0.0, group.get_right()[0] - right)
    dy = max(0.0, bottom - group.get_bottom()[1]) - max(0.0, group.get_top()[1] - top)
    return group.shift([dx, dy, 0])


def prepare_visual(plan: VisualPlan, ctx: PrimitiveContext) -> Tuple[BuiltVisual, Optional[VGroup]]:
    header = build_header(plan.spec, ctx.fonts)
    built = build_visual(plan.spec, replace(ctx, header=header))
    fit_into_box(built.extent, body_box(header))
    return built, header


def clear_since(scene, marker: Sequence[Any]) -> None:
    """Fade out everything added to the scene after `marker` was taken."""
    keep = set(map(id, marker)) | set(map(id, scene.foreground_mobjects))
    added = [mobject for mobject in scene.mobjects if id(mobject) not in keep]
    if added:
        scene.play(*[FadeOut(mobject, shift=UP * 0.08) for mobject in added], run_time=CLEAR_TIME)


def _idle(scene, duration: float, ambient) -> None:
    if ambient is not None:
        scene.play(ambient.animate.rotate(PI / 8), run_time=duration, rate_func=smooth)
    else:
        scene.wait(duration)


def play_scene(scene, plan: ScenePlan, ctx: PrimitiveContext, voiceover: bool, ambient=None) -> None:
    """Play one scene: narrated visuals beat-by-beat, then after-narration visuals."""
    state = {"marker": list(scene.mobjects)}
    beats: List[Beat] = []
    for index, visual in enumerate(v for v in plan.visuals if v.timing == "narrated"):
        built, _header = prepare_visual(visual, ctx)
        visual_beats = list(built.beats)
        first = visual_beats[0]

        def opener(target, duration, first=first, index=index):
            if index > 0:
                clear_since(target, state["marker"])
            state["marker"] = list(target.mobjects)
            first(target, duration)

        visual_beats[0] = opener
        beats.extend(visual_beats)

    for sentence, assigned in zip(plan.sentences, assign_beats(len(plan.sentences), len(beats))):
        if voiceover:
            with scene.voiceover(text=sentence) as tracker:
                emit_subcaptions(scene, sentence, tracker.duration)
                duration = max(MIN_NARRATED_BEAT, min(MAX_NARRATED_BEAT, tracker.duration * NARRATED_BEAT_FACTOR))
                _run(scene, [beats[i] for i in assigned], duration, ambient, share=True)
        else:
            start = scene.time
            _run(scene, [beats[i] for i in assigned], SILENT_BEAT, ambient, share=False)
            elapsed = scene.time - start
            emit_subcaptions(scene, sentence, elapsed, offset=-elapsed)
    if beats:
        clear_since(scene, state["marker"])

    for visual in (v for v in plan.visuals if v.timing == "after_narration"):
        marker = list(scene.mobjects)
        built, _header = prepare_visual(visual, ctx)
        for beat in built.beats:
            beat(scene, AFTER_NARRATION_BEAT)
        scene.wait(AFTER_NARRATION_HOLD)
        clear_since(scene, marker)


def _run(scene, beats: List[Beat], duration: float, ambient, share: bool) -> None:
    if not beats:
        _idle(scene, duration if share else SILENT_IDLE, ambient)
        return
    each = max(MIN_SHARED_BEAT, duration / len(beats)) if share else duration
    for beat in beats:
        beat(scene, each)
