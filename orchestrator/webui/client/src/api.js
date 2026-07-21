const BASE = "/api";

async function request(method, url, body) {
  const res = await fetch(`${BASE}${url}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const isJson = res.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await res.json() : await res.text();
  if (!res.ok) {
    const message = (isJson && data?.error) || `请求失败（${res.status}）`;
    throw new Error(message);
  }
  return data;
}

export const api = {
  getModules: () => request("GET", "/modules"),
  getModule: (id) => request("GET", `/modules/${id}`),
  getActions: () => request("GET", "/actions"),

  runAction: (actionId, params) => request("POST", "/jobs", { actionId, params }),
  getJobs: () => request("GET", "/jobs"),
  getJob: (id) => request("GET", `/jobs/${id}`),
  getJobLogs: (id) => request("GET", `/jobs/${id}/logs`),
  killJob: (id) => request("POST", `/jobs/${id}/kill`),

  getMcpServers: () => request("GET", "/mcp-servers"),
  startMcpServer: (name) => request("POST", `/mcp-servers/${name}/start`),
  stopMcpServer: (name) => request("POST", `/mcp-servers/${name}/stop`),
  getMcpLogs: (name) => request("GET", `/mcp-servers/${name}/logs`),

  getIngestManifest: (relPath) => request("GET", `/ingest/manifest?path=${encodeURIComponent(relPath)}`),

  getObsidianTree: () => request("GET", "/obsidian/tree"),
  getObsidianNote: (relPath) => request("GET", `/obsidian/note?path=${encodeURIComponent(relPath)}`),

  getSkills: () => request("GET", "/skills"),
};
