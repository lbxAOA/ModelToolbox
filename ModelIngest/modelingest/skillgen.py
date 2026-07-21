"""B 部分收尾：为一个刚蒸馏好的 Obsidian 知识库自动生成一个 ModelSkill 技能。

复用 ``ModelSkill/scripts/new_skill.py`` 脚手架一个 SKILL.md（起 name/description/
triggers），再把它的占位 Steps 段替换成"如何切到这个知识库检索"的具体指引
（``obsidian-rag-mcp`` 是单 vault 设计，切知识库 = 改 ``OBSIDIAN_VAULT`` 再 reindex），
最后调用 ``build_registry.py`` 让新技能立刻可被搜索到。

ModelIngest 与 ModelSkill 都是 MIT，无需像 ModelTraining(AGPL)/ModelOffice(Apache)
那样做子进程隔离；这里仍然选择子进程调用而不是 import，是因为 ModelSkill 的脚手架
逻辑本来就是"跑一个独立脚本 + 重建 registry 文件"，没有可复用的 Python API。
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MODELSKILL_ROOT = _REPO_ROOT / "ModelSkill"
_SLUG_RE = re.compile(r"[^a-z0-9-]+")


class SkillGenError(RuntimeError):
    """生成技能失败（脚手架脚本或 registry 重建报错）。"""


def _slug(name: str) -> str:
    s = _SLUG_RE.sub("-", name.strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


@dataclass
class SkillGenResult:
    name: str
    skill_path: Path


def generate_knowledge_base_skill(
    *,
    name: str,
    description: str,
    triggers: str,
    vault_root: Path,
    source_root: Path,
    model_spec: str,
    profile: str,
) -> SkillGenResult:
    """脚手架 + 定制 + 注册一个"如何检索这个知识库"的技能。"""
    if not _MODELSKILL_ROOT.is_dir():
        raise SkillGenError(f"未找到 ModelSkill 目录：{_MODELSKILL_ROOT}")

    slug = _slug(name)
    if not slug:
        raise SkillGenError("知识库名称无法生成合法的技能标识（slug 为空）")

    new_skill_py = _MODELSKILL_ROOT / "scripts" / "new_skill.py"
    build_registry_py = _MODELSKILL_ROOT / "scripts" / "build_registry.py"

    proc = subprocess.run(
        [
            sys.executable, str(new_skill_py),
            "--name", slug,
            "--description", description,
            "--triggers", triggers,
            "--tools", "Read, Bash",
            "--force",
        ],
        cwd=_MODELSKILL_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise SkillGenError(f"脚手架技能失败：{proc.stderr.strip() or proc.stdout.strip()}")

    skill_md = _MODELSKILL_ROOT / "skills" / slug / "SKILL.md"
    if not skill_md.is_file():
        raise SkillGenError(f"脚手架未产出预期文件：{skill_md}")

    vault_display = str(vault_root)
    source_display = str(source_root)
    body = f"""## When to use

需要回答与「{name}」这个知识库相关的问题、或用户明确要求检索/查阅这个知识库时使用。

## 知识库信息

- **Vault 目录**：`{vault_display}`
- **原始语料目录**：`{source_display}`
- **蒸馏模型**：`{model_spec}`（profile={profile}）
- 检索层是 `ModelMCP/obsidian-rag-mcp`（Ollama embedding + sqlite 向量库），
  它一次只索引一个 vault（由环境变量 `OBSIDIAN_VAULT` 指定）。

## Steps

1. 切换检索目标到这个知识库（若当前 `OBSIDIAN_VAULT` 不是这个目录）：
   ```bash
   set OBSIDIAN_VAULT={vault_display}
   cd ModelMCP/obsidian-rag-mcp
   obsidian-rag index
   ```
2. 语义检索：`obsidian-rag search "<问题关键词>" -k 5`。
3. 需要整篇笔记时：`obsidian-rag get <search 返回的 source 相对路径>`。
4. 通过 MCP 使用时对应工具是 `search(query, k)` / `get_note(source)` / `reindex(force)`。

## Notes

- 本技能由 ModelIngest 的 `make-skill` 命令自动生成（对应蒸馏 `{source_display}` →
  `{vault_display}` 的一次运行），如需更新内容直接编辑本文件后运行 `/skill-sync`。
"""
    text = skill_md.read_text(encoding="utf-8")
    text = re.sub(r"## When to use.*", lambda _m: body, text, flags=re.DOTALL)
    skill_md.write_text(text, encoding="utf-8")

    proc2 = subprocess.run(
        [sys.executable, str(build_registry_py), "--quiet"],
        cwd=_MODELSKILL_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc2.returncode != 0:
        raise SkillGenError(f"重建 registry 失败：{proc2.stderr.strip() or proc2.stdout.strip()}")

    return SkillGenResult(name=slug, skill_path=skill_md)
