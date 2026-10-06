"""Final-ready QA: run every check for one lesson and write qa_report.json.

    report = run_qa(project_root, slug="arrays_in_cpp")
    write_report(report, default_report_path(project_root, report.slug))
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from ..media_probe import probe_duration
from ..models import LessonValidationError
from ..package import display_path, load_package, resolve_package_path
from .checks import CHECKS, QAContext, load_history
from .report import FAIL, NEEDS_REVIEW, PASS, CheckResult, QAReport, write_report  # noqa: F401

EXIT_CODES = {PASS: 0, FAIL: 1, NEEDS_REVIEW: 2}


def _generated_package(root: Path, slug: str) -> Path:
    return (root / "generated" / "packages" / slug / "lesson_package.json").resolve()


def _shadowed_example(root: Path, slug: str, package: dict) -> Optional[Path]:
    """The examples/ package hidden by a generated copy, when their review_status differ."""
    example = root / "examples" / slug / "lesson_package.json"
    if not example.exists():
        return None
    try:
        other = load_package(example)
    except LessonValidationError:
        return example
    return example if other.get("review_status") != package.get("review_status") else None


def _run_check(check, ctx: QAContext) -> CheckResult:
    """A check that crashes becomes a FAIL row, so QA always produces a report."""
    try:
        return check(ctx)
    except Exception as exc:  # noqa: BLE001 - report every failure instead of a traceback
        name = check.__name__
        return CheckResult(name, name.replace("_", " ").capitalize(), FAIL,
                           f"The check could not run: {type(exc).__name__}: {exc}",
                           "Fix the package problems listed above, then run QA again.")


def default_report_path(project_root: Path, slug: str) -> Path:
    return Path(project_root) / "generated" / "qa" / slug / "qa_report.json"


def run_qa(
    project_root: Path,
    package_path: Optional[Path] = None,
    slug: Optional[str] = None,
    video_dir: Optional[Path] = None,
    now: Optional[Callable[[], datetime]] = None,
    probe: Optional[Callable[[Path], Optional[float]]] = None,
) -> QAReport:
    if package_path is None and not slug:
        raise ValueError("run_qa needs a package path or a slug")
    root = Path(project_root).resolve()
    package, error = None, ""
    if package_path is None:
        try:
            package_path = resolve_package_path(root, slug)
        except FileNotFoundError as exc:
            error = str(exc).replace(str(root) + "/", "")
    if package_path is not None:
        package_path = Path(package_path).resolve()
        try:
            package = load_package(package_path)
        except LessonValidationError as exc:
            error = str(exc)
    if package is not None and not slug:
        slug = str(package.get("slug") or package_path.parent.name)
    slug = slug or package_path.parent.name

    ctx = QAContext(
        root=root, slug=slug, package_path=package_path, package=package, package_error=error,
        video_dir=Path(video_dir or root / "generated" / "videos").resolve(), probe=probe or probe_duration,
        history=load_history(root),
    )
    if package is not None and slug and package_path == _generated_package(root, slug):
        ctx.shadowed_package = _shadowed_example(root, slug, package)
    checks = [_run_check(check, ctx) for check in CHECKS]
    srt_path = ctx.video_dir / f"{slug}.srt"
    inputs = {
        "package": display_path(package_path, root) if package_path else None,
        "scene": display_path(root / "generated" / "scenes" / f"{slug}.py", root),
        "compile_metadata": display_path(root / "generated" / "scenes" / f"{slug}.compile.json", root),
        "video": display_path(ctx.video, root),
        "captions_srt": display_path(srt_path, root),
        "captions_vtt": display_path(srt_path.with_suffix(".vtt"), root),
    }
    stamp = (now or (lambda: datetime.now(timezone.utc).astimezone()))()
    return QAReport(slug=slug, created_at=stamp.isoformat(timespec="seconds"), inputs=inputs, checks=checks)
