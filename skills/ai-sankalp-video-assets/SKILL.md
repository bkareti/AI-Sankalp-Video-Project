---
name: ai-sankalp-video-assets
description: Prepare or produce complete beginner-friendly AI Sankalp programming videos from a topic, code example, rough script, or one-line request such as "create video to explain arrays in C++." Use for lesson planning, assets, Manim storyboards, or an explicitly requested end-to-end video. Do not use for general explanations with no video deliverable or render-only requests.
---

# AI Sankalp Video Assets

Create a production-ready lesson package that a junior team member can reliably convert into an AI Sankalp Manim video. Produce content and asset specifications by default; do not render a video, generate a full production Manim scene, or create bitmap files unless the user explicitly asks.

## Expand simple commands

Treat a short command such as `create video to explain Array in C++` as sufficient input. Do not ask the user to restate the long production prompt. Read [references/simple-command-mode.md](references/simple-command-mode.md), infer its documented defaults, state consequential assumptions in the lesson brief, and proceed.

Determine the requested stopping point from the verb:

- `plan`, `prepare`, `storyboard`, or `create package`: produce the Markdown and JSON lesson package only.
- `generate scene` or `create Manim script`: produce the package and implementation, but do not render.
- `create video`, `generate video`, `make video`, or an explicit request for an MP4: produce the package, generate the Manim implementation, render the video, and visually inspect representative frames.

The words `create video` explicitly authorize local scene/config generation and rendering for this project. They do not authorize unrelated publishing, uploading, or external sharing. Use the requested topic and language; infer audience, runtime, lesson scope, duration, examples, narration style, file names, and visual treatment. Ask a question only when ambiguity would materially change technical correctness, such as whether “arrays in Python” means lists, NumPy arrays, or `array.array` and the surrounding context does not resolve it.

When the AI Sankalp project is available, save the full package under `generated/packages/<slug>/`, derive the app-compatible config from `generator_compatibility`, and use the existing generator instead of recreating its branding or render pipeline. Preserve the rich package JSON separately from the reduced render config.

## Establish the lesson

Use the supplied material as authoritative. Preserve the user's topic, code, intended scope, language/version, audience, and desired duration. When details are absent, make conservative assumptions and state them briefly in the lesson brief instead of blocking progress.

- Default audience: tier-2/tier-3 Indian college students encountering the concept for the first time.
- Default level: beginner. Raise it only when the topic or request clearly requires prior expertise.
- Set prerequisites narrowly; do not turn them into an extra lesson.
- Express one observable learning objective: what the learner should understand, trace, predict, or implement after watching.
- Estimate duration from the actual narration and scene timings. Aim for roughly 125–145 spoken words per minute, allowing additional time for code tracing and visual pauses.

Verify technical claims and code before presenting them. Distinguish a simplified teaching model from exact runtime behavior. If a claim depends on a language version, implementation, or database dialect, name that boundary. Use authoritative documentation when facts are uncertain or version-sensitive.

## Design the teaching arc

Build a coherent sequence containing these scene roles:

1. Intro
2. Concept motivation
3. Main explanation, split into as many focused scenes as needed
4. Code walkthrough
5. Visual animation or trace
6. Common mistake
7. Practice question
8. Summary
9. Outro

Keep each scene focused on one teaching job. Motivate the problem before introducing syntax. Reveal state changes in the same order the narration describes them. The practice scene should be answerable using only the lesson, and should include a short answer or answer cue for the production team.

Write voiceover in short, natural sentences. Prefer concrete language and define necessary terminology on first use. Use analogies only when their mapping to the technical concept is explicit; state where an analogy stops being exact if misunderstanding is plausible. Indian college examples such as marks, placement shortlists, lab queues, attendance, or canteen orders are useful when natural, but avoid forced cultural references and stereotypes.

## Shape a human teaching voice

Write for a patient instructor explaining at a whiteboard, not for an announcer reading documentation. Unless the user specifies another voice, use a warm, confident, gender-neutral teaching persona with clear neutral Indian English pronunciation.

- Use natural transitions such as “Now watch what changes” or “Here is the important part” only where they guide attention. Do not repeat the same transition formula.
- Prefer one idea per sentence and contractions where they sound natural. Avoid fragments, dense noun phrases, robotic numbered narration, marketing language, and fake conversational fillers.
- Let visuals carry detail. The voiceover should explain meaning instead of reading every word already visible on screen.
- Speak code for understanding rather than reciting punctuation. For example, say “C plus plus,” “the value at index two,” or “range from one to six,” while keeping exact syntax on screen. Add pronunciation notes for identifiers, acronyms, symbols, and domain terms that a speech engine may misread.
- Use measured modulation: calm energy for setup, slightly stronger emphasis for the key rule, slower pace during code tracing, a genuine thinking pause for practice, and a concise upbeat recap. Avoid exaggerated pitch changes or constant emphasis.

Set a global target pace and refine it per scene:

- Intro and outro: 135–145 words per minute, welcoming but brief.
- Motivation and explanation: 125–138 words per minute.
- Code walkthrough and visual trace: 105–125 words per minute, with pauses aligned to highlights and state changes.
- Common mistake: 115–130 words per minute, with the incorrect and corrected states clearly separated.
- Practice: 110–125 words per minute, followed by a 2–4 second thinking pause when the format permits.
- Summary: 130–145 words per minute with slightly higher energy.

Keep most voiceover segments between one and three sentences so animation cues can synchronize cleanly. Provide pace, tone, energy, emphasis words, pronunciation notes, and pause guidance as delivery metadata; keep the record-ready `text` free of bracketed stage directions.

Treat speech controls as provider capabilities, not promises. The current gTTS path supports language/domain selection and a global speed multiplier, but not reliable per-word pitch, emotion, or SSML modulation. For gTTS, create human rhythm with sentence boundaries, commas, segment length, and timed pauses; keep `generator_compatibility.voiceover.speed` near `1.0` unless the user asks otherwise. Put richer modulation guidance in provider-neutral metadata for a future neural or recorded-human voice. Do not emit unsupported gTTS parameters.

## Prepare code

Provide the smallest runnable example that demonstrates the objective. Keep unrelated syntax out of the main example.

- State the required language/runtime or SQL dialect when relevant.
- Explain the example in execution order, not merely line order when those differ.
- Include exact expected output. If output is nondeterministic, label it as representative and explain why.
- Identify beginner mistakes that are genuinely plausible for this example.
- Add one practice variation that changes a single meaningful dimension.
- Never silently repair user-supplied code. Show the correction and explain it when the input is invalid.

## Choose visuals and assets

Prefer native Manim objects for programming ideas: text, code panels, arrays, pointers, stack frames, trees, graphs, tables, arrows, highlights, braces, flowcharts, database rows, timelines, and state transitions. These remain crisp, editable, and synchronized with narration.

Use a bitmap only when a concept materially benefits from an illustration that would be awkward or ineffective to construct in Manim. For every bitmap, provide a generation prompt specifying subject, composition, palette, 16:9 context, clean character-free educational style, no embedded text, and sufficient empty space for labels. Do not request a bitmap for code, flowcharts, tables, memory diagrams, or UI-like panels that Manim can draw directly.

Classify every asset as exactly one of:

- `manim`: construct directly from Manim primitives.
- `reuse`: use an existing supplied asset, such as the AI Sankalp logo.
- `generate`: create a new bitmap only when justified.

Apply the established visual system unless the user supplies another template:

- Background `#071321`; panels `#10243A` and `#16324F`.
- Primary blue `#1473E6`; cyan `#21D4FD`; mint `#55E6C1`; gold `#FFC857`.
- Main text `#F5F9FF`; muted text `#9EB3C7`; warning accent `#FF6B6B`.
- 16:9 at 1920×1080, strong contrast, generous safe margins, and readable code at normal playback size.
- Keep the AI Sankalp logo in the upper-right safe area and the `AI SANKALP • VISUAL LEARNING` footer unobtrusive. Use `assets/ai_sankalp_logo.svg` when the project supplies it.
- Do not rely on color alone to communicate meaning; pair color with labels, shape, position, or motion.

## Deliver the package

Read [references/output-contract.md](references/output-contract.md) before producing the deliverable. Follow its Markdown section order and JSON field contract. Keep the Markdown useful to humans and the JSON self-contained for machines; do not replace one with the other.

The JSON must be valid JSON, not JSON5: use double quotes, escape code newlines, use `null` rather than comments or placeholders, and include every required top-level field. Keep IDs stable and cross-reference scenes, assets, code examples, and voiceover segments by those IDs.

Do not expose unsupported certainty. Mark an assumption as an assumption, a representative output as representative, and an optional asset as optional. End with the quality checklist completed as pass, needs review, or not applicable, with a brief note for anything other than pass.

If the user explicitly asks for implementation, use the completed package as the source of truth. Generate the Manim script only after the package is internally consistent. Render only when the user explicitly requests rendering, including through the simple-command verbs above, and report voiceover/network limitations before relying on an online speech service.
