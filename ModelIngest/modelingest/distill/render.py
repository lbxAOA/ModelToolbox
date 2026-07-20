"""把校验后的 note dict 渲染成 Markdown，版式对齐 ObsidianRag/Algorithms/*.md。

产出形如::

    ---
    category: <category>
    sources: [<source>]
    generated_at: <iso>
    generated_by: <model>
    auto_generated: true
    ---

    # <Title>

    **Parent:** [[<Parent MOC>]] → <Subcategory>
    **Tags:** #a #b

    ## Definition
    ...

    ## Related
    - [[Other Note]]

链接节（is_links）里的每一项都渲染成 ``[[...]]``；其余列表节渲染成 ``- 项``。
"""

from __future__ import annotations

from datetime import datetime, timezone

from .profiles import Profile


def _yaml_scalar(value: str) -> str:
    if value == "" or any(c in value for c in ':#[]{}",\n') or value.strip() != value:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def _strip_wikilink(name: str) -> str:
    n = name.strip()
    if n.startswith("[[") and n.endswith("]]"):
        n = n[2:-2]
    return n.strip()


def _as_tag(t: str) -> str:
    t = t.strip()
    if not t:
        return ""
    return t if t.startswith("#") else "#" + t.lstrip("#")


def render_note(
    note: dict,
    profile: Profile,
    *,
    parent_moc: str,
    source: str,
    generated_by: str,
    category: str | None = None,
    generated_at: str | None = None,
) -> str:
    """渲染单篇 note。``parent_moc`` 为不含括号的 MOC 标题（如 "Strings MOC"）。"""
    ts = generated_at or datetime.now(timezone.utc).isoformat()
    cat = category or profile.category_default
    title = note["title"]
    subcategory = note.get("subcategory", "")
    tags = [_as_tag(t) for t in note.get("tags", []) if _as_tag(t)]
    sections = note.get("sections", {})

    lines: list[str] = ["---"]
    lines.append(f"category: {_yaml_scalar(cat)}")
    lines.append(f"sources: [{_yaml_scalar(source)}]")
    lines.append(f"generated_at: {ts}")
    lines.append(f"generated_by: {_yaml_scalar(generated_by)}")
    lines.append("auto_generated: true")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")

    parent_line = f"**Parent:** [[{parent_moc}]]"
    if subcategory:
        parent_line += f" → {subcategory}"
    lines.append(parent_line)
    if tags:
        lines.append(f"**Tags:** {' '.join(tags)}")
    lines.append("")

    for sec in profile.sections:
        val = sections.get(sec.key)
        if sec.is_list:
            items = val or []
            if not items and not sec.required:
                continue
            lines.append(f"## {sec.heading}")
            for item in items:
                if sec.is_links:
                    lines.append(f"- [[{_strip_wikilink(item)}]]")
                else:
                    lines.append(f"- {item}")
            lines.append("")
        else:
            text = (val or "").strip()
            if not text and not sec.required:
                continue
            lines.append(f"## {sec.heading}")
            lines.append(text)
            lines.append("")

    # 去掉结尾多余空行，保留单个换行结束。
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def render_moc(
    *,
    moc_title: str,
    parent_moc: str | None,
    description: str,
    groups: list[tuple[str, list[str]]],
    source: str,
    generated_by: str,
    generated_at: str | None = None,
) -> str:
    """渲染一个 MOC（目录索引）笔记，版式对齐 Strings MOC.md。

    ``groups`` 为 ``[(小标题, [笔记标题, ...]), ...]``；无分组时用单组、空小标题。
    """
    ts = generated_at or datetime.now(timezone.utc).isoformat()
    lines: list[str] = ["---"]
    lines.append("category: Index")
    lines.append(f"sources: [{_yaml_scalar(source)}]")
    lines.append(f"generated_at: {ts}")
    lines.append(f"generated_by: {_yaml_scalar(generated_by)}")
    lines.append("auto_generated: true")
    lines.append("---")
    lines.append("")
    lines.append(f"# {moc_title}")
    lines.append("")
    if parent_moc:
        lines.append(f"Parent: [[{parent_moc}]]")
        lines.append("")
    if description.strip():
        lines.append(description.strip())
        lines.append("")

    for heading, titles in groups:
        if heading:
            lines.append(f"## {heading}")
        for t in titles:
            lines.append(f"- [[{_strip_wikilink(t)}]]")
        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"
