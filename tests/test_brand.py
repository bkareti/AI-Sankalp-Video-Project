import re
import tempfile
import unittest
from pathlib import Path

from ai_sankalp import brand

ROOT = Path(__file__).resolve().parents[1]
MAC_FONTS = ["Avenir Next", "Helvetica Neue", "Menlo", "Arial", "Courier New", "Sans", "Monospace", "Times"]
LINUX_FONTS = ["DejaVu Sans", "DejaVu Sans Mono", "DejaVu Serif", "Liberation Serif", "Sans", "Monospace"]
BARE_FONTS = ["Sans", "Monospace", "Serif"]


class FontResolutionTests(unittest.TestCase):
    def test_resolve_font_macos(self):
        self.assertEqual("Avenir Next", brand.resolve_font(brand.SANS_FALLBACKS, MAC_FONTS))
        self.assertEqual("Menlo", brand.resolve_font(brand.MONO_FALLBACKS, MAC_FONTS))

    def test_resolve_font_linux(self):
        self.assertEqual("DejaVu Sans", brand.resolve_font(brand.SANS_FALLBACKS, LINUX_FONTS))
        self.assertEqual("DejaVu Sans Mono", brand.resolve_font(brand.MONO_FALLBACKS, LINUX_FONTS))

    def test_resolve_font_bare_system_never_serif(self):
        self.assertEqual("Sans", brand.resolve_font(brand.SANS_FALLBACKS, BARE_FONTS))
        self.assertEqual("Monospace", brand.resolve_font(brand.MONO_FALLBACKS, BARE_FONTS))
        self.assertEqual("Sans", brand.resolve_font(brand.SANS_FALLBACKS, []))

    def test_resolution_is_case_insensitive(self):
        self.assertEqual("Avenir Next", brand.resolve_font(brand.SANS_FALLBACKS, ["avenir next"]))

    def test_chains_end_with_generic_families(self):
        self.assertEqual(brand.GENERIC_SANS, brand.SANS_FALLBACKS[-1])
        self.assertEqual(brand.GENERIC_MONO, brand.MONO_FALLBACKS[-1])

    def test_bundled_fonts_preferred(self):
        with tempfile.TemporaryDirectory() as directory:
            font_dir = Path(directory)
            (font_dir / "Inter-Regular.ttf").write_bytes(b"")
            (font_dir / "JetBrainsMono-Regular.otf").write_bytes(b"")
            (font_dir / "notes.txt").write_text("ignored")
            files = brand.bundled_font_files(font_dir)
            self.assertEqual(["Inter-Regular.ttf", "JetBrainsMono-Regular.otf"], [path.name for path in files])
            families = {"Inter-Regular.ttf": "Inter", "JetBrainsMono-Regular.otf": "JetBrains Mono"}
            sans, mono = brand.font_chains(files, family_of=lambda path: families[path.name])
            self.assertEqual("Inter", sans[0])
            self.assertEqual("JetBrains Mono", mono[0])
            self.assertEqual("Inter", brand.resolve_font(sans, MAC_FONTS + ["Inter"]))

    def test_brand_fonts_registers_bundled_files_before_listing(self):
        from unittest import mock

        calls = []
        fake_pango = mock.Mock()
        fake_pango.register_font.side_effect = lambda path: calls.append(("register", Path(path).name))
        fake_pango.list_fonts.side_effect = lambda: calls.append(("list",)) or MAC_FONTS + ["Inter", "JetBrains Mono"]
        families = {"Inter-Regular.ttf": "Inter", "JetBrainsMono-Regular.ttf": "JetBrains Mono"}
        with tempfile.TemporaryDirectory() as directory:
            font_dir = Path(directory)
            for name in families:
                (font_dir / name).write_bytes(b"")
            brand.brand_fonts.cache_clear()
            try:
                with mock.patch.object(brand, "FONT_DIR", font_dir), \
                        mock.patch.dict("sys.modules", {"manimpango": fake_pango}), \
                        mock.patch.object(brand, "_family_name", side_effect=lambda path: families[path.name]):
                    fonts = brand.brand_fonts()
            finally:
                brand.brand_fonts.cache_clear()
        self.assertEqual(
            [("register", "Inter-Regular.ttf"), ("register", "JetBrainsMono-Regular.ttf"), ("list",)], calls,
        )
        self.assertEqual(brand.BrandFonts(sans="Inter", mono="JetBrains Mono"), fonts)

    def test_missing_font_dir_is_empty(self):
        self.assertEqual([], brand.bundled_font_files(Path("/nonexistent/fonts")))


class SafeAreaTests(unittest.TestCase):
    def test_safe_area_invariants(self):
        self.assertGreater(brand.CONTENT_SAFE_BOTTOM_Y, brand.CAPTION_BAND_TOP_Y)
        self.assertGreater(brand.CAPTION_BAND_TOP_Y, brand.CAPTION_BAND_BOTTOM_Y)
        self.assertGreater(brand.CAPTION_BAND_BOTTOM_Y, brand.FOOTER_TOP_Y)
        self.assertLess(brand.SAFE_TOP_Y, brand.FRAME_HEIGHT / 2)

    def test_caption_band_pixels(self):
        top, bottom = brand.caption_band_pixels(1080)
        self.assertEqual((915, 1029), (top, bottom))
        top, bottom = brand.caption_band_pixels(480)
        self.assertTrue(0.84 * 480 < top < bottom < 0.96 * 480)

    def test_palette_matches_brand_rules(self):
        for token in ("background", "panel", "panel_raised", "primary", "cyan", "mint", "gold", "text", "muted", "warning"):
            self.assertRegex(brand.PALETTE[token], r"^#[0-9A-F]{6}$")
        self.assertEqual("#071321", brand.BG)
        self.assertEqual("#1473E6", brand.ACCENT)


class SourceScanTests(unittest.TestCase):
    def test_no_hex_or_font_literals_outside_brand(self):
        sources = list((ROOT / "ai_sankalp").glob("*.py")) + list((ROOT / "ai_sankalp" / "primitives").glob("*.py"))
        offenders = []
        for path in sources:
            if path.name == "brand.py":
                continue
            source = path.read_text(encoding="utf-8")
            for pattern in (r"#[0-9A-Fa-f]{6}\b", r"""font\s*=\s*["']"""):
                for match in re.finditer(pattern, source):
                    line = source.count("\n", 0, match.start()) + 1
                    offenders.append(f"{path.relative_to(ROOT)}:{line}: {match.group(0)}")
        self.assertEqual([], offenders)


class BrandMobjectTests(unittest.TestCase):
    """Builds real Manim mobjects (no rendering, no network)."""

    @classmethod
    def setUpClass(cls):
        from ai_sankalp.primitives.frame import build_footer, build_logo

        cls.fonts = brand.BrandFonts(sans="Sans", mono="Monospace")
        cls.logo = build_logo()
        cls.footer = build_footer(cls.fonts)

    def test_logo_in_upper_right_safe_area(self):
        self.assertAlmostEqual(brand.LOGO_WIDTH, self.logo.width, places=3)
        self.assertAlmostEqual(self.logo.width, self.logo.height, places=2)  # native 1:1 SVG
        self.assertGreaterEqual(self.logo.get_left()[0], brand.LOGO_ZONE_MIN_X)
        self.assertGreaterEqual(self.logo.get_bottom()[1], brand.LOGO_ZONE_MIN_Y)
        self.assertLessEqual(self.logo.get_top()[1], brand.FRAME_HEIGHT / 2 - 0.2)

    def test_footer_text_shared_and_below_caption_band(self):
        self.assertEqual("AI SANKALP  •  VISUAL LEARNING", brand.FOOTER_TEXT)
        self.assertLessEqual(self.footer.get_top()[1], brand.FOOTER_TOP_Y)
        self.assertLess(self.footer.get_left()[0], 0)


if __name__ == "__main__":
    unittest.main()
