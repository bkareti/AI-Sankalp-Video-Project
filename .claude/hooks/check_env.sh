#!/bin/bash
# SessionStart hook: report what is missing from the local toolchain. It never installs or changes anything.
# stdout from a SessionStart hook is added to Claude's context, so a missing tool is known before work starts.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

missing=()
[ -x .venv/bin/python ] || missing+=("virtualenv .venv (run: bash scripts/dev/setup_mac.sh)")
for tool in ffmpeg ffprobe git; do
  command -v "$tool" >/dev/null 2>&1 || missing+=("$tool (macOS: brew install ffmpeg)")
done
if [ -x .venv/bin/python ]; then
  .venv/bin/python -c "import manim" >/dev/null 2>&1 || missing+=("manim in .venv (run: bash scripts/dev/setup_mac.sh)")
  [ -x .venv/bin/ruff ] || missing+=("ruff in .venv (run: bash scripts/dev/setup_mac.sh)")
fi
command -v gh >/dev/null 2>&1 || missing+=("gh CLI (optional; needed to read issues and open PRs: brew install gh)")

if [ ${#missing[@]} -eq 0 ]; then
  echo "env check: toolchain OK (use .venv/bin/python)"
else
  echo "env check: missing or not ready:"
  printf ' - %s\n' "${missing[@]}"
  echo "Do not claim tests or renders ran if the tool for them is missing."
fi
exit 0
