import { useEffect, useState } from "react";
import { api } from "../api.js";
import { socket } from "../socket.js";
import Card from "./Card.jsx";
import JobConsole from "./JobConsole.jsx";

/** 订阅某个 job 直到结束（success/failed），结束时回调一次。 */
function useJobDone(job, onDone) {
  useEffect(() => {
    if (!job) return undefined;
    if (job.status !== "running") {
      onDone(job);
      return undefined;
    }
    let cancelled = false;
    socket.emit("job:subscribe", job.id);
    const onJobDone = (payload) => {
      if (cancelled || payload.id !== job.id) return;
      onDone(payload);
    };
    socket.on("job:done", onJobDone);
    return () => {
      cancelled = true;
      socket.off("job:done", onJobDone);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [job?.id]);
}

async function runJobAndGetLogs(actionId, params) {
  const job = await api.runAction(actionId, params);
  return job;
}

/**
 * B 部分：本地 md 目录 → 选择 AI（本地 Ollama 型号 / 已配置的外部 API）→ 蒸馏
 * → 蒸馏成功后自动生成一个 ModelSkill 技能，登记这个知识库怎么检索。
 */
export default function DistillPanel() {
  const [form, setForm] = useState({
    source: "",
    output: "",
    profile: "concept",
    aiKind: "ollama", // "ollama" | "api"
    ollamaModel: "",
    apiProvider: "",
    apiModel: "",
    kbName: "",
    kbTriggers: "",
  });
  const [error, setError] = useState(null);

  const [ollamaModels, setOllamaModels] = useState(null); // null=未加载
  const [ollamaLoading, setOllamaLoading] = useState(false);
  const [apiProviders, setApiProviders] = useState(null); // null=未加载
  const [apiLoading, setApiLoading] = useState(false);

  const [distillJob, setDistillJob] = useState(null);
  const [distillDone, setDistillDone] = useState(false);
  const [skillJob, setSkillJob] = useState(null);

  const setField = (name, value) => setForm((f) => ({ ...f, [name]: value }));

  const loadOllamaModels = async () => {
    setError(null);
    setOllamaLoading(true);
    try {
      const job = await runJobAndGetLogs("provider.models", { provider: "ollama" });
      // 短命令：直接等它结束后取日志解析，不单独渲染 JobConsole。
      await new Promise((resolve) => {
        if (job.status !== "running") return resolve();
        socket.emit("job:subscribe", job.id);
        const onDone = (payload) => {
          if (payload.id !== job.id) return;
          socket.off("job:done", onDone);
          resolve();
        };
        socket.on("job:done", onDone);
      });
      const text = await api.getJobLogs(job.id);
      const names = JSON.parse(text.trim().split("\n").pop());
      setOllamaModels(names);
      if (names.length > 0 && !form.ollamaModel) setField("ollamaModel", names[0]);
    } catch (err) {
      setError(`获取 Ollama 模型列表失败：${err.message}`);
      setOllamaModels([]);
    } finally {
      setOllamaLoading(false);
    }
  };

  const loadApiProviders = async () => {
    setError(null);
    setApiLoading(true);
    try {
      const job = await runJobAndGetLogs("provider.listJson", {});
      await new Promise((resolve) => {
        if (job.status !== "running") return resolve();
        socket.emit("job:subscribe", job.id);
        const onDone = (payload) => {
          if (payload.id !== job.id) return;
          socket.off("job:done", onDone);
          resolve();
        };
        socket.on("job:done", onDone);
      });
      const text = await api.getJobLogs(job.id);
      const data = JSON.parse(text.trim().split("\n").pop());
      const ok = (data.providers || []).filter((p) => p.status === "ok" && p.name !== "ollama");
      setApiProviders(ok);
      if (ok.length > 0 && !form.apiProvider) setField("apiProvider", ok[0].name);
    } catch (err) {
      setError(`获取已配置 API 列表失败：${err.message}`);
      setApiProviders([]);
    } finally {
      setApiLoading(false);
    }
  };

  const modelSpec = () => {
    if (form.aiKind === "ollama") {
      if (!form.ollamaModel) return null;
      return `ollama:${form.ollamaModel}`;
    }
    if (!form.apiProvider) return null;
    return form.apiModel ? `${form.apiProvider}:${form.apiModel}` : form.apiProvider;
  };

  const handleDistill = async (e) => {
    e.preventDefault();
    setError(null);
    setDistillDone(false);
    setSkillJob(null);
    const spec = modelSpec();
    if (!spec) {
      setError("请先选择本地 Ollama 型号，或已配置的外部 API");
      return;
    }
    if (!form.kbName.trim()) {
      setError("请填写知识库名称（用于自动生成检索技能）");
      return;
    }
    try {
      const job = await api.runAction("ingest.distill", {
        source: form.source,
        output: form.output,
        profile: form.profile,
        model: spec,
      });
      setDistillJob(job);
    } catch (err) {
      setError(err.message);
    }
  };

  useJobDone(distillJob, (job) => {
    setDistillDone(job.status === "success");
  });

  const handleMakeSkill = async () => {
    setError(null);
    const spec = modelSpec();
    try {
      const job = await api.runAction("ingest.makeSkill", {
        name: form.kbName,
        description: `知识库「${form.kbName}」，由 ${form.source} 蒸馏而来。`,
        triggers: form.kbTriggers,
        vault: form.output,
        source: form.source,
        modelSpec: spec,
        profile: form.profile,
      });
      setSkillJob(job);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Card title="B 部分：本地 md 目录 → 选择 AI → 蒸馏知识库 → 自动生成检索技能">
      <form onSubmit={handleDistill}>
        <div className="field">
          <label htmlFor="di-source">md 源目录（已经全部是清洗后的 md 文件）</label>
          <input
            id="di-source"
            type="text"
            placeholder="ObsidianRag_md"
            value={form.source}
            onChange={(e) => setField("source", e.target.value)}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="di-output">知识库(vault)输出目录</label>
          <input
            id="di-output"
            type="text"
            placeholder="ObsidianRag_vault"
            value={form.output}
            onChange={(e) => setField("output", e.target.value)}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="di-profile">笔记模板 profile</label>
          <select id="di-profile" value={form.profile} onChange={(e) => setField("profile", e.target.value)}>
            <option value="concept">concept</option>
            <option value="algorithm">algorithm</option>
          </select>
        </div>

        <div style={{ display: "flex", gap: 8, margin: "12px 0" }}>
          <button
            type="button"
            className={form.aiKind === "ollama" ? "btn btn-primary" : "btn"}
            onClick={() => setField("aiKind", "ollama")}
          >
            本地 Ollama 模型
          </button>
          <button
            type="button"
            className={form.aiKind === "api" ? "btn btn-primary" : "btn"}
            onClick={() => setField("aiKind", "api")}
          >
            已配置的外部 API
          </button>
        </div>

        {form.aiKind === "ollama" ? (
          <div className="field">
            <label htmlFor="di-ollama-model">Ollama 已安装型号</label>
            <div style={{ display: "flex", gap: 8 }}>
              <select
                id="di-ollama-model"
                value={form.ollamaModel}
                onChange={(e) => setField("ollamaModel", e.target.value)}
                style={{ flex: 1 }}
              >
                {(ollamaModels || []).length === 0 && <option value="">（先点击刷新获取型号）</option>}
                {(ollamaModels || []).map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
              <button type="button" className="btn" onClick={loadOllamaModels} disabled={ollamaLoading}>
                {ollamaLoading ? "加载中…" : "刷新型号列表"}
              </button>
            </div>
          </div>
        ) : (
          <div className="field">
            <label htmlFor="di-api-provider">已配置的 provider（status=ok）</label>
            <div style={{ display: "flex", gap: 8 }}>
              <select
                id="di-api-provider"
                value={form.apiProvider}
                onChange={(e) => setField("apiProvider", e.target.value)}
                style={{ flex: 1 }}
              >
                {(apiProviders || []).length === 0 && <option value="">（先点击刷新获取已配置的 API）</option>}
                {(apiProviders || []).map((p) => (
                  <option key={p.name} value={p.name}>
                    {p.name}（默认 {p.default_model || "（无需指定）"}）
                  </option>
                ))}
              </select>
              <button type="button" className="btn" onClick={loadApiProviders} disabled={apiLoading}>
                {apiLoading ? "加载中…" : "刷新 API 列表"}
              </button>
            </div>
            <input
              style={{ marginTop: 8 }}
              type="text"
              placeholder="覆盖模型（可选，缺省用该 provider 默认模型）"
              value={form.apiModel}
              onChange={(e) => setField("apiModel", e.target.value)}
            />
          </div>
        )}

        <div className="field">
          <label htmlFor="di-kb-name">知识库名称（必填，用于自动生成检索技能）</label>
          <input
            id="di-kb-name"
            type="text"
            placeholder="oi-wiki 算法竞赛知识库"
            value={form.kbName}
            onChange={(e) => setField("kbName", e.target.value)}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="di-kb-triggers">技能触发词（可选，逗号分隔，用于以后被更好地检索匹配）</label>
          <input
            id="di-kb-triggers"
            type="text"
            placeholder="算法竞赛, oi wiki, 动态规划"
            value={form.kbTriggers}
            onChange={(e) => setField("kbTriggers", e.target.value)}
          />
        </div>

        <button className="btn" type="submit">
          ① 蒸馏知识库（distill）
        </button>
      </form>

      {error && (
        <div className="muted" style={{ color: "var(--danger)", marginTop: 8 }}>
          {error}
        </div>
      )}

      {distillJob && (
        <div style={{ marginTop: 16 }}>
          <JobConsole job={distillJob} />
        </div>
      )}

      {distillDone && (
        <button className="btn" style={{ marginTop: 12 }} type="button" onClick={handleMakeSkill}>
          ② 自动生成检索技能（make-skill）
        </button>
      )}

      {skillJob && (
        <div style={{ marginTop: 16 }}>
          <JobConsole job={skillJob} />
        </div>
      )}
    </Card>
  );
}
