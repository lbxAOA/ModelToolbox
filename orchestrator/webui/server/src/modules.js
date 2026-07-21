/**
 * 8 个模块的静态元信息（名称/说明/许可证徽章），供 Dashboard 与各模块页展示。
 * 许可证信息见仓库根 LICENSES.md：ModelTraining 为 AGPL-3.0（仅可子进程调用），
 * ModelOffice 派生自 e2b（Apache-2.0），其余为 MIT。
 */
export const MODULES = [
  {
    id: "model-ingest",
    name: "ModelIngest",
    tagline: "爬取 + 清洗原始数据 → 干净 md → 蒸馏知识库",
    license: "MIT",
    path: "ModelIngest",
    stage: "阶段 A / B",
  },
  {
    id: "model-provider",
    name: "ModelProvider",
    tagline: "统一大模型调用层（闭源旗舰 + 本地 Ollama + CLI Agent）",
    license: "MIT",
    path: "ModelProvider",
    stage: "全阶段",
  },
  {
    id: "model-training",
    name: "ModelTraining",
    tagline: "unsloth 微调私有视觉模型 → 导出 GGUF",
    license: "AGPL-3.0",
    path: "ModelTraining",
    stage: "阶段1",
  },
  {
    id: "pipeline",
    name: "pipeline",
    tagline: "四阶段管线胶水层：datagen / train(子进程) / serve",
    license: "MIT",
    path: "pipeline",
    stage: "阶段0-2",
  },
  {
    id: "model-mcp",
    name: "ModelMCP",
    tagline: "领域工具 MCP server（altium / ltspice / rag / ach）",
    license: "MIT / 各子服务器独立",
    path: "ModelMCP",
    stage: "调用",
  },
  {
    id: "model-memory",
    name: "ModelMemory",
    tagline: "代码知识图谱 + 变更影响分析",
    license: "MIT（含第三方组件，见 LICENSES.md）",
    path: "ModelMemory",
    stage: "调用",
  },
  {
    id: "model-office",
    name: "ModelOffice",
    tagline: "代码执行 / 沙箱（e2b 派生，sandbox-mcp 规划中）",
    license: "Apache-2.0",
    path: "ModelOffice",
    stage: "规划中",
  },
  {
    id: "model-skill",
    name: "ModelSkill",
    tagline: "技能注册与路由（registry + hooks）",
    license: "MIT",
    path: "ModelSkill",
    stage: "调用",
  },
  {
    id: "obsidian-rag",
    name: "ObsidianRag",
    tagline: "知识库语料（原件不入库，检索兜底）",
    license: "用户内容",
    path: "ObsidianRag",
    stage: "语料",
  },
];

export function getModule(id) {
  return MODULES.find((m) => m.id === id) ?? null;
}
