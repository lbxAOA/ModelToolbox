"""skilllib — shared core for the Claude Code skill manager.

Zero external dependencies (pure stdlib). Provides:
  - discovery + parsing of skills/*/SKILL.md
  - building registry/skills-index.json and registry/SKILLS.md
  - tokenizing + scoring a free-text task against the registry

Used by build_registry.py, search_skills.py, prompt_hook.py,
skill_edit_hook.py and new_skill.py.
"""

from __future__ import annotations

import json
import math
import re
import sys
import datetime
from pathlib import Path


def configure_utf8() -> None:
    """Force UTF-8 on stdio so non-ASCII output survives the pipe to Claude
    Code regardless of the OS locale codepage (e.g. GBK on Windows)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


def read_stdin_utf8() -> str:
    """Read stdin as UTF-8 bytes, independent of the locale codepage."""
    try:
        return sys.stdin.buffer.read().decode("utf-8", errors="replace")
    except Exception:
        try:
            return sys.stdin.read()
        except Exception:
            return ""

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------

# scripts/ lives directly under the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
REGISTRY_DIR = PROJECT_ROOT / "registry"
INDEX_PATH = REGISTRY_DIR / "skills-index.json"
CATALOG_PATH = REGISTRY_DIR / "SKILLS.md"

# Search defaults.
DEFAULT_TOP_N = 3
DEFAULT_THRESHOLD = 0.12  # below this a result is treated as "no match"

# Very common words that should not drive matching.
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "is", "are", "be", "this", "that", "it", "as", "by", "at", "from",
    "i", "you", "we", "my", "me", "please", "can", "could", "would", "should",
    "do", "does", "how", "what", "when", "use", "using", "used", "help",
    "want", "need", "make", "get", "into", "skill", "claude",
}


# ----------------------------------------------------------------------------
# Tokenizing
# ----------------------------------------------------------------------------

_LATIN_RE = re.compile(r"[a-z0-9]+")
# CJK Unified Ideographs (+ Extension A) — covers common Chinese / Kanji.
_CJK_RE = re.compile(r"[㐀-䶿一-鿿]+")


def tokenize(text: str) -> list[str]:
    """Tokenize mixed-language text.

    - Latin/digit runs -> lowercased words (len >= 2, stopwords removed).
    - CJK runs -> overlapping character bigrams (no segmenter needed), so
      Chinese task prompts can match Chinese trigger phrases. A 1-char CJK run
      yields that single character.
    """
    if not text:
        return []
    tokens: list[str] = []
    for w in _LATIN_RE.findall(text.lower()):
        if len(w) >= 2 and w not in _STOPWORDS:
            tokens.append(w)
    for run in _CJK_RE.findall(text):
        if len(run) == 1:
            tokens.append(run)
        else:
            for i in range(len(run) - 1):
                tokens.append(run[i:i + 2])
    return tokens


# ----------------------------------------------------------------------------
# SKILL.md parsing (frontmatter, dependency-free)
# ----------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(raw: str) -> dict:
    """Return a dict of frontmatter values.

    Prefer pyyaml when available; otherwise fall back to a minimal line
    parser that handles the simple `key: value` shape used by SKILL.md
    (name / description / allowed-tools), including single-quoted or
    double-quoted single-line values.
    """
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        return {}
    block = m.group(1)

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(block)
        return data if isinstance(data, dict) else {}
    except Exception:
        pass

    # --- fallback line parser ------------------------------------------------
    out: dict[str, str] = {}
    key = None
    buf: list[str] = []

    def _flush():
        nonlocal key, buf
        if key is not None:
            val = " ".join(s.strip() for s in buf).strip()
            val = _strip_quotes(val)
            out[key] = val
        key, buf = None, []

    for line in block.splitlines():
        mm = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if mm and not line.startswith(" "):
            _flush()
            key = mm.group(1).strip()
            buf = [mm.group(2)]
        elif key is not None:
            # continuation line of a folded/multi-line value
            buf.append(line)
    _flush()
    return out


def _strip_quotes(val: str) -> str:
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
        return val[1:-1]
    return val


def _extract_triggers(description: str) -> list[str]:
    """Pull the comma-separated phrases after a 'Triggers on:' marker."""
    if not description:
        return []
    m = re.search(r"triggers?\s+on\s*:\s*(.+)$", description,
                  re.IGNORECASE | re.DOTALL)
    if not m:
        return []
    tail = m.group(1)
    # Accept both ASCII and full-width Chinese punctuation as separators.
    parts = re.split(r"[,;\n，；、]", tail)
    triggers = [p.strip().rstrip(".。") for p in parts if p.strip()]
    return triggers


def _normalize_tools(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [t.strip() for t in str(value).split(",") if t.strip()]


def parse_skill_file(skill_md: Path) -> dict | None:
    """Parse a single SKILL.md into a registry record, or None if unusable."""
    try:
        raw = skill_md.read_text(encoding="utf-8")
    except Exception:
        return None

    fm = _parse_frontmatter(raw)
    name = (fm.get("name") or skill_md.parent.name).strip()
    description = (fm.get("description") or "").strip()
    triggers = _extract_triggers(description)
    tools = _normalize_tools(fm.get("allowed-tools") or fm.get("allowed_tools"))

    rel = skill_md.relative_to(PROJECT_ROOT).as_posix()
    return {
        "name": name,
        "path": rel,
        "description": description,
        "triggers": triggers,
        "allowed_tools": tools,
    }


def discover_skills(skills_dir: Path = SKILLS_DIR) -> list[dict]:
    """Find and parse every skills/*/SKILL.md (sorted by name)."""
    records: list[dict] = []
    if not skills_dir.exists():
        return records
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        rec = parse_skill_file(skill_md)
        if rec:
            records.append(rec)
    records.sort(key=lambda r: r["name"].lower())
    return records


# ----------------------------------------------------------------------------
# Registry build
# ----------------------------------------------------------------------------

def _searchable_text(rec: dict) -> str:
    """The text a query is matched against (name weighted via repetition)."""
    parts = [
        rec["name"], rec["name"].replace("-", " "),
        rec.get("description", ""),
        " ".join(rec.get("triggers", [])),
    ]
    return " ".join(p for p in parts if p)


def build_registry(skills_dir: Path = SKILLS_DIR,
                   index_path: Path = INDEX_PATH,
                   catalog_path: Path = CATALOG_PATH) -> dict:
    """(Re)build the JSON index + Markdown catalog. Returns the index dict."""
    records = discover_skills(skills_dir)

    # Document frequency for IDF weighting.
    df: dict[str, int] = {}
    for rec in records:
        for tok in set(tokenize(_searchable_text(rec))):
            df[tok] = df.get(tok, 0) + 1
    n_docs = max(len(records), 1)

    for rec in records:
        toks = tokenize(_searchable_text(rec))
        rec["tokens"] = sorted(set(toks))

    index = {
        "generated_at": datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds"),
        "skill_count": len(records),
        "document_frequency": df,
        "n_docs": n_docs,
        "skills": records,
    }

    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    catalog_path.write_text(_render_catalog(index), encoding="utf-8")
    return index


def _render_catalog(index: dict) -> str:
    """Human-readable, Obsidian-friendly catalog (wikilinks per skill)."""
    lines = [
        "# Skills Catalog",
        "",
        f"> Generated by `scripts/build_registry.py` at {index['generated_at']}.",
        f"> {index['skill_count']} skill(s) registered. Do not edit by hand — run `/skill-sync`.",
        "",
    ]
    if not index["skills"]:
        lines.append("_No skills found under `skills/`. Create one with `/skill-new`._")
        lines.append("")
        return "\n".join(lines)

    for rec in index["skills"]:
        desc = rec.get("description", "").strip()
        # Use just the lead sentence for the catalog summary.
        summary = re.split(r"(?<=[.!?])\s", desc)[0] if desc else "(no description)"
        lines.append(f"## [[{rec['name']}]]")
        lines.append("")
        lines.append(f"- **Path:** `{rec['path']}`")
        if rec.get("allowed_tools"):
            lines.append(f"- **Tools:** {', '.join(rec['allowed_tools'])}")
        if rec.get("triggers"):
            shown = ", ".join(rec["triggers"][:8])
            lines.append(f"- **Triggers:** {shown}")
        lines.append(f"- **Summary:** {summary}")
        lines.append("")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Search
# ----------------------------------------------------------------------------

def load_index(index_path: Path = INDEX_PATH) -> dict | None:
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def search(query: str,
           index: dict | None = None,
           top_n: int = DEFAULT_TOP_N,
           threshold: float = DEFAULT_THRESHOLD,
           index_path: Path = INDEX_PATH) -> list[dict]:
    """Rank registered skills against `query`.

    Score = IDF-weighted token overlap (normalized by query length)
            + trigger-phrase exact-match bonus
            + skill-name token-hit bonus.
    Returns a list of {name, path, description, score, matched} sorted desc,
    filtered to score >= threshold and capped at top_n.
    """
    if index is None:
        index = load_index(index_path)
    if not index or not index.get("skills"):
        return []

    q_tokens = tokenize(query)
    if not q_tokens:
        return []
    q_set = set(q_tokens)

    df = index.get("document_frequency", {})
    n_docs = max(index.get("n_docs", 1), 1)
    q_lower = query.lower()

    results = []
    for rec in index["skills"]:
        rec_tokens = set(rec.get("tokens", []))
        overlap = q_set & rec_tokens

        # IDF-weighted overlap.
        score = 0.0
        for tok in overlap:
            idf = math.log(1 + n_docs / (1 + df.get(tok, 0)))
            score += idf
        # Normalize by query size so long prompts aren't unfairly favored.
        score = score / math.sqrt(len(q_set))

        matched = sorted(overlap)

        # Trigger-phrase exact substring bonus (strong signal). Allow 2-char
        # CJK phrases (meaningful in Chinese); require 3+ chars for Latin.
        for trig in rec.get("triggers", []):
            t = trig.strip().lower()
            has_cjk = _CJK_RE.search(t) is not None
            if t in q_lower and (len(t) >= 3 or (has_cjk and len(t) >= 2)):
                score += 0.6
                matched.append(f"trigger:{trig}")

        # Skill-name token hit bonus.
        name_tokens = set(tokenize(rec["name"].replace("-", " ")))
        if name_tokens & q_set:
            score += 0.4

        if score > 0:
            results.append({
                "name": rec["name"],
                "path": rec["path"],
                "description": rec.get("description", ""),
                "score": round(score, 4),
                "matched": matched,
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    return [r for r in results if r["score"] >= threshold][:top_n]


def summarize(description: str, limit: int = 140) -> str:
    """One-line summary of a skill description for compact output."""
    desc = (description or "").strip()
    # Drop the trigger tail from the summary.
    desc = re.split(r"triggers?\s+on\s*:", desc, flags=re.IGNORECASE)[0].strip()
    lead = re.split(r"(?<=[.!?])\s", desc)[0] if desc else ""
    if len(lead) > limit:
        lead = lead[: limit - 1].rstrip() + "…"
    return lead or "(no description)"
