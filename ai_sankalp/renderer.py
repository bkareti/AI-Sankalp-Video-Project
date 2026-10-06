from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .caption_burn import CaptionBurnError, burn_captions as burn_caption_video
from .captions import (
    SOURCE_ESTIMATED, SOURCE_RENDER, CaptionFiles, Cue, estimate_cues_from_lesson, estimate_cues_from_package,
    export_captions, find_render_srt, parse_srt,
)
from .generator import GeneratedLesson, check_scene_syntax
from .history import HistoryLog
from .models import LessonConfig
from .package import display_path, load_package


class DependencyError(RuntimeError):
    pass


class RenderError(RuntimeError):
    pass


@dataclass
class RenderResult:
    video_path: Path
    command: List[str]
    output: str
    captions: Optional[CaptionFiles] = None
    captioned_video_path: Optional[Path] = None


def narration_cues(lesson: LessonConfig, package_path: Optional[Path]) -> List[Cue]:
    """Estimated cues from what the template narrates (package scenes or standard script)."""
    if package_path is not None and lesson.visual_template != "standard":
        return estimate_cues_from_package(load_package(package_path))
    return estimate_cues_from_lesson(lesson)


def collect_captions(media_dir: Path, lesson: LessonConfig, package_path: Optional[Path], output_dir: Path) -> CaptionFiles:
    """Copy the render's SRT (or estimate one) next to the MP4 as SRT and VTT."""
    cues: List[Cue] = []
    source = SOURCE_ESTIMATED
    rendered = find_render_srt(media_dir, lesson.slug)
    if rendered is not None:
        try:
            cues = parse_srt(rendered.read_text(encoding="utf-8"))
            source = SOURCE_RENDER
        except ValueError:
            cues = []
    if not cues:
        cues, source = narration_cues(lesson, package_path), SOURCE_ESTIMATED
    return export_captions(cues, output_dir, lesson.slug, source)


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

    def _check_scene(self, scene_path: Path) -> None:
        """Refuse to start Manim on a scene that is missing or does not compile."""
        name = display_path(scene_path, self.root)
        try:
            source = Path(scene_path).read_bytes()
        except OSError as exc:
            raise RenderError(f"scene file cannot be read: {name} ({exc}). Run generate first.") from exc
        check_scene_syntax(source, name)

    def render(
        self,
        generated: GeneratedLesson,
        lesson: LessonConfig,
        output_dir: Path | None = None,
        quality: str = "low",
        burn_captions: bool = False,
    ) -> RenderResult:
        if quality not in self.QUALITY:
            raise ValueError(f"quality must be one of: {', '.join(self.QUALITY)}")
        self._check_scene(generated.scene_path)
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
        captions = collect_captions(media_dir, lesson, generated.package_path, output_dir)
        # Record the render before the optional burn-in: the MP4 and captions are
        # already in place, so history must describe them even if burning fails.
        self.history.add(
            "render_succeeded", topic=lesson.topic, video=str(final_path), quality=quality,
            voiceover=lesson.voiceover.enabled,
            captions=captions.to_dict(lambda path: display_path(path, self.root)),
        )
        captioned_path = None
        if burn_captions:
            captioned_path = output_dir / f"{lesson.slug}_captioned.mp4"
            try:
                burn_caption_video(final_path, parse_srt(captions.srt.read_text(encoding="utf-8")), captioned_path, quality)
            except CaptionBurnError as exc:
                self.history.add("caption_burn_failed", topic=lesson.topic, video=str(final_path), error=str(exc)[-3000:])
                raise RenderError(str(exc)) from exc
            self.history.add(
                "captions_burned", topic=lesson.topic, video=str(final_path),
                captioned_video=display_path(captioned_path, self.root),
            )
        return RenderResult(
            video_path=final_path, command=command, output=combined,
            captions=captions, captioned_video_path=captioned_path,
        )
