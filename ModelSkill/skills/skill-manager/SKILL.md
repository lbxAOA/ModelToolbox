---
name: skill-manager
description: "Manage and route Claude Code skills for this project. Maintains a searchable registry of every skill under skills/, finds the best skill for a given task, lists/syncs the registry, and scaffolds new skills. Use when the user asks to manage, list, search, find, sync, register, or create skills, or asks 'is there a skill for X?'. 管理并路由本项目的技能：维护技能注册表、为任务匹配技能、列出/同步注册表、脚手架新建技能。Triggers on: skill manager, manage skills, list skills, search skills, find a skill, which skill, is there a skill for, sync skills, rebuild skill registry, register skill, new skill, create a skill, scaffold skill, /skill-search, /skill-list, /skill-sync, /skill-new, 技能管理器, 管理技能, 列出技能, 搜索技能, 查找技能, 有没有对应技能, 有没有技能, 同步技能, 重建技能注册表, 注册技能, 新建技能, 创建技能, 脚手架技能。"
allowed-tools: Read, Grep, Glob, Bash
---

# skill-manager

The orchestrator for this project's skill system. It keeps a registry of every
skill under `skills/` and helps match an incoming task to the right skill.

Most matching happens **automatically**: a `UserPromptSubmit` hook
(`scripts/prompt_hook.py`) searches the registry on every prompt and injects a
`<skill-manager>` block listing candidate skills. This skill is for the
**explicit** management operations below.

## Operations & routing

| Intent | Command | Script |
|--------|---------|--------|
| "is there a skill for X?" / find a skill | `/skill-search <query>` | `scripts/search_skills.py` |
| list all registered skills | `/skill-list` | reads `registry/skills-index.json` |
| rebuild the registry | `/skill-sync` | `scripts/build_registry.py` |
| create a new skill | `/skill-new <name>` | `scripts/new_skill.py` |

## How to run an operation

All operations are thin wrappers over Python scripts (cross-platform, no
dependencies). Run them from the project root with `python` (use `py` on Windows
if `python` is not on PATH):

```bash
python scripts/search_skills.py "ingest this pdf into my notes"
python scripts/build_registry.py        # rebuild registry/skills-index.json + SKILLS.md
python scripts/new_skill.py --name pdf-extract --description "..." --triggers "..."
```

## Registry layout

- `registry/skills-index.json` — machine-readable index (used by search + hook).
- `registry/SKILLS.md` — human/Obsidian-readable catalog with `[[wikilinks]]`.

The registry is rebuilt automatically on session start and whenever a `SKILL.md`
is edited (PostToolUse hook). Run `/skill-sync` to force a rebuild.

## Authoring a good skill

For a skill to be matched well, its `description` should be specific and end
with a `Triggers on:` clause listing the phrases that should activate it — the
search engine gives those exact phrases a strong bonus. See any existing
`skills/*/SKILL.md` for the pattern.

**Bilingual matching:** the search engine tokenizes Chinese via character
bigrams, so you can mix English and 中文 freely in `description` and in
`Triggers on:`. List Chinese trigger phrases (separated by `,` or `，`) so that
pure-Chinese task prompts also match. Example:
`Triggers on: extract pdf, parse pdf, 提取 pdf, 解析 pdf, pdf 转文本。`
