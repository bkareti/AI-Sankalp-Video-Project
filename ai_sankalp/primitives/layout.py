"""Brand-aware text, panel, and card helpers shared by every template."""
from __future__ import annotations

import textwrap
from typing import Optional

from manim import BOLD, DOWN, LEFT, NORMAL, RIGHT, UP, Code, Line, RoundedRectangle, Text, VGroup

from .. import brand
from ..brand import BrandFonts


TEXT_OVERSAMPLE = 4


def fit(mobject, max_width: float, max_height: Optional[float] = None):
    """Scale `mobject` down (never up) to fit the given box."""
    if mobject.width > max_width:
        mobject.scale_to_fit_width(max_width)
    if max_height is not None and mobject.height > max_height:
        mobject.scale_to_fit_height(max_height)
    return mobject


def wrap_text(value: str, width: int) -> str:
    return textwrap.fill(" ".join(str(value).split()), width=width, break_long_words=False)


def text(
    value: str,
    fonts: BrandFonts,
    size: float = 24,
    color: str = brand.SOFT_WHITE,
    bold: bool = False,
    mono: bool = False,
    **kwargs,
) -> Text:
    # Pango rounds glyph advances at small sizes, which visibly breaks
    # kerning ("PYTHONFOR LOOPS"). Typeset large, then scale to `size`.
    mobject = Text(
        str(value),
        font=fonts.mono if mono else fonts.sans,
        font_size=size * TEXT_OVERSAMPLE,
        color=color,
        weight=BOLD if bold else NORMAL,
        **kwargs,
    )
    return mobject.scale(1 / TEXT_OVERSAMPLE)


def panel(width: float, height: float, stroke_color: str = brand.ACCENT, **overrides) -> RoundedRectangle:
    style = dict(brand.PANEL_STYLE, stroke_color=stroke_color)
    style.update(overrides)
    return RoundedRectangle(width=width, height=height, **style)


def glass_card(
    label: str,
    fonts: BrandFonts,
    color: str = brand.CYAN,
    width: float = 2.55,
    height: float = 0.82,
    font_size: float = 22,
    mono: bool = False,
) -> VGroup:
    box = RoundedRectangle(
        width=width, height=height, corner_radius=0.16,
        stroke_color=color, stroke_width=1.8,
        fill_color=brand.PANEL_2, fill_opacity=0.94,
    )
    caption = text(label, fonts, font_size, bold=True, mono=mono)
    fit(caption, width - 0.32, height - 0.18)
    caption.move_to(box)
    return VGroup(box, caption)


def section_label(value: str, fonts: BrandFonts) -> Text:
    label = text(value.upper(), fonts, 15, color=brand.CYAN, bold=True)
    return label.to_edge(LEFT, buff=brand.SAFE_MARGIN_X).to_edge(UP, buff=0.28)


def title_text(value: str, fonts: BrandFonts, size: float = 40) -> Text:
    title = fit(text(value, fonts, size, bold=True), brand.LOGO_ZONE_MIN_X + 5.2)
    return title.to_edge(UP, buff=0.48).to_edge(LEFT, buff=brand.SAFE_MARGIN_X)


def header(eyebrow: str, title: str, fonts: BrandFonts) -> VGroup:
    eyebrow_text = text(eyebrow.upper(), fonts, 15, color=brand.CYAN, bold=True)
    title_mobject = fit(text(title, fonts, 36, bold=True), 11.2)
    accent = Line(LEFT, RIGHT, color=brand.CYAN, stroke_width=4).set_width(1.65)
    group = VGroup(eyebrow_text, title_mobject, accent).arrange(DOWN, buff=0.11, aligned_edge=LEFT)
    return group.to_edge(UP, buff=0.24).to_edge(LEFT, buff=brand.SAFE_MARGIN_X)


def code_block(code: str, language: str, fonts: BrandFonts):
    """Syntax-highlighted code window in the brand mono font."""
    try:
        return Code(
            code_string=code,
            language=language,
            formatter_style=brand.CODE_STYLE,
            add_line_numbers=True,
            background="window",
            paragraph_config={"font": fonts.mono},
        )
    except Exception:
        return text(wrap_text(code, 70), fonts, 19, mono=True)
