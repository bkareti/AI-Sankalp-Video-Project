from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .models import LessonConfig, LessonValidationError


@dataclass
class LoadedLesson:
    lesson: LessonConfig
    package: Optional[Dict[str, Any]] = None
    package_path: Optional[Path] = None


def read_data(path: Path) -> Any:
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise LessonValidationError(f"config file not found: {path}")
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml
            except ImportError as exc:
                raise LessonValidationError(
                    "YAML input requires PyYAML. Install requirements.txt or use JSON."
                ) from exc
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        return json.loads(path.read_text(encoding="utf-8"))
    except LessonValidationError:
        raise
    except Exception as exc:
        raise LessonValidationError(f"could not read config {path}: {exc}") from exc


def load_config(path: Path) -> LessonConfig:
    """Load a reduced lesson config (the format generated scenes read)."""
    return LessonConfig.from_dict(read_data(path))


def load_lesson_input(path: Path) -> LoadedLesson:
    """Load either a reduced config or a rich lesson package.

    A package is recognized by its `scenes` and `generator_compatibility`
    keys; it is validated and converted into a reduced config.
    """
    from .package import display_path, ensure_valid_package, is_lesson_package, package_to_lesson

    resolved = Path(path).expanduser().resolve()
    data = read_data(resolved)
    if is_lesson_package(data):
        ensure_valid_package(data, display_path(resolved))
        return LoadedLesson(lesson=package_to_lesson(data), package=data, package_path=resolved)
    return LoadedLesson(lesson=LessonConfig.from_dict(data))


def save_config(config: LessonConfig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
