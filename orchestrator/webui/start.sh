#!/usr/bin/env bash
# ModelToolbox Web 总控台启动脚本（macOS / Linux）。
# 生产模式（默认）：安装依赖 -> 构建前端 -> 启动后端（单端口同时提供 API + 静态页面 + WebSocket）。
# 开发模式（--dev）：分别启动 vite dev server（热更新）与 node 后端。
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$ROOT_DIR/server"
CLIENT_DIR="$ROOT_DIR/client"

DEV=false
SKIP_BUILD=false
for arg in "$@"; do
  case "$arg" in
    --dev) DEV=true ;;
    --skip-build) SKIP_BUILD=true ;;
  esac
done

ensure_deps() {
  local dir="$1"
  if [ ! -d "$dir/node_modules" ]; then
    echo "安装依赖：$dir"
    (cd "$dir" && npm install)
  fi
}

ensure_deps "$SERVER_DIR"
ensure_deps "$CLIENT_DIR"

if [ "$DEV" = true ]; then
  echo "开发模式：分别启动 client (vite :5173) 与 server (:5678)"
  (cd "$SERVER_DIR" && node src/index.js) &
  SERVER_PID=$!
  trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
  (cd "$CLIENT_DIR" && npm run dev)
  exit 0
fi

if [ "$SKIP_BUILD" = false ]; then
  echo "构建前端…"
  (cd "$CLIENT_DIR" && npm run build)
fi

echo "启动 ModelToolbox 总控台…"
cd "$SERVER_DIR"
exec node src/index.js
