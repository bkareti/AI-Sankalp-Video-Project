# Lesson review checklist (SME sign-off)

A lesson is **final-ready** only when `python app.py qa` passes every check.
Two of those checks are human ones:

- a subject-matter expert (SME) approves the lesson;
- the four manual checklist items below are marked `pass`.

Automated checks cannot judge whether a lesson teaches well. That is the SME's job.

## 1. Run QA first

```bash
.venv/bin/python app.py generate --config examples/<slug>/lesson_package.json --render --quality high
.venv/bin/python app.py qa --slug <slug>
```

The QA command exits with:

- `0`: final-ready;
- `2`: something needs review;
- `1`: something failed.

It also writes `generated/qa/<slug>/qa_report.json`. Fix every `FAIL` first: each one prints a **Why** and a **Fix**.

To watch with captions burned in, add `--burn-captions` to the render and open
`generated/videos/<slug>_captioned.mp4`.

## 2. Watch the whole video and check each item

### Pedagogy
- [ ] Every statement and code example is technically correct. The expected output matches what the code really prints.
- [ ] The lesson objective is met: a beginner could do what it promises.
- [ ] The common-mistake scene shows a real mistake and the real error or behavior.
- [ ] The practice question has one clear answer, and the video reveals it.

### Pacing
- [ ] The narration is not rushed, and the pauses after questions are long enough to think.
- [ ] Each visual appears while the narration talks about it, not before or after.
- [ ] No scene holds a static frame for long without reason.

### Readability
- [ ] All text, code, and captions are readable on a phone screen.
- [ ] No text overflows its panel or overlaps other text.
- [ ] Captions match the narration and never cover important visuals. They sit in the bottom band above the footer.

### Brand
- [ ] Use `docs/brand-checklist.md`: logo in the upper right, footer, fonts, palette, safe margins.

## 3. Record the result in the lesson package

Record approval in **the package file QA checks**. QA names that file in its first
row ("Lesson package exists") and in `inputs.package` of `qa_report.json`.

- `qa --slug <slug>` prefers `generated/packages/<slug>/lesson_package.json`,
  where the video-assets skill saves new packages. It uses
  `examples/<slug>/lesson_package.json` only when no generated copy exists.
- If both exist with different `review_status`, QA marks the package row
  "needs review" so an approval is never lost in the wrong file.
- To check a specific file, use `qa --package <path>`.

Edit `review_status` in that file:

```json
"review_status": {
  "sme_approved": true,
  "sme_reviewer": "Full Name",
  "sme_approved_on": "2026-10-01",
  "notes": "Checked code output on g++ 13. Slowed the trace scene.",
  "checklist": {"pedagogy": "pass", "pacing": "pass", "readability": "pass", "brand": "pass"}
}
```

- Use `needs_review` for an item that needs another pass, and say why in `notes`.
- Never set `sme_approved` to `true` on someone else's behalf.
- An approval must name the reviewer and the date (`YYYY-MM-DD`).
- If the lesson content changes after approval, set `sme_approved` back to `false` and review again.

Then run QA once more, the same way as before (`--slug <slug>` or `--package <path>`). It must exit `0`.
