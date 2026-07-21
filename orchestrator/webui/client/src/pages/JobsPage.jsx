import { useEffect, useState } from "react";
import { api } from "../api.js";
import TopBar from "../components/TopBar.jsx";
import Card from "../components/Card.jsx";
import StatusPill from "../components/StatusPill.jsx";
import JobConsole from "../components/JobConsole.jsx";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState(null);

  const refresh = () => {
    api.getJobs().then(setJobs).catch((err) => setError(err.message));
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <TopBar title="任务历史" subtitle="所有通过总控台触发的 CLI 任务（内存记录，重启后清空）" />
      <div className="content" style={{ display: "flex", gap: 16 }}>
        <Card title="任务列表">
          {error && <div className="muted">{error}</div>}
          <table className="table" style={{ minWidth: 380 }}>
            <thead>
              <tr>
                <th>模块</th>
                <th>任务</th>
                <th>状态</th>
                <th>开始时间</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id} style={{ cursor: "pointer" }} onClick={() => setSelected(j)}>
                  <td>{j.module}</td>
                  <td>{j.label}</td>
                  <td>
                    <StatusPill status={j.status} />
                  </td>
                  <td className="muted">{new Date(j.startedAt).toLocaleString()}</td>
                </tr>
              ))}
              {jobs.length === 0 && (
                <tr>
                  <td colSpan={4} className="muted">
                    暂无任务
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </Card>
        <Card title={selected ? `${selected.module} / ${selected.label}` : "选择左侧任务查看日志"}>
          <div style={{ minWidth: 420 }}>
            {selected ? <JobConsole job={selected} /> : <div className="muted">尚未选择任务</div>}
          </div>
        </Card>
      </div>
    </>
  );
}
