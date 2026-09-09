from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config_io import save_config
from .history import HistoryLog
from .models import LessonConfig


@dataclass
class GeneratedLesson:
    config_path: Path
    scene_path: Path
    scene_class: str


class LessonGenerator:
    def __init__(self, project_root: Path):
        self.root = Path(project_root).resolve()
        self.generated = self.root / "generated"
        self.template_path = self.root / "templates" / "generated_scene.py.tmpl"
        self.history = HistoryLog(self.generated / "history.jsonl")

    def generate(self, lesson: LessonConfig) -> GeneratedLesson:
        if not self.template_path.exists():
            raise FileNotFoundError(f"scene template not found: {self.template_path}")
        config_path = self.generated / "configs" / f"{lesson.slug}.json"
        scene_path = self.generated / "scenes" / f"{lesson.slug}.py"
        save_config(lesson, config_path)

        template = self.template_path.read_text(encoding="utf-8")
        relative_config = f"configs/{lesson.slug}.json"
        if lesson.visual_template == "futuristic_array":
            scene_module = "ai_sankalp.futuristic_array_scene"
            scene_base = "FuturisticArrayLesson"
        else:
            scene_module = "ai_sankalp.manim_scene"
            scene_base = "ConfigDrivenLesson"
        scene_source = (
            template.replace("__SCENE_CLASS__", lesson.scene_class)
            .replace("__CONFIG_RELATIVE_PATH__", relative_config)
            .replace("__SCENE_MODULE__", scene_module)
            .replace("__SCENE_BASE__", scene_base)
        )
        scene_path.parent.mkdir(parents=True, exist_ok=True)
        scene_path.write_text(scene_source, encoding="utf-8")
        self.history.add(
            "scene_generated",
            topic=lesson.topic,
            title=lesson.title,
            output_name=lesson.output_video_name,
            scene=str(scene_path),
            config=str(config_path),
            voiceover=lesson.voiceover.enabled,
        )
        return GeneratedLesson(config_path=config_path, scene_path=scene_path, scene_class=lesson.scene_class)
