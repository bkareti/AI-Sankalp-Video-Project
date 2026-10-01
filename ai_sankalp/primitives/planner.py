"""Lesson planning: which primitives each package scene shows, and when.

Pure Python (no Manim), so packages can be checked in the generator, QA,
and tests without rendering.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .specs import NO_HEADER_TYPES, beat_count, check_visual, default_visual_for_scene, scene_label

SENTENCE_PATTERN = re.compile(r"[^.!?]+(?:[.!?]+|$)")


class PlanError(ValueError):
    def __init__(self, issues: List[str]):
        super().__init__("cannot plan the lesson:\n" + "\n".join(f"  - {issue}" for issue in issues))
        self.issues = issues


@dataclass
class VisualPlan:
    type: str
    spec: Dict[str, Any]
    beat_count: int
    timing: str = "narrated"


@dataclass
class ScenePlan:
    scene_id: str
    type: str
    visuals: List[VisualPlan] = field(default_factory=list)
    sentences: List[str] = field(default_factory=list)


def split_sentences(text: str) -> List[str]:
    return [piece.strip() for piece in SENTENCE_PATTERN.findall(text or "") if piece.strip()]


def assign_beats(sentence_count: int, beat_count: int) -> List[List[int]]:
    """Map beats onto narrated sentences.

    One beat per sentence while both last. Extra sentences get no beat (the
    scene idles); extra beats all play during the last sentence, so no
    animation is silently dropped.
    """
    if sentence_count <= 0:
        return []
    groups: List[List[int]] = [[] for _ in range(sentence_count)]
    for beat in range(beat_count):
        groups[min(beat, sentence_count - 1)].append(beat)
    return groups


def _scene_visual_specs(scene: Dict[str, Any], package: Dict[str, Any], where: str, issues: List[str]) -> List[Dict[str, Any]]:
    raw_visuals = scene.get("visuals")
    if raw_visuals is None:
        raw_visuals = [default_visual_for_scene(scene, package)]
        where_of = lambda index: f"{where} (default visual for type '{scene.get('type')}')"  # noqa: E731
    else:
        where_of = lambda index: f"{where}.visuals[{index}]"  # noqa: E731
    if not isinstance(raw_visuals, list) or not 1 <= len(raw_visuals) <= 3:
        issues.append(f"{where}.visuals: must be a list of 1 to 3 visuals")
        return []
    specs = []
    for index, raw in enumerate(raw_visuals):
        spec, problems = check_visual(raw, context="scene")
        issues.extend(f"{where_of(index)}: {problem}" for problem in problems)
        if not problems:
            specs.append(spec)
    return specs


def _code_example_issue(spec: Dict[str, Any], scene: Dict[str, Any], package: Dict[str, Any]) -> str:
    ids = {example.get("id") for example in package.get("code_examples") or [] if isinstance(example, dict)}
    wanted = spec.get("code_example_id") or (scene.get("code_example_ids") or [None])[0]
    if wanted is None:
        return "" if ids else "code_walkthrough needs a code example, but the package has none"
    return "" if wanted in ids else f"code_example_id '{wanted}' does not match any code_examples[].id"


def plan_scene(scene: Dict[str, Any], index: int, package: Dict[str, Any], issues: List[str]) -> ScenePlan:
    where = f"scenes[{index}]"
    visuals = []
    for visual_index, spec in enumerate(_scene_visual_specs(scene, package, where, issues)):
        if spec["type"] not in NO_HEADER_TYPES:
            spec.setdefault("label", scene_label(scene, index))
            spec.setdefault("title", str(scene.get("title", "")).strip()[:48] or spec["label"])
        if spec["type"] == "code_walkthrough":
            problem = _code_example_issue(spec, scene, package)
            if problem:
                issues.append(f"{where}.visuals[{visual_index}]: {problem}")
                continue
        visuals.append(VisualPlan(spec["type"], spec, beat_count(spec), spec.get("timing", "narrated")))
    return ScenePlan(
        scene_id=str(scene.get("id", f"scene_{index + 1:02d}")),
        type=str(scene.get("type", "")),
        visuals=visuals,
        sentences=split_sentences(str(scene.get("voiceover", ""))),
    )


def lesson_plan_issues(package: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    for index, scene in enumerate(package.get("scenes") or []):
        if isinstance(scene, dict):
            plan_scene(scene, index, package, issues)
    return issues


def plan_lesson(package: Dict[str, Any]) -> List[ScenePlan]:
    issues: List[str] = []
    plans = [
        plan_scene(scene, index, package, issues)
        for index, scene in enumerate(package.get("scenes") or [])
        if isinstance(scene, dict)
    ]
    if issues:
        raise PlanError(issues)
    return plans
