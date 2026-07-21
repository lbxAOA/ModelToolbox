"""阶段 B distill 测试：chunk / validate / render / teacher(JSON抽取) / distiller(假 teacher) / linker。

全部离线，不调用真实 LLM、不联网。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from modelingest.distill import get_profile, profile_names
from modelingest.distill.chunk import chunk_markdown, strip_frontmatter
from modelingest.distill.distiller import DistillConfig, distill_file, run as distill_run
from modelingest.distill.linker import build_title_index, link_vault
from modelingest.distill.render import render_note
from modelingest.distill.teacher import build_prompt, build_system, extract_json
from modelingest.distill.validate import NoteValidationError, validate_notes


# --------------------------- profiles ---------------------------

def test_profiles_available():
    assert "concept" in profile_names()
    assert "algorithm" in profile_names()
    algo = get_profile("algorithm")
    assert "signals" in {s.key for s in algo.sections}
    assert "related" in algo.link_section_keys


def test_unknown_profile():
    with pytest.raises(KeyError):
        get_profile("nope")


# --------------------------- chunk ---------------------------

def test_strip_frontmatter():
    md = "---\na: 1\n---\n\n# Title\nbody"
    assert strip_frontmatter(md).startswith("# Title")


def test_chunk_by_heading_and_merge():
    md = "# A\n" + "x" * 500 + "\n\n## B\nshort\n\n## C\n" + "y" * 500
    chunks = chunk_markdown(md, min_chars=400, max_chars=10000)
    assert len(chunks) >= 2
    assert all(c.text.strip() for c in chunks)


def test_chunk_hard_wrap():
    md = "# A\n\n" + "\n\n".join("para " + "z" * 100 for _ in range(20))
    chunks = chunk_markdown(md, min_chars=100, max_chars=500)
    assert all(len(c.text) <= 600 for c in chunks)


# --------------------------- validate ---------------------------

def test_validate_notes_ok():
    profile = get_profile("algorithm")
    payload = {
        "notes": [{
            "title": "KMP",
            "subcategory": "Exact Matching",
            "tags": ["strings", "kmp"],
            "sections": {
                "definition": "Linear time matching.",
                "signals": ["find pattern in text"],
                "complexity": ["Time: O(n+m)", "Space: O(m)"],
                "when_to_use": "single pattern",
                "idea": "prefix function",
                "related": ["Z-Function"],
            },
        }]
    }
    notes = validate_notes(payload, profile)
    assert notes[0]["title"] == "KMP"
    assert notes[0]["sections"]["complexity"] == ["Time: O(n+m)", "Space: O(m)"]


def test_validate_missing_required():
    profile = get_profile("algorithm")
    bad = {"notes": [{"title": "X", "sections": {"definition": "only this"}}]}
    with pytest.raises(NoteValidationError):
        validate_notes(bad, profile)


def test_validate_coerces_string_list():
    profile = get_profile("concept")
    payload = {"title": "T", "sections": {
        "definition": "d",
        "key_points": "one; two; three",
    }}
    notes = validate_notes(payload, profile)
    assert notes[0]["sections"]["key_points"] == ["one", "two", "three"]


# --------------------------- render ---------------------------

def test_render_algorithm_format():
    profile = get_profile("algorithm")
    note = {
        "title": "Segment Tree",
        "subcategory": "Range Query Structures",
        "tags": ["data-structures", "segment-tree"],
        "sections": {
            "definition": "A binary tree over ranges.",
            "signals": ["point update, range query"],
            "complexity": ["Time: O(log n)", "Space: O(n)"],
            "when_to_use": "dynamic range queries",
            "idea": "each node covers [l,r]",
            "related": ["Fenwick Tree", "[[Sparse Table]]"],
        },
    }
    md = render_note(note, profile, parent_moc="Data Structures MOC",
                     source="x/seg.md", generated_by="test")
    assert md.startswith("---")
    assert "# Segment Tree" in md
    assert "**Parent:** [[Data Structures MOC]] → Range Query Structures" in md
    assert "**Tags:** #data-structures #segment-tree" in md
    assert "## Problem Recognition Signals" in md
    assert "- [[Fenwick Tree]]" in md
    assert "- [[Sparse Table]]" in md      # 已含 [[]] 不重复包裹
    assert "auto_generated: true" in md


# --------------------------- teacher JSON extraction ---------------------------

def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_fenced():
    txt = "sure:\n```json\n{\"notes\": []}\n```\nthanks"
    assert extract_json(txt) == {"notes": []}


def test_extract_json_embedded():
    txt = 'blah {\n"x": [1,2]\n} trailing'
    assert extract_json(txt) == {"x": [1, 2]}


def test_extract_json_fail():
    with pytest.raises(ValueError):
        extract_json("no json here")


def test_build_prompt_mentions_sections():
    p = build_prompt(get_profile("algorithm"), "some content", doc_title="Doc")
    assert "signals" in p
    assert "Doc" in p
    assert build_system()


# --------------------------- distiller with fake teacher ---------------------------

def _fake_teacher_factory(title="Concept One"):
    def teacher(prompt: str, system: str) -> str:
        return json.dumps({"notes": [{
            "title": title,
            "subcategory": "Sub",
            "tags": ["t"],
            "sections": {
                "definition": "A definition.",
                "key_points": ["p1", "p2"],
                "when_to_use": "always",
                "details": "some details",
                "related": ["Other Concept"],
            },
        }]})
    return teacher


def test_distill_file_writes_notes(tmp_path: Path):
    src_root = tmp_path / "raw"
    (src_root / "Area").mkdir(parents=True)
    src = src_root / "Area" / "doc.md"
    src.write_text("# Doc\n\n" + "content " * 100, encoding="utf-8")

    vault = tmp_path / "vault"
    cfg = DistillConfig(source_root=src_root, vault_root=vault, profile="concept")
    profile = get_profile("concept")

    written, errors = distill_file(src, cfg, profile, _fake_teacher_factory())
    assert not errors
    assert written
    note = written[0].read_text(encoding="utf-8")
    assert "# Concept One" in note
    assert "[[Data Structures MOC]]" not in note   # parent is Area MOC
    assert "[[Area MOC]]" in note


def test_distill_run_incremental_and_link(tmp_path: Path, monkeypatch):
    src_root = tmp_path / "raw"
    (src_root / "Area").mkdir(parents=True)
    (src_root / "Area" / "a.md").write_text("# A\n\n" + "x " * 100, encoding="utf-8")

    vault = tmp_path / "vault"
    cfg = DistillConfig(source_root=src_root, vault_root=vault, profile="concept")

    # 打桩 build_teacher，避免依赖 ModelProvider。
    import modelingest.distill.distiller as dmod
    monkeypatch.setattr(dmod, "build_teacher",
                        lambda role="teacher", model=None: _fake_teacher_factory())

    s1 = distill_run(cfg)
    assert s1.distilled == 1
    assert s1.notes >= 1
    assert s1.link_stats["mocs"] >= 1

    # 第二次：未变，应跳过。
    s2 = distill_run(cfg)
    assert s2.distilled == 0
    assert s2.skipped == 1

    # MOC 生成了。
    mocs = list(vault.rglob("*MOC.md"))
    assert mocs


# --------------------------- linker ---------------------------

def test_linker_relinks_related(tmp_path: Path):
    vault = tmp_path / "v"
    (vault / "Cat").mkdir(parents=True)
    (vault / "Cat" / "Alpha.md").write_text(
        "---\n---\n\n# Alpha\n\n## Related\n- beta node\n- [[Alpha]]\n",
        encoding="utf-8",
    )
    (vault / "Cat" / "Beta Node.md").write_text(
        "---\n---\n\n# Beta Node\n\n## Related\n- Alpha\n", encoding="utf-8"
    )

    idx = build_title_index(vault)
    assert "beta node" in idx and idx["beta node"] == "Beta Node"

    stats = link_vault(vault)
    alpha = (vault / "Cat" / "Alpha.md").read_text(encoding="utf-8")
    assert "- [[Beta Node]]" in alpha       # 纯文本对齐到真实标题
    assert stats["mocs"] >= 1
    moc = (vault / "Cat" / "Cat MOC.md").read_text(encoding="utf-8")
    assert "[[Alpha]]" in moc and "[[Beta Node]]" in moc
