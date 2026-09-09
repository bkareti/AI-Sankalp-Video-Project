from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import LessonConfig, LessonValidationError


def load_config(path: Path) -> LessonConfig:
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
            data: Dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
    except LessonValidationError:
        raise
    except Exception as exc:
        raise LessonValidationError(f"could not read config {path}: {exc}") from exc
    return LessonConfig.from_dict(data)


def save_config(config: LessonConfig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
