"""Visual specs: validation and normalization without importing Manim.

A visual spec is a flat JSON object, for example::

    {"type": "flow", "title": "One pass of the loop",
     "items": ["Take next item", "Run the body", "Repeat"]}

`type` selects the primitive; every other key is a primitive parameter.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple

TITLE_MAX = 48
ITEM_MAX = 60
CELL_MAX = 24

Problems = List[str]


def _text(value: Any, where: str, problems: Problems, limit: int = ITEM_MAX) -> str:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        problems.append(f"{where} must be text")
        return ""
    text = " ".join(str(value).split())
    if not text:
        problems.append(f"{where} must not be empty")
    elif len(text) > limit:
        problems.append(f"{where} must be at most {limit} characters (got {len(text)})")
    return text


def _text_list(value: Any, where: str, problems: Problems, low: int, high: int, limit: int = ITEM_MAX) -> List[str]:
    if not isinstance(value, list):
        problems.append(f"{where} must be a list of {low} to {high} text items")
        return []
    if not low <= len(value) <= high:
        problems.append(f"{where} must have {low} to {high} items (got {len(value)})")
    return [_text(item, f"{where}[{index}]", problems, limit) for index, item in enumerate(value)]


def _items(spec: Dict[str, Any], problems: Problems) -> Dict[str, Any]:
    return {"items": _text_list(spec.get("items"), "items", problems, 2, 5)}


def _compare(spec: Dict[str, Any], problems: Problems) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for side in ("left", "right"):
        column = spec.get(side)
        if not isinstance(column, dict):
            problems.append(f"{side} must be an object with title and items")
            continue
        unknown = sorted(set(column) - {"title", "items"})
        if unknown:
            problems.append(f"{side} has unknown key(s): {', '.join(unknown)}")
        result[side] = {
            "title": _text(column.get("title"), f"{side}.title", problems, TITLE_MAX),
            "items": _text_list(column.get("items"), f"{side}.items", problems, 1, 4),
        }
    return result


def _table(spec: Dict[str, Any], problems: Problems) -> Dict[str, Any]:
    columns = _text_list(spec.get("columns"), "columns", problems, 1, 4, CELL_MAX)
    raw_rows = spec.get("rows")
    rows: List[List[str]] = []
    if not isinstance(raw_rows, list) or not 1 <= len(raw_rows) <= 6:
        problems.append("rows must be a list of 1 to 6 rows")
        raw_rows = raw_rows if isinstance(raw_rows, list) else []
    for index, row in enumerate(raw_rows):
        if not isinstance(row, list) or len(row) != len(columns):
            problems.append(f"rows[{index}] must have exactly {len(columns)} cell(s), one per column")
            continue
        rows.append([_text(cell, f"rows[{index}][{cell_index}]", problems, CELL_MAX) for cell_index, cell in enumerate(row)])
    return {"columns": columns, "rows": rows}


Normalizer = Callable[[Dict[str, Any], Problems], Dict[str, Any]]
# type -> (parameter keys, normalizer)
SPECS: Dict[str, Tuple[Tuple[str, ...], Normalizer]] = {
    "flow": (("items",), _items),
    "steps": (("items",), _items),
    "compare": (("left", "right"), _compare),
    "table": (("columns", "rows"), _table),
}
SPEC_TYPES: Tuple[str, ...] = tuple(SPECS)
COMMON_KEYS = ("type", "title")


def check_visual(raw: Any) -> Tuple[Dict[str, Any], Problems]:
    """Return (normalized spec, problems). The spec is only usable when problems is empty."""
    problems: Problems = []
    if not isinstance(raw, dict):
        return {}, ["must be an object with a type"]
    kind = raw.get("type")
    if kind not in SPECS:
        return {}, [f"type must be one of: {', '.join(SPEC_TYPES)} (got {kind!r})"]
    keys, normalize = SPECS[kind]
    unknown = sorted(set(raw) - set(COMMON_KEYS) - set(keys))
    if unknown:
        problems.append(f"unknown key(s) for {kind}: {', '.join(unknown)}")
    spec: Dict[str, Any] = {"type": kind}
    if raw.get("title") is not None:
        spec["title"] = _text(raw["title"], "title", problems, TITLE_MAX)
    spec.update(normalize(raw, problems))
    return spec, problems


def validate_visual(raw: Any) -> Problems:
    return check_visual(raw)[1]
