from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .template_registry import TEMPLATE_NAMES


class LessonValidationError(ValueError):
    """Raised when lesson input cannot produce a useful video."""


VOICE_PROVIDERS = ("gtts", "edge")
RATE_PATTERN = r"^[+-]\d+%$"
PITCH_PATTERN = r"^[+-]\d+Hz$"


def safe_slug(value: str, fallback: str = "lesson") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip()).strip("_").lower()
    return slug[:80] or fallback


def _text_field(data: Dict[str, Any], *keys: str) -> str:
    """Return the first present key as text; null (e.g. a blank YAML value) counts as missing."""
    for key in keys:
        value = data.get(key)
        if value is not None:
            return str(value)
    return ""


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

    ACCEPTED_FIELDS = frozenset({
        "enabled", "language", "tld", "speed", "provider", "voice", "rate", "pitch",
    })
    # Accepted for documentation in packages; never used at render time.
    INFORMATIONAL_FIELDS = frozenset({"human_delivery_notes"})

    @classmethod
    def from_dict(cls, data: Any) -> "VoiceoverConfig":
        if isinstance(data, bool):
            return cls(enabled=data)
        if data is None:
            return cls()
        if not isinstance(data, dict):
            raise LessonValidationError("voiceover must be true, false, or an object")
        enabled = data.get("enabled", True)
        if not isinstance(enabled, bool):
            raise LessonValidationError("voiceover.enabled must be true or false")
        speed = data.get("speed", 1.0)
        if isinstance(speed, bool) or not isinstance(speed, (int, float)):
            raise LessonValidationError("voiceover.speed must be a number between 0.5 and 2.0")
        speed = float(speed)
        if not 0.5 <= speed <= 2.0:
            raise LessonValidationError("voiceover.speed must be between 0.5 and 2.0")
        provider = str(data.get("provider", "gtts")).strip().lower() or "gtts"
        if provider not in VOICE_PROVIDERS:
            raise LessonValidationError(
                f"voiceover.provider must be one of: {', '.join(VOICE_PROVIDERS)} (got '{provider}')"
            )
        rate = str(data.get("rate", "+0%")).strip() or "+0%"
        if not re.match(RATE_PATTERN, rate):
            raise LessonValidationError(f"voiceover.rate must look like +0% or -4% (got '{rate}')")
        pitch = str(data.get("pitch", "+0Hz")).strip() or "+0Hz"
        if not re.match(PITCH_PATTERN, pitch):
            raise LessonValidationError(f"voiceover.pitch must look like +0Hz or -2Hz (got '{pitch}')")
        return cls(
            enabled=enabled,
            language=str(data.get("language", "en")).strip() or "en",
            tld=str(data.get("tld", "com")).strip() or "com",
            speed=speed,
            provider=provider,
            voice=str(data.get("voice", "en-IN-NeerjaNeural")).strip() or "en-IN-NeerjaNeural",
            rate=rate,
            pitch=pitch,
        )


@dataclass
class LessonSection:
    title: str
    bullets: List[str]
    narration: str = ""

    ACCEPTED_FIELDS = frozenset({"title", "bullets", "narration"})

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

    # Every top-level key from_dict reads. Aliases kept for older configs:
    # lesson_title, programming_language, code, output, explanation, script.
    ACCEPTED_FIELDS = frozenset({
        "topic", "title", "lesson_title", "language", "programming_language",
        "sections", "explanation", "script", "code_example", "code", "summary",
        "output_video_name", "output", "voiceover", "visual_template",
    })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LessonConfig":
        if not isinstance(data, dict):
            raise LessonValidationError("lesson config must be a JSON/YAML object")

        topic = _text_field(data, "topic").strip()
        title = _text_field(data, "title", "lesson_title").strip()
        language = _text_field(data, "language", "programming_language").strip()
        code = _text_field(data, "code_example", "code").rstrip()
        output_name = _text_field(data, "output_video_name", "output").strip()

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
        if visual_template not in TEMPLATE_NAMES:
            raise LessonValidationError(
                f"visual_template must be one of: {', '.join(TEMPLATE_NAMES)} (got '{visual_template}')"
            )

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
