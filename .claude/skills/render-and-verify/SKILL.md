---
name: render-and-verify
description: Render a test video offline, run the automated video QA gates, and inspect sampled frames so a visual, timing or audio change is backed by evidence. Use after changing scenes, templates, the renderer, themes, TTS, captions or the lesson schema.
---

# Render and verify

Purpose: produce evidence for a change that can affect pixels, motion or sound, and be exact about what that
evidence does and does not show.

## 1. Choose the render

| Goal | Command | Notes |
| --- | --- | --- |
| Fast iteration, no audio | `python app.py sample --render --no-voiceover --quality low` | Works offline. Manim `-ql` is 854x480 at 15 fps. |
| Layout check at final size | `python app.py sample --render --no-voiceover --quality high` | Manim `-qh` is 1080p60, the project spec. Slower. |
| Narrated final | add narration with the local TTS service | Needs the TTS voice installed. Do not attempt in an environment without it. |

`--quality` accepts low, medium, high, production, 4k. Check `python app.py --help` for the current flags before relying on this table, and update this file if
they changed. Use `.venv/bin/python`.

If Manim, FFmpeg or Cairo is missing, say so and stop. Do not mock a render.

## 2. Run the automated gates

```bash
python scripts/qa/check_video.py <video.mp4> --profile preview --no-audio-required \
  --report qa_report.json --frames-dir qa_frames
```

Use `--profile final` for a release candidate. It enforces 1920x1080, 60 fps, H.264, yuv420p, AAC audio,
loudness near -16 LUFS, true peak at or below -1 dBTP, no clipping, matching audio and video length.
Thresholds are proposals in `docs/quality/acceptance-criteria.md`; they are not facts about Manim.

Exit code 0 means no errors, 1 means a failed gate, 2 means the checker could not run. Warnings
(long silences, content near the frame edge, frozen sections) need a human decision, not automatic dismissal.

If the lesson has a caption file, also run `python scripts/qa/check_captions.py <captions.srt> --video-seconds <length>`
(`ffprobe` gives the length). It checks structure and readability, not wording.

## 3. Look at the frames

Open `qa_frames/contact_sheet.jpg` and at least three individual frames, including the first scene, the
densest scene and the last one. Check, and write down for each frame:

- Text is inside the safe area, readable and not overlapping.
- Code, output and highlights match what the narration or caption says at that moment.
- Colours come from the theme tokens, not ad-hoc values.
- No placeholder text, debug labels or empty scenes.

If you cannot view images in this session, say "frames were not visually inspected" in the PR.

## 4. Regression compare (optional)

```bash
python scripts/qa/check_video.py <video.mp4> --frames-dir qa_frames --update-golden tests/golden/<name>   # create
python scripts/qa/check_video.py <video.mp4> --frames-dir qa_frames --golden tests/golden/<name>          # compare
```

Golden frames are small PNGs and may be committed; only update them when a visual change is intended and
approved. Never update a golden set to silence a failure.

## 5. Report

Put in the PR: the render command, the QA command, the exit code, the report's errors and warnings, the
frames you inspected, and these two lines verbatim, filled in:

- Automated gates cover: container spec, loudness and clipping, blank frames, edge contact, frozen sections.
- Not verified by automation: explanation accuracy, visual-narration match, legibility, voice quality, motion feel.
  Needs human review: <yes/no and who>.

## Do not

Commit videos, frames or `qa_report.json`. Lower a threshold or add `--no-audio-required` to final renders to
pass a gate. Say a video is "studio quality". The most you can say is which gates passed and what a human
still has to judge.
