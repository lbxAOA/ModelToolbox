"""第二遍：全库建链 + 生成 MOC。

蒸馏第一遍产出的笔记里，``Related`` 节写的是**纯标题**（如 ``KMP Algorithm``），
第二遍扫描整个 vault 的笔记标题，把能对应上的标题渲染成 ``[[标题]]``，并为每个
子目录生成一个 ``<目录名> MOC.md`` 索引（版式对齐现有 Strings MOC.md）。

设计为**幂等**：可反复运行；只改写 Related 节内的链接与（重）生成 MOC 文件，
不改动正文其它部分。
"""

from __future__ import annotations

import re
from pathlib import Path

from .render import render_moc

_H1 = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_FM = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def _title_of(md_path: Path) -> str:
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return md_path.stem
    body = _FM.sub("", text, count=1)
    m = _H1.search(body)
    return (m.group(1).strip() if m else md_path.stem)


def _is_moc(md_path: Path) -> bool:
    return md_path.stem.endswith(" MOC") or md_path.stem.endswith("MOC")


def _is_hidden(md_path: Path, vault: Path) -> bool:
    """路径中任一层以 ``.`` 开头即视为隐藏（如 ``.ingest_meta`` 存放准则/manifest等元数据），
    不作为笔记参与建链/MOC——否则 ``rglob`` 会把隐藏目录下的非笔记文件也扫进来。"""
    try:
        rel_parts = md_path.relative_to(vault).parts
    except ValueError:
        rel_parts = md_path.parts
    return any(part.startswith(".") for part in rel_parts)


def build_title_index(vault: Path) -> dict[str, str]:
    """标题（小写）→ 规范标题。用于把 Related 里的纯文本对齐到真实笔记。"""
    index: dict[str, str] = {}
    for md in vault.rglob("*.md"):
        if _is_moc(md) or _is_hidden(md, vault):
            continue
        title = _title_of(md)
        index.setdefault(title.lower(), title)
    return index


_RELATED_BLOCK = re.compile(
    r"(?ms)^(##\s+Related\s*\n)(.*?)(?=^##\s|\Z)"
)
_LIST_ITEM = re.compile(r"^\s*-\s*(.+?)\s*$")


def _canonical(name: str, index: dict[str, str]) -> str:
    n = name.strip()
    if n.startswith("[[") and n.endswith("]]"):
        n = n[2:-2].strip()
    return index.get(n.lower(), n)


def relink_file(md_path: Path, index: dict[str, str]) -> bool:
    """把某篇笔记 Related 节里的条目改写成 [[规范标题]]。返回是否有改动。"""
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return False

    def _fix_block(m: re.Match) -> str:
        header, body = m.group(1), m.group(2)
        new_lines = []
        for line in body.splitlines():
            item = _LIST_ITEM.match(line)
            if not item:
                new_lines.append(line)
                continue
            canon = _canonical(item.group(1), index)
            new_lines.append(f"- [[{canon}]]")
        return header + "\n".join(new_lines) + ("\n" if body.endswith("\n") else "\n")

    new_text = _RELATED_BLOCK.sub(_fix_block, text)
    if new_text != text:
        md_path.write_text(new_text, encoding="utf-8")
        return True
    return False


def build_mocs(
    vault: Path,
    *,
    generated_by: str = "ModelIngest",
) -> list[Path]:
    """为 vault 下每个含笔记的子目录生成 ``<目录名> MOC.md``。返回写出的 MOC 路径。

    - 目录内的非 MOC 笔记按标题排序，列进该目录 MOC。
    - 子目录 MOC 作为父目录 MOC 的子项（Parent 链）。
    """
    written: list[Path] = []
    vault = vault.resolve()

    # 收集每个目录下的笔记标题与子目录。
    for folder in sorted({p.parent for p in vault.rglob("*.md") if not _is_hidden(p, vault)}):
        notes = sorted(
            (p for p in folder.glob("*.md") if not _is_moc(p) and not _is_hidden(p, vault)),
            key=lambda p: _title_of(p).lower(),
        )
        subdir_mocs = []
        for sub in sorted(folder.iterdir()):
            if sub.is_dir() and not sub.name.startswith("."):
                # 子目录若有笔记，则其 MOC 标题为 "<子目录名> MOC"
                if any(not _is_hidden(p, vault) for p in sub.rglob("*.md")):
                    subdir_mocs.append(f"{sub.name} MOC")
        if not notes and not subdir_mocs:
            continue

        moc_title = f"{folder.name} MOC"
        # 顶层 vault 目录用其名字；父链接指向上层目录 MOC（若在 vault 内）。
        parent_moc = None
        if folder != vault and folder.parent != folder and folder.parent.is_relative_to(vault):
            parent_moc = f"{folder.parent.name} MOC"

        groups: list[tuple[str, list[str]]] = []
        if subdir_mocs:
            groups.append(("Sections", subdir_mocs))
        if notes:
            groups.append(("Notes" if subdir_mocs else "", [_title_of(p) for p in notes]))

        md = render_moc(
            moc_title=moc_title,
            parent_moc=parent_moc,
            description=f"Index of notes under **{folder.name}**.",
            groups=groups,
            source="ModelIngest distill",
            generated_by=generated_by,
        )
        out = folder / f"{moc_title}.md"
        out.write_text(md, encoding="utf-8")
        written.append(out)
    return written


def link_vault(vault: Path, *, generated_by: str = "ModelIngest") -> dict:
    """执行第二遍：建标题索引 → 改写 Related 链接 → 生成 MOC。"""
    vault = Path(vault).resolve()
    index = build_title_index(vault)
    relinked = 0
    for md in vault.rglob("*.md"):
        if _is_moc(md):
            continue
        if relink_file(md, index):
            relinked += 1
    mocs = build_mocs(vault, generated_by=generated_by)
    return {"titles": len(index), "relinked": relinked, "mocs": len(mocs)}
