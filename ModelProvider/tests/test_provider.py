"""ModelProvider 单元测试（离线，注入假传输）。"""
from __future__ import annotations

import os

import pytest

from modelprovider import ChatRequest, LLMClient, Message
from modelprovider import http as mp_http
from modelprovider import config as mp_config


@pytest.fixture(autouse=True)
def _keys(monkeypatch):
    # 给需要 key 的 provider 塞假 key，让 resolve 通过。
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setenv("GEMINI_API_KEY", "sk-test")


def _install_transport(monkeypatch, capture: dict, response: dict):
    def fake(method, url, headers, json_body, timeout):
        capture["method"] = method
        capture["url"] = url
        capture["headers"] = headers
        capture["body"] = json_body
        return 200, response
    monkeypatch.setattr(mp_http, "TRANSPORT", fake)


def test_openai_compat_roundtrip(monkeypatch):
    cap: dict = {}
    resp = {
        "model": "gpt-4o-mini",
        "choices": [{"message": {"content": "hi there"}}],
        "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
    }
    _install_transport(monkeypatch, cap, resp)
    client = LLMClient.for_provider("openai", load_env=False)
    out = client.ask("hello", system="be terse")
    assert out == "hi there"
    assert cap["url"].endswith("/chat/completions")
    assert cap["headers"]["Authorization"] == "Bearer sk-test"
    # system 应作为第一条消息
    assert cap["body"]["messages"][0]["role"] == "system"


def test_deepseek_uses_own_base(monkeypatch):
    cap: dict = {}
    _install_transport(
        monkeypatch, cap,
        {"choices": [{"message": {"content": "ok"}}]},
    )
    client = LLMClient.for_provider("deepseek", load_env=False)
    client.ask("x")
    assert "api.deepseek.com" in cap["url"]


def test_anthropic_splits_system(monkeypatch):
    cap: dict = {}
    resp = {
        "model": "claude-3-5-sonnet-latest",
        "content": [{"type": "text", "text": "answer"}],
        "usage": {"input_tokens": 4, "output_tokens": 1},
    }
    _install_transport(monkeypatch, cap, resp)
    client = LLMClient.for_provider("anthropic", load_env=False)
    out = client.ask("q", system="sys")
    assert out == "answer"
    assert cap["body"]["system"] == "sys"
    assert cap["headers"]["x-api-key"] == "sk-test"
    assert all(m["role"] != "system" for m in cap["body"]["messages"])


def test_gemini_maps_roles_and_key(monkeypatch):
    cap: dict = {}
    resp = {
        "candidates": [
            {"content": {"parts": [{"text": "g-answer"}]}}
        ],
        "usageMetadata": {
            "promptTokenCount": 2,
            "candidatesTokenCount": 3,
            "totalTokenCount": 5,
        },
    }
    _install_transport(monkeypatch, cap, resp)
    client = LLMClient.for_provider("gemini", load_env=False)
    out = client.ask(
        [Message.assistant("prev"), Message.user("now")], system="sys"
    )
    assert out == "g-answer"
    assert "key=sk-test" in cap["url"]
    assert cap["body"]["systemInstruction"]["parts"][0]["text"] == "sys"
    # assistant -> model
    assert cap["body"]["contents"][0]["role"] == "model"


def test_ollama_needs_no_key(monkeypatch):
    cap: dict = {}
    _install_transport(
        monkeypatch, cap, {"choices": [{"message": {"content": "local"}}]}
    )
    client = LLMClient.for_provider("ollama", load_env=False)
    out = client.ask("hi")
    assert out == "local"
    assert "localhost:11434" in cap["url"]
    assert "Authorization" not in cap["headers"]


def test_multimodal_image_part(monkeypatch):
    from modelprovider import ImagePart

    cap: dict = {}
    _install_transport(
        monkeypatch, cap, {"choices": [{"message": {"content": "seen"}}]}
    )
    client = LLMClient.for_provider("openai", load_env=False)
    img = ImagePart.from_bytes(b"\x89PNG", mime="image/png")
    from modelprovider import TextPart

    msg = Message("user", [TextPart("看这张图"), img])
    client.chat(ChatRequest(messages=[msg]))
    content = cap["body"]["messages"][0]["content"]
    assert any(part["type"] == "image_url" for part in content)


def test_role_resolution(monkeypatch):
    monkeypatch.setenv("MODELTOOLBOX_TEACHER", "deepseek:deepseek-chat")
    cfg = mp_config.resolve_role("teacher")
    assert cfg.spec.name == "deepseek"
    assert cfg.model == "deepseek-chat"


def test_unknown_provider_raises():
    with pytest.raises(KeyError):
        mp_config.resolve("nope")


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        mp_config.resolve("openai")


def test_claude_code_needs_no_key(monkeypatch):
    # cli_agent provider 不需要 API key，即便完全没设置任何 key 也应能 resolve。
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cfg = mp_config.resolve("claude_code")
    assert cfg.spec.kind == "cli_agent"
    assert cfg.api_key is None


def test_claude_code_cli_roundtrip(monkeypatch):
    from modelprovider.providers import cli_agent as mp_cli_agent

    captured: dict = {}

    class _FakeCompletedProcess:
        returncode = 0
        stdout = "hello from claude code\n"
        stderr = ""

    def fake_run(argv, capture_output, text, timeout):
        captured["argv"] = argv
        captured["timeout"] = timeout
        return _FakeCompletedProcess()

    monkeypatch.setattr(mp_cli_agent.subprocess, "run", fake_run)
    client = LLMClient.for_provider("claude_code", load_env=False)
    out = client.ask("你好", system="be terse")

    assert out == "hello from claude code"
    assert captured["argv"][0] == "claude"
    assert "-p" in captured["argv"]
    assert any("你好" in a for a in captured["argv"])


def test_codex_cli_uses_own_argv_template(monkeypatch):
    from modelprovider.providers import cli_agent as mp_cli_agent

    captured: dict = {}

    class _FakeCompletedProcess:
        returncode = 0
        stdout = "codex says hi"
        stderr = ""

    def fake_run(argv, capture_output, text, timeout):
        captured["argv"] = argv
        return _FakeCompletedProcess()

    monkeypatch.setattr(mp_cli_agent.subprocess, "run", fake_run)
    client = LLMClient.for_provider("codex", load_env=False)
    out = client.ask("q")

    assert out == "codex says hi"
    assert captured["argv"][:2] == ["codex", "exec"]


def test_cli_agent_argv_override_via_env(monkeypatch):
    from modelprovider.providers import cli_agent as mp_cli_agent

    monkeypatch.setenv("MODELTOOLBOX_CLAUDE_CODE_CMD", "myclaude --print {prompt}")
    captured: dict = {}

    class _FakeCompletedProcess:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(argv, capture_output, text, timeout):
        captured["argv"] = argv
        return _FakeCompletedProcess()

    monkeypatch.setattr(mp_cli_agent.subprocess, "run", fake_run)
    client = LLMClient.for_provider("claude_code", load_env=False)
    client.ask("hi")

    assert captured["argv"][0] == "myclaude"
    assert captured["argv"][1] == "--print"


def test_cli_agent_nonzero_exit_raises(monkeypatch):
    from modelprovider.providers import cli_agent as mp_cli_agent

    class _FakeCompletedProcess:
        returncode = 1
        stdout = ""
        stderr = "not logged in"

    monkeypatch.setattr(
        mp_cli_agent.subprocess, "run",
        lambda *a, **k: _FakeCompletedProcess(),
    )
    client = LLMClient.for_provider("codex", load_env=False)
    with pytest.raises(mp_cli_agent.CLIAgentError, match="not logged in"):
        client.ask("hi")


def test_cli_agent_missing_binary_raises(monkeypatch):
    from modelprovider.providers import cli_agent as mp_cli_agent

    def fake_run(*a, **k):
        raise FileNotFoundError()

    monkeypatch.setattr(mp_cli_agent.subprocess, "run", fake_run)
    client = LLMClient.for_provider("claude_code", load_env=False)
    with pytest.raises(mp_cli_agent.CLIAgentError):
        client.ask("hi")
