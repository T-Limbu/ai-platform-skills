# Pull newly added or edited skills from local Antigravity runtime back to Git repository
$ErrorActionPreference = "Stop"

$repoSkillsDir = $PSScriptRoot
$localSkillsDir = Join-Path $env:USERPROFILE ".gemini\config\skills"

if (-not (Test-Path $localSkillsDir)) {
    Write-Host "Local skills directory not found: $localSkillsDir" -ForegroundColor Red
    exit 1
}

$localDirs = Get-ChildItem -Path $localSkillsDir -Directory

Write-Host "Pulling $($localDirs.Count) skills from $localSkillsDir to repository..." -ForegroundColor Cyan

foreach ($dir in $localDirs) {
    $target = Join-Path $repoSkillsDir $dir.Name
    Copy-Item -Path $dir.FullName -Destination $target -Recurse -Force
    Write-Host "  -> Pulled $($dir.Name)" -ForegroundColor Green
}

Write-Host "Done! Git repository has latest skills from local runtime." -ForegroundColor Green
