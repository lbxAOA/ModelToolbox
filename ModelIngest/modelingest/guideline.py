"""知识库准则：通过几个问题了解用户需求，生成一份 distill 阶段可直接使用的准则文档。

对应 README/``__init__.py`` 描述的流程第 5-7 步：

    5. 通过几个问题了解用户对这个知识库的需求
    6. 根据回答生成一份"知识库准则"（本模块产出的 ``GUIDELINE.md``）
    7. 蒸馏（distill）时把该准则连同 md 语料一并交给模型（Ollama 或闭源皆可）

准则文件与回答 JSON 存放在 ``<vault_root>/.ingest_meta/``（隐藏目录，不会被
:mod:`distill.linker` 当作笔记扫描——见 ``linker.py`` 对隐藏目录的过滤）。

CLI 用法见 ``modelingest guideline --help``；每个问题既可通过 flag 直接给出
（供 webui 表单式调用），也可省略全部 flag 触发交互式问答（供人在终端里直接用）。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

GUIDELINE_SUBDIR = ".ingest_meta"
GUIDELINE_FILENAME = "GUIDELINE.md"
ANSWERS_FILENAME = "guideline_answers.json"


@dataclass(frozen=True)
class Question:
    key: str
    label: str                     # 问题文本
    kind: str                      # "text" | "choice" | "bool"
    choices: tuple[tuple[str, str], ...] = ()  # (value, 说明) 仅 kind="choice" 用
    default: str = ""
    required: bool = False         # 交互模式下是否不允许空

    def describe_choices(self) -> str:
        return "、".join(f"{v}({desc})" for v, desc in self.choices)


# 六个问题，覆盖"这个知识库要怎么被蒸馏/使用"最关键的决策点。
QUESTIONS: tuple[Question, ...] = (
    Question(
        key="domain",
        label="这个知识库的领域/用途是什么？（如：算法竞赛、电路板设计、通用笔记）",
        kind="text",
        default="通用知识库",
    ),
    Question(
        key="audience",
        label="主要使用场景是？",
        kind="choice",
        choices=(
            ("self_review", "自己复习/查阅"),
            ("rag_retrieval", "AI 检索问答（RAG）"),
            ("training_data", "用作模型训练语料"),
            ("mixed", "以上都要兼顾"),
        ),
        default="mixed",
    ),
    Question(
        key="granularity",
        label="笔记粒度偏好？",
        kind="choice",
        choices=(
            ("atomic", "高度原子化：一个概念一篇，尽量拆细"),
            ("medium", "适度合并：紧密相关的概念可以合成一篇"),
            ("long_form", "保留较长上下文：不过度拆分，允许一篇覆盖多个小节"),
        ),
        default="atomic",
    ),
    Question(
        key="language",
        label="笔记语言风格？",
        kind="choice",
        choices=(
            ("zh", "纯中文"),
            ("en", "纯英文"),
            ("bilingual", "中英混合：专业术语/代码保留英文，讲解用中文"),
        ),
        default="zh",
    ),
    Question(
        key="keep_formulas_code",
        label="是否需要完整保留原文中的公式/代码片段（而不是概括改写）？",
        kind="bool",
        default="true",
    ),
    Question(
        key="extra_notes",
        label="还有其它特殊要求吗？（可留空，如：每篇末尾加一道例题、标注难度……）",
        kind="text",
        default="",
    ),
)


@dataclass
class GuidelineResult:
    text: str
    answers: dict
    guideline_path: Path
    answers_path: Path
    sha256: str


def _bool_of(raw: str) -> bool:
    return str(raw).strip().lower() not in {"0", "false", "no", "n", "否", ""}


def prompt_interactive(
    defaults: dict | None = None,
    *,
    input_fn: Callable[[str], str] = input,
    print_fn: Callable[[str], None] = print,
) -> dict:
    """在终端里逐条提问，回车使用默认值。仅供人直接跑 CLI 时使用（webui 走 flag）。"""
    defaults = dict(defaults or {})
    answers: dict = {}
    print_fn("即将生成本知识库的蒸馏准则，回车可直接采用默认值：")
    for q in QUESTIONS:
        default = defaults.get(q.key, q.default)
        hint = f"[{q.describe_choices()}] " if q.choices else ""
        raw = input_fn(f"  · {q.label} {hint}(默认: {default or '空'}): ").strip()
        answers[q.key] = raw or default
    return answers


def normalize_answers(raw: dict) -> dict:
    """补全缺省值、校验 choice 合法性。"""
    answers: dict = {}
    valid_choices = {q.key: {v for v, _ in q.choices} for q in QUESTIONS if q.choices}
    for q in QUESTIONS:
        val = raw.get(q.key)
        if val is None or val == "":
            val = q.default
        if q.key in valid_choices and val not in valid_choices[q.key]:
            raise ValueError(
                f"{q.key} 取值非法: {val!r}，可选: {', '.join(sorted(valid_choices[q.key]))}"
            )
        answers[q.key] = val
    return answers


_AUDIENCE_LABEL = {
    "self_review": "自己复习/查阅",
    "rag_retrieval": "AI 检索问答（RAG）",
    "training_data": "模型训练语料",
    "mixed": "自用查阅 + AI 检索 + 训练语料兼顾",
}
_GRANULARITY_LABEL = {
    "atomic": "高度原子化——一个概念一篇，尽量拆细，避免大杂烩",
    "medium": "适度合并——紧密相关的概念可以合成一篇",
    "long_form": "保留较长上下文——不过度拆分，允许一篇覆盖多个小节",
}
_LANGUAGE_LABEL = {
    "zh": "全文使用中文（专有名词可保留英文原文）",
    "en": "全文使用英文",
    "bilingual": "中英混合：专业术语/代码保持英文，讲解性文字使用中文",
}


def build_guideline_text(answers: dict) -> str:
    """把回答渲染成一份 Markdown 准则：既给人看，也直接拼进 teacher 的 system prompt。"""
    a = normalize_answers(answers)
    keep_fc = _bool_of(a["keep_formulas_code"])
    lines = [
        "# 知识库蒸馏准则",
        "",
        "> 本文件由 `modelingest guideline` 根据用户问答自动生成，"
        "会在 `modelingest distill` 时自动附加给蒸馏模型（Ollama 或闭源均可）。"
        "可直接编辑本文件调整规则，无需重新回答问题。",
        "",
        f"- **领域/用途**：{a['domain']}",
        f"- **主要使用场景**：{_AUDIENCE_LABEL.get(a['audience'], a['audience'])}",
        f"- **笔记粒度**：{_GRANULARITY_LABEL.get(a['granularity'], a['granularity'])}",
        f"- **语言风格**：{_LANGUAGE_LABEL.get(a['language'], a['language'])}",
        f"- **公式/代码原文**：{'必须完整保留，不要概括改写' if keep_fc else '可以概括改写，不强求逐字保留'}",
    ]
    if a["extra_notes"]:
        lines.append(f"- **额外要求**：{a['extra_notes']}")
    lines += [
        "",
        "## 给蒸馏模型的指令",
        "",
        "请在生成每篇原子知识卡片时严格遵守以上规则，尤其是笔记粒度与语言风格；"
        "额外要求（如有）优先级高于 profile 的默认写作指引。",
    ]
    return "\n".join(lines) + "\n"


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _paths(vault_root: Path) -> tuple[Path, Path]:
    meta_dir = Path(vault_root) / GUIDELINE_SUBDIR
    return meta_dir / GUIDELINE_FILENAME, meta_dir / ANSWERS_FILENAME


def generate_and_save(vault_root: Path, raw_answers: dict) -> GuidelineResult:
    """校验回答 → 渲染准则 → 落盘（vault_root/.ingest_meta/）。"""
    answers = normalize_answers(raw_answers)
    text = build_guideline_text(answers)
    guideline_path, answers_path = _paths(Path(vault_root))
    guideline_path.parent.mkdir(parents=True, exist_ok=True)
    guideline_path.write_text(text, encoding="utf-8")
    answers_path.write_text(json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8")
    return GuidelineResult(
        text=text,
        answers=answers,
        guideline_path=guideline_path,
        answers_path=answers_path,
        sha256=_hash(text),
    )


def load_guideline(vault_root: Path, explicit_path: Path | None = None) -> tuple[str, str] | None:
    """读取准则文本，返回 ``(text, sha256前16位)``；不存在返回 ``None``。

    优先用 ``explicit_path``；否则自动探测 ``vault_root/.ingest_meta/GUIDELINE.md``。
    """
    path = Path(explicit_path) if explicit_path else _paths(Path(vault_root))[0]
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    return text, _hash(text)
