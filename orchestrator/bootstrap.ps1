# bootstrap.ps1 — ModelToolbox 一键环境初始化 (Windows / PowerShell)
#
# 幂等、非破坏性：可重复运行。只装纯 Python 外壳模块，
# 不自动安装 AGPL 的 ModelTraining(需用户显式进该目录处理)。
#
# 用法:  ./orchestrator/bootstrap.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

function Info($m) { Write-Host "[bootstrap] $m" -ForegroundColor Cyan }
function Warn($m) { Write-Host "[bootstrap] $m" -ForegroundColor Yellow }

Info "仓库根: $Root"

# 1) 检查 python
try { $py = (python --version) 2>&1; Info "Python: $py" }
catch { Warn "未找到 python，请先安装 Python 3.9+"; exit 1 }

# 2) 安装纯 Python 外壳模块(可编辑)
foreach ($m in @("ModelProvider", "ModelIngest")) {
  $path = Join-Path $Root $m
  if (Test-Path $path) {
    Info "安装 $m ..."
    python -m pip install -e $path -q
  } else {
    Warn "跳过 $m (目录不存在)"
  }
}

# 3) 准备 .env
$envFile = Join-Path $Root ".env"
$envExample = Join-Path $Root "ModelProvider/.env.example"
if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
  Copy-Item $envExample $envFile
  Warn "已从 ModelProvider/.env.example 生成 .env —— 请填入 API key"
} else {
  Info ".env 已存在或无模板，跳过"
}

# 4) 检查 ollama(可选)
try {
  $null = (ollama --version) 2>&1
  Info "检测到 ollama，拉取 embedding 模型 nomic-embed-text ..."
  ollama pull nomic-embed-text 2>&1 | Out-Null
} catch {
  Warn "未检测到 ollama。本地推理/RAG 需要它: https://ollama.com/download"
}

Info "完成。后续:"
Write-Host "  1. 编辑 .env 填入闭源大模型 key(可选)"
Write-Host "  2. modelprovider list        # 检查 provider 状态"
Write-Host "  3. modelingest --help        # 文档转 md"
Write-Host "  4. 见 orchestrator/mcp.aggregate.json 拼装 MCP"
