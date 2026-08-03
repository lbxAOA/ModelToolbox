# ModelToolbox 发布前检查脚本
# 功能：在发布前验证所有必要条件

param(
    [Parameter(Mandatory=$false)]
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"

function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error-Custom { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }

$rootDir = "c:\ModelToolbox"
Set-Location $rootDir

$python = if (Test-Path "$rootDir\.venv\Scripts\python.exe") { 
    "$rootDir\.venv\Scripts\python.exe" 
} else { 
    "python" 
}

$checks = @{
    "passed" = 0
    "failed" = 0
    "warnings" = 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ModelToolbox 发布前检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 Git 状态
Write-Info "检查 Git 工作区..."
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Warning "工作区有未提交的更改"
    $checks.warnings++
} else {
    Write-Success "工作区干净"
    $checks.passed++
}

# 2. 检查当前分支
$branch = git rev-parse --abbrev-ref HEAD
Write-Info "当前分支: $branch"
if ($branch -ne "main" -and $branch -ne "master") {
    Write-Warning "不在主分支上"
    $checks.warnings++
} else {
    Write-Success "在主分支上"
    $checks.passed++
}

# 3. 检查是否与远程同步
Write-Info "检查远程同步状态..."
git fetch origin
$localCommit = git rev-parse HEAD
$remoteCommit = git rev-parse origin/$branch
if ($localCommit -ne $remoteCommit) {
    Write-Warning "本地与远程不同步"
    $checks.warnings++
} else {
    Write-Success "与远程同步"
    $checks.passed++
}

# 4. 检查版本号一致性
if ($Version) {
    Write-Info "检查版本号一致性..."
    $versionFiles = @(
        "pyproject.toml",
        "ModelCore/pyproject.toml",
        "ModelProvider/pyproject.toml",
        "ModelSkill/pyproject.toml",
        "ModelMCP/pyproject.toml",
        "package.json"
    )
    
    $inconsistent = $false
    foreach ($file in $versionFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            if ($content -notmatch [regex]::Escape($Version)) {
                Write-Warning "$file 版本号不一致"
                $inconsistent = $true
            }
        }
    }
    
    if ($inconsistent) {
        $checks.failed++
    } else {
        Write-Success "版本号一致"
        $checks.passed++
    }
}

# 5. 运行测试
Write-Info "运行测试套件..."
$modules = @("ModelCore", "ModelProvider", "ModelSkill", "ModelMCP")
$testsFailed = $false

foreach ($module in $modules) {
    $result = & $python -m pytest "$module/tests/" -q 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "$module 测试失败"
        $testsFailed = $true
    }
}

if ($testsFailed) {
    $checks.failed++
} else {
    Write-Success "所有测试通过"
    $checks.passed++
}

# 6. 检查包构建
Write-Info "检查包构建..."
$buildOk = $true
foreach ($module in $modules) {
    Set-Location "$rootDir\$module"
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
    }
    
    Write-Info "构建 $module..."
    & $python -m build --wheel --no-isolation
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "$module 构建失败"
        $buildOk = $false
    }
    
    Set-Location $rootDir
}

if ($buildOk) {
    Write-Success "所有包构建成功"
    $checks.passed++
} else {
    $checks.failed++
}

# 7. 检查文档
Write-Info "检查文档文件..."
$docs = @("README.md", "CHANGELOG.md", "LICENSE")
$docsMissing = $false

foreach ($doc in $docs) {
    if (-not (Test-Path $doc)) {
        Write-Warning "缺少 $doc"
        $docsMissing = $true
    }
}

if ($docsMissing) {
    $checks.warnings++
} else {
    Write-Success "文档完整"
    $checks.passed++
}

# 8. 检查依赖
Write-Info "检查 Python 依赖..."
$requiredTools = @("build", "twine", "pytest")
$missingTools = @()

foreach ($tool in $requiredTools) {
    $check = & $python -m $tool --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingTools += $tool
    }
}

if ($missingTools.Count -gt 0) {
    Write-Warning "缺少工具: $($missingTools -join ', ')"
    $checks.warnings++
} else {
    Write-Success "所有必需工具已安装"
    $checks.passed++
}

# 9. 检查 NPM 登录
Write-Info "检查 NPM 状态..."
$npmUser = npm whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "未登录 NPM"
    $checks.warnings++
} else {
    Write-Success "NPM 已登录: $npmUser"
    $checks.passed++
}

# 10. 检查 PyPI 配置
Write-Info "检查 PyPI 配置..."
if (Test-Path "$env:USERPROFILE\.pypirc") {
    Write-Success "PyPI 配置文件存在"
    $checks.passed++
} else {
    Write-Warning "未找到 PyPI 配置文件"
    $checks.warnings++
}

# 显示总结
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "检查结果" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "通过: $($checks.passed)" -ForegroundColor Green
Write-Host "警告: $($checks.warnings)" -ForegroundColor Yellow
Write-Host "失败: $($checks.failed)" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($checks.failed -gt 0) {
    Write-Error-Custom "发布前检查失败！请修复错误后重试。"
    exit 1
} elseif ($checks.warnings -gt 0) {
    Write-Warning "发布前检查通过，但有警告。"
    exit 0
} else {
    Write-Success "发布前检查全部通过！可以安全发布。"
    exit 0
}
