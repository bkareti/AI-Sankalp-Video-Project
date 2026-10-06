# AI architecture

Decision record for issue #10: which AI runs where, how it is called, paid for,
secured, and recovered. Later work (repair #13, planner #15, UI #18, batch #19)
builds on this document and on `ai_sankalp/llm.py`.

Status: decided 2026-10-03. Prices were checked on that date; re-check before a
batch run.

## Decision in one paragraph

AI is **optional**. The Planner (topic to rich lesson package) stays a
**human-run agent skill** (`skills/ai-sankalp-video-assets`, run from Codex or
Claude Code). A small **Python adapter** (`ai_sankalp/llm.py`) is the integration
target for unattended or bounded calls: repair, batch and UI features. The
default provider is `none`, so every existing command works offline with no key.
Compiler, QA, rendering, captions and TTS selection stay deterministic code.

## Which AI runs where

| Component | Runtime | Triggered by | Model class | Network | Human gate |
|---|---|---|---|---|---|
| Planner (topic to package `.md` + `.json`) | Agent skill in Codex or Claude Code | A person ("create video to explain ...") | Sonnet class, Opus class for new topic families | Yes (the agent) | Person reads the package before compiling |
| Python Planner | `ai_sankalp/llm.py` | Deferred to #15 | Same | Yes | Same as above |
| Repair of a failed package or scene | `ai_sankalp/llm.py` | #13, on a failed validation or QA check | Haiku class for small schema/syntax fixes, Sonnet otherwise | Yes | Person accepts the saved diff |
| Batch authoring | `ai_sankalp/llm.py` | #19, sequential first | Sonnet class | Yes | Per-video review, SME approval |
| Compiler (package to config to scene) | Python, `generator.py` | `app.py generate` | none | No | none |
| QA gates | Python, `ai_sankalp/qa` | `app.py qa` | none | No | SME approval is a gate |
| Captions, rendering | Python / Manim | `app.py generate --render` | none | No | Frame inspection |
| TTS | gTTS or Edge TTS via manim-voiceover | Render time | none (speech service) | Yes at first render, cached after | Listen to the render |

This issue builds and documents the adapter. Nothing calls it yet.

## Providers, models, and the quality bar

- **Default:** Anthropic Claude through the Messages API. Sonnet class for most
  work, Opus class for first drafts of a new topic family, Haiku class only for
  repairing small schema or syntax errors.
- **Alternative:** OpenAI. Documented only; no client exists in this repo yet.
  Its prices were not verified for this document.
- **Model IDs are never hardcoded.** The model comes from `AI_SANKALP_LLM_MODEL`
  because IDs go stale. Choose it from the provider's current model list.
- **Why not an SDK or a multi-provider framework yet:** an SDK adds a dependency
  and a clean-clone install step before any caller exists, and a framework such
  as LiteLLM is a lot of machinery for one call site. Either can sit behind the
  same `LLMClient` protocol later.

Minimum quality bar. A model is acceptable only if it:

1. Reliably produces a full package (about 26-34k tokens, see the cost section)
   that passes `validate_package`.
   More than one schema failure in three attempts on the two tracked fixtures
   (`examples/arrays_in_cpp`, `examples/python_for_loops`) is below the bar.
2. Writes correct code and expected output (checked by running the code where
   possible).
3. Produces packages that pass `app.py qa` and SME review.

## Cost per 5-minute video

LLM prices are from <https://platform.claude.com/docs/en/about-claude/pricing>,
checked 2026-10-03 (verified). Token counts are **estimates**, not measured
runs. Basis: in `examples/arrays_in_cpp`, `lesson_package.json` is 41,799 bytes
and `lesson_package.md` is 56,008 bytes, 97,807 bytes together. At about 3.8
bytes per token (an assumption) that is about 26k tokens, or about 34k with the
roughly 30% extra tokens that Claude 4.7+ tokenizers produce for the same text.

Per-video assumption:

| Pass | Input tokens | Output tokens |
|---|---|---|
| Draft (skill, schema and brief in, full package out) | about 20k | about 34k |
| Two revisions, each sends the package back and returns targeted patches | about 54k each | about 5k each |
| Total | about 128k | about 44k |

The 5k-per-revision figure assumes patches, not full rewrites. A full rewrite per
pass would roughly double output cost. This is the first number to measure.

| Model (price per million input / output) | Per 5-minute video | 50 videos, standard | 50 videos, Batch API (-50%) |
|---|---|---|---|
| Sonnet 5.5 ($2 / $10) | about $0.70 | about $35 | about $17 |
| Opus 5.5 ($4 / $20) | about $1.39 | about $70 | about $35 |
| Haiku 4.5 ($1 / $5), below the bar for drafting | about $0.35 | about $17 | about $9 |

- **Prompt caching:** cache reads cost 0.1x the input price (0.05x on Opus 5.5),
  which lowers input cost when the skill and schema prefix is reused. Not
  included in the table above.
- **Repair (#13):** assumes a repair prompt that carries only the failing section and
  its error, not the whole package: about 20k input and 5k output tokens per
  attempt, about $0.09 on Sonnet 5.5. Three attempts cost at most about $0.27.
- **Skill path (Codex or Claude Code):** billed to the operator's plan, not
  metered per token here. Plan prices were not verified.

### TTS

5 minutes at about 132 words per minute is about 660 words, about 4,000
characters; with up to 3 synthesis passes, about 12k characters. manim-voiceover
caches each segment, so unchanged text is not charged again.

| Option | Cost | Status |
|---|---|---|
| gTTS, Edge TTS (current) | $0 | Unofficial endpoints, no SLA, no key |
| OpenAI `tts-1` | about $15 per million characters, so about $0.06 to $0.18 per video | **Not verified** by this change |
| Azure Neural TTS | free tier of 0.5M characters per month (about 40-125 videos); paid rate unknown | **Not verified** by this change |

Adding a paid TTS provider needs a new `voiceover.provider` value with schema
and tests; it is out of scope here.

SME review time is the largest real cost and is not priced. All figures are
estimates; re-check prices and measure real token usage (`LLMResponse` reports
it) before a batch run.

## Keys and secrets

- Variables: `AI_SANKALP_LLM_PROVIDER`,
  `AI_SANKALP_LLM_MODEL`, `AI_SANKALP_LLM_TIMEOUT`, `ANTHROPIC_API_KEY`.
- Load order: an optional untracked `.env`, overridden by the process
  environment. `load_settings(dotenv_path=DEFAULT_DOTENV_PATH)` does this.
  `DEFAULT_DOTENV_PATH` is the repo-root `.env`. `.env` is read only when a
  path is passed, so tests stay deterministic and callers do not depend on the
  working directory.
- `.env` and `.env.*` are gitignored (`.env.example` is exempt so a template can
  be added later; none is tracked yet).
- Each developer uses their own key. There is no shared key in the repo, CI or
  hooks. Batch runs (#19) use the maintainer's account.
- The key is never logged, never in a `repr`, and never in an error message.
- The guard hook `.claude/hooks/guard_bash.py` also blocks staging `.env`
  files in Claude Code sessions.

## Privacy

What may be sent to a provider: the topic, package drafts, compact error tails,
and repo-relative paths. Never `.env` contents, absolute local paths, or
learner data.

## Rate limits

Calls are sequential. #19 runs sequentially first, with the Batch API as an
option for large runs. The adapter does not retry; callers own retry and budget
policy (#13, #19) so it lives in one place.

## Offline and degraded behavior

- Provider `none` or a missing key: everything except AI calls works.
  `build_client()` raises `LLMConfigError` naming the missing variable and
  stating that generate, render and qa still work.
- LLM outage, network error, timeout, 408, 429 or 5xx: callers get
  `LLMUnavailableError`. #13 and #19 record the failure and skip or fail that
  one job; they do not hang.
- A rejected key or model (`authentication_error`, `permission_error`,
  `not_found_error`; HTTP 401, 403, 404): callers get `LLMConfigError` naming
  `ANTHROPIC_API_KEY` and `AI_SANKALP_LLM_MODEL` with the API's error type. A
  billing problem (`billing_error`, HTTP 402) is also an `LLMConfigError` that
  mentions billing and spend limits. Every call will fail, so a batch must stop
  the whole run.
- A bad single request (`invalid_request_error`, HTTP 400, or 413, for example a
  prompt that is too long): a plain `LLMError` carrying the API's message. Only
  that job fails; a batch records it and continues.
- A response cut off at `max_tokens`: `LLMResponse.stop_reason` is
  `"max_tokens"`. Callers must check it before parsing the text.
- Fallbacks when the LLM cannot be used: hand-edit the package JSON, or start
  from the tracked examples.
- TTS outage: cached audio is reused. Otherwise render with `--no-voiceover`,
  generate captions from the narration, or switch between gTTS and Edge TTS.
- Tests never use the network (`FakeLLMClient`, injected transport).

## Human review points

1. After the Planner draft, a person reads the package `.md` and `.json` before
   compiling.
2. Every AI repair is saved as a snapshot or diff and a person accepts it
   before a final render.
3. A person inspects frames from the low-quality render.
4. SME approval is enforced by the existing `sme_approval` QA check. AI must
   **never** set `review_status.sme_approved`, `sme_reviewer` or
   `sme_approved_on`. This rule binds #13 and #15.

## Integration contract

`ai_sankalp/llm.py` exposes:

- `LLMRequest(system, prompt, max_output_tokens, purpose)` and
  `LLMResponse(text, provider, model, input_tokens, output_tokens, stop_reason)`.
- `LLMClient` protocol with `complete(request) -> LLMResponse`.
- `load_settings(env=None, dotenv_path=None)` and `build_client(settings)`.
- `FakeLLMClient(responses)` for offline tests; it records requests.
- Errors, all subclasses of `LLMError`: `LLMConfigError` (not configured, or
  the key or model was rejected, or billing failed; retrying will not help) and
  `LLMUnavailableError` (network error, 408, 429, 5xx; retry later). Any other
  failure, including a bad single request, is a plain `LLMError`.

Callers get a client with `build_client(load_settings(dotenv_path=DEFAULT_DOTENV_PATH))` and in
tests use `FakeLLMClient`. The real HTTP path (Anthropic Messages API) is
unit-tested through an injected transport; it has not been exercised against the
live API in CI.

## Out of scope and follow-ups

OpenAI client, retry/backoff/budget caps (#13, #19), Python Planner (#15), an
`app.py check` line for LLM status, cost logging to `history.jsonl` (#19),
prompt caching and Batch API support in the adapter, paid TTS providers.

Known limitations of the adapter: no streaming, and one socket timeout
(default 120 s, `AI_SANKALP_LLM_TIMEOUT`). Anthropic recommends streaming or the
Batch API for very long outputs, so #15 and #19 should raise the timeout or add
streaming before generating full packages.
