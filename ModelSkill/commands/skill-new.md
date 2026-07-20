---
description: Scaffold a new skill (SKILL.md) and register it
argument-hint: <name> [description]
allowed-tools: Bash(python:*), Read
---

Scaffold a new skill for this project based on `$ARGUMENTS`.

1. Determine the skill **name** (kebab-case) from the arguments. If the user did
   not provide a clear description and trigger phrases, ask for:
   - a one-line **description** of what the skill does, and
   - a few **trigger phrases** (the words/requests that should activate it).

2. Create the skill (fill in the gathered values):

   ```bash
   python scripts/new_skill.py --name <name> \
     --description "<one-line description>" \
     --triggers "<phrase 1>, <phrase 2>, <phrase 3>" \
     --tools "Read, Grep, Glob, Bash"
   ```

3. The script writes `skills/<name>/SKILL.md` and rebuilds the registry. Open the
   generated SKILL.md, refine the body (When to use / Steps), and confirm it is
   listed via `/skill-list`.
