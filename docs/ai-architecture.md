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

1. Reliably produces a 20-30k-token package that passes `validate_package`.
   More than one schema failure in three attempts on the two tracked fixtures
   (`examples/arrays_in_cpp`, `examples/python_for_loops`) is below the bar.
2. Writes correct code and expected output (checked by running the code where
   possible).
3. Produces packages that pass `app.py qa` and SME review.

## Cost per 5-minute video

LLM prices are from <https://platform.claude.com/docs/en/about-claude/pricing>,
checked 2026-10-03 (verified). Token counts are **estimates**, not measured
runs: `examples/arrays_in_cpp/lesson_package.json` is 785 lines (about 11k
tokens) and its `.md` about 10k; Claude 4.7+ tokenizers produce roughly 30% more
tokens for the same text. Assumption: one draft plus two revisions is about
90k input and 45k output tokens per video.

| Model (price per million input / output) | Per 5-minute video | 50 videos, standard | 50 videos, Batch API (-50%) |
|---|---|---|---|
| Sonnet 5.5 ($2 / $10) | about $0.63 | about $32 | about $16 |
| Opus 5.5 ($4 / $20) | about $1.26 | about $63 | about $32 |
| Haiku 4.5 ($1 / $5), below the bar for drafting | about $0.32 | about $16 | about $8 |

- **Prompt caching:** cache reads cost 0.1x the input price (0.05x on Opus 5.5),
  which lowers input cost when the skill and schema prefix is reused. Not
  included in the table above.
- **Repair (#13):** each attempt is about 20k input and 5k output tokens, about
  $0.09 on Sonnet 5.5. Three attempts cost at most about $0.27.
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
  environment. `load_settings()` does this.
- `.env` and `.env.*` are gitignored (`.env.example` is exempt so a template can
  be added later; none is tracked yet).
- Each developer uses their own key. There is no shared key in the repo, CI or
  hooks. Batch runs (#19) use the maintainer's account.
- The key is never logged, never in a `repr`, and never in an error message.
- Existing guard hooks in `.claude/hooks` and `.codex/hooks` also block staging
  `.env` files.

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
- LLM outage, timeout, 429 or 5xx: callers get `LLMUnavailableError`. #13 and
  #19 record the failure and skip or fail that one job; they do not hang.
  Fallbacks: hand-edit the package JSON, or start from the tracked examples.
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
  `LLMResponse(text, provider, model, input_tokens, output_tokens)`.
- `LLMClient` protocol with `complete(request) -> LLMResponse`.
- `load_settings(env=None, dotenv_path=None)` and `build_client(settings)`.
- `FakeLLMClient(responses)` for offline tests; it records requests.
- Errors: `LLMConfigError` (not configured) and `LLMUnavailableError` (cannot
  reach or rejected), both subclasses of `LLMError`.

Callers get a client with `build_client(load_settings(dotenv_path=...))` and in
tests use `FakeLLMClient`. The real HTTP path (Anthropic Messages API) is
unit-tested through an injected transport; it has not been exercised against the
live API in CI.

## Out of scope and follow-ups

OpenAI client, retry/backoff/budget caps (#13, #19), Python Planner (#15), an
`app.py check` line for LLM status, cost logging to `history.jsonl` (#19),
prompt caching and Batch API support in the adapter, paid TTS providers.
