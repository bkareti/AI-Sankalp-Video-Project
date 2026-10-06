import http.client
import json
import re
import subprocess
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

from ai_sankalp import llm
from ai_sankalp.llm import (
    ANTHROPIC_URL,
    DEFAULT_DOTENV_PATH,
    AnthropicClient,
    FakeLLMClient,
    LLMConfigError,
    LLMError,
    LLMRequest,
    LLMSettings,
    LLMUnavailableError,
    build_client,
    load_settings,
    parse_dotenv,
)

ROOT = Path(__file__).resolve().parents[1]
SECRET = "sk-test-SECRET-123"
REQUEST = LLMRequest(system="sys", prompt="hello", max_output_tokens=50, purpose="test")


def ok_body(text="hi", **usage):
    return json.dumps({"content": [{"type": "text", "text": text}, {"type": "tool_use"}],
                       "usage": usage or {"input_tokens": 3, "output_tokens": 4}}).encode()


def settings(**kw):
    base = {"provider": "anthropic", "model": "m-1", "api_key": SECRET}
    base.update(kw)
    return LLMSettings(**base)


class ConfigErrorTests(unittest.TestCase):
    def test_missing_api_key_error_names_variable_and_doc(self):
        with self.assertRaises(LLMConfigError) as ctx:
            build_client(settings(api_key=None))
        message = str(ctx.exception)
        self.assertIn("ANTHROPIC_API_KEY", message)
        self.assertIn("docs/ai-architecture.md", message)
        self.assertIn("still works", message)

    def test_missing_model_error(self):
        with self.assertRaises(LLMConfigError) as ctx:
            build_client(settings(model=None))
        self.assertIn("AI_SANKALP_LLM_MODEL", str(ctx.exception))

    def test_provider_none_is_disabled_error(self):
        with self.assertRaises(LLMConfigError) as ctx:
            build_client(LLMSettings())
        self.assertIn("AI_SANKALP_LLM_PROVIDER", str(ctx.exception))
        self.assertIn("disabled", str(ctx.exception))

    def test_unknown_provider_lists_valid_values(self):
        with self.assertRaises(LLMConfigError) as ctx:
            build_client(settings(provider="mystery"))
        self.assertIn("none, anthropic", str(ctx.exception))

    def test_bad_timeout_is_a_config_error(self):
        for value in ("soon", "-5", "0", "nan", "inf"):
            with self.subTest(value=value), self.assertRaises(LLMConfigError):
                load_settings(env={"AI_SANKALP_LLM_TIMEOUT": value})

    def test_anthropic_client_error_names_variables(self):
        with self.assertRaises(LLMConfigError) as ctx:
            AnthropicClient(LLMSettings(provider="anthropic"))
        self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))
        self.assertIn("AI_SANKALP_LLM_MODEL", str(ctx.exception))

    def test_defaults_are_disabled(self):
        loaded = load_settings(env={})
        self.assertEqual(loaded.provider, "none")
        self.assertIsNone(loaded.api_key)


class SettingsTests(unittest.TestCase):
    def test_dotenv_values_loaded_and_process_env_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text('# comment\nAI_SANKALP_LLM_PROVIDER=anthropic\n'
                            'export AI_SANKALP_LLM_MODEL="from-file"\nANTHROPIC_API_KEY=\'file-key\'\n',
                            encoding="utf-8")
            loaded = load_settings(env={"AI_SANKALP_LLM_MODEL": "from-env"}, dotenv_path=path)
        self.assertEqual(loaded.provider, "anthropic")
        self.assertEqual(loaded.model, "from-env")
        self.assertEqual(loaded.api_key, "file-key")

    def test_missing_dotenv_file_is_ok(self):
        loaded = load_settings(env={}, dotenv_path=ROOT / "does-not-exist.env")
        self.assertEqual(loaded.provider, "none")

    def test_parse_dotenv_ignores_blank_and_malformed_lines(self):
        self.assertEqual(parse_dotenv("\n# x\nnoequals\nA=1\n"), {"A": "1"})

    def test_parse_dotenv_strips_inline_comments_but_not_quoted_hashes(self):
        parsed = parse_dotenv('A=abc # my key\nB="x # y"\nC=a#b\n')
        self.assertEqual(parsed, {"A": "abc", "B": "x # y", "C": "a#b"})

    def test_default_dotenv_path_is_repo_root_and_not_read_implicitly(self):
        self.assertEqual(DEFAULT_DOTENV_PATH, ROOT / ".env")
        with mock.patch.object(Path, "read_text", side_effect=AssertionError(".env read")):
            self.assertEqual(load_settings(env={}).provider, "none")

    def test_settings_repr_and_errors_never_contain_key(self):
        self.assertNotIn(SECRET, repr(settings()))
        failures = [
            (400, b"{}"), (429, b"{}"), (500, b"{}"), (200, b"not json"),
        ]
        for status, body in failures:
            client = AnthropicClient(settings(), transport=lambda *a, _s=status, _b=body: (_s, _b))
            with self.assertRaises(LLMError) as ctx:
                client.complete(REQUEST)
            self.assertNotIn(SECRET, str(ctx.exception))


class AnthropicClientTests(unittest.TestCase):
    def test_request_shape_via_fake_transport(self):
        seen = {}

        def transport(url, headers, body, timeout_s):
            seen.update(url=url, headers=dict(headers), body=json.loads(body), timeout=timeout_s)
            return 200, ok_body()

        AnthropicClient(settings(timeout_s=9.0), transport).complete(REQUEST)
        self.assertEqual(seen["url"], ANTHROPIC_URL)
        self.assertEqual(seen["headers"]["x-api-key"], SECRET)
        self.assertEqual(seen["headers"]["anthropic-version"], llm.ANTHROPIC_VERSION)
        self.assertEqual(seen["body"], {"model": "m-1", "max_tokens": 50, "system": "sys",
                                        "messages": [{"role": "user", "content": "hello"}]})
        self.assertEqual(seen["timeout"], 9.0)

    def test_response_parsing_text_and_usage(self):
        client = build_client(settings(), transport=lambda *a: (200, ok_body("done", input_tokens=7, output_tokens=2)))
        response = client.complete(REQUEST)
        self.assertEqual((response.text, response.provider, response.model), ("done", "anthropic", "m-1"))
        self.assertEqual((response.input_tokens, response.output_tokens), (7, 2))
        self.assertIsNone(response.stop_reason)

    def test_stop_reason_is_reported(self):
        body = json.dumps({"content": [{"type": "text", "text": "cut"}], "stop_reason": "max_tokens"}).encode()
        response = AnthropicClient(settings(), transport=lambda *a: (200, body)).complete(REQUEST)
        self.assertEqual(response.stop_reason, "max_tokens")

    def test_http_429_and_500_raise_unavailable(self):
        for status in (429, 500, 503):
            client = AnthropicClient(settings(), transport=lambda *a, _s=status: (_s, b"{}"))
            with self.assertRaises(LLMUnavailableError) as ctx:
                client.complete(REQUEST)
            self.assertIn(str(status), str(ctx.exception))

    def test_rejected_credentials_or_model_raise_config_error_naming_variables(self):
        body = json.dumps({"error": {"type": "not_found_error", "message": "model: m-1"}}).encode()
        for status in (400, 401, 403, 404):
            client = AnthropicClient(settings(), transport=lambda *a, _s=status: (_s, body))
            with self.assertRaises(LLMConfigError) as ctx:
                client.complete(REQUEST)
            message = str(ctx.exception)
            self.assertIn(str(status), message)
            self.assertIn("ANTHROPIC_API_KEY", message)
            self.assertIn("AI_SANKALP_LLM_MODEL", message)
            self.assertIn("not_found_error", message)
            self.assertNotIsInstance(ctx.exception, LLMUnavailableError)

    def test_408_and_529_are_unavailable_and_other_4xx_is_plain_error(self):
        for status in (408, 529):
            client = AnthropicClient(settings(), transport=lambda *a, _s=status: (_s, b"{}"))
            with self.assertRaises(LLMUnavailableError):
                client.complete(REQUEST)
        client = AnthropicClient(settings(), transport=lambda *a: (413, b"{}"))
        with self.assertRaises(LLMError) as ctx:
            client.complete(REQUEST)
        self.assertNotIsInstance(ctx.exception, (LLMUnavailableError, LLMConfigError))

    def test_error_detail_that_echoes_the_key_is_dropped(self):
        body = json.dumps({"error": {"type": "authentication_error", "message": f"bad {SECRET}"}}).encode()
        client = AnthropicClient(settings(), transport=lambda *a: (401, body))
        with self.assertRaises(LLMConfigError) as ctx:
            client.complete(REQUEST)
        self.assertNotIn(SECRET, str(ctx.exception))

    def test_timeout_and_network_errors_raise_unavailable(self):
        errors = (TimeoutError("slow"), urllib.error.URLError("down"), http.client.IncompleteRead(b"x"),
                  http.client.BadStatusLine("x"))
        for exc in errors:
            def transport(*args, _e=exc):
                raise _e
            with self.assertRaises(LLMUnavailableError):
                AnthropicClient(settings(), transport).complete(REQUEST)

    def test_malformed_json_raises_llm_error(self):
        for body in (b"not json", b'{"nope": 1}'):
            client = AnthropicClient(settings(), transport=lambda *a, _b=body: (200, _b))
            with self.assertRaises(LLMError) as ctx:
                client.complete(REQUEST)
            self.assertNotIsInstance(ctx.exception, LLMUnavailableError)

    def test_default_transport_not_used_in_tests(self):
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            client = AnthropicClient(settings(), transport=lambda *a: (200, ok_body()))
            self.assertEqual(client.complete(REQUEST).text, "hi")

    def test_default_transport_success_path_returns_status_and_body(self):
        resp = mock.MagicMock()
        resp.__enter__.return_value = resp
        resp.status = 200
        resp.read.return_value = ok_body("net")
        with mock.patch("urllib.request.urlopen", return_value=resp) as urlopen:
            response = AnthropicClient(settings()).complete(REQUEST)
        self.assertEqual(response.text, "net")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], llm.DEFAULT_TIMEOUT_S)

    def test_default_transport_turns_http_error_into_status(self):
        error = urllib.error.HTTPError(ANTHROPIC_URL, 429, "limit", {}, None)
        error.read = lambda: b"{}"
        with mock.patch("urllib.request.urlopen", side_effect=error), self.assertRaises(LLMUnavailableError) as ctx:
            AnthropicClient(settings()).complete(REQUEST)
        self.assertIn("429", str(ctx.exception))


class FakeClientTests(unittest.TestCase):
    def test_fake_client_returns_queued_responses_and_records_requests(self):
        fake = FakeLLMClient(["a", "b"])
        self.assertEqual(fake.complete(REQUEST).text, "a")
        self.assertEqual(fake.complete(REQUEST).text, "b")
        self.assertEqual(fake.requests, [REQUEST, REQUEST])
        with self.assertRaises(LLMError):
            fake.complete(REQUEST)


class RepoHygieneTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / ".git").exists(), "needs a git checkout")
    def test_gitignore_ignores_env_but_not_example(self):
        def ignored(name):
            return subprocess.run(["git", "check-ignore", "-q", name], cwd=ROOT, check=False).returncode == 0
        self.assertTrue(ignored(".env"))
        self.assertTrue(ignored(".env.local"))
        self.assertFalse(ignored(".env.example"))

    def test_ai_architecture_doc_mentions_every_env_variable(self):
        doc = (ROOT / "docs" / "ai-architecture.md").read_text(encoding="utf-8")
        for name in (llm.ENV_PROVIDER, llm.ENV_MODEL, llm.ENV_TIMEOUT, llm.ENV_ANTHROPIC_KEY):
            self.assertIn(name, doc)

    def test_readme_links_the_architecture_doc(self):
        self.assertIn("docs/ai-architecture.md", (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_no_hardcoded_keys_in_adapter_doc_or_readme(self):
        key_shape = re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}")
        self.assertIsNotNone(key_shape.search("sk-ant-api03-" + "A" * 40))
        for path in ("ai_sankalp/llm.py", "tests/test_llm.py", "docs/ai-architecture.md", "README.md"):
            self.assertIsNone(key_shape.search((ROOT / path).read_text(encoding="utf-8")), path)


if __name__ == "__main__":
    unittest.main()
