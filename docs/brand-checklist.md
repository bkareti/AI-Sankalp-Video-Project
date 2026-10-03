# Brand smoke checklist

Run this after any change to a template, a primitive, or `ai_sankalp/brand.py`.

## Render

```bash
.venv/bin/python app.py sample --render --no-voiceover --quality low
.venv/bin/python app.py generate --config examples/arrays_in_cpp/config.json --render --no-voiceover --quality low
```

Extract frames (pick times that land on the intro, an explanation slide with
and without a visual, code, summary, and outro):

```bash
ffmpeg -v error -ss 12 -i generated/videos/python_for_loops.mp4 -frames:v 1 /tmp/frame_12.png
```

## Check every frame

- [ ] **Logo:** the supplied SVG sits in the upper-right corner at its native
      square proportions, with no extra badge, border, or recoloring, and no
      content overlaps it.
- [ ] **Footer:** `AI SANKALP • VISUAL LEARNING` sits small and muted in the
      bottom-left, in both templates.
- [ ] **Fonts:** text is a clean sans-serif and code is monospace. Nothing
      renders in a serif font.
- [ ] **Palette:** dark navy background (`#071321`), blue/cyan accents, mint for
      positive and coral for warnings. Meaning is never carried by color alone.
- [ ] **Safe margins:** text and panels stay clear of the left and right edges
      and the top edge.
- [ ] **Caption band:** nothing important sits in the bottom band reserved for
      captions (roughly the lowest 15% of the frame, above the footer).
- [ ] **Readability:** at normal phone playback size, every label and code line
      is readable, and no text overflows its panel.
- [ ] **Section visuals:** sections without a `visual` use the full-width
      bullet panel; sections with one show only the text supplied in the
      config.

Source of truth for tokens and limits: `ai_sankalp/brand.py`.
