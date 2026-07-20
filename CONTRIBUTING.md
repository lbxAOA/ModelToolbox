# 贡献指南 (Contributing)

感谢参与 ModelToolbox。本文档约定工程规范，确保多模块协作一致。

## 仓库结构

```
ModelToolbox/
├── ModelIngest/     文档 → md 语料（保留本地原件）
├── ModelProvider/   闭源大模型统一接口
├── ModelTraining/   小样本多模态微调（AGPL, unsloth 派生）
├── ModelMCP/        硬件等 MCP server
├── ModelMemory/     记忆 + 代码知识图谱
├── ModelSkill/      私有 Skill registry
├── ModelOffice/     执行 / 沙箱（Apache, e2b 派生）
├── ObsidianRag/     知识库语料
├── orchestrator/    顶层编排（MCP 聚合 / persona / bootstrap）
└── docs/            架构文档
```

## 硬性规则

1. **不提交原始文档与大文件**：PDF / Word / Excel / 模型权重（`*.gguf`/`*.safetensors`）
   等一律由 `.gitignore` 排除，只提交转换后的 `*.md` 与代码。
2. **不提交密钥**：API key 走 `.env`（已忽略），仓库内仅保留 `.env.example`。
3. **不提交虚拟环境 / 依赖目录**：`.venv/`、`node_modules/`、`__pycache__/`。
4. **许可证边界**：跨模块调用走 MCP / CLI / API，避免直接 `import` 造成 license 耦合
   （尤其不要 `import` ModelTraining 的 AGPL 代码到 MIT 模块）。
5. **命名规范**：新模块沿用 `Model*` 前缀；不要重命名上游开源库的内部包名与版权。

## 提交规范

采用 Conventional Commits：

```
feat(ingest): 新增 xlsx 转 md 表格支持
fix(provider): 修复 Anthropic 超时重试
docs: 更新架构图
chore(repo): 清理误跟踪的 .venv
```

- 每次提交聚焦单一模块 / 单一关注点。
- 分支：`feat/*`、`fix/*`、`agents/*`；通过 PR 合入 `main`。

## 本地校验

提交前请确认：

- [ ] 无原始文档 / 权重 / 密钥被加入暂存区（`git status` 核对）
- [ ] 改动限定在目标模块，未触碰上游库内部与版权头
- [ ] README / docs 与改动同步
