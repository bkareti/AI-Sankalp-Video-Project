# AI Sankalp one-line video request

Users can request a complete lesson video with one sentence:

```text
create video to explain {TOPIC} in {LANGUAGE}
```

Examples:

```text
create video to explain Array in C++
create video to explain for loops in Python
create video to explain joins in SQL
```

Codex should invoke `$ai-sankalp-video-assets`, infer the normal beginner-video defaults, construct the full lesson prompt internally, and complete the requested workflow. The user does not need to supply audience, duration, scene list, code, narration directions, asset list, file names, or render settings unless they want to override a default.

## Expansion template

```text
Use $ai-sankalp-video-assets to create an AI Sankalp educational video about {TOPIC} in {LANGUAGE}.

Target beginner tier-2/tier-3 Indian college students. Use {VERSION_OR_DIALECT} and assume only {PREREQUISITES}. The learner should be able to {LEARNING_OBJECTIVE}. Aim for {DURATION_MINUTES} minutes.

Create the complete Markdown lesson package and valid JSON configuration. Include an intro, motivation, focused explanations, minimal runnable code, code walkthrough, animated visual trace, common mistake, practice question, summary, and outro. Verify technical claims, code, and expected output.

Use AI Sankalp branding and prefer Manim-native visuals. Write natural narration for a warm, patient instructor using clear neutral Indian English. Target approximately 132 WPM overall and 105–120 WPM during code tracing. Include tone, energy, modulation, emphasis, pronunciation, and pause metadata. Use gTTS-compatible segmentation and punctuation when gTTS is selected.

After validating the package, create the app-compatible config and production Manim scene. Render a 1080p MP4 with voiceover, inspect representative frames, and save it as {OUTPUT_FILENAME} under the generated video folder. Do not publish or upload it.
```

Defaults and topic-specific interpretation rules live in the installed skill at `references/simple-command-mode.md`.
