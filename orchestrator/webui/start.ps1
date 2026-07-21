Param(
    [switch]$Dev,       # 开发模式：分别启动 client(vite dev server) 和 server(nodemon 式重启无, 直接 node)
    [switch]$SkipBuild  # 跳过前端构建（生产模式下若 dist 已存在可用）
)

# ModelToolbox Web 总控台启动脚本（Windows）。
# 生产模式（默认）：安装依赖 -> 构建前端 -> 启动后端（单端口同时提供 API + 静态页面 + WebSocket）。
# 开发模式（-Dev）：分别启动 vite dev server（热更新）与 node 后端，通过 vite 代理互通。

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$serverDir = Join-Path $root "server"
$clientDir = Join-Path $root "client"

function Ensure-Deps($dir) {
    if (-not (Test-Path (Join-Path $dir "node_modules"))) {
        Write-Host "安装依赖：$dir" -ForegroundColor Cyan
        Push-Location $dir
        npm install
        Pop-Location
    }
}

Ensure-Deps $serverDir
Ensure-Deps $clientDir

if ($Dev) {
    Write-Host "开发模式：分别启动 client (vite :5173) 与 server (:5678)" -ForegroundColor Cyan
    $serverProc = Start-Process -FilePath "node" -ArgumentList "src/index.js" -WorkingDirectory $serverDir -PassThru -NoNewWindow
    try {
        Push-Location $clientDir
        npm run dev
    } finally {
        Pop-Location
        if ($serverProc -and -not $serverProc.HasExited) {
            Stop-Process -Id $serverProc.Id -Force -ErrorAction SilentlyContinue
        }
    }
    exit 0
}

if (-not $SkipBuild) {
    Write-Host "构建前端…" -ForegroundColor Cyan
    Push-Location $clientDir
    npm run build
    Pop-Location
}

Write-Host "启动 ModelToolbox 总控台…" -ForegroundColor Cyan
Push-Location $serverDir
try {
    node src/index.js
} finally {
    Pop-Location
}
