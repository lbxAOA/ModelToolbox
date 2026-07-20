"""teacher 封装：把一个内容块交给 ModelProvider 的 teacher 角色，产出受约束的 note JSON。

- ModelProvider 是**可选依赖**：未安装时 :func:`build_teacher` 抛出清晰指引，
  distill 主流程据此优雅报错（不影响阶段 A 的 parse）。
- prompt 由 profile 动态生成，要求模型**只输出 JSON**；本模块负责稳健地抽取 JSON。
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Optional

from .profiles import Profile


class TeacherUnavailable(RuntimeError):
    pass


# 一个 teacher 就是 (prompt, system) -> raw_text 的可调用体。
Teacher = Callable[[str, str], str]


def build_teacher(role: str = "teacher", model: Optional[str] = None) -> Teacher:
    """构造调用 ModelProvider 的 teacher。未安装 modelprovider 则抛 TeacherUnavailable。"""
    try:
        from modelprovider import LLMClient
    except ImportError as exc:  # pragma: no cover - 依赖缺失路径
        raise TeacherUnavailable(
            "distill 需要 ModelProvider（teacher 角色）。请先安装：\n"
            "  pip install -e ../ModelProvider\n"
            "并在 .env 配置对应 key（见 ModelProvider/.env.example）。"
        ) from exc

    if model:
        client = LLMClient.for_provider(_provider_of(model), model=_model_of(model))
    else:
        client = LLMClient.for_role(role)

    def _call(prompt: str, system: str) -> str:
        return client.ask(prompt, system=system, temperature=0.2, max_tokens=2048)

    return _call


def _provider_of(spec: str) -> str:
    return spec.split(":", 1)[0] if ":" in spec else spec


def _model_of(spec: str) -> Optional[str]:
    return spec.split(":", 1)[1] if ":" in spec else None


# --------------------------------------------------------------------------- #
# prompt 构造
# --------------------------------------------------------------------------- #
_SYSTEM = (
    "你是严谨的领域知识编辑，负责把原始资料提炼成结构化的原子知识卡片，"
    "用于本地检索与小模型训练。只输出 JSON，不要解释、不要 Markdown 代码围栏。"
)


def build_prompt(profile: Profile, content: str, *, doc_title: str = "") -> str:
    """根据 profile 生成蒸馏 prompt。"""
    field_specs = []
    for sec in profile.sections:
        kind = "字符串列表" if sec.is_list else "字符串"
        if sec.is_links:
            kind = "字符串列表（相关笔记的标题，只写标题本身，不要加 [[]]）"
        req = "必填" if sec.required else "可选(无内容则给空值)"
        field_specs.append(f'    - "{sec.key}"（{kind}，{req}）：{sec.description}')
    sections_desc = "\n".join(field_specs)

    return (
        f"{profile.description}\n\n"
        f"下面是来源文档「{doc_title}」的一段内容。请从中提炼出 1 到 3 篇原子知识卡片"
        f"（每篇聚焦一个独立概念；若这段内容只讲一个概念就产出 1 篇；"
        f"若基本无有效知识则返回空的 notes 列表）。\n\n"
        f"每篇卡片是一个 JSON 对象，字段如下：\n"
        f'  - "title"（字符串，必填）：概念名称，简洁、可作为知识库条目标题。\n'
        f'  - "subcategory"（字符串，可选）：更细的归类，用于 Parent 行。\n'
        f'  - "tags"（字符串列表，可选）：3-5 个短标签，不含空格。\n'
        f'  - "sections"（对象，必填）：包含以下键：\n'
        f"{sections_desc}\n\n"
        f"只输出如下 JSON（不要额外文本）：\n"
        f'{{"notes": [{{"title": "...", "subcategory": "...", "tags": ["..."], '
        f'"sections": {{...}}}}]}}\n\n'
        f"=== 原始内容开始 ===\n{content}\n=== 原始内容结束 ==="
    )


# --------------------------------------------------------------------------- #
# JSON 抽取
# --------------------------------------------------------------------------- #
_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> Any:
    """从模型输出中稳健抽取 JSON 对象/数组。失败抛 ValueError。"""
    if not text or not text.strip():
        raise ValueError("空响应")

    # 1) 直接解析。
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2) 去代码围栏后解析。
    m = _FENCE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 3) 截取第一个 { 到最后一个 }（或 [ ... ]）。
    for open_c, close_c in (("{", "}"), ("[", "]")):
        start = text.find(open_c)
        end = text.rfind(close_c)
        if start != -1 and end != -1 and end > start:
            snippet = text[start : end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                continue

    raise ValueError("无法从响应中解析出 JSON")


def build_system() -> str:
    return _SYSTEM
