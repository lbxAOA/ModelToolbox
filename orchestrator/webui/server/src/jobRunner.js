import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";

const jobs = new Map(); // id -> job record（含不可序列化的 process 引用）
const MAX_LOG_CHUNKS = 5000;
let io = null;

export function attachIo(socketIoInstance) {
  io = socketIoInstance;
}

function toSummary(job) {
  const { process: _proc, logs: _logs, ...rest } = job;
  return rest;
}

export function listJobs() {
  return [...jobs.values()].sort((a, b) => b.startedAt - a.startedAt).map(toSummary);
}

export function getJobSummary(id) {
  const job = jobs.get(id);
  return job ? toSummary(job) : null;
}

export function getJobLogs(id) {
  const job = jobs.get(id);
  return job ? job.logs.join("") : null;
}

/**
 * 执行一个白名单命令（不经过 shell，argv 数组直接传给 spawn，避免 shell 注入）。
 * 返回 job 摘要；实时输出通过 socket.io 房间 `job:<id>` 广播。
 */
export function runJob({ label, module, command, args, cwd }) {
  const id = randomUUID();
  const job = {
    id,
    label,
    module,
    command,
    args,
    cwd,
    status: "running",
    startedAt: Date.now(),
    endedAt: null,
    exitCode: null,
    logs: [],
    process: null,
  };
  jobs.set(id, job);

  const emitLog = (chunk) => {
    const text = chunk.toString("utf8");
    job.logs.push(text);
    if (job.logs.length > MAX_LOG_CHUNKS) job.logs.shift();
    io?.to(`job:${id}`).emit("job:log", { id, chunk: text });
  };

  let child;
  try {
    child = spawn(command, args, { cwd, shell: false, windowsHide: true });
  } catch (err) {
    job.status = "failed";
    job.endedAt = Date.now();
    emitLog(`[spawn-error] ${err.message}\n`);
    return toSummary(job);
  }

  job.process = child;

  child.stdout?.on("data", emitLog);
  child.stderr?.on("data", emitLog);
  child.on("error", (err) => {
    job.status = "failed";
    job.endedAt = Date.now();
    emitLog(`[process-error] ${err.message}\n`);
    io?.to(`job:${id}`).emit("job:done", toSummary(job));
  });
  child.on("close", (code) => {
    job.exitCode = code;
    job.status = code === 0 ? "success" : "failed";
    job.endedAt = Date.now();
    io?.to(`job:${id}`).emit("job:done", toSummary(job));
  });

  return toSummary(job);
}

export function killJob(id) {
  const job = jobs.get(id);
  if (!job || job.status !== "running" || !job.process) return false;
  job.process.kill();
  return true;
}
