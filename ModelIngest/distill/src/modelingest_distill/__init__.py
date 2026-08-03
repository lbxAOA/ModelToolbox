"""ModelIngest 阶段 B —— distill：把解析后的 md 语料蒸馏成结构化原子笔记知识库。

对外主要入口：
- :func:`distiller.run`      —— 完整蒸馏 + 建链
- :func:`distiller.link_only` —— 只重跑建链 + MOC
- :func:`profiles.get_profile` / :func:`profiles.profile_names`
"""

from __future__ import annotations

from .distiller import DistillConfig, DistillSummary, link_only, run
from .profiles import DEFAULT_PROFILE, get_profile, profile_names
from .teacher import TeacherUnavailable

__all__ = [
    "DistillConfig",
    "DistillSummary",
    "run",
    "link_only",
    "get_profile",
    "profile_names",
    "DEFAULT_PROFILE",
    "TeacherUnavailable",
]
