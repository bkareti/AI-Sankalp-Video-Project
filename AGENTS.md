# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python Manim project for AI Sankalp educational videos. Scene source files live in `scenes/`; each file should define one Manim scene class, such as `SmokeTest` in `scenes/smoke_test.py` or `CArrayBeginners` in `scenes/c_array_beginners.py`. Use `scenes/lesson_template.py` as the starting point for new lessons. Shared visual assets belong in `assets/`, generated Manim output is written under `media/`, and final exported videos can be placed in `output/`. Helper scripts live in `scripts/`.

## Build, Test, and Development Commands

Set up the local environment before rendering:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run a quick render health check:

```bash
manim -ql scenes/smoke_test.py SmokeTest
```

Preview the main lesson with the project helper:

```bash
scripts/render_preview.sh scenes/c_array_beginners.py CArrayBeginners
```

Use `manim -pqh scenes/c_array_beginners.py CArrayBeginners` for a higher-quality review render. Voiceover rendering uses `gTTS`, so it may require internet access.

## Coding Style & Naming Conventions

Use Python with 4-space indentation and descriptive scene class names in `PascalCase`. File names should be lowercase with underscores, for example `python_for_loops.py`. Keep reusable colors, layout constants, and asset paths near the top of a scene file. Prefer clear Manim groups (`VGroup`, `Text`, `SVGMobject`) and short comments only for non-obvious animation or layout choices.

## Testing Guidelines

There is no formal automated test suite yet. Treat rendering as the primary verification step. Run `SmokeTest` after environment changes, then render the edited lesson at low quality with `-ql`. Review the generated files under `media/videos/` for timing, framing, text overflow, logo placement, and voiceover sync.

## Commit & Pull Request Guidelines

No git history is available in this workspace, so use concise imperative commit messages such as `Add array lesson scene` or `Fix logo placement`. Pull requests should describe the lesson or rendering change, list the Manim command used for verification, and include screenshots or a short video sample when visual output changes. Mention any new external assets, fonts, or voiceover dependencies.

## Security & Configuration Tips

Do not commit `.venv/`, local editor state, or large scratch exports. Keep reusable source assets in `assets/`; generated Manim cache and videos should stay in `media/` unless a final deliverable belongs in `output/`.
