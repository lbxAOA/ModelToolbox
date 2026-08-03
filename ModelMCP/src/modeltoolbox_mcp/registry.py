from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re

from modeltoolbox_core.config import default_config
from modeltoolbox_core.paths import resolve_in_root


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = default_config().state_dir / "mcp" / "servers.json"


@dataclass(frozen=True)
class McpServer:
    name: str
    command: list[str]
    cwd: str | None = None
    description: str = ""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-._")
    if not slug:
        raise ValueError("Server name must contain at least one safe character")
    if slug in {".", ".."}:
        raise ValueError("Invalid server name")
    return slug


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, object]:
    if not path.exists():
        return {"servers": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(payload: dict[str, object], path: Path = DEFAULT_REGISTRY) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def list_servers(path: Path = DEFAULT_REGISTRY) -> list[McpServer]:
    payload = load_registry(path)
    servers = payload.get("servers", [])
    if not isinstance(servers, list):
        return []
    records: list[McpServer] = []
    for item in servers:
        if not isinstance(item, dict):
            continue
        command = item.get("command", [])
        if not item.get("name") or not isinstance(command, list):
            continue
        records.append(
            McpServer(
                name=str(item["name"]),
                command=[str(part) for part in command],
                cwd=str(item["cwd"]) if item.get("cwd") else None,
                description=str(item.get("description") or ""),
            )
        )
    return sorted(records, key=lambda server: server.name.lower())


def upsert_server(server: McpServer, path: Path = DEFAULT_REGISTRY) -> None:
    payload = load_registry(path)
    servers = [item for item in payload.get("servers", []) if isinstance(item, dict) and item.get("name") != server.name]
    servers.append(server.__dict__)
    payload["servers"] = sorted(servers, key=lambda item: str(item.get("name", "")).lower())
    save_registry(payload, path)


def remove_server(name: str, path: Path = DEFAULT_REGISTRY) -> bool:
    payload = load_registry(path)
    before = [item for item in payload.get("servers", []) if isinstance(item, dict)]
    after = [item for item in before if item.get("name") != name]
    payload["servers"] = after
    save_registry(payload, path)
    return len(after) != len(before)


def discover_servers(root: Path = PROJECT_ROOT, path: Path = DEFAULT_REGISTRY) -> list[McpServer]:
    discovered: list[McpServer] = []
    for server_py in sorted(root.glob("*/server.py")):
        name = slugify(server_py.parent.name)
        command = ["python", "server.py"]
        record = McpServer(
            name=name,
            command=command,
            cwd=server_py.parent.resolve().as_posix(),
            description=f"Discovered MCP server from {server_py.parent.name}",
        )
        upsert_server(record, path)
        discovered.append(record)
    return discovered


def export_config(path: Path = DEFAULT_REGISTRY) -> dict[str, object]:
    servers: dict[str, object] = {}
    for server in list_servers(path):
        servers[server.name] = {
            "command": server.command[0],
            "args": server.command[1:],
            "cwd": server.cwd,
        }
    return {"mcpServers": servers}


def scaffold_server(name: str, *, root: Path = PROJECT_ROOT, overwrite: bool = False) -> Path:
    slug = slugify(name)
    target = resolve_in_root(root, slug)
    if target.exists() and not overwrite:
        raise FileExistsError(f"MCP server already exists: {target}")
    target.mkdir(parents=True, exist_ok=True)
    server_py = target / "server.py"
    if server_py.exists() and not overwrite:
        raise FileExistsError(f"MCP server already exists: {server_py}")
    server_py.write_text(
        """from __future__ import annotations


def main() -> None:
    print(\"MCP server scaffold: replace this with a real transport implementation.\")


if __name__ == \"__main__\":
    main()
""",
        encoding="utf-8",
    )
    upsert_server(
        McpServer(
            name=slug,
            command=["python", "server.py"],
            cwd=target.resolve().as_posix(),
            description="Generated MCP server scaffold",
        )
    )
    return server_py
