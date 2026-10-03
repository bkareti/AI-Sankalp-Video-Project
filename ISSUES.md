# AI Sankalp Video Automation Roadmap Issues

Prepared from the project brief, local repository audit, and the review in
`REVIEW.md`.

GitHub creation status: real GitHub issues were not created because the
available GitHub credentials could not access
`bkareti/AI-Sankalp-Video-Project`. Use this file as the local fallback issue
list, or copy each issue into GitHub after repository access is available.

## Current Product Reality

The project can make videos today. The current `arrays_in_cpp.mp4` is a real
5:13, 1920x1080 narrated lesson, and the existing 6 unit tests pass.

The strategic gap is that the repository currently contains two different
product paths:

| Area | `standard` template | `futuristic_array` template |
| --- | --- | --- |
| Input | Any reduced lesson config | One C++ arrays package plus hardcoded visuals |
| Reusable for new topics | Yes | No |
| Visual quality | Acceptable, visibly generic | Strong flagship demo |
| Product meaning | MVP fallback | Quality target to productize |

`futuristic_array_scene.py` reads narration from
`generated/packages/<slug>/lesson_package.json`, but its visuals are largely
literal C++ array content: fixed marks values, fixed declaration, fixed
indexing, fixed trace, fixed bounds example, and fixed practice flow. Rendering
another topic with `visual_template: futuristic_array` will still draw the C++
array lesson, or fail if the package is missing.

Therefore the main project is not just "add an AI pipeline." The main project
is to turn the polished C++ array demo style into reusable, data-driven Manim
primitives that can produce comparable quality across Python, C, C++, Java,
SQL, DSA, and AI/ML topics.

## Current Repository Audit

### What Exists

- Python Manim app with CLI and Tkinter entry point in `app.py`.
- Core package in `ai_sankalp/`.
- Config parsing and validation in `ai_sankalp/models.py` and
  `ai_sankalp/config_io.py`.
- Scene wrapper generation in `ai_sankalp/generator.py`.
- Manim render orchestration in `ai_sankalp/renderer.py`.
- Generic reusable scene in `ai_sankalp/manim_scene.py`.
- Polished but hardcoded C++ array scene in
  `ai_sankalp/futuristic_array_scene.py`.
- gTTS and Edge TTS support.
- History logging in `generated/history.jsonl`.
- JSON schema in `templates/lesson.schema.json`.
- Reduced sample config in `examples/python_for_loops.json`.
- Rich generated C++ package currently under
  `generated/packages/arrays_in_cpp/`.
- Hand-authored visual reference scenes in `scenes/`.
- AI Sankalp logo in `assets/ai_sankalp_logo.svg`.
- Codex skill package under `skills/ai-sankalp-video-assets/`.
- Basic generator/model tests in `tests/test_generator.py`.
- VS Code tasks for setup, tests, sample generation, and rendering.

### What Works Today

- Existing unit tests pass.
- Dependency check passes in the current local environment.
- The Python for-loops sample can generate and render offline.
- The C++ arrays flagship render exists locally and is high quality.
- The rich package format already contains many fields the roadmap needs:
  scenes, voice profile, voiceover segments, code examples, assets, branding,
  quality checklist, and `generator_compatibility`.

### Confirmed Blockers

- Clean clones cannot render the flagship sample because `.gitignore` excludes
  `generated/packages/*`, while `FuturisticArrayLesson` hard-requires a package
  JSON under that path.
- Missing `futuristic_array` package prerequisites fail late inside Manim
  rather than during generation.
- Branding is inconsistent because templates use different fonts and font
  assumptions.
- `templates/lesson.schema.json` and README do not document
  `visual_template` or Edge voiceover fields used by the working C++ sample.
- The generic `standard` template fabricates visual model labels from bullet
  text, which produces diagram-looking content without real visual meaning.
- Captions exist only as Manim cache byproducts; they are not stable final
  artifacts, not burned in, not documented, and not QA checked.
- Render cache uses UUID folders, so it neither reuses Manim partial renders
  nor prunes old bytes.
- History records absolute paths instead of repo-relative paths.
- Dependency checks can miss partial installs when `manim` imports but related
  packages are missing.
- Important content truncation can happen without a warning.
- Tests do not cover renderer behavior, schema validity, example configs,
  generated scene compilation, or sample render regression.

## Revised Architecture

Use four implementation components rather than ten runtime agents.

### Planner

- Responsibility: produce or revise a rich lesson package from a topic, script,
  or code example.
- Current source: the existing `ai-sankalp-video-assets` skill.
- Future option: a thin Python LLM adapter only after provider, cost, key, and
  outage policy are decided.
- Output: validated `lesson_package.json` and human-readable package notes.

### Compiler

- Responsibility: convert a rich package into reduced render config, selected
  Manim primitives, generated scene entry point, captions, and render inputs.
- Output: deterministic scene/config/caption artifacts.
- Non-goal: free-form code generation for every video. Prefer reusable
  primitives with data-driven parameters.

### Repair

- Responsibility: use compact errors to repair invalid packages, generated
  scenes, render failures, or missing assets.
- Runs only on failure and only within bounded retry limits.
- Output: repair attempt record and patched package/source where applicable.

### QA

- Responsibility: validate technical content, package structure, render output,
  captions, branding, visual regressions, and human review status.
- Output: `qa_report.json` plus a human review checklist.
- Launch rule: final-ready status requires SME approval.

Deterministic systems such as audio synthesis, asset validation, rendering,
assembly, caching, and storage remain normal code modules, not agents.

## Revised Sequencing

1. Fix blockers B1-B4 and the standard-template visual tell.
2. Promote the existing rich C++ package to committed examples and schema
   fixtures.
3. Productize the polished template system as P0 work.
4. Make captions a launch requirement.
5. Add QA, SME sign-off, and golden regression render checks.
6. Decide the AI provider/runtime/cost architecture.
7. Add CLI, repair, UI, batch, and external asset features after the reusable
   video compiler is solid.

Phase 1 from the original roadmap is dissolved. New folders should appear only
when a feature needs them.

## Issue 1: P0 - Make the Flagship Sample Portable

### Title

P0: Make the flagship C++ arrays sample render from a clean clone

### Goal

Ensure the best current video can be reproduced by a new developer without
untracked generated package files.

### Background

`.gitignore` excludes `generated/packages/*`, but the `futuristic_array`
runtime requires `generated/packages/<slug>/lesson_package.json`. This makes
the flagship sample fragile and breaks the promise that the repository can
demonstrate its best output.

### Tasks

- [x] Move or copy `generated/packages/arrays_in_cpp/lesson_package.json` to a
  tracked fixture path such as `examples/arrays_in_cpp/lesson_package.json`.
- [x] Move or copy the human-readable package markdown to the same example
  folder if useful for review.
- [x] Add fallback lookup in `FuturisticArrayLesson` from generated package path
  to tracked example package path.
- [x] Add an example reduced config for `arrays_in_cpp`.
- [x] Update README with exact commands to render the flagship sample.
- [x] Confirm generated cache and final media policy remains clear.

### Acceptance Criteria

- A clean clone can render the C++ arrays sample after normal setup.
- The flagship package JSON is tracked in Git.
- Missing generated package files no longer break the flagship example.
- The README points to the tracked source package.

### Dependencies

- Existing local sample package.

### Suggested Files/Modules

- `examples/arrays_in_cpp/lesson_package.json`
- `examples/arrays_in_cpp/lesson_package.md`
- `examples/arrays_in_cpp/config.json`
- `ai_sankalp/futuristic_array_scene.py`
- `.gitignore`
- `README.md`

### Test/Verification Plan

- Delete local generated package copy.
- Run sample generation and render commands.
- Confirm final MP4 is created.
- Confirm `git ls-files examples/arrays_in_cpp` includes the package.

### Priority

P0

### Estimated Effort

0.5 day

## Issue 2: P0 - Validate Template Prerequisites Early

### Title

P0: Fail early when a selected visual template cannot support a lesson

### Goal

Prevent late Manim subprocess failures for unsupported or missing template
inputs.

### Background

`visual_template: futuristic_array` validates for any lesson, but the scene
requires a package with specific scene IDs and C++ array assumptions. Today
unsupported inputs fail late and unclearly.

### Tasks

- [ ] Add template prerequisite validation in `LessonGenerator.generate()`.
- [ ] Require a package path or supported fallback package for templates that
  need rich package data.
- [ ] Validate required scene IDs before rendering.
- [ ] Reject non-array/non-C++ use of the current `futuristic_array` template
  until it is productized.
- [ ] Return actionable `LessonValidationError` messages.
- [ ] Add tests for missing package, wrong topic/template pairing, and valid
  package fallback.

### Acceptance Criteria

- Unsupported template choices fail before Manim starts.
- Error messages explain the missing package or unsupported template use.
- Existing standard lessons continue to generate.
- Existing C++ array sample remains supported.

### Dependencies

- Issue 1 fixture path decision.

### Suggested Files/Modules

- `ai_sankalp/generator.py`
- `ai_sankalp/models.py`
- `ai_sankalp/futuristic_array_scene.py`
- `tests/test_generator.py`
- `tests/test_templates.py`

### Test/Verification Plan

- Unit test `futuristic_array` without a package.
- Unit test `futuristic_array` with SQL/Python input.
- Unit test valid `arrays_in_cpp` fixture.
- Compile generated scene with `py_compile`.

### Priority

P0

### Estimated Effort

0.5 to 1 day

## Issue 3: P0 - Fix Schema and Documentation Drift

### Title

P0: Document and validate all lesson fields used by working examples

### Goal

Bring schema, README, examples, and model behavior back into sync.

### Background

`models.py` supports `visual_template` and Edge voiceover fields, but
`templates/lesson.schema.json` and README document only the older MVP fields.
Users following docs cannot reproduce the C++ arrays video path.

### Tasks

- [ ] Add `visual_template` to `templates/lesson.schema.json`.
- [ ] Add `voiceover.provider`, `voiceover.voice`, `voiceover.rate`, and
  `voiceover.pitch` to the schema.
- [ ] Document supported visual templates and their constraints.
- [ ] Document gTTS versus Edge TTS behavior and provider limitations.
- [ ] Add schema validation tests for every tracked example config.
- [ ] Update README examples to include the flagship C++ arrays path.

### Acceptance Criteria

- Every tracked example config validates against the schema.
- README explains how to choose `standard` versus `futuristic_array`.
- README explains Edge TTS fields used by the C++ sample.
- Schema and `LessonConfig.from_dict()` agree on accepted fields.

### Dependencies

- Issue 1 tracked examples.

### Suggested Files/Modules

- `templates/lesson.schema.json`
- `README.md`
- `examples/`
- `tests/test_schema.py`
- `ai_sankalp/models.py`

### Test/Verification Plan

- Run schema tests against all example JSON files.
- Run existing unit tests.
- Generate both Python and C++ example configs.

### Priority

P0

### Estimated Effort

0.5 to 1 day

## Issue 4: P0 - Establish a Brand Kit and Font Strategy

### Title

P0: Centralize AI Sankalp brand tokens, fonts, logo rules, and safe areas

### Goal

Make all templates look like one AI Sankalp product across machines.

### Background

The standard and flagship templates use different font assumptions and logo
treatment. The flagship hardcodes macOS fonts, while the standard template can
fall back to serif text.

### Tasks

- [ ] Add a central brand module with colors, font names, safe margins, logo
  sizing, footer text, and common panel styles.
- [ ] Decide whether to bundle fonts under `assets/fonts/`.
- [ ] Define fallback font chain for non-macOS machines.
- [ ] Update both existing templates to use the shared brand module.
- [ ] Keep logo handling consistent and respect native SVG proportions.
- [ ] Add a visual smoke checklist for brand consistency.

### Acceptance Criteria

- Standard and flagship templates share brand constants.
- Text renders in a clean sans/mono pairing on macOS and non-macOS setups.
- Logo and footer placement are consistent.
- No template hardcodes brand colors or fonts unnecessarily.

### Dependencies

- None.

### Suggested Files/Modules

- `ai_sankalp/brand.py`
- `ai_sankalp/manim_scene.py`
- `ai_sankalp/futuristic_array_scene.py`
- `assets/fonts/`
- `README.md`

### Test/Verification Plan

- Unit test brand constants where practical.
- Render standard and flagship samples.
- Inspect representative frames.

### Priority

P0

### Estimated Effort

1 day

## Issue 5: P0 - Remove the Generic Visual Model Tell

### Title

P0: Replace fabricated standard-template visual labels with meaningful visuals

### Goal

Improve the reusable standard template so it no longer looks obviously
auto-generated.

### Background

`_keywords()` derives the "VISUAL MODEL" boxes from the first few words of each
bullet. This creates diagram-shaped content without real instructional meaning.

### Tasks

- [ ] Add an explicit optional visual field to section config, or remove the
  visual panel when no meaningful visual is supplied.
- [ ] Let bullet-only sections use full width when no visual exists.
- [ ] Add simple explicit visual modes such as flow, compare, steps, and table
  only when supplied by data.
- [ ] Add tests for old configs with no visual field.
- [ ] Update README with the new optional section visual format if added.

### Acceptance Criteria

- Standard template no longer fabricates labels from bullet text.
- Existing configs still render.
- Lessons without visuals look intentionally laid out, not half-empty.
- Explicit visuals are data-driven and human-readable in JSON.

### Dependencies

- Issue 3 schema update if a new field is added.

### Suggested Files/Modules

- `ai_sankalp/manim_scene.py`
- `ai_sankalp/models.py`
- `templates/lesson.schema.json`
- `examples/python_for_loops.json`
- `tests/test_generator.py`

### Test/Verification Plan

- Render the Python for-loops sample.
- Inspect the former visual panel frames.
- Run unit tests.

### Priority

P0

### Estimated Effort

1 day

## Issue 6: P0 - Promote Rich Package Schema From Existing Package

### Title

P0: Promote the existing rich lesson package into schema and fixtures

### Goal

Use the current `arrays_in_cpp` package as the seed for the production content
contract instead of designing a second format from scratch.

### Background

The generated C++ package already contains the needed product concepts:
scenes, timing, voice profile, voice delivery metadata, code examples, asset
manifest, branding, quality checklist, and generator compatibility.

### Tasks

- [ ] Move the current rich C++ package to a tracked fixture path.
- [ ] Create `templates/lesson_package.schema.json` from that structure.
- [ ] Add package validation utilities.
- [ ] Add conversion from rich package `generator_compatibility` to reduced
  render config.
- [ ] Preserve backward compatibility for reduced configs.
- [ ] Add fixtures for at least one Python package and one C++ package.

### Acceptance Criteria

- Rich package fixture validates against schema.
- Reduced config generation from package is deterministic.
- Existing `examples/python_for_loops.json` still works.
- Invalid package errors identify actionable fields.

### Dependencies

- Issue 1.
- Issue 3.

### Suggested Files/Modules

- `templates/lesson_package.schema.json`
- `examples/arrays_in_cpp/lesson_package.json`
- `ai_sankalp/config_io.py`
- `ai_sankalp/models.py`
- `ai_sankalp/package.py`
- `tests/test_package_schema.py`

### Test/Verification Plan

- Validate rich fixtures.
- Round-trip rich package to reduced config.
- Run existing tests.

### Priority

P0

### Estimated Effort

1 day

## Issue 7: P0 - Productize Reusable Manim Primitives

### Title

P0: Turn the polished C++ demo style into reusable Manim primitives

### Goal

Create data-driven visual primitives that can produce the flagship quality
level for multiple topics.

### Background

This is the core product work. The current polished scene is a hand-built
one-off. To make reliable videos for topic #2, the project needs reusable
animated primitives with the same polish.

### Tasks

- [ ] Extract reusable layout, text fitting, code panel, title card, and brand
  frame helpers.
- [ ] Build an array/memory lane primitive.
- [ ] Build a loop trace primitive with moving pointer and output stream.
- [ ] Build stack and queue primitives.
- [ ] Build table/SQL join primitives.
- [ ] Build flowchart/process primitives.
- [ ] Build step-reveal code walkthrough primitive.
- [ ] Add scene role mapping from package scene types to primitives.
- [ ] Add visual QA examples for each primitive.
- [ ] Keep existing flagship render visually recognizable while making it
  data-driven.

### Acceptance Criteria

- The C++ arrays video can be rendered from package data rather than fixed
  literals in the scene code.
- At least five reusable primitives are available.
- Each primitive has a small fixture and smoke render path.
- New topics can select primitives through package data.
- The standard template can use these primitives where appropriate.

### Dependencies

- Issue 4.
- Issue 6.

### Suggested Files/Modules

- `ai_sankalp/manim_scene.py`
- `ai_sankalp/futuristic_array_scene.py`
- `ai_sankalp/primitives/`
- `ai_sankalp/templates/`
- `tests/test_primitives.py`
- `docs/templates.md`

### Test/Verification Plan

- Render C++ arrays from data-driven primitives.
- Render one small sample per primitive.
- Compare selected frames against golden expectations.
- Run unit tests.

### Priority

P0

### Estimated Effort

3 to 4 weeks

## Issue 8: P0 - Make Captions a Launch Requirement

### Title

P0: Export, validate, and optionally burn in captions for every final video

### Goal

Ensure phone-first learners can use videos with or without audio.

### Background

Manim Voiceover can create subcaption artifacts, and `.srt` files may appear in
render cache, but captions are not stable final outputs and are not part of QA.

### Tasks

- [ ] Copy generated SRT/VTT files from render cache to the final output folder.
- [ ] Generate captions directly from package narration when render cache does
  not provide them.
- [ ] Add optional burn-in path for phone-friendly final videos.
- [ ] Reserve lower-third safe areas for captions in templates.
- [ ] Add caption presence and duration checks to QA.
- [ ] Update README and CLI help.

### Acceptance Criteria

- Every final video has a stable caption sidecar.
- Caption burn-in can be enabled for review or final export.
- Missing captions block final-ready status.
- Captions do not cover important visuals.

### Dependencies

- Issue 4.
- Issue 7.

### Suggested Files/Modules

- `ai_sankalp/renderer.py`
- `ai_sankalp/captions.py`
- `ai_sankalp/qa/`
- `generated/<slug>/captions/`
- `README.md`

### Test/Verification Plan

- Render narrated sample and confirm caption sidecar is copied.
- Run offline caption generation from package narration.
- Manually inspect burned-in caption sample.

### Priority

P0

### Estimated Effort

2 to 3 days

## Issue 9: P0 - Add QA, SME Gate, and Golden Regression Render

### Title

P0: Add final-ready QA with SME sign-off and visual regression coverage

### Goal

Prevent technically or visually broken videos from being marked ready for
students.

### Background

Current tests cover only models and generator behavior. Production needs QA for
schema, renderability, captions, assets, branding, content review, and visual
regressions.

### Tasks

- [ ] Add `review_status` to rich packages.
- [ ] Require SME approval before final-ready status.
- [ ] Add `qa_report.json` with pass, needs review, and fail statuses.
- [ ] Validate package schema, reduced config, generated scene compilation,
  required assets, caption output, final MP4, and history entry.
- [ ] Add golden regression fixture for the flagship sample.
- [ ] Assert scene count, approximate duration, and selected frame hashes or
  perceptual checks.
- [ ] Add manual review checklist for pedagogy, pacing, readability, and brand.

### Acceptance Criteria

- QA refuses final-ready without SME approval.
- QA catches missing package, missing captions, missing MP4, and invalid schema.
- Golden render catches major template regressions.
- QA output is understandable to a junior team member.

### Dependencies

- Issue 6.
- Issue 8.

### Suggested Files/Modules

- `ai_sankalp/qa/`
- `ai_sankalp/package.py`
- `tests/test_qa.py`
- `tests/test_golden_render.py`
- `docs/review-checklist.md`

### Test/Verification Plan

- Run QA on valid sample.
- Run QA on fixtures with missing captions, missing assets, and no SME approval.
- Run golden regression check.

### Priority

P0

### Estimated Effort

3 to 5 days

## Issue 10: P1 - Decide AI Runtime, Provider, Cost, and Failure Policy

### Title

P1: Decide how AI is called, paid for, secured, and recovered

### Goal

Choose the AI architecture before building repair, UI, and batch features that
depend on it.

### Background

Today authoring works through a human-invoked Codex skill. Later phases assume
Python-side LLM calls. The project needs an explicit decision on model,
runtime, API key ownership, cost per video, rate limits, privacy, and outage
behavior.

### Tasks

- [ ] Decide whether Planner runs through Codex skill, Python LLM adapter, or
  both.
- [ ] Decide model/provider options and minimum quality bar.
- [ ] Estimate token and TTS cost per 5-minute video.
- [ ] Define API key configuration and secret handling.
- [ ] Define offline/degraded behavior.
- [ ] Define where human review enters the AI authoring loop.
- [ ] Document decision in `docs/ai-architecture.md`.

### Acceptance Criteria

- The team can answer which AI runs where.
- Cost per video and batch cost assumptions are documented.
- API keys are not hardcoded.
- Later repair/UI/batch work has a stable integration target.

### Dependencies

- None.

### Suggested Files/Modules

- `docs/ai-architecture.md`
- `ai_sankalp/llm.py` if Python-side calls are selected
- `.env.example`
- `README.md`

### Test/Verification Plan

- Review decision document.
- Add a no-network test path for any LLM adapter.
- Confirm missing API key produces clear errors.

### Priority

P1

### Estimated Effort

1 to 2 days

## Issue 11: P1 - Add Package Compiler Workflow

### Title

P1: Compile rich lesson packages into renderable scenes and configs

### Goal

Make the rich package the source of truth for routine video generation.

### Background

The current generator writes wrapper scenes from reduced configs. The full
pipeline should compile rich packages into reduced config, template choices,
scene entry points, captions, and QA inputs.

### Tasks

- [ ] Add package compiler service.
- [ ] Convert `generator_compatibility` to reduced render config.
- [ ] Select primitives/templates from package scene types and visual objects.
- [ ] Generate deterministic scene entry points.
- [ ] Compile generated scenes with `py_compile`.
- [ ] Store compiler metadata beside outputs.
- [ ] Keep old config-driven generation working.

### Acceptance Criteria

- Rich package compiles to renderable scene/config/caption inputs.
- Compilation is deterministic for unchanged packages.
- Syntax errors fail before render.
- Reduced configs remain supported.

### Dependencies

- Issue 6.
- Issue 7.

### Suggested Files/Modules

- `ai_sankalp/compiler.py`
- `ai_sankalp/generator.py`
- `templates/generated_scene.py.tmpl`
- `generated/scenes/`
- `tests/test_compiler.py`

### Test/Verification Plan

- Compile Python and C++ rich fixtures.
- Run `py_compile` on generated scenes.
- Render one compiled sample offline.

### Priority

P1

### Estimated Effort

3 to 5 days

## Issue 12: P1 - Expand CLI Around the Real Workflow

### Title

P1: Add CLI commands for package, compile, render, QA, and final-ready checks

### Goal

Expose the production workflow without requiring users to know internal file
locations.

### Background

`app.py` already supports sample, generate, interactive, history, and check.
The revised workflow needs package-first commands and QA status.

### Tasks

- [ ] Add `package validate`.
- [ ] Add `package compile`.
- [ ] Add `render`.
- [ ] Add `qa`.
- [ ] Add `final-ready` check.
- [ ] Add flags for language, audience, difficulty, duration, no voiceover,
  captions, quality, and output folder where appropriate.
- [ ] Keep existing CLI commands backward compatible.

### Acceptance Criteria

- A user can validate, compile, render, and QA a package from CLI.
- CLI output lists stable artifact paths.
- Existing sample commands still work.
- Errors are written in non-technical, actionable language.

### Dependencies

- Issue 8.
- Issue 9.
- Issue 11.

### Suggested Files/Modules

- `app.py`
- `ai_sankalp/pipeline.py`
- `README.md`
- `.vscode/tasks.json`
- `tests/test_cli.py`

### Test/Verification Plan

- CLI parser tests.
- Smoke test package validation.
- Smoke test compile/render/QA flow.

### Priority

P1

### Estimated Effort

2 to 4 days

## Issue 13: P1 - Add Bounded Repair Loop

### Title

P1: Add AI-assisted repair for failed packages and renders

### Goal

Repair invalid generated artifacts without hiding failures or retrying
indefinitely.

### Background

Render failures currently surface as errors. A production pipeline should
collect compact failure context and request targeted repair only when useful.

### Tasks

- [ ] Define repair attempt records.
- [ ] Capture schema errors, syntax errors, missing assets, caption failures,
  and Manim render tails.
- [ ] Add bounded retry policy.
- [ ] Add repair prompts for package, scene, asset, and caption issues.
- [ ] Integrate selected LLM architecture from Issue 10.
- [ ] Store repair snapshots.

### Acceptance Criteria

- Repair runs only on eligible failures.
- Retry count is bounded.
- Each repair attempt is logged.
- Final failure reports include original error and attempted fixes.

### Dependencies

- Issue 10.
- Issue 11.
- Issue 9.

### Suggested Files/Modules

- `ai_sankalp/repair.py`
- `ai_sankalp/llm.py`
- `ai_sankalp/history.py`
- `generated/<slug>/repairs/`
- `tests/test_repair.py`

### Test/Verification Plan

- Fixture test for schema repair prompt.
- Fixture test for syntax error repair prompt.
- Test max retry behavior.

### Priority

P1

### Estimated Effort

3 to 5 days

## Issue 14: P1 - Fix Render Cache and History Lifecycle

### Title

P1: Make render cache reusable, prunable, and history paths portable

### Goal

Reduce render waste and keep history useful across repo locations.

### Background

The renderer creates fresh UUID cache folders, so Manim partial renders are not
reused and cache bytes accumulate. History records absolute paths that become
stale when the repo moves.

### Tasks

- [ ] Key render cache by package/config content hash.
- [ ] Add cache prune command or policy.
- [ ] Store repo-relative paths in history.
- [ ] Add migration or tolerant display for older absolute history records.
- [ ] Improve dependency checks for partial installs.
- [ ] Add renderer tests with subprocess mocked where needed.

### Acceptance Criteria

- Re-rendering unchanged content can reuse cache.
- Old cache folders can be pruned safely.
- New history records use repo-relative paths.
- Dependency check validates Manim, Manim Voiceover, gTTS, Edge TTS, PyYAML,
  and FFmpeg consistently.

### Dependencies

- None.

### Suggested Files/Modules

- `ai_sankalp/renderer.py`
- `ai_sankalp/history.py`
- `app.py`
- `tests/test_renderer.py`
- `tests/test_history.py`

### Test/Verification Plan

- Unit test cache key stability.
- Unit test repo-relative history records.
- Mock partial dependency failure.
- Render same sample twice and compare cache behavior.

### Priority

P1

### Estimated Effort

2 to 3 days

## Issue 15: P2 - Add Planner Authoring Flow

### Title

P2: Add topic-to-package planning with human review

### Goal

Turn a user request such as "Explain Python for loops" into a validated rich
package while preserving human review before final production.

### Background

The existing Codex skill already produces strong lesson packages. The product
should integrate that capability thoughtfully rather than prematurely replacing
it with fully autonomous Python LLM calls.

### Tasks

- [ ] Define Planner input fields: topic, language, audience, difficulty,
  duration, optional script/code.
- [ ] Reuse the existing skill contract as the package authoring standard.
- [ ] Add optional Python-side LLM adapter only if Issue 10 selects it.
- [ ] Save package drafts under stable package folders.
- [ ] Require human review before compile/render final status.
- [ ] Add deterministic fixture output for tests.

### Acceptance Criteria

- Topic-only input can produce a package draft through the selected planning
  path.
- Package draft validates against schema.
- Human review status is explicit.
- Offline tests do not require live AI.

### Dependencies

- Issue 6.
- Issue 10.
- Issue 9.

### Suggested Files/Modules

- `ai_sankalp/planner.py`
- `ai_sankalp/llm.py`
- `prompts/`
- `generated/packages/`
- `tests/test_planner.py`

### Test/Verification Plan

- Validate fixture package draft.
- Test missing required topic/language behavior.
- Test no-network fallback path.

### Priority

P2

### Estimated Effort

3 to 5 days

## Issue 16: P2 - Add Asset Manifest and Optional Image Generation

### Title

P2: Manage Manim, reused, and generated assets through a manifest

### Goal

Track required visuals and prevent missing assets from reaching render time.

### Background

Most programming visuals should be Manim-native. Generated bitmap assets should
be optional and used only when they add learning value.

### Tasks

- [ ] Validate asset manifest entries from rich packages.
- [ ] Support `manim`, `reuse`, and `generate` strategies.
- [ ] Verify required reused asset paths.
- [ ] Add optional generated-image prompts for appropriate illustrations.
- [ ] Copy final asset references into package outputs.
- [ ] Add fallback rules for optional assets.

### Acceptance Criteria

- Every package visual object maps to an asset or primitive.
- Missing required assets fail QA.
- Optional generated assets can be skipped without breaking render.
- Code, tables, memory diagrams, and flowcharts remain Manim-native by default.

### Dependencies

- Issue 6.
- Issue 7.

### Suggested Files/Modules

- `ai_sankalp/assets.py`
- `ai_sankalp/qa/`
- `assets/`
- `generated/<slug>/images/`
- `tests/test_assets.py`

### Test/Verification Plan

- Test missing logo/asset failure.
- Test optional asset fallback.
- Validate asset manifest in C++ fixture.

### Priority

P2

### Estimated Effort

2 to 4 days

## Issue 17: P2 - Add Final Assembly and Storage Policy

### Title

P2: Define final video assembly, metadata, and generated media storage policy

### Goal

Create consistent final MP4 packages with metadata, captions, optional music,
and clear storage rules.

### Background

The renderer currently copies a Manim MP4 to `generated/videos`. Production
needs final folders, metadata, optional music/outro hooks, and a policy for
which generated artifacts are tracked, ignored, or stored externally.

### Tasks

- [ ] Define final output layout under `generated/<slug>/video/` or another
  stable path.
- [ ] Write final metadata JSON beside the MP4.
- [ ] Add optional background music support at low volume.
- [ ] Add intro/outro assembly hooks.
- [ ] Decide which artifacts belong in Git, release assets, cloud storage, or
  local cache only.
- [ ] Document media retention policy.

### Acceptance Criteria

- Final output folder includes MP4, captions, metadata, and QA report.
- Optional music can be disabled.
- Storage policy is documented and reflected in `.gitignore`.
- Phase 14 handoff no longer depends on untracked generated files.

### Dependencies

- Issue 8.
- Issue 9.
- Issue 14.

### Suggested Files/Modules

- `ai_sankalp/assembly.py`
- `ai_sankalp/renderer.py`
- `.gitignore`
- `README.md`
- `docs/storage-policy.md`

### Test/Verification Plan

- Assemble one final package.
- Confirm all expected sidecars exist.
- Confirm `.gitignore` matches policy.

### Priority

P2

### Estimated Effort

3 to 5 days

## Issue 18: P2 - Add Review-Friendly UI

### Title

P2: Build Streamlit or web UI for package review and render control

### Goal

Let non-technical users create, review, render, and QA videos without touching
internal files.

### Background

Tkinter is useful for the MVP, but the full workflow needs package preview,
QA visibility, human sign-off, and final output browsing.

### Tasks

- [ ] Choose Streamlit MVP or FastAPI-backed UI.
- [ ] Add topic/script input form.
- [ ] Add package preview tabs for brief, storyboard, narration, code, assets,
  captions, and QA.
- [ ] Add review status and SME approval controls.
- [ ] Add compile/render/QA controls.
- [ ] Add history and final artifact browser.

### Acceptance Criteria

- A reviewer can inspect package content before rendering.
- A reviewer can mark SME approval.
- Render and QA status are visible.
- Errors do not discard user input.

### Dependencies

- Issue 9.
- Issue 11.
- Issue 12.

### Suggested Files/Modules

- `streamlit_app.py`
- `ai_sankalp/pipeline.py`
- `requirements.txt`
- `README.md`
- `docs/ui.md`

### Test/Verification Plan

- Manual UI smoke test.
- Service-level tests for UI actions.
- Verify final artifacts open from UI.

### Priority

P2

### Estimated Effort

3 to 5 days

## Issue 19: P2 - Add Batch Generation With Cost and Time Controls

### Title

P2: Add batch video generation with failure isolation and budget reporting

### Goal

Generate many videos while tracking time, cost, failures, and review status.

### Background

A 50-topic batch has meaningful render time, AI cost, TTS cost, and review
cost. Batch generation should not be planned until the reusable compiler and AI
architecture are stable.

### Tasks

- [ ] Define batch input format.
- [ ] Add dry-run estimate for render time and AI/TTS cost.
- [ ] Add sequential batch execution.
- [ ] Isolate failures by job.
- [ ] Support resume behavior.
- [ ] Add summary report.
- [ ] Add optional concurrency only after sequential mode is stable.

### Acceptance Criteria

- Batch of at least three packages runs sequentially.
- One failure does not stop the whole batch unless fail-fast is enabled.
- Summary report includes success, failure, skipped, time, and estimated cost.
- Human review status is preserved per video.

### Dependencies

- Issue 10.
- Issue 11.
- Issue 13.

### Suggested Files/Modules

- `ai_sankalp/batch.py`
- `ai_sankalp/pipeline.py`
- `configs/batches/`
- `generated/batches/`
- `tests/test_batch.py`

### Test/Verification Plan

- Batch fixture with two valid jobs and one invalid job.
- Resume interrupted batch.
- Verify cost/time report.

### Priority

P2

### Estimated Effort

2 to 4 days

## Issue 20: P1 - Documentation and Handoff

### Title

P1: Document setup, authoring, review, rendering, and extension workflows

### Goal

Make the project usable by developers, content reviewers, and junior team
members.

### Background

The README explains the current MVP. The revised product needs docs for rich
packages, templates, captions, QA, SME review, AI decisions, troubleshooting,
and future extensions.

### Tasks

- [ ] Update README with current architecture and commands.
- [ ] Add setup docs for Python, Manim, FFmpeg, TTS, and fonts.
- [ ] Add authoring docs for rich packages.
- [ ] Add review checklist docs for content and SME sign-off.
- [ ] Add template extension docs.
- [ ] Add troubleshooting docs for dependencies, render failures, voiceover,
  captions, missing assets, and cache.
- [ ] Add future extension notes for better voices, image generation, LMS
  upload, and cloud rendering.

### Acceptance Criteria

- A fresh developer can set up and render samples from docs.
- A content reviewer can understand package review and SME approval.
- A junior contributor can add a new topic or primitive with guidance.
- Troubleshooting covers the known blockers from `REVIEW.md`.

### Dependencies

- Issue 1.
- Issue 3.
- Issue 8.
- Issue 9.
- Issue 10.

### Suggested Files/Modules

- `README.md`
- `docs/setup.md`
- `docs/authoring.md`
- `docs/templates.md`
- `docs/review-checklist.md`
- `docs/troubleshooting.md`

### Test/Verification Plan

- Follow setup docs from a clean environment.
- Render Python and C++ samples.
- Complete QA and review checklist.

### Priority

P1

### Estimated Effort

2 to 4 days

