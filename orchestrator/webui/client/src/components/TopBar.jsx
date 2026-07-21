export default function TopBar({ title, subtitle }) {
  return (
    <div className="topbar">
      <h1>{title}</h1>
      {subtitle && <div className="muted">{subtitle}</div>}
    </div>
  );
}
