"""轻量校验：把 teacher 产出的 note JSON 对照 profile 检查并规范化（零依赖）。

返回一个规范化后的 dict（缺失可选字段补默认、类型收敛、去空），
或抛 :class:`NoteValidationError`（缺必填 / 结构不对），供调用方跳过并记录。
"""

from __future__ import annotations

from typing import Any

from .profiles import Profile


class NoteValidationError(ValueError):
    pass


def _as_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    return str(v).strip()


def _as_str_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        # 允许模型误传成整段文本：按换行/分号拆。
        parts = [p.strip(" -•\t") for p in v.replace(";", "\n").splitlines()]
        return [p for p in parts if p]
    if isinstance(v, (list, tuple)):
        out: list[str] = []
        for item in v:
            s = _as_str(item)
            if s:
                out.append(s)
        return out
    return [_as_str(v)]


def validate_note(data: Any, profile: Profile) -> dict:
    """校验并规范化一篇 note JSON。

    期望结构::

        {
          "title": "...",
          "subcategory": "...",        # 可选
          "tags": ["...", ...],        # 可选
          "sections": { "<key>": <str | list[str]>, ... }
        }
    """
    if not isinstance(data, dict):
        raise NoteValidationError("note 顶层必须是对象")

    title = _as_str(data.get("title"))
    if not title:
        raise NoteValidationError("缺少 title")

    raw_sections = data.get("sections")
    if not isinstance(raw_sections, dict):
        raise NoteValidationError("缺少 sections 对象")

    norm_sections: dict[str, Any] = {}
    missing_required: list[str] = []

    for sec in profile.sections:
        val = raw_sections.get(sec.key)
        if sec.is_list:
            items = _as_str_list(val)
            if sec.required and not items:
                missing_required.append(sec.key)
            norm_sections[sec.key] = items
        else:
            text = _as_str(val)
            if sec.required and not text:
                missing_required.append(sec.key)
            norm_sections[sec.key] = text

    if missing_required:
        raise NoteValidationError(
            f"'{title}' 缺少必填小节: {', '.join(missing_required)}"
        )

    return {
        "title": title,
        "subcategory": _as_str(data.get("subcategory")),
        "tags": _as_str_list(data.get("tags")),
        "sections": norm_sections,
    }


def validate_notes(payload: Any, profile: Profile) -> list[dict]:
    """校验一批 note（teacher 对一个 chunk 可能产出多篇）。

    接受 ``{"notes": [...]}``、直接的列表，或单个 note 对象。
    逐篇校验，跳过非法项；全部非法则抛错。
    """
    if isinstance(payload, dict) and "notes" in payload:
        items = payload.get("notes")
    else:
        items = payload
    if isinstance(items, dict):
        items = [items]
    if not isinstance(items, list):
        raise NoteValidationError("期望 notes 列表")

    valid: list[dict] = []
    errors: list[str] = []
    for it in items:
        try:
            valid.append(validate_note(it, profile))
        except NoteValidationError as exc:
            errors.append(str(exc))
    if not valid:
        raise NoteValidationError("；".join(errors) or "无有效 note")
    return valid
