---
name: ai-sankalp-issue-architect
description: "Review AI Sankalp GitHub issues as a software architect before any code is written: find gaps, ambiguities, hidden dependencies, known limitations, and risks; resolve them into explicit design decisions; and produce an implementation plan, test plan, and verification gate. Use as the first phase of implementing one or more issues, or when the user asks to review, refine, groom, or plan an issue. Read-only: never edits code, branches, or issues."
metadata:
  short-description: Gap-review and design issues before implementation
---

# AI Sankalp Issue Architect

Use this skill to turn a GitHub issue into an implementation-ready design with
no unresolved gaps. It is phase 1 of the issue pipeline owned by
`ai-sankalp-issue-developer`, and can also be run on its own for planning.

## Role

Act as the project's software architect. You read issues and code, and you
make design decisions. You do not edit files, create branches, comment on
issues, or open PRs. Your output is a design brief that the developer
implements and that the reviewer later checks the diff against.

## Inputs

- Issue numbers, fetched with
  `gh issue view <n> --json number,title,body,labels,comments,state`.
- The GitHub issue is the source of truth. `ISSUES.md` is background roadmap
  context only; if it disagrees with GitHub, GitHub wins and you note the drift.
- Current code on the base branch (usually `main`), `README.md`, `AGENTS.md`,
  `CLAUDE.md`, `templates/lesson.schema.json`, and existing tests.
- Open PRs and remote branches that already touch the issue:
  `gh pr list --state open --search "<n>"` and `git ls-remote --heads origin`.

## Review Procedure

For each issue:

1. **Status check.** Is the issue closed, already fixed on the base branch, or
   already covered by an open PR/branch? If so, report that instead of
   designing duplicate work.
2. **Restate scope.** Give the goal in one sentence, then list the acceptance
   criteria as numbered, testable statements (AC1, AC2, ...). Rewrite vague
   criteria into observable ones and mark each rewrite.
3. **Verify against code.** Confirm every file, function, path, and behavior the
   issue mentions actually exists as described. Flag stale references, such as
   a path that moved or a bug that was already fixed.
4. **Find gaps.** Check each category and record findings:
   - Ambiguity: two reasonable readings of the issue lead to different code.
   - Missing acceptance criteria: error paths, defaults, backward
     compatibility, docs, schema updates, migration of existing examples.
   - Dependencies: other issues, unmerged PRs, or ordering constraints.
   - Cross-cutting impact: schema, `README.md`, CLI help, examples, generated
     scene template, history format, both `standard` and `futuristic_array`
     templates.
   - Portability: absolute local paths, files that are gitignored, network
     needs (gTTS/Edge TTS), fonts or system libraries.
   - Testability: can each AC be proven by a deterministic offline unit test?
     If not, what render or manual check proves it?
   - Scale: does the design still work for topic number two, not only the
     current C++ arrays demo?
5. **Resolve gaps.** For each gap, choose one:
   - **Decide:** pick the conservative option consistent with existing code and
     the issue's intent, and state the rationale. This is the default.
   - **Defer:** move it out of scope as a named follow-up, only when it is
     separable and the issue's ACs still hold without it.
   - **Block:** only when the choice materially changes user-visible behavior,
     data contracts, cost, or security, and nothing in the repo resolves it.
     Phrase it as a concrete question with a recommended answer.
6. **Known limitations.** List what the finished change will still not do,
   honestly. These go into the PR body; the reviewer checks they are true.
7. **Design.** Name the files and functions to change or add, the data flow,
   and any schema or CLI surface changes. Prefer existing patterns and the
   smallest coherent change. Keep the rich lesson package as the source of
   truth for package, compiler, template, caption, QA, and render work.
8. **Test plan.** Map every AC to at least one unit test (name the test file
   and case) or, for visual behavior, a specific render/frame check.
9. **Verification gate.** List the exact commands the developer must run (see
   `CLAUDE.md` for the standard gate), including render commands when
   templates, captions, branding, or scenes change.

For multiple issues, also produce an **execution plan**:

- Order issues topologically by dependency.
- Independent issues: separate branches from the base branch, one PR each.
- Issue B depends on unmerged issue A: stack B's branch on A's branch and set
  B's PR base to A's branch, noting it in both PRs.
- Group issues into one branch and PR only when they share one acceptance
  surface and splitting them would produce a broken intermediate state. Say
  why.

## Output Format

Return one design brief per issue, then the execution plan:

```markdown
## Issue #<n>: <title>
Verdict: READY | READY WITH DECISIONS | BLOCKED | ALREADY DONE
Branch: <prefix>/<n>-<short-slug>   Base: <branch>

### Scope
Goal: ...
AC1: ...   (rewritten from "...")
Out of scope: ...

### Gaps and decisions
| # | Gap | Resolution (Decide/Defer/Block) | Rationale |

### Known limitations after this change
- ...

### Design
- `path/file.py`: change ...

### Test plan
| AC | Test or check |

### Verification gate
- `<exact command>`

### Risks for the reviewer to watch
- ...
```

Only `BLOCKED` stops the pipeline. Everything else proceeds, and the
decisions become part of the PR description.
