---
name: implement-user-story
description: Step-by-step protocol for implementing one GitHub issue (user story or bug) in the AI Sankalp video project, from restating requirements to an evidence-backed pull request. Use whenever asked to implement, fix or build an issue, story or backlog item.
---

# Implement a user story

Follow the steps in order. Do not skip a step because the story looks small; use the "trivial" path in
step 2 instead. The repository rules are in `AGENTS.md`.

## Inputs

An issue number or the full issue text. Read it with `gh issue view <n> --comments`. If you cannot get the
original text, stop and ask. Never work from a paraphrase.

## Step 1. Restate and question

Write, in the conversation:

1. The goal in one or two sentences, in your own words.
2. The acceptance criteria, numbered `AC1`, `AC2`, ... Copy them from the issue. If the issue has none,
   propose some and mark them "proposed, needs approval".
3. Out of scope: what you will not do.
4. Ambiguities and missing information: unclear requirements, missing assets or fonts, unspecified audience
   or style, undefined thresholds, behaviour for failure cases.
5. Assumptions you would make if nobody answers, each one flagged.

If any ambiguity changes what you would build, **stop and ask** the human. Ask only the essential questions,
at most five, and say what you will assume if there is no answer. Do not start coding while a blocking
question is open.

## Step 2. Plan and get approval

A story is **non-trivial** if it touches more than two files, the lesson schema, a template, the renderer,
the QA gates, CI or `.claude/`, or if it adds a dependency. Everything else is trivial (a typo, a docs fix,
a one-function bug fix with an obvious test).

- **Non-trivial**: produce a plan and **wait for explicit approval**. The `architect` agent can draft it;
  you can also write it directly. The plan lists: approach and why, files to change, new files, tests to add,
  how each AC will be verified, the render evidence you will produce, risks, and a rollback.
- **Trivial**: state in one line why it is trivial and continue.

Approval means a clear yes from the human in this conversation or on the issue. Silence is not approval.

## Step 3. Implement

- Branch from an up-to-date `main`: `git switch -c issue/<n>-<short-slug>`. Never commit to `main`.
- Make the smallest coherent change that meets the ACs. If you discover needed work outside the plan,
  stop and tell the human, or open a follow-up issue. Do not widen scope silently.
- Follow `AGENTS.md`: type hints, `ruff` clean, no absolute paths, no secrets, deterministic offline tests,
  no generated media in git.
- Write the test first when practical. Each AC gets at least one test or one named manual check.
- Commit in small steps with Conventional Commit messages (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
  Push the branch regularly so work is not lost if the session ends.
- Never edit or delete an existing test to make it pass. If a test is wrong, explain why and ask.

## Step 4. Verify with commands

Run these from the repository root and record each command and its result. If a command cannot run in this
environment, say so; do not skip it silently.

```bash
.venv/bin/ruff check .
.venv/bin/python -m compileall -q ai_sankalp scenes app.py scripts
.venv/bin/python app.py check
.venv/bin/python -m unittest discover -s tests -v
```

If the change can affect pixels, timing, audio or the lesson schema, also follow the `render-and-verify`
skill: render offline, run `scripts/qa/check_video.py`, and look at the sampled frames yourself.

A gate that failed before your change still counts. Show the command, the failure and proof that it failed on
`main` too. Do not hide it and do not "fix" it in the same PR unless the issue says so.

## Step 5. Self-review, line by line

Run `git diff origin/main...HEAD` and read every line as if someone else wrote it. Check:

- Each AC maps to code and to a test or check. Fill the traceability table now.
- No debug code, TODOs without an issue, commented-out code, unrelated reformatting, or changed files
  you did not mean to change (`git status`, `git diff --stat`).
- Failure paths: missing file, empty input, offline, bad config.
- Cross-platform: paths, line endings, shell assumptions.
- Secrets and local paths: `git diff origin/main...HEAD | grep -nE "(sk-|ghp_|api[_-]?key|/Users/|C:\\\\)"`.
- Docs, README and `AGENTS.md` updated if behaviour or commands changed.
- You did not weaken a gate, threshold or test.

Fix what you find, re-run step 4, and note what the self-review caught.

## Step 6. Open the pull request

Push the branch and open a PR using `.github/pull_request_template.md`. Do not leave any section empty.
Fill in:

- **Summary**: what and why, two to four sentences. Link the issue with `Closes #<n>`.
- **Traceability table**: one row per AC, with status (met, partly met, not met), evidence (file and line,
  test name, command output), and who must verify it (automated, author, human).
- **Evidence**: the exact commands run and their results, paths or attached copies of the QA report and
  contact sheet, and the frames you looked at. Generated videos go in CI artifacts, not in git.
- **Limitations**: what you did not test, what is assumed, known gaps, follow-up issues opened.
- **Human checkpoints needed**: subject-expert review, voice or visual taste review, whichever applies.

Create it as a draft if any AC is not met: `gh pr create --draft --body-file <file>`.

## Step 7. Independent review before merge

Ask the human to start the `reviewer` in a **new Claude Code session** on the PR branch
(`claude --agent reviewer`, ideally in a separate git worktree) with only the issue number and PR number. It must
re-check the PR against the original issue and report a verdict. Address its blocking findings, push, and
ask for a re-review. The human decides whether to merge.

## Never

Merge, tag, publish a release, delete branches, force-push, change repository or branch-protection settings,
commit secrets or media, or claim render quality you did not look at. Those are the human's actions.

## Final message

End with: the PR URL, the traceability table, the commands you ran with pass/fail, what you did **not**
verify, and the questions or checkpoints waiting on the human.
