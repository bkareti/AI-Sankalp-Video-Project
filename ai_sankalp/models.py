from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List


class LessonValidationError(ValueError):
    """Raised when lesson input cannot produce a useful video."""


def safe_slug(value: str, fallback: str = "lesson") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip()).strip("_").lower()
    return slug[:80] or fallback


def scene_class_name(value: str) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", value)
    name = "".join(word[:1].upper() + word[1:] for word in words) or "Lesson"
    if name[0].isdigit():
        name = f"Lesson{name}"
    return f"{name}Scene"


@dataclass
class VoiceoverConfig:
    enabled: bool = True
    language: str = "en"
    tld: str = "com"
    speed: float = 1.0
    provider: str = "gtts"
    voice: str = "en-IN-NeerjaNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"

    @classmethod
    def from_dict(cls, data: Any) -> "VoiceoverConfig":
        if isinstance(data, bool):
            return cls(enabled=data)
        if data is None:
            return cls()
        if not isinstance(data, dict):
            raise LessonValidationError("voiceover must be true, false, or an object")
        speed = float(data.get("speed", 1.0))
        if not 0.5 <= speed <= 2.0:
            raise LessonValidationError("voiceover.speed must be between 0.5 and 2.0")
        return cls(
            enabled=bool(data.get("enabled", True)),
            language=str(data.get("language", "en")).strip() or "en",
            tld=str(data.get("tld", "com")).strip() or "com",
            speed=speed,
            provider=str(data.get("provider", "gtts")).strip().lower() or "gtts",
            voice=str(data.get("voice", "en-IN-NeerjaNeural")).strip() or "en-IN-NeerjaNeural",
            rate=str(data.get("rate", "+0%")).strip() or "+0%",
            pitch=str(data.get("pitch", "+0Hz")).strip() or "+0Hz",
        )


@dataclass
class LessonSection:
    title: str
    bullets: List[str]
    narration: str = ""

    @classmethod
    def from_value(cls, value: Any, index: int) -> "LessonSection":
        if isinstance(value, str):
            return cls(title=f"Step {index}", bullets=[value.strip()])
        if not isinstance(value, dict):
            raise LessonValidationError(f"section {index} must be text or an object")
        raw_bullets = value.get("bullets", [])
        if isinstance(raw_bullets, str):
            raw_bullets = [raw_bullets]
        bullets = [str(item).strip() for item in raw_bullets if str(item).strip()]
        title = str(value.get("title", f"Step {index}")).strip()
        if not title or not bullets:
            raise LessonValidationError(f"section {index} needs a title and at least one bullet")
        return cls(title=title, bullets=bullets, narration=str(value.get("narration", "")).strip())


@dataclass
class LessonConfig:
    topic: str
    title: str
    language: str
    sections: List[LessonSection]
    code_example: str
    output_video_name: str
    summary: List[str] = field(default_factory=list)
    voiceover: VoiceoverConfig = field(default_factory=VoiceoverConfig)
    visual_template: str = "standard"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LessonConfig":
        if not isinstance(data, dict):
            raise LessonValidationError("lesson config must be a JSON/YAML object")

        topic = str(data.get("topic", "")).strip()
        title = str(data.get("title", data.get("lesson_title", ""))).strip()
        language = str(data.get("language", data.get("programming_language", ""))).strip()
        code = str(data.get("code_example", data.get("code", ""))).rstrip()
        output_name = str(data.get("output_video_name", data.get("output", ""))).strip()

        raw_sections = data.get("sections")
        if raw_sections is None:
            raw_sections = cls._sections_from_explanation(data.get("explanation", data.get("script", [])))
        if not isinstance(raw_sections, list):
            raise LessonValidationError("sections/explanation must be a list or text")
        parsed_sections = [LessonSection.from_value(value, i + 1) for i, value in enumerate(raw_sections)]
        sections: List[LessonSection] = []
        for section in parsed_sections:
            chunks = [section.bullets[index:index + 4] for index in range(0, len(section.bullets), 4)]
            for index, bullets in enumerate(chunks):
                sections.append(LessonSection(
                    title=section.title if index == 0 else f"{section.title} (continued)",
                    bullets=bullets,
                    narration=section.narration if index == 0 else "",
                ))

        missing = [name for name, value in (
            ("topic", topic), ("title", title), ("language", language),
            ("code_example", code), ("output_video_name", output_name),
        ) if not value]
        if missing:
            raise LessonValidationError(f"missing required field(s): {', '.join(missing)}")
        if not sections:
            raise LessonValidationError("at least one explanation section is required")

        raw_summary = data.get("summary", [])
        if isinstance(raw_summary, str):
            raw_summary = [line.strip(" -\t") for line in raw_summary.splitlines() if line.strip(" -\t")]
        summary = [str(item).strip() for item in raw_summary if str(item).strip()]
        if not summary:
            summary = [section.bullets[0] for section in sections[:4]]

        visual_template = str(data.get("visual_template", "standard")).strip().lower() or "standard"
        if visual_template not in {"standard", "futuristic_array"}:
            raise LessonValidationError("visual_template must be standard or futuristic_array")

        return cls(
            topic=topic,
            title=title,
            language=language,
            sections=sections,
            code_example=code,
            output_video_name=safe_slug(Path(output_name).stem, "ai_sankalp_lesson"),
            summary=summary[:4],
            voiceover=VoiceoverConfig.from_dict(data.get("voiceover")),
            visual_template=visual_template,
        )

    @staticmethod
    def _sections_from_explanation(value: Any) -> List[Any]:
        if isinstance(value, list):
            return value
        if not isinstance(value, str):
            return []
        blocks = [block.strip() for block in re.split(r"\n\s*\n", value) if block.strip()]
        sections: List[Dict[str, Any]] = []
        for index, block in enumerate(blocks, 1):
            lines = [line.strip().lstrip("-*• ").strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue
            has_heading = len(lines) > 1 and len(lines[0]) <= 55 and not lines[0].endswith((".", ";"))
            sections.append({
                "title": lines[0].rstrip(":" ) if has_heading else f"Step {index}",
                "bullets": lines[1:] if has_heading else lines,
            })
        return sections

    @property
    def slug(self) -> str:
        return safe_slug(self.output_video_name)

    @property
    def scene_class(self) -> str:
        return scene_class_name(self.slug)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
