---
description: List every skill registered in this project's skill registry
allowed-tools: Bash(python:*), Read
---

List all skills currently registered for this project.

First make sure the registry is fresh, then read it:

```bash
python scripts/build_registry.py --quiet
```

Then read `registry/skills-index.json` (or the human-readable
`registry/SKILLS.md`) and present a concise table of each skill: **name**,
one-line **summary**, and its **trigger phrases**. Mention the total count.
