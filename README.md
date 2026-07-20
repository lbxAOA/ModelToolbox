<h1 align="center">ModelToolbox</h1>

<p align="center">
  <b>一整套「私有 · 小样本 · 多模态」本地模型系统</b><br>
  在个人笔记本上，把你自己的知识库训练进一个小模型，<br>
  让它在你覆盖的领域内（含看原理图 / PCB）达到甚至超过通用旗舰模型的水平。
</p>

<p align="center">
  <a href="#-理念">理念</a> •
  <a href="#-系统架构">架构</a> •
  <a href="#-模块一览">模块</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-许可证">许可证</a>
</p>

---

## ✨ 理念

主流「大模型 + RAG」方案在个人笔记本上有两个痛点：**吃硬件**、**依赖联网的闭源 API**。

ModelToolbox 走另一条路 —— **训练为主，检索兜底**：

- **知识焊进权重**：用你的 Obsidian 知识库微调一个小的多模态模型（Gemma 系，自带视觉），
  知识进了权重，推理时只需一个轻量本地模型。
- **看得见图**：模型保留视觉能力，能读你的原理图 / PCB 截图，结合领域知识做判断、挑错。
- **窄领域超越旗舰**：在「你亲手喂过的知识点 + 看图判断」上，一个专精小模型可以胜过
  「什么都会但都不精」的通用旗舰。
- **闭源 API 作为工具**：需要时调用 OpenAI / Anthropic / Gemini / DeepSeek —— 主要用来
  **蒸馏训练数据**（老师模型）和**兜底 / 效果对比**，而非日常依赖。

> 现实校准：能做到的是「在你的知识点与看图判断上超过旗舰」；做不到的是「在整个领域全面超过」。
> 目标锚定前者。

## 🏗 系统架构

```
原始文档(本地,不上传)
   PDF / Word / Excel / PPT / 图片
        │
        ▼  ① ModelIngest  ── 转 md + 抽页图,保留原件
   md 语料 + 页图(assets,本地)
        │
        ▼  ② 数据合成(ModelProvider 老师模型) ── PDF/md → 数千训练样本
   训练集(问答 / 看图推理 / 原理图挑错)
        │
        ▼  ③ ModelTraining(unsloth) ── Gemma 视觉 LoRA 微调 → GGUF + mmproj
   私有多模态模型
        │
        ▼  ④ Ollama serve(本地) ── ollama create / serve
   localhost:11434 (/v1 OpenAI 兼容 + /api)
        │
   ┌────┴─────────────────────────────┐
   ▼ 人肉通道                          ▼ 系统通道
   VSCode Copilot 选本地模型           Agent 运行时 / MCP 工具
        └──── 上传原理图/PCB → 看图 + 领域知识 → 判断 ────┘
                          │
                          ▼ 兜底
                  obsidian-rag-mcp(训练未覆盖 / 需精确引用原文时检索)
```

编排原则：**MCP 统一总线 + 模块松耦合**。模块之间通过 MCP / CLI / API 边界通信，
不做深度代码耦合 —— 既满足许可证隔离，也让每块可独立演进。

## 🧩 模块一览

| 模块 | 职责 | 形态 | 许可证 |
|------|------|------|--------|
| **ModelIngest** | 原始文档（PDF/Word/Excel/PPT/图片）→ Markdown，保留本地原件 | CLI (+MCP) | MIT |
| **ModelProvider** | 统一闭源大模型接口：OpenAI / Anthropic / Gemini / DeepSeek（+本地 Ollama） | 库 / API | MIT |
| **ModelTraining** | 小样本多模态微调（Gemma 视觉），导出 GGUF | CLI / Studio | AGPL-3.0 · unsloth 派生 |
| **ModelMCP** | 给模型的硬件工具手：Altium / LTspice / Obsidian-RAG 等 MCP server | MCP | 各服务器独立 |
| **ModelMemory** | 跨会话记忆 + 代码知识图谱审查 | MCP / Action | 见模块 |
| **ModelSkill** | 私有 Skill registry 与自动路由 | Plugin | MIT |
| **ModelOffice** | 代码执行 / 沙箱与 SDK | SDK | Apache-2.0 · e2b 派生 |
| **ObsidianRag** | 知识库语料（训练语料源 · 检索源） | 数据 | 内容各自版权 |

> 命名约定：产品外壳统一 `Model*` 体系；**上游开源库（unsloth / e2b 等）内部命名与版权署名一律保留**。

## 🚀 快速开始

> 🚧 项目开发中。各模块的详细安装见对应目录的 `README.md`。

```bash
# 1. 文档转语料（原件留本地，不上传）
#    cd ModelIngest && ...

# 2. 合成训练数据（需配置闭源 API 密钥，见 ModelProvider/.env.example）
#    cd ModelProvider && ...

# 3. 微调并导出 GGUF(+mmproj)
#    cd ModelTraining && ...

# 4. 本地承载
#    ollama create my-hw-vlm -f Modelfile && ollama serve

# 5. 使用：VSCode Copilot 选本地模型，或走 localhost:11434 API
```

详见 [`docs/architecture.md`](docs/architecture.md)。

## 📄 许可证

本仓库为**多许可证**工程，各模块 license 隔离，互不传染。根编排 / 胶水代码采用
[MIT](LICENSE)；派生自开源项目的模块（ModelTraining←unsloth AGPL-3.0，
ModelOffice←e2b Apache-2.0 等）**沿用其原始许可证并保留版权署名**。完整映射见
[`LICENSES.md`](LICENSES.md)。
