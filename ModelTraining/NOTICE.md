# NOTICE — ModelTraining

本模块是 **ModelToolbox** 的一部分，用于承担「训练」层：以用户的私有知识库
对小型多模态模型（Gemma 系）进行小样本微调，并导出为 GGUF 供 Ollama 承载。

## 派生声明（Derivative Work）

- 上游项目：**Unsloth**（https://github.com/unslothai/unsloth）
- 上游许可证：**GNU Affero General Public License v3.0 (AGPL-3.0)**
- 原始许可证文本完整保留于本目录 [`COPYING`](./COPYING)，上游版权归其原作者所有。

根据 AGPL-3.0 条款，本模块保留上游版权声明与许可证，并在此声明由
ModelToolbox 维护者所做的修改。

## ModelToolbox 侧的修改概述

- 仅在**产品外壳层**做集成性包装（后续以 `model-serve-mcp` 暴露训练/推理/导出为 MCP 工具）。
- 不改动 Unsloth 内部实现与其版权署名。
- 面向本项目的四阶段管线（文档转 md → 数据合成 → Gemma 视觉微调 + mmproj → Ollama）做流程编排。

## 许可证隔离

- 本模块整体保持 **AGPL-3.0**。
- ModelToolbox 其他模块（MIT / Apache 等）与本模块**仅通过 MCP / CLI / API 松耦合**调用，
  不将本模块源码 `import` 进异许可证模块，以避免许可证传染。

详见仓库根 [`LICENSES.md`](../LICENSES.md)。
