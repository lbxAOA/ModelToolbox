# orchestrator/webui — ModelToolbox 总控台（Web）

面向全部 8 个模块的本地 Web 控制面板：一个页面里触发各模块既有 CLI、查看
MCP server 状态、浏览 ObsidianRag 语料、追踪任务日志。风格参考 Claude Desktop
（暖米色背景、衬线标题、圆角卡片、左侧会话式导航）。

## 架构

```
orchestrator/webui/
  server/   Node.js (ESM) + Express + Socket.IO 后端
    src/actions.js      白名单命令模板（每个 action 显式校验参数、拼 argv 数组）
    src/jobRunner.js     spawn 子进程、内存任务表、Socket.IO 实时日志
    src/mcpServers.js    读取 ../../mcp.aggregate.json，管理 MCP server 的启停
    src/paths.js         resolveInRepo() 路径穿越防护 + isSafeToken() 参数校验
    src/routes.js        REST 路由
    src/index.js         Express + Socket.IO 入口，生产模式下顺带托管 client/dist
    scripts/read_ingest_manifest.py   只读 ModelIngest manifest sqlite（stdlib，无第三方依赖）
  client/   React + Vite 前端（Claude Desktop 风格主题见 src/styles/theme.css）
  start.ps1 / start.sh   一键启动脚本
```

## 安全设计

- 后端只通过 `child_process.spawn(command, args)`（argv 数组、`shell:false`）调用
  各模块**既有** CLI，不做任何 `import`，维持 `LICENSES.md` 里 AGPL(ModelTraining) /
  Apache-2.0(ModelOffice) 的许可证隔离约束。
- 所有用户输入的相对路径先经 `resolveInRepo()` 校验，确保解析结果落在仓库根目录内，
  防止路径穿越读写仓库外文件。
- 默认只监听 `127.0.0.1`，不对局域网暴露。
- `pipeline train` / `pipeline serve` 默认 dry-run（只打印将执行的命令），需要用户
  显式勾选“确认真正执行”才会真正跑起来，与 `pipeline` CLI 本身的 `--execute` 语义一致。

## 启动

```powershell
# Windows
.\start.ps1          # 生产模式：npm install(若需要) -> 构建前端 -> 启动后端，单端口 http://127.0.0.1:5678
.\start.ps1 -Dev      # 开发模式：vite dev server(:5173) + node 后端(:5678)，前端热更新
```

```bash
# macOS / Linux
./start.sh            # 生产模式
./start.sh --dev       # 开发模式
```

首次运行前也可手动复制 `server/.env.example` 为 `server/.env` 调整端口 / 监听地址 /
仓库路径 / Python 解释器。

## 已知问题

- `client` 的 `vite`/`esbuild` 存在一个仅影响本地开发服务器（`vite dev`，非生产构建）
  的中等严重度 CORS 问题（[GHSA-67mh-4wv8-2f99](https://github.com/advisories/GHSA-67mh-4wv8-2f99)）。
  由于开发服务器默认只绑定 localhost 且从不加 `--host` 对外暴露，风险很低；修复需升级到
  破坏性的 Vite 8，暂不处理。
