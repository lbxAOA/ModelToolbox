import { useEffect, useRef, useState } from "react";
import { socket } from "../socket.js";
import { api } from "../api.js";
import StatusPill from "./StatusPill.jsx";

export default function JobConsole({ job, onKilled }) {
  const [logText, setLogText] = useState("");
  const [status, setStatus] = useState(job?.status ?? "running");
  const boxRef = useRef(null);

  useEffect(() => {
    if (!job) return;
    let cancelled = false;
    setLogText("");
    setStatus(job.status);

    api
      .getJobLogs(job.id)
      .then((text) => {
        if (!cancelled) setLogText(text);
      })
      .catch(() => {});

    socket.emit("job:subscribe", job.id);

    const onLog = (payload) => {
      if (payload.id !== job.id) return;
      setLogText((prev) => prev + payload.chunk);
    };
    const onDone = (payload) => {
      if (payload.id !== job.id) return;
      setStatus(payload.status);
    };
    socket.on("job:log", onLog);
    socket.on("job:done", onDone);
    return () => {
      cancelled = true;
      socket.off("job:log", onLog);
      socket.off("job:done", onDone);
    };
  }, [job?.id]);

  useEffect(() => {
    if (boxRef.current) boxRef.current.scrollTop = boxRef.current.scrollHeight;
  }, [logText]);

  if (!job) return null;

  const handleKill = async () => {
    await api.killJob(job.id);
    onKilled?.();
  };

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
        <StatusPill status={status} />
        <span className="muted">
          {job.command} {job.args?.join(" ")}
        </span>
        {status === "running" && (
          <button className="btn btn-danger" style={{ marginLeft: "auto" }} onClick={handleKill}>
            终止
          </button>
        )}
      </div>
      <div className="console" ref={boxRef}>
        {logText || "（暂无输出）"}
      </div>
    </div>
  );
}
