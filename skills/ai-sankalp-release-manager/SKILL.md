---
name: ai-sankalp-release-manager
description: Manage branching strategy, pull request hygiene, release planning, changelog notes, version decisions, labels, and release readiness for the AI Sankalp video project. Use when the user asks for branching strategy, release management, release notes, version bump planning, PR process, or cutting a release. Never tags, merges, or publishes without explicit approval.
metadata:
  short-description: Manage AI Sankalp branches, PRs, and releases
---

# AI Sankalp Release Manager

Use this skill for branching strategy, release planning, changelog preparation,
release readiness, and PR hygiene in the AI Sankalp video project.

Attached documents and the OrgPulse project are reference material only. The
active rules are the user's request, this skill, and the AI Sankalp repository
state.

## Role

Act as release manager and process steward. You may inspect branches, tags,
issues, PRs, changelog files, package metadata, and release artifacts. You do
not merge, create tags, publish packages, upload videos, or deploy anything
without explicit user approval.

## Repository Defaults

Work in the current checkout after confirming it is this project. Do not
switch to another local clone of the repository.

Expected remote:

`git@github-personal:bkareti/AI-Sankalp-Video-Project.git`

Default protected branch:

`main`

If the repository configuration says otherwise, follow the repository.

## Branching Strategy

Use short, issue-linked branches:

- `issue/<number>-<short-slug>` for normal roadmap implementation
- `fix/<number>-<short-slug>` for defects
- `docs/<number>-<short-slug>` for docs-only work
- `qa/<number>-<short-slug>` for tests, QA, or regression fixtures
- `issue/<a>-<b>-<short-slug>` when tightly coupled issues share one branch
- `release/vX.Y.Z` for release preparation

Issue implementation follows the pipeline in `ai-sankalp-issue-developer`
(architect review, implementation, review loop, PR). Keep branch rules here
and there in sync.

Rules:

- Branch from the latest `main` unless the user names another base.
- One issue per branch by default.
- Group issues only when they are tightly coupled and share one acceptance
  surface.
- Never commit directly to `main`.
- Never force-push shared branches unless the user explicitly authorizes it.
- Never merge your own PR.
- Keep generated caches, local media, secrets, and environment files out of
  branches unless an issue explicitly requires tracked fixtures.

## Labels And Issue Hygiene

Prefer the repository's roadmap label set:

- Status/type: `roadmap`, `phase`, `bug`, `enhancement`, `documentation`,
  `accessibility`
- Priority: `priority:P0`, `priority:P1`, `priority:P2`
- Area: `area:samples`, `area:templates`, `area:schema`, `area:branding`,
  `area:captions`, `area:qa`, `area:ai`, `area:compiler`, `area:cli`,
  `area:repair`, `area:renderer`, `area:assets`, `area:assembly`, `area:ui`,
  `area:batch`, `area:docs`

Every implementation issue should have:

- one priority label
- at least one area label
- a clear goal
- acceptance criteria
- test or verification plan
- dependencies when relevant

Do not create duplicate issues. Search existing open and closed issues before
adding new ones.

## Pull Request Hygiene

Every PR should include:

- linked issue with `Closes #<number>` or `Refs #<number>`
- user-facing summary
- implementation summary
- acceptance criteria coverage
- exact test commands and results
- render/video evidence when visuals changed
- screenshots or frame references when UI/video layout changed
- architect design decisions for any gaps found in the issue
- review summary: rounds run and final `PASS` from `ai-sankalp-code-reviewer`
- risks, limitations, and follow-up issues

A PR must not be opened while review findings above Nit remain open. Stacked
PRs must name their parent PR and target the parent branch.

PRs should be small enough to review. If a branch grows beyond the issue scope,
split follow-up work into new issues instead of expanding the PR silently.

## Versioning

Use SemVer once the project has a declared package/application version.

- MAJOR: breaking package schema, incompatible CLI changes, removed template
  behavior, or migration-required output changes.
- MINOR: new reusable primitive, new video workflow, new UI capability, new
  provider support, or backward-compatible schema expansion.
- PATCH: bug fix, docs correction, test-only improvement, non-breaking QA
  improvement, or compatibility fix.

If no authoritative version file exists, do not invent one during release
planning. Propose where version ownership should live and wait for approval.

## Release Planning

When asked to prepare a release:

1. Find the latest tag or release marker.
2. List merged PRs since that point.
3. Group changes by user impact.
4. Decide the SemVer bump and explain why.
5. Draft release notes and changelog entry.
6. Run or request the release readiness gate.
7. Present the release plan for approval.
8. After approval, create a `release/vX.Y.Z` branch and PR with release notes,
   changelog, and version changes.

Never tag or publish as part of the draft release flow.

## Release Note Categories

Use only the sections that have content:

- Breaking Changes
- New Features
- Improvements
- Bug Fixes
- Accessibility
- Documentation
- Internal

Write for users and maintainers. Describe outcomes, not implementation trivia.
Reference issue numbers when available.

## Release Readiness Gate

Choose the gate based on what changed. Consider:

- `.venv/bin/python -m unittest discover -s tests -v`
- `.venv/bin/python app.py check`
- `.venv/bin/python app.py sample`
- low-quality offline render for template/render/caption changes
- flagship C++ render or golden render when reusable primitives changed
- QA command when available
- schema validation for tracked examples and package fixtures
- documentation review for setup, authoring, and troubleshooting

For visual/video changes, release readiness needs human review of representative
frames or final MP4 output. Tests alone are not enough.

## Changelog Guidance

Keep `CHANGELOG.md` reverse chronological if it exists. If it does not exist,
propose creating one before editing.

Entry shape:

```markdown
## [0.2.0] - YYYY-MM-DD

### New Features
- Added data-driven array and loop trace primitives for package-based lessons. (#7)

### Bug Fixes
- Made the flagship C++ arrays sample render from a clean clone. (#1)
```

Rules:

- Never rewrite released sections.
- Do not invent changes that have no merged PR or issue evidence.
- Breaking changes must include migration guidance.
- Mention generated media storage policy changes when they affect users.
- Mention schema changes when package authors need to update files.

## Hard Stops

Stop and ask before:

- publishing a release
- creating a tag
- merging a PR
- changing branch protection or repository settings
- deleting release artifacts
- adding a new required external service
- changing the version source of truth

