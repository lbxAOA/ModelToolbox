import { Router } from "express";
import fs from "node:fs";
import path from "node:path";
import { execFile } from "node:child_process";
import { MODULES, getModule } from "./modules.js";
import { ACTIONS, buildJobSpec, listActions } from "./actions.js";
import { runJob, listJobs, getJobSummary, getJobLogs, killJob } from "./jobRunner.js";
import * as mcpServers from "./mcpServers.js";
import { REPO_ROOT, PYTHON_BIN, SCRIPTS_DIR } from "./config.js";
import { resolveInRepo } from "./paths.js";

export const router = Router();

// ---------------------------------------------------------------- modules --
router.get("/modules", (_req, res) => {
  res.json(MODULES);
});

router.get("/modules/:id", (req, res) => {
  const mod = getModule(req.params.id);
  if (!mod) return res.status(404).json({ error: "未知模块" });
  res.json(mod);
});

// ---------------------------------------------------------------- actions --
router.get("/actions", (_req, res) => {
  res.json(listActions());
});

// ------------------------------------------------------------------ jobs --
router.post("/jobs", (req, res) => {
  const { actionId, params } = req.body || {};
  if (!ACTIONS[actionId]) return res.status(400).json({ error: `未知 action: ${actionId}` });
  try {
    const spec = buildJobSpec(actionId, params);
    const job = runJob(spec);
    res.status(201).json(job);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.get("/jobs", (_req, res) => {
  res.json(listJobs());
});

router.get("/jobs/:id", (req, res) => {
  const job = getJobSummary(req.params.id);
  if (!job) return res.status(404).json({ error: "任务不存在" });
  res.json(job);
});

router.get("/jobs/:id/logs", (req, res) => {
  const logs = getJobLogs(req.params.id);
  if (logs === null) return res.status(404).json({ error: "任务不存在" });
  res.type("text/plain").send(logs);
});

router.post("/jobs/:id/kill", (req, res) => {
  const ok = killJob(req.params.id);
  res.json({ killed: ok });
});

// ------------------------------------------------------------ mcp servers --
router.get("/mcp-servers", (_req, res) => {
  try {
    res.json(mcpServers.listServers());
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post("/mcp-servers/:name/start", (req, res) => {
  try {
    mcpServers.startServer(req.params.name);
    res.json({ started: true });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.post("/mcp-servers/:name/stop", (req, res) => {
  const ok = mcpServers.stopServer(req.params.name);
  res.json({ stopped: ok });
});

router.get("/mcp-servers/:name/logs", (req, res) => {
  res.type("text/plain").send(mcpServers.getLogs(req.params.name));
});

// -------------------------------------------------------------- ingest ----
router.get("/ingest/manifest", (req, res) => {
  const rel = req.query.path;
  if (typeof rel !== "string") return res.status(400).json({ error: "缺少 path 参数" });
  let manifestPath;
  try {
    manifestPath = resolveInRepo(rel);
  } catch (err) {
    return res.status(400).json({ error: err.message });
  }
  const script = path.join(SCRIPTS_DIR, "read_ingest_manifest.py");
  execFile(PYTHON_BIN, [script, manifestPath], { timeout: 15000 }, (err, stdout, stderr) => {
    if (err) return res.status(500).json({ error: stderr?.toString() || err.message });
    try {
      res.json(JSON.parse(stdout.toString("utf8")));
    } catch {
      res.status(500).json({ error: "解析 manifest 输出失败", raw: stdout.toString("utf8") });
    }
  });
});

// ------------------------------------------------------------ obsidian ----
const MD_EXT = new Set([".md", ".markdown"]);

function buildTree(dirAbs, relBase) {
  const entries = fs.readdirSync(dirAbs, { withFileTypes: true });
  const nodes = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    if (entry.name.startsWith(".")) continue; // 跳过 .obsidian 等隐藏目录
    const relPath = path.posix.join(relBase, entry.name);
    if (entry.isDirectory()) {
      const children = buildTree(path.join(dirAbs, entry.name), relPath);
      if (children.length) nodes.push({ type: "dir", name: entry.name, path: relPath, children });
    } else if (MD_EXT.has(path.extname(entry.name).toLowerCase())) {
      nodes.push({ type: "file", name: entry.name, path: relPath });
    }
  }
  return nodes;
}

router.get("/obsidian/tree", (_req, res) => {
  try {
    const root = resolveInRepo("ObsidianRag");
    res.json(buildTree(root, "ObsidianRag"));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get("/obsidian/note", (req, res) => {
  const rel = req.query.path;
  if (typeof rel !== "string") return res.status(400).json({ error: "缺少 path 参数" });
  let abs;
  try {
    abs = resolveInRepo(rel);
  } catch (err) {
    return res.status(400).json({ error: err.message });
  }
  if (!abs.startsWith(resolveInRepo("ObsidianRag") + path.sep) && abs !== resolveInRepo("ObsidianRag")) {
    return res.status(400).json({ error: "只能读取 ObsidianRag 目录下的文件" });
  }
  if (!MD_EXT.has(path.extname(abs).toLowerCase())) {
    return res.status(400).json({ error: "只能读取 .md 文件" });
  }
  fs.readFile(abs, "utf8", (err, content) => {
    if (err) return res.status(404).json({ error: "文件不存在或不可读" });
    res.json({ path: rel, content });
  });
});

// -------------------------------------------------------------- skills ----
router.get("/skills", (_req, res) => {
  try {
    const p = resolveInRepo("ModelSkill/registry/skills-index.json");
    const raw = fs.readFileSync(p, "utf8");
    res.json(JSON.parse(raw));
  } catch (err) {
    res.status(500).json({ error: `读取技能索引失败：${err.message}` });
  }
});

// ------------------------------------------------------------- meta info --
router.get("/repo-root", (_req, res) => {
  res.json({ repoRoot: REPO_ROOT });
});
