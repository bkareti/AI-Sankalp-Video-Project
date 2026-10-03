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


FUTURISTIC_ARRAY_SCENE_IDS: Tuple[str, ...] = (
    "scene_01_intro",
    "scene_02_motivation",
    "scene_03_explanation",
    "scene_04_indexing",
    "scene_05_code",
    "scene_06_trace",
    "scene_07_mistake",
    "scene_08_practice",
    "scene_09_summary",
    "scene_10_outro",
)
CPP_LANGUAGE_NAMES = {"c++", "cpp", "c plus plus", "cplusplus"}


def _check_futuristic_array(lesson: Any, package: Optional[Dict[str, Any]]) -> List[str]:
    problems: List[str] = []
    language = " ".join(str(lesson.language).lower().split())
    about_arrays = "array" in f"{lesson.topic} {lesson.title}".lower()
    if language not in CPP_LANGUAGE_NAMES or not about_arrays:
        problems.append(
            "visual_template 'futuristic_array' currently supports only C++ array lessons "
            f"(got language '{lesson.language}', topic '{lesson.topic}'). "
            "Use visual_template 'standard' for other topics."
        )
    if package is not None:
        present = {scene.get("id") for scene in package.get("scenes", []) if isinstance(scene, dict)}
        missing = [scene_id for scene_id in FUTURISTIC_ARRAY_SCENE_IDS if scene_id not in present]
        if missing:
            problems.append(
                "the lesson package is missing scene id(s) required by 'futuristic_array': "
                + ", ".join(missing)
            )
    return problems


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
        description="Flagship C++ arrays template; needs a rich lesson package.",
        check=_check_futuristic_array,
    ),
}
TEMPLATE_NAMES: Tuple[str, ...] = tuple(TEMPLATES)


def get_template(name: str) -> TemplateSpec:
    return TEMPLATES[name]
