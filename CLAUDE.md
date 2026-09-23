# AI Sankalp Video Project

A local Python + Manim app that turns a lesson config (JSON/YAML) into a
branded, narrated educational programming video. Lessons are data: configs go
through `ai_sankalp/` (models → generator → renderer), not hand-edited scenes.

GitHub: `bkareti/AI-Sankalp-Video-Project` (SSH remote alias
`github-personal`). Default branch: `main`. Work in this checkout; do not
switch to other local clones of the repo.

## Layout

- `app.py`: CLI and desktop entry point (`gui`, `generate`, `sample`,
  `interactive`, `history`, `check`)
- `ai_sankalp/`: `models.py` (config validation), `config_io.py`,
  `generator.py` (scene wrapper generation), `renderer.py` (Manim
  orchestration), `manim_scene.py` (`standard` template),
  `futuristic_array_scene.py` (flagship `futuristic_array` template, currently
  C++ arrays-specific), `history.py`, `edge_tts_service.py`, `gui.py`
- `templates/lesson.schema.json`: lesson config contract.
  `templates/generated_scene.py.tmpl`: generated scene entry point.
- `examples/`: tracked sample configs. `examples/arrays_in_cpp/` holds the
  flagship rich lesson package and its reduced config.
- `generated/`: local output (configs, scenes, audio, videos, packages,
  history). Gitignored except `.gitkeep`.
- `scenes/`: hand-authored Manim references. Routine lessons use the generator.
- `tests/`: fast offline `unittest` suite.
- `skills/`: the project's agent skills (Codex layout), linked into
  `.claude/skills/`.
- `.claude/agents/`: Claude Code subagents.
- `ISSUES.md`: roadmap background. GitHub issues are the source of truth.

## Commands

Always use the project virtualenv:

```bash
.venv/bin/python -m unittest discover -s tests -v                # unit tests
.venv/bin/python app.py check                                     # env check
.venv/bin/python app.py sample                                    # generate, no render
.venv/bin/python app.py sample --render --no-voiceover --quality low   # offline render
.venv/bin/python app.py generate --config examples/arrays_in_cpp/config.json --render --quality low  # flagship
.venv/bin/python -m manim -ql scenes/smoke_test.py SmokeTest      # Manim health
```

Narrated renders use gTTS or Edge TTS and need network access. Unit tests must
never need network access.

## Implementing Issues (default workflow)

When the user says "implement issue N", "implement issues 2, 4 and 7",
"fix #N", or similar, use the **`ai-sankalp-issue-developer`** skill
(`skills/ai-sankalp-issue-developer/SKILL.md`) and follow its pipeline end to
end, without waiting for per-phase approval:

1. **Intake:** check the repo, the working tree, and existing PRs/branches per
   issue (never open a duplicate PR).
2. **Architect review:** delegate to the `ai-sankalp-architect` subagent
   (skill `ai-sankalp-issue-architect`) for all requested issues. It returns a
   design brief per issue with gaps resolved, known limitations, a test plan,
   a verification gate, and a dependency-ordered execution plan. Ask the user
   only about `BLOCKED` items.
3. **Branch:** `issue/<n>-<slug>`, `fix/<n>-<slug>`, `docs/<n>-<slug>`,
   `qa/<n>-<slug>` from the latest `origin/main`. Stack a dependent issue on
   its parent's branch.
4. **Implement and test:** follow the brief. Every behavior change gets
   deterministic offline tests.
5. **Verification gate:** tests, `app.py check`, `app.py sample`, plus a
   low-quality render and frame inspection for any visual change.
6. **Review ⟲ fix:** delegate to the `ai-sankalp-reviewer` subagent (skill
   `ai-sankalp-code-reviewer`). Fix every Blocker, Major, and Minor finding,
   re-run the gate, and re-review until the verdict is `PASS`. After 3 rounds
   without `PASS`, stop and report instead of opening a PR.
7. **Commit, push, PR:** Conventional Commits, `Closes #<n>`, and a PR body
   with design decisions, AC coverage, verification commands, review rounds,
   and known limitations. Report the PR URL.

The other skills:
- `ai-sankalp-release-manager`: branching policy, release notes, versioning,
  release readiness.
- `ai-sankalp-video-assets`: lesson packages and videos from a topic
  ("create video to explain arrays in C++").

## Conventions

- Python, 4-space indent, `PascalCase` scene classes, `snake_case` files.
  Keep colors, layout constants, and asset paths near the top of scene files.
- Brand palette and rules live in `skills/ai-sankalp-video-assets/SKILL.md`.
  Keep the logo in the upper-right safe area, keep safe margins, and leave
  caption space.
- Keep the rich lesson package as the source of truth. Prefer data-driven Manim
  primitives over topic-specific hardcoded visuals.
- `visual_template` is validated in `ai_sankalp/models.py`. Adding a template
  means updating validation, the generator routing, the schema, and tests.
- No absolute local paths, secrets, `.venv/`, `media/`, or `generated/`
  output in commits. Stage files by explicit path.

## Hard Stops (ask first)

Never merge PRs, push to `main`, force-push, create tags or releases, close
issues by hand, change repo settings, or upload or publish videos, unless the
user explicitly asks.
