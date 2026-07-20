# NOTICE — ModelOffice

本模块是 **ModelToolbox** 的一部分，用于承担「执行 / 沙箱」层：让模型能在
隔离环境中安全运行代码与处理任务（后续以 `sandbox-mcp` 暴露）。

## 派生声明（Derivative Work）

- 上游项目：**E2B**（https://github.com/e2b-dev/E2B）
- 上游许可证：**Apache License 2.0**
- 原始许可证文本保留于各 SDK 子包（`packages/*/LICENSE`），上游版权归其原作者所有。

## ModelToolbox 侧的修改概述

- 仅在**产品外壳层**做集成性包装与文档（本模块 `README.md`）。
- 不改动 E2B SDK 内部实现与其版权署名（含 `CODEOWNERS`、`NOTICE` 等上游文件）。
- 计划将 python-sdk 包成 `sandbox-mcp`，使技能中的代码执行走隔离沙箱而非主机。

## 许可证隔离

- 本模块整体保持 **Apache-2.0**。
- 与其他模块**仅通过 MCP / CLI / API 松耦合**调用。

详见仓库根 [`LICENSES.md`](../LICENSES.md)。
