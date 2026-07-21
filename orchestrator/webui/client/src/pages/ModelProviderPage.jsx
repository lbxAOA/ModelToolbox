import TopBar from "../components/TopBar.jsx";
import ActionForm from "../components/ActionForm.jsx";

export default function ModelProviderPage() {
  return (
    <>
      <TopBar title="ModelProvider" subtitle="统一大模型调用层：闭源旗舰 + 本地 Ollama + CLI Agent" />
      <div className="content">
        <ActionForm actionId="provider.list" title="查看 provider / 角色状态（list）" />
        <ActionForm actionId="provider.ask" title="对话（ask）" />
      </div>
    </>
  );
}
