import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "总览 Dashboard", end: true },
  { to: "/ingest", label: "ModelIngest" },
  { to: "/provider", label: "ModelProvider" },
  { to: "/pipeline", label: "Pipeline 管线" },
  { to: "/training", label: "ModelTraining" },
  { to: "/mcp", label: "ModelMCP" },
  { to: "/memory", label: "ModelMemory" },
  { to: "/skill", label: "ModelSkill" },
  { to: "/obsidian", label: "ObsidianRag" },
  { to: "/office", label: "ModelOffice" },
  { to: "/jobs", label: "任务历史 Jobs" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">ModelToolbox</div>
      {LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.end}
          className={({ isActive }) => "sidebar-link" + (isActive ? " active" : "")}
        >
          {link.label}
        </NavLink>
      ))}
    </aside>
  );
}
