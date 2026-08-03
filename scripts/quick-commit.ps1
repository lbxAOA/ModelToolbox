#!/usr/bin/env pwsh
# ModelToolbox 快速提交脚本
# 用法: .\scripts\quick-commit.ps1 "commit message"

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Message
)

$ErrorActionPreference = "Stop"

function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }

Set-Location "c:\ModelToolbox"

Write-Info "提交更改..."

# 显示状态
git status --short

# 添加所有更改
git add .

# 提交
git commit -m $Message

# 推送
$branch = git rev-parse --abbrev-ref HEAD
Write-Info "推送到 $branch..."
git push origin $branch

Write-Success "提交完成！"
