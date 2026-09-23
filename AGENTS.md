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

Run the offline unit suite with `.venv/bin/python -m unittest discover -s tests -v` for every change. Rendering is the verification step for visual work: run `SmokeTest` after environment changes, then render the edited lesson at low quality. Review the output for timing, framing, text overflow, logo placement, and voiceover sync.

## Implementing Issues

When asked to implement one or more GitHub issues ("implement issues 2, 4 and 7"), use `$ai-sankalp-issue-developer` (`skills/ai-sankalp-issue-developer/SKILL.md`) and follow its pipeline end to end:

1. Architect review with `$ai-sankalp-issue-architect`: resolve gaps, list known limitations, and order issues by dependency.
2. Branch from the latest `origin/main` as `issue/<n>-<slug>`, `fix/<n>-<slug>`, `docs/<n>-<slug>`, or `qa/<n>-<slug>`.
3. Implement with unit tests, then run the verification gate.
4. Review with `$ai-sankalp-code-reviewer` as a separate pass. Fix every Blocker, Major, and Minor finding, and re-review until `PASS`.
5. Commit, push, and open the PR. Never merge.

`CLAUDE.md` holds the same workflow for Claude Code.

## Commit & Pull Request Guidelines

Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`) with `Closes #<n>` or `Refs #<n>`. Pull requests follow the template in the issue-developer skill: summary, design decisions, acceptance-criteria coverage, exact verification commands, review rounds, and known limitations. Include frames or a short video sample when visual output changes, and mention any new external assets, fonts, or voiceover dependencies.

## Security & Configuration Tips

Do not commit `.venv/`, local editor state, or large scratch exports. Keep reusable source assets in `assets/`; generated Manim cache and videos should stay in `media/` unless a final deliverable belongs in `output/`.
