# ModelMemory 快速参考

## 一分钟开始

```bash
# 1. 启动 Neo4j
docker run -d -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j

# 2. 安装依赖
pip install neo4j tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript

# 3. 初始化项目
cd your-project
mtb memory init .

# 4. 解析代码
mtb memory parse .

# 5. 搜索
mtb memory search "function_name"
```

## 常用命令

```bash
mtb memory init .              # 初始化
mtb memory parse .             # 解析代码库
mtb memory search "query"      # 搜索
mtb memory stats               # 统计
mtb memory update file.py      # 更新单个文件
```

## Python API

```python
from modeltoolbox_memory import CodeGraph

graph = CodeGraph.from_project(".")
graph.init()
stats = graph.parse()
results = graph.search("auth")
graph.close()
```

## 配置位置

`~/.modeltoolbox/state/memory/config.json`

## 文档

- **完整指南**: [README.md](README.md)
- **迁移指南**: [MIGRATION.md](MIGRATION.md)
- **重构报告**: [COMPLETION_REPORT.md](COMPLETION_REPORT.md)

## 核心概念

- **节点**: File, Function, Class, Package
- **关系**: CONTAINS, CALLS, IMPORTS, INHERITS
- **搜索**: 全文搜索（Neo4j FTS）+ 语义搜索（可选）
- **更新**: 增量更新（重新解析变更文件）

## 依赖

- Neo4j 5.0+
- Python 3.11+
- tree-sitter 0.21+

## 状态

✅ Python 解析  
⏳ JavaScript/TypeScript（框架就绪）  
⏳ 语义搜索（框架就绪）  
⏳ 影响分析（框架就绪）
