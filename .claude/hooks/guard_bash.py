#!/usr/bin/env python3
"""PreToolUse hook for Bash: block commands that change shared state in ways agents must not.

Permission deny rules in .claude/settings.json already cover the common spellings, but they match the
command text Claude writes and are not a security boundary (for example `git -C . push` is a different
form). This hook is a second, broader net. The real boundary is GitHub branch protection on `main`.

Protocol: reads the hook JSON on stdin. Exit code 2 blocks the tool call and shows stderr to Claude.
"""
from __future__ import annotations

import json
import re
import sys

# (pattern, reason). Patterns run against the whole command string, case-sensitive.
RULES: list[tuple[str, str]] = [
    (r"\bgit\b[^|;&]*\bpush\b[^|;&]*(--force|--force-with-lease|\s-f(\s|$))", "force-push is not allowed"),
    (r"\bgit\b[^|;&]*\bpush\b[^|;&]*(\s|:)main(\s|$)", "pushing to main is not allowed; open a PR"),
    (r"\bgit\b[^|;&]*\bpush\b[^|;&]*--delete", "deleting remote branches is not allowed"),
    (r"\bgit\b[^|;&]*\bpush\b[^|;&]*\s:[A-Za-z0-9_./-]+(\s|$)", "deleting remote branches is not allowed"),
    (r"\bgit\b[^|;&]*\breset\b[^|;&]*--hard", "git reset --hard can destroy work"),
    (r"\bgit\b[^|;&]*\bclean\b", "git clean can destroy untracked work"),
    (r"\bgit\b[^|;&]*\btag\b", "tagging is a release action; ask the human"),
    (r"\bgh\s+pr\s+merge\b", "agents never merge pull requests"),
    (r"\bgh\s+(release|repo|secret|workflow\s+run)\b", "repository settings, releases and secrets are human-only"),
    (r"\bgh\s+api\b.*(/merge\b|--method\s+DELETE|-X\s+DELETE|--method\s+PUT|-X\s+PUT)", "this GitHub API call can merge or delete"),
    (r"\bgh\s+api\b.*/(branches/[^\s/]+/protection|rulesets|actions/secrets|actions/variables|hooks|collaborators|keys|environments)\b",
     "repository protection, secrets, webhooks and access are human-only settings"),
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r", "recursive forced delete is not allowed"),
    (r"\bgit\b[^|;&]*\badd\b[^|;&]*(\.venv|\bmedia/|generated/videos|generated/audio|\.render_cache|\.env\b)", "do not stage venv, media, caches or .env files"),
    (r"\bgit\b[^|;&]*\badd\b[^|;&]*\.(mp4|mov|wav|mp3|webm)\b", "do not stage rendered media"),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # Never block on a malformed hook payload.
    command = (payload.get("tool_input") or {}).get("command") or ""
    for pattern, reason in RULES:
        if re.search(pattern, command):
            print(f"Blocked by guard_bash.py: {reason}. Command: {command[:200]}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
