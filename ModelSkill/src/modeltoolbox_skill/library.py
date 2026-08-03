from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re

from modeltoolbox_core.paths import resolve_in_root


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS_DIR = PROJECT_ROOT / "skills"
DEFAULT_REGISTRY_DIR = PROJECT_ROOT / "registry"


@dataclass(frozen=True)
class SkillRecord:
    name: str
    path: str
    description: str
    triggers: list[str]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-._")
    if not slug:
        raise ValueError("Skill name must contain at least one safe character")
    if slug in {".", ".."}:
        raise ValueError("Invalid skill name")
    return slug


def _frontmatter(raw: str) -> dict[str, str]:
    if not raw.startswith("---\n"):
        return {}
    end = raw.find("\n---\n", 4)
    if end < 0:
        return {}
    data: dict[str, str] = {}
    for line in raw[4:end].splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            data[match.group(1)] = match.group(2).strip().strip("'\"")
    return data


def _description(raw: str) -> str:
    frontmatter = _frontmatter(raw)
    if frontmatter.get("description"):
        return frontmatter["description"]
    for line in raw.splitlines():
        text = line.strip("# ").strip()
        if text and text != "---":
            return text[:240]
    return ""


def parse_skill(path: Path, *, skills_dir: Path = DEFAULT_SKILLS_DIR) -> SkillRecord | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return None
    frontmatter = _frontmatter(raw)
    name = frontmatter.get("name") or path.parent.name
    description = _description(raw)
    triggers = [item.strip() for item in re.split(r"[,;，；、]", frontmatter.get("triggers", "")) if item.strip()]
    return SkillRecord(
        name=name,
        path=path.relative_to(skills_dir.parent).as_posix(),
        description=description,
        triggers=triggers,
    )


def discover_skills(skills_dir: Path = DEFAULT_SKILLS_DIR) -> list[SkillRecord]:
    if not skills_dir.exists():
        return []
    records = [parse_skill(path, skills_dir=skills_dir) for path in sorted(skills_dir.glob("*/SKILL.md"))]
    return sorted((record for record in records if record is not None), key=lambda item: item.name.lower())


def build_registry(
    *,
    skills_dir: Path = DEFAULT_SKILLS_DIR,
    registry_dir: Path = DEFAULT_REGISTRY_DIR,
) -> dict[str, object]:
    records = discover_skills(skills_dir)
    registry_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill_count": len(records),
        "skills": [record.__dict__ for record in records],
    }
    (registry_dir / "skills-index.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = ["# Skills", ""]
    for record in records:
        lines.append(f"- `{record.name}` - {record.description} ({record.path})")
    (registry_dir / "SKILLS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def search_skills(query: str, *, skills_dir: Path = DEFAULT_SKILLS_DIR, limit: int = 5) -> list[SkillRecord]:
    terms = {term.lower() for term in re.findall(r"[\w.-]+", query, flags=re.UNICODE)}
    scored: list[tuple[int, SkillRecord]] = []
    for record in discover_skills(skills_dir):
        haystack = " ".join([record.name, record.description, *record.triggers]).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, record))
    scored.sort(key=lambda item: (-item[0], item[1].name.lower()))
    return [record for _, record in scored[:limit]]


def _collect_markdown_summary(source: Path, max_files: int = 12, max_chars: int = 7000) -> str:
    parts: list[str] = []
    for path in sorted(source.rglob("*.md"))[:max_files]:
        if path.name.upper() == "SKILL.MD":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        if not text:
            continue
        rel = path.relative_to(source).as_posix()
        parts.append(f"### {rel}\n\n{text[:1200]}")
        if sum(len(part) for part in parts) >= max_chars:
            break
    return "\n\n".join(parts)[:max_chars]


def build_from_markdown_library(
    source: Path | str,
    *,
    name: str | None = None,
    skills_dir: Path = DEFAULT_SKILLS_DIR,
    overwrite: bool = False,
) -> Path:
    source_path = Path(source).resolve()
    if not source_path.exists() or not source_path.is_dir():
        raise ValueError(f"Markdown library does not exist: {source_path}")
    skill_name = slugify(name or source_path.name)
    skills_dir.mkdir(parents=True, exist_ok=True)
    target = resolve_in_root(skills_dir, skill_name)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Skill already exists: {target}")
    target.mkdir(parents=True, exist_ok=True)
    summary = _collect_markdown_summary(source_path)
    if not summary:
        summary = "No Markdown content was found in the source library."
    body = f"""---
name: {skill_name}
description: Use this skill when working with the ingested Markdown library at {source_path.as_posix()}.
---

# {skill_name}

Use this skill for tasks that need the curated knowledge captured in the source Markdown library.

## Source

{source_path.as_posix()}

## Working Notes

Read the indexed Markdown library first, prefer source-local terminology, and cite the relevant file path when answering from this material.

## Seed Context

{summary}
"""
    skill_path = target / "SKILL.md"
    skill_path.write_text(body, encoding="utf-8")
    build_registry(skills_dir=skills_dir, registry_dir=DEFAULT_REGISTRY_DIR)
    return skill_path
