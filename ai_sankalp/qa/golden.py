"""Golden regression data for the flagship lesson.

Two layers:

- **Plan golden** (always on, offline): the primitive plan of the package,
  covering scene ids, primitives, sentence and beat counts, and planned
  seconds. It is stored in tests/golden/<slug>.plan.json.
- **Frame golden** (opt-in, renders): a silent low-quality render's duration and
  a difference hash (dHash) of 10 evenly spaced frames. It is stored in
  tests/golden/<slug>.frames.json.

Update after an intentional change:

    .venv/bin/python -m ai_sankalp.qa.golden update-plan --slug arrays_in_cpp
    .venv/bin/python -m ai_sankalp.qa.golden update-frames --slug arrays_in_cpp
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from ..media_probe import probe_duration
from ..primitives.planner import plan_lesson

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = PROJECT_ROOT / "tests" / "golden"
FRAME_COUNT = 10
HASH_SIZE = 8
MAX_HAMMING = 10
DURATION_TOLERANCE = 0.10


def plan_snapshot(package: Dict[str, Any]) -> Dict[str, Any]:
    plans = plan_lesson(package)
    return {
        "slug": package.get("slug"),
        "scene_count": len(plans),
        "planned_seconds": sum(float(scene.get("timing_seconds") or 0) for scene in package.get("scenes", [])),
        "duration_minutes": package.get("duration_minutes"),
        "scenes": [
            {
                "id": plan.scene_id,
                "type": plan.type,
                "sentences": len(plan.sentences),
                "visuals": [
                    {"type": visual.type, "beats": visual.beat_count, "timing": visual.timing}
                    for visual in plan.visuals
                ],
            }
            for plan in plans
        ],
    }


def dhash(image, size: int = HASH_SIZE) -> str:
    """Difference hash of a PIL image as a hex string (size*size bits)."""
    from PIL import Image

    gray = image.convert("L").resize((size + 1, size), Image.LANCZOS)
    pixels = list(gray.getdata())
    bits = 0
    for row in range(size):
        for column in range(size):
            left = pixels[row * (size + 1) + column]
            right = pixels[row * (size + 1) + column + 1]
            bits = (bits << 1) | (1 if left > right else 0)
    return f"{bits:0{size * size // 4}x}"


def hamming(first: str, second: str) -> int:
    return bin(int(first, 16) ^ int(second, 16)).count("1")


def frame_times(duration: float, count: int = FRAME_COUNT) -> List[float]:
    return [round((index + 0.5) / count * duration, 3) for index in range(count)]


def extract_frames(video: Path, times: Sequence[float], out_dir: Path) -> List[Path]:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is required to extract frames")
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, moment in enumerate(times):
        path = out_dir / f"frame_{index:02d}.png"
        subprocess.run(
            [ffmpeg, "-v", "error", "-y", "-ss", f"{moment}", "-i", str(video), "-frames:v", "1", str(path)],
            check=True,
        )
        paths.append(path)
    return paths


def render_silent_video(slug: str, out_dir: Path, project_root: Path = PROJECT_ROOT) -> Path:
    """Render the tracked package silently at low quality into `out_dir`."""
    package = project_root / "examples" / slug / "lesson_package.json"
    subprocess.run(
        [sys.executable, str(project_root / "app.py"), "generate", "--config", str(package),
         "--render", "--no-voiceover", "--quality", "low", "--output-dir", str(out_dir)],
        cwd=project_root, check=True, capture_output=True, text=True,
    )
    return out_dir / f"{slug}.mp4"


def frames_snapshot(video: Path, work_dir: Path) -> Dict[str, Any]:
    from PIL import Image

    duration = probe_duration(video)
    if duration is None:
        raise RuntimeError("ffprobe could not measure the video")
    times = frame_times(duration)
    frames = []
    for moment, path in zip(times, extract_frames(video, times, work_dir)):
        with Image.open(path) as image:
            frames.append({"t": moment, "dhash": dhash(image)})
    return {
        "quality": "low", "voiceover": False, "duration_seconds": round(duration, 2),
        "max_hamming": MAX_HAMMING, "duration_tolerance": DURATION_TOLERANCE, "frames": frames,
    }


def compare_frames(golden: Dict[str, Any], current: Dict[str, Any]) -> List[str]:
    """Differences between two frame snapshots (empty when they match)."""
    problems = []
    expected = golden["duration_seconds"]
    if abs(current["duration_seconds"] - expected) > expected * golden.get("duration_tolerance", DURATION_TOLERANCE):
        problems.append(f"duration {current['duration_seconds']}s differs from golden {expected}s")
    limit = golden.get("max_hamming", MAX_HAMMING)
    for index, (want, got) in enumerate(zip(golden["frames"], current["frames"])):
        distance = hamming(want["dhash"], got["dhash"])
        if distance > limit:
            problems.append(f"frame {index} at {got['t']}s differs (hamming {distance} > {limit})")
    return problems


def golden_path(slug: str, kind: str) -> Path:
    return GOLDEN_DIR / f"{slug}.{kind}.json"


def _write(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Update or check golden regression data.")
    parser.add_argument("action", choices=("update-plan", "update-frames", "check-frames"))
    parser.add_argument("--slug", default="arrays_in_cpp")
    args = parser.parse_args(argv)
    package = json.loads((PROJECT_ROOT / "examples" / args.slug / "lesson_package.json").read_text(encoding="utf-8"))
    if args.action == "update-plan":
        _write(golden_path(args.slug, "plan"), plan_snapshot(package))
        print(f"Wrote {golden_path(args.slug, 'plan').relative_to(PROJECT_ROOT)}")
        return 0
    with tempfile.TemporaryDirectory(prefix="ai_sankalp_golden_") as directory:
        work = Path(directory)
        current = frames_snapshot(render_silent_video(args.slug, work), work / "frames")
    if args.action == "update-frames":
        _write(golden_path(args.slug, "frames"), current)
        print(f"Wrote {golden_path(args.slug, 'frames').relative_to(PROJECT_ROOT)}")
        return 0
    problems = compare_frames(json.loads(golden_path(args.slug, "frames").read_text(encoding="utf-8")), current)
    for problem in problems:
        print(problem)
    print("Frames match the golden render." if not problems else f"{len(problems)} difference(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
