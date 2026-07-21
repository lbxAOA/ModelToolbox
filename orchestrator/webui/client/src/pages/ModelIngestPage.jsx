import TopBar from "../components/TopBar.jsx";
import ActionForm from "../components/ActionForm.jsx";

export default function ModelIngestPage() {
  return (
    <>
      <TopBar title="ModelIngest" subtitle="爬取 + 清洗原始数据 → md → 蒸馏知识库（阶段 A / B）" />
      <div className="content">
        <ActionForm actionId="ingest.crawl" title="抓取网页（crawl）" />
        <ActionForm actionId="ingest.run" title="清洗转换（run）" />
        <ActionForm actionId="ingest.status" title="查看状态（status）" />
        <ActionForm actionId="ingest.clean" title="清理失效记录（clean）" />
        <ActionForm actionId="ingest.distill" title="蒸馏知识库（distill）" />
      </div>
    </>
  );
}
