# Synchronize repository skills to local Antigravity runtime
$ErrorActionPreference = "Stop"

$repoSkillsDir = $PSScriptRoot
$localSkillsDir = Join-Path $env:USERPROFILE ".gemini\config\skills"

if (-not (Test-Path $localSkillsDir)) {
    New-Item -ItemType Directory -Path $localSkillsDir -Force | Out-Null
}

$skillDirs = Get-ChildItem -Path $repoSkillsDir -Directory | Where-Object { $_.Name -notin @('.git', '.github', 'node_modules') }

Write-Host "Syncing $($skillDirs.Count) skills from repository to $localSkillsDir..." -ForegroundColor Cyan

foreach ($dir in $skillDirs) {
    $target = Join-Path $localSkillsDir $dir.Name
    Copy-Item -Path $dir.FullName -Destination $target -Recurse -Force
    Write-Host "  -> Synced $($dir.Name)" -ForegroundColor Green
}

Write-Host "Done! Antigravity skills are up to date." -ForegroundColor Green
