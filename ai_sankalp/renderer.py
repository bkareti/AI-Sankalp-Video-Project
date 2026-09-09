from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .generator import GeneratedLesson
from .history import HistoryLog
from .models import LessonConfig


class DependencyError(RuntimeError):
    pass


class RenderError(RuntimeError):
    pass


@dataclass
class RenderResult:
    video_path: Path
    command: List[str]
    output: str


def _python_with_manim(project_root: Path) -> Path:
    if importlib.util.find_spec("manim") is not None:
        return Path(sys.executable)
    local_python = project_root / ".venv" / "bin" / "python"
    if local_python.exists():
        check = subprocess.run(
            [str(local_python), "-c", "import manim, manim_voiceover, gtts, edge_tts"],
            capture_output=True,
            text=True,
        )
        if check.returncode == 0:
            return local_python
    raise DependencyError(
        "Manim dependencies are missing. Activate .venv and run: python -m pip install -r requirements.txt"
    )


def dependency_status(project_root: Path) -> Dict[str, str]:
    status: Dict[str, str] = {}
    try:
        python = _python_with_manim(project_root)
        status["python"] = str(python)
        check = subprocess.run(
            [str(python), "-c", "import manim, manim_voiceover, gtts, edge_tts; print(manim.__version__)"],
            capture_output=True,
            text=True,
        )
        status["python_packages"] = "ok" if check.returncode == 0 else check.stderr.strip() or "missing"
        status["manim_version"] = check.stdout.strip() if check.returncode == 0 else "unknown"
        yaml_check = subprocess.run(
            [str(python), "-c", "import yaml"], capture_output=True, text=True,
        )
        status["yaml_support"] = "ok" if yaml_check.returncode == 0 else "missing (optional; JSON still works)"
    except DependencyError as exc:
        status["python_packages"] = str(exc)
    status["ffmpeg"] = shutil.which("ffmpeg") or "missing"
    return status


class ManimRenderer:
    QUALITY = {"low": "l", "medium": "m", "high": "h", "production": "p", "4k": "k"}

    def __init__(self, project_root: Path):
        self.root = Path(project_root).resolve()
        self.generated = self.root / "generated"
        self.history = HistoryLog(self.generated / "history.jsonl")

    def render(
        self,
        generated: GeneratedLesson,
        lesson: LessonConfig,
        output_dir: Path | None = None,
        quality: str = "low",
    ) -> RenderResult:
        if quality not in self.QUALITY:
            raise ValueError(f"quality must be one of: {', '.join(self.QUALITY)}")
        python = _python_with_manim(self.root)
        if shutil.which("ffmpeg") is None:
            raise DependencyError("ffmpeg is missing. On macOS, install it with: brew install ffmpeg")

        job_id = uuid.uuid4().hex[:10]
        media_dir = self.generated / ".render_cache" / job_id
        output_dir = Path(output_dir or self.generated / "videos").expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_filename = f"{lesson.slug}.mp4"
        command = [
            str(python), "-m", "manim",
            f"-q{self.QUALITY[quality]}",
            "--format", "mp4",
            "--progress_bar", "none",
            "--media_dir", str(media_dir),
            "--output_file", output_filename,
            str(generated.scene_path),
            generated.scene_class,
        ]
        self.history.add(
            "render_started", topic=lesson.topic, scene=str(generated.scene_path),
            quality=quality, voiceover=lesson.voiceover.enabled,
        )
        process = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        combined = "\n".join(part for part in (process.stdout, process.stderr) if part).strip()
        if process.returncode != 0:
            hint = ""
            lowered = combined.lower()
            if lesson.voiceover.enabled and any(word in lowered for word in ("gtts", "edge_tts", "network", "connect", "http")):
                hint = " Voice generation failed; check internet access or disable voiceover."
            self.history.add("render_failed", topic=lesson.topic, error=combined[-3000:])
            raise RenderError(f"Manim render failed.{hint}\n\n{combined[-5000:]}")

        candidates = list(media_dir.rglob(output_filename))
        if not candidates:
            self.history.add("render_failed", topic=lesson.topic, error="MP4 not found after successful command")
            raise RenderError(f"Manim completed but did not create {output_filename}")
        source = max(candidates, key=lambda item: item.stat().st_mtime)
        final_path = output_dir / output_filename
        shutil.copy2(source, final_path)
        self.history.add(
            "render_succeeded", topic=lesson.topic, video=str(final_path), quality=quality,
            voiceover=lesson.voiceover.enabled,
        )
        return RenderResult(video_path=final_path, command=command, output=combined)
