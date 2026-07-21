import { useEffect, useState } from "react";
import { api } from "../api.js";
import TopBar from "../components/TopBar.jsx";
import Card from "../components/Card.jsx";

export default function ModelSkillPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    api.getSkills().then(setData).catch((err) => setError(err.message));
  }, []);

  const skills = (data?.skills || []).filter(
    (s) =>
      !filter ||
      s.name.toLowerCase().includes(filter.toLowerCase()) ||
      s.description.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <>
      <TopBar title="ModelSkill" subtitle="技能注册与路由（registry + hooks），只读展示" />
      <div className="content">
        {error && <Card>{error}</Card>}
        {data && (
          <Card title={`已注册技能（${data.skill_count ?? skills.length}）`}>
            <div className="field">
              <input
                type="text"
                placeholder="按名称或描述过滤…"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              />
            </div>
            {skills.map((s) => (
              <div key={s.name} style={{ marginBottom: 14 }}>
                <div style={{ fontWeight: 600 }}>{s.name}</div>
                <div className="muted" style={{ fontSize: 12.5 }}>
                  {s.path}
                </div>
                <div style={{ fontSize: 13, marginTop: 4 }}>{s.description}</div>
              </div>
            ))}
          </Card>
        )}
      </div>
    </>
  );
}
