# ModelProvider

**ModelToolbox 的统一大模型调用层。** 把闭源旗舰模型与本地模型收敛到一个接口，
让系统在「私有模型训练完成之前」就能跑通，并为训练提供数据蒸馏老师。

## 支持的 provider

| provider | 协议 | 默认模型 | 需要 key |
|----------|------|----------|----------|
| `openai` | OpenAI Chat Completions | `gpt-4o-mini` | ✅ |
| `deepseek` | OpenAI 兼容 | `deepseek-chat` | ✅ |
| `anthropic` | Anthropic Messages | `claude-3-5-sonnet-latest` | ✅ |
| `gemini` | Google generativelanguage | `gemini-1.5-flash` | ✅ |
| `ollama` | OpenAI 兼容（本地） | `llama3.1` | ❌ |

所有 provider 都支持**多模态**（文本 + 图像），适配器会把中立的 `ImagePart`
翻译成各家格式（OpenAI `image_url` / Anthropic `source.base64` / Gemini `inlineData`）。

## 三个角色

| 角色 | 用途 | 默认 |
|------|------|------|
| `teacher` | 数据蒸馏老师，合成训练样本（P4 阶段0） | `anthropic:claude-3-5-sonnet-latest` |
| `fallback` | 兜底 / 与私有模型对比的旗舰 | `openai:gpt-4o-mini` |
| `runner` | 训练完成前先跑通的本地模型 | `ollama:llama3.1` |

角色→模型可用环境变量覆盖：`MODELTOOLBOX_TEACHER` / `MODELTOOLBOX_FALLBACK` / `MODELTOOLBOX_RUNNER`。

## 安装

```bash
cd ModelProvider
pip install -e ".[dev]"
```

零运行时依赖（HTTP 走标准库 `urllib`）。

## 配置

复制 `.env.example` 为 `.env`（放仓库根或运行目录），填入 key。
`.env` 已被根 `.gitignore` 排除，不会提交。

## 用法

### Python

```python
from modelprovider import LLMClient, Message, ImagePart, TextPart

# 按 provider
client = LLMClient.for_provider("deepseek")
print(client.ask("用一句话解释运放的虚短虚断"))

# 按角色
teacher = LLMClient.for_role("teacher")
sample = teacher.ask("为这段电路知识生成一条问答训练样本", system="你是电子学老师")

# 多模态：看原理图
vision = LLMClient.for_provider("openai", model="gpt-4o")
msg = Message("user", [TextPart("这张原理图有什么问题？"),
                       ImagePart.from_path("schematic.png")])
from modelprovider import ChatRequest
print(vision.chat(ChatRequest(messages=[msg])).text)
```

### CLI

```bash
modelprovider list                      # 查看 provider/角色与 key 状态
modelprovider ask "你好" --provider ollama
modelprovider ask "解释傅里叶变换" --role teacher
modelprovider ping --provider openai
```

## 在 ModelToolbox 中的位置

- **训练前**：`runner` 让整套系统先用本地通用模型跑通链路。
- **训练中**：`teacher` 用 107 份 PDF + 笔记蒸馏出数千条领域训练样本（P4 阶段0）。
- **训练后**：`fallback` 作为私有模型的兜底与对比基准。

许可证：MIT。与 AGPL 的 ModelTraining 仅通过 CLI/API 松耦合，互不 import。
