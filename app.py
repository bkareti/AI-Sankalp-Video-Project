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
    generate.add_argument(
        "--burn-captions", action="store_true",
        help="Also write <name>_captioned.mp4 with captions drawn into the video",
    )

    sample = subparsers.add_parser("sample", help="Generate the included Python loops sample")
    sample.add_argument("--render", action="store_true")
    sample.add_argument("--no-voiceover", action="store_true", help="Render without gTTS/internet")
    sample.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="low")
    sample.add_argument("--burn-captions", action="store_true", help="Also write a captioned copy of the MP4")

    captions = subparsers.add_parser(
        "captions", help="Write SRT and VTT captions from narration text, without rendering",
    )
    captions.add_argument("--config", type=Path, required=True, help="Reduced lesson config or rich lesson_package.json")
    captions.add_argument("--output-dir", type=Path, help="Caption folder (default: generated/videos)")
    captions.add_argument(
        "--force", action="store_true", help="Replace captions that a render timed exactly",
    )

    qa = subparsers.add_parser(
        "qa", help="Check whether a lesson is final-ready (exit 0 = ready, 2 = needs review, 1 = fail)",
    )
    target = qa.add_mutually_exclusive_group(required=True)
    target.add_argument("--slug", help="Lesson slug, e.g. arrays_in_cpp (package found by slug)")
    target.add_argument("--package", type=Path, help="Path to a lesson_package.json")
    qa.add_argument("--video-dir", type=Path, help="Folder with the final MP4 and captions (default: generated/videos)")
    qa.add_argument("--report", type=Path, help="Report path (default: generated/qa/<slug>/qa_report.json)")

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
    burn_captions: bool = False,
) -> int:
    generator = LessonGenerator(PROJECT_ROOT)
    generated = generator.generate(lesson, package_path=package_path)
    print(f"Scene:  {generated.scene_path}")
    print(f"Config: {generated.config_path}")
    print(f"Class:  {generated.scene_class}")
    if generated.package_path:
        print(f"Package: {generated.package_path}")
    if render:
        result = ManimRenderer(PROJECT_ROOT).render(generated, lesson, output_dir, quality, burn_captions)
        print(f"Video:  {result.video_path}")
        if result.captions:
            print(f"Captions: {result.captions.srt} and {result.captions.vtt} ({result.captions.source}, {result.captions.cue_count} cues)")
        if result.captioned_video_path:
            print(f"Captioned video: {result.captioned_video_path}")
    else:
        print("Scene generated. Add --render to create the MP4.")
        if burn_captions:
            print("Note: --burn-captions only applies with --render; no captioned video was made.")
    return 0


def write_captions(config: Path, output_dir: Path | None, force: bool = False) -> int:
    from ai_sankalp.captions import SOURCE_ESTIMATED, SOURCE_RENDER, export_captions, read_caption_source
    from ai_sankalp.generator import check_template_prerequisites
    from ai_sankalp.renderer import narration_cues

    loaded = load_lesson_input(config)
    package_path = check_template_prerequisites(loaded.lesson, PROJECT_ROOT, loaded.package_path)
    folder = Path(output_dir or PROJECT_ROOT / "generated" / "videos").expanduser().resolve()
    if read_caption_source(folder, loaded.lesson.slug) == SOURCE_RENDER and not force:
        print(
            f"Error: {folder / loaded.lesson.slug}.srt was timed by a render; estimated captions would replace it. "
            "Use --output-dir for a separate copy, or --force to replace it.",
            file=sys.stderr,
        )
        return 1
    files = export_captions(narration_cues(loaded.lesson, package_path), folder, loaded.lesson.slug, SOURCE_ESTIMATED)
    print(f"Captions: {files.srt}")
    print(f"          {files.vtt}")
    print(f"{files.cue_count} cues, timed from narration text (a render times them exactly).")
    return 0


def run_quality_check(slug: str | None, package: Path | None, video_dir: Path | None, report_path: Path | None) -> int:
    from ai_sankalp.package import display_path
    from ai_sankalp.qa import EXIT_CODES, default_report_path, run_qa, write_report

    report = run_qa(PROJECT_ROOT, package_path=package, slug=slug, video_dir=video_dir)
    path = write_report(report, Path(report_path or default_report_path(PROJECT_ROOT, report.slug)))
    print(report.format_text())
    print(f"\nReport: {display_path(path, PROJECT_ROOT)}")
    return EXIT_CODES[report.status]


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
                loaded.lesson, args.render, args.quality, args.output_dir, loaded.package_path, args.burn_captions
            )
        if args.command == "sample":
            lesson = load_config(PROJECT_ROOT / "examples" / "python_for_loops.json")
            if args.no_voiceover:
                lesson.voiceover.enabled = False
            return generate_and_maybe_render(lesson, args.render, args.quality, burn_captions=args.burn_captions)
        if args.command == "captions":
            return write_captions(args.config, args.output_dir, args.force)
        if args.command == "qa":
            return run_quality_check(args.slug, args.package, args.video_dir, args.report)
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

