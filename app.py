#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ai_sankalp.config_io import load_config, load_lesson_input
from ai_sankalp.generator import LessonGenerator
from ai_sankalp.history import HistoryLog
from ai_sankalp.models import LessonConfig, LessonValidationError
from ai_sankalp.renderer import DependencyError, ManimRenderer, RenderError, dependency_status


PROJECT_ROOT = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate branded AI Sankalp programming lesson videos with Manim."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("gui", help="Open the local lesson input form")

    generate = subparsers.add_parser(
        "generate", help="Generate a scene from a JSON/YAML lesson config or a rich lesson package"
    )
    generate.add_argument(
        "--config", type=Path, required=True,
        help="Reduced lesson config (JSON/YAML) or rich lesson_package.json (auto-detected)",
    )
    generate.add_argument("--render", action="store_true", help="Render the generated scene to MP4")
    generate.add_argument(
        "--no-voiceover", action="store_true", help="Render without narration (no internet needed)"
    )
    generate.add_argument("--output-dir", type=Path, help="Final MP4 folder (default: generated/videos)")
    generate.add_argument(
        "--quality", choices=("low", "medium", "high", "production", "4k"), default="low"
    )

    sample = subparsers.add_parser("sample", help="Generate the included Python loops sample")
    sample.add_argument("--render", action="store_true")
    sample.add_argument("--no-voiceover", action="store_true", help="Render without gTTS/internet")
    sample.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="low")

    subparsers.add_parser("interactive", help="Enter a lesson through terminal prompts")
    history = subparsers.add_parser("history", help="Show recent generation and render events")
    history.add_argument("--limit", type=int, default=20)
    subparsers.add_parser("check", help="Check Manim, voiceover, PyYAML, and ffmpeg")
    return parser


def interactive_lesson() -> LessonConfig:
    print("Enter explanation blocks. Use a blank line between steps; finish with a line containing END.")
    topic = input("Topic: ").strip()
    title = input("Lesson title: ").strip()
    language = input("Programming language: ").strip()
    output = input("Output video name: ").strip()
    print("Explanation:")
    explanation_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        explanation_lines.append(line)
    print("Code example (finish with a line containing END):")
    code_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        code_lines.append(line)
    enabled = input("Voiceover? [Y/n]: ").strip().lower() not in {"n", "no"}
    return LessonConfig.from_dict({
        "topic": topic,
        "title": title,
        "language": language,
        "output_video_name": output,
        "explanation": "\n".join(explanation_lines),
        "code_example": "\n".join(code_lines),
        "voiceover": enabled,
    })


def generate_and_maybe_render(
    lesson: LessonConfig,
    render: bool,
    quality: str = "low",
    output_dir: Path | None = None,
    package_path: Path | None = None,
) -> int:
    generator = LessonGenerator(PROJECT_ROOT)
    generated = generator.generate(lesson, package_path=package_path)
    print(f"Scene:  {generated.scene_path}")
    print(f"Config: {generated.config_path}")
    print(f"Class:  {generated.scene_class}")
    if generated.package_path:
        print(f"Package: {generated.package_path}")
    if render:
        result = ManimRenderer(PROJECT_ROOT).render(generated, lesson, output_dir, quality)
        print(f"Video:  {result.video_path}")
    else:
        print("Scene generated. Add --render to create the MP4.")
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command in {None, "gui"}:
            from ai_sankalp.gui import launch_gui
            launch_gui(PROJECT_ROOT)
            return 0
        if args.command == "generate":
            loaded = load_lesson_input(args.config)
            if args.no_voiceover:
                loaded.lesson.voiceover.enabled = False
            return generate_and_maybe_render(
                loaded.lesson, args.render, args.quality, args.output_dir, loaded.package_path
            )
        if args.command == "sample":
            lesson = load_config(PROJECT_ROOT / "examples" / "python_for_loops.json")
            if args.no_voiceover:
                lesson.voiceover.enabled = False
            return generate_and_maybe_render(lesson, args.render, args.quality)
        if args.command == "interactive":
            lesson = interactive_lesson()
            should_render = input("Render the MP4 now? [y/N]: ").strip().lower() in {"y", "yes"}
            return generate_and_maybe_render(lesson, should_render)
        if args.command == "history":
            records = HistoryLog(PROJECT_ROOT / "generated" / "history.jsonl").recent(args.limit)
            if not records:
                print("No generation history yet.")
            for record in records:
                details = {key: value for key, value in record.items() if key not in {"timestamp", "event", "error"}}
                print(f"{record.get('timestamp', '-')}  {record.get('event', '-'):18}  {json.dumps(details, ensure_ascii=False)}")
            return 0
        if args.command == "check":
            status = dependency_status(PROJECT_ROOT)
            for name, value in status.items():
                print(f"{name:16} {value}")
            return 0 if status.get("ffmpeg") != "missing" and status.get("python_packages") == "ok" else 1
    except (LessonValidationError, DependencyError, RenderError, FileNotFoundError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

