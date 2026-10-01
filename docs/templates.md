# Visual templates and primitives

AI Sankalp videos are built from **primitives**: reusable, data-driven Manim
building blocks. A lesson picks primitives through data, never by editing scene
code. Every primitive takes its text and values from JSON, uses the brand kit
(`ai_sankalp/brand.py`), and stays inside the safe area above the caption band.

## Where primitives are used

| Template | How it picks primitives |
|---|---|
| `futuristic_array` (flagship) | Each package scene lists up to three `visuals`. A scene without `visuals` gets a default by its `type` (see below). |
| `standard` | A section may add one `visual`. Only the "standard-compatible" primitives below are allowed there. |

A package scene visual (`scenes[].visuals[]`) accepts these common keys:

- `type` (required): the primitive name.
- `label`: small eyebrow text, such as `"02 / MENTAL MODEL"`. Defaults to the scene number and type.
- `title`: the slide heading. Defaults to the scene title.
- `timing`:
  - `"narrated"` (default) spreads the primitive's beats across the scene's narration, one beat per sentence.
  - `"after_narration"` plays the beats after the narration at 0.7 s each.

When a primitive has more beats than the narration has sentences, the extra beats
share the last sentence, so no animation is dropped. Narration sentences
without a beat hold the frame with a slow ambient motion.

## Catalog

Unless stated otherwise, "values" are 1–8 short scalars (each at most 6 characters).

| Primitive | Standard-compatible | Parameters | Beats |
|---|---|---|---|
| `title_card` | no | `heading`; optional `eyebrow`, `subtitle`, `lane_values` | 2, or 4 with a lane |
| `outro_card` | no | `heading`; optional `subtitle`, `next_step` | 1 + subtitle + 2 for `next_step` |
| `bullet_card` | no | `bullets` (1–5 lines) | 1 |
| `card_merge` | no | `cards` (2–8), `target_name`, `target_values`; optional `callout` | 5, or 6 with a callout |
| `array_lane` | yes | `values`; optional `name`, `show_indexes` (default true), `addresses` `{start, step}`, `chips` (1–3) | 3 to 7: each chip after the first, and `addresses`, add beats |
| `token_breakdown` | no | `tokens` (2–5 `{text, role}`), `code_line`; optional `values`, `highlight_index` | 3 + tokens + lane + flash |
| `index_access` | no | `values`, `index`, `access_label`, `result_label`; optional `offset_label` | 8 |
| `code_walkthrough` | no | optional `code_example_id` (default: the scene's first `code_example_ids`), `steps` (0–4), `language` | 5 + steps, or 3 without steps |
| `loop_trace` | yes | `values`; optional `variable` (default `i`), `variable_values` (default: indexes), `outputs`, `output_title`, `stop_label` | 3 + values + 2 for `stop_label` |
| `bounds_check` | no | `values`, `ghost_label`, `wrong_label`, `correct_label`, `warning` | 9 |
| `practice_reveal` | no | `values`, `question`, `answer`, `highlight_index`; optional `countdown` (0–5, default 3) | 6, or 5 without a countdown |
| `concept_map` | yes | `center`, `nodes` (2–4) | 1 + nodes + 2 |
| `flow` | yes | `items` (2–5) | 1 |
| `steps` | yes | `items` (2–5) | 1 |
| `compare` | yes | `left` and `right`: `{title, items (1–4)}` | 1 |
| `table` | yes | `columns` (1–4), `rows` (1–6) | 1 |

The exact rules and beat counts live in `ai_sankalp/primitives/specs.py`. That
module is pure Python, so configs can be validated without Manim. Invalid
parameters fail at load or generate time with a path, for example
`scenes[5].visuals[0]: values must have 1 to 8 items (got 0)`.

## Defaults by scene type

| Scene `type` | Default primitive |
|---|---|
| `intro` | `title_card` from the package title, language and topic |
| `outro` | `outro_card` from `on_screen_text` |
| `code_walkthrough` | `code_walkthrough` of the scene's first code example |
| `summary` (with 2+ `on_screen_text` lines) | `concept_map` around the topic |
| anything else | `bullet_card` from `on_screen_text` |

## Example

From `examples/arrays_in_cpp/lesson_package.json`:

```json
{
  "type": "loop_trace",
  "label": "06 / LIVE TRACE",
  "title": "Follow i as the data flows",
  "values": ["70", "85", "90", "75", "88"],
  "variable": "i",
  "output_title": "OUTPUT STREAM",
  "stop_label": "i = 5  →  STOP"
}
```

## Fixtures and smoke renders

Every primitive has a small fixture in `examples/primitives/<type>.json`. Each
fixture holds `narration`, `language`, `visual`, and `code_examples` where
needed. `scenes/primitive_smoke.py` turns each fixture into a silent scene.

```bash
.venv/bin/python scenes/primitive_smoke.py                       # list smoke scenes
.venv/bin/python -m manim -ql scenes/primitive_smoke.py LoopTraceSmoke
```

## Adding a primitive

1. Add its parameters, normalizer, and beat count to `ai_sankalp/primitives/specs.py`.
2. Write a builder `(spec, ctx) -> BuiltVisual` that takes all text from the spec, and register it in `ai_sankalp/primitives/registry.py`.
3. Add the type to the `sceneVisual` enum in `templates/lesson_package.schema.json`. If it is standard-compatible, also add it to `STANDARD_COMPATIBLE` and to the `visual` enum in both schemas.
4. Add `examples/primitives/<type>.json` and run its smoke render.
5. Run the tests. `tests/test_primitives.py` checks that the registry, schemas, fixtures, beat counts, and safe-area bounds all agree.
