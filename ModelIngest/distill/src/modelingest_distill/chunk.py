"""把一篇解析后的 Markdown 切成"概念大小"的块，供 teacher 逐块蒸馏。

策略：
- 按 Markdown 标题（``#``/``##``/``###``）划分；每个 heading 起一个块。
- 累积过短的相邻块，直到达到 ``min_chars``（避免碎片）。
- 单块超过 ``max_chars`` 时按段落硬切，保证不超模型上下文。
- front-matter（``--- ... ---``）会被剥离，不进入块内容。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_FRONTMATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


@dataclass
class Chunk:
    heading: str          # 该块最近的标题（可空）
    text: str             # 块正文（含标题行）
    index: int            # 在文档内的序号


def strip_frontmatter(md: str) -> str:
    return _FRONTMATTER.sub("", md, count=1)


def _split_by_heading(md: str) -> list[tuple[str, str]]:
    """返回 [(heading, block_text)]，block_text 含标题行本身。"""
    lines = md.splitlines()
    blocks: list[tuple[str, list[str]]] = []
    cur_heading = ""
    cur: list[str] = []

    def flush():
        if cur and any(l.strip() for l in cur):
            blocks.append((cur_heading, list(cur)))

    for line in lines:
        m = _HEADING.match(line)
        if m:
            flush()
            cur_heading = m.group(2).strip()
            cur = [line]
        else:
            cur.append(line)
    flush()
    return [(h, "\n".join(b).strip()) for h, b in blocks]


def _hard_wrap(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    paras = re.split(r"\n\s*\n", text)
    out: list[str] = []
    buf = ""
    for p in paras:
        if len(buf) + len(p) + 2 > max_chars and buf:
            out.append(buf.strip())
            buf = p
        else:
            buf = f"{buf}\n\n{p}" if buf else p
    if buf.strip():
        out.append(buf.strip())
    return out


def chunk_markdown(
    md: str,
    *,
    min_chars: int = 400,
    max_chars: int = 6000,
) -> list[Chunk]:
    """把 md 切成块列表。"""
    body = strip_frontmatter(md).strip()
    if not body:
        return []

    raw = _split_by_heading(body)
    if not raw:
        raw = [("", body)]

    # 合并过短块。
    merged: list[tuple[str, str]] = []
    acc_heading = ""
    acc_text = ""
    for heading, text in raw:
        if not acc_text:
            acc_heading, acc_text = heading, text
            continue
        if len(acc_text) < min_chars:
            acc_text = f"{acc_text}\n\n{text}"
            if not acc_heading:
                acc_heading = heading
        else:
            merged.append((acc_heading, acc_text))
            acc_heading, acc_text = heading, text
    if acc_text:
        merged.append((acc_heading, acc_text))

    # 硬切过长块，编号。
    chunks: list[Chunk] = []
    idx = 0
    for heading, text in merged:
        for piece in _hard_wrap(text, max_chars):
            chunks.append(Chunk(heading=heading, text=piece, index=idx))
            idx += 1
    return chunks
