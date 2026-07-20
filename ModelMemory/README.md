# ModelMemory

让模型**拥有跨会话记忆**，不必每开一个新窗口就从零开始；并提供基于代码知识图谱的变更审查。

## 组成

- `code_review_graph/` — 在本地用 Tree-sitter 构建代码知识图谱，做风险评分的变更影响分析。
- `action.yml` — 组合式 GitHub Action：在 PR 上发布风险评分审查评论（本地优先，代码不外传）。
- `.mcp.json` — 以 MCP server 形式暴露 `code-review-graph`。
- `skills/` — 记忆 / 审查相关技能（build-graph、review-*、explore-codebase 等）。

## 定位

ModelToolbox 中的「记忆 + 代码理解」层，通过 MCP 总线供 Agent 调用。

> 许可证：见模块内说明与根 `LICENSES.md`（含 code-review-graph 等第三方组件）。
