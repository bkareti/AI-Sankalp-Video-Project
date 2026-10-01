"""Captions: chunking, timing, SRT/VTT files, and checks (no Manim).

Templates add one subcaption per narrated block through
:func:`emit_subcaptions`, so every render writes an SRT next to its MP4.
When a render has no SRT, :func:`estimate_cues_from_package` or
:func:`estimate_cues_from_lesson` builds cues from the narration text.
"""
from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

LINE_CHARS = 42
MAX_LINES = 2
CUE_GAP = 0.1
MAX_CHARS_PER_SECOND = 30.0
DEFAULT_PACE_WPM = 140
# Approximate per-scene overhead in the flagship (clears and transitions).
SCENE_OVERHEAD_SECONDS = 0.55
SOURCE_RENDER = "render"
SOURCE_ESTIMATED = "estimated"

TIMESTAMP = re.compile(r"(\d+):(\d{2}):(\d{2})[,.](\d{3})")


@dataclass(frozen=True)
class Cue:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class CaptionFiles:
    srt: Path
    vtt: Path
    source: str
    cue_count: int

    def to_dict(self, display=str) -> Dict[str, Any]:
        return {"srt": display(self.srt), "vtt": display(self.vtt), "source": self.source, "cue_count": self.cue_count}


# --- chunking and timing -------------------------------------------------------
def _sentences(text: str) -> List[str]:
    return [piece.strip() for piece in re.findall(r"[^.!?]+(?:[.!?]+|$)", text) if piece.strip()]


def chunk_caption_text(text: str, line_chars: int = LINE_CHARS, max_lines: int = MAX_LINES) -> List[str]:
    """Split narration into cues of at most `max_lines` lines of `line_chars`."""
    chunks: List[str] = []
    # A single token longer than a line (a long URL or identifier) is split
    # across lines, which shows a space inside it; lesson narration rarely has one.
    for sentence in _sentences(" ".join(text.split())):
        # wrap() bounds every line, so a chunk of max_lines lines never needs trimming.
        lines = textwrap.wrap(sentence, line_chars, break_long_words=True)
        for index in range(0, len(lines), max_lines):
            chunks.append(" ".join(lines[index:index + max_lines]))
    return chunks


def format_lines(chunk: str, line_chars: int = LINE_CHARS) -> str:
    return "\n".join(textwrap.wrap(chunk, line_chars, break_long_words=True))


def timed_chunks(text: str, start: float, duration: float, gap: float = CUE_GAP) -> List[Cue]:
    """Spread `text` over [start, start + duration], proportional to length."""
    chunks = chunk_caption_text(text)
    if not chunks or duration <= 0:
        return []
    total = sum(len(chunk) for chunk in chunks)
    cues: List[Cue] = []
    cursor = start
    for chunk in chunks:
        length = duration * len(chunk) / total
        end = cursor + length
        cues.append(Cue(round(cursor, 3), round(max(cursor + 0.05, end - gap), 3), format_lines(chunk)))
        cursor = end
    return cues


def emit_subcaptions(scene, text: str, duration: float, offset: float = 0.0) -> None:
    """Add timed caption chunks to a Manim scene (offset is relative to now)."""
    earliest = -float(scene.time)  # never before the scene starts (srt drops negative starts)
    for cue in timed_chunks(text, offset, duration):
        start = max(cue.start, earliest)
        scene.add_subcaption(cue.text, duration=max(0.05, cue.end - start), offset=start)


# --- estimation from narration ---------------------------------------------------
def _words(text: str) -> int:
    return len(text.split())


def estimate_cues_from_package(package: Dict[str, Any]) -> List[Cue]:
    profile = package.get("voice_profile") or {}
    default_pace = profile.get("target_pace_wpm") or DEFAULT_PACE_WPM
    cues: List[Cue] = []
    cursor = 0.0
    for scene in package.get("scenes") or []:
        delivery = scene.get("voice_delivery") or {}
        pace = delivery.get("pace_wpm") or default_pace
        cursor += float(delivery.get("pause_before_seconds") or 0)
        for sentence in _sentences(str(scene.get("voiceover", ""))):
            seconds = max(0.6, _words(sentence) / pace * 60)
            cues.extend(timed_chunks(sentence, cursor, seconds))
            cursor += seconds
        cursor += float(delivery.get("pause_after_seconds") or 0) + SCENE_OVERHEAD_SECONDS
    return cues


def estimate_cues_from_lesson(lesson, pace_wpm: int = DEFAULT_PACE_WPM) -> List[Cue]:
    from .narration import standard_script

    cues: List[Cue] = []
    cursor = 0.0
    for segment in standard_script(lesson):
        seconds = max(0.8, _words(segment.text) / pace_wpm * 60)
        cues.extend(timed_chunks(segment.text, cursor, seconds))
        cursor += seconds + 0.6
    return cues


# --- SRT / VTT -------------------------------------------------------------------
def _stamp(seconds: float, separator: str) -> str:
    milliseconds = int(round(max(0.0, seconds) * 1000))
    hours, rest = divmod(milliseconds, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def format_srt(cues: Sequence[Cue]) -> str:
    blocks = [
        f"{index}\n{_stamp(cue.start, ',')} --> {_stamp(cue.end, ',')}\n{cue.text}\n"
        for index, cue in enumerate(cues, 1)
    ]
    return "\n".join(blocks)


def format_vtt(cues: Sequence[Cue]) -> str:
    blocks = [f"{_stamp(cue.start, '.')} --> {_stamp(cue.end, '.')}\n{cue.text}\n" for cue in cues]
    return "WEBVTT\n\n" + "\n".join(blocks)


def _seconds(parts) -> float:
    hours, minutes, secs, millis = (int(part) for part in parts)
    return hours * 3600 + minutes * 60 + secs + millis / 1000


def parse_srt(text: str) -> List[Cue]:
    """Parse SRT (or WebVTT) text. Raises ValueError on a malformed timing line."""
    cues: List[Cue] = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip()):
        lines = [line for line in block.split("\n") if line.strip()]
        timing_index = next((index for index, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            if lines and lines[0].strip().upper().startswith("WEBVTT"):
                continue
            raise ValueError(f"caption block without a timing line: {block[:40]!r}")
        stamps = TIMESTAMP.findall(lines[timing_index])
        if len(stamps) != 2:
            raise ValueError(f"malformed timing line: {lines[timing_index]!r}")
        start, end = (_seconds(stamp) for stamp in stamps)
        cues.append(Cue(start, end, "\n".join(lines[timing_index + 1:])))
    return cues


def validate_cues(cues: Sequence[Cue], video_duration: Optional[float] = None) -> List[str]:
    """Readability and timing problems (empty when the captions look right)."""
    problems: List[str] = []
    if not cues:
        return ["no caption cues"]
    previous_end = 0.0
    for index, cue in enumerate(cues, 1):
        length = cue.end - cue.start
        if length <= 0:
            problems.append(f"cue {index} has no duration")
            continue
        if cue.start < previous_end - 0.05:
            problems.append(f"cue {index} overlaps the previous cue")
        rate = len(cue.text.replace("\n", " ")) / length
        if rate > MAX_CHARS_PER_SECOND:
            problems.append(f"cue {index} is too fast to read ({rate:.0f} characters per second)")
        if len(cue.text.split("\n")) > MAX_LINES:
            problems.append(f"cue {index} has more than {MAX_LINES} lines")
        previous_end = cue.end
    if video_duration is not None and cues[-1].end > video_duration + 1.0:
        problems.append(f"captions end at {cues[-1].end:.1f}s, after the video ends ({video_duration:.1f}s)")
    return problems


# --- files -----------------------------------------------------------------------
def find_render_srt(media_dir: Path, slug: str) -> Optional[Path]:
    candidates = sorted(Path(media_dir).rglob(f"{slug}.srt"), key=lambda path: path.stat().st_mtime)
    return candidates[-1] if candidates else None


def caption_paths(output_dir: Path, slug: str):
    return Path(output_dir) / f"{slug}.srt", Path(output_dir) / f"{slug}.vtt"


def caption_info_path(output_dir: Path, slug: str) -> Path:
    """Sidecar that records how the captions next to it were timed."""
    return Path(output_dir) / f"{slug}.captions.json"


def read_caption_source(output_dir: Path, slug: str) -> Optional[str]:
    try:
        return json.loads(caption_info_path(output_dir, slug).read_text(encoding="utf-8")).get("source")
    except (OSError, ValueError, AttributeError):
        return None


def export_captions(cues: Sequence[Cue], output_dir: Path, slug: str, source: str) -> CaptionFiles:
    srt_path, vtt_path = caption_paths(output_dir, slug)
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    srt_path.write_text(format_srt(cues), encoding="utf-8")
    vtt_path.write_text(format_vtt(cues), encoding="utf-8")
    caption_info_path(output_dir, slug).write_text(
        json.dumps({"source": source, "cue_count": len(cues)}) + "\n", encoding="utf-8",
    )
    return CaptionFiles(srt=srt_path, vtt=vtt_path, source=source, cue_count=len(cues))
