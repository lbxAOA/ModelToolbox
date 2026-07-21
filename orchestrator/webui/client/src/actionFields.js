// 与 server/src/actions.js 中的 build(params) 一一对应的表单字段描述。
export const ACTION_FIELDS = {
  "ingest.crawl": [
    { name: "url", label: "URL", type: "text", placeholder: "https://example.com", required: true },
    { name: "output", label: "输出目录（仓库内相对路径）", type: "text", placeholder: "ObsidianRag/_crawled", required: true },
    { name: "depth", label: "抓取深度", type: "number", default: 1 },
    { name: "ignoreRobots", label: "忽略 robots.txt", type: "checkbox" },
    { name: "overwrite", label: "覆盖已存在文件", type: "checkbox" },
  ],
  "ingest.run": [
    { name: "source", label: "源目录", type: "text", placeholder: "ObsidianRag", required: true },
    { name: "output", label: "输出目录", type: "text", placeholder: "ObsidianRag_md", required: true },
    { name: "overwrite", label: "覆盖已存在文件", type: "checkbox" },
    { name: "noPdfPages", label: "跳过 PDF 分页", type: "checkbox" },
    { name: "noHtmlClean", label: "关闭 HTML 去噪", type: "checkbox" },
    { name: "noInjectionScan", label: "关闭 Prompt 注入检测", type: "checkbox" },
    { name: "noQualityFilter", label: "关闭质量过滤", type: "checkbox" },
    { name: "noDedup", label: "关闭近似去重", type: "checkbox" },
  ],
  "ingest.status": [
    { name: "source", label: "源目录", type: "text", required: true },
    { name: "output", label: "输出目录", type: "text", required: true },
  ],
  "ingest.clean": [
    { name: "source", label: "源目录", type: "text", required: true },
    { name: "output", label: "输出目录", type: "text", required: true },
  ],
  "ingest.distill": [
    { name: "source", label: "md 源目录", type: "text", required: true },
    { name: "output", label: "输出目录", type: "text", required: true },
    { name: "profile", label: "蒸馏 profile", type: "select", options: ["", "concept", "algorithm"] },
    { name: "overwrite", label: "覆盖已存在文件", type: "checkbox" },
    { name: "noLink", label: "跳过关联链接", type: "checkbox" },
  ],
  "provider.list": [],
  "provider.ask": [
    { name: "prompt", label: "Prompt", type: "textarea", required: true },
    {
      name: "provider",
      label: "provider",
      type: "select",
      options: ["", "openai", "deepseek", "anthropic", "gemini", "ollama", "claude_code", "codex"],
    },
    { name: "role", label: "role", type: "select", options: ["", "teacher", "fallback", "runner"] },
  ],
  "pipeline.datagen": [
    { name: "corpus", label: "语料目录（ModelIngest 产物）", type: "text", required: true },
    { name: "out", label: "输出 jsonl 路径", type: "text", placeholder: "pipeline/out/train.jsonl", required: true },
    { name: "limit", label: "限制文件数（试运行，可选）", type: "number" },
    { name: "perChunk", label: "每块样本数（默认 3）", type: "number" },
    { name: "role", label: "role", type: "select", options: ["", "teacher", "fallback", "runner"] },
  ],
  "pipeline.train": [
    { name: "config", label: "训练配置文件", type: "text", required: true },
    { name: "execute", label: "确认真正执行训练（否则仅 dry-run 打印命令）", type: "checkbox" },
  ],
  "pipeline.serve": [
    { name: "gguf", label: "GGUF 模型路径", type: "text", required: true },
    { name: "name", label: "Ollama 模型名（默认 modeltoolbox-private）", type: "text" },
    { name: "mmproj", label: "mmproj 路径（可选，视觉模型需要）", type: "text" },
    { name: "execute", label: "确认真正执行（否则仅 dry-run 打印命令）", type: "checkbox" },
  ],
  "memory.status": [],
  "memory.repos": [],
  "memory.build": [],
  "memory.detectChanges": [{ name: "base", label: "对比基线（可选，如 main）", type: "text" }],
};
