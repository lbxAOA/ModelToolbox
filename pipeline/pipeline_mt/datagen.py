"""阶段0 数据合成：从 md 语料 + teacher 模型蒸馏出微调训练样本。

设计：
- 输入 = ModelIngest 产出的 md（含 front-matter 溯源）。
- 用 ModelProvider 的 `teacher` 角色，对每个语料块生成若干问答对。
- 输出 = JSONL（chatml/sharegpt 兼容），可直接喂给 ModelTraining。
- teacher 可注入（离线测试用假函数），不强依赖网络。

许可证边界：本模块 MIT，只通过 `import modelprovider`（同为 MIT）与
CLI 调 ModelTraining（AGPL, 子进程），不 import AGPL 代码。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Optional

# teacher 签名: (system, user) -> assistant 文本
TeacherFn = Callable[[str, str], str]

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

_SYSTEM_PROMPT = (
    "你是严谨的领域教师。基于给定的资料片段，生成高质量的问答训练样本，"
    "用于微调一个私有领域模型。要求：问题具体、可独立回答；答案完全依据资料，"
    "不臆造；覆盖关键概念、原理与推理。严格输出 JSON 数组，每项形如 "
    '{"question": "...", "answer": "..."}，不要输出多余文字。'
)


@dataclass
class QAPair:
    question: str
    answer: str
    source: str = ""

    def to_chatml(self, system: str = "") -> dict:
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": self.question})
        msgs.append({"role": "assistant", "content": self.answer})
        return {"messages": msgs}


@dataclass
class DatagenConfig:
    corpus_dir: Path
    out_path: Path
    per_chunk: int = 3
    max_chunk_chars: int = 1500
    system: str = "你是一个私有领域助手，基于所学知识准确、简洁地作答。"
    limit_files: Optional[int] = None


def strip_frontmatter(text: str) -> str:
    return _FRONTMATTER.sub("", text, count=1).strip()


def split_chunks(text: str, max_chars: int) -> List[str]:
    body = strip_frontmatter(text)
    if not body:
        return []
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    chunks: List[str] = []
    cur: List[str] = []
    size = 0
    for p in paras:
        if cur and size + len(p) > max_chars:
            chunks.append("\n\n".join(cur))
            cur, size = [], 0
        cur.append(p)
        size += len(p)
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks


def _parse_qa(raw: str, source: str) -> List[QAPair]:
    """尽力从 teacher 输出解析 JSON 数组；失败则返回空。"""
    raw = raw.strip()
    # 去掉可能的 ```json 围栏
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", raw, re.DOTALL)
    if fence:
        raw = fence.group(1)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # 退化：尝试截取第一个 [ ... ]
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if not m:
            return []
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return []
    out = []
    for item in data if isinstance(data, list) else []:
        q = str(item.get("question", "")).strip()
        a = str(item.get("answer", "")).strip()
        if q and a:
            out.append(QAPair(q, a, source))
    return out


def iter_md_files(corpus_dir: Path, limit: Optional[int] = None) -> Iterable[Path]:
    n = 0
    for p in sorted(Path(corpus_dir).rglob("*.md")):
        yield p
        n += 1
        if limit and n >= limit:
            return


def generate(config: DatagenConfig, teacher: TeacherFn) -> dict:
    """执行数据合成，写 JSONL，返回统计。"""
    config.out_path.parent.mkdir(parents=True, exist_ok=True)
    files = 0
    chunks = 0
    pairs = 0
    with config.out_path.open("w", encoding="utf-8") as fh:
        for md in iter_md_files(config.corpus_dir, config.limit_files):
            files += 1
            text = md.read_text(encoding="utf-8-sig", errors="replace")
            rel = str(md.relative_to(config.corpus_dir)).replace("\\", "/")
            for chunk in split_chunks(text, config.max_chunk_chars):
                chunks += 1
                user = (
                    f"资料片段（来源 {rel}）：\n\n{chunk}\n\n"
                    f"请生成 {config.per_chunk} 条问答训练样本。"
                )
                raw = teacher(_SYSTEM_PROMPT, user)
                for qa in _parse_qa(raw, rel):
                    fh.write(
                        json.dumps(qa.to_chatml(config.system), ensure_ascii=False)
                        + "\n"
                    )
                    pairs += 1
    return {"files": files, "chunks": chunks, "pairs": pairs, "out": str(config.out_path)}


def make_provider_teacher(role: str = "teacher") -> TeacherFn:
    """用 ModelProvider 构造真实 teacher（延迟导入，避免测试强依赖）。"""
    from modelprovider import LLMClient

    client = LLMClient.for_role(role)

    def _teacher(system: str, user: str) -> str:
        return client.ask(user, system=system, temperature=0.4, max_tokens=1200)

    return _teacher
