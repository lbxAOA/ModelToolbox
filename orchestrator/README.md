# orchestrator — ModelToolbox 顶层编排层

把 8 个模块串成一套系统的**入口层**。不发明新协议，以 MCP 为统一总线 + 轻量适配。

## 内容

| 文件 | 作用 |
|------|------|
| `mcp.aggregate.json` | 聚合所有子模块的 MCP server（已实现 `enabled:true`；占位 `enabled:false`），以及非 MCP 的 CLI 适配器（provider/ingest） |
| `bootstrap.ps1` / `bootstrap.sh` | 一键初始化：装纯 Python 外壳模块、生成 `.env`、拉 Ollama embedding 模型 |

系统级 persona 与模块选择策略见仓库根 [`../CLAUDE.md`](../CLAUDE.md)。

## 快速开始

```powershell
# Windows
./orchestrator/bootstrap.ps1
```

```bash
# macOS / Linux
./orchestrator/bootstrap.sh
```

## MCP server 状态

- **已实现**：`altium`、`ach-roundtable`、`code-review-graph`
- **占位/规划中**：`obsidian-rag`、`ltspice`、`model-serve`、`sandbox`（见 P4 管线）

`bootstrap` 只安装纯 Python 外壳模块（ModelProvider / ModelIngest），
**不**自动安装 AGPL 的 ModelTraining —— 需用户显式进入该目录处理，以维持许可证边界。
