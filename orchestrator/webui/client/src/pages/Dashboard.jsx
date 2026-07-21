import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";
import TopBar from "../components/TopBar.jsx";
import Card from "../components/Card.jsx";

const MODULE_ROUTES = {
  "model-ingest": "/ingest",
  "model-provider": "/provider",
  "model-training": "/training",
  pipeline: "/pipeline",
  "model-mcp": "/mcp",
  "model-memory": "/memory",
  "model-office": "/office",
  "model-skill": "/skill",
  "obsidian-rag": "/obsidian",
};

export default function Dashboard() {
  const [modules, setModules] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.getModules().then(setModules).catch((err) => setError(err.message));
  }, []);

  return (
    <>
      <TopBar title="ModelToolbox 总控台" subtitle="本地模型系统：训练为主，检索兜底" />
      <div className="content">
        {error && <Card>{error}</Card>}
        <div className="card-grid">
          {modules.map((m) => (
            <div
              key={m.id}
              className="card"
              style={{ cursor: MODULE_ROUTES[m.id] ? "pointer" : "default" }}
              onClick={() => MODULE_ROUTES[m.id] && navigate(MODULE_ROUTES[m.id])}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <h3>{m.name}</h3>
                <span className="badge">{m.license}</span>
              </div>
              <div className="muted" style={{ marginBottom: 8 }}>
                {m.tagline}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>
                {m.stage} · {m.path}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
