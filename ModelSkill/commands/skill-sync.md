---
description: Rebuild the skill registry by rescanning skills/
allowed-tools: Bash(python:*)
---

Rebuild the skill registry from the current contents of `skills/`.

Run:

```bash
python scripts/build_registry.py
```

This regenerates both `registry/skills-index.json` (used by search + the
auto-trigger hook) and `registry/SKILLS.md` (the human/Obsidian catalog). Report
how many skills were registered and list their names.
