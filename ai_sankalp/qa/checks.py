"""Final-ready QA checks. Each returns a CheckResult a junior reviewer can act on."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..captions import SOURCE_ESTIMATED, caption_paths, parse_srt, read_caption_source, validate_cues
from ..generator import check_template_prerequisites
from ..history import HistoryLog
from ..models import LessonConfig, LessonValidationError
from ..package import CHECKLIST_ITEMS, display_path, package_to_lesson, review_status_issues, validate_package
from .report import FAIL, NEEDS_REVIEW, PASS, CheckResult

DURATION_TOLERANCE = 0.35
MAX_DETAILS = 20


@dataclass
class QAContext:
    root: Path
    slug: str
    package_path: Optional[Path]
    package: Optional[Dict[str, Any]]
    package_error: str
    video_dir: Path
    probe: Callable[[Path], Optional[float]]
    lesson: Optional[LessonConfig] = None
    video_duration: Optional[float] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    # Set by package_schema: later checks only read package fields from a valid package.
    package_valid: bool = False
    # An examples/ package hidden by a generated/packages copy with a different review_status.
    shadowed_package: Optional[Path] = None

    def rel(self, path: Path) -> str:
        return display_path(path, self.root)

    @property
    def video(self) -> Path:
        return self.video_dir / f"{self.slug}.mp4"

    @property
    def config_arg(self) -> str:
        return self.rel(self.package_path) if self.package_path else f"examples/{self.slug}/lesson_package.json"

    def latest_render(self) -> Optional[Dict[str, Any]]:
        target = self.video.resolve()
        for record in self.history:  # newest first
            if record.get("event") == "render_succeeded" and record.get("video"):
                if Path(record["video"]).resolve() == target:
                    return record
        return None


def _missing_package(check_id: str, title: str, ctx: QAContext) -> CheckResult:
    return CheckResult(check_id, title, FAIL, "Cannot check this without a valid lesson package.",
                       "Fix the package checks above first.")


def _needs_valid_package(ctx: QAContext) -> bool:
    return ctx.package is None or not ctx.package_valid


def package_present(ctx: QAContext) -> CheckResult:
    title = "Lesson package exists"
    if ctx.package is None:
        return CheckResult("package_present", title, FAIL, ctx.package_error or f"No lesson package found for '{ctx.slug}'.",
                           "Create the package with the ai-sankalp-video-assets skill, or pass --package <path>.")
    if ctx.shadowed_package is not None:
        return CheckResult(
            "package_present", title, NEEDS_REVIEW,
            f"QA is checking {ctx.config_arg}, but {ctx.rel(ctx.shadowed_package)} also exists with a different "
            "review_status. Approvals must go in the file QA checks.",
            f"Record review_status in {ctx.config_arg}, remove the stale copy, or run: "
            f"python app.py qa --package {ctx.rel(ctx.shadowed_package)}",
        )
    return CheckResult("package_present", title, PASS, f"Found {ctx.config_arg}. Record SME approval in this file.")


def package_schema(ctx: QAContext) -> CheckResult:
    title = "Lesson package matches the package schema"
    if ctx.package is None:
        return _missing_package("package_schema", title, ctx)
    issues = validate_package(ctx.package)
    ctx.package_valid = not issues
    if issues:
        return CheckResult(
            "package_schema", title, FAIL, f"{len(issues)} field problem(s) in the package.",
            f"Fix the fields listed below in {ctx.config_arg}, then run QA again.",
            [str(issue) for issue in issues[:MAX_DETAILS]],
        )
    return CheckResult("package_schema", title, PASS, "The package is valid, and its cross-references resolve.")


def reduced_config(ctx: QAContext) -> CheckResult:
    title = "Render config matches the package"
    if _needs_valid_package(ctx):
        return _missing_package("reduced_config", title, ctx)
    try:
        ctx.lesson = package_to_lesson(ctx.package)
    except (LessonValidationError, KeyError) as exc:
        return CheckResult("reduced_config", title, FAIL, f"The package cannot be converted to a render config: {exc}",
                           f"Fix generator_compatibility in {ctx.config_arg}.")
    generated = ctx.root / "generated" / "configs" / f"{ctx.slug}.json"
    fix = f"Run: python app.py generate --config {ctx.config_arg}"
    if not generated.exists():
        return CheckResult("reduced_config", title, FAIL, f"{ctx.rel(generated)} has not been generated yet.", fix)
    try:
        current = LessonConfig.from_dict(json.loads(generated.read_text(encoding="utf-8")))
    except (ValueError, LessonValidationError) as exc:
        return CheckResult("reduced_config", title, FAIL, f"{ctx.rel(generated)} cannot be read: {exc}", fix)
    if current != ctx.lesson:
        current.voiceover.enabled = ctx.lesson.voiceover.enabled
        reason = (
            "was generated with --no-voiceover (a silent preview)" if current == ctx.lesson
            else "was generated from older package content"
        )
        return CheckResult("reduced_config", title, NEEDS_REVIEW, f"{ctx.rel(generated)} differs from the package: it {reason}.", fix)
    return CheckResult("reduced_config", title, PASS, f"{ctx.rel(generated)} matches the package.")


def template_prerequisites(ctx: QAContext) -> CheckResult:
    title = "Visual template can draw this lesson"
    if ctx.lesson is None:
        return _missing_package("template_prerequisites", title, ctx)
    try:
        check_template_prerequisites(ctx.lesson, ctx.root, ctx.package_path)
    except (LessonValidationError, OSError) as exc:
        return CheckResult("template_prerequisites", title, FAIL, str(exc),
                           "Fix the package or choose visual_template 'standard'.")
    return CheckResult("template_prerequisites", title, PASS, f"'{ctx.lesson.visual_template}' supports this lesson.")


def scene_compiles(ctx: QAContext) -> CheckResult:
    title = "Generated scene compiles"
    scene = ctx.root / "generated" / "scenes" / f"{ctx.slug}.py"
    fix = f"Run: python app.py generate --config {ctx.config_arg}"
    if not scene.exists():
        return CheckResult("scene_compiles", title, FAIL, f"{ctx.rel(scene)} does not exist.", fix)
    try:
        # compile() in memory: QA never writes outside generated/qa (no .pyc files).
        compile(scene.read_text(encoding="utf-8"), str(scene), "exec")
    except SyntaxError as exc:
        return CheckResult("scene_compiles", title, FAIL, f"{ctx.rel(scene)} has a syntax error: {exc}", fix)
    return CheckResult("scene_compiles", title, PASS, f"{ctx.rel(scene)} compiles.")


def required_assets(ctx: QAContext) -> CheckResult:
    title = "Reused and generated assets are present"
    if _needs_valid_package(ctx):
        return _missing_package("required_assets", title, ctx)
    package_dir = ctx.package_path.parent if ctx.package_path else ctx.root
    search = [ctx.root / "assets", package_dir / "assets", package_dir]
    missing = []
    for asset in ctx.package.get("assets") or []:
        if asset.get("source_strategy") not in ("reuse", "generate"):
            continue
        name = asset.get("suggested_filename") or ""
        if not name or not any((folder / name).is_file() for folder in search):
            missing.append(f"{asset.get('id')}: {name or '(no suggested_filename)'}")
    if missing:
        return CheckResult(
            "required_assets", title, FAIL, f"{len(missing)} asset file(s) are missing.",
            f"Add each file to assets/ or {ctx.rel(package_dir)}/assets/.", missing,
        )
    return CheckResult("required_assets", title, PASS, "Every reused or generated asset file exists.")


def final_video(ctx: QAContext) -> CheckResult:
    title = "Final MP4 exists with the expected length"
    fix = f"Run: python app.py generate --config {ctx.config_arg} --render --quality high"
    if not ctx.video.exists() or ctx.video.stat().st_size == 0:
        return CheckResult("final_video", title, FAIL, f"{ctx.rel(ctx.video)} is missing or empty.", fix)
    ctx.video_duration = ctx.probe(ctx.video)
    if ctx.video_duration is None:
        return CheckResult("final_video", title, NEEDS_REVIEW, "The video length could not be measured (is ffprobe installed?).",
                           "Install ffmpeg (which includes ffprobe), or watch the video to confirm its length.")
    planned = float(ctx.package["duration_minutes"]) * 60 if ctx.package_valid else 0.0
    if planned and abs(ctx.video_duration - planned) / planned > DURATION_TOLERANCE:
        return CheckResult(
            "final_video", title, NEEDS_REVIEW,
            f"The video is {ctx.video_duration:.0f}s long but the package plans {planned:.0f}s "
            f"(more than {DURATION_TOLERANCE:.0%} off). A silent preview render is much shorter.",
            fix,
        )
    return CheckResult("final_video", title, PASS, f"{ctx.rel(ctx.video)} is {ctx.video_duration:.0f}s long.")


def captions(ctx: QAContext) -> CheckResult:
    title = "Captions exist and are readable"
    srt_path, vtt_path = caption_paths(ctx.video_dir, ctx.slug)
    fix = (f"Render again (captions are written next to the MP4), or run: python app.py captions --config {ctx.config_arg}"
           " (add --force to replace render-timed captions)")
    missing = [ctx.rel(path) for path in (srt_path, vtt_path) if not path.exists()]
    if missing:
        return CheckResult("captions", title, FAIL, "Caption file(s) missing: " + ", ".join(missing), fix)
    try:
        cues = parse_srt(srt_path.read_text(encoding="utf-8"))
        vtt_cues = parse_srt(vtt_path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        return CheckResult("captions", title, FAIL, f"A caption file cannot be read: {exc}", fix)
    if not cues or len(vtt_cues) != len(cues):
        return CheckResult("captions", title, FAIL, "The SRT has no cues, or the SRT and VTT disagree.", fix)
    problems = validate_cues(cues, ctx.video_duration)
    # The sidecar written with the files is authoritative; history is a fallback for older renders.
    source = read_caption_source(ctx.video_dir, ctx.slug) or ((ctx.latest_render() or {}).get("captions") or {}).get("source")
    if source == SOURCE_ESTIMATED:
        problems.insert(0, "captions were estimated from narration text, not timed by the render")
    elif source is None:
        problems.insert(0, "it is unknown how these captions were timed (no captions.json or render record)")
    if problems:
        return CheckResult(
            "captions", title, NEEDS_REVIEW, "The captions need a human check.",
            "Watch the captioned video (render with --burn-captions) and confirm timing and readability.",
            problems[:MAX_DETAILS],
        )
    return CheckResult("captions", title, PASS, f"{len(cues)} caption cues in {ctx.rel(srt_path)} and {ctx.rel(vtt_path)}.")


def history(ctx: QAContext) -> CheckResult:
    title = "Render history shows a narrated final render"
    record = ctx.latest_render()
    fix = f"Run: python app.py generate --config {ctx.config_arg} --render --quality high"
    if record is None:
        return CheckResult("history", title, NEEDS_REVIEW,
                           f"generated/history.jsonl has no successful render of {ctx.rel(ctx.video)}.", fix)
    wants_voice = ctx.lesson.voiceover.enabled if ctx.lesson else True
    if wants_voice and not record.get("voiceover", True):
        return CheckResult("history", title, FAIL,
                           "The latest render was a silent preview (--no-voiceover), but the lesson has narration.",
                           fix + " (without --no-voiceover)")
    return CheckResult("history", title, PASS,
                       f"Rendered {record.get('timestamp', '')} at {record.get('quality', '?')} quality.")


def sme_approval(ctx: QAContext) -> CheckResult:
    title = "Subject-matter expert approved the lesson"
    fix = ("Ask the SME to review the video with docs/review-checklist.md, then set review_status.sme_approved, "
           f"sme_reviewer and sme_approved_on in {ctx.config_arg}.")
    if _needs_valid_package(ctx):
        review = (ctx.package or {}).get("review_status")
        if isinstance(review, dict) and review.get("sme_approved") is not True:
            return CheckResult("sme_approval", title, FAIL, "review_status.sme_approved is false.", fix)
        return CheckResult("sme_approval", title, FAIL,
                           "Approval cannot be confirmed until the package schema problems are fixed.", fix)
    review = ctx.package.get("review_status")
    if not isinstance(review, dict):
        return CheckResult("sme_approval", title, FAIL, "The package has no review_status.", fix)
    if review.get("sme_approved") is not True:
        return CheckResult("sme_approval", title, FAIL, "review_status.sme_approved is false.", fix)
    issues = review_status_issues(ctx.package)
    if issues:
        return CheckResult("sme_approval", title, FAIL, "The approval is incomplete.", fix, [str(issue) for issue in issues])
    return CheckResult("sme_approval", title, PASS, f"Approved by {review['sme_reviewer']} on {review['sme_approved_on']}.")


def manual_checklist(ctx: QAContext) -> CheckResult:
    title = "Manual review checklist is complete"
    if _needs_valid_package(ctx):
        return _missing_package("manual_checklist", title, ctx)
    checklist = (ctx.package.get("review_status") or {}).get("checklist") or {}
    open_items = [f"{item}: {checklist.get(item, 'pending')}" for item in CHECKLIST_ITEMS if checklist.get(item) != "pass"]
    if open_items:
        return CheckResult(
            "manual_checklist", title, NEEDS_REVIEW, "Some review checklist items are not marked pass.",
            "Review each item with docs/review-checklist.md and set it to \"pass\" in review_status.checklist.",
            open_items,
        )
    return CheckResult("manual_checklist", title, PASS, "Pedagogy, pacing, readability, and brand are all marked pass.")


CHECKS = (
    package_present, package_schema, reduced_config, template_prerequisites, scene_compiles,
    required_assets, final_video, captions, history, sme_approval, manual_checklist,
)


def load_history(root: Path) -> List[Dict[str, Any]]:
    return HistoryLog(root / "generated" / "history.jsonl").recent(10 ** 6)
