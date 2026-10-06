from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config_io import save_config
from .history import HistoryLog
from .models import LessonConfig, LessonValidationError
from .package import display_path, ensure_valid_package, load_package, resolve_package_path
from .template_registry import TEMPLATES


COMPILE_METADATA_SUFFIX = ".compile.json"


class SceneSyntaxError(LessonValidationError):
    """Raised when a generated scene is not valid Python, so it cannot render."""


@dataclass
class GeneratedLesson:
    config_path: Path
    scene_path: Path
    scene_class: str
    package_path: Optional[Path] = None


def compile_metadata_path(scene_path: Path) -> Path:
    """Where the package compiler stores its metadata: beside the scene it describes."""
    return Path(scene_path).with_suffix(COMPILE_METADATA_SUFFIX)


def check_scene_syntax(source: str, name: str) -> None:
    """Fail with a readable message when `source` does not compile.

    This is what `py_compile` does, in memory, so checking never writes a
    `.pyc` file or leaves a half-written scene behind.
    """
    try:
        compile(source, name, "exec")
    except (SyntaxError, ValueError) as exc:
        line = getattr(exc, "lineno", None)
        where = f" at line {line}" if line else ""
        detail = getattr(exc, "msg", None) or str(exc)
        raise SceneSyntaxError(
            f"generated scene {name} has a syntax error{where}: {detail}. "
            "Restore templates/generated_scene.py.tmpl and generate again."
        ) from exc


def check_template_prerequisites(
    lesson: LessonConfig, project_root: Path, package_path: Optional[Path] = None
) -> Optional[Path]:
    """Fail before any file is written when the template cannot render `lesson`.

    Returns the package path the template will use, or None when the template
    does not need a package.
    """
    spec = TEMPLATES[lesson.visual_template]
    if not spec.requires_package:
        return Path(package_path) if package_path else None

    if package_path is None:
        try:
            package_path = resolve_package_path(project_root, lesson.slug)
        except FileNotFoundError:
            generated = display_path(
                project_root / "generated" / "packages" / lesson.slug / "lesson_package.json", project_root
            )
            example = display_path(
                project_root / "examples" / lesson.slug / "lesson_package.json", project_root
            )
            raise LessonValidationError(
                f"visual_template '{spec.name}' needs a rich lesson package, but none was found for "
                f"'{lesson.slug}'. Checked {generated} and {example}. Create one with the "
                "ai-sankalp-video-assets skill, pass the package itself with --config, "
                "or use visual_template 'standard'."
            ) from None
    package = load_package(package_path)
    ensure_valid_package(package, display_path(package_path, project_root))
    problems = spec.check(lesson, package)
    if problems:
        raise LessonValidationError("; ".join(problems))
    return Path(package_path)


def _package_path_literal(package_path: Optional[Path], project_root: Path) -> str:
    if package_path is None:
        return "None"
    try:
        relative = Path(package_path).resolve().relative_to(project_root)
    except ValueError:
        return f"Path({str(Path(package_path).resolve())!r})"
    return f"PROJECT_ROOT / {relative.as_posix()!r}"


class LessonGenerator:
    def __init__(self, project_root: Path):
        self.root = Path(project_root).resolve()
        self.generated = self.root / "generated"
        self.template_path = self.root / "templates" / "generated_scene.py.tmpl"
        self.history = HistoryLog(self.generated / "history.jsonl")

    def generate(self, lesson: LessonConfig, package_path: Optional[Path] = None) -> GeneratedLesson:
        if not self.template_path.exists():
            raise FileNotFoundError(f"scene template not found: {self.template_path}")
        resolved_package = check_template_prerequisites(lesson, self.root, package_path)
        # Only an explicitly supplied package is pinned in the scene; otherwise
        # the scene resolves by slug at render time (generated/ copy first).
        pinned_package = resolved_package if package_path is not None else None

        config_path = self.generated / "configs" / f"{lesson.slug}.json"
        scene_path = self.generated / "scenes" / f"{lesson.slug}.py"

        spec = TEMPLATES[lesson.visual_template]
        template = self.template_path.read_text(encoding="utf-8")
        relative_config = f"configs/{lesson.slug}.json"
        scene_source = (
            template.replace("__SCENE_CLASS__", lesson.scene_class)
            .replace("__CONFIG_RELATIVE_PATH__", relative_config)
            .replace("__SCENE_MODULE__", spec.scene_module)
            .replace("__SCENE_BASE__", spec.scene_base)
            .replace("__PACKAGE_PATH__", _package_path_literal(pinned_package, self.root))
        )
        # A scene that cannot compile fails here, before any file changes.
        check_scene_syntax(scene_source, display_path(scene_path, self.root))

        save_config(lesson, config_path)
        scene_path.parent.mkdir(parents=True, exist_ok=True)
        scene_path.write_text(scene_source, encoding="utf-8")
        # Metadata from an earlier package compile describes files that were just
        # replaced. The package compiler writes a fresh one after generating.
        compile_metadata_path(scene_path).unlink(missing_ok=True)
        self.history.add(
            "scene_generated",
            topic=lesson.topic,
            title=lesson.title,
            output_name=lesson.output_video_name,
            scene=str(scene_path),
            config=str(config_path),
            package=display_path(resolved_package, self.root) if resolved_package else None,
            voiceover=lesson.voiceover.enabled,
        )
        return GeneratedLesson(
            config_path=config_path,
            scene_path=scene_path,
            scene_class=lesson.scene_class,
            package_path=resolved_package,
        )
