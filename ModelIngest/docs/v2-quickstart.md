# ModelIngest v2.0 快速上手指南

## 10 分钟快速开始

### 步骤 1：安装核心包（2 分钟）

```bash
cd c:\ModelToolbox\ModelIngest\v2

# 安装必需包（开发模式）
pip install -e common
pip install -e core
pip install -e parse
pip install -e clean

# 可选：安装视觉处理（推荐）
pip install -e render
playwright install chromium

# 可选：安装内容获取
pip install -e fetch
```

### 步骤 2：验证安装（1 分钟）

```bash
# 运行快速测试
python test_quick.py
```

预期输出：
```
🚀 ModelIngest v2.0 快速测试
============================================================
测试 1: 基础管道（parse + clean）
...
✓ 所有测试通过!
```

### 步骤 3：生成配置文件（1 分钟）

```bash
# 基础配置
python -m modelingest_core.cli init

# 启用视觉处理
python -m modelingest_core.cli init --visual --output kb_config.yaml
```

生成的配置文件示例：
```yaml
version: '2.0'
source:
  type: local
  path: ./raw_docs
pipeline:
  stages:
  - render
  - parse
  - clean
  render:
    mode: tiles
    tile_width: 1024
    tile_height: 1024
    overlap: 100
output:
  root: ./knowledge_base
  manifest_path: ./.ingest_cache/manifest.sqlite
  overwrite: false
```

### 步骤 4：准备测试数据（2 分钟）

```bash
# 创建测试目录
mkdir test_docs

# 添加一些测试文件
# - test_docs/sample.md
# - test_docs/sample.pdf
# - test_docs/sample.html
```

或使用现有文档：
```bash
# 使用 ObsidianRag 作为测试数据
# 路径：c:\ModelToolbox\ModelIngest\modelingest\ObsidianRag
```

### 步骤 5：执行构建（4 分钟）

#### 方式 A：使用配置文件

```bash
python -m modelingest_core.cli build --config kb_config.yaml
```

#### 方式 B：使用命令行参数

```bash
# 基础构建（只解析和清洗）
python -m modelingest_core.cli build \
  --source ./test_docs \
  --output ./my_kb

# 启用视觉处理
python -m modelingest_core.cli build \
  --source ./test_docs \
  --output ./my_kb \
  --visual

# 完整构建（视觉 + 文本 + 清洗）
python -m modelingest_core.cli build \
  --source ../modelingest/ObsidianRag \
  --output ./obsidian_kb \
  --visual
```

预期输出：
```
▶ ModelIngest v2.0 构建
  源路径: test_docs
  输出目录: my_kb
  执行阶段: render → parse → clean

▶ 执行阶段: render...
  ✓ 完成: {'files': 5, 'tiles': 47}
▶ 执行阶段: parse...
  ✓ 完成: {'files': 5, 'converted': 5, 'skipped': 0}
▶ 执行阶段: clean...
  ✓ 完成: {'files': 5, 'cleaned': 3}

✓ 构建完成!
```

### 步骤 6：检查输出（1 分钟）

```bash
# 查看输出结构
tree my_kb /F

# 示例输出：
my_kb/
├── .ingest_cache/
│   ├── manifest.sqlite          # 增量处理缓存
│   └── tiles/                   # 视觉瓦片
│       ├── page_0000.png
│       ├── page_0001.png
│       └── ...
├── sample.md                    # 转换后的 Markdown
├── sample_from_pdf.md
└── sample_from_html.md
```

## 常见使用场景

### 场景 1：技术文档知识库

```bash
# 1. 收集 PDF 技术文档到一个文件夹
mkdir tech_docs
# 复制文档到 tech_docs/

# 2. 构建知识库（启用视觉处理，保留表格和图表）
python -m modelingest_core.cli build \
  --source ./tech_docs \
  --output ./tech_kb \
  --visual

# 3. 查看结果
# 输出包含：
# - 原始文档截图（保留表格/图表/公式）
# - Markdown 文本（可搜索）
# - Frontmatter 元数据（溯源）
```

### 场景 2：在线课程笔记

```bash
# 1. 下载课程网页到本地
# （可使用现有 crawler，待集成）

# 2. 构建知识库
python -m modelingest_core.cli build \
  --source ./course_pages \
  --output ./course_kb \
  --visual

# 输出：每个网页的截图 + 文本
```

### 场景 3：只解析特定格式

```bash
# 只解析 PDF（使用特定解析器）
python -m modelingest_core.cli parse \
  --source ./pdfs \
  --output ./output \
  --parsers mineru docling markitdown
```

### 场景 4：增量更新

```bash
# 首次构建
python -m modelingest_core.cli build \
  --source ./docs \
  --output ./kb \
  --visual

# 添加新文档到 docs/ 后，再次运行
# 只会处理新增或变更的文件（基于 SHA256）
python -m modelingest_core.cli build \
  --source ./docs \
  --output ./kb \
  --visual
```

## Python API 使用

```python
from pathlib import Path
from modelingest_core import IngestConfig, PipelineOrchestrator

# 简单用法
config = IngestConfig(
    source_path=Path("./docs"),
    output_root=Path("./kb"),
    stages=["parse", "clean"],
)

orchestrator = PipelineOrchestrator(config)
results = orchestrator.run()

print(f"完成: {results}")
```

```python
# 高级用法：启用视觉处理
config = IngestConfig(
    source_path=Path("./docs"),
    output_root=Path("./kb"),
    stages=["render", "parse", "clean"],
)

# 配置视觉渲染
config.enable_stage("render", {
    "mode": "tiles",
    "tile_width": 1024,
    "tile_height": 1024,
    "overlap": 100,
})

# 配置解析器优先级
config.enable_stage("parse", {
    "parsers": ["visual", "mineru", "docling", "markitdown"],
})

orchestrator = PipelineOrchestrator(config)
results = orchestrator.run()
```

## 故障排除

### 问题 1：找不到 modelingest_core 模块

```bash
# 确保已安装 core 包
pip install -e core

# 或者添加到 PYTHONPATH
export PYTHONPATH="$PYTHONPATH:c:/ModelToolbox/ModelIngest/v2/core/src"
```

### 问题 2：Playwright 浏览器未安装

```bash
# 安装 Chromium
playwright install chromium

# 如果遇到权限问题，使用管理员权限
```

### 问题 3：解析器不可用

```bash
# 检查已注册的解析器
python -c "from modelingest_parse import list_parsers; print(list_parsers())"

# 安装可选解析器
pip install docling  # 高级 PDF 解析
pip install mineru   # 公式识别
```

### 问题 4：YAML 配置加载失败

```bash
# 确保已安装 pyyaml
pip install pyyaml

# 或使用 Python 对象配置（不需要 YAML）
```

## 下一步

1. **添加自定义解析器**：参考 `parse/src/modelingest_parse/parsers.py`
2. **集成知识蒸馏**：待 distill 阶段迁移完成
3. **集成检索系统**：使用 ModelMCP/obsidian-rag-mcp
4. **性能优化**：并行处理、批量转换

## 更多资源

- **完整文档**：[README.md](README.md)
- **重构方案**：[../docs/modelingest-refactor.md](../docs/modelingest-refactor.md)
- **预期效果**：[../docs/modelingest-expected-outcomes.md](../docs/modelingest-expected-outcomes.md)
- **完成报告**：[COMPLETION_REPORT.md](COMPLETION_REPORT.md)

---

**版本**: 2.0.0  
**日期**: 2026-07-30  
**作者**: GitHub Copilot
