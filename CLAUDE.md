# CLAUDE.md — ModelToolbox 系统级约定

本文件是 **ModelToolbox** 的顶层 persona 与模块选择策略，供 Claude / Copilot 等
Agent 在本仓库工作时读取。子模块可有各自的 `CLAUDE.md`/`AGENTS.md`，本文件是它们的上层。

## 这是什么

一套本地模型系统：用用户的 Obsidian 知识库微调一个带视觉能力的小模型，使其在**窄领域**（算法竞赛、数学建模、电路板设计）超过通用旗舰模型，全程可在个人笔记本本地运行。核心理念是 **训练为主，检索兜底**。

## 模块地图（8 模块）

| 模块                    | 职责                                 | 调用方式                                         |
| ----------------------- | ------------------------------------ | ------------------------------------------------ |
| **ModelTraining** | 微调私有模型(unsloth)→导出 GGUF     | CLI / 子进程(AGPL 隔离)                          |
| **ModelProvider** | 统一大模型调用(闭源 + Ollama)        | `modelprovider` CLI / `import modelprovider` |
| **ModelIngest**   | 文档转 md(PDF/Word/Excel/…)         | `modelingest` CLI                              |
| **ModelMCP**      | 领域工具 MCP(altium/ltspice/rag/ach) | MCP server                                       |
| **ModelMemory**   | 代码审查记忆图                       | MCP(code-review-graph)                           |
| **ModelOffice**   | 代码执行/沙箱(e2b)                   | 计划包成 sandbox-mcp                             |
| **ModelSkill**    | 技能注册与路由                       | skill 插件 + hook                                |
| **ObsidianRag**   | 知识库语料(原件不入库)               | 被 ingest/rag 消费                               |

## 模块选择策略（按任务）

- **要看原理图/PCB/电路** → 私有模型(视觉) + `ModelMCP/altium`；仿真相关走 `ltspice`。
- **要查知识库笔记** → `obsidian-rag`(检索兜底)，再交给私有模型作答。
- **私有模型没训好 / 要对比** → `ModelProvider` 的 `fallback` 角色调旗舰。
- **要合成训练数据** → `ModelProvider` 的 `teacher` 角色 + `ModelIngest` 产出的 md。
- **要跑/审查代码** → `ModelMemory`(审查) + `ModelOffice`(沙箱执行)。
- **训练/导出模型** → `ModelTraining`(unsloth_cli)。

## 双通道调用

1. **人肉**：VSCode GitHub Copilot 原生 Ollama provider，模型选择器选本地私有模型。
2. **系统自动**：Ollama OpenAI 兼容 API(`localhost:11434/v1`) + 本仓库聚合的 MCP server。

聚合 MCP 清单见 [`orchestrator/mcp.aggregate.json`](./orchestrator/mcp.aggregate.json)。

## 硬约束（务必遵守）

- **许可证隔离**：`ModelTraining`(AGPL) 与 `ModelOffice`(Apache) 只能通过 CLI/子进程/MCP
  调用，**不得** `import` 进 MIT 模块。详见 [`LICENSES.md`](./LICENSES.md)。
- **原始文档不入库**：PDF/Word/Excel 等留本地，仓库只提交转换后的 `*.md`。
- **密钥不入库**：key 走 `.env`（已被 `.gitignore` 排除），参考各模块 `.env.example`。
- **改名只动外壳**：统一 `Model*` 命名只作用于顶层/编排层/自建组件；上游库(unsloth/e2b)
  内部命名与版权不动。

## 四阶段管线（训练为主）

```
阶段0 数据合成: ModelIngest(107 PDF→md) + ModelProvider(teacher 蒸馏) → 数千训练样本
阶段1 视觉微调: ModelTraining(unsloth FastVisionModel + Gemma) → 导出 GGUF + mmproj
阶段2 本地承载: ollama create/serve → 私有模型
阶段3 双通道:   VSCode Copilot 原生 + API/MCP
检索兜底:       obsidian-rag(Ollama embedding + 向量库)
```

详见 [`docs/architecture.md`](./docs/architecture.md)。
