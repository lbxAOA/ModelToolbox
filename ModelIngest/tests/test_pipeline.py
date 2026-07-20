"""ModelIngest 单元测试（不依赖 markitdown / PyMuPDF，用 .txt 直通路径验证核心逻辑）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from modelingest.config import IngestConfig
from modelingest import pipeline
from modelingest.frontmatter import build_frontmatter
from modelingest.manifest import Manifest, sha256_file


def _mk_source(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    (src / "sub").mkdir(parents=True)
    (src / "a.txt").write_text("hello alpha", encoding="utf-8")
    (src / "sub" / "b.txt").write_text("nested beta", encoding="utf-8")
    return src


def test_run_converts_txt_with_frontmatter(tmp_path: Path):
    src = _mk_source(tmp_path)
    out = tmp_path / "out"
    cfg = IngestConfig(source_root=src, output_root=out)

    summary = pipeline.run(cfg)
    assert summary.converted == 2
    assert summary.failed == 0

    a_md = out / "a.md"
    assert a_md.exists()
    text = a_md.read_text(encoding="utf-8")
    assert text.startswith("---")
    assert "source: a.txt" in text
    assert "converter: passthrough" in text
    assert "hello alpha" in text
    # 镜像目录结构
    assert (out / "sub" / "b.md").exists()


def test_incremental_skip_and_rechange(tmp_path: Path):
    src = _mk_source(tmp_path)
    out = tmp_path / "out"
    cfg = IngestConfig(source_root=src, output_root=out)

    assert pipeline.run(cfg).converted == 2
    # 第二次运行：内容未变，应全部跳过
    second = pipeline.run(cfg)
    assert second.converted == 0
    assert second.skipped == 2

    # 修改一个文件 → 只重转它
    (src / "a.txt").write_text("hello CHANGED", encoding="utf-8")
    third = pipeline.run(cfg)
    assert third.converted == 1
    assert third.skipped == 1


def test_status_and_clean(tmp_path: Path):
    src = _mk_source(tmp_path)
    out = tmp_path / "out"
    cfg = IngestConfig(source_root=src, output_root=out)
    pipeline.run(cfg)

    # 删除源文件后：status 报告 stale，clean 清理
    (src / "a.txt").unlink()
    st = pipeline.status(cfg)
    assert st["stale_source_deleted"] == 1
    assert "a.txt" in st["stale_list"]

    removed = pipeline.clean(cfg)
    assert removed == 1
    assert not (out / "a.md").exists()


def test_sha256_stable(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_text("abc", encoding="utf-8")
    assert sha256_file(f) == sha256_file(f)


def test_frontmatter_escapes_special():
    fm = build_frontmatter(source="a: weird.pdf", sha256="deadbeef", converter="markitdown")
    assert 'source: "a: weird.pdf"' in fm
    assert "generator: ModelIngest" in fm


def test_manifest_needs_convert(tmp_path: Path):
    m = Manifest(tmp_path / "m.sqlite")
    assert m.needs_convert("a.pdf", "hash1") is True
    m.record("a.pdf", "hash1", "a.md", "markitdown")
    assert m.needs_convert("a.pdf", "hash1") is False
    assert m.needs_convert("a.pdf", "hash2") is True
    m.close()
