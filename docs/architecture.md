# ModelToolbox 架构文档

> 私有 · 小样本 · 多模态 · 本地运行。训练为主，检索兜底。

## 1. 设计目标

在**个人笔记本**上，用用户自己的 Obsidian 知识库，训练一个小的多模态模型，使其在
**用户知识库覆盖的领域 + 看图（原理图 / PCB）判断**上达到甚至超过通用旗舰模型。

- 现实可达：在「亲手喂过的知识点 + 看图判断」上超过旗舰。
- 现实不可达：在整个领域全面超过旗舰。目标锚定前者。

## 2. 为什么「训练为主」而非「RAG 为主」

| 维度 | RAG 为主 | 训练为主（本项目） |
|------|----------|--------------------|
| 知识位置 | 向量库，运行时检索注入 | 焊进模型权重 |
| 硬件要求 | 高（检索 + 长上下文） | 低（推理只需小模型） |
| 联网依赖 | 常需嵌入 / 检索服务 | 纯本地 |
| 一致性 | 依赖检索质量 | 稳定 |
| RAG 角色 | 主力 | **兜底**（训练未覆盖 / 需精确引用原文） |

## 3. 数据 / 控制流

```
① ModelIngest        原始文档(PDF/Word/Excel/PPT/图片) → md + 页图(assets)
                     · 原件保留本地, 不上传
                     · md 带 front-matter 溯源, hash 增量
        │
② 数据合成           md/PDF + ModelProvider 老师模型(闭源旗舰) → 数千训练样本
   (阶段0)           · 领域问答 / 看图推理 / 原理图挑错
                     · 质量过滤去重
        │
③ ModelTraining      Gemma3(自带视觉) + unsloth FastVisionModel LoRA
   (阶段1)           → export GGUF + mmproj.gguf(★视觉投影必带)
        │
④ Ollama             ollama create → serve localhost:11434 (/v1 + /api)
   (阶段2)
        │
⑤ 调用               ① VSCode Copilot 选本地模型(人肉)
   (阶段3)           ② Agent / MCP(系统自动)
                     兜底: obsidian-rag-mcp
```

## 4. 编排：MCP 统一总线

- **总线**：所有能力以 MCP server 暴露，由顶层 `orchestrator/mcp.aggregate.json` 聚合。
- **松耦合**：模块间只经 MCP / CLI / API 通信，不深度 `import`。既满足许可证隔离
  （AGPL 的 ModelTraining 不污染 MIT 模块），也让每块可独立演进。
- **双通道调用**：人肉（VSCode Copilot 原生 Ollama）与系统自动（OpenAI 兼容 API / MCP）
  并存，互不冲突。

## 5. 闭源大模型的三个角色（ModelProvider）

1. **老师模型**：阶段0 数据蒸馏，把教材 / 笔记合成训练样本。
2. **兜底 / 对比**：本地模型答不好时回退；或做「小模型 vs 旗舰」评测。
3. **过渡 provider**：训练完成前先用闭源 API 跑通全流程。

支持：OpenAI · Anthropic · Gemini · DeepSeek（OpenAI 兼容为基准）+ 本地 Ollama。

## 6. 关键风险

| 风险 | 说明 | 对策 |
|------|------|------|
| 训练数据不足 | 硬件领域仅 9 篇短 md，直接训会过拟合 | 阶段0 用 107 份 PDF 教材 + 老师模型放大成数千样本 |
| mmproj 缺失 | Gemma 视觉微调导出若漏视觉投影，Ollama 里「看不见图」 | 导出流程强制校验 mmproj.gguf |
| 许可证传染 | ModelTraining 为 AGPL | 各模块分 license + 松耦合边界 |
| 仓库臃肿 / 泄漏 | 原始文档、权重、venv | .gitignore 排除，原件只留本地 |

## 7. 模块状态

| 模块 | 状态 |
|------|------|
| ModelMCP (altium/ach-roundtable) | 已有源码；ltspice / obsidian-rag-mcp 待实现 |
| ModelTraining | unsloth 基座就位，视觉微调 + 导出流程待封装 |
| ModelOffice | e2b SDK 就位，待包 MCP |
| ModelMemory / ModelSkill | 就位 |
| ModelIngest / ModelProvider / orchestrator | 待建（本轮计划） |

详见根 [`README.md`](../README.md) 与 [`LICENSES.md`](../LICENSES.md)。
