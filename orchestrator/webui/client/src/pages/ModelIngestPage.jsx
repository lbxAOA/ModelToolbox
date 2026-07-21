import TopBar from "../components/TopBar.jsx";
import ActionForm from "../components/ActionForm.jsx";
import SourceDiscoverPanel from "../components/SourceDiscoverPanel.jsx";
import DistillPanel from "../components/DistillPanel.jsx";

export default function ModelIngestPage() {
  return (
    <>
      <TopBar
        title="ModelIngest"
        subtitle="网址/本地目录 + 清洗原始数据 → md → 蒸馏知识库 → 自动生成检索技能（阶段 A / B）"
      />
      <div className="content">
        <SourceDiscoverPanel />
        <DistillPanel />
        <ActionForm actionId="ingest.distillLink" title="高级：重建关联（distill-link，仅重建 wikilink + MOC）" />
        <ActionForm actionId="ingest.status" title="查看状态（status）" />
        <ActionForm actionId="ingest.clean" title="清理失效记录（clean）" />
      </div>
    </>
  );
}
