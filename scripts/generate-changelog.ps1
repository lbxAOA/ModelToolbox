# ModelToolbox 更新日志生成脚本
# 功能：从 Git 提交历史生成 CHANGELOG.md

param(
    [Parameter(Mandatory=$false)]
    [string]$FromTag = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ToTag = "HEAD",
    
    [Parameter(Mandatory=$false)]
    [string]$Output = "CHANGELOG.md"
)

$ErrorActionPreference = "Stop"

function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }

$rootDir = "c:\ModelToolbox"
Set-Location $rootDir

Write-Info "生成更新日志..."

# 获取标签列表
$tags = git tag --sort=-version:refname
if (-not $FromTag -and $tags) {
    $FromTag = $tags[0]
}

# 获取提交历史
$range = if ($FromTag) { "$FromTag..$ToTag" } else { $ToTag }
$commits = git log $range --pretty=format:"%H|%s|%an|%ad" --date=short

# 分类提交
$changelog = @{
    "feat" = @()
    "fix" = @()
    "docs" = @()
    "style" = @()
    "refactor" = @()
    "test" = @()
    "chore" = @()
    "perf" = @()
    "ci" = @()
    "build" = @()
    "revert" = @()
    "other" = @()
}

foreach ($commit in $commits) {
    if (-not $commit) { continue }
    
    $parts = $commit -split "\|"
    $hash = $parts[0].Substring(0, 7)
    $message = $parts[1]
    $author = $parts[2]
    $date = $parts[3]
    
    # 解析提交类型
    if ($message -match "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.*?\))?:\s*(.*)") {
        $type = $matches[1]
        $scope = $matches[2]
        $subject = $matches[3]
        
        $changelog[$type] += @{
            hash = $hash
            scope = $scope
            subject = $subject
            author = $author
            date = $date
        }
    } else {
        $changelog["other"] += @{
            hash = $hash
            subject = $message
            author = $author
            date = $date
        }
    }
}

# 生成 Markdown
$markdown = @"
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"@

# 添加各类型的提交
$typeNames = @{
    "feat" = "✨ Features"
    "fix" = "🐛 Bug Fixes"
    "docs" = "📝 Documentation"
    "style" = "💄 Styles"
    "refactor" = "♻️ Code Refactoring"
    "perf" = "⚡ Performance Improvements"
    "test" = "✅ Tests"
    "build" = "📦 Build System"
    "ci" = "👷 CI/CD"
    "chore" = "🔧 Chores"
    "revert" = "⏪ Reverts"
}

foreach ($type in $changelog.Keys) {
    $commits = $changelog[$type]
    if ($commits.Count -eq 0) { continue }
    
    $typeName = if ($typeNames.ContainsKey($type)) { $typeNames[$type] } else { "Other" }
    $markdown += "`n### $typeName`n`n"
    
    foreach ($commit in $commits) {
        $scope = if ($commit.scope) { " **$($commit.scope.Trim('()'))**: " } else { ": " }
        $markdown += "- $($commit.subject)$scope ([$($commit.hash)](https://github.com/yourusername/ModelToolbox/commit/$($commit.hash)))`n"
    }
}

# 保存到文件
if (Test-Path $Output) {
    # 如果文件已存在，插入到现有内容前面
    $existing = Get-Content $Output -Raw
    
    # 找到第一个版本标题的位置
    if ($existing -match "(## \[[\d\.]+\])") {
        $insertPos = $existing.IndexOf($matches[1])
        $markdown = $markdown + "`n" + $existing.Substring($insertPos)
        $header = $existing.Substring(0, $insertPos)
        $markdown = $header + $markdown
    } else {
        $markdown = $markdown + "`n`n" + $existing
    }
}

Set-Content $Output $markdown -Encoding UTF8

Write-Success "更新日志已生成: $Output"
Write-Info "请手动编辑并添加版本号和日期"
