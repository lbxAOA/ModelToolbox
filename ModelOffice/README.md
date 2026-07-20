# ModelOffice

模型的**办公室**：代码执行 / 沙箱环境与配套 SDK，让模型能安全地运行代码、处理任务。

## 组成

- `packages/` — 多语言 SDK（`python-sdk` / `js-sdk` / `cli` / `connect-python`）。
- `templates/` — 沙箱环境模板（含 E2B Dockerfile）。
- `spec/` — 接口规范与 MCP server 目录。

## 定位

派生自开源沙箱项目 **e2b**（Apache-2.0）。在 ModelToolbox 中承担「执行 / 沙箱」层 ——
后续将包成 `sandbox-mcp`，让技能里的代码执行走隔离沙箱，而非直接在主机上跑。

> 许可证：Apache-2.0（e2b 派生），保留原始 LICENSE 与 NOTICE。详见根 `LICENSES.md`。
