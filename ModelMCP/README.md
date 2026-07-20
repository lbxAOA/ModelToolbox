# ModelMCP

给模型的**工具手**：一组 MCP (Model Context Protocol) server，让模型能连接并操作第三方工具，
以硬件 / 电子设计为主。

## 子服务器

| 目录 | 作用 | 状态 |
|------|------|------|
| `altium-mcp/` | 从模型控制 Altium Designer：查元件、建符号 / 封装、布局、输出 | 已有 |
| `ach-roundtable-mcp/` | ACH（竞争性假设分析）多智能体圆桌 | 已有 |
| `ltspice/` | LTspice 电路仿真：读写 .asc、改参数、跑仿真、读回工作点 / 波形 | 🚧 待实现 |
| `obsidian-rag-mcp/` | 对 ObsidianRag 语料的检索（RAG 兜底）：search / get-note | 🚧 待实现 |

## 定位

在 ModelToolbox 中，ModelMCP 提供「模型看得见图之后还能动手」的能力 —— 训练让模型**懂**硬件，
MCP 让它能**操作**硬件工具链。通过顶层 `orchestrator` 聚合进 MCP 总线。

> 许可证：各子服务器独立，详见各自目录与根 `LICENSES.md`。
