#!/usr/bin/env bash
set -euo pipefail

SCENE_FILE="${1:-scenes/c_array_beginners.py}"
SCENE_CLASS="${2:-CArrayBeginners}"

.venv/bin/manim -pql "$SCENE_FILE" "$SCENE_CLASS"
