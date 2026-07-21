import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// server/src -> server -> webui -> orchestrator -> ModelToolbox（仓库根）
const DEFAULT_REPO_ROOT = path.resolve(__dirname, "../../../..");

export const REPO_ROOT = process.env.MODELTOOLBOX_ROOT
  ? path.resolve(process.env.MODELTOOLBOX_ROOT)
  : DEFAULT_REPO_ROOT;

export const MCP_AGGREGATE_PATH = path.join(REPO_ROOT, "orchestrator", "mcp.aggregate.json");

export const PORT = Number(process.env.PORT || 5678);
export const HOST = process.env.HOST || "127.0.0.1"; // 默认只监听本机，避免误对局域网暴露

export const PYTHON_BIN = process.env.PYTHON_BIN || (process.platform === "win32" ? "python" : "python3");

export const SCRIPTS_DIR = path.join(__dirname, "..", "scripts");
