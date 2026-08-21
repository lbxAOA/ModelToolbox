# MCP 与 Skills 管理

终端客户端通过本地 Bridge 管理受信任 MCP、Skills 和市场缓存。

- `Integrations` 展示目标客户端的契约状态：只有 Claude Code 当前可写；Cursor、VS Code、Windsurf、Codex 仍是检查/导出模式。
- `Marketplace` 默认离线，仅展示已验证的本地缓存。未来在线刷新和下载需要用户显式启用，并且只有受信任来源才可一键安装。
- MCP 本地进程的启动、停止和健康状态属于运行时 Bridge 会话；所有启动均需确认，且不会记录环境变量值、令牌或 MCP 协议内容。
- Skills 被视为不受信任的指令内容；安装不会执行 Skill 脚本。

常用 CLI：

```text
mtb integrations-list
mtb mcp-list
mtb mcp-start <mcp-id> --confirm
mtb marketplace-status
mtb marketplace-search --query <keyword>
mtb marketplace-recommendations
```
