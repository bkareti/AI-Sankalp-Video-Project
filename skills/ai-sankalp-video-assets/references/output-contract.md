# AI Sankalp lesson-package contract

Use this contract whenever producing a package with the `ai-sankalp-video-assets` skill.

## Markdown document order

### 1. Lesson brief

Include topic, target audience, prerequisites, learning objective, estimated duration, difficulty, language/runtime or dialect, and explicit assumptions.

### 2. Teaching script

Present the scene-by-scene narration in playback order. Use one subsection per scene and keep the words ready to record. Do not replace narration with production notes.

Begin this section with a compact voice direction card: persona, accent/language, target pace, tone, energy range, modulation approach, and pronunciation dictionary. For every scene, separate the exact record-ready text from delivery notes. Do not place stage directions inside the spoken text.

### 3. Scene plan

Use a compact table with scene ID, type, purpose, and estimated duration. Include intro, motivation, main explanation, code walkthrough, visual trace, common mistake, practice, summary, and outro. Multiple main-explanation scenes are allowed.

### 4. Manim-ready storyboard

For every scene include:

- Scene title and type
- Voiceover text
- On-screen text
- Visual objects
- Animation sequence/notes
- Code snippet or code-example reference, if any
- Timing guidance in seconds
- Voice delivery: pace, tone, energy, emphasis, pronunciation, and intentional pauses
- Transition to the next scene

The displayed content and animation must match what the voiceover is discussing at that moment.

### 5. Visual asset requirements

Use a table with asset ID, name, purpose, suggested filename, strategy (`manim`, `reuse`, or `generate`), format, and description. Follow the table with construction notes for Manim assets. Include an image-generation prompt only for `generate` assets; otherwise write `Not needed`.

Always include the reusable AI Sankalp logo/footer asset. Do not list every ordinary Text object as a separate asset; group recurring primitives into meaningful systems such as `code_panel`, `array_cells`, or `call_stack_frames`.

### 6. Code examples

For each example include purpose, prerequisites/version, minimal working code, execution-order explanation, expected output, beginner mistakes, and one practice variation. Keep code fences outside the final JSON block.

### 7. Manim generation guidance

Include recommended scene class, scene filename, output filename, canvas, palette/style, layout, voiceover segmentation, animation order, and any implementation cautions. Use PascalCase for the class and lowercase underscores for files.

### 8. Metadata

Include topic slug, suggested title, short description, tags, course category, level, estimated duration, and output folder name.

### 9. Quality checklist

Evaluate:

- Concept is accurate.
- Script is beginner-friendly.
- Voiceover sounds natural.
- Voice pace, modulation, pronunciation, and pauses are specified without relying on unsupported provider controls.
- Visuals match narration.
- Code is correct and its output is verified.
- Composition and text will remain clear at 1080p.
- Branding is included.
- The lesson contains intro, summary, and outro.
- Common mistake and practice scenes teach rather than merely fill time.
- JSON is valid and cross-references resolve.

Use `Pass`, `Needs review`, or `Not applicable` and explain non-pass results.

### 10. Machine-readable lesson configuration

End with exactly one fenced `json` block. It must be valid as copied, with no ellipses, comments, Markdown code fences inside string values, or dangling commas.

## JSON shape

Include all top-level fields shown here. Additional fields are allowed when genuinely useful.

```json
{
  "topic": "Human-readable topic",
  "slug": "lowercase_topic_slug",
  "title": "Suggested lesson title",
  "language": "Language, technology, or neutral",
  "language_version": "Version/dialect or not specified",
  "audience": "Specific learner description",
  "prerequisites": ["Narrow prerequisite"],
  "difficulty": "beginner",
  "duration_minutes": 6.5,
  "lesson_objective": "One observable learning objective",
  "short_description": "One or two sentences",
  "course_category": "Course grouping",
  "voice_profile": {
    "persona": "Patient instructor explaining at a whiteboard",
    "accent_language": "Clear neutral Indian English",
    "target_pace_wpm": 132,
    "speed_multiplier": 1.0,
    "tone": "Warm, confident, and beginner-friendly",
    "energy": "Medium with gentle variation",
    "modulation": "Slow slightly for code tracing and emphasize only key rules",
    "pronunciation_dictionary": [
      {
        "written": "C++",
        "spoken": "C plus plus"
      }
    ],
    "provider_notes": "Use natural neural speech when available. With gTTS, express rhythm through punctuation, short segments, and timed pauses."
  },
  "scenes": [
    {
      "id": "scene_01_intro",
      "type": "intro",
      "title": "Scene title",
      "purpose": "Teaching or production purpose",
      "voiceover": "Record-ready narration",
      "voice_delivery": {
        "pace_wpm": 140,
        "tone": "Welcoming",
        "energy": "Medium",
        "modulation": "Gentle rise on the lesson question, then settle",
        "emphasis_words": ["topic keyword"],
        "pronunciation_notes": [],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.5
      },
      "on_screen_text": ["Short displayed phrase"],
      "visual_objects": ["asset_branding", "asset_title_card"],
      "animation_notes": ["Reveal title, then topic"],
      "code_example_ids": [],
      "timing_seconds": 12,
      "transition": "Fade title into motivation scene"
    }
  ],
  "code_examples": [
    {
      "id": "code_01_main",
      "purpose": "What this example demonstrates",
      "runtime": "Runtime/version/dialect",
      "code": "print(\"example\")",
      "explanation_steps": ["Explain in execution order"],
      "expected_output": "example",
      "output_is_representative": false,
      "beginner_mistakes": ["Plausible mistake and correction"],
      "practice_variation": "One focused modification"
    }
  ],
  "assets": [
    {
      "id": "asset_branding",
      "name": "AI Sankalp branding",
      "purpose": "Persistent brand identity",
      "suggested_filename": "ai_sankalp_logo.svg",
      "description": "Logo badge in the upper-right and subtle footer",
      "source_strategy": "reuse",
      "format": "SVG",
      "manim_construction": null,
      "image_generation_prompt": null
    }
  ],
  "voiceover_segments": [
    {
      "id": "vo_01_intro",
      "scene_id": "scene_01_intro",
      "text": "Record-ready narration",
      "estimated_seconds": 8,
      "pace_wpm": 140,
      "tone": "Welcoming",
      "energy": "Medium",
      "modulation": "Natural opening with emphasis on the topic",
      "emphasis_words": ["topic keyword"],
      "pronunciation_notes": [],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.5
    }
  ],
  "tags": ["searchable", "topic", "tags"],
  "output_filename": "lowercase_topic_slug.mp4",
  "output_folder_name": "lowercase_topic_slug",
  "branding": {
    "logo_asset_id": "asset_branding",
    "logo_position": "upper_right_safe_area",
    "footer_text": "AI SANKALP • VISUAL LEARNING",
    "palette": {
      "background": "#071321",
      "panel": "#10243A",
      "primary": "#1473E6",
      "cyan": "#21D4FD",
      "mint": "#55E6C1",
      "gold": "#FFC857",
      "text": "#F5F9FF",
      "muted": "#9EB3C7",
      "warning": "#FF6B6B"
    }
  },
  "generator_compatibility": {
    "sections": [
      {
        "title": "Main concept heading",
        "bullets": ["No more than four concise bullets per generated slide"],
        "narration": "Narration matching these bullets"
      }
    ],
    "code_example": "print(\"example\")",
    "summary": ["Concise recap point"],
    "output_video_name": "lowercase_topic_slug",
    "voiceover": {
      "enabled": true,
      "language": "en",
      "tld": "co.in",
      "speed": 1.0,
      "human_delivery_notes": "Use short segments and punctuation-based pauses; gTTS does not support reliable pitch or emotion controls."
    }
  }
}
```

## Controlled values and cross-references

Use one of these scene `type` values when applicable: `intro`, `motivation`, `explanation`, `code_walkthrough`, `visual_trace`, `common_mistake`, `practice`, `summary`, `outro`.

Use lowercase snake-case IDs. Each `visual_objects` entry must match an asset ID. Each `code_example_ids` entry must match a code-example ID. Each voiceover segment must match one scene ID. Scene timing totals should be reasonably consistent with `duration_minutes`; small allowances for transitions are acceptable.

The `voice_profile` is provider-neutral direction. `voiceover_segments[].text` must exactly match the corresponding scene narration, while delivery fields describe how it should sound. Pace and pause values should agree with scene timing. Do not use SSML unless the selected speech provider explicitly supports it and the user requests it.

`generator_compatibility` maps the richer package to the current local AI Sankalp generator. Include only explanation content in `sections`; intro, code, summary, branding, and outro are supplied by its reusable runtime. Keep each section at four bullets or fewer. This compatibility object supplements, rather than replaces, the richer `scenes` data.
