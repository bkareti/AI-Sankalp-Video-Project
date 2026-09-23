---
name: ai-sankalp-issue-developer
description: "Implement one or more GitHub issues in the AI Sankalp video project end to end: architect gap review, branch, implement, unit tests, render/QA gate, independent code review with a fix-until-clean loop, commit, push, and open a PR. Use when the user says 'implement issue 3', 'implement issues 2, 4 and 7', 'fix #5', 'work on issue', or 'build issue'. Never merges."
metadata:
  short-description: Implement AI Sankalp issues with architect review, tests, review loop, and PR
---

# AI Sankalp Issue Developer

Use this skill when the user asks to implement one or more GitHub issues in
the AI Sankalp video project. It owns the whole pipeline and calls two
supporting roles:

- **Architect:** `ai-sankalp-issue-architect` (design brief, no gaps)
- **Reviewer:** `ai-sankalp-code-reviewer` (pre-PR review, PASS required)

The user's request and the GitHub issues are the active instructions. Attached
documents, other projects (for example OrgPulse), and `ISSUES.md` are
background context only.

## Pipeline

```
Intake → Architect review → Branch → Implement + tests → Verification gate
      → Review ⟲ Fix (until PASS) → Commit → Push → PR → Report
```

Run the full pipeline for each issue in the architect's execution order. Do
not skip phases. Do not open a PR while any review finding above Nit is open.

Hard stops: never merge PRs, close issues by hand, force-push, tag releases,
publish or upload videos, or push to `main`.

## Phase 0: Intake

- Work in the current checkout. Confirm it is this project: `git remote -v`
  should point at `bkareti/AI-Sankalp-Video-Project` (SSH host alias
  `github-personal`). Do not switch to another clone of the repo.
- Parse every issue number from the request (`1`, `#1`, `1, 3 and 5`,
  `1-3`).
- Run `git status --porcelain`. Uncommitted or untracked work that is not
  yours belongs to the user: leave it untouched and never stage it. If it
  would conflict with a branch switch, stop and ask.
- Run `git fetch origin`. For each issue, look for existing work:
  `gh pr list --state open --json number,url,headRefName,closingIssuesReferences`
  (match on a linked issue number or a head branch containing `/<n>-`) and
  `git branch -r --list 'origin/*/<n>-*'`. If a match exists, report it and
  continue on that branch (pushing new commits updates the PR). Never open a
  duplicate PR.

## Phase 1: Architect Review

Run the architect role for all requested issues at once, so cross-issue
dependencies are visible:

- **Claude Code:** delegate to the `ai-sankalp-architect` subagent with the
  issue numbers and the base branch.
- **Codex or no subagents:** follow
  `skills/ai-sankalp-issue-architect/SKILL.md` inline as a separate pass before
  touching code.

Then act on the verdicts:

- `ALREADY DONE`: skip the issue and report why.
- `BLOCKED`: ask the user the architect's concrete question, with its
  recommended answer. Continue with the other issues that are not blocked by
  it.
- `READY` or `READY WITH DECISIONS`: proceed. The design brief is now the
  contract for implementation, review, and the PR body.

## Phase 2: Branch

- Base: the latest `origin/main`, unless the execution plan stacks this issue
  on another issue's branch or the user names a base.
- Naming, lowercase with a 3–5 word kebab-case slug:
  - `issue/<n>-<slug>` for roadmap and feature work
  - `fix/<n>-<slug>` for defects (issues labelled `bug`)
  - `docs/<n>-<slug>` for documentation-only work
  - `qa/<n>-<slug>` for test/QA-only work
  - `issue/<n>-<m>-<slug>` when the architect grouped issues
- `git switch -c <branch> origin/main`, then confirm the branch before the
  first edit.

## Phase 3: Implement And Test

- Implement exactly the design brief. If implementation reveals the brief is
  wrong, update the decision explicitly (and carry it into the PR body)
  instead of silently diverging.
- Make the smallest coherent change that meets every AC. Prefer existing
  patterns and data-driven Manim primitives over one-off hardcoded scenes.
- Protect AI Sankalp branding, safe margins, fonts, caption space, and
  phone-readable text in any video-template work.
- Never hardcode secrets or API keys. Provide offline fixtures for AI/network
  paths.
- Keep generated artifacts (`media/`, `generated/` output, MP4s) out of
  commits unless the issue requires tracked fixtures.

Add or update tests for every behavior change, following the architect's test
plan:

- Bug fix: a regression test that fails without the fix.
- Parser/schema/model: valid input, invalid input, defaults, error messages.
- Compiler/template routing: selected template, unsupported template, missing
  package, deterministic output.
- Renderer/cache/history: mock subprocesses and cover failure paths.
- Caption/QA: missing sidecars, valid sidecars, final-ready blocks, SME
  approval.
- CLI: argument parsing and user-facing failure messages.

Unit tests must be deterministic and offline.

## Phase 4: Verification Gate

Run the architect's gate. At minimum:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python app.py check
.venv/bin/python app.py sample
```

For template, render, brand, caption, QA, or scene changes, also run:

```bash
.venv/bin/python app.py sample --render --no-voiceover --quality low
.venv/bin/python app.py generate --config examples/arrays_in_cpp/config.json --render --quality low
```

When a render changes, extract and inspect representative frames (intro,
explanation, code, summary, outro) for logo placement, text overflow, safe
margins, and caption space. Tests alone do not prove video quality.

If a failure predates your change, confirm it on `origin/main`, record the
command and output, and do not hide it with unrelated fixes.

Commit locally once the gate passes, so the reviewer sees `<base>...HEAD`.
Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`,
`chore:`) with `Refs #<n>` in the body. Stage only files you changed, by
explicit path. Never use `git add -A` or `git add .`.

## Phase 5: Review And Fix Loop

1. Request a review:
   - **Claude Code:** delegate to the `ai-sankalp-reviewer` subagent with the
     base branch, the feature branch, the design brief, and your gate results.
     A fresh-context reviewer is required; do not substitute a self-review.
   - **Codex or no subagents:** follow
     `skills/ai-sankalp-code-reviewer/SKILL.md` as a separate pass: re-read the
     full diff from scratch as if someone else wrote it.
2. On `CHANGES REQUIRED`: fix every Blocker, Major, and Minor finding. Fix
   Nits unless the fix is out of scope, and note any skipped Nit in the PR.
   If you disagree with a finding, prove it with code or a test and record
   the reasoning. Do not just ignore it.
3. Re-run the full verification gate, commit the fixes (`fix: address review
   findings`), and request the next review round, passing the previous
   findings so the reviewer can confirm each one is resolved.
4. Repeat until the verdict is `PASS`.

If the review is still not `PASS` after 3 rounds, or a finding needs a product
decision, stop. Do not push or open the PR. Report the open findings to the
user and ask how to proceed.

## Phase 6: Push And PR

Only after `PASS`:

```bash
git push -u origin <branch>
gh pr create --base <base> --head <branch> --title "<type>: <issue title>" --body-file <tmp>
```

The PR title uses Conventional Commit style. For issues labelled with a
priority, keep the priority prefix out of the title. The body contains:

```markdown
## Summary
<user-facing outcome, then implementation summary>

Closes #<n>            (use `Refs #<n>` when the issue is only partly done)

## Design decisions
<architect gaps and how each was resolved>

## Acceptance criteria
- [x] AC1 … (evidence: test name or render check)

## Verification
- [x] `<exact command>` → <result>

## Review
<number of review rounds; final verdict PASS; any Nits deliberately skipped>

## Known limitations and follow-ups
- …
```

Stacked PRs: set `--base` to the parent issue's branch and state in the body
"Stacked on #<parent PR>; merge that first."

After creating the PR, run `gh pr view <url> --json url,mergeable,statusCheckRollup`.
If CI checks exist, wait for them. If a check fails, fix it and push
(re-reviewing when the fix is non-trivial).

## Phase 7: Report

For each issue, report: the PR URL, the branch, the architect's decisions, the
number of review rounds, the verification commands and results, and the
known limitations. Report skipped, blocked, or already-done issues with
reasons. Stop there; merging is the user's decision.
