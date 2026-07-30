# 快速开始

本指南将帮助您快速上手 ModelIngest。

## 安装

### 方式 1：从 PyPI 安装（推荐，v1.0）

```bash
pip install modelingest
```

### 方式 2：从源码安装

```bash
git clone https://github.com/yourusername/modelingest.git
cd ModelIngest
pip install -e .
```

### 方式 3：安装 v2.0（开发版）

```bash
cd ModelIngest/v2
pip install -e common -e core -e parse -e clean
```

## 基础使用（v1.0）

### 1. 解析本地文档

```bash
# 准备文档目录
mkdir raw_docs
# 将 PDF、Word、Excel 等文件放入 raw_docs/

# 执行解析
modelingest run --source ./raw_docs --output ./md_output
```

输出结构：
```
md_output/
├── document1.md
├── document2.md
└── ...
```

### 2. 知识蒸馏

```bash
# 将 Markdown 蒸馏为原子笔记
modelingest distill \
  --source ./md_output \
  --output ./knowledge_base \
  --profile concept
```

输出结构：
```
knowledge_base/
├── 概念A.md
├── 概念B.md
├── MOC_index.md
└── ...
```

### 3. 网页爬取

```bash
# 爬取网站内容
modelingest crawl \
  --url https://example.com/docs \
  --output ./raw_docs \
  --depth 2
```

### 4. 一键构建（实验性）

```bash
# 从原始文档到知识库
modelingest build \
  --source ./raw_docs \
  --output ./knowledge_base \
  --distill
```

## v2.0 使用

### 1. 初始化配置

```bash
cd v2
python -m modelingest_core.cli init --visual
```

生成 `modelingest.yaml`：
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

### 2. 执行构建

```bash
python -m modelingest_core.cli build \
  --source ./raw_docs \
  --output ./kb \
  --visual
```

### 3. 单独运行某个阶段

```bash
# 只执行视觉渲染
python -m modelingest_core.cli render \
  --source ./webpage.html \
  --output ./tiles

# 只执行解析
python -m modelingest_core.cli parse \
  --source ./files \
  --output ./md
```

## 常见场景

### 场景 1：整理技术文档

```bash
# 1. 准备文档
mkdir tech_docs
# 将 PDF 技术文档放入 tech_docs/

# 2. 执行转换
modelingest run --source ./tech_docs --output ./tech_md

# 3. 蒸馏为笔记
modelingest distill \
  --source ./tech_md \
  --output ./tech_kb \
  --profile concept

# 4. 在 Obsidian 中打开 tech_kb/
```

### 场景 2：爬取在线教程

```bash
# 1. 爬取课程网站
modelingest crawl \
  --url https://course.example.com \
  --output ./course_raw \
  --depth 3

# 2. 转换为知识库
modelingest build \
  --source ./course_raw \
  --output ./course_kb \
  --distill
```

### 场景 3：研究论文库

```bash
# 1. 准备论文
mkdir papers
# 将 PDF 论文放入 papers/

# 2. 使用研究配置
modelingest distill \
  --source ./papers \
  --output ./research_kb \
  --profile research
```

## 配置文件

### 创建配置文件

```bash
# 生成默认配置
modelingest config init

# 编辑配置
vim ~/.modelingest/config.yaml
```

### 配置示例

```yaml
# ~/.modelingest/config.yaml

parsers:
  priority: [mineru, docling, markitdown]
  
distill:
  default_profile: concept
  model: gpt-4
  
output:
  structure: obsidian
  create_moc: true
```

## 高级用法

### 自定义解析器优先级

```bash
modelingest run \
  --source ./docs \
  --output ./md \
  --parsers mineru docling markitdown
```

### 指定 LLM 模型

```bash
modelingest distill \
  --source ./md \
  --output ./kb \
  --model gpt-4 \
  --profile algorithm
```

### 增量更新

```bash
# 首次运行
modelingest run --source ./docs --output ./md

# 添加新文档到 docs/

# 增量更新（只处理新文件）
modelingest run --source ./docs --output ./md
```

## 故障排除

### 问题 1：解析失败

```bash
# 查看详细日志
modelingest run --source ./docs --output ./md --verbose

# 尝试不同解析器
modelingest run --source ./docs --output ./md --parsers docling
```

### 问题 2：蒸馏错误

```bash
# 检查 API 配置
echo $OPENAI_API_KEY

# 使用本地模型
modelingest distill --source ./md --output ./kb --model ollama/llama3
```

### 问题 3：中文乱码

```bash
# 指定编码
modelingest run --source ./docs --output ./md --encoding utf-8
```

## 下一步

- 阅读 [配置指南](configuration.md)
- 查看 [API 文档](api.md)
- 探索 [示例项目](../examples/)
- 了解 [v2.0 新特性](../v2/README.md)

## 获取帮助

```bash
# 查看命令帮助
modelingest --help
modelingest run --help
modelingest distill --help

# 查看版本
modelingest --version
```

---

遇到问题？[提交 Issue](https://github.com/yourusername/modelingest/issues)
