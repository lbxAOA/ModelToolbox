#!/usr/bin/env pwsh
# Local license checking script for development

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "=== ModelToolbox License Compliance Check ===" -ForegroundColor Cyan
Write-Host ""

# Check Python dependencies
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow

try {
    pip-licenses --version | Out-Null
} catch {
    Write-Host "Installing pip-licenses..." -ForegroundColor Gray
    pip install pip-licenses
}

Write-Host "Python packages:" -ForegroundColor Green
pip-licenses --format=plain-vertical | Select-Object -First 50

# Check for problematic licenses
$pythonCheck = pip-licenses --format=csv | Select-String -Pattern "AGPL|GPL(?!-3\.0)" -SimpleMatch:$false
if ($pythonCheck) {
    Write-Host ""
    Write-Host "❌ Found problematic Python licenses:" -ForegroundColor Red
    $pythonCheck | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    $hasIssues = $true
} else {
    Write-Host "✅ All Python dependencies have acceptable licenses" -ForegroundColor Green
}

Write-Host ""
Write-Host "Checking NPM dependencies..." -ForegroundColor Yellow

if (Test-Path "package.json") {
    try {
        npm list --depth=0 2>&1 | Out-Null
    } catch {
        Write-Host "Installing NPM dependencies..." -ForegroundColor Gray
        npm install
    }
    
    # Show summary
    Write-Host "NPM packages (summary):" -ForegroundColor Green
    npm list --depth=0 | Select-Object -First 20
} else {
    Write-Host "⚠️  No package.json found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking THIRD_PARTY.md status..." -ForegroundColor Yellow

if (Test-Path "THIRD_PARTY.md") {
    $thirdParty = Get-Content "THIRD_PARTY.md" -Raw
    
    # Check for unresolved issues
    if ($thirdParty -match "needs final confirmation") {
        Write-Host "⚠️  THIRD_PARTY.md mentions unresolved license issues" -ForegroundColor Yellow
        $hasIssues = $true
    }
    
    if ($thirdParty -match "legacy.*material") {
        Write-Host "⚠️  Legacy code still referenced in THIRD_PARTY.md" -ForegroundColor Yellow
        $hasIssues = $true
    }
    
    Write-Host "✅ THIRD_PARTY.md exists" -ForegroundColor Green
} else {
    Write-Host "❌ THIRD_PARTY.md not found" -ForegroundColor Red
    $hasIssues = $true
}

Write-Host ""
if ($hasIssues) {
    Write-Host "⚠️  License compliance issues found. Review required." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "✅ License compliance check passed" -ForegroundColor Green
    exit 0
}
