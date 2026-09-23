# C++ Arrays: Store, Access, and Traverse

## 1. Lesson brief

- **Topic:** Built-in fixed-size arrays in C++
- **Audience:** Tier-2 and tier-3 Indian college students meeting arrays for the first time
- **Prerequisites:** Variables, basic `for` loops, and `std::cout`
- **Learning objective:** Declare a fixed-size array, predict an element from its index, and traverse every valid element safely.
- **Estimated duration:** 5.2 minutes
- **Difficulty:** Beginner
- **Runtime:** C++17
- **Assumptions:** “Array” means a built-in fixed-size C++ array. The lesson covers declaration, initialization, zero-based indexing, consecutive storage, access, traversal, and out-of-bounds access. `std::array` is mentioned only as a next step.

## 2. Teaching script

**Voice direction card:** A warm, patient instructor using the `en-IN-NeerjaNeural` voice. Target 132 WPM overall, 108–118 WPM during indexing and tracing, and 138–142 WPM in the recap and outro. Keep energy medium with gentle variation. Emphasize only `starts at zero`, `less than the size`, and `out of bounds`. Speak C++ as “C plus plus,” `std::cout` as “standard C out,” and `i++` as “i plus plus.” Synthesize sentence-sized segments at rate `-4%` and pitch `+1Hz` for human rhythm and animation alignment.

### Scene 1 — Meet the Array

**Record-ready text:** Welcome to AI Sankalp. Imagine you have the marks of five students. By the end of this lesson, you will know how one C plus plus array can store those marks, how an index finds a value, and how a loop visits every valid position.

**Delivery:** Welcoming, 140 WPM, medium energy; gently lift the three-part promise and pause for 0.5 seconds.

### Scene 2 — Why Not Five Variables?

**Record-ready text:** Without an array, we might create mark one, mark two, mark three, and so on. That is already repetitive for five students. For one hundred students, the program becomes difficult to manage. These values belong together, so we need one structure that keeps them together. An array gives the group one name and stores each value in a numbered position.

**Delivery:** Conversational, 132 WPM; build toward “one hundred students,” then settle on the solution.

### Scene 3 — The Array Mental Model

**Record-ready text:** Think of an array as a row of equal-sized boxes. The array called marks has five boxes, and every box stores an integer. A built-in C plus plus array has a fixed size once it is created. Its elements are stored consecutively, so the next element follows the previous one in memory. The boxes are a teaching picture; real memory stores bits and bytes, not drawn rectangles.

**Delivery:** Clear, 128 WPM; slow on “fixed size” and “consecutively.”

### Scene 4 — Declaration and Zero-Based Indexing

**Record-ready text:** Here is the declaration: int marks, square bracket five, equals five starting values. Int is the element type. Marks is the array name. Five is the number of elements. The important rule is that indexing starts at zero. So five elements use indexes zero, one, two, three, and four. Marks at index two is the third element, which is ninety. The index counts the offset from the beginning, not the human position number.

**Delivery:** Precise, 118 WPM; pause after each declaration component and stress “starts at zero.”

### Scene 5 — A Complete Runnable Example

**Record-ready text:** The program includes iostream so it can print. Inside main, the declaration creates five integers. The next line reads one element directly: marks at index two. Then the for loop starts i at zero. It keeps running while i is less than five, and i plus plus moves to the next index. On each pass, standard C out prints marks at the current index. The loop condition matches the valid index range, zero through four.

**Delivery:** Patient, 112 WPM; use short pauses while each code region is highlighted.

### Scene 6 — Trace the Loop

**Record-ready text:** Now watch what changes. At i equals zero, the marker points to the first box, so the program prints seventy. Then i becomes one and the program prints eighty-five. At two, it prints ninety. At three, it prints seventy-five. At four, it prints eighty-eight. After that, i becomes five. The condition i less than five is false, so the loop stops before any invalid access. Only the index and selected element change on each pass.

**Delivery:** Measured, 108 WPM; keep an even pace through the iterations and pause before the stopping rule.

### Scene 7 — The Out-of-Bounds Mistake

**Record-ready text:** A common mistake is writing i less than or equal to five. That loop eventually tries marks at index five. But a five-element array ends at index four. Accessing index five is out of bounds. In C plus plus, that is undefined behavior: the program might print rubbish, appear to work, or crash. Never depend on one observed result. The correction is i less than five, so every access stays inside the array.

**Delivery:** Calm caution, 120 WPM; clearly separate the incorrect and corrected conditions.

### Scene 8 — Your Turn

**Record-ready text:** Quick practice. For scores equal to twelve, eighteen, twenty-one, and fifteen, what does scores at index three contain? And which loop condition visits every valid element exactly once? Pause and decide. The answers are fifteen, and i less than four, because four elements have indexes zero through three.

**Delivery:** Encouraging, 116 WPM; hold the answer for three seconds before revealing it.

### Scene 9 — What You Learned

**Record-ready text:** Let us recap. A built-in array stores a fixed number of same-type elements in consecutive storage. Indexing starts at zero, so an array of size n uses zero through n minus one. Square brackets access one element. A for loop can traverse the array safely when its condition stays below the size. Index equal to the size is already out of bounds.

**Delivery:** Confident, 138 WPM; give equal weight to each rule and land firmly on the bounds rule.

### Scene 10 — Keep Building

**Record-ready text:** You can now declare, access, and traverse a C plus plus array safely. A useful next step is standard array, which adds a safer container interface while keeping a fixed size. Thank you for learning with AI Sankalp.

**Delivery:** Upbeat, 142 WPM; finish warmly after a 0.8-second pause.

## 3. Scene plan

| Scene ID | Type | Purpose | Time |
|---|---|---|---:|
| `scene_01_intro` | Intro | Set the learning promise | 17 s |
| `scene_02_motivation` | Motivation | Replace repetitive variables with one grouped structure | 30 s |
| `scene_03_explanation` | Explanation | Establish fixed size, same type, and consecutive storage | 34 s |
| `scene_04_indexing` | Explanation | Read the declaration and map zero-based indexes | 40 s |
| `scene_05_code` | Code walkthrough | Explain the runnable program in execution order | 42 s |
| `scene_06_trace` | Visual trace | Animate indexes zero through four and the stop at five | 43 s |
| `scene_07_mistake` | Common mistake | Correct the out-of-bounds loop condition | 36 s |
| `scene_08_practice` | Practice | Predict one access and one loop bound | 31 s |
| `scene_09_summary` | Summary | Reinforce four durable rules | 25 s |
| `scene_10_outro` | Outro | Close and point briefly to `std::array` | 14 s |

## 4. Manim-ready storyboard

### Scene 1 — Meet the Array (intro)

- **Voiceover:** Use Scene 1 record-ready text above.
- **On-screen text:** `C++ Arrays`; `Store • Access • Traverse`.
- **Objects:** `asset_branding`, `asset_title_card`.
- **Animation:** Reveal the title, then the three learning verbs.
- **Code:** None.
- **Timing:** 17 seconds.
- **Voice:** 140 WPM, welcoming, medium energy, 0.5-second end pause.
- **Transition:** Marks cards replace the title.

### Scene 2 — Why Not Five Variables? (motivation)

- **Voiceover:** Use Scene 2 record-ready text above.
- **On-screen text:** `mark1, mark2, mark3, ...`; `What about 100 students?`; `One name: marks`.
- **Objects:** `asset_comparison_cards`, `asset_array_cells`, persistent branding.
- **Animation:** Stack variable cards, show the scaling problem, transform them into an array strip.
- **Code:** None.
- **Timing:** 30 seconds.
- **Voice:** 132 WPM, conversational, emphasize “belong together.”
- **Transition:** Zoom into the array strip.

### Scene 3 — The Array Mental Model (explanation)

- **Voiceover:** Use Scene 3 record-ready text above.
- **On-screen text:** `5 elements`; `same type: int`; `fixed size`; `consecutive storage`.
- **Objects:** `asset_array_cells`, `asset_memory_strip`, persistent branding.
- **Animation:** Reveal equal cells, label type and size, align them with consecutive memory slots.
- **Code:** None.
- **Timing:** 34 seconds.
- **Voice:** 128 WPM, explanatory, slow on the key properties.
- **Transition:** Place the declaration below the cells.

### Scene 4 — Declaration and Zero-Based Indexing (explanation)

- **Voiceover:** Use Scene 4 record-ready text above.
- **On-screen text:** `int marks[5] = {70, 85, 90, 75, 88};`; indexes `0 1 2 3 4`; `marks[2] = 90`.
- **Objects:** `asset_array_cells`, `asset_code_panel`, persistent branding.
- **Animation:** Highlight type, name, and size; add index labels; select index two.
- **Code:** `code_01_main` declaration and direct access.
- **Timing:** 40 seconds.
- **Voice:** 118 WPM, precise, with declaration-component pauses.
- **Transition:** Expand into the full program.

### Scene 5 — A Complete Runnable Example (code walkthrough)

- **Voiceover:** Use Scene 5 record-ready text above.
- **On-screen text:** Complete program and exact output.
- **Objects:** `asset_code_panel`, persistent branding.
- **Animation:** Highlight include, declaration, direct access, loop header, and output statement in execution order.
- **Code:** `code_01_main`.
- **Timing:** 42 seconds.
- **Voice:** 112 WPM, patient and trace-aligned.
- **Transition:** Move the loop header beside the array.

### Scene 6 — Trace the Loop (visual trace)

- **Voiceover:** Use Scene 6 record-ready text above.
- **On-screen text:** `i: 0 → 1 → 2 → 3 → 4`; output values; `i = 5 → false → stop`.
- **Objects:** `asset_array_cells`, `asset_trace_marker`, persistent branding.
- **Animation:** Move the marker cell by cell and append each output; reveal a stop sign at five.
- **Code:** `code_01_main` loop.
- **Timing:** 43 seconds.
- **Voice:** 108 WPM, even and measured.
- **Transition:** Convert the stop sign into a warning.

### Scene 7 — The Out-of-Bounds Mistake (common mistake)

- **Voiceover:** Use Scene 7 record-ready text above.
- **On-screen text:** `Wrong: i <= 5`; `marks[5] ✗`; `Undefined behavior`; `Correct: i < 5`.
- **Objects:** `asset_array_cells`, `asset_bounds_warning`, persistent branding.
- **Animation:** Show a crossed-out sixth ghost cell, then replace the wrong condition with the safe one.
- **Code:** `code_01_main`, contrasted with the deliberate wrong variation.
- **Timing:** 36 seconds.
- **Voice:** 120 WPM, cautionary but calm.
- **Transition:** Fade the warning into a practice card.

### Scene 8 — Your Turn (practice)

- **Voiceover:** Use Scene 8 record-ready text above.
- **On-screen text:** `int scores[4] = {12, 18, 21, 15};`; `scores[3] = ?`; `i < ?`; answer cue `15 and 4`.
- **Objects:** `asset_practice_card`, `asset_array_cells`, persistent branding.
- **Animation:** Hold the unanswered question for three seconds; reveal index labels and answers.
- **Code:** `code_01_main` practice variation.
- **Timing:** 31 seconds.
- **Voice:** 116 WPM, encouraging, with an intentional thinking pause.
- **Transition:** Collapse the practice cells into recap cards.

### Scene 9 — What You Learned (summary)

- **Voiceover:** Use Scene 9 record-ready text above.
- **On-screen text:** `Fixed size • Same type`; `0 to n − 1`; `name[index]`; `i < size`.
- **Objects:** `asset_recap_cards`, persistent branding.
- **Animation:** Reveal four recap cards in narration order.
- **Code:** None.
- **Timing:** 25 seconds.
- **Voice:** 138 WPM, concise and confident.
- **Transition:** Fade to the closing brand line.

### Scene 10 — Keep Building (outro)

- **Voiceover:** Use Scene 10 record-ready text above.
- **On-screen text:** `Keep Learning. Keep Building.`; `Next: std::array`.
- **Objects:** `asset_title_card`, persistent branding.
- **Animation:** Reveal closing line, then a small next-step label.
- **Code:** None.
- **Timing:** 14 seconds.
- **Voice:** 142 WPM, warm and upbeat.
- **Transition:** End.

## 5. Visual asset requirements

| Asset ID | Name | Purpose | Suggested filename | Strategy | Format | Description |
|---|---|---|---|---|---|---|
| `asset_branding` | AI Sankalp branding | Persistent identity | `ai_sankalp_logo.svg` | reuse | SVG | Supplied SVG directly rendered without framing or modification |
| `asset_title_card` | Title card | Intro/outro | `title_card` | manim | primitives | Gradient text, pill, and underline |
| `asset_comparison_cards` | Variable cards | Motivation | `comparison_cards` | manim | primitives | Separate variables transforming into one group |
| `asset_array_cells` | Array cells | Values and indexes | `array_cells` | manim | primitives | Equal cells with value/index layers |
| `asset_memory_strip` | Memory strip | Consecutive storage | `memory_strip` | manim | primitives | Adjacent address slots under logical cells |
| `asset_code_panel` | C++ code panel | Walkthrough | `cpp_code_panel` | manim | `Code` | Syntax-highlighted C++17 code |
| `asset_trace_marker` | Loop marker | Animated traversal | `trace_marker` | manim | primitives | Moving arrow, highlight, and output list |
| `asset_bounds_warning` | Bounds warning | Correct invalid index | `bounds_warning` | manim | primitives | Crossed sixth cell and condition cards |
| `asset_practice_card` | Practice card | Question/answer pause | `practice_card` | manim | primitives | Delayed answer reveal |
| `asset_recap_cards` | Recap cards | Summary | `recap_cards` | manim | primitives | Two-by-two rule grid |

**Construction notes:** Use cinematic full-screen flows rather than split bullet panels: luminous array cells, moving data packets, scanning highlights, morphing code tokens, glass cards, and a live output stream. Keep values legible at normal playback size and pair every color with a label, shape, or position change. The box model is explicitly identified as a teaching abstraction. Render `assets/ai_sankalp_logo.svg` directly at native proportions; never add a badge, border, recoloring, or replacement wordmark. No generated bitmap is needed.

**Image-generation prompt:** Not needed.

## 6. Code examples

### `code_01_main` — Access and traverse five marks

**Purpose:** Demonstrate declaration, one direct indexed access, and a complete safe traversal.

**Prerequisites/runtime:** C++17 and a standard-conforming compiler.

```cpp
#include <iostream>

int main() {
    int marks[5] = {70, 85, 90, 75, 88};

    std::cout << "Third mark: " << marks[2] << '\n';
    std::cout << "All marks: ";

    for (int i = 0; i < 5; ++i) {
        std::cout << marks[i] << ' ';
    }

    std::cout << '\n';
    return 0;
}
```

**Execution order:** Create five `int` elements; read `marks[2]` as the third value; initialize `i` to zero; test `i < 5`; print `marks[i]`; increment and repeat until the test fails at five.

**Expected output:**

```text
Third mark: 90
All marks: 70 85 90 75 88 
```

**Beginner mistakes:** `marks[5]` is not the fifth element; `marks[4]` is. The condition `i <= 5` attempts an out-of-bounds access and causes undefined behavior. Every initializer must be convertible to the element type.

**Practice variation:** Use `int scores[4] = {12, 18, 21, 15};`, predict `scores[3]`, and change the traversal bound to four.

## 7. Manim generation guidance

- **Scene class:** `ArraysInCppScene`
- **Scene filename:** `generated/scenes/arrays_in_cpp.py`
- **Output filename:** `arrays_in_cpp.mp4`
- **Canvas:** 1920×1080, 16:9, 30 FPS
- **Palette:** Background `#071321`; panels `#10243A`/`#16324F`; blue `#1473E6`; cyan `#21D4FD`; mint `#55E6C1`; gold `#FFC857`; text `#F5F9FF`; muted `#9EB3C7`; warning `#FF6B6B`.
- **Layout:** Logo in the upper-right safe area; footer low and unobtrusive; headings top-left; main content centered with generous margins.
- **Voiceover:** Edge neural TTS `en-IN-NeerjaNeural`, rate `-4%`, pitch `+1Hz`, speed `1.0`. Segment by sentence for natural rhythm.
- **Animation order:** Motivation cards → array model → syntax/indexes → code → loop trace → wrong/correct bounds → practice pause → recap → outro.
- **Cautions:** Do not imply that an out-of-bounds read has a predictable result. Do not use color alone. Keep code within a 4.9-unit content height and visually distinguish valid indexes from the invalid size index.

## 8. Metadata

- **Slug:** `arrays_in_cpp`
- **Title:** C++ Arrays: Store, Access, and Traverse
- **Description:** Visual beginner lesson on built-in C++17 arrays, indexes, traversal, and safe bounds.
- **Tags:** C++, arrays, indexing, for loop, beginner programming, AI Sankalp
- **Course category:** C++ Foundations
- **Level:** Beginner
- **Estimated duration:** 5.2 minutes
- **Output folder:** `arrays_in_cpp`

## 9. Quality checklist

| Check | Status | Note |
|---|---|---|
| Concept is accurate | Pass | Built-in C++17 array semantics and undefined behavior are stated correctly. |
| Script is beginner-friendly | Pass | One familiar marks example carries the full lesson. |
| Voiceover sounds natural | Pass | Sentences are short and explanatory. |
| Voice direction is provider-safe | Pass | Rich direction is metadata; gTTS uses only supported controls. |
| Visuals match narration | Pass | Every explanation has a synchronized object and reveal order. |
| Code and output are verified | Pass | The program is deterministic and compiled during production QA. |
| Composition is clear at 1080p | Pass | Generator fit guards and safe margins are used. |
| Branding is included | Pass | Existing SVG is rendered directly and unmodified, with no added badge or wordmark. |
| Intro, summary, and outro exist | Pass | All three are explicit. |
| Mistake and practice teach | Pass | The mistake corrects a real bounds error; practice changes one dimension. |
| JSON and references resolve | Pass | IDs and references are validated before rendering. |

## 10. Machine-readable lesson configuration

+```json
{
  "topic": "Arrays in C++",
  "slug": "arrays_in_cpp",
  "title": "C++ Arrays: Store, Access, and Traverse",
  "language": "C++",
  "language_version": "C++17",
  "audience": "Tier-2 and tier-3 Indian college students learning arrays for the first time",
  "prerequisites": [
    "Basic C++ variables",
    "Basic for-loop syntax",
    "Basic console output with std::cout"
  ],
  "difficulty": "beginner",
  "duration_minutes": 5.2,
  "lesson_objective": "After watching, the learner can declare a fixed-size C++ array, predict an element from its index, and traverse every valid element with a for loop.",
  "short_description": "A visual introduction to built-in fixed-size arrays in C++17 using student marks, zero-based indexing, contiguous storage, traversal, and safe bounds.",
  "course_category": "C++ Foundations",
  "voice_profile": {
    "persona": "Patient instructor explaining at a whiteboard",
    "accent_language": "Clear neutral Indian English",
    "target_pace_wpm": 132,
    "speed_multiplier": 1.0,
    "tone": "Warm, confident, and beginner-friendly",
    "energy": "Medium with gentle variation",
    "modulation": "Slow slightly for code tracing and emphasize only the key indexing and bounds rules",
    "pronunciation_dictionary": [
      {
        "written": "C++",
        "spoken": "C plus plus"
      },
      {
        "written": "std::cout",
        "spoken": "standard C out"
      },
      {
        "written": "i++",
        "spoken": "i plus plus"
      }
    ],
    "provider_notes": "Use Edge neural voice en-IN-NeerjaNeural at rate -4% and pitch +1Hz. Synthesize sentence-sized segments for natural rhythm and animation alignment."
  },
  "scenes": [
    {
      "id": "scene_01_intro",
      "type": "intro",
      "title": "Meet the Array",
      "purpose": "Set the lesson goal and connect arrays to a familiar collection of marks.",
      "voiceover": "Welcome to AI Sankalp. Imagine you have the marks of five students. By the end of this lesson, you will know how one C plus plus array can store those marks, how an index finds a value, and how a loop visits every valid position.",
      "voice_delivery": {
        "pace_wpm": 140,
        "tone": "Welcoming",
        "energy": "Medium",
        "modulation": "Lift gently on the three-part lesson promise",
        "emphasis_words": ["array", "index", "loop"],
        "pronunciation_notes": ["C++ is spoken as C plus plus"],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.5
      },
      "on_screen_text": ["C++ Arrays", "Store • Access • Traverse"],
      "visual_objects": ["asset_branding", "asset_title_card"],
      "animation_notes": ["Reveal the title, then the three learning verbs."],
      "code_example_ids": [],
      "timing_seconds": 17,
      "transition": "Marks cards replace the title."
    },
    {
      "id": "scene_02_motivation",
      "type": "motivation",
      "title": "Why Not Five Variables?",
      "purpose": "Motivate grouping related values under one name.",
      "voiceover": "Without an array, we might create mark one, mark two, mark three, and so on. That is already repetitive for five students. For one hundred students, the program becomes difficult to manage. These values belong together, so we need one structure that keeps them together. An array gives the group one name and stores each value in a numbered position.",
      "voice_delivery": {
        "pace_wpm": 132,
        "tone": "Conversational and motivating",
        "energy": "Medium",
        "modulation": "Build slightly toward one hundred students, then settle on the solution",
        "emphasis_words": ["belong together", "one name", "numbered position"],
        "pronunciation_notes": [],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.6
      },
      "on_screen_text": ["mark1, mark2, mark3, ...", "What about 100 students?", "One name: marks"],
      "visual_objects": ["asset_branding", "asset_comparison_cards", "asset_array_cells"],
      "animation_notes": ["Stack separate variable cards, show a 100-student warning, then transform them into one array strip."],
      "code_example_ids": [],
      "timing_seconds": 30,
      "transition": "Zoom into the array strip."
    },
    {
      "id": "scene_03_explanation",
      "type": "explanation",
      "title": "The Array Mental Model",
      "purpose": "Define a built-in fixed-size array and state the same-type and consecutive-storage model.",
      "voiceover": "Think of an array as a row of equal-sized boxes. The array called marks has five boxes, and every box stores an integer. A built-in C plus plus array has a fixed size once it is created. Its elements are stored consecutively, so the next element follows the previous one in memory. The boxes are a teaching picture; real memory stores bits and bytes, not drawn rectangles.",
      "voice_delivery": {
        "pace_wpm": 128,
        "tone": "Clear and explanatory",
        "energy": "Medium-low",
        "modulation": "Slow on fixed size and consecutively",
        "emphasis_words": ["five boxes", "integer", "fixed size", "consecutively"],
        "pronunciation_notes": ["C++ is spoken as C plus plus"],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.7
      },
      "on_screen_text": ["marks", "5 elements", "same type: int", "fixed size", "consecutive storage"],
      "visual_objects": ["asset_branding", "asset_array_cells", "asset_memory_strip"],
      "animation_notes": ["Reveal five equal cells, label their shared type and fixed size, then align them over consecutive memory slots."],
      "code_example_ids": [],
      "timing_seconds": 34,
      "transition": "Place declaration syntax below the cells."
    },
    {
      "id": "scene_04_indexing",
      "type": "explanation",
      "title": "Declaration and Zero-Based Indexing",
      "purpose": "Explain the declaration and map indexes zero through four to five values.",
      "voiceover": "Here is the declaration: int marks, square bracket five, equals five starting values. Int is the element type. Marks is the array name. Five is the number of elements. The important rule is that indexing starts at zero. So five elements use indexes zero, one, two, three, and four. Marks at index two is the third element, which is ninety. The index counts the offset from the beginning, not the human position number.",
      "voice_delivery": {
        "pace_wpm": 118,
        "tone": "Precise and reassuring",
        "energy": "Medium",
        "modulation": "Pause after each declaration component and stress starts at zero",
        "emphasis_words": ["element type", "array name", "starts at zero", "third element"],
        "pronunciation_notes": ["Read marks[2] as marks at index two"],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.8
      },
      "on_screen_text": ["int marks[5] = {70, 85, 90, 75, 88};", "index: 0  1  2  3  4", "marks[2] = 90"],
      "visual_objects": ["asset_branding", "asset_array_cells", "asset_code_panel"],
      "animation_notes": ["Highlight type, name, and size in order; add index labels; frame index two and reveal ninety."],
      "code_example_ids": ["code_01_main"],
      "timing_seconds": 40,
      "transition": "Expand the declaration into the complete program."
    },
    {
      "id": "scene_05_code",
      "type": "code_walkthrough",
      "title": "A Complete Runnable Example",
      "purpose": "Connect declaration, access, traversal, and output in a minimal C++17 program.",
      "voiceover": "The program includes iostream so it can print. Inside main, the declaration creates five integers. The next line reads one element directly: marks at index two. Then the for loop starts i at zero. It keeps running while i is less than five, and i plus plus moves to the next index. On each pass, standard C out prints marks at the current index. The loop condition matches the valid index range, zero through four.",
      "voice_delivery": {
        "pace_wpm": 112,
        "tone": "Patient code walkthrough",
        "energy": "Medium-low",
        "modulation": "Use short pauses as each code region is highlighted",
        "emphasis_words": ["index two", "less than five", "current index", "zero through four"],
        "pronunciation_notes": ["std::cout is spoken as standard C out", "i++ is spoken as i plus plus"],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.8
      },
      "on_screen_text": ["Complete C++17 program", "Expected output: Third mark: 90 | All marks: 70 85 90 75 88"],
      "visual_objects": ["asset_branding", "asset_code_panel"],
      "animation_notes": ["Reveal the program, then highlight include, declaration, direct access, loop header, and print statement in execution order."],
      "code_example_ids": ["code_01_main"],
      "timing_seconds": 42,
      "transition": "Move the loop header beside the array cells."
    },
    {
      "id": "scene_06_trace",
      "type": "visual_trace",
      "title": "Trace the Loop",
      "purpose": "Animate each valid index and connect it to the printed value.",
      "voiceover": "Now watch what changes. At i equals zero, the marker points to the first box, so the program prints seventy. Then i becomes one and the program prints eighty-five. At two, it prints ninety. At three, it prints seventy-five. At four, it prints eighty-eight. After that, i becomes five. The condition i less than five is false, so the loop stops before any invalid access. Only the index and selected element change on each pass.",
      "voice_delivery": {
        "pace_wpm": 108,
        "tone": "Measured and trace-focused",
        "energy": "Medium",
        "modulation": "Slow evenly through the five iterations, then pause before the stopping rule",
        "emphasis_words": ["zero", "four", "five is false", "stops"],
        "pronunciation_notes": ["i is spoken as eye"],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.8
      },
      "on_screen_text": ["i: 0 → 1 → 2 → 3 → 4", "output: 70 85 90 75 88", "i = 5 → condition false → stop"],
      "visual_objects": ["asset_branding", "asset_array_cells", "asset_trace_marker"],
      "animation_notes": ["Move a labeled marker across the five cells and append each value to output; show a stop sign when i reaches five."],
      "code_example_ids": ["code_01_main"],
      "timing_seconds": 43,
      "transition": "Turn the stop sign into a warning card."
    },
    {
      "id": "scene_07_mistake",
      "type": "common_mistake",
      "title": "The Out-of-Bounds Mistake",
      "purpose": "Teach that index five is invalid for a five-element array and that accessing it is undefined behavior.",
      "voiceover": "A common mistake is writing i less than or equal to five. That loop eventually tries marks at index five. But a five-element array ends at index four. Accessing index five is out of bounds. In C plus plus, that is undefined behavior: the program might print rubbish, appear to work, or crash. Never depend on one observed result. The correction is i less than five, so every access stays inside the array.",
      "voice_delivery": {
        "pace_wpm": 120,
        "tone": "Cautionary but calm",
        "energy": "Medium",
        "modulation": "Separate the incorrect and corrected conditions with a clear pause",
        "emphasis_words": ["index five", "out of bounds", "undefined behavior", "less than five"],
        "pronunciation_notes": ["C++ is spoken as C plus plus"],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.8
      },
      "on_screen_text": ["Wrong: i <= 5", "marks[5] ✗", "Undefined behavior", "Correct: i < 5"],
      "visual_objects": ["asset_branding", "asset_array_cells", "asset_bounds_warning"],
      "animation_notes": ["Show a sixth ghost cell crossed out; label the incorrect condition, then replace it with the safe condition."],
      "code_example_ids": ["code_01_main"],
      "timing_seconds": 36,
      "transition": "Fade the warning into a question card."
    },
    {
      "id": "scene_08_practice",
      "type": "practice",
      "title": "Your Turn",
      "purpose": "Check whether the learner can map an index and predict loop output.",
      "voiceover": "Quick practice. For scores equal to twelve, eighteen, twenty-one, and fifteen, what does scores at index three contain? And which loop condition visits every valid element exactly once? Pause and decide. The answers are fifteen, and i less than four, because four elements have indexes zero through three.",
      "voice_delivery": {
        "pace_wpm": 116,
        "tone": "Encouraging",
        "energy": "Medium",
        "modulation": "Ask both questions clearly, allow thinking time, then reveal the answer warmly",
        "emphasis_words": ["index three", "exactly once", "fifteen", "less than four"],
        "pronunciation_notes": ["i is spoken as eye"],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 3.0
      },
      "on_screen_text": ["int scores[4] = {12, 18, 21, 15};", "scores[3] = ?", "i < ?", "Answer: 15 and 4"],
      "visual_objects": ["asset_branding", "asset_practice_card", "asset_array_cells"],
      "animation_notes": ["Show the question without the answer, hold for three seconds, then reveal index labels and the answer."],
      "code_example_ids": ["code_01_main"],
      "timing_seconds": 31,
      "transition": "Collapse the practice array into recap cards."
    },
    {
      "id": "scene_09_summary",
      "type": "summary",
      "title": "What You Learned",
      "purpose": "Reinforce the definition, index range, traversal rule, and safety rule.",
      "voiceover": "Let us recap. A built-in array stores a fixed number of same-type elements in consecutive storage. Indexing starts at zero, so an array of size n uses zero through n minus one. Square brackets access one element. A for loop can traverse the array safely when its condition stays below the size. Index equal to the size is already out of bounds.",
      "voice_delivery": {
        "pace_wpm": 138,
        "tone": "Concise and confident",
        "energy": "Medium-high",
        "modulation": "Give each recap rule equal weight and land firmly on the bounds rule",
        "emphasis_words": ["fixed number", "starts at zero", "below the size", "out of bounds"],
        "pronunciation_notes": ["n minus one is spoken naturally"],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.6
      },
      "on_screen_text": ["Fixed size • Same type", "Indexes: 0 to n − 1", "Access: name[index]", "Safe loop: i < size"],
      "visual_objects": ["asset_branding", "asset_recap_cards"],
      "animation_notes": ["Reveal four recap cards in the same order as the narration."],
      "code_example_ids": [],
      "timing_seconds": 25,
      "transition": "Recap cards fade to the closing brand line."
    },
    {
      "id": "scene_10_outro",
      "type": "outro",
      "title": "Keep Building",
      "purpose": "Close the lesson and suggest the next topic without adding new scope.",
      "voiceover": "You can now declare, access, and traverse a C plus plus array safely. A useful next step is standard array, which adds a safer container interface while keeping a fixed size. Thank you for learning with AI Sankalp.",
      "voice_delivery": {
        "pace_wpm": 142,
        "tone": "Upbeat and concise",
        "energy": "Medium-high",
        "modulation": "Warm close with a slight lift on the next step",
        "emphasis_words": ["safely", "next step", "AI Sankalp"],
        "pronunciation_notes": ["std::array is spoken as standard array"],
        "pause_before_seconds": 0.0,
        "pause_after_seconds": 0.8
      },
      "on_screen_text": ["Keep Learning. Keep Building.", "Next: std::array"],
      "visual_objects": ["asset_branding", "asset_title_card"],
      "animation_notes": ["Reveal the closing line and a small next-step label."],
      "code_example_ids": [],
      "timing_seconds": 14,
      "transition": "End."
    }
  ],
  "code_examples": [
    {
      "id": "code_01_main",
      "purpose": "Declare five marks, access the third element, and traverse all valid indexes.",
      "runtime": "C++17",
      "code": "#include <iostream>\n\nint main() {\n    int marks[5] = {70, 85, 90, 75, 88};\n\n    std::cout << \"Third mark: \" << marks[2] << '\\n';\n    std::cout << \"All marks: \";\n\n    for (int i = 0; i < 5; ++i) {\n        std::cout << marks[i] << ' ';\n    }\n\n    std::cout << '\\n';\n    return 0;\n}",
      "explanation_steps": [
        "Create a fixed-size array named marks containing five int elements.",
        "Read marks[2]; zero-based indexing maps it to the third value, 90.",
        "Initialize i to 0 and test i < 5 before every loop pass.",
        "Print marks[i], then increment i until the condition becomes false at i equal to 5."
      ],
      "expected_output": "Third mark: 90\nAll marks: 70 85 90 75 88 \n",
      "output_is_representative": false,
      "beginner_mistakes": [
        "Using marks[5] for the fifth element; the fifth element is marks[4].",
        "Using i <= 5 in the loop; this attempts the invalid access marks[5].",
        "Mixing element types in a built-in int array; every element must be convertible to int."
      ],
      "practice_variation": "Change the array to int scores[4] = {12, 18, 21, 15}; then predict scores[3] and update the loop bound to 4."
    }
  ],
  "assets": [
    {
      "id": "asset_branding",
      "name": "AI Sankalp branding",
      "purpose": "Persistent brand identity",
      "suggested_filename": "ai_sankalp_logo.svg",
      "description": "The supplied SVG rendered directly in the upper-right at its native proportions, with no badge, border, recoloring, or added wordmark",
      "source_strategy": "reuse",
      "format": "SVG",
      "manim_construction": null,
      "image_generation_prompt": null
    },
    {
      "id": "asset_title_card",
      "name": "Lesson title card",
      "purpose": "Introduce and close the lesson",
      "suggested_filename": "title_card",
      "description": "Gradient title, topic pill, underline, and closing text built with Manim primitives",
      "source_strategy": "manim",
      "format": "Manim primitives",
      "manim_construction": "Text, RoundedRectangle, Line, and VGroup",
      "image_generation_prompt": null
    },
    {
      "id": "asset_comparison_cards",
      "name": "Separate-variable comparison",
      "purpose": "Show why many separate variables are hard to manage",
      "suggested_filename": "comparison_cards",
      "description": "Stacked variable cards that transform into a single array",
      "source_strategy": "manim",
      "format": "Manim primitives",
      "manim_construction": "RoundedRectangle cards, monospace Text, braces, and Transform",
      "image_generation_prompt": null
    },
    {
      "id": "asset_array_cells",
      "name": "Reusable array cell system",
      "purpose": "Display values, indexes, and selected elements",
      "suggested_filename": "array_cells",
      "description": "Five equal labeled cells with value and index layers",
      "source_strategy": "manim",
      "format": "Manim primitives",
      "manim_construction": "Square or RoundedRectangle cells grouped in a VGroup with Text labels and SurroundingRectangle highlights",
      "image_generation_prompt": null
    },
    {
      "id": "asset_memory_strip",
      "name": "Consecutive memory strip",
      "purpose": "Connect the box analogy to consecutive storage",
      "suggested_filename": "memory_strip",
      "description": "Adjacent address slots aligned beneath the logical array cells",
      "source_strategy": "manim",
      "format": "Manim primitives",
      "manim_construction": "Rectangles, short address labels, braces, and arrows",
      "image_generation_prompt": null
    },
    {
      "id": "asset_code_panel",
      "name": "C++ code panel",
      "purpose": "Show declaration and runnable program",
      "suggested_filename": "cpp_code_panel",
      "description": "Syntax-highlighted code with line numbers and moving highlight",
      "source_strategy": "manim",
      "format": "Manim Code object",
      "manim_construction": "Code with cpp lexer, dark window background, and translucent highlight rectangles",
      "image_generation_prompt": null
    },
    {
      "id": "asset_trace_marker",
      "name": "Loop trace marker",
      "purpose": "Synchronize index, selected cell, and output",
      "suggested_filename": "trace_marker",
      "description": "Arrow and i-value label that move from cell zero through four",
      "source_strategy": "manim",
      "format": "Manim primitives",
      "manim_construction": "Arrow, Text label, SurroundingRectangle, and output VGroup",
      "image_generation_prompt": null
    },
    {
      "id": "asset_bounds_warning",
      "name": "Bounds warning",
      "purpose": "Distinguish a valid last index from invalid index five",
      "suggested_filename": "bounds_warning",
      "description": "Crossed-out ghost cell and wrong-versus-correct loop conditions",
      "source_strategy": "manim",
      "format": "Manim primitives",
      "manim_construction": "Dashed rectangle, Cross, warning Text, and condition cards",
      "image_generation_prompt": null
    },
    {
      "id": "asset_practice_card",
      "name": "Practice question card",
      "purpose": "Hold the question and delayed answer cue",
      "suggested_filename": "practice_card",
      "description": "Question panel with a three-second answer reveal",
      "source_strategy": "manim",
      "format": "Manim primitives",
      "manim_construction": "RoundedRectangle, Text, countdown dots, and FadeIn",
      "image_generation_prompt": null
    },
    {
      "id": "asset_recap_cards",
      "name": "Recap cards",
      "purpose": "Summarize the four key rules",
      "suggested_filename": "recap_cards",
      "description": "Four compact high-contrast cards",
      "source_strategy": "manim",
      "format": "Manim primitives",
      "manim_construction": "RoundedRectangle and Text arranged in a two-by-two grid",
      "image_generation_prompt": null
    }
  ],
  "voiceover_segments": [
    {
      "id": "vo_01_intro",
      "scene_id": "scene_01_intro",
      "text": "Welcome to AI Sankalp. Imagine you have the marks of five students. By the end of this lesson, you will know how one C plus plus array can store those marks, how an index finds a value, and how a loop visits every valid position.",
      "estimated_seconds": 17,
      "pace_wpm": 140,
      "tone": "Welcoming",
      "energy": "Medium",
      "modulation": "Lift gently on the three-part lesson promise",
      "emphasis_words": ["array", "index", "loop"],
      "pronunciation_notes": ["C++ is spoken as C plus plus"],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.5
    },
    {
      "id": "vo_02_motivation",
      "scene_id": "scene_02_motivation",
      "text": "Without an array, we might create mark one, mark two, mark three, and so on. That is already repetitive for five students. For one hundred students, the program becomes difficult to manage. These values belong together, so we need one structure that keeps them together. An array gives the group one name and stores each value in a numbered position.",
      "estimated_seconds": 30,
      "pace_wpm": 132,
      "tone": "Conversational and motivating",
      "energy": "Medium",
      "modulation": "Build slightly toward one hundred students, then settle on the solution",
      "emphasis_words": ["belong together", "one name", "numbered position"],
      "pronunciation_notes": [],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.6
    },
    {
      "id": "vo_03_explanation",
      "scene_id": "scene_03_explanation",
      "text": "Think of an array as a row of equal-sized boxes. The array called marks has five boxes, and every box stores an integer. A built-in C plus plus array has a fixed size once it is created. Its elements are stored consecutively, so the next element follows the previous one in memory. The boxes are a teaching picture; real memory stores bits and bytes, not drawn rectangles.",
      "estimated_seconds": 34,
      "pace_wpm": 128,
      "tone": "Clear and explanatory",
      "energy": "Medium-low",
      "modulation": "Slow on fixed size and consecutively",
      "emphasis_words": ["five boxes", "integer", "fixed size", "consecutively"],
      "pronunciation_notes": ["C++ is spoken as C plus plus"],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.7
    },
    {
      "id": "vo_04_indexing",
      "scene_id": "scene_04_indexing",
      "text": "Here is the declaration: int marks, square bracket five, equals five starting values. Int is the element type. Marks is the array name. Five is the number of elements. The important rule is that indexing starts at zero. So five elements use indexes zero, one, two, three, and four. Marks at index two is the third element, which is ninety. The index counts the offset from the beginning, not the human position number.",
      "estimated_seconds": 40,
      "pace_wpm": 118,
      "tone": "Precise and reassuring",
      "energy": "Medium",
      "modulation": "Pause after each declaration component and stress starts at zero",
      "emphasis_words": ["element type", "array name", "starts at zero", "third element"],
      "pronunciation_notes": ["Read marks[2] as marks at index two"],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.8
    },
    {
      "id": "vo_05_code",
      "scene_id": "scene_05_code",
      "text": "The program includes iostream so it can print. Inside main, the declaration creates five integers. The next line reads one element directly: marks at index two. Then the for loop starts i at zero. It keeps running while i is less than five, and i plus plus moves to the next index. On each pass, standard C out prints marks at the current index. The loop condition matches the valid index range, zero through four.",
      "estimated_seconds": 42,
      "pace_wpm": 112,
      "tone": "Patient code walkthrough",
      "energy": "Medium-low",
      "modulation": "Use short pauses as each code region is highlighted",
      "emphasis_words": ["index two", "less than five", "current index", "zero through four"],
      "pronunciation_notes": ["std::cout is spoken as standard C out", "i++ is spoken as i plus plus"],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.8
    },
    {
      "id": "vo_06_trace",
      "scene_id": "scene_06_trace",
      "text": "Now watch what changes. At i equals zero, the marker points to the first box, so the program prints seventy. Then i becomes one and the program prints eighty-five. At two, it prints ninety. At three, it prints seventy-five. At four, it prints eighty-eight. After that, i becomes five. The condition i less than five is false, so the loop stops before any invalid access. Only the index and selected element change on each pass.",
      "estimated_seconds": 43,
      "pace_wpm": 108,
      "tone": "Measured and trace-focused",
      "energy": "Medium",
      "modulation": "Slow evenly through the five iterations, then pause before the stopping rule",
      "emphasis_words": ["zero", "four", "five is false", "stops"],
      "pronunciation_notes": ["i is spoken as eye"],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.8
    },
    {
      "id": "vo_07_mistake",
      "scene_id": "scene_07_mistake",
      "text": "A common mistake is writing i less than or equal to five. That loop eventually tries marks at index five. But a five-element array ends at index four. Accessing index five is out of bounds. In C plus plus, that is undefined behavior: the program might print rubbish, appear to work, or crash. Never depend on one observed result. The correction is i less than five, so every access stays inside the array.",
      "estimated_seconds": 36,
      "pace_wpm": 120,
      "tone": "Cautionary but calm",
      "energy": "Medium",
      "modulation": "Separate the incorrect and corrected conditions with a clear pause",
      "emphasis_words": ["index five", "out of bounds", "undefined behavior", "less than five"],
      "pronunciation_notes": ["C++ is spoken as C plus plus"],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.8
    },
    {
      "id": "vo_08_practice",
      "scene_id": "scene_08_practice",
      "text": "Quick practice. For scores equal to twelve, eighteen, twenty-one, and fifteen, what does scores at index three contain? And which loop condition visits every valid element exactly once? Pause and decide. The answers are fifteen, and i less than four, because four elements have indexes zero through three.",
      "estimated_seconds": 31,
      "pace_wpm": 116,
      "tone": "Encouraging",
      "energy": "Medium",
      "modulation": "Ask both questions clearly, allow thinking time, then reveal the answer warmly",
      "emphasis_words": ["index three", "exactly once", "fifteen", "less than four"],
      "pronunciation_notes": ["i is spoken as eye"],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 3.0
    },
    {
      "id": "vo_09_summary",
      "scene_id": "scene_09_summary",
      "text": "Let us recap. A built-in array stores a fixed number of same-type elements in consecutive storage. Indexing starts at zero, so an array of size n uses zero through n minus one. Square brackets access one element. A for loop can traverse the array safely when its condition stays below the size. Index equal to the size is already out of bounds.",
      "estimated_seconds": 25,
      "pace_wpm": 138,
      "tone": "Concise and confident",
      "energy": "Medium-high",
      "modulation": "Give each recap rule equal weight and land firmly on the bounds rule",
      "emphasis_words": ["fixed number", "starts at zero", "below the size", "out of bounds"],
      "pronunciation_notes": ["n minus one is spoken naturally"],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.6
    },
    {
      "id": "vo_10_outro",
      "scene_id": "scene_10_outro",
      "text": "You can now declare, access, and traverse a C plus plus array safely. A useful next step is standard array, which adds a safer container interface while keeping a fixed size. Thank you for learning with AI Sankalp.",
      "estimated_seconds": 14,
      "pace_wpm": 142,
      "tone": "Upbeat and concise",
      "energy": "Medium-high",
      "modulation": "Warm close with a slight lift on the next step",
      "emphasis_words": ["safely", "next step", "AI Sankalp"],
      "pronunciation_notes": ["std::array is spoken as standard array"],
      "pause_before_seconds": 0.0,
      "pause_after_seconds": 0.8
    }
  ],
  "tags": ["C++", "arrays", "indexing", "for loop", "beginner programming", "AI Sankalp"],
  "output_filename": "arrays_in_cpp.mp4",
  "output_folder_name": "arrays_in_cpp",
  "visual_template": "futuristic_array",
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
    "visual_template": "futuristic_array",
    "sections": [
      {
        "title": "Why arrays help",
        "bullets": [
          "Related values stay together under one array name.",
          "A numbered position identifies each element.",
          "One array scales better than many separate variables."
        ],
        "narration": "Without an array, we might create mark one, mark two, mark three, and so on. That is already repetitive for five students. For one hundred students, the program becomes difficult to manage. These values belong together, so we need one structure that keeps them together. An array gives the group one name and stores each value in a numbered position."
      },
      {
        "title": "Build the mental model",
        "bullets": [
          "A fixed-size array is a row of equal-type elements.",
          "int marks[5] stores exactly five integers.",
          "Built-in array elements occupy consecutive storage."
        ],
        "narration": "Think of an array as a row of equal-sized boxes. The array called marks has five boxes, and every box stores an integer. A built-in C plus plus array has a fixed size once it is created. Its elements are stored consecutively, so the next element follows the previous one in memory. The boxes are a teaching picture; real memory stores bits and bytes, not drawn rectangles."
      },
      {
        "title": "Read the declaration and indexes",
        "bullets": [
          "int is the type, marks is the name, and 5 is the size.",
          "Five elements use indexes 0 through 4.",
          "marks[2] selects the third element: 90."
        ],
        "narration": "Here is the declaration: int marks, square bracket five, equals five starting values. Int is the element type. Marks is the array name. Five is the number of elements. The important rule is that indexing starts at zero. So five elements use indexes zero, one, two, three, and four. Marks at index two is the third element, which is ninety. The index counts the offset from the beginning, not the human position number."
      },
      {
        "title": "Connect the code to the output",
        "bullets": [
          "The declaration creates five integer elements.",
          "marks[2] reads the third value directly.",
          "The loop prints marks[i] while i stays below 5.",
          "The exact output is 90, then all five marks."
        ],
        "narration": "The program includes iostream so it can print. Inside main, the declaration creates five integers. The next line reads one element directly: marks at index two. Then the for loop starts i at zero. It keeps running while i is less than five, and i plus plus moves to the next index. On each pass, standard C out prints marks at the current index. The loop condition matches the valid index range, zero through four."
      },
      {
        "title": "Trace the traversal",
        "bullets": [
          "Start i at 0 and read marks[i].",
          "Advance through indexes 0, 1, 2, 3, and 4.",
          "At i equal to 5, i < 5 is false and the loop stops."
        ],
        "narration": "Now watch what changes. At i equals zero, the marker points to the first box, so the program prints seventy. Then i becomes one and the program prints eighty-five. At two, it prints ninety. At three, it prints seventy-five. At four, it prints eighty-eight. After that, i becomes five. The condition i less than five is false, so the loop stops before any invalid access. Only the index and selected element change on each pass."
      },
      {
        "title": "Avoid an out-of-bounds access",
        "bullets": [
          "Wrong: i <= 5 eventually attempts marks[5].",
          "Index 5 is outside a five-element array.",
          "Out-of-bounds access causes undefined behavior.",
          "Correct: keep the loop condition i < 5."
        ],
        "narration": "A common mistake is writing i less than or equal to five. That loop eventually tries marks at index five. But a five-element array ends at index four. Accessing index five is out of bounds. In C plus plus, that is undefined behavior: the program might print rubbish, appear to work, or crash. Never depend on one observed result. The correction is i less than five, so every access stays inside the array."
      },
      {
        "title": "Quick practice",
        "bullets": [
          "scores contains 12, 18, 21, and 15.",
          "What is scores[3]?",
          "Which loop bound visits all four valid indexes?",
          "Answer: scores[3] is 15, and use i < 4."
        ],
        "narration": "Quick practice. For scores equal to twelve, eighteen, twenty-one, and fifteen, what does scores at index three contain? And which loop condition visits every valid element exactly once? Pause and decide. The answers are fifteen, and i less than four, because four elements have indexes zero through three."
      }
    ],
    "code_example": "#include <iostream>\n\nint main() {\n    int marks[5] = {70, 85, 90, 75, 88};\n\n    std::cout << \"Third mark: \" << marks[2] << '\\n';\n    std::cout << \"All marks: \";\n\n    for (int i = 0; i < 5; ++i) {\n        std::cout << marks[i] << ' ';\n    }\n\n    std::cout << '\\n';\n    return 0;\n}",
    "summary": [
      "A built-in array has a fixed number of same-type elements.",
      "Indexes run from 0 through size minus 1.",
      "Use name[index] to access an element.",
      "Traverse safely with a loop condition below the array size."
    ],
    "output_video_name": "arrays_in_cpp",
    "voiceover": {
      "enabled": true,
      "language": "en",
      "tld": "co.in",
      "speed": 1.0,
      "provider": "edge",
      "voice": "en-IN-NeerjaNeural",
      "rate": "-4%",
      "pitch": "+1Hz",
      "human_delivery_notes": "Use sentence-sized neural speech segments, selective emphasis, and animation-aligned pauses."
    }
  }
}
```
