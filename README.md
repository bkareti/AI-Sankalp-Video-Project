# AI Sankalp Video Generator

A reusable local Python app that turns a programming topic, explanation, and code example into a branded animated Manim lesson. Lessons are data, not hand-edited scene files: create a JSON/YAML config or fill in the desktop form, then generate and render.

The video template includes an intro, lesson title, step-by-step explanation cards, an animated visual model, syntax-highlighted code, a recap, persistent AI Sankalp branding, optional gTTS narration/subcaptions, and an outro.

## Project structure

```text
app.py                         CLI and desktop-app entry point
ai_sankalp/                    Models, generator, renderer, UI, Manim runtime
templates/generated_scene.py.tmpl
templates/lesson.schema.json   Reusable lesson format
examples/python_for_loops.json Working sample lesson
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

If a narrated render fails, first confirm that `https://translate.google.com` is reachable. To keep working offline, set `"voiceover": false` or use `--no-voiceover` for the sample.

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

- Add a voice provider behind the speech-service setup in `ai_sankalp/manim_scene.py`.
- Add new visual templates as runtime scene classes and select one from lesson config.
- Add subtitles from Manim Voiceover's generated subcaptions.
- Build a web UI over `LessonGenerator` and `ManimRenderer` without changing the lesson format.
- Add batch generation by loading multiple configs and calling the same generator/renderer APIs.

The original hand-authored scenes remain in `scenes/` as visual references; new routine lessons should use the generator.
