<#
.SYNOPSIS
  Start the continuous playback polling process.

This script will ensure the user is authenticated (runs `auth_local.py` if
no token cache is present), then launch `poll_playback.py`. The Python
process will exit automatically when the cached token expires.

USAGE
  .\scripts\start_polling.ps1         # run continuously
  .\scripts\start_polling.ps1 -Once    # run a single quick iteration (useful for testing)
#>

param(
    [switch]$Once
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location (Resolve-Path "$scriptDir\..")

$cacheFile = Join-Path (Get-Location) ".cache-spotify"
if (-not (Test-Path $cacheFile)) {
    Write-Host "No token cache found. Running authentication..."
    python .\scripts\auth_local.py
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Authentication failed (exit code $LASTEXITCODE). Aborting."
        exit $LASTEXITCODE
    }
}

$maxArg = ""
if ($Once) { $maxArg = "--max-loops=1" }

Write-Host "Starting playback poller..."
python -u .\scripts\poll_playback.py --interval 60 $maxArg
$rc = $LASTEXITCODE
Write-Host "Poller exited with code $rc"
exit $rc
