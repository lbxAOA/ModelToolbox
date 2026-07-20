# 许可证映射 (Per-Module Licensing)

ModelToolbox 是一个**多许可证**聚合工程。各模块许可证隔离，模块之间仅通过
MCP / CLI / API 边界通信，**不做深度代码耦合**，因此上游的 copyleft（如 AGPL）
不会传染到其它模块。

| 模块 | 许可证 | 来源 / 说明 |
|------|--------|-------------|
| 根 / orchestrator / docs | MIT | ModelToolbox 原创 |
| ModelIngest | MIT | ModelToolbox 原创；依赖 markitdown 等（各自许可证） |
| ModelProvider | MIT | ModelToolbox 原创 |
| ModelSkill | MIT | ModelToolbox 原创 |
| ModelTraining | **AGPL-3.0** | 派生自 [unsloth](https://github.com/unslothai/unsloth)；保留其版权与 AGPL 全文 |
| ModelOffice | **Apache-2.0** | 派生自 [e2b](https://github.com/e2b-dev)；保留其 LICENSE 与 NOTICE |
| ModelMCP | 各子服务器独立 | altium-mcp / ltspice / obsidian-rag-mcp 等，见各自目录 |
| ModelMemory | 见模块 | 含 code-review-graph 等第三方组件 |
| ObsidianRag | 内容各自版权 | 知识库语料；原始文档（PDF 等）不随仓库分发 |

## 合规原则

1. **只改产品外壳层**：统一 `Model*` 命名仅作用于顶层文档、编排层与自建组件。
2. **保留上游内部命名与版权**：unsloth / e2b 等库内部的包名、import、版权头一律不动。
3. **派生声明**：对上游项目的修改在对应模块内以 NOTICE / 派生说明记录，不删除原始版权。
4. **AGPL 隔离**：ModelTraining（AGPL）仅通过 CLI / 子进程 / MCP 被调用，不被其它模块
   直接 `import`，以维持许可证边界。
