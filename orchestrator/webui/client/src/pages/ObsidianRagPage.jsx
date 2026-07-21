import { useEffect, useState } from "react";
import { api } from "../api.js";
import TopBar from "../components/TopBar.jsx";
import Card from "../components/Card.jsx";

function TreeNode({ node, activePath, onSelect }) {
  const [open, setOpen] = useState(false);
  if (node.type === "file") {
    return (
      <div
        className={"tree-file" + (activePath === node.path ? " active" : "")}
        onClick={() => onSelect(node.path)}
      >
        📄 {node.name}
      </div>
    );
  }
  return (
    <div className="tree-node">
      <div className="tree-file" onClick={() => setOpen((o) => !o)}>
        {open ? "📂" : "📁"} {node.name}
      </div>
      {open && (
        <div style={{ paddingLeft: 16 }}>
          {node.children.map((child) => (
            <TreeNode key={child.path} node={child} activePath={activePath} onSelect={onSelect} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function ObsidianRagPage() {
  const [tree, setTree] = useState([]);
  const [error, setError] = useState(null);
  const [selectedPath, setSelectedPath] = useState(null);
  const [note, setNote] = useState(null);

  useEffect(() => {
    api.getObsidianTree().then(setTree).catch((err) => setError(err.message));
  }, []);

  const handleSelect = async (relPath) => {
    setSelectedPath(relPath);
    setNote(null);
    try {
      const data = await api.getObsidianNote(relPath);
      setNote(data.content);
    } catch (err) {
      setNote(`（读取失败：${err.message}）`);
    }
  };

  return (
    <>
      <TopBar title="ObsidianRag" subtitle="知识库语料只读浏览（原件不入库，检索兜底）" />
      <div className="content" style={{ display: "flex", gap: 16 }}>
        <Card title="目录" >
          <div style={{ width: 260, maxHeight: "70vh", overflowY: "auto" }}>
            {error && <div className="muted">{error}</div>}
            {tree.map((node) => (
              <TreeNode key={node.path} node={node} activePath={selectedPath} onSelect={handleSelect} />
            ))}
          </div>
        </Card>
        <Card title={selectedPath || "选择左侧文件查看内容"} >
          <div style={{ minWidth: 400 }}>
            {note != null ? <div className="note-view">{note}</div> : <div className="muted">尚未选择文件</div>}
          </div>
        </Card>
      </div>
    </>
  );
}
