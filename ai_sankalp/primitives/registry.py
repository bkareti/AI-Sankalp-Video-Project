"""Primitive type name -> builder. Keys must equal specs.SPEC_TYPES."""
from __future__ import annotations

from typing import Any, Callable, Dict

from .base import BuiltVisual, PrimitiveContext
from .cards import bullet_card, card_merge, concept_map, outro_card, title_card
from .code import code_walkthrough
from .diagrams import diagram_builder
from .lanes import array_lane, bounds_check, index_access, loop_trace, practice_reveal, token_breakdown
from .specs import STANDARD_COMPATIBLE  # noqa: F401  (re-exported)

Builder = Callable[[Dict[str, Any], PrimitiveContext], BuiltVisual]

BUILDERS: Dict[str, Builder] = {
    "flow": diagram_builder("flow"),
    "steps": diagram_builder("steps"),
    "compare": diagram_builder("compare"),
    "table": diagram_builder("table"),
    "title_card": title_card,
    "card_merge": card_merge,
    "array_lane": array_lane,
    "token_breakdown": token_breakdown,
    "index_access": index_access,
    "code_walkthrough": code_walkthrough,
    "loop_trace": loop_trace,
    "bounds_check": bounds_check,
    "practice_reveal": practice_reveal,
    "concept_map": concept_map,
    "outro_card": outro_card,
    "bullet_card": bullet_card,
}


def build_visual(spec: Dict[str, Any], ctx: PrimitiveContext) -> BuiltVisual:
    return BUILDERS[spec["type"]](spec, ctx)
