import path from "node:path";
import { REPO_ROOT } from "./config.js";
import { resolveInRepo, isSafeToken } from "./paths.js";

const PROVIDER_ENUM = ["openai", "deepseek", "anthropic", "gemini", "ollama", "claude_code", "codex"];
const ROLE_ENUM = ["teacher", "fallback", "runner"];

function req(cond, msg) {
  if (!cond) throw new Error(msg);
}

/** 路径类参数：必须解析到仓库内，返回绝对路径字符串（供 CLI 直接使用）。 */
function reqPath(value, label) {
  req(typeof value === "string" && value.trim() !== "", `${label} 不能为空`);
  try {
    return resolveInRepo(value);
  } catch (err) {
    throw new Error(`${label} 非法：${err.message}`);
  }
}

function reqUrl(value) {
  req(
    typeof value === "string" && /^https?:\/\/[^\s"'<>]{1,500}$/i.test(value),
    "url 必须是合法的 http(s) 链接"
  );
  return value;
}

function reqEnum(value, allowed, label) {
  req(allowed.includes(value), `${label} 必须是 ${allowed.join("/")} 之一`);
  return value;
}

/**
 * 每个 action 是一个白名单命令模板：module（归属哪个 ModelToolbox 模块）、
 * label（UI 展示名）、command/cwd（固定，不受用户输入影响）、build(params)（校验
 * 并拼出 argv 数组，spawn 时不经过 shell，从根源上避免 shell 注入）。
 */
export const ACTIONS = {
  "ingest.crawl": {
    module: "model-ingest",
    label: "抓取网页（crawl）",
    cwd: "ModelIngest",
    command: "modelingest",
    build(p) {
      const url = reqUrl(p.url);
      const output = reqPath(p.output, "output");
      const args = ["crawl", "--url", url, "--output", output];
      const depth = Math.max(0, Math.min(5, Number(p.depth) || 0));
      args.push("--depth", String(depth));
      if (p.ignoreRobots) args.push("--ignore-robots");
      if (p.overwrite) args.push("--overwrite");
      return args;
    },
  },
  "ingest.run": {
    module: "model-ingest",
    label: "清洗转换（run）",
    cwd: "ModelIngest",
    command: "modelingest",
    build(p) {
      const source = reqPath(p.source, "source");
      const output = reqPath(p.output, "output");
      const args = ["run", "--source", source, "--output", output];
      if (p.overwrite) args.push("--overwrite");
      if (p.noPdfPages) args.push("--no-pdf-pages");
      if (p.noHtmlClean) args.push("--no-html-clean");
      if (p.noInjectionScan) args.push("--no-injection-scan");
      if (p.noQualityFilter) args.push("--no-quality-filter");
      if (p.noDedup) args.push("--no-dedup");
      return args;
    },
  },
  "ingest.status": {
    module: "model-ingest",
    label: "查看状态（status）",
    cwd: "ModelIngest",
    command: "modelingest",
    build(p) {
      const source = reqPath(p.source, "source");
      const output = reqPath(p.output, "output");
      return ["status", "--source", source, "--output", output];
    },
  },
  "ingest.clean": {
    module: "model-ingest",
    label: "清理失效记录（clean）",
    cwd: "ModelIngest",
    command: "modelingest",
    build(p) {
      const source = reqPath(p.source, "source");
      const output = reqPath(p.output, "output");
      return ["clean", "--source", source, "--output", output];
    },
  },
  "ingest.distill": {
    module: "model-ingest",
    label: "蒸馏知识库（distill）",
    cwd: "ModelIngest",
    command: "modelingest",
    build(p) {
      const source = reqPath(p.source, "source");
      const output = reqPath(p.output, "output");
      const args = ["distill", "--source", source, "--output", output];
      if (p.profile) args.push("--profile", reqEnum(p.profile, ["concept", "algorithm"], "profile"));
      if (p.overwrite) args.push("--overwrite");
      if (p.noLink) args.push("--no-link");
      return args;
    },
  },
  "provider.list": {
    module: "model-provider",
    label: "查看 provider / 角色状态",
    cwd: "ModelProvider",
    command: "modelprovider",
    build() {
      return ["list"];
    },
  },
  "provider.ask": {
    module: "model-provider",
    label: "对话（ask）",
    cwd: "ModelProvider",
    command: "modelprovider",
    build(p) {
      req(
        typeof p.prompt === "string" && p.prompt.trim().length > 0 && p.prompt.length < 8000,
        "prompt 不能为空且需小于 8000 字符"
      );
      const args = ["ask", p.prompt];
      if (p.provider) args.push("--provider", reqEnum(p.provider, PROVIDER_ENUM, "provider"));
      if (p.role) args.push("--role", reqEnum(p.role, ROLE_ENUM, "role"));
      return args;
    },
  },
  "pipeline.datagen": {
    module: "pipeline",
    label: "阶段0：合成训练数据（datagen）",
    cwd: "pipeline",
    command: "pipeline",
    build(p) {
      const corpus = reqPath(p.corpus, "corpus");
      const out = reqPath(p.out, "out");
      const args = ["datagen", "--corpus", corpus, "--out", out];
      if (p.limit) {
        const limit = Math.max(1, Math.min(10000, Number(p.limit) || 5));
        args.push("--limit", String(limit));
      }
      if (p.perChunk) {
        const perChunk = Math.max(1, Math.min(20, Number(p.perChunk) || 3));
        args.push("--per-chunk", String(perChunk));
      }
      if (p.role) args.push("--role", reqEnum(p.role, ROLE_ENUM, "role"));
      return args;
    },
  },
  "pipeline.train": {
    module: "pipeline",
    label: "阶段1：视觉微调（train，AGPL 子进程）",
    cwd: "pipeline",
    command: "pipeline",
    build(p) {
      const config = reqPath(p.config, "config");
      const args = ["train", "--config", config];
      // 默认 dry-run（不加 --execute），必须显式确认才真正执行训练。
      if (p.execute === true) args.push("--execute");
      return args;
    },
  },
  "pipeline.serve": {
    module: "pipeline",
    label: "阶段2：Ollama 承载（serve）",
    cwd: "pipeline",
    command: "pipeline",
    build(p) {
      const gguf = reqPath(p.gguf, "gguf");
      const args = ["serve", "--gguf", gguf];
      if (p.name) {
        req(isSafeToken(p.name, /^[\w.-]{1,100}$/), "name 只能包含字母数字 . _ -");
        args.push("--name", p.name);
      }
      if (p.mmproj) args.push("--mmproj", reqPath(p.mmproj, "mmproj"));
      if (p.execute === true) args.push("--execute");
      return args;
    },
  },
  "memory.status": {
    module: "model-memory",
    label: "查看状态（status）",
    cwd: "ModelMemory",
    command: "code-review-graph",
    build() {
      return ["status"];
    },
  },
  "memory.repos": {
    module: "model-memory",
    label: "查看已注册仓库（repos）",
    cwd: "ModelMemory",
    command: "code-review-graph",
    build() {
      return ["repos"];
    },
  },
  "memory.build": {
    module: "model-memory",
    label: "完整重建知识图谱（build，重新解析所有文件）",
    cwd: "ModelMemory",
    command: "code-review-graph",
    build() {
      return ["build"];
    },
  },
  "memory.detectChanges": {
    module: "model-memory",
    label: "检测变更影响（detect-changes）",
    cwd: "ModelMemory",
    command: "code-review-graph",
    build(p) {
      const args = ["detect-changes", "--brief"];
      if (p.base) {
        req(isSafeToken(p.base, /^[\w./-]{1,200}$/), "base 非法");
        args.push("--base", p.base);
      }
      return args;
    },
  },
};

export function buildJobSpec(actionId, params = {}) {
  const action = ACTIONS[actionId];
  if (!action) throw new Error(`未知 action: ${actionId}`);
  const args = action.build(params || {});
  const cwd = action.cwd ? path.join(REPO_ROOT, action.cwd) : REPO_ROOT;
  return { label: action.label, command: action.command, args, cwd, module: action.module, actionId };
}

export function listActions() {
  return Object.entries(ACTIONS).map(([id, a]) => ({
    id,
    module: a.module,
    label: a.label,
    command: a.command,
    cwd: a.cwd,
  }));
}
