---
description: Search the skill registry for skills matching a task description
argument-hint: <task description>
allowed-tools: Bash(python:*), Read
---

Search this project's skill registry for skills that match the task described in
`$ARGUMENTS`.

Run:

```bash
python scripts/search_skills.py "$ARGUMENTS"
```

(If `python` is not found on Windows, use `py` instead.)

Then report the ranked matches to the user. If a result clearly fits the task,
offer to invoke that skill via the Skill tool. If nothing matches, say so and
suggest `/skill-new` to create a skill for this kind of task.
