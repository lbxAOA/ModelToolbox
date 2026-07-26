[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Message,

    [switch]$AllowLargeDeletion,

    [switch]$NoPush,

    [string]$RemoteBranch = "main",

    [string]$AuthorName = "lbxAOA",

    [string]$AuthorEmail = "255046545+lbxAOA@users.noreply.github.com"
)

$ErrorActionPreference = "Stop"

function Invoke-Git {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
    }
}

$repo = (& git rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or -not $repo) {
    throw "Run this script inside a Git repository."
}

Push-Location $repo
try {
    $branch = (& git branch --show-current).Trim()
    if (-not $branch) {
        throw "The repository is in detached HEAD state. Refusing to commit."
    }

    Write-Host "Repository: $repo"
    Write-Host "Branch: $branch"
    Write-Host "Author: $AuthorName <$AuthorEmail>"

    Invoke-Git @("add", "--all")

    $stagedNames = @(git diff --cached --name-only --diff-filter=ACDMRTUXB)
    if ($stagedNames.Count -eq 0) {
        throw "No changes are staged after git add --all."
    }

    $deletedCount = @(git diff --cached --name-only --diff-filter=D).Count

    if ($deletedCount -gt 5 -and -not $AllowLargeDeletion) {
        throw "Refusing to commit $deletedCount deleted files. Re-run with -AllowLargeDeletion after reviewing the staged diff."
    }

    $sensitive = @(
        git diff --cached --name-only --diff-filter=ACMRTUXB | Where-Object {
            $_ -match "(^|/)(\.env($|\.)|.*\.pem$|.*\.key$|secrets\.json$|.*obsidian-local-rest-api/data\.json$)"
        }
    )
    if ($sensitive.Count -gt 0) {
        throw "Refusing to commit sensitive-looking files: $($sensitive -join ', ')"
    }

    Invoke-Git @("diff", "--cached", "--check")
    Write-Host "Staged files: $($stagedNames.Count)"
    Write-Host "Deleted files: $deletedCount"

    $commitArgs = @(
        "-c", "user.name=$AuthorName",
        "-c", "user.email=$AuthorEmail",
        "commit", "-m", $Message,
        "--author", "$AuthorName <$AuthorEmail>"
    )
    Invoke-Git $commitArgs

    if (-not $NoPush) {
        & git ls-remote --exit-code --heads origin $RemoteBranch *> $null
        if ($LASTEXITCODE -ne 0) {
            throw "Remote branch origin/$RemoteBranch does not exist. Refusing to create a new branch."
        }
        Invoke-Git @("push", "origin", "HEAD:$RemoteBranch")
    }
}
finally {
    Pop-Location
}