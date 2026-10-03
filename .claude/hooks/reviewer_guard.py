#!/usr/bin/env python3
"""PreToolUse hook used by the `reviewer` subagent (declared in its frontmatter).

The reviewer needs Bash to run tests and read the diff, but must never change the repository or GitHub.
`disallowedTools: Bash(...)` cannot express that: the docs say it removes the whole Bash tool. So this hook
allows read-only commands and blocks anything that writes. It is a guardrail against mistakes, not a
security boundary; the real boundary is that a human merges.

Protocol: JSON on stdin; exit code 2 blocks the call and shows stderr to Claude.
"""
from __future__ import annotations

import json
import re
import sys

BLOCKED = [
    (r"\bgit\b[^|;&]*\b(add|commit|push|merge|rebase|reset|restore|stash|cherry-pick|revert|tag|clean|rm|mv|apply|am|pull)\b",
     "the reviewer must not change the repository"),
    (r"\bgit\b[^|;&]*\b(checkout|switch)\b[^|;&]*(-b|-B|-c|-C)\b", "the reviewer must not create branches"),
    (r"\bgit\b[^|;&]*\bcheckout\b[^|;&]*\s--(\s|$)", "checkout of paths would discard changes"),
    (r"\bgh\s+pr\s+(merge|close|reopen|edit|ready|create)\b", "the reviewer posts reviews only; it does not change PR state"),
    (r"\bgh\s+(release|repo|secret|workflow)\b", "repository settings are human-only"),
    (r"\bgh\s+api\b.*(-X|--method)\s+(POST|PUT|PATCH|DELETE)\b", "the reviewer may only read from the GitHub API"),
    (r"(^|[^<>&0-9])>>?\s*[^&\s]", "writing files through redirection is not allowed"),
    (r"\b(sed|perl)\b[^|;&]*\s-i\b", "in-place edits are not allowed"),
    (r"\b(rm|mv|cp|touch|mkdir|chmod|tee)\b", "the reviewer must not modify files"),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    for pattern, reason in BLOCKED:
        if re.search(pattern, command):
            print(f"Blocked by reviewer_guard.py: {reason}. Command: {command[:200]}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
