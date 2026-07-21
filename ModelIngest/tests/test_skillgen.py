"""skillgen 单测：用假的 ModelSkill 脚手架脚本（临时目录）验证拼装/替换逻辑，
不触碰仓库里真正的 ModelSkill/registry。"""

from __future__ import annotations

from pathlib import Path

import pytest

from modelingest import skillgen


def _fake_modelskill_root(tmp_path: Path) -> Path:
    root = tmp_path / "ModelSkill"
    (root / "scripts").mkdir(parents=True)
    (root / "skills").mkdir(parents=True)

    # 假的 new_skill.py：按 --name 在 skills/<name>/SKILL.md 里写一个占位文件。
    (root / "scripts" / "new_skill.py").write_text(
        """
import argparse
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--name", required=True)
p.add_argument("--description", required=True)
p.add_argument("--triggers", default="")
p.add_argument("--tools", default="")
p.add_argument("--force", action="store_true")
args = p.parse_args()

skill_dir = Path(__file__).resolve().parent.parent / "skills" / args.name
skill_dir.mkdir(parents=True, exist_ok=True)
(skill_dir / "SKILL.md").write_text(
    "---\\nname: " + args.name + "\\n---\\n\\n# " + args.name + "\\n\\n## When to use\\n\\nPLACEHOLDER\\n",
    encoding="utf-8",
)
""",
        encoding="utf-8",
    )
    # 假的 build_registry.py：什么都不做，只需能正常退出。
    (root / "scripts" / "build_registry.py").write_text(
        "import sys\nargs = sys.argv[1:]\nprint('rebuilt', args)\n",
        encoding="utf-8",
    )
    return root


def test_generate_knowledge_base_skill(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    fake_root = _fake_modelskill_root(tmp_path)
    monkeypatch.setattr(skillgen, "_MODELSKILL_ROOT", fake_root)

    result = skillgen.generate_knowledge_base_skill(
        name="OI Wiki 算法竞赛知识库",
        description="OI Wiki 蒸馏而成的算法竞赛知识库",
        triggers="oi wiki, 算法竞赛",
        vault_root=tmp_path / "vault",
        source_root=tmp_path / "src_md",
        model_spec="ollama:gemma4:latest",
        profile="algorithm",
    )

    assert result.name == "oi-wiki"
    assert result.skill_path.is_file()
    text = result.skill_path.read_text(encoding="utf-8")
    assert "PLACEHOLDER" not in text
    assert "## When to use" in text
    assert "## 知识库信息" in text
    assert "ollama:gemma4:latest" in text
    assert "OBSIDIAN_VAULT" in text
    assert str(tmp_path / "vault") in text


def test_generate_knowledge_base_skill_missing_modelskill_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(skillgen, "_MODELSKILL_ROOT", tmp_path / "does-not-exist")
    with pytest.raises(skillgen.SkillGenError):
        skillgen.generate_knowledge_base_skill(
            name="x",
            description="y",
            triggers="",
            vault_root=tmp_path / "v",
            source_root=tmp_path / "s",
            model_spec="ollama:x",
            profile="concept",
        )


def test_generate_knowledge_base_skill_empty_slug(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    fake_root = _fake_modelskill_root(tmp_path)
    monkeypatch.setattr(skillgen, "_MODELSKILL_ROOT", fake_root)
    with pytest.raises(skillgen.SkillGenError):
        skillgen.generate_knowledge_base_skill(
            name="###",
            description="y",
            triggers="",
            vault_root=tmp_path / "v",
            source_root=tmp_path / "s",
            model_spec="ollama:x",
            profile="concept",
        )
