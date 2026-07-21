import { useEffect, useState } from "react";
import { api } from "../api.js";
import { socket } from "../socket.js";
import Card from "./Card.jsx";
import JobConsole from "./JobConsole.jsx";

const CATALOG_MARKER = "@@CATALOG_JSON@@";

function parseCatalog(logText) {
  const line = logText.split("\n").find((l) => l.startsWith(CATALOG_MARKER));
  if (!line) return null;
  try {
    return JSON.parse(line.slice(CATALOG_MARKER.length));
  } catch {
    return null;
  }
}

function humanSize(n) {
  if (typeof n !== "number") return "";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

const LOCAL_STATUS_LABEL = {
  new: "待转换（新文件）",
  changed: "待转换（内容有更新）",
  unchanged: "已转换过（内容未变）",
};

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

/**
 * A 部分：网址 或 本地目录 二选一 → 展开目录/文件清单 → 用户确认 → （网址还需抓取）→ 填充 md。
 * 对应 modelingest 的 discover/scan → crawl（仅网址） → run 三段命令。
 */
export default function SourceDiscoverPanel() {
  const [mode, setMode] = useState("url"); // "url" | "local"
  const [form, setForm] = useState({
    url: "",
    localSource: "",
    output: "",
    mdOutput: "",
    depth: 1,
    maxPages: 100,
    allowCrossDomain: false,
    ignoreRobots: false,
  });
  const [error, setError] = useState(null);

  const [scanJob, setScanJob] = useState(null);
  const [catalog, setCatalog] = useState(null); // null = 未扫描；[] = 扫描但为空
  const [selected, setSelected] = useState(() => new Set());

  const [crawlJob, setCrawlJob] = useState(null);
  const [crawlDone, setCrawlDone] = useState(false);

  const [runJob, setRunJob] = useState(null);

  const setField = (name, value) => setForm((f) => ({ ...f, [name]: value }));

  const resetDownstream = () => {
    setError(null);
    setCatalog(null);
    setSelected(new Set());
    setCrawlJob(null);
    setCrawlDone(false);
    setRunJob(null);
  };

  const switchMode = (next) => {
    if (next === mode) return;
    setMode(next);
    resetDownstream();
    setScanJob(null);
  };

  const handleDiscoverUrl = async (e) => {
    e.preventDefault();
    resetDownstream();
    try {
      const job = await api.runAction("ingest.discover", {
        url: form.url,
        depth: form.depth,
        maxPages: form.maxPages,
        allowCrossDomain: form.allowCrossDomain,
        ignoreRobots: form.ignoreRobots,
      });
      setScanJob(job);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleScanLocal = async (e) => {
    e.preventDefault();
    resetDownstream();
    try {
      const job = await api.runAction("ingest.scan", {
        source: form.localSource,
        output: form.mdOutput,
      });
      setScanJob(job);
    } catch (err) {
      setError(err.message);
    }
  };

  useJobDone(scanJob, async (job) => {
    if (job.status !== "success") return;
    try {
      const text = await api.getJobLogs(job.id);
      const parsed = parseCatalog(text);
      if (!parsed) {
        setError("未能从任务日志中解析出目录，请查看下方日志排查");
        return;
      }
      setCatalog(parsed);
      if (mode === "url") {
        setSelected(new Set(parsed.filter((e) => e.status === "ok").map((e) => e.url)));
      } else {
        setSelected(new Set(parsed.map((e) => e.path)));
      }
    } catch (err) {
      setError(err.message);
    }
  });

  const entryKey = (entry) => (mode === "url" ? entry.url : entry.path);
  const isSelectable = (entry) => (mode === "url" ? entry.status === "ok" : true);

  const toggleKey = (key) =>
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });

  const selectAll = () =>
    setSelected(new Set((catalog || []).filter(isSelectable).map(entryKey)));
  const selectNone = () => setSelected(new Set());

  const handleConfirmUrl = async () => {
    setError(null);
    if (selected.size === 0) {
      setError("请至少勾选一个页面再确认抓取");
      return;
    }
    try {
      const job = await api.runAction("ingest.crawl", {
        output: form.output,
        urls: [...selected].join("\n"),
        depth: 0,
        ignoreRobots: form.ignoreRobots,
      });
      setCrawlJob(job);
      setCrawlDone(false);
      setRunJob(null);
    } catch (err) {
      setError(err.message);
    }
  };

  useJobDone(crawlJob, (job) => {
    setCrawlDone(job.status === "success");
  });

  const handleRunAfterCrawl = async () => {
    setError(null);
    try {
      const job = await api.runAction("ingest.run", {
        source: form.output,
        output: form.mdOutput,
      });
      setRunJob(job);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleConfirmLocal = async () => {
    setError(null);
    if (selected.size === 0) {
      setError("请至少勾选一个文件再确认填充 md");
      return;
    }
    try {
      const job = await api.runAction("ingest.run", {
        source: form.localSource,
        output: form.mdOutput,
        includes: [...selected].join("\n"),
      });
      setRunJob(job);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Card title="A 部分：网址 / 本地目录 → 展开目录确认 → 填充 md">
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button
          type="button"
          className={mode === "url" ? "btn btn-primary" : "btn"}
          onClick={() => switchMode("url")}
        >
          来源：网址
        </button>
        <button
          type="button"
          className={mode === "local" ? "btn btn-primary" : "btn"}
          onClick={() => switchMode("local")}
        >
          来源：本地目录
        </button>
      </div>

      {mode === "url" ? (
        <form onSubmit={handleDiscoverUrl}>
          <div className="field">
            <label htmlFor="wd-url">起始 URL</label>
            <input
              id="wd-url"
              type="text"
              placeholder="https://example.com"
              value={form.url}
              onChange={(e) => setField("url", e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="wd-output">原始文档输出目录（仓库内相对路径）</label>
            <input
              id="wd-output"
              type="text"
              placeholder="ObsidianRag/_crawled"
              value={form.output}
              onChange={(e) => setField("output", e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="wd-md-output">清洗转换后的 md 输出目录</label>
            <input
              id="wd-md-output"
              type="text"
              placeholder="ObsidianRag/_crawled_md"
              value={form.mdOutput}
              onChange={(e) => setField("mdOutput", e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="wd-depth">发现深度（跟随分支链接层数）</label>
            <input id="wd-depth" type="number" value={form.depth} onChange={(e) => setField("depth", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="wd-max">最多发现页面数（安全上限）</label>
            <input id="wd-max" type="number" value={form.maxPages} onChange={(e) => setField("maxPages", e.target.value)} />
          </div>
          <div className="field-checkbox">
            <input
              type="checkbox"
              id="wd-cross"
              checked={form.allowCrossDomain}
              onChange={(e) => setField("allowCrossDomain", e.target.checked)}
            />
            <label htmlFor="wd-cross">允许跨域跟随</label>
          </div>
          <div className="field-checkbox">
            <input
              type="checkbox"
              id="wd-robots"
              checked={form.ignoreRobots}
              onChange={(e) => setField("ignoreRobots", e.target.checked)}
            />
            <label htmlFor="wd-robots">忽略 robots.txt</label>
          </div>
          <button className="btn" type="submit">
            ① 扫描分支页面（discover）
          </button>
        </form>
      ) : (
        <form onSubmit={handleScanLocal}>
          <div className="field">
            <label htmlFor="wd-local-source">本地文件夹地址（仓库内相对路径）</label>
            <input
              id="wd-local-source"
              type="text"
              placeholder="ObsidianRag/Algorithms"
              value={form.localSource}
              onChange={(e) => setField("localSource", e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="wd-local-md-output">清洗转换后的 md 输出目录</label>
            <input
              id="wd-local-md-output"
              type="text"
              placeholder="ObsidianRag/Algorithms_md"
              value={form.mdOutput}
              onChange={(e) => setField("mdOutput", e.target.value)}
              required
            />
          </div>
          <button className="btn" type="submit">
            ① 展开文件夹目录（scan）
          </button>
        </form>
      )}

      {error && (
        <div className="muted" style={{ color: "var(--danger)", marginTop: 8 }}>
          {error}
        </div>
      )}

      {scanJob && (
        <div style={{ marginTop: 16 }}>
          <JobConsole job={scanJob} />
        </div>
      )}

      {catalog && (
        <div style={{ marginTop: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h3 style={{ margin: 0 }}>
              ② 确认目录（共 {catalog.length} {mode === "url" ? "个页面" : "个文件"} · 已选 {selected.size}）
            </h3>
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" className="btn" onClick={selectAll}>
                全选可用
              </button>
              <button type="button" className="btn" onClick={selectNone}>
                全不选
              </button>
            </div>
          </div>
          <div style={{ maxHeight: 320, overflowY: "auto", border: "1px solid var(--border)", borderRadius: 8 }}>
            <table className="table">
              <thead>
                <tr>
                  <th></th>
                  {mode === "url" ? (
                    <>
                      <th>标题</th>
                      <th>URL</th>
                      <th>层级</th>
                      <th>状态</th>
                    </>
                  ) : (
                    <>
                      <th>相对路径</th>
                      <th>类型</th>
                      <th>大小</th>
                      <th>状态</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {catalog.map((entry) => {
                  const key = entryKey(entry);
                  return (
                    <tr key={key}>
                      <td>
                        <input
                          type="checkbox"
                          disabled={!isSelectable(entry)}
                          checked={selected.has(key)}
                          onChange={() => toggleKey(key)}
                        />
                      </td>
                      {mode === "url" ? (
                        <>
                          <td>{entry.title || "（无标题）"}</td>
                          <td className="muted" style={{ wordBreak: "break-all" }}>
                            {entry.url}
                          </td>
                          <td>{entry.depth}</td>
                          <td>{entry.status === "ok" ? "可用" : `失败：${entry.error || ""}`}</td>
                        </>
                      ) : (
                        <>
                          <td className="muted" style={{ wordBreak: "break-all" }}>
                            {entry.path}
                          </td>
                          <td>{entry.ext}</td>
                          <td>{humanSize(entry.size)}</td>
                          <td>{LOCAL_STATUS_LABEL[entry.status] || entry.status}</td>
                        </>
                      )}
                    </tr>
                  );
                })}
                {catalog.length === 0 && (
                  <tr>
                    <td colSpan={5} className="muted">
                      未发现任何{mode === "url" ? "页面" : "可转换文件"}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {mode === "url" ? (
            <button className="btn" style={{ marginTop: 12 }} type="button" onClick={handleConfirmUrl}>
              ③ 确认抓取选中内容（crawl）
            </button>
          ) : (
            <button className="btn" style={{ marginTop: 12 }} type="button" onClick={handleConfirmLocal}>
              ③ 确认填充 md 文件（run）
            </button>
          )}
        </div>
      )}

      {crawlJob && (
        <div style={{ marginTop: 16 }}>
          <JobConsole job={crawlJob} />
        </div>
      )}

      {mode === "url" && crawlDone && (
        <button className="btn" style={{ marginTop: 12 }} type="button" onClick={handleRunAfterCrawl}>
          ④ 清洗转换，填充 md（run）
        </button>
      )}

      {runJob && (
        <div style={{ marginTop: 16 }}>
          <JobConsole job={runJob} />
        </div>
      )}
    </Card>
  );
}
