"""Measure media with ffprobe (optional; callers treat None as unknown)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional


def probe_duration(path: Path) -> Optional[float]:
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None or not Path(path).exists():
        return None
    process = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(process.stdout.strip())
    except ValueError:
        return None
