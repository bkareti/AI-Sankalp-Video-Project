"""The persistent AI Sankalp frame: background, logo, and footer."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from manim import DOWN, LEFT, RIGHT, UP, UR, Circle, Dot, Line, SVGMobject, VGroup

from .. import brand
from ..brand import BrandFonts
from .layout import text


@dataclass
class BrandFrame:
    background: VGroup
    logo: SVGMobject
    footer: VGroup
    ambient: Optional[Circle] = None


def build_logo(logo_path: Path = brand.LOGO_PATH) -> SVGMobject:
    """The supplied SVG at its native proportions: no badge, border, or recoloring."""
    if not Path(logo_path).exists():
        raise FileNotFoundError(f"AI Sankalp logo not found: {logo_path}")
    logo = SVGMobject(str(logo_path)).set(width=brand.LOGO_WIDTH)
    return logo.to_corner(UR, buff=brand.LOGO_BUFF)


def build_footer(fonts: BrandFonts) -> VGroup:
    footer = text(brand.FOOTER_TEXT, fonts, brand.FOOTER_FONT_SIZE, color=brand.MUTED, bold=True)
    footer.to_edge(DOWN, buff=brand.FOOTER_BUFF).to_edge(LEFT, buff=brand.FOOTER_LEFT_BUFF)
    return VGroup(footer)


def _calm_background() -> VGroup:
    return VGroup(
        Circle(radius=3.2, color=brand.ACCENT, stroke_width=2, stroke_opacity=0.08).shift(LEFT * 6 + DOWN * 3),
        Circle(radius=2.4, color=brand.CYAN, stroke_width=2, stroke_opacity=0.07).shift(RIGHT * 6 + UP * 3),
    )


def _grid_background():
    grid = VGroup()
    for x in range(-7, 8):
        grid.add(Line([x, -4, 0], [x, 4, 0], color=brand.ELECTRIC, stroke_width=0.45, stroke_opacity=0.055))
    for y in range(-4, 5):
        grid.add(Line([-8, y, 0], [8, y, 0], color=brand.CYAN, stroke_width=0.45, stroke_opacity=0.045))
    glows = VGroup(
        Circle(radius=3.4, color=brand.ELECTRIC, stroke_opacity=0.08, stroke_width=3).shift(LEFT * 6 + DOWN * 2.8),
        Circle(radius=2.7, color=brand.VIOLET, stroke_opacity=0.07, stroke_width=3).shift(RIGHT * 6 + UP * 2.7),
    )
    circuits = VGroup(
        Line([-7, 2.8, 0], [-5.7, 2.8, 0], color=brand.CYAN, stroke_opacity=0.16),
        Line([-5.7, 2.8, 0], [-5.2, 2.3, 0], color=brand.CYAN, stroke_opacity=0.16),
        Line([5.2, -2.8, 0], [6.5, -2.8, 0], color=brand.VIOLET, stroke_opacity=0.16),
        Line([5.2, -2.8, 0], [4.7, -2.3, 0], color=brand.VIOLET, stroke_opacity=0.16),
        Dot([-5.7, 2.8, 0], radius=0.035, color=brand.CYAN),
        Dot([5.2, -2.8, 0], radius=0.035, color=brand.VIOLET),
    )
    ambient = Circle(radius=3.15, color=brand.CYAN, stroke_width=1, stroke_opacity=0.04)
    ambient.shift(RIGHT * 5.6 + UP * 2.9)
    return VGroup(grid, glows, circuits, ambient), ambient


def add_brand_frame(scene, fonts: BrandFonts, style: str = "calm") -> BrandFrame:
    """Add the shared background, logo, and footer to `scene`.

    style "calm" is the standard template's quiet glow; "grid" is the
    flagship's circuit grid. Palette, logo, footer, and fonts are identical.
    """
    scene.camera.background_color = brand.BG
    ambient = None
    if style == "grid":
        background, ambient = _grid_background()
    elif style == "calm":
        background = _calm_background()
    else:
        raise ValueError(f"unknown brand frame style: {style}")
    background.set_z_index(-20)
    scene.add(background)
    logo = build_logo()
    logo.set_z_index(100)
    footer = build_footer(fonts)
    scene.add_foreground_mobjects(logo, footer)
    return BrandFrame(background=background, logo=logo, footer=footer, ambient=ambient)
