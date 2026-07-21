import TopBar from "../components/TopBar.jsx";
import Card from "../components/Card.jsx";

export default function ModelOfficePage() {
  return (
    <>
      <TopBar title="ModelOffice" subtitle="代码执行 / 沙箱（e2b 派生，Apache-2.0）" />
      <div className="content">
        <Card title="规划中">
          <p className="muted">
            ModelOffice 计划封装为 <code>sandbox-mcp</code>，通过 MCP 协议对外提供代码执行能力，
            届时会出现在「ModelMCP」页面的 server 列表中（对应 <code>mcp.aggregate.json</code> 里
            <code>enabled: false, planned: true</code> 的 <code>sandbox</code> 条目）。目前本控制台尚未
            提供直接操作入口。
          </p>
        </Card>
      </div>
    </>
  );
}
