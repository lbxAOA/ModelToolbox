import TopBar from "../components/TopBar.jsx";
import ActionForm from "../components/ActionForm.jsx";

export default function ModelMemoryPage() {
  return (
    <>
      <TopBar title="ModelMemory" subtitle="代码知识图谱 + 变更影响分析（code-review-graph）" />
      <div className="content">
        <ActionForm actionId="memory.status" title="查看状态（status）" />
        <ActionForm actionId="memory.repos" title="查看已注册仓库（repos）" />
        <ActionForm actionId="memory.build" title="完整重建知识图谱（build）" />
        <ActionForm actionId="memory.detectChanges" title="检测变更影响（detect-changes）" />
      </div>
    </>
  );
}
