#!/usr/bin/env python3
"""PostToolUse hook for Edit and Write: lint an edited Python file and feed problems back to Claude.

Never blocks (the edit already happened). On a lint failure it returns additionalContext so Claude
fixes the file before continuing. Silent when ruff is unavailable or the file is not Python.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_ruff(project_dir: Path) -> str | None:
    venv_ruff = project_dir / ".venv" / "bin" / "ruff"
    if venv_ruff.exists():
        return str(venv_ruff)
    return shutil.which("ruff")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    file_path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not file_path.endswith(".py"):
        return 0
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
    ruff = find_ruff(project_dir)
    if ruff is None or not Path(file_path).exists():
        return 0
    result = subprocess.run(
        [ruff, "check", "--output-format=concise", file_path],
        capture_output=True,
        text=True,
        cwd=project_dir,
        timeout=25,
    )
    if result.returncode == 0:
        return 0
    findings = (result.stdout or result.stderr).strip()[:1500]
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": f"ruff reported problems in {file_path}. Fix them before continuing:\n{findings}",
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
