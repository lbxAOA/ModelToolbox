# pipeline — ModelToolbox 四阶段管线

把「文档 → 训练数据 → 私有模型 → 本地承载 → 双通道调用」串成一条可执行的链路。
这是**训练为主**理念的落地层：让知识焊进权重，而非仅靠检索。

```
阶段0 数据合成   ModelIngest(md) + ModelProvider(teacher 蒸馏)  → train.jsonl
阶段1 视觉微调   ModelTraining(unsloth, 子进程) Gemma 视觉 LoRA  → GGUF + mmproj
阶段2 本地承载   本模块生成 Modelfile → ollama create           → 私有模型
阶段3 双通道     VSCode Copilot 原生 Ollama  +  API/MCP(orchestrator)
兜底           obsidian-rag-mcp 检索(见 ModelMCP/obsidian-rag-mcp)
```

## 许可证边界

本模块 **MIT**。只 `import modelprovider`(MIT)，对 AGPL 的 ModelTraining
**仅通过子进程 CLI** 调用（`pipeline_mt/train.py`），不 import 其代码。

## 安装

```bash
cd pipeline
pip install -e ".[provider,dev]"
```

## 用法

### 阶段0：合成训练数据

先用 ModelIngest 把知识库转成 md，再蒸馏：

```bash
# 先配置 teacher（见 ModelProvider/.env.example: MODELTOOLBOX_TEACHER）
pipeline datagen --corpus ObsidianRag --out pipeline/out/train.jsonl --limit 5
```

`--limit` 先跑几篇验证质量，再全量。产物 `train.jsonl` 为 chatml 格式。

### 阶段1：视觉微调（子进程调 unsloth）

```bash
# 默认只打印命令（安全预演）；确认后加 --execute
pipeline train --config pipeline/configs/train.gemma-vision.yaml
pipeline train --config pipeline/configs/train.gemma-vision.yaml --execute
```

配置模板 `configs/train.gemma-vision.yaml` 已设 `finetune_vision_layers: true`
+ 4bit LoRA（笔记本友好）。导出 GGUF 时**务必带 mmproj**，否则 Ollama 看不见图。

### 阶段2：Ollama 承载

```bash
pipeline serve --gguf pipeline/out/model.gguf \
               --mmproj pipeline/out/mmproj.gguf \
               --name modeltoolbox-private --execute
```

生成 `Modelfile` 并 `ollama create`。之后即可在 VSCode Copilot 选本地模型，
或经 `orchestrator/mcp.aggregate.json` 走 API/MCP。

## 关键风险提示

- **mmproj 必带**：Gemma 视觉微调导出若漏掉视觉投影，模型将「看不见」原理图。
- **数据不足**：硬件类原始笔记很少，阶段0靠 teacher + 107 份 PDF 放大到数千样本。
- **先 dry-run**：train/serve 默认不执行，确认命令无误再 `--execute`。

产物目录 `pipeline/out/`（GGUF/JSONL/adapter）已被 `.gitignore` 排除。
