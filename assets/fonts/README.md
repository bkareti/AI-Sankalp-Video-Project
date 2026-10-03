# Bundled fonts (optional)

Drop `.ttf` or `.otf` files here to make every AI Sankalp video use them on
any machine. At render time the files are registered with Pango
(`manimpango.register_font`) and their families are tried before the system
fallback chain in `ai_sankalp/brand.py`. A family whose name contains "Mono"
is used for code; anything else is used for text.

No fonts are committed yet. The recommended pair is **Inter** (text) and
**JetBrains Mono** (code), both under the SIL Open Font License 1.1.

Licensing rule: only add fonts whose license allows redistribution, and commit
the license file (for example `OFL.txt`) next to the font files.

Without bundled fonts, the fallback chains are:

- Text: Avenir Next, Inter, Helvetica Neue, Segoe UI, Noto Sans, DejaVu Sans,
  Liberation Sans, Arial, then the generic `Sans` family.
- Code: Menlo, JetBrains Mono, SF Mono, Consolas, DejaVu Sans Mono,
  Liberation Mono, Noto Sans Mono, Courier New, then the generic `Monospace`.

The generic families at the end of each chain mean text never falls back to
a serif font.
