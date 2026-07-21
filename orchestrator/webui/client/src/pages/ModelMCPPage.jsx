import { useEffect, useState } from "react";
import { api } from "../api.js";
import { socket } from "../socket.js";
import TopBar from "../components/TopBar.jsx";
import Card from "../components/Card.jsx";
import StatusPill from "../components/StatusPill.jsx";

export default function ModelMCPPage() {
  const [servers, setServers] = useState([]);
  const [error, setError] = useState(null);
  const [logsByName, setLogsByName] = useState({});
  const [expanded, setExpanded] = useState(null);

  const refresh = () => {
    api.getMcpServers().then(setServers).catch((err) => setError(err.message));
  };

  useEffect(() => {
    refresh();
    const onLog = ({ name, chunk }) => {
      setLogsByName((prev) => ({ ...prev, [name]: (prev[name] || "") + chunk }));
    };
    const onStopped = () => refresh();
    socket.on("mcp:log", onLog);
    socket.on("mcp:stopped", onStopped);
    const interval = setInterval(refresh, 4000);
    return () => {
      socket.off("mcp:log", onLog);
      socket.off("mcp:stopped", onStopped);
      clearInterval(interval);
    };
  }, []);

  const handleStart = async (name) => {
    setError(null);
    try {
      await api.startMcpServer(name);
      socket.emit("mcp:subscribe", name);
      setExpanded(name);
      refresh();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleStop = async (name) => {
    await api.stopMcpServer(name);
    refresh();
  };

  return (
    <>
      <TopBar title="ModelMCP" subtitle="领域工具 MCP server：altium / ltspice / obsidian-rag / ach-roundtable / code-review-graph" />
      <div className="content">
        {error && <Card>{error}</Card>}
        {servers.map((s) => (
          <Card
            key={s.name}
            title={s.name}
            right={<StatusPill status={s.status} />}
          >
            <div className="muted" style={{ marginBottom: 8 }}>
              {s.description || "（无描述）"} {s.module && <span className="badge">{s.module}</span>}
            </div>
            {!s.enabled && <div className="muted">尚未启用（enabled=false，规划中）</div>}
            {s.command && (
              <div className="muted" style={{ fontFamily: "var(--font-mono)", fontSize: 12, marginBottom: 8 }}>
                {s.command} {s.args?.join(" ")} {s.cwd && `（cwd: ${s.cwd}）`}
              </div>
            )}
            <div style={{ display: "flex", gap: 8 }}>
              {s.status === "running" ? (
                <button className="btn btn-danger" onClick={() => handleStop(s.name)}>
                  停止
                </button>
              ) : (
                <button className="btn" disabled={!s.invocable} onClick={() => handleStart(s.name)}>
                  启动
                </button>
              )}
              <button className="btn btn-secondary" onClick={() => setExpanded(expanded === s.name ? null : s.name)}>
                {expanded === s.name ? "收起日志" : "查看日志"}
              </button>
            </div>
            {expanded === s.name && (
              <div className="console" style={{ marginTop: 10, height: 180 }}>
                {logsByName[s.name] || "（暂无输出）"}
              </div>
            )}
          </Card>
        ))}
      </div>
    </>
  );
}
