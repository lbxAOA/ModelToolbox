import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { MCP_AGGREGATE_PATH, REPO_ROOT } from "./config.js";

let io = null;
export function attachIo(socketIoInstance) {
  io = socketIoInstance;
}

const running = new Map(); // name -> { process, startedAt, logs: [] }
const MAX_LOG_CHUNKS = 2000;

export function loadServerDefs() {
  const raw = fs.readFileSync(MCP_AGGREGATE_PATH, "utf8");
  const json = JSON.parse(raw);
  return json.mcpServers || {};
}

export function listServers() {
  const defs = loadServerDefs();
  return Object.entries(defs).map(([name, def]) => {
    const live = running.get(name);
    return {
      name,
      module: def.module,
      description: def.description,
      enabled: !!def.enabled,
      planned: !!def.planned,
      invocable: Boolean(def.enabled && def.command && def.args),
      command: def.command ?? null,
      args: def.args ?? null,
      cwd: def.cwd ?? null,
      status: live ? "running" : "stopped",
      startedAt: live?.startedAt ?? null,
    };
  });
}

export function startServer(name) {
  const defs = loadServerDefs();
  const def = defs[name];
  if (!def) throw new Error(`未知 MCP server: ${name}`);
  if (!def.enabled) throw new Error(`${name} 尚未实现（enabled=false，规划中）`);
  if (!def.command || !def.args) throw new Error(`${name} 没有可执行的 command/args 配置`);
  if (running.has(name)) return running.get(name);

  const cwd = def.cwd ? path.join(REPO_ROOT, def.cwd) : REPO_ROOT;
  const child = spawn(def.command, def.args, { cwd, shell: false, windowsHide: true });
  const entry = { process: child, startedAt: Date.now(), logs: [] };
  running.set(name, entry);

  const emit = (chunk) => {
    const text = chunk.toString("utf8");
    entry.logs.push(text);
    if (entry.logs.length > MAX_LOG_CHUNKS) entry.logs.shift();
    io?.to(`mcp:${name}`).emit("mcp:log", { name, chunk: text });
  };
  child.stdout?.on("data", emit);
  child.stderr?.on("data", emit);
  child.on("close", (code) => {
    running.delete(name);
    io?.to(`mcp:${name}`).emit("mcp:stopped", { name, code });
  });
  child.on("error", (err) => {
    emit(`[process-error] ${err.message}\n`);
    running.delete(name);
    io?.to(`mcp:${name}`).emit("mcp:stopped", { name, code: -1 });
  });

  return entry;
}

export function stopServer(name) {
  const entry = running.get(name);
  if (!entry) return false;
  entry.process.kill();
  running.delete(name);
  return true;
}

export function getLogs(name) {
  return running.get(name)?.logs.join("") ?? "";
}
