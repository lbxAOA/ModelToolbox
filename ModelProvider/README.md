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
| `claude_code` | 本地 CLI（subprocess 调用 `claude`） | 跟随 CLI 登录计划 | ❌ |
| `codex` | 本地 CLI（subprocess 调用 `codex`） | 跟随 CLI 登录计划 | ❌ |

所有 provider 都支持**多模态**（文本 + 图像），适配器会把中立的 `ImagePart`
翻译成各家格式（OpenAI `image_url` / Anthropic `source.base64` / Gemini `inlineData`）。
`claude_code`/`codex` 为 CLI 适配器，目前仅支持纯文本（图像分片会被忽略）。

### claude_code / codex —— 无需 API key 的 CLI Agent provider

这两个 provider 不走 HTTP API，而是用 `subprocess`（无 shell）调用本地已登录的
`claude`（Claude Code CLI）/ `codex`（OpenAI Codex CLI）可执行文件，直接复用终端里
已认证的会话/订阅，**不需要单独申请 API key**。适用于本地开发机已经登录了
这些编程助手、不想另付费 API 的场景（如 `teacher` 角色蔣馆训练数据）。

```bash
# CLI 需先安装并在本机完成登录（自行安装/登录，本模块不负责认证），
# PATH 中能找到 claude / codex 即可：
modelprovider ask "用一句话解释虚短虚断" --provider claude_code
modelprovider ask "解释傅里叶变换" --provider codex

# 把 teacher 角色改成免 key 的 CLI（无需 ANTHROPIC_API_KEY）：
MODELTOOLBOX_TEACHER=claude_code modelingest distill -s ../ObsidianRag_md -o ../KnowledgeVault
```

可用环境变量调整：

| 变量 | 作用 |
|------|------|
| `CLAUDE_CODE_BIN` / `CODEX_CLI_BIN` | 覆盖可执行文件路径（默认从 PATH 找 `claude`/`codex`）|
| `MODELTOOLBOX_CLAUDE_CODE_CMD` / `MODELTOOLBOX_CODEX_CMD` | 整体覆盖命令行模板（适配不同版本 CLI 的参数，`{prompt}` 会被替换为实际 prompt）|

注意：CLI 一般不暴露 token/usage 统计，`ChatResponse.usage` 固定为 0；完整 stdout/stderr
保留在 `ChatResponse.raw` 中便于排查。

## 三个角色

| 角色 | 用途 | 默认 |
|------|------|------|
| `teacher` | 数据蒸馏老师，合成训练样本（P4 阶段0） | `anthropic:claude-3-5-sonnet-latest` |
| `fallback` | 兜底 / 与私有模型对比的旗舰 | `openai:gpt-4o-mini` |
| `runner` | 训练完成前先跑通的本地模型 | `ollama:llama3.1` |

角色→模型可用环境变量覆盖：`MODELTOOLBOX_TEACHER` / `MODELTOOLBOX_FALLBACK` / `MODELTOOLBOX_RUNNER`。
值的格式是 `provider:model`（`model` 可省略，用 provider 默认模型），任何 provider 都可以给任何角色使用，
包括 API 型（openai/deepseek/anthropic/gemini）、本地开源型（ollama），以及 CLI Agent 型（claude_code/codex）。

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
