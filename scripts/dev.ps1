#Requires -Version 7.0
<#
.SYNOPSIS
  Runs backend (uvicorn --reload, :8000) and frontend (vite, :5173) together. Ctrl+C stops both.
.EXAMPLE
  pwsh ./scripts/dev.ps1
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root 'backend/.venv/Scripts/python.exe'
if (-not (Test-Path $python)) { throw 'Backend venv missing. Run ./scripts/setup.ps1 first.' }

$backend = Start-Process -FilePath $python `
    -ArgumentList '-m', 'uvicorn', 'app.main:app', '--reload', '--port', '8000' `
    -WorkingDirectory (Join-Path $root 'backend') -NoNewWindow -PassThru

try {
    Push-Location (Join-Path $root 'frontend')
    npm run dev
}
finally {
    Pop-Location
    if ($backend -and -not $backend.HasExited) {
        # uvicorn --reload spawns a child worker; kill the whole tree.
        taskkill /PID $backend.Id /T /F | Out-Null
    }
}
