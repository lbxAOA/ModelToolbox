import { Link } from "react-router-dom";
import TopBar from "../components/TopBar.jsx";
import Card from "../components/Card.jsx";

export default function ModelTrainingPage() {
  return (
    <>
      <TopBar title="ModelTraining" subtitle="unsloth 微调私有视觉模型 → 导出 GGUF（AGPL-3.0）" />
      <div className="content">
        <Card title="许可证隔离说明">
          <p className="muted">
            ModelTraining 采用 AGPL-3.0 许可证。根据仓库 <code>LICENSES.md</code> 的硬约束，本控制台
            <b>不会 import</b> 其任何代码，只能通过 CLI / 子进程调用。实际的训练动作已归并到「Pipeline 管线」
            页面的「阶段1：train」表单中，由 <code>pipeline train</code> 以子进程方式转发给
            <code>ModelTraining/unsloth-cli.py</code>。
          </p>
          <Link className="btn" to="/pipeline">
            前往 Pipeline 管线执行训练
          </Link>
        </Card>
      </div>
    </>
  );
}
