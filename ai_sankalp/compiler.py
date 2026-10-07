"""Package compiler: a rich lesson package in, everything a render needs out.

    compiled = PackageCompiler(project_root).compile(package_path)

One call validates the package, converts `generator_compatibility` to the
reduced render config, picks the visual template, writes the scene entry
point (after checking it compiles), and stores `<slug>.compile.json` beside
the scene. Pure Python (no Manim), and deterministic: the same package and
template always produce byte-identical config, scene, and metadata. The
metadata holds no timestamps; `generated/history.jsonl` is the timestamped log.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .captions import Cue, estimate_cues_from_lesson, estimate_cues_from_package
from .generator import GeneratedLesson, LessonGenerator, compile_metadata_path
from .models import LessonConfig
from .narration import standard_script
from .package import (
    display_path, ensure_valid_package, load_package, package_to_lesson, select_visual_template,
)
from .primitives.planner import plan_lesson
from .template_registry import TEMPLATES

# Bump when the compiler changes what it writes for an unchanged package.
COMPILER_VERSION = 1
STANDARD = "standard"


@dataclass
class CompiledLesson:
    lesson: LessonConfig
    generated: GeneratedLesson
    metadata_path: Path
    metadata: Dict[str, Any]


def canonical_sha256(value: Any) -> str:
    """SHA-256 of `value` as canonical JSON, so key order and whitespace do not matter.

    `default=str` covers values YAML produces that JSON cannot hold (an unquoted
    date becomes `datetime.date`); they hash as their ISO text.
    """
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def template_sha256(path: Path) -> str:
    """Hash the scene template as the generator reads it (text, newlines normalized).

    The scene is built from that text, so a CRLF checkout of the same template
    must give the same hash.
    """
    return hashlib.sha256(Path(path).read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def _futuristic_plan(package: Dict[str, Any]) -> List[Dict[str, Any]]:
    """What each scene draws: every primitive, and whether the scene chose it or got the default."""
    scenes = [scene for scene in package["scenes"] if isinstance(scene, dict)]
    plan = []
    for scene, scene_plan in zip(scenes, plan_lesson(package)):
        explicit = scene.get("visuals") is not None
        plan.append({
            "scene_id": scene_plan.scene_id,
            "type": scene_plan.type,
            "visuals": [
                {
                    "type": visual.type,
                    "selected_by": "scenes[].visuals" if explicit else f"default for scene type '{scene_plan.type}'",
                    "timing": visual.timing,
                    "beats": visual.beat_count,
                }
                for visual in scene_plan.visuals
            ],
            "visual_objects": list(scene.get("visual_objects") or []),
            "code_example_ids": list(scene.get("code_example_ids") or []),
            "sentence_count": len(scene_plan.sentences),
        })
    return plan


def _standard_plan(lesson: LessonConfig) -> List[Dict[str, Any]]:
    return [
        {"section": section.title, "visual": section.visual["type"] if section.visual else None}
        for section in lesson.sections
    ]


def _narration(package: Dict[str, Any], lesson: LessonConfig, template: str) -> Dict[str, Any]:
    """The text the template speaks; the caption estimate and the render both start from it."""
    if template == STANDARD:
        return {
            "source": "standard_script",
            "segments": [{"id": segment.id, "text": segment.text} for segment in standard_script(lesson)],
        }
    return {
        "source": "package_scenes",
        "segments": [
            {"id": str(scene.get("id", "")), "text": str(scene.get("voiceover", ""))}
            for scene in package["scenes"] if isinstance(scene, dict)
        ],
    }


def _caption_estimate(cues: List[Cue]) -> Dict[str, Any]:
    return {
        "estimated_cue_count": len(cues),
        "estimated_seconds": round(max((cue.end for cue in cues), default=0.0), 3),
    }


def _warnings(package: Dict[str, Any], template: str) -> List[str]:
    warnings = []
    if template == STANDARD and any(
        isinstance(scene, dict) and scene.get("visuals") is not None for scene in package["scenes"]
    ):
        warnings.append(
            "The package declares scenes[].visuals, but the 'standard' template draws only "
            "generator_compatibility.sections. Set visual_template to 'futuristic_array' to use them."
        )
    return warnings


class PackageCompiler:
    def __init__(self, project_root: Path):
        self.root = Path(project_root).resolve()
        self.generator = LessonGenerator(self.root)

    def compile(self, package_path: Path, voiceover_enabled: Optional[bool] = None) -> CompiledLesson:
        """Compile the package at `package_path`.

        `voiceover_enabled` overrides the package setting (a silent preview) and
        is recorded in the metadata. An invalid package or a scene that does not
        compile raises before any output is written.
        """
        package_path = Path(package_path).expanduser().resolve()
        source = display_path(package_path, self.root)
        package = load_package(package_path)
        ensure_valid_package(package, source)
        lesson = package_to_lesson(package)
        if voiceover_enabled is not None:
            lesson.voiceover.enabled = voiceover_enabled

        generated = self.generator.generate(lesson, package_path=package_path)
        metadata = self._metadata(package, lesson, generated, source)
        metadata_path = compile_metadata_path(generated.scene_path)
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return CompiledLesson(lesson=lesson, generated=generated, metadata_path=metadata_path, metadata=metadata)

    def _metadata(
        self, package: Dict[str, Any], lesson: LessonConfig, generated: GeneratedLesson, source: str
    ) -> Dict[str, Any]:
        template = lesson.visual_template
        selected_by = select_visual_template(package)[1]
        spec = TEMPLATES[template]
        package_sha = canonical_sha256(package)
        template_sha = template_sha256(self.generator.template_path)
        options = {"voiceover_enabled": lesson.voiceover.enabled}
        template_info = {
            "name": spec.name,
            "selected_by": selected_by,
            "scene_module": spec.scene_module,
            "scene_base": spec.scene_base,
        }
        if template == STANDARD:
            plan: List[Dict[str, Any]] = _standard_plan(lesson)
            cues = estimate_cues_from_lesson(lesson)
        else:
            plan = _futuristic_plan(package)
            cues = estimate_cues_from_package(package)
        return {
            "compiler_version": COMPILER_VERSION,
            "compile_key": canonical_sha256({
                "compiler_version": COMPILER_VERSION,
                "package_sha256": package_sha,
                "source_path": source,
                "scene_template_sha256": template_sha,
                "template": template_info,
                "options": options,
            }),
            "slug": lesson.slug,
            "source": {"kind": "lesson_package", "path": source, "sha256": package_sha},
            "options": options,
            "template": template_info,
            "scene_template_sha256": template_sha,
            "outputs": {
                "config": {
                    "path": display_path(generated.config_path, self.root),
                    "sha256": file_sha256(generated.config_path),
                },
                "scene": {
                    "path": display_path(generated.scene_path, self.root),
                    "sha256": file_sha256(generated.scene_path),
                    "class": generated.scene_class,
                },
            },
            "plan": plan,
            "narration": _narration(package, lesson, template),
            "captions": _caption_estimate(cues),
            "warnings": _warnings(package, template),
        }
