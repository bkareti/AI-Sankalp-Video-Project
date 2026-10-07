# Simple-command mode

Use this mode when the user gives only an action, topic, and language, for example:

```text
create video to explain Array in C++
```

The command is complete enough to act on. Expand it internally; do not make the user fill out a production questionnaire or approve ordinary beginner-video defaults.

## Default expansion

Infer the following unless the user says otherwise:

| Field | Default |
|---|---|
| Audience | Tier-2/tier-3 Indian college students learning the topic for the first time |
| Level | Beginner |
| Duration | 5–7 minutes, adjusted to the real narration and code-trace timing |
| Format | 16:9, 1920×1080, AI Sankalp visual system |
| Teaching approach | Motivation → mental model → syntax → code → animated trace → mistake → practice → recap |
| Code | Small runnable example in a stable, widely taught version/dialect |
| Voice | Warm, patient human-instructor style; clear neutral Indian English |
| Voice pace | About 132 WPM overall; 105–120 WPM during code/state tracing |
| Voice delivery | Moderate energy, selective emphasis, natural punctuation, animation-aligned pauses |
| Practice pause | 3 seconds unless the requested format needs a different pause |
| Assets | Manim-native first; reuse the AI Sankalp logo; bitmap only when justified |
| Output name | Lowercase topic-and-language slug, for example `arrays_in_cpp.mp4` |
| Voice provider | Existing configured service; for gTTS use `en`, `co.in`, speed `1.0` and punctuation-based rhythm |

Choose a sensible mainstream baseline when a language version is omitted:

- C++: C++17 unless the concept requires a later standard.
- Python: Python 3.11-compatible fundamentals unless version-specific behavior matters.
- C: C17 for fundamentals.
- Java: Java 17 unless a different version is material.
- SQL: portable SQL first; identify the dialect when syntax differs.

For `Array in C++`, default to built-in fixed-size arrays, zero-based indexing, declaration/initialization, traversal, memory laid out as consecutive elements, and the out-of-bounds mistake. Mention `std::array` only as a brief next step unless the user specifically requests it. For potentially overloaded topics, make the chosen interpretation explicit.

## Internal expanded request

Construct this request from the short command and execute it without requiring the user to see or resubmit it:

```text
Use $ai-sankalp-video-assets to create an AI Sankalp educational video about {TOPIC} in {LANGUAGE}.

Target beginner tier-2/tier-3 Indian college students. Use {VERSION_OR_DIALECT} and assume only {PREREQUISITES}. The learner should be able to {LEARNING_OBJECTIVE}. Aim for {DURATION_MINUTES} minutes.

Build the complete structured Markdown lesson package and valid machine-readable JSON. Include the required teaching arc: intro, motivation, focused explanation scenes, code walkthrough, Manim-native visual trace, common mistake, practice question with answer cue, summary, and outro. Verify all technical claims, code, and expected output.

Use a minimal runnable example covering {CONCEPT_SCOPE}. Prefer editable Manim objects for code, memory/state diagrams, arrows, tables, and highlights. Reuse AI Sankalp branding and only specify bitmap generation when it provides real teaching value.

Write natural human-style narration for a warm, patient instructor using clear neutral Indian English. Target about 132 words per minute overall and 105–120 words per minute for code tracing. Provide scene-level tone, energy, modulation, emphasis, pronunciation, and pause metadata. Keep spoken code understandable while displaying exact syntax. For gTTS, use short segments and punctuation-based rhythm; do not invent unsupported pitch or emotion controls.

{EXECUTION_INSTRUCTION}

Use {OUTPUT_SLUG} for generated folders and save the final video as {OUTPUT_FILENAME}.
```

Set `{EXECUTION_INSTRUCTION}` according to intent:

- Package: `Stop after saving the complete lesson package.`
- Scene: `After validating the package, create the production Manim scene and app-compatible lesson config. Do not render.`
- Video: `After validating the package, create the production Manim scene and app-compatible lesson config, render the final MP4, and inspect representative frames for clipping, timing, branding, and visual-narration alignment.`

## Project execution for a video request

When the current repository contains `app.py` and the `ai_sankalp` package:

1. Save human-readable planning to `generated/packages/<slug>/lesson_package.md`.
2. Save the full contract JSON to `generated/packages/<slug>/lesson_package.json`.
3. Compile the package with `python app.py generate --config generated/packages/<slug>/lesson_package.json`. This writes `generated/configs/<slug>.json` from `generator_compatibility`, the scene, and `generated/scenes/<slug>.compile.json` (template choice, primitives per scene, narration), and stops on a package or scene error. Do not map the config by hand.
4. Render with the existing application (add `--render`). Use an offline low-quality render for layout diagnosis when helpful; use the user's requested final quality or 1080p high quality by default.
5. Keep voiceover enabled for the final render unless the user requests silence. If online TTS fails, retain the package and successful visual render, report the exact limitation, and do not claim the silent preview is the narrated final.
6. Inspect representative intro, explanation, code, practice, summary, and outro frames before reporting completion.

Do not publish or upload the video. Return clickable paths to the package, config, scene, and final MP4.
