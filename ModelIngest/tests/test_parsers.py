"""阶段 A 解析器注册表测试（不依赖真实 mineru/docling/marker/markitdown）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from modelingest import parsers
from modelingest.parsers import ConversionError, convert_to_markdown


def test_passthrough_for_text(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_text("hello world", encoding="utf-8")
    text, name = convert_to_markdown(f)
    assert "hello world" in text
    assert name == "passthrough"


def test_priority_env_override(monkeypatch):
    monkeypatch.setenv("INGEST_PDF_PARSER", "docling, markitdown")
    assert parsers._priority() == ["docling", "markitdown"]

    monkeypatch.setenv("INGEST_PDF_PARSER", "bogus")
    # 非法名过滤后为空 → 退回默认。
    assert parsers._priority() == list(parsers._DEFAULT_PRIORITY)


def test_registry_degrades_to_next(monkeypatch, tmp_path: Path):
    """前一个解析器返回 None，应降级到后一个。"""
    calls = []

    def fake_a(path):
        calls.append("a")
        return None

    def fake_b(path):
        calls.append("b")
        return "# ok"

    monkeypatch.setitem(parsers._REGISTRY, "mineru", fake_a)
    monkeypatch.setitem(parsers._REGISTRY, "docling", fake_b)
    monkeypatch.setenv("INGEST_PDF_PARSER", "mineru,docling")

    f = tmp_path / "x.pdf"
    f.write_bytes(b"%PDF-1.4 dummy")
    text, name = convert_to_markdown(f)
    assert text == "# ok"
    assert name == "docling"
    assert calls == ["a", "b"]


def test_parser_exception_does_not_break_chain(monkeypatch, tmp_path: Path):
    def boom(path):
        raise RuntimeError("kaboom")

    def ok(path):
        return "recovered"

    monkeypatch.setitem(parsers._REGISTRY, "mineru", boom)
    monkeypatch.setitem(parsers._REGISTRY, "markitdown", ok)
    monkeypatch.setenv("INGEST_PDF_PARSER", "mineru,markitdown")

    f = tmp_path / "x.pdf"
    f.write_bytes(b"%PDF dummy")
    text, name = convert_to_markdown(f)
    assert text == "recovered"
    assert name == "markitdown"


def test_all_fail_raises(monkeypatch, tmp_path: Path):
    monkeypatch.setitem(parsers._REGISTRY, "markitdown", lambda p: None)
    monkeypatch.setenv("INGEST_PDF_PARSER", "markitdown")
    f = tmp_path / "x.pdf"
    f.write_bytes(b"%PDF dummy")
    with pytest.raises(ConversionError):
        convert_to_markdown(f)
