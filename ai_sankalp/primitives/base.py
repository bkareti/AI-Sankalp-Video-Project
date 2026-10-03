"""Shared types and helpers for primitive builders.

A builder turns a normalized spec into a :class:`BuiltVisual`: the mobjects
it may show (``parts``) and an ordered list of animation beats. Each beat is
``beat(scene, duration)`` and plays one narrated step. Builders never read
lesson literals from code; everything comes from the spec or the package.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from manim import DOWN, RIGHT, UP, Dot, FadeIn, RoundedRectangle, VGroup

from .. import brand
from ..brand import BrandFonts
from .layout import fit, text

Beat = Callable[[Any, float], None]


@dataclass
class PrimitiveContext:
    fonts: BrandFonts
    package: Optional[Dict[str, Any]] = None
    scene_data: Optional[Dict[str, Any]] = None
    project_root: Optional[Path] = None
    language: str = ""
    # Scene header (section label + title) to reveal with the first beat.
    header: Optional[VGroup] = None


@dataclass
class BuiltVisual:
    parts: List[Any]
    beats: List[Beat] = field(default_factory=list)

    @property
    def extent(self) -> VGroup:
        """Every mobject the visual may show, without nested duplicates."""
        return VGroup(*unique_roots(self.parts))


def unique_roots(mobjects: Sequence[Any]) -> List[Any]:
    """Drop duplicates and mobjects already contained in another listed mobject."""
    roots: List[Any] = []
    for mobject in mobjects:
        if mobject is None or any(mobject is root for root in roots):
            continue
        if any(mobject in root.get_family() for root in mobjects if root is not mobject and root is not None):
            continue
        roots.append(mobject)
    return roots


def play(scene, animations: Sequence[Any], duration: float, **kwargs) -> None:
    """Play animations, or hold for `duration` when there is nothing to play."""
    animations = [animation for animation in animations if animation is not None]
    if animations:
        scene.play(*animations, run_time=duration, **kwargs)
    else:
        scene.wait(duration)


def with_header(ctx: PrimitiveContext, animations: Sequence[Any]) -> List[Any]:
    """Animations for a first beat, preceded by the scene header fade-in."""
    header = [FadeIn(part) for part in ctx.header] if ctx.header is not None else []
    return header + list(animations)


def accent(index: int) -> str:
    return brand.ACCENT_CYCLE[index % len(brand.ACCENT_CYCLE)]


def lane_cell(value: str, index: int, fonts: BrandFonts, show_index: bool = True) -> VGroup:
    """One glowing array cell: glow, shell, inner, value, [index], port."""
    color = accent(index)
    glow = RoundedRectangle(width=1.48, height=1.38, corner_radius=0.18, stroke_color=color, stroke_width=8, stroke_opacity=0.10)
    shell = RoundedRectangle(
        width=1.42, height=1.32, corner_radius=0.18, stroke_color=color, stroke_width=2.2,
        fill_color=brand.PANEL_2, fill_opacity=0.96,
    )
    inner = RoundedRectangle(
        width=1.17, height=0.84, corner_radius=0.12, stroke_color=brand.SOFT_WHITE, stroke_opacity=0.08,
        fill_color=brand.PANEL, fill_opacity=0.8,
    ).shift(DOWN * 0.07)
    value_text = fit(text(value, fonts, 31, bold=True), 1.05, 0.6).move_to(inner)
    index_text = text(f"[{index}]", fonts, 15, color=color, bold=True, mono=True).shift(UP * 0.48)
    port = Dot(radius=0.045, color=color).next_to(shell, DOWN, buff=0.02)
    if not show_index:
        index_text.set_opacity(0)
    return VGroup(glow, shell, inner, value_text, index_text, port)


# Indexes into a lane cell's submobjects.
CELL_SHELL = 1
CELL_INDEX = 4


def build_lane(values: Sequence[str], fonts: BrandFonts, show_indexes: bool = True, scale: float = 1.0) -> VGroup:
    cells = VGroup(*[lane_cell(str(value), index, fonts, show_indexes) for index, value in enumerate(values)])
    return cells.arrange(RIGHT, buff=0.12).scale(scale)


def swap_text(old, value: str, fonts: BrandFonts, size: float, **kwargs):
    """A replacement Text that matches `old`'s on-screen height and position."""
    replacement = text(value, fonts, size, **kwargs)
    if old.height > 0:
        replacement.scale_to_fit_height(old.height)
    return replacement.move_to(old)
