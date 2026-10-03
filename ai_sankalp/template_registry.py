"""Visual template registry: routing and prerequisites, without importing Manim."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

PrerequisiteCheck = Callable[[Any, Optional[Dict[str, Any]]], List[str]]


def _no_checks(lesson: Any, package: Optional[Dict[str, Any]]) -> List[str]:
    return []


@dataclass(frozen=True)
class TemplateSpec:
    name: str
    scene_module: str
    scene_base: str
    requires_package: bool = False
    description: str = ""
    check: PrerequisiteCheck = field(default=_no_checks, compare=False, repr=False)


def _check_package_plan(lesson: Any, package: Optional[Dict[str, Any]]) -> List[str]:
    """Every package scene must resolve to valid primitives (explicit or default)."""
    if package is None:
        return []
    from .primitives.planner import lesson_plan_issues

    issues = lesson_plan_issues(package)
    if not issues:
        return []
    return ["the lesson package cannot be drawn with 'futuristic_array': " + "; ".join(issues)]


TEMPLATES: Dict[str, TemplateSpec] = {
    "standard": TemplateSpec(
        name="standard",
        scene_module="ai_sankalp.manim_scene",
        scene_base="ConfigDrivenLesson",
        description="Reusable layout for any topic, driven by the reduced lesson config.",
    ),
    "futuristic_array": TemplateSpec(
        name="futuristic_array",
        scene_module="ai_sankalp.futuristic_array_scene",
        scene_base="FuturisticArrayLesson",
        requires_package=True,
        description="Flagship data-driven template; draws every package scene with primitives.",
        check=_check_package_plan,
    ),
}
TEMPLATE_NAMES: Tuple[str, ...] = tuple(TEMPLATES)


def get_template(name: str) -> TemplateSpec:
    return TEMPLATES[name]
