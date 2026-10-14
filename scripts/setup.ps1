#Requires -Version 7.0
<#
.SYNOPSIS
  One-time local setup: checks tools, creates backend venv, installs deps, seeds .env.
.EXAMPLE
  pwsh ./scripts/setup.ps1
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

function Assert-Command([string]$Name, [string]$Hint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing '$Name'. $Hint"
    }
}

Assert-Command 'python' 'Install Python 3.11+ (winget install Python.Python.3.12).'
Assert-Command 'npm' 'Install Node.js 22 LTS (winget install OpenJS.NodeJS.LTS).'
Assert-Command 'git' 'Install Git (winget install Git.Git).'
if (-not (Get-Command 'ollama' -ErrorAction SilentlyContinue)) {
    Write-Warning "Ollama not found. Install it (winget install Ollama.Ollama) or use 'docker compose --profile ollama up'."
}

$envFile = Join-Path $root '.env'
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $root '.env.example') $envFile
    Write-Host 'Created .env from .env.example' -ForegroundColor Green
}

Push-Location (Join-Path $root 'backend')
try {
    if (-not (Test-Path '.venv')) { python -m venv .venv }
    & ./.venv/Scripts/python.exe -m pip install --upgrade pip --quiet
    & ./.venv/Scripts/python.exe -m pip install -r requirements-dev.txt --quiet
    if ($LASTEXITCODE -ne 0) { throw 'pip install failed' }
    Write-Host 'Backend dependencies installed' -ForegroundColor Green
}
finally { Pop-Location }

Push-Location (Join-Path $root 'frontend')
try {
    npm ci --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw 'npm ci failed' }
    Write-Host 'Frontend dependencies installed' -ForegroundColor Green
}
finally { Pop-Location }

Write-Host "`nNext: ollama pull gemma4 ; pwsh ./scripts/dev.ps1" -ForegroundColor Cyan
