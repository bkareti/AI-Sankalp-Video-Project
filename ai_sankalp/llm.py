"""Optional Python-side LLM adapter (see docs/ai-architecture.md).

Nothing in the app calls this yet; it is the stable integration target for
repair (#13), planner (#15), UI (#18) and batch (#19). The default provider is
``none``, so every existing command works without a key or a network.

Standard library only. The adapter does not retry: retry and budget policy
belong to the callers so they live in one place.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

ENV_PROVIDER = "AI_SANKALP_LLM_PROVIDER"
ENV_MODEL = "AI_SANKALP_LLM_MODEL"
ENV_ANTHROPIC_KEY = "ANTHROPIC_API_KEY"
ENV_TIMEOUT = "AI_SANKALP_LLM_TIMEOUT"
PROVIDERS = ("none", "anthropic")
DEFAULT_TIMEOUT_S = 120.0
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DOC_HINT = "see docs/ai-architecture.md"

# transport(url, headers, body, timeout_s) -> (http_status, response_body_bytes)
Transport = Callable[[str, Mapping[str, str], bytes, float], tuple[int, bytes]]


class LLMError(RuntimeError):
    """Base class for adapter errors. Messages never contain the API key."""


class LLMConfigError(LLMError):
    """The provider, model or key is not configured."""


class LLMUnavailableError(LLMError):
    """The provider could not be reached or rejected the call (timeout, 429, 5xx)."""


@dataclass(frozen=True)
class LLMSettings:
    provider: str = "none"
    model: str | None = None
    api_key: str | None = field(default=None, repr=False)
    timeout_s: float = DEFAULT_TIMEOUT_S


@dataclass(frozen=True)
class LLMRequest:
    system: str
    prompt: str
    max_output_tokens: int
    purpose: str = ""


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int


class LLMClient(Protocol):
    def complete(self, request: LLMRequest) -> LLMResponse: ...


def parse_dotenv(text: str) -> dict[str, str]:
    """Parse KEY=VALUE lines. Supports comments, an `export ` prefix and quotes."""
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def load_settings(env: Mapping[str, str] | None = None, dotenv_path: Path | None = None) -> LLMSettings:
    """Build settings from `.env` (optional) overlaid by the process environment."""
    merged: dict[str, str] = {}
    if dotenv_path is not None and Path(dotenv_path).is_file():
        merged.update(parse_dotenv(Path(dotenv_path).read_text(encoding="utf-8")))
    merged.update(os.environ if env is None else env)
    try:
        timeout = float(merged.get(ENV_TIMEOUT) or DEFAULT_TIMEOUT_S)
    except ValueError as exc:
        raise LLMConfigError(f"{ENV_TIMEOUT} must be a number of seconds; {DOC_HINT}.") from exc
    return LLMSettings(
        provider=(merged.get(ENV_PROVIDER) or "none").strip().lower(),
        model=(merged.get(ENV_MODEL) or "").strip() or None,
        api_key=(merged.get(ENV_ANTHROPIC_KEY) or "").strip() or None,
        timeout_s=timeout,
    )


class FakeLLMClient:
    """Offline client for tests: returns queued responses and records requests."""

    def __init__(self, responses: list[str], provider: str = "fake", model: str = "fake-model") -> None:
        self._responses = list(responses)
        self.provider = provider
        self.model = model
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if not self._responses:
            raise LLMError("FakeLLMClient has no queued responses left.")
        return LLMResponse(self._responses.pop(0), self.provider, self.model, 0, 0)


def _urllib_transport(url: str, headers: Mapping[str, str], body: bytes, timeout_s: float) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


class AnthropicClient:
    def __init__(self, settings: LLMSettings, transport: Transport | None = None) -> None:
        if not settings.api_key or not settings.model:
            raise LLMConfigError(f"AnthropicClient needs a key and a model; {DOC_HINT}.")
        self._settings = settings
        self._transport = transport or _urllib_transport

    def complete(self, request: LLMRequest) -> LLMResponse:
        settings = self._settings
        body = json.dumps({
            "model": settings.model,
            "max_tokens": request.max_output_tokens,
            "system": request.system,
            "messages": [{"role": "user", "content": request.prompt}],
        }).encode("utf-8")
        headers = {
            "content-type": "application/json",
            "x-api-key": settings.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
        }
        try:
            status, raw = self._transport(ANTHROPIC_URL, headers, body, settings.timeout_s)
        except (TimeoutError, urllib.error.URLError, OSError) as exc:
            raise LLMUnavailableError(f"Anthropic request failed: {type(exc).__name__}.") from None
        if status >= 400:
            raise LLMUnavailableError(f"Anthropic returned HTTP {status}.")
        try:
            data = json.loads(raw)
            text = "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
            usage = data.get("usage", {})
            return LLMResponse(text, "anthropic", settings.model, int(usage.get("input_tokens", 0)),
                               int(usage.get("output_tokens", 0)))
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            raise LLMError(f"Anthropic returned an unreadable response ({type(exc).__name__}).") from None


def build_client(settings: LLMSettings, transport: Transport | None = None) -> LLMClient:
    """Return a client for `settings`, or raise `LLMConfigError` with the fix."""
    if settings.provider == "none":
        raise LLMConfigError(
            f"AI calls are disabled. Set {ENV_PROVIDER} to one of {', '.join(PROVIDERS[1:])} to enable them "
            f"({DOC_HINT}). The non-AI pipeline (generate, render, qa) still works."
        )
    if settings.provider not in PROVIDERS:
        raise LLMConfigError(
            f"Unknown {ENV_PROVIDER} '{settings.provider}'. Valid values: {', '.join(PROVIDERS)} ({DOC_HINT})."
        )
    if not settings.model:
        raise LLMConfigError(f"{ENV_MODEL} is not set; choose a model explicitly ({DOC_HINT}).")
    if not settings.api_key:
        raise LLMConfigError(
            f"{ENV_ANTHROPIC_KEY} is not set for provider '{settings.provider}' ({DOC_HINT}). "
            "The non-AI pipeline (generate, render, qa) still works without it."
        )
    return AnthropicClient(settings, transport)
