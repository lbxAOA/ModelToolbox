import express from "express";
import http from "node:http";
import path from "node:path";
import fs from "node:fs";
import { Server as SocketIOServer } from "socket.io";
import { fileURLToPath } from "node:url";

import { HOST, PORT, REPO_ROOT } from "./config.js";
import { router } from "./routes.js";
import * as jobRunner from "./jobRunner.js";
import * as mcpServers from "./mcpServers.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CLIENT_DIST = path.resolve(__dirname, "..", "..", "client", "dist");

const app = express();
app.use(express.json({ limit: "1mb" }));

// 仅在本地开发（Vite dev server 跑在 5173）时放行跨域，生产模式由本服务器
// 直接托管前端静态文件，不需要 CORS。
const DEV_ORIGINS = new Set(["http://localhost:5173", "http://127.0.0.1:5173"]);
app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (origin && DEV_ORIGINS.has(origin)) {
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  }
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

app.use("/api", router);

if (fs.existsSync(CLIENT_DIST)) {
  app.use(express.static(CLIENT_DIST));
  app.get("*", (req, res, next) => {
    if (req.path.startsWith("/api")) return next();
    res.sendFile(path.join(CLIENT_DIST, "index.html"));
  });
} else {
  app.get("/", (_req, res) => {
    res
      .status(200)
      .type("text/plain")
      .send(
        "前端尚未构建。请先运行：cd orchestrator/webui/client && npm install && npm run build\n" +
          "或使用仓库根 orchestrator/webui/start.ps1 / start.sh 一键启动。"
      );
  });
}

const server = http.createServer(app);
const io = new SocketIOServer(server, { cors: { origin: [...DEV_ORIGINS] } });

jobRunner.attachIo(io);
mcpServers.attachIo(io);

io.on("connection", (socket) => {
  socket.on("job:subscribe", (id) => socket.join(`job:${id}`));
  socket.on("mcp:subscribe", (name) => socket.join(`mcp:${name}`));
});

server.listen(PORT, HOST, () => {
  console.log(`ModelToolbox 总控台已启动：http://${HOST}:${PORT}`);
  console.log(`仓库根目录：${REPO_ROOT}`);
});
