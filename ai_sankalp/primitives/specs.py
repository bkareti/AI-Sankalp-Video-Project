"""Visual specs: validation, normalization, and beat counts without Manim.

A visual spec is a flat JSON object, for example::

    {"type": "flow", "title": "One pass of the loop",
     "items": ["Take next item", "Run the body", "Repeat"]}

`type` selects the primitive; every other key is a primitive parameter.
Specs appear in two places:

- reduced configs: ``sections[].visual`` (context ``"section"``), limited to
  the primitives in ``STANDARD_COMPATIBLE``;
- lesson packages: ``scenes[].visuals[]`` (context ``"scene"``), where
  ``label`` (eyebrow text) and ``timing`` are also accepted.

Each primitive reveals itself in a fixed number of animation "beats";
``beat_count`` must match the builders in ``ai_sankalp/primitives``.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

TITLE_MAX = 48
ITEM_MAX = 60
CELL_MAX = 24
COMPARE_ITEM_MAX = 40
# Total characters across one table row; each cell gets an equal share.
TABLE_TEXT_BUDGET = 48
VALUE_MAX = 6
TIMINGS = ("narrated", "after_narration")

Problems = List[str]
Spec = Dict[str, Any]


# --- field readers -------------------------------------------------------------
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


def _spaced(value: Any, where: str, problems: Problems, limit: int = ITEM_MAX) -> str:
    """Like _text, but keeps intentional runs of spaces ("i = 5  →  STOP")."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        problems.append(f"{where} must be text")
        return ""
    text = str(value).strip()
    if not text:
        problems.append(f"{where} must not be empty")
    elif len(text) > limit:
        problems.append(f"{where} must be at most {limit} characters (got {len(text)})")
    return text


def _text_list(value: Any, where: str, problems: Problems, low: int, high: int, limit: int = ITEM_MAX,
               reader: Callable[..., str] = _text) -> List[str]:
    if not isinstance(value, list):
        problems.append(f"{where} must be a list of {low} to {high} text items")
        return []
    if not low <= len(value) <= high:
        problems.append(f"{where} must have {low} to {high} items (got {len(value)})")
    return [reader(item, f"{where}[{index}]", problems, limit) for index, item in enumerate(value)]


def _values(value: Any, where: str, problems: Problems, low: int = 1, high: int = 8) -> List[str]:
    return _text_list(value, where, problems, low, high, VALUE_MAX)


def _optional(raw: Spec, key: str, reader: Callable[..., Any], problems: Problems, *args: Any) -> Any:
    return reader(raw[key], key, problems, *args) if raw.get(key) is not None else None


def _integer(value: Any, where: str, problems: Problems, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        problems.append(f"{where} must be a whole number")
        return low
    if not low <= value <= high:
        problems.append(f"{where} must be between {low} and {high} (got {value})")
    return value


def _boolean(value: Any, where: str, problems: Problems) -> bool:
    if not isinstance(value, bool):
        problems.append(f"{where} must be true or false")
        return True
    return value


def _index_into(raw: Spec, key: str, values: List[str], problems: Problems, required: bool = True) -> Optional[int]:
    if raw.get(key) is None:
        if required:
            problems.append(f"{key} is required")
        return None
    return _integer(raw[key], key, problems, 0, max(0, len(values) - 1))


# --- per-type normalizers -------------------------------------------------------
def _items(raw: Spec, problems: Problems) -> Spec:
    return {"items": _text_list(raw.get("items"), "items", problems, 2, 5)}


def _compare(raw: Spec, problems: Problems) -> Spec:
    result: Spec = {}
    for side in ("left", "right"):
        column = raw.get(side)
        if not isinstance(column, dict):
            problems.append(f"{side} must be an object with title and items")
            continue
        unknown = sorted(set(column) - {"title", "items"})
        if unknown:
            problems.append(f"{side} has unknown key(s): {', '.join(unknown)}")
        result[side] = {
            "title": _text(column.get("title"), f"{side}.title", problems, TITLE_MAX),
            "items": _text_list(column.get("items"), f"{side}.items", problems, 1, 4, COMPARE_ITEM_MAX),
        }
    return result


def _table(raw: Spec, problems: Problems) -> Spec:
    before = len(problems)
    columns = _text_list(raw.get("columns"), "columns", problems, 1, 4, CELL_MAX)
    columns_ok = len(problems) == before
    # Narrower cells as columns are added keep table text readable at 480p.
    cell_limit = TABLE_TEXT_BUDGET // max(1, len(columns))
    for index, column in enumerate(columns):
        if len(column) > cell_limit:
            problems.append(f"columns[{index}] must be at most {cell_limit} characters with {len(columns)} columns")
    raw_rows = raw.get("rows")
    rows: List[List[str]] = []
    if not isinstance(raw_rows, list) or not 1 <= len(raw_rows) <= 6:
        problems.append("rows must be a list of 1 to 6 rows")
        raw_rows = raw_rows if isinstance(raw_rows, list) else []
    if not columns_ok:
        return {"columns": columns, "rows": rows}
    for index, row in enumerate(raw_rows):
        if not isinstance(row, list) or len(row) != len(columns):
            problems.append(f"rows[{index}] must have exactly {len(columns)} cell(s), one per column")
            continue
        rows.append([
            _text(cell, f"rows[{index}][{cell_index}]", problems, min(CELL_MAX, cell_limit))
            for cell_index, cell in enumerate(row)
        ])
    return {"columns": columns, "rows": rows}


def _title_card(raw: Spec, problems: Problems) -> Spec:
    return {
        "eyebrow": _optional(raw, "eyebrow", _spaced, problems, TITLE_MAX),
        "heading": _spaced(raw.get("heading"), "heading", problems, TITLE_MAX),
        "subtitle": _optional(raw, "subtitle", _spaced, problems, ITEM_MAX),
        "lane_values": _optional(raw, "lane_values", _values, problems),
    }


def _card_merge(raw: Spec, problems: Problems) -> Spec:
    return {
        "cards": _text_list(raw.get("cards"), "cards", problems, 2, 8, CELL_MAX, _spaced),
        "callout": _optional(raw, "callout", _spaced, problems, TITLE_MAX),
        "target_name": _text(raw.get("target_name"), "target_name", problems, CELL_MAX),
        "target_values": _values(raw.get("target_values"), "target_values", problems),
    }


def _array_lane(raw: Spec, problems: Problems) -> Spec:
    addresses = raw.get("addresses")
    normalized_addresses = None
    if addresses is not None:
        if not isinstance(addresses, dict) or set(addresses) != {"start", "step"}:
            problems.append("addresses must be an object with start and step")
        else:
            normalized_addresses = {
                "start": _integer(addresses["start"], "addresses.start", problems, 0, 10 ** 9),
                "step": _integer(addresses["step"], "addresses.step", problems, 1, 1024),
            }
    return {
        "name": _optional(raw, "name", _text, problems, CELL_MAX),
        "values": _values(raw.get("values"), "values", problems),
        "show_indexes": _boolean(raw.get("show_indexes", True), "show_indexes", problems),
        "addresses": normalized_addresses,
        "chips": _optional(raw, "chips", lambda v, w, p: _text_list(v, w, p, 1, 3, 32, _spaced), problems),
    }


def _token_breakdown(raw: Spec, problems: Problems) -> Spec:
    tokens: List[Dict[str, str]] = []
    raw_tokens = raw.get("tokens")
    if not isinstance(raw_tokens, list) or not 2 <= len(raw_tokens) <= 5:
        problems.append("tokens must be a list of 2 to 5 {text, role} objects")
        raw_tokens = raw_tokens if isinstance(raw_tokens, list) else []
    for index, token in enumerate(raw_tokens):
        if not isinstance(token, dict) or set(token) != {"text", "role"}:
            problems.append(f"tokens[{index}] must be an object with text and role")
            continue
        tokens.append({
            "text": _text(token["text"], f"tokens[{index}].text", problems, CELL_MAX),
            "role": _text(token["role"], f"tokens[{index}].role", problems, 20),
        })
    values = _optional(raw, "values", _values, problems)
    return {
        "tokens": tokens,
        "code_line": _text(raw.get("code_line"), "code_line", problems),
        "values": values,
        "highlight_index": _index_into(raw, "highlight_index", values or [], problems, required=False)
        if values else None,
    }


def _index_access(raw: Spec, problems: Problems) -> Spec:
    values = _values(raw.get("values"), "values", problems)
    return {
        "values": values,
        "index": _index_into(raw, "index", values, problems),
        "access_label": _spaced(raw.get("access_label"), "access_label", problems, CELL_MAX),
        "result_label": _spaced(raw.get("result_label"), "result_label", problems, CELL_MAX),
        "offset_label": _optional(raw, "offset_label", _spaced, problems, 32),
    }


def _code_walkthrough(raw: Spec, problems: Problems) -> Spec:
    return {
        "code_example_id": _optional(raw, "code_example_id", _text, problems, 64),
        "steps": _text_list(raw.get("steps", []), "steps", problems, 0, 4, CELL_MAX, _spaced),
        "language": _optional(raw, "language", _text, problems, 24),
    }


def _loop_trace(raw: Spec, problems: Problems) -> Spec:
    values = _values(raw.get("values"), "values", problems)
    outputs = _optional(raw, "outputs", lambda v, w, p: _text_list(v, w, p, 1, 8, 10), problems)
    if outputs is not None and len(outputs) != len(values):
        problems.append(f"outputs must have one entry per value ({len(values)})")
    variable_values = _optional(raw, "variable_values", lambda v, w, p: _text_list(v, w, p, 1, 8, VALUE_MAX), problems)
    if variable_values is not None and len(variable_values) != len(values):
        problems.append(f"variable_values must have one entry per value ({len(values)})")
    return {
        "values": values,
        "variable": _text(raw.get("variable", "i"), "variable", problems, 8),
        "variable_values": variable_values,
        "outputs": outputs,
        "output_title": _text(raw.get("output_title", "OUTPUT"), "output_title", problems, 24),
        "stop_label": _optional(raw, "stop_label", _spaced, problems, 32),
    }


def _bounds_check(raw: Spec, problems: Problems) -> Spec:
    return {
        "values": _values(raw.get("values"), "values", problems),
        "ghost_label": _text(raw.get("ghost_label"), "ghost_label", problems, VALUE_MAX),
        "wrong_label": _spaced(raw.get("wrong_label"), "wrong_label", problems, CELL_MAX),
        "correct_label": _spaced(raw.get("correct_label"), "correct_label", problems, CELL_MAX),
        "warning": _text(raw.get("warning"), "warning", problems, 32),
    }


def _practice_reveal(raw: Spec, problems: Problems) -> Spec:
    values = _values(raw.get("values"), "values", problems)
    return {
        "values": values,
        "question": _spaced(raw.get("question"), "question", problems),
        "answer": _spaced(raw.get("answer"), "answer", problems),
        "highlight_index": _index_into(raw, "highlight_index", values, problems),
        "countdown": _integer(raw.get("countdown", 3), "countdown", problems, 0, 5),
    }


def _concept_map(raw: Spec, problems: Problems) -> Spec:
    return {
        "center": _text(raw.get("center"), "center", problems, 20),
        "nodes": _text_list(raw.get("nodes"), "nodes", problems, 2, 4, CELL_MAX),
    }


def _outro_card(raw: Spec, problems: Problems) -> Spec:
    return {
        "heading": _spaced(raw.get("heading"), "heading", problems, TITLE_MAX),
        "subtitle": _optional(raw, "subtitle", _spaced, problems, ITEM_MAX),
        "next_step": _optional(raw, "next_step", _spaced, problems, TITLE_MAX),
    }


def _bullet_card(raw: Spec, problems: Problems) -> Spec:
    return {"bullets": _text_list(raw.get("bullets"), "bullets", problems, 1, 5)}


Normalizer = Callable[[Spec, Problems], Spec]
# type -> (parameter keys, normalizer)
SPECS: Dict[str, Tuple[Tuple[str, ...], Normalizer]] = {
    "flow": (("items",), _items),
    "steps": (("items",), _items),
    "compare": (("left", "right"), _compare),
    "table": (("columns", "rows"), _table),
    "title_card": (("eyebrow", "heading", "subtitle", "lane_values"), _title_card),
    "card_merge": (("cards", "callout", "target_name", "target_values"), _card_merge),
    "array_lane": (("name", "values", "show_indexes", "addresses", "chips"), _array_lane),
    "token_breakdown": (("tokens", "code_line", "values", "highlight_index"), _token_breakdown),
    "index_access": (("values", "index", "access_label", "result_label", "offset_label"), _index_access),
    "code_walkthrough": (("code_example_id", "steps", "language"), _code_walkthrough),
    "loop_trace": (("values", "variable", "variable_values", "outputs", "output_title", "stop_label"), _loop_trace),
    "bounds_check": (("values", "ghost_label", "wrong_label", "correct_label", "warning"), _bounds_check),
    "practice_reveal": (("values", "question", "answer", "highlight_index", "countdown"), _practice_reveal),
    "concept_map": (("center", "nodes"), _concept_map),
    "outro_card": (("heading", "subtitle", "next_step"), _outro_card),
    "bullet_card": (("bullets",), _bullet_card),
}
SPEC_TYPES: Tuple[str, ...] = tuple(SPECS)
# Primitives that also work inside the standard template's visual panel.
STANDARD_COMPATIBLE: Tuple[str, ...] = (
    "flow", "steps", "compare", "table", "array_lane", "loop_trace", "concept_map",
)
# Full-frame cards that draw their own heading instead of the scene header.
NO_HEADER_TYPES = ("title_card", "outro_card")
SECTION_KEYS = ("type", "title")
SCENE_KEYS = ("type", "title", "label", "timing")


def check_visual(raw: Any, context: str = "section") -> Tuple[Spec, Problems]:
    """Return (normalized spec, problems). The spec is only usable when problems is empty."""
    problems: Problems = []
    if not isinstance(raw, dict):
        return {}, ["must be an object with a type"]
    allowed = STANDARD_COMPATIBLE if context == "section" else SPEC_TYPES
    kind = raw.get("type")
    if not isinstance(kind, str) or kind not in allowed:
        return {}, [f"type must be one of: {', '.join(allowed)} (got {kind!r})"]
    keys, normalize = SPECS[kind]
    common = SECTION_KEYS if context == "section" else SCENE_KEYS
    unknown = sorted(set(raw) - set(common) - set(keys))
    if unknown:
        problems.append(f"unknown key(s) for {kind}: {', '.join(unknown)}")
    spec: Spec = {"type": kind}
    if raw.get("title") is not None:
        spec["title"] = _spaced(raw["title"], "title", problems, TITLE_MAX)
    if context == "scene":
        if raw.get("label") is not None:
            spec["label"] = _spaced(raw["label"], "label", problems, 40)
        timing = raw.get("timing", "narrated")
        if timing not in TIMINGS:
            problems.append(f"timing must be one of: {', '.join(TIMINGS)} (got {timing!r})")
        spec["timing"] = timing
    for key, value in normalize(raw, problems).items():
        if value is not None:
            spec[key] = value
    return spec, problems


def validate_visual(raw: Any, context: str = "section") -> Problems:
    return check_visual(raw, context)[1]


def beat_count(spec: Spec) -> int:
    """Number of animation beats the primitive's builder produces."""
    kind = spec["type"]
    if kind in ("flow", "steps", "compare", "table", "bullet_card"):
        return 1
    if kind == "title_card":
        return 4 if spec.get("lane_values") else 2
    if kind == "card_merge":
        return 6 if spec.get("callout") else 5
    if kind == "array_lane":
        chips = len(spec.get("chips") or [])
        addresses = 1 if spec.get("addresses") else 0
        return 2 + max(0, chips - 1) + addresses + (1 if chips or addresses else 0) + 1
    if kind == "token_breakdown":
        values = 1 if spec.get("values") else 0
        flash = 1 if values and spec.get("highlight_index") is not None else 0
        return 2 + len(spec["tokens"]) + 1 + values + flash
    if kind == "index_access":
        return 8
    if kind == "code_walkthrough":
        steps = len(spec.get("steps") or [])
        return 2 + steps + (3 if steps else 1)
    if kind == "loop_trace":
        return 2 + len(spec["values"]) + (2 if spec.get("stop_label") else 0) + 1
    if kind == "bounds_check":
        return 9
    if kind == "practice_reveal":
        return 6 if spec.get("countdown", 3) else 5
    if kind == "concept_map":
        return 1 + len(spec["nodes"]) + min(2, len(spec["nodes"]))
    if kind == "outro_card":
        return 1 + (1 if spec.get("subtitle") else 0) + (2 if spec.get("next_step") else 0)
    raise KeyError(kind)


# --- defaults by scene type -----------------------------------------------------
def _clip(value: Any, limit: int) -> str:
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def scene_label(scene: Dict[str, Any], number: int) -> str:
    return f"{number:02d} / {str(scene.get('type', 'scene')).replace('_', ' ').upper()}"


def default_visual_for_scene(scene: Dict[str, Any], package: Dict[str, Any]) -> Spec:
    """A sensible primitive for a scene that does not list explicit visuals."""
    kind = scene.get("type")
    texts = [_clip(item, ITEM_MAX) for item in scene.get("on_screen_text") or [] if str(item).strip()]
    title = _clip(scene.get("title") or package.get("title", ""), TITLE_MAX)
    if kind == "intro":
        spec: Spec = {
            "type": "title_card",
            "eyebrow": _clip(f"{package.get('language', '')}  •  {package.get('topic', '')}".upper(), TITLE_MAX),
            "heading": _clip(package.get("title") or title, TITLE_MAX),
        }
        if texts:
            spec["subtitle"] = texts[-1]
        return spec
    if kind == "outro":
        spec = {"type": "outro_card", "heading": _clip(texts[0] if texts else title, TITLE_MAX)}
        if len(texts) > 1:
            spec["subtitle"] = texts[1]
        return spec
    if kind == "code_walkthrough" and (scene.get("code_example_ids") or package.get("code_examples")):
        return {"type": "code_walkthrough", "title": title}
    if kind == "summary" and len(texts) >= 2:
        return {
            "type": "concept_map", "title": title,
            "center": _clip(package.get("topic", "Recap"), 20),
            "nodes": [_clip(item, CELL_MAX) for item in texts[:4]],
        }
    return {"type": "bullet_card", "title": title, "bullets": texts[:5] or [title]}
