"""What each template says, as plain data (no Manim).

The standard scene speaks these segments, and the caption fallback times
them, so captions always match the narration.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .models import LessonConfig


@dataclass(frozen=True)
class NarrationSegment:
    id: str
    text: str


def _clean(text: str) -> str:
    return " ".join(text.split())


def standard_script(lesson: LessonConfig) -> List[NarrationSegment]:
    segments = [NarrationSegment(
        "intro",
        f"Welcome to AI Sankalp. In this lesson, we will learn {lesson.topic} using {lesson.language}, step by step.",
    )]
    for number, section in enumerate(lesson.sections, 1):
        text = section.narration or f"{section.title}. " + " ".join(section.bullets)
        segments.append(NarrationSegment(f"section_{number:02d}", _clean(text)))
    segments.append(NarrationSegment(
        "code",
        f"Now let us connect the idea to code. This {lesson.language} example demonstrates {lesson.topic}. "
        "Read each line and connect it to the steps we just learned.",
    ))
    segments.append(NarrationSegment("summary", _clean("Let us recap. " + " ".join(lesson.summary))))
    segments.append(NarrationSegment("outro", "Thank you for learning with AI Sankalp. Keep learning, and keep building."))
    return [NarrationSegment(segment.id, _clean(segment.text)) for segment in segments]
