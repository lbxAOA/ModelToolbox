export default function StatusPill({ status }) {
  const label = { running: "运行中", success: "成功", failed: "失败", stopped: "已停止" }[status] || status;
  return <span className={`status-pill ${status}`}>{label}</span>;
}
