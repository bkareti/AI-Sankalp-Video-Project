# AI Sankalp Video Generator

A reusable local Python app that turns a programming topic, explanation, and code example into a branded animated Manim lesson. Lessons are data, not hand-edited scene files: create a JSON/YAML config or fill in the desktop form, then generate and render.

The video template includes an intro, lesson title, step-by-step explanation cards, an animated visual model, syntax-highlighted code, a recap, persistent AI Sankalp branding, optional gTTS narration/subcaptions, and an outro.

## Project structure

```text
app.py                         CLI and desktop-app entry point
ai_sankalp/                    Models, generator, renderer, UI, Manim runtime
templates/generated_scene.py.tmpl
templates/lesson.schema.json   Reduced lesson config format
templates/lesson_package.schema.json  Rich lesson package format
examples/python_for_loops.json Working sample lesson
examples/python_for_loops/     Rich package for the Python sample
examples/arrays_in_cpp/        Flagship C++ arrays sample (reduced config + rich package)
assets/ai_sankalp_logo.svg
generated/
  configs/                     Normalized lesson configs
  scenes/                      Small generated Manim entry points
  audio/                       gTTS voiceover cache
  videos/                      Final MP4 files
  history.jsonl                Generation/render event history
scenes/                        Original hand-authored Manim examples
tests/                         Fast generator/model tests
```

## Requirements

- Python 3.9+
- Manim system libraries
- ffmpeg
- Internet access only when gTTS voiceover is enabled

On macOS, install Manim's common system dependencies first:

```bash
brew install ffmpeg cairo pango
```

Create the environment and install Python packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py check
```

## Use the desktop form

```bash
source .venv/bin/activate
python app.py
```

`python app.py gui` does the same thing. Enter the topic, title, language, explanation, code, filename, voiceover preference, quality, and output folder. Separate explanation steps with a blank line. The first short line in each block becomes its heading.

## Use a one-line Codex command

The installed `$ai-sankalp-video-assets` skill expands a short request into the lesson brief, narration, storyboard, code, visual assets, generator config, Manim scene, and final render:

```text
create video to explain Array in C++
```

`create video` requests the complete local workflow, including rendering and visual inspection. Use `prepare a video package to explain Array in C++` to stop after Markdown and JSON, or `generate a Manim scene to explain Array in C++` to create code without rendering. The reusable expansion template is in `prompts/ai_sankalp_video_request.md`.

## Run the sample

Generate the scene and normalized config without rendering:

```bash
python app.py sample
```

Render a quick preview without internet or narration:

```bash
python app.py sample --render --no-voiceover --quality low
```

Render with gTTS narration:

```bash
python app.py sample --render --quality medium
```

The final file is saved as `generated/videos/python_for_loops.mp4`. gTTS audio is cached in `generated/audio/`.

## Render the flagship C++ arrays sample

The polished `futuristic_array` template renders from a rich lesson package
tracked at `examples/arrays_in_cpp/lesson_package.json`, with a matching
reduced config at `examples/arrays_in_cpp/config.json`. This works from a
clean clone with no prior generation step:

```bash
python app.py generate --config examples/arrays_in_cpp/config.json --render --quality low
```

Add `--no-voiceover` to render it offline without narration.

The final file is saved as `generated/videos/arrays_in_cpp.mp4`. At render
time, the scene looks for a matching package under
`generated/packages/arrays_in_cpp/lesson_package.json` first (useful while
iterating on package content) and falls back to the tracked
`examples/arrays_in_cpp/lesson_package.json` fixture when that generated
copy does not exist, since `generated/packages/*` is not committed to git.

## Create a reusable lesson config

Copy `examples/python_for_loops.json` and change its values. The main format is:

```json
{
  "topic": "SQL joins",
  "title": "Understanding SQL Joins",
  "language": "SQL",
  "sections": [
    {
      "title": "Why joins exist",
      "bullets": [
        "Related data often lives in separate tables.",
        "A join combines rows through a matching column."
      ],
      "narration": "Optional custom words for this section's voiceover."
    }
  ],
  "code_example": "SELECT * FROM students JOIN marks ON students.id = marks.student_id;",
  "summary": ["Joins connect related table rows."],
  "output_video_name": "sql_joins",
  "voiceover": {
    "enabled": true,
    "language": "en",
    "tld": "co.in",
    "speed": 1.0
  }
}
```

`explanation` may be used instead of `sections`. It accepts plain text or a list of bullet strings. JSON and YAML are supported; the complete JSON schema is in `templates/lesson.schema.json`.

Generate or render any config:

```bash
python app.py generate --config lessons/sql_joins.json
python app.py generate --config lessons/sql_joins.json --render --quality low
python app.py generate --config lessons/sql_joins.yaml --render --output-dir output
```

### Lesson config fields

| Field | Required | Notes |
|---|---|---|
| `topic` | yes | Short topic name shown on the intro card. |
| `title` | yes | Lesson title. Older alias: `lesson_title`. |
| `language` | yes | Programming language; also selects code highlighting. Older alias: `programming_language`. |
| `sections` | yes, or `explanation` | List of `{title, bullets, narration?}`. Sections with more than four bullets are split into continued slides. A plain string becomes a one-bullet section. |
| `explanation` | instead of `sections` | Blank-line separated text blocks, or a list of sections. Older alias: `script`. |
| `code_example` | yes | Code shown in the walkthrough. Older alias: `code`. |
| `summary` | no | Up to four recap lines; defaults to the first bullet of the first sections. |
| `output_video_name` | yes | File name for the MP4 (made filesystem-safe). Older alias: `output`. |
| `voiceover` | no | `true`, `false`, or an object (see below). Defaults to gTTS narration. |
| `visual_template` | no | `standard` (default) or `futuristic_array`. |

Unknown keys are ignored. Text fields that contain numbers are converted to text; an empty (null) value counts as missing. `provider` and `visual_template` are case-insensitive. An empty `rate` or `pitch` falls back to its default.

### Visual templates

| Template | Use it for | Needs |
|---|---|---|
| `standard` | Any topic and language. Bullet slides, a code walkthrough, recap and outro, all from the config. | Only the reduced config. |
| `futuristic_array` | The flagship, diagram-first C++ arrays lesson. | A rich lesson package with the ten flagship scene ids, and a C++ array topic. |

`futuristic_array` currently supports only C++ array lessons. The generator
checks this before writing any file or starting Manim: it fails early with a
clear message when the package is missing, invalid, missing a required scene
id, or the lesson is not a C++ array lesson. Use `standard` for everything else.

### Voiceover providers (gTTS vs Edge TTS)

| Field | Provider | Default | Notes |
|---|---|---|---|
| `enabled` | both | `true` | `false` renders silently, with no network access. |
| `provider` | both | `gtts` | `gtts` or `edge`. |
| `speed` | both | `1.0` | Playback speed multiplier, 0.5 to 2.0. |
| `language` | gTTS | `en` | gTTS language code. |
| `tld` | gTTS | `com` | Google domain that sets the accent, e.g. `co.in` for Indian English. |
| `voice` | Edge | `en-IN-NeerjaNeural` | Any Microsoft Edge neural voice name. |
| `rate` | Edge | `+0%` | Signed percentage, e.g. `-4%`. |
| `pitch` | Edge | `+0Hz` | Signed hertz, e.g. `+1Hz`. |
| `human_delivery_notes` | none | | Informational only (used in lesson packages); ignored at render time. |

- **gTTS** (Google Translate speech) is simple and free, but has no pitch or
  emotion control. Audio is cached in `generated/audio/`.
- **Edge TTS** uses Microsoft's neural voices, which sound more natural and
  support `voice`, `rate` and `pitch`. The flagship C++ sample uses
  `en-IN-NeerjaNeural` at `-4%` and `+1Hz`. Audio is cached in
  `generated/audio_edge/`.
- Both providers need internet access while rendering. Both templates honor
  the selected provider. Add `--no-voiceover` to `generate` or `sample` to
  render offline.

## Rich lesson packages

A lesson package (`examples/<slug>/lesson_package.json`) is the full source of
truth for a lesson: scenes, narration, voice direction, code examples, assets,
branding, and a `generator_compatibility` block that converts into the reduced
config above. Its contract is `templates/lesson_package.schema.json`, plus
cross-reference checks (scene ids, asset ids, code example ids, and
`generator_compatibility.output_video_name` equal to `slug`).

Tracked packages:

- `examples/arrays_in_cpp/lesson_package.json` (flagship, `futuristic_array`)
- `examples/python_for_loops/lesson_package.json` (`standard`)

Pass a package straight to `generate`; it is detected, validated, and converted:

```bash
python app.py generate --config examples/arrays_in_cpp/lesson_package.json
python app.py generate --config examples/python_for_loops/lesson_package.json --render --no-voiceover
```

When you pass a package path with `--config`, the generated scene is pinned to
that file. Otherwise (a reduced config with `futuristic_array`), the scene
looks up the package by slug at render time, preferring
`generated/packages/<slug>/lesson_package.json` over `examples/<slug>/`.

Invalid packages fail with field paths such as
`scenes[3].voiceover: is required` or
`voiceover_segments[2].scene_id: 'scene_99' does not match any scenes[].id`.

For a prompt-based terminal workflow:

```bash
python app.py interactive
```

## History and troubleshooting

Show recent jobs:

```bash
python app.py history
python app.py history --limit 50
```

Every generation, render start, success, and failure is appended to `generated/history.jsonl`. A render failure includes Manim's useful tail output. Network/gTTS failures suggest either restoring internet access or disabling voiceover. Missing Python packages and ffmpeg are checked before rendering:

```bash
python app.py check
```

If a narrated render fails, first confirm that `https://translate.google.com` is reachable. To keep working offline, set `"voiceover": false` or use `--no-voiceover` with `sample` or `generate`.

## Direct Manim rendering

After generating a scene, it remains a normal Manim entry point. The CLI prints its class name, so it can also be rendered directly:

```bash
manim -ql generated/scenes/python_for_loops.py PythonForLoopsScene
```

Using `app.py ... --render` is preferred because it also manages the final output location and history.

## Verification

Run the fast tests and the existing Manim health check:

```bash
python -m unittest discover -s tests -v
manim -ql scenes/smoke_test.py SmokeTest
```

## Extending the app

The main extension points are deliberately separate:

- Add a voice provider in `ai_sankalp/speech.py` and the `provider` enum in both schemas.
- Add a visual template as a runtime scene class registered in `ai_sankalp/template_registry.py` (routing and prerequisite checks), then update the schema enum and tests.
- Add subtitles from Manim Voiceover's generated subcaptions.
- Build a web UI over `LessonGenerator` and `ManimRenderer` without changing the lesson format.
- Add batch generation by loading multiple configs and calling the same generator/renderer APIs.

The original hand-authored scenes remain in `scenes/` as visual references; new routine lessons should use the generator.
