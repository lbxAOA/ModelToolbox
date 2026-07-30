# ModelIngest

> 多模态文档 → 结构化知识库转换器

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

ModelIngest 是一个强大的文档处理工具，采用独立包架构，支持将各种格式的文档（PDF、Word、HTML 等）转换为结构化的 Obsidian 知识库，并支持视觉+文本双通道处理。

## ✨ 特性

- 📄 **多格式支持**：PDF、DOCX、XLSX、PPTX、HTML 等
- � **网页爬取**：支持网站内容抓取（零依赖，基于 urllib）
- 🎨 **视觉渲染**：使用 Playwright 和 PyMuPDF 渲染网页/PDF 为截图
- 🔄 **增量处理**：基于 SHA256，只处理变更文件
- 🧠 **知识蒸馏**：通过 LLM 提炼原子笔记
- 🔗 **自动建链**：生成 wikilink 和 MOC
- 🏗️ **模块化架构**：独立包设计，清晰解耦
- 🎯 **解析器注册表**：插件式架构，易于扩展

## 📦 项目结构

```
ModelIngest/
├── common/              # 共享工具包
│   └── src/modelingest_common/
│       ├── manifest.py
│       ├── progress.py
│       ├── frontmatter.py
│       └── guideline.py
│
├── core/                # 核心编排
│   └── src/modelingest_core/
│       ├── cli.py
│       ├── handlers.py
│       ├── config.py
│       ├── contracts.py
│       └── orchestrator.py
│
├── fetch/               # 内容获取
│   └── src/modelingest_fetch/
│       ├── stage.py
│       └── crawler.py
│
├── render/              # 视觉渲染 ⭐
│   └── src/modelingest_render/
│       ├── stage.py
│       ├── screenshot.py
│       └── tile_generator.py
│
├── parse/               # 文档解析
│   └── src/modelingest_parse/
│       ├── stage.py
│       ├── registry.py
│       └── parsers/
│
├── clean/               # 内容清洗
│   └── src/modelingest_clean/
│       └── stage.py
│
├── distill/             # 知识蒸馏
│   └── src/modelingest_distill/
│       ├── distiller.py
│       ├── teacher.py
│       ├── chunk.py
│       ├── profiles.py
│       └── linker.py
│
└── organize/            # 知识组织
    └── src/modelingest_organize/
        ├── stage.py
        └── organizer.py
```

## 🚀 快速开始

### 安装

```bash
# 基础功能
pip install -e .

# 完整功能（包含所有可选依赖）
pip install -e ".[all]"

# 按需安装
pip install -e ".[fetch]"      # 网页爬取
pip install -e ".[visual]"     # 视觉渲染
pip install -e ".[distill]"    # 知识蒸馏
pip install -e ".[organize]"   # 知识组织
```

### 基本用法

#### 1. 端到端构建（推荐）

```bash
# 从本地目录构建
modelingest build --source ./docs --output ./knowledge_base

# 从网页构建
modelingest build --source https://example.com --output ./kb

# 启用所有功能
modelingest build --source ./docs --output ./kb --visual --distill
```

#### 2. 网页爬取

```bash
# 发现链接（不下载）
modelingest discover --url https://example.com --depth 2

# 抓取网页
modelingest crawl --url https://example.com --output ./raw_docs --depth 1
```

#### 3. 文档解析

```bash
# 解析为 Markdown
modelingest parse --source ./raw_docs --output ./markdown
```

#### 4. 知识蒸馏

```bash
# 生成准则（可选）
modelingest guideline --output ./kb --domain 算法 --interactive

# 执行蒸馏
modelingest distill --source ./markdown --output ./kb --profile algorithm
```

## 📚 命令参考

### 主命令

- `build` - 端到端构建知识库
- `discover` - 发现网页链接
- `crawl` - 抓取网页
- `parse` - 解析文档
- `distill` - 知识蒸馏
- `guideline` - 生成知识库准则

### 工具命令

- `init` - 生成配置文件模板
- `scan` - 扫描待处理文件
- `status` - 查看增量状态
- `clean` - 清理缓存

## 🎨 架构设计

ModelIngest 采用**独立包架构**，每个包负责特定功能：

- **解耦设计**：各阶段独立开发、测试、发布
- **灵活组合**：按需安装和使用
- **易于扩展**：插件式架构，支持自定义解析器
- **类型安全**：完整的类型标注

## 🔧 配置

支持 Python 代码配置和 YAML 文件配置：

```yaml
# modelingest.yaml
version: "2.0"

source_type: local
source_path: ./docs

stages:
  - fetch
  - parse
  - clean
  - distill

output_root: ./knowledge_base
overwrite: false
max_workers: 4
```

## 📖 文档

- [快速入门](docs/v2-quickstart.md)
- [架构设计](docs/modelingest-refactor-summary.md)

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
├── distill/             # 知识蒸馏
├── organize/            # 知识库组织
│
├── modelingest_v1_legacy/  # v1.0 旧版代码（保留）
├── docs/                # 文档
├── examples/            # 示例
└── tests/               # 测试
```

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/modelingest.git
cd ModelIngest

# 安装核心包
pip install -e common -e core -e parse -e clean

# 可选：安装视觉渲染
pip install -e render
playwright install chromium
```

### 基础使用

```bash
# 1. 初始化配置（可选）
python -m modelingest_core.cli init

# 2. 构建知识库（推荐）
python -m modelingest_core.cli build \
  --source ./raw_docs \
  --output ./knowledge_base \
  --visual

# 3. 单独运行某个阶段
python -m modelingest_core.cli parse \
  --source ./raw_docs \
  --output ./md_output
```

### 配置文件使用

创建 `modelingest.yaml`：

```yaml
source:
  type: local
  path: ./raw_docs

pipeline:
  stages: [render, parse, clean]
  
  render:
    enabled: true
    mode: tiles

output:
  root: ./knowledge_base
```

然后执行：

```bash
python -m modelingest_core.cli build --config modelingest.yaml
```

## 📖 文档

- [快速开始](docs/quickstart.md)
- [架构设计](docs/modelingest-refactor.md)
- [预期效果](docs/modelingest-expected-outcomes.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

## 🔧 高级配置

创建 `modelingest.yaml` 配置文件：

```yaml
source:
  type: local
  path: ./raw_docs

pipeline:
  stages: [render, parse, clean, distill, organize]
  
  # 视觉渲染配置
  render:
    enabled: true
    mode: tiles          # tiles | full
    tile_width: 1024
    tile_height: 1024
  
  # 解析配置
  parse:
    parsers: [visual, mineru, docling, markitdown]
    
  # 蒸馏配置
  distill:
    profile: concept     # concept | algorithm | research
    model: gpt-4         # 可选

output:
  root: ./knowledge_base
  structure: obsidian
```

## 🛠️ 开发

```bash
# 安装开发依赖
pip install -e common[dev] -e core[dev]

# 运行快速测试
python test_quick.py

# 代码检查
black common/ core/ parse/ clean/
pylint common/ core/ parse/ clean/
```

## 🏗️ 架构特点

### 独立包设计

每个阶段都是独立的 Python 包，可单独安装和使用：

```bash
# 只安装解析功能
pip install -e common -e core -e parse

# 添加视觉渲染
pip install -e render

# 完整安装
pip install -e common -e core -e render -e parse -e clean -e distill -e organize
```

### 解析器注册表

支持插件式扩展：

```python
from modelingest_parse.registry import register_parser

@register_parser("my_parser", priority=50)
def parse_my_format(path: Path) -> Optional[str]:
    """自定义解析器"""
    return markdown_text
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史。

## 📄 许可

[MIT License](LICENSE)

## 🙏 致谢

- [markitdown](https://github.com/microsoft/markitdown) - 文档解析
- [Playwright](https://playwright.dev/) - 网页渲染
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF 处理
- [PixelRAG](https://github.com/StarTrail-org/PixelRAG) - 架构灵感

## 📧 联系

- 问题反馈：[GitHub Issues](https://github.com/yourusername/modelingest/issues)
- 讨论区：[GitHub Discussions](https://github.com/yourusername/modelingest/discussions)

## 🗂️ 旧版本

v1.0 代码已移至 `modelingest_v1_legacy/` 目录，供参考使用。
