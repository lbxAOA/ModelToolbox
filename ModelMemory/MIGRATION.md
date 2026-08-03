# ModelMemory 迁移指南

从旧版 SQLite 索引系统迁移到新版 Neo4j 图数据库系统。

## 重大变更

### 1. 数据库变更
- **旧版**: SQLite FTS5 (`~/.modeltoolbox/state/memory/graph.db`)
- **新版**: Neo4j 图数据库 (`bolt://localhost:7687`)

### 2. 命令变更

| 旧命令 | 新命令 | 说明 |
|--------|--------|------|
| `mtb memory index [path]` | `mtb memory parse [path]` | 解析代码库 |
| `mtb memory search "query"` | `mtb memory search "query"` | 全文搜索（保持不变） |
| `mtb memory context "query"` | `mtb memory search "query"` | 搜索（合并到 search） |
| `mtb memory impact path` | `mtb memory impact path` | 影响分析（保持不变） |
| `mtb memory doctor` | `mtb memory init` | 初始化（功能增强） |

### 3. 新增命令

```bash
mtb memory init [path]              # 初始化项目和数据库 schema
mtb memory update file1 file2       # 增量更新指定文件
mtb memory search-semantic "query"  # 语义搜索（需要配置）
mtb memory stats                    # 图统计信息
```

### 4. 选项变更

#### parse 命令
```bash
# 旧版
mtb memory index --db path/to/db.sqlite --include .py

# 新版
mtb memory parse --include "*.py" --exclude "tests/*"
# 注意: 数据库通过配置文件管理，不再是命令行选项
```

#### search 命令
```bash
# 旧版
mtb memory search "query" --root . --db path/to/db.sqlite

# 新版
mtb memory search "query" --limit 10 --json
# 注意: root 和 db 通过配置文件管理
```

## 迁移步骤

### 步骤 1: 安装依赖

```bash
# 安装新的依赖
pip install neo4j tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript
```

### 步骤 2: 启动 Neo4j

```bash
# 使用 Docker（推荐）
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# 或下载安装包
# https://neo4j.com/download/
```

### 步骤 3: 配置连接

创建或编辑配置文件 `~/.modeltoolbox/state/memory/config.json`:

```json
{
  "neo4j": {
    "uri": "bolt://localhost:7687",
    "username": "neo4j",
    "password": "password",
    "database": "neo4j"
  },
  "embedding": {
    "provider": "local",
    "model": "all-MiniLM-L6-v2"
  },
  "parser": {
    "languages": ["python", "javascript", "typescript"],
    "max_file_size": 1048576
  }
}
```

### 步骤 4: 初始化新系统

```bash
# 初始化项目
cd your-project
mtb memory init .
```

### 步骤 5: 重新索引

```bash
# 解析代码库
mtb memory parse .

# 查看统计
mtb memory stats
```

### 步骤 6: 验证迁移

```bash
# 测试搜索
mtb memory search "your_function_name"

# 检查结果
mtb memory stats --json
```

## 数据迁移

**重要**: 旧版 SQLite 数据 **无法自动迁移** 到 Neo4j。原因：

1. 数据结构完全不同（FTS vs 图）
2. 新版存储更丰富的元数据（AST 节点、关系）
3. 旧版只有文本，新版有结构化代码

### 保留旧数据

如果需要保留旧的 SQLite 索引：

```bash
# 备份旧数据库
cp ~/.modeltoolbox/state/memory/graph.db ~/.modeltoolbox/state/memory/graph.db.backup

# 旧版命令仍可用（如果保留 index.py.old）
# 但不推荐同时使用两套系统
```

### 并行运行

可以短期内并行运行两个系统：

1. 重命名 `index.py.old` 回 `index.py` 使用旧版
2. 使用新版时确保 `index.py` 被重命名

**不推荐长期并行**，建议完全迁移到新版。

## 功能对比

### 旧版能做的，新版都能做
✅ 全文搜索  
✅ 文件索引  
✅ 简单的影响分析（基于关键词）  

### 新版新增功能
✅ 结构化代码理解（函数、类）  
✅ 代码关系图（调用、继承、导入）  
✅ 更精确的影响分析  
✅ 语义搜索（可选）  
✅ MCP 服务器（AI 代理集成）  
✅ 增量更新  
✅ 多语言支持框架  

### 新版暂未实现
⏳ 完整的 JavaScript/TypeScript 支持（框架已就绪）  
⏳ 语义搜索（需要配置 embedding）  
⏳ 社区检测  
⏳ Web Dashboard  

## 常见问题

### Q: 为什么要迁移？
A: 新版提供结构化的代码理解，不仅是文本搜索，还能理解代码关系，为高级分析打基础。

### Q: 必须使用 Neo4j 吗？
A: 目前是的。未来可能支持其他图数据库（如 PostgreSQL + AGE）。

### Q: 可以继续使用旧版吗？
A: 短期可以，但旧版不再维护。建议尽快迁移。

### Q: 旧数据能导入吗？
A: 不能自动导入。需要重新解析代码库。

### Q: 性能如何？
A: 初次解析较慢（需要 AST 解析），但增量更新很快。查询性能取决于 Neo4j 配置。

### Q: Neo4j 占用多少资源？
A: 默认约 512MB-1GB 内存。可以通过配置调整。

### Q: 可以用云端 Neo4j 吗？
A: 可以！修改配置文件中的 `uri` 和认证信息即可。

## 回滚方案

如果新版有问题，可以回滚到旧版：

```bash
# 1. 重命名文件
cd ModelToolbox/ModelMemory/modeltoolbox_memory
mv index.py.old index.py

# 2. 使用旧命令
mtb memory index .
mtb memory search "query"
```

## 支持

如有问题：
1. 查看日志: `mtb memory --help`
2. 检查 Neo4j 状态: 访问 http://localhost:7474
3. 查看配置: `~/.modeltoolbox/state/memory/config.json`

## 总结

迁移虽然需要重新索引，但新版功能更强大，值得投入。主要步骤：

1. ✅ 安装 Neo4j 和 tree-sitter
2. ✅ 配置连接
3. ✅ 运行 `mtb memory init` 和 `mtb memory parse`
4. ✅ 开始使用新功能

**建议**: 在小项目上先测试，确认无误后再迁移大项目。
