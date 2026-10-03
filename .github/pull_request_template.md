## Summary

Closes #

<!-- One or two sentences on what changed for the user or the maintainer. -->

## Requirement traceability

| AC | Requirement (copied from the issue) | Evidence (file:line, test name, command, frame) | Status |
| --- | --- | --- | --- |
| AC1 | | | Met / Partly met / Not met |
| AC2 | | | |

## Verification

Exact commands and the result of each. Paste the tail of the output, not a summary.

- [ ] `ruff check .`
- [ ] `python -m unittest discover -s tests -v`
- [ ] `python app.py check`
- [ ] Offline render: `python app.py sample --render --no-voiceover --quality low` (rendering, template, brand, caption or scene changes)
- [ ] `python scripts/qa/check_video.py <video> --profile preview` reports no errors

## Render evidence

<!-- Required when anything visual changed. Attach or link frames (intro, explanation, code, practice, summary, outro)
and say which timestamps you looked at. Write "Not applicable" otherwise. -->

## Known limitations and what was not tested

<!-- Be specific. "None" is rarely true. -->

## Checklist

- [ ] No generated media, caches, `.venv`, `.env` files, keys or absolute local paths in the diff
- [ ] Docs and `templates/lesson.schema.json` updated if behaviour or input format changed
- [ ] Branch name and commit messages follow `AGENTS.md`
- [ ] Independent review done (reviewer agent session or a human) against the original issue
