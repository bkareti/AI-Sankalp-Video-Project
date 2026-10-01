"""AI Sankalp brand kit: palette, fonts, logo, footer, and safe areas.

Every template and primitive takes colors, fonts, and layout limits from
here, so all videos look like one product. Manim and ManimPango are imported
lazily; the constants and pure helpers work without them.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# --- Palette -----------------------------------------------------------------
PALETTE: Dict[str, str] = {
    "background": "#071321",
    "panel": "#10243A",
    "panel_raised": "#16324F",
    "primary": "#1473E6",
    "cyan": "#21D4FD",
    "mint": "#55E6C1",
    "gold": "#FFC857",
    "text": "#F5F9FF",
    "muted": "#9EB3C7",
    "warning": "#FF6B6B",
    "violet": "#9A7BFF",
    "electric": "#4C8DFF",
    "white": "#FFFFFF",
}
BG = PALETTE["background"]
PANEL = PALETTE["panel"]
PANEL_2 = PALETTE["panel_raised"]
ACCENT = PALETTE["primary"]
CYAN = PALETTE["cyan"]
MINT = PALETTE["mint"]
GOLD = PALETTE["gold"]
SOFT_WHITE = PALETTE["text"]
MUTED = PALETTE["muted"]
CORAL = PALETTE["warning"]
VIOLET = PALETTE["violet"]
ELECTRIC = PALETTE["electric"]
WHITE = PALETTE["white"]
# Repeating accent order for sibling items such as array cells or flow nodes.
ACCENT_CYCLE: Tuple[str, ...] = (CYAN, ELECTRIC, VIOLET, MINT, GOLD)

# --- Fonts -------------------------------------------------------------------
FONT_DIR = PROJECT_ROOT / "assets" / "fonts"
# Avenir Next/Menlo first keeps the established macOS look; the generic Pango
# families at the end guarantee a sans/mono pair (never the serif default).
SANS_FALLBACKS: Tuple[str, ...] = (
    "Avenir Next", "Inter", "Helvetica Neue", "Segoe UI", "Noto Sans",
    "DejaVu Sans", "Liberation Sans", "Arial", "Sans",
)
MONO_FALLBACKS: Tuple[str, ...] = (
    "Menlo", "JetBrains Mono", "SF Mono", "Consolas", "DejaVu Sans Mono",
    "Liberation Mono", "Noto Sans Mono", "Courier New", "Monospace",
)
GENERIC_SANS = "Sans"
GENERIC_MONO = "Monospace"
FONT_SUFFIXES = (".ttf", ".otf")


@dataclass(frozen=True)
class BrandFonts:
    sans: str
    mono: str


def resolve_font(candidates: Sequence[str], available: Iterable[str]) -> str:
    """Return the first candidate installed on this machine (case-insensitive).

    The last candidate is a generic Pango family and is used when nothing else
    matches, so the result is always a usable font name.
    """
    installed = {name.lower() for name in available}
    for name in candidates:
        if name.lower() in installed:
            return name
    return candidates[-1]


def bundled_font_files(font_dir: Path = FONT_DIR) -> List[Path]:
    if not font_dir.is_dir():
        return []
    return sorted(path for path in font_dir.iterdir() if path.suffix.lower() in FONT_SUFFIXES)


def _family_name(path: Path) -> Optional[str]:
    try:
        from PIL import ImageFont

        family, _style = ImageFont.truetype(str(path), size=12).getname()
        return family
    except Exception:
        return None


def font_chains(
    font_files: Sequence[Path], family_of: Callable[[Path], Optional[str]] = _family_name
) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """Prepend bundled families to the sans and mono fallback chains."""
    sans: List[str] = []
    mono: List[str] = []
    for path in font_files:
        family = family_of(path)
        if not family:
            continue
        target = mono if "mono" in family.lower() else sans
        if family not in target:
            target.append(family)
    return tuple(sans) + SANS_FALLBACKS, tuple(mono) + MONO_FALLBACKS


@lru_cache(maxsize=1)
def brand_fonts() -> BrandFonts:
    """Register bundled fonts and resolve the sans/mono pair (Manim process only)."""
    import manimpango

    files = bundled_font_files()
    for path in files:
        manimpango.register_font(str(path))
    sans_chain, mono_chain = font_chains(files)
    available = manimpango.list_fonts()
    return BrandFonts(sans=resolve_font(sans_chain, available), mono=resolve_font(mono_chain, available))


# --- Frame, safe areas, logo, footer (Manim units; frame is 14.22 x 8) --------
FRAME_WIDTH = 8.0 * 16 / 9  # 14.22...
FRAME_HEIGHT = 8.0
SAFE_MARGIN_X = 0.45
SAFE_TOP_Y = 3.76
CONTENT_MAX_WIDTH = FRAME_WIDTH - 2 * SAFE_MARGIN_X

LOGO_PATH = PROJECT_ROOT / "assets" / "ai_sankalp_logo.svg"
LOGO_WIDTH = 0.72
LOGO_BUFF = 0.22
# Content must stay out of the logo box in the upper-right corner.
LOGO_ZONE_MIN_X = 6.0
LOGO_ZONE_MIN_Y = 2.95

FOOTER_TEXT = "AI SANKALP  •  VISUAL LEARNING"
FOOTER_FONT_SIZE = 13
FOOTER_BUFF = 0.13
FOOTER_LEFT_BUFF = 0.3

# Lower-third band reserved for captions (see issue #8). Content stays above
# CONTENT_SAFE_BOTTOM_Y; the footer sits below the band.
CAPTION_BAND_TOP_Y = -2.78
CAPTION_BAND_BOTTOM_Y = -3.62
CONTENT_SAFE_BOTTOM_Y = -2.70
FOOTER_TOP_Y = -3.70


def caption_band_pixels(height_px: int) -> Tuple[int, int]:
    """Map the caption band to (top, bottom) pixel rows for a frame height."""
    def to_row(y: float) -> int:
        return round((FRAME_HEIGHT / 2 - y) / FRAME_HEIGHT * height_px)

    return to_row(CAPTION_BAND_TOP_Y), to_row(CAPTION_BAND_BOTTOM_Y)


# --- Shared component styles ---------------------------------------------------
PANEL_STYLE = {
    "corner_radius": 0.18,
    "stroke_color": ACCENT,
    "stroke_opacity": 0.55,
    "fill_color": PANEL,
    "fill_opacity": 0.96,
}
CODE_STYLE = "monokai"
