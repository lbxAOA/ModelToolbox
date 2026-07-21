import TopBar from "../components/TopBar.jsx";
import ActionForm from "../components/ActionForm.jsx";
import Card from "../components/Card.jsx";

export default function PipelinePage() {
  return (
    <>
      <TopBar title="Pipeline 管线" subtitle="四阶段管线胶水层：阶段0 datagen → 阶段1 train（AGPL 子进程）→ 阶段2 serve" />
      <div className="content">
        <ActionForm actionId="pipeline.datagen" title="阶段0：合成训练数据（datagen）" />
        <Card title="阶段1：视觉微调（train）">
          <p className="muted">
            train 会以子进程方式调用 ModelTraining（AGPL-3.0），本控制台不会 import 其代码，仅通过 CLI 参数转发。
            默认 dry-run，只打印将要执行的命令；勾选“确认真正执行训练”后才会真正启动微调。
          </p>
        </Card>
        <ActionForm actionId="pipeline.train" title="" />
        <ActionForm actionId="pipeline.serve" title="阶段2：Ollama 承载（serve）" />
      </div>
    </>
  );
}
