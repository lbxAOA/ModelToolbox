# ModelToolbox 发布到 PyPI 脚本
# 功能：构建并发布 Python 包到 PyPI

param(
    [Parameter(Mandatory=$false)]
    [string]$Package = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$TestPyPI = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error-Custom { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }

$rootDir = "c:\ModelToolbox"
$python = if (Test-Path "$rootDir\.venv\Scripts\python.exe") { 
    "$rootDir\.venv\Scripts\python.exe" 
} else { 
    "python" 
}

Set-Location $rootDir

Write-Info "开始 PyPI 发布流程..."

# 定义包列表
$packages = @{
    "core" = "ModelCore"
    "provider" = "ModelProvider"
    "skill" = "ModelSkill"
    "mcp" = "ModelMCP"
}

# 确定要发布的包
$toPublish = @()
if ($Package -eq "all") {
    $toPublish = $packages.Values
} elseif ($packages.ContainsKey($Package)) {
    $toPublish = @($packages[$Package])
} else {
    Write-Error-Custom "未知的包: $Package"
    Write-Info "可用的包: core, provider, skill, mcp, all"
    exit 1
}

# 检查必要的工具
Write-Info "检查构建工具..."
$tools = @("build", "twine")
foreach ($tool in $tools) {
    $check = & $python -m $tool --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "$tool 未安装，正在安装..."
        & $python -m pip install $tool
    }
}

# 构建和发布每个包
foreach ($packageDir in $toPublish) {
    Write-Info "处理包: $packageDir"
    Set-Location "$rootDir\$packageDir"
    
    # 清理旧的构建文件
    Write-Info "清理旧的构建文件..."
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force "dist"
    }
    if (Test-Path "build") {
        Remove-Item -Recurse -Force "build"
    }
    
    # 构建包
    if (-not $SkipBuild) {
        Write-Info "构建 $packageDir..."
        if (-not $DryRun) {
            & $python -m build
            if ($LASTEXITCODE -ne 0) {
                Write-Error-Custom "$packageDir 构建失败"
                exit 1
            }
            Write-Success "$packageDir 构建完成"
        } else {
            Write-Info "[DRY RUN] 将构建 $packageDir"
        }
    }
    
    # 上传到 PyPI
    if (-not $DryRun) {
        Write-Info "上传 $packageDir 到 PyPI..."
        
        $repository = if ($TestPyPI) { "testpypi" } else { "pypi" }
        $repoUrl = if ($TestPyPI) { "https://test.pypi.org/legacy/" } else { "" }
        
        if ($repoUrl) {
            & $python -m twine upload --repository-url $repoUrl dist/*
        } else {
            & $python -m twine upload dist/*
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "$packageDir 已上传到 $repository"
        } else {
            Write-Error-Custom "$packageDir 上传失败"
            exit 1
        }
    } else {
        Write-Info "[DRY RUN] 将上传 $packageDir 到 PyPI"
    }
    
    Set-Location $rootDir
}

Write-Success "所有包发布完成！"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PyPI 发布摘要" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "已发布: $($toPublish.Count) 个包" -ForegroundColor Green
Write-Host "目标: $(if ($TestPyPI) { 'TestPyPI' } else { 'PyPI' })" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
