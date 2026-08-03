# ModelToolbox 自动发布脚本
# 功能：提交到 GitHub 并发布到 NPM

param(
    [Parameter(Mandatory=$false)]
    [string]$Version = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Message = "chore: release version",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipGit = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipNpm = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error-Custom { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }

# 检查当前目录
$rootDir = "c:\ModelToolbox"
$python = if (Test-Path "$rootDir\.venv\Scripts\python.exe") { 
    "$rootDir\.venv\Scripts\python.exe" 
} else { 
    "python" 
}

if (-not (Test-Path "$rootDir\pyproject.toml")) {
    Write-Error-Custom "请在 ModelToolbox 根目录运行此脚本"
    exit 1
}

Set-Location $rootDir

Write-Info "开始发布流程..."

# 1. 检查工作区状态
Write-Info "检查 Git 工作区状态..."
$gitStatus = git status --porcelain
if ($gitStatus -and -not $DryRun) {
    Write-Warning "工作区有未提交的更改："
    git status --short
    $confirm = Read-Host "是否继续? (y/N)"
    if ($confirm -ne "y") {
        Write-Info "已取消发布"
        exit 0
    }
}

# 2. 运行测试
if (-not $SkipTests) {
    Write-Info "运行测试套件..."
    
    $modules = @("ModelCore", "ModelProvider", "ModelSkill", "ModelMCP")
    $totalTests = 0
    $failedTests = 0
    
    foreach ($module in $modules) {
        Write-Info "测试 $module..."
        $result = & $python -m pytest "$module/tests/" -v --tb=short 2>&1 | Out-String
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -ne 0) {
            Write-Error-Custom "$module 测试失败"
            Write-Host $result
            $failedTests++
        } else {
            # 提取通过的测试数量
            if ($result -match "(\d+) passed") {
                $passed = $matches[1]
                $totalTests += [int]$passed
                Write-Success "${module}: $passed 个测试通过"
            }
        }
    }
    
    if ($failedTests -gt 0) {
        Write-Error-Custom "有 $failedTests 个模块测试失败，终止发布"
        exit 1
    }
    
    Write-Success "所有测试通过！总计 $totalTests 个测试"
} else {
    Write-Warning "跳过测试"
}

# 3. 更新版本号（如果指定）
if ($Version) {
    Write-Info "更新版本号到 $Version..."
    
    if (-not $DryRun) {
        # 更新 Python 包版本
        $pyprojectFiles = @(
            "pyproject.toml",
            "ModelCore/pyproject.toml",
            "ModelProvider/pyproject.toml",
            "ModelSkill/pyproject.toml",
            "ModelMCP/pyproject.toml"
        )
        
        foreach ($file in $pyprojectFiles) {
            if (Test-Path $file) {
                $content = Get-Content $file -Raw
                $content = $content -replace 'version\s*=\s*"[\d\.]+"', "version = `"$Version`""
                Set-Content $file $content -NoNewline
                Write-Success "已更新 $file"
            }
        }
        
        # 更新 NPM 包版本
        if (Test-Path "package.json") {
            $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
            $packageJson.version = $Version
            $packageJson | ConvertTo-Json -Depth 10 | Set-Content "package.json"
            Write-Success "已更新 package.json"
        }
    } else {
        Write-Info "[DRY RUN] 将更新版本号到 $Version"
    }
}

# 4. Git 提交和推送
if (-not $SkipGit) {
    Write-Info "提交到 GitHub..."
    
    if (-not $DryRun) {
        # 添加所有更改
        git add .
        
        # 创建提交
        $commitMsg = if ($Version) { "$Message $Version" } else { $Message }
        git commit -m $commitMsg
        
        # 如果指定了版本，创建标签
        if ($Version) {
            git tag -a "v$Version" -m "Release version $Version"
            Write-Success "已创建标签 v$Version"
        }
        
        # 推送到远程
        $currentBranch = git rev-parse --abbrev-ref HEAD
        Write-Info "推送到远程分支 $currentBranch..."
        git push origin $currentBranch
        
        # 推送标签
        if ($Version) {
            git push origin "v$Version"
            Write-Success "已推送标签到 GitHub"
        }
        
        Write-Success "已提交并推送到 GitHub"
    } else {
        Write-Info "[DRY RUN] 将提交并推送到 GitHub"
    }
} else {
    Write-Warning "跳过 Git 提交"
}

# 5. 发布到 NPM
if (-not $SkipNpm) {
    Write-Info "发布到 NPM..."
    
    if (Test-Path "package.json") {
        if (-not $DryRun) {
            # 检查是否已登录 NPM
            $npmUser = npm whoami 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "未登录 NPM，请先运行 'npm login'"
                $login = Read-Host "是否现在登录? (y/N)"
                if ($login -eq "y") {
                    npm login
                } else {
                    Write-Warning "跳过 NPM 发布"
                    exit 0
                }
            }
            
            Write-Info "当前 NPM 用户: $npmUser"
            
            # 发布
            npm publish --access public
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "已成功发布到 NPM"
            } else {
                Write-Error-Custom "NPM 发布失败"
                exit 1
            }
        } else {
            Write-Info "[DRY RUN] 将发布到 NPM"
        }
    } else {
        Write-Warning "未找到 package.json，跳过 NPM 发布"
    }
} else {
    Write-Warning "跳过 NPM 发布"
}

Write-Success "发布流程完成！"

# 显示摘要
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "发布摘要" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
if ($Version) {
    Write-Host "版本: $Version" -ForegroundColor Green
}
if (-not $SkipTests) {
    Write-Host "测试: 通过 ($totalTests 个)" -ForegroundColor Green
}
if (-not $SkipGit) {
    Write-Host "GitHub: 已推送" -ForegroundColor Green
}
if (-not $SkipNpm) {
    Write-Host "NPM: 已发布" -ForegroundColor Green
}
Write-Host "========================================" -ForegroundColor Cyan
