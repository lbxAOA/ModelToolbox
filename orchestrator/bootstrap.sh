#!/usr/bin/env bash
# bootstrap.sh — ModelToolbox 一键环境初始化 (macOS / Linux)
#
# 幂等、非破坏性。只装纯 Python 外壳模块，不自动安装 AGPL 的 ModelTraining。
#
# 用法:  ./orchestrator/bootstrap.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

info() { printf '\033[36m[bootstrap] %s\033[0m\n' "$*"; }
warn() { printf '\033[33m[bootstrap] %s\033[0m\n' "$*"; }

info "仓库根: $ROOT"

# 1) python
if command -v python3 >/dev/null 2>&1; then
  info "Python: $(python3 --version)"
  PY=python3
else
  warn "未找到 python3，请先安装 Python 3.9+"; exit 1
fi

# 2) 安装纯 Python 外壳模块
for m in ModelProvider ModelIngest; do
  if [ -d "$ROOT/$m" ]; then
    info "安装 $m ..."
    "$PY" -m pip install -e "$ROOT/$m" -q
  else
    warn "跳过 $m (目录不存在)"
  fi
done

# 3) .env
if [ ! -f "$ROOT/.env" ] && [ -f "$ROOT/ModelProvider/.env.example" ]; then
  cp "$ROOT/ModelProvider/.env.example" "$ROOT/.env"
  warn "已生成 .env —— 请填入 API key"
else
  info ".env 已存在或无模板，跳过"
fi

# 4) ollama (可选)
if command -v ollama >/dev/null 2>&1; then
  info "检测到 ollama，拉取 nomic-embed-text ..."
  ollama pull nomic-embed-text >/dev/null 2>&1 || warn "拉取失败(可稍后手动)"
else
  warn "未检测到 ollama。本地推理/RAG 需要它: https://ollama.com/download"
fi

info "完成。后续:"
echo "  1. 编辑 .env 填入闭源大模型 key(可选)"
echo "  2. modelprovider list"
echo "  3. modelingest --help"
echo "  4. 见 orchestrator/mcp.aggregate.json 拼装 MCP"
