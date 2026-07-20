# ModelIngest

原始文档 → **结构化知识库**的两段式管线。

- **阶段 A 前置（crawl，可选）**：抓取公开网页 / 文件到本地，产物是原始 `.html`/`.pdf`/...，
  与本地文档一视同仁，随后交给 parse 正常转换。
- **阶段 A（parse）**：把 PDF / Word / Excel / PPT / 图片等统一转成带溯源信息的干净 `.md`，
  **保留本地原件（不上传）**。
- **阶段 B（distill）**：把干净 md 蒸馏成**结构化原子笔记**（一概念一卡片，固定 schema），
  并自动建 `[[wikilink]]` + 生成 MOC，产出像 `ObsidianRag/Algorithms/*.md` 那样的知识库。

下游消费：
- **ModelTraining 阶段0 数据合成** —— 用卡片 + PDF 页图合成训练样本
- **obsidian-rag-mcp** —— 检索兜底

## 设计要点

### 阶段 A 前置 —— crawl（可选）

| 维度 | 做法 |
|------|------|
| 定位 | 只做「抓取 + 落盘」，不做解析；抓下来的原始文件写入 `--output`（通常是某个 source 目录），随后用 `modelingest run` 像本地文档一样正常转换 |
| 依赖 | 零运行时依赖，用标准库 `urllib`（与 ModelProvider 的 HTTP 层同一套路），可注入假实现测试 |
| 礼貌抓取 | 默认遵守 `robots.txt`；请求间有 `--delay` 秒间隔；有 `--max-pages` 安全上限 |
| 增量 | sqlite manifest 按 URL 记录 etag / last-modified / sha256，未变则跳过（条件请求 304，或内容 hash 兜底）|
| 浅层深度抓取 | `--depth 0`（默认）只抓给定 URL；`--depth N` 从 HTML 中提取同域 `<a href>` 链接继续抓取（`--allow-cross-domain` 可放开跨域）|
| 落盘命名 | 按 URL host + path 镜像成相对路径，扩展名按响应 `content-type` 判定（html/pdf/txt/md/csv），回退到 URL 自带后缀 |

### 阶段 A —— parse

| 维度 | 做法 |
|------|------|
| 解析器 | 可插拔注册表，按优先级降级：**mineru → docling → marker → markitdown → passthrough**；复杂 PDF（多栏/公式/表格/阅读顺序）优先用 mineru/docling，未安装则自动退到 markitdown |
| 优先级覆盖 | `INGEST_PDF_PARSER=docling,markitdown`（逗号分隔）|
| 保留原件 | 原件留在 `--source`，md 写到 `--output`（镜像目录），原件由根 `.gitignore` 排除 |
| 溯源 | 每个 md 顶部 YAML front-matter：`source` / `sha256` / `converter` / `converted_at` / `assets` |
| 增量 | sqlite manifest 记录源文件 hash，未变则跳过 |
| 多模态 | PDF 每页渲染 PNG 存 `assets/`（供视觉训练）；需 `PyMuPDF`，缺失则降级 |

### 阶段 B —— distill

| 维度 | 做法 |
|------|------|
| 蒸馏老师 | 复用 **ModelProvider** 的 `teacher` 角色（旗舰模型），按 profile 受约束输出 JSON |
| 笔记模板 | `concept`（通用，默认）/ `algorithm`（复刻 Algorithms 版式）；见 `distill/profiles.py` |
| 稳健性 | JSON 抽取容错 + 轻量 schema 校验，非法 note 跳过并记录，不中断整批 |
| 原子化 | 按标题把长文切成概念块，每块产出 1-3 篇独立卡片 |
| 建链 | 第二遍扫全库标题，把 `Related` 改写成 `[[规范标题]]`，并为每个目录生成 `<目录> MOC.md`（幂等，可单独重跑）|
| 增量 | 独立的 distill manifest（源 md hash + profile 未变则跳过，蒸馏成本高）|

## 安装

```bash
cd ModelIngest
pip install -e ".[pdf,dev]"          # markitdown + PyMuPDF(页图) + pytest
pip install -e ".[parse]"            # 可选：docling（复杂 PDF）；或自行装 mineru/marker
pip install -e ../ModelProvider      # 阶段 B 需要（teacher 角色）
```

## 使用

### 阶段 A 前置 —— crawl（可选）

```bash
# 抓取单个公开页面，落盘到 source 目录下的 web 子目录
 modelingest crawl --url https://example.com/article --output ../ObsidianRag/web

# 批量抓取（每行一个 URL 的文件），深度 1 跟随同域链接
 modelingest crawl --urls-file urls.txt --output ../ObsidianRag/web --depth 1

# 忽略 robots.txt / 强制重抓（谨慎使用）
 modelingest crawl --url https://example.com/a --output ../ObsidianRag/web --overwrite

# 抓下来的原始文件随后用普通 阶段 A 流程转换成 md
 modelingest run --source ../ObsidianRag --output ../ObsidianRag_md
```

### 阶段 A —— parse

```bash
# 转换（增量）：原件留在 source，md 输出到 output
modelingest run --source ../ObsidianRag --output ../ObsidianRag_md

modelingest status --source ../ObsidianRag --output ../ObsidianRag_md   # 待转/已转/失效
modelingest clean  --source ../ObsidianRag --output ../ObsidianRag_md   # 清理源已删的记录与 md

# 可选开关
modelingest run -s ../ObsidianRag -o ../ObsidianRag_md --no-pdf-pages   # 不抽页图
modelingest run -s ../ObsidianRag -o ../ObsidianRag_md --overwrite      # 全量重转
INGEST_PDF_PARSER=docling modelingest run -s ... -o ...                 # 指定解析器
```

### 阶段 B —— distill

```bash
# 干净 md → 结构化知识库（默认 concept 模板，自动建链 + MOC）
modelingest distill --source ../ObsidianRag_md --output ../KnowledgeVault

# 算法类语料，复刻 Algorithms 版式
modelingest distill -s ../ObsidianRag_md -o ../KnowledgeVault --profile algorithm

# 指定蒸馏模型 / 只重跑建链
modelingest distill -s ../ObsidianRag_md -o ../KnowledgeVault --model deepseek:deepseek-chat
modelingest distill-link --output ../KnowledgeVault
```

## 输出示例

阶段 A：

```
ObsidianRag_md/
├── Hardware-PCB/
│   ├── 布线规则与技巧.md          # front-matter + 正文
│   └── assets/Horowitz/Horowitz_p0001.png   # PDF 页图（本地保留，不上传）
└── .ingest_cache/ingest_manifest.sqlite     # 增量状态（本地保留）
```

阶段 B（distill 产出，版式对齐 Algorithms）：

```
KnowledgeVault/
├── Hardware-PCB/
│   ├── 布线规则与技巧.md         # 原子卡片：Definition/Key Points/.../Related [[..]]
│   ├── ...
│   └── Hardware-PCB MOC.md       # 自动生成的目录索引
└── .distill_cache/distill_manifest.sqlite
```

parse 产物 md 顶部 front-matter：

```yaml
---
source: Hardware-PCB/Horowitz.pdf
sha256: 9f2b...
converter: docling
converted_at: 2026-07-20T16:00:00+00:00
assets:
  - assets/Horowitz/Horowitz_p0001.png
generator: ModelIngest
---
```

## 在 ModelToolbox 中的位置

流水线**最上游**：`ModelIngest(crawl → parse → distill) → 数据合成 → ModelTraining → Ollama → 调用`。
遵循「松耦合」原则，仅通过文件 / CLI 边界与其它模块交互；distill 通过 `import modelprovider`
调用 teacher（同为 MIT，许可证相容）。crawl 阶段不下载任何额外依赖，与 parse/distill 完全解耦。

> 许可证：MIT（ModelToolbox 原创）。依赖的 markitdown / docling / mineru / PyMuPDF 各自适用其许可证。
