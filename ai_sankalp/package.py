"""Rich lesson packages: location, validation, and conversion to reduced configs.

A lesson package (``examples/<slug>/lesson_package.json``) is the source of
truth for a lesson. Its ``generator_compatibility`` block converts into the
reduced config the renderer uses.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import LessonConfig, LessonValidationError
from .schema_validation import SchemaIssue, load_schema, validate

PACKAGE_SCHEMA = "lesson_package.schema.json"
MAX_REPORTED_ISSUES = 20


class PackageValidationError(LessonValidationError):
    """Raised when a lesson package does not satisfy the package contract."""

    def __init__(self, message: str, issues: List[SchemaIssue]):
        super().__init__(message)
        self.issues = issues


def resolve_package_path(project_root: Path, slug: str) -> Path:
    """Locate a lesson package JSON for `slug`, preferring generated output.

    `generated/packages/*` is gitignored scratch output, so a clean clone has
    nothing there. Tracked fixtures under `examples/<slug>/` keep the
    flagship sample renderable without requiring a prior generation step.
    """
    generated_path = project_root / "generated" / "packages" / slug / "lesson_package.json"
    if generated_path.exists():
        return generated_path
    example_path = project_root / "examples" / slug / "lesson_package.json"
    if example_path.exists():
        return example_path
    raise FileNotFoundError(
        f"No lesson package found for '{slug}'. Checked {generated_path} and {example_path}."
    )


def display_path(path: Path, project_root: Optional[Path] = None) -> str:
    """Return `path` relative to the project root when it lives inside it."""
    root = Path(project_root or Path(__file__).resolve().parents[1]).resolve()
    try:
        return Path(path).resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path)


def load_package(path: Path) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise LessonValidationError(f"lesson package not found: {display_path(path)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise LessonValidationError(f"could not read lesson package {display_path(path)}: {exc}") from exc
    if not isinstance(data, dict):
        raise LessonValidationError(f"lesson package {display_path(path)} must be a JSON object")
    return data


def is_lesson_package(data: Any) -> bool:
    """`generator_compatibility`, or `scenes` together with `slug`, marks a package.

    A package missing one of those keys still gets package validation (and a
    "... is required" message), while a reduced config with a stray `scenes`
    note is not mistaken for a package.
    """
    if not isinstance(data, dict):
        return False
    return "generator_compatibility" in data or ("scenes" in data and "slug" in data)


def _ids(items: Any) -> List[Any]:
    if not isinstance(items, list):
        return []
    return [item.get("id") for item in items if isinstance(item, dict)]


def _list(value: Any) -> List[Any]:
    """A list field, or [] when the schema check will already report its type."""
    return value if isinstance(value, list) else []


def semantic_issues(package: Dict[str, Any]) -> List[SchemaIssue]:
    """Cross-reference checks that JSON Schema cannot express."""
    issues: List[SchemaIssue] = []
    scenes = package.get("scenes") if isinstance(package.get("scenes"), list) else []
    scene_ids = _ids(scenes)
    asset_ids = set(_ids(package.get("assets")))
    code_ids = set(_ids(package.get("code_examples")))
    voiceover_by_scene = {
        scene.get("id"): scene.get("voiceover") for scene in scenes if isinstance(scene, dict)
    }

    seen = set()
    for index, scene_id in enumerate(scene_ids):
        if scene_id in seen:
            issues.append(SchemaIssue(f"scenes[{index}].id", f"duplicate scene id '{scene_id}'"))
        seen.add(scene_id)

    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        for item_index, asset_id in enumerate(_list(scene.get("visual_objects"))):
            if asset_id not in asset_ids:
                issues.append(SchemaIssue(
                    f"scenes[{index}].visual_objects[{item_index}]",
                    f"'{asset_id}' does not match any assets[].id",
                ))
        for item_index, code_id in enumerate(_list(scene.get("code_example_ids"))):
            if code_id not in code_ids:
                issues.append(SchemaIssue(
                    f"scenes[{index}].code_example_ids[{item_index}]",
                    f"'{code_id}' does not match any code_examples[].id",
                ))

    segments = package.get("voiceover_segments")
    for index, segment in enumerate(segments if isinstance(segments, list) else []):
        if not isinstance(segment, dict):
            continue
        scene_id = segment.get("scene_id")
        if scene_id not in voiceover_by_scene:
            issues.append(SchemaIssue(
                f"voiceover_segments[{index}].scene_id",
                f"'{scene_id}' does not match any scenes[].id",
            ))
        elif segment.get("text") != voiceover_by_scene[scene_id]:
            issues.append(SchemaIssue(
                f"voiceover_segments[{index}].text",
                f"must exactly match the voiceover of scene '{scene_id}'",
            ))

    branding = package.get("branding")
    if isinstance(branding, dict) and branding.get("logo_asset_id") not in asset_ids:
        issues.append(SchemaIssue(
            "branding.logo_asset_id",
            f"'{branding.get('logo_asset_id')}' does not match any assets[].id",
        ))

    compatibility = package.get("generator_compatibility")
    if isinstance(compatibility, dict) and "slug" in package:
        if compatibility.get("output_video_name") != package.get("slug"):
            issues.append(SchemaIssue(
                "generator_compatibility.output_video_name",
                f"must equal slug '{package.get('slug')}' so the renderer can find this package",
            ))
    return issues


def plan_schema_issues(package: Dict[str, Any]) -> List[SchemaIssue]:
    """Primitive-plan problems (scenes[].visuals and defaults) as field issues."""
    from .primitives.planner import lesson_plan_issues

    issues = []
    for issue in lesson_plan_issues(package):
        path, _, message = issue.partition(": ")
        issues.append(SchemaIssue(path, message))
    return issues


def validate_package(package: Any) -> List[SchemaIssue]:
    """Return schema and cross-reference issues (empty when the package is valid)."""
    issues = validate(package, load_schema(PACKAGE_SCHEMA))
    if isinstance(package, dict):
        schema_ok = not issues
        issues.extend(semantic_issues(package))
        if schema_ok:
            # Planning assumes well-typed fields, so it only runs on a schema-valid package.
            issues.extend(plan_schema_issues(package))
    return issues


def ensure_valid_package(package: Any, source: str = "lesson package") -> None:
    issues = validate_package(package)
    if not issues:
        return
    shown = "\n".join(f"  - {issue}" for issue in issues[:MAX_REPORTED_ISSUES])
    more = len(issues) - MAX_REPORTED_ISSUES
    suffix = f"\n  ... and {more} more" if more > 0 else ""
    raise PackageValidationError(
        f"{source} is not a valid lesson package ({len(issues)} issue(s)):\n{shown}{suffix}",
        issues,
    )


def package_to_config_dict(package: Dict[str, Any]) -> Dict[str, Any]:
    """Build the reduced render config from a package with a fixed key order."""
    compatibility = package["generator_compatibility"]
    return {
        "topic": package["topic"],
        "title": package["title"],
        "language": package["language"],
        "sections": compatibility["sections"],
        "code_example": compatibility["code_example"],
        "summary": compatibility["summary"],
        "output_video_name": compatibility["output_video_name"],
        "voiceover": compatibility["voiceover"],
        "visual_template": (
            compatibility.get("visual_template") or package.get("visual_template") or "standard"
        ),
    }


def package_to_lesson(package: Dict[str, Any]) -> LessonConfig:
    return LessonConfig.from_dict(package_to_config_dict(package))
