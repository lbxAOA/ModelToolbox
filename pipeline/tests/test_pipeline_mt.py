"""pipeline 测试：datagen 解析/合成、Modelfile 渲染、命令构造（全离线）。"""
from __future__ import annotations

import json
from pathlib import Path

from pipeline_mt.datagen import (
    DatagenConfig,
    QAPair,
    _parse_qa,
    generate,
    split_chunks,
    strip_frontmatter,
)
from pipeline_mt.serve import ModelfileSpec, render_modelfile
from pipeline_mt.train import build_train_cmd


FM_MD = """---
source: notes/opamp.md
sha256: abc
---
# 运放

虚短虚断是理想运放分析的两条法则。

第二段：负反馈使输入端电位相等。
"""


def test_strip_frontmatter():
    body = strip_frontmatter(FM_MD)
    assert not body.startswith("---")
    assert "虚短虚断" in body


def test_split_chunks():
    chunks = split_chunks(FM_MD, max_chars=20)
    assert len(chunks) >= 2


def test_parse_qa_plain_json():
    raw = '[{"question": "什么是虚短?", "answer": "两输入端电位近似相等"}]'
    pairs = _parse_qa(raw, "x.md")
    assert len(pairs) == 1
    assert pairs[0].question.startswith("什么是")


def test_parse_qa_fenced():
    raw = '```json\n[{"question":"q","answer":"a"}]\n```'
    assert len(_parse_qa(raw, "x.md")) == 1


def test_parse_qa_garbage():
    assert _parse_qa("对不起我无法回答", "x.md") == []


def test_generate_end_to_end(tmp_path):
    corpus = tmp_path / "md"
    corpus.mkdir()
    (corpus / "a.md").write_text(FM_MD, encoding="utf-8")

    def fake_teacher(system, user):
        return json.dumps(
            [
                {"question": "Q1", "answer": "A1"},
                {"question": "Q2", "answer": "A2"},
            ],
            ensure_ascii=False,
        )

    out = tmp_path / "train.jsonl"
    cfg = DatagenConfig(corpus_dir=corpus, out_path=out, per_chunk=2)
    stats = generate(cfg, fake_teacher)
    assert stats["files"] == 1
    assert stats["pairs"] >= 2
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    rec = json.loads(lines[0])
    assert rec["messages"][-1]["role"] == "assistant"
    # 含 system
    assert rec["messages"][0]["role"] == "system"


def test_render_modelfile_with_vision(tmp_path):
    spec = ModelfileSpec(
        gguf_path=Path("model.gguf"),
        mmproj_path=Path("mmproj.gguf"),
        name="mt-private",
    )
    text = render_modelfile(spec)
    assert "FROM model.gguf" in text
    assert "mmproj.gguf" in text  # 视觉投影被写入
    assert "SYSTEM" in text
    assert "PARAMETER temperature" in text


def test_render_modelfile_text_only():
    spec = ModelfileSpec(gguf_path=Path("m.gguf"))
    text = render_modelfile(spec)
    assert "mmproj" not in text


def test_build_train_cmd_dryrun():
    cmd = build_train_cmd(Path("cfg.yaml"), dry_run=True)
    assert "train" in cmd
    assert "--dry-run" in cmd
    assert cmd[-2:] == ["--config", "cfg.yaml"] or "--config" in cmd
