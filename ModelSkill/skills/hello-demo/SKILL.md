---
name: hello-demo
description: "Demonstration skill used to verify the skill manager's auto-discovery and routing. Greets the user and reports the current time and environment. Safe, side-effect-free example for testing /skill-search and the UserPromptSubmit auto-trigger. 用于验证技能管理器自动发现与路由的演示技能。Triggers on: hello demo, greet me, say hello, demo skill, test the skill manager, sanity check skills, hello world skill, 运行演示, 演示技能, 测试技能管理器, 打个招呼, 你好演示, 测试所有功能, 健全性检查, 跑一下演示。"
allowed-tools: Read, Bash
---

# hello-demo

A tiny example skill that exists so the skill manager has something real to
discover, rank, and route to. Use it to confirm the system works end-to-end.

## When to use

- Verifying that `/skill-search` returns a ranked match.
- Verifying that the `UserPromptSubmit` hook injects a `<skill-manager>` block
  (e.g. ask "run the hello demo" and watch for the candidate-skills context).

## Steps

1. Greet the user.
2. Optionally report the current date/time:

   ```bash
   python -c "import datetime; print('hello from skill-manager @', datetime.datetime.now())"
   ```

3. Confirm which trigger phrase matched, so it's clear the router worked.

## Notes

Replace or delete this skill once you've confirmed the manager works — it's only
a scaffolding/validation aid.
