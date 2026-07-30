"""笔记 profile（schema）定义。

一个 profile 描述"一篇原子笔记长什么样"：
- ``fields``：正文 front-matter 之外的语义字段（title / parent / subcategory / tags）。
- ``sections``：正文小节，顺序即渲染顺序。
- ``link_sections``：哪些小节的内容是"指向其它笔记的链接列表"（渲染成 ``[[...]]``）。

内置两个 profile：

- ``concept``（默认）——通用概念卡片，适配任意领域（硬件、电子、流程……）。
- ``algorithm`` ——精确复刻 ``ObsidianRag/Algorithms/*.md`` 的版式，
  用于把算法类语料蒸馏成与现有知识库一致的卡片。

teacher（LLM）会被要求**严格按 profile 输出 JSON**，再由 :mod:`render` 渲染成 md。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Section:
    """一个正文小节。"""

    key: str            # JSON 里的键
    heading: str        # 渲染成 "## <heading>"
    required: bool = True
    is_list: bool = False       # 内容是要点列表（- 项）而非段落
    is_links: bool = False      # 列表项是指向其它笔记的标题（渲染成 [[...]]）
    description: str = ""        # 给 teacher 的写作指引


@dataclass(frozen=True)
class Profile:
    """一种笔记模板。"""

    name: str
    category_default: str                 # front-matter 的 category 缺省值
    sections: tuple[Section, ...]
    tag_prefixes: tuple[str, ...] = ()     # 建议的标签前缀，仅提示 teacher
    description: str = ""                  # profile 总体用途，写进 prompt

    def section(self, key: str) -> Section | None:
        for s in self.sections:
            if s.key == key:
                return s
        return None

    @property
    def required_keys(self) -> tuple[str, ...]:
        return tuple(s.key for s in self.sections if s.required)

    @property
    def link_section_keys(self) -> tuple[str, ...]:
        return tuple(s.key for s in self.sections if s.is_links)


# --------------------------------------------------------------------------- #
# concept —— 通用概念卡片（默认）
# --------------------------------------------------------------------------- #
_CONCEPT = Profile(
    name="concept",
    category_default="Concept",
    description=(
        "一篇聚焦单一概念/主题的原子知识卡片，面向领域检索与模型训练。"
        "语言精炼、自足，不堆砌原文。"
    ),
    sections=(
        Section("definition", "Definition",
                description="1-3 句给出该概念的准确定义，可独立阅读。"),
        Section("key_points", "Key Points", is_list=True,
                description="3-6 条最重要的事实/规则/参数，每条一句。"),
        Section("when_to_use", "When to Use", required=False,
                description="在什么场景/条件下会用到它；不适用可留空。"),
        Section("details", "Details", required=False,
                description="必要的原理/步骤/注意事项，2-5 句，避免冗长。"),
        Section("related", "Related", required=False, is_list=True, is_links=True,
                description="3-6 个密切相关的其它概念标题（将互相链接）。"),
    ),
)


# --------------------------------------------------------------------------- #
# algorithm —— 精确复刻 ObsidianRag/Algorithms 版式
# --------------------------------------------------------------------------- #
_ALGORITHM = Profile(
    name="algorithm",
    category_default="Algorithm",
    tag_prefixes=("#",),
    description=(
        "竞赛/工程算法卡片，复刻现有 Algorithms 知识库版式。"
        "每篇含 Problem Recognition Signals（用真实题面/约束的口吻），"
        "便于把未知问题归类到该算法。"
    ),
    sections=(
        Section("definition", "Definition",
                description="1-2 句准确定义该算法/数据结构做什么、核心机制。"),
        Section("signals", "Problem Recognition Signals", is_list=True,
                description="2-4 条，用真实题面/数据范围的口吻，帮助识别应使用本算法。"),
        Section("complexity", "Complexity", is_list=True,
                description="Time / Space 各一条，写清与 n/m 的关系及常数布局。"),
        Section("when_to_use", "When to Use",
                description="1-2 句：相对更朴素/更强的做法，何时恰好选它。"),
        Section("idea", "Idea",
                description="2-4 句讲清算法主思想与关键不变量，不贴完整代码。"),
        Section("related", "Related", is_list=True, is_links=True,
                description="2-5 个相关算法/结构标题（将互相链接）。"),
    ),
)


_PROFILES: dict[str, Profile] = {p.name: p for p in (_CONCEPT, _ALGORITHM)}

DEFAULT_PROFILE = "concept"


def get_profile(name: str | None) -> Profile:
    """按名取 profile；``None`` 返回默认。未知名抛 ``KeyError``。"""
    key = (name or DEFAULT_PROFILE).strip()
    if key not in _PROFILES:
        raise KeyError(
            f"未知 profile: {key!r}，可用: {', '.join(sorted(_PROFILES))}"
        )
    return _PROFILES[key]


def profile_names() -> list[str]:
    return sorted(_PROFILES)
