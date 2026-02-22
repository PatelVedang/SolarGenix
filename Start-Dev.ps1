# =============================================================================
#  SolarGenix — Development Environment Orchestrator
#  Run this script from the root of the SolarGenix repository.
#  It opens three separate PowerShell windows, one per service.
# =============================================================================

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- Resolve absolute root so relative paths are safe regardless of CWD -----────
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition

# ── Colour helpers ─────────────────────────────────────────────────────────────
function Write-Step  { param([string]$msg) Write-Host "`n[-->] $msg" -ForegroundColor Cyan   }
function Write-Ok    { param([string]$msg) Write-Host "[ OK] $msg"  -ForegroundColor Green  }
function Write-Warn  { param([string]$msg) Write-Host "[!!!] $msg"  -ForegroundColor Yellow }
function Write-Fatal { param([string]$msg) Write-Host "[ERR] $msg"  -ForegroundColor Red    }

# -- Verify required service scripts exist before spawning anything ----------
function Assert-Script {
    param([string]$path, [string]$label)
    if (-not (Test-Path $path)) {
        Write-Fatal "Service script not found for $label : $path"
        exit 1
    }
}

# -- Spawn a new PowerShell window for a service script ----------------------
function Start-ServiceWindow {
    param(
        [string]$Title,
        [string]$ScriptPath
    )

    Write-Step "Launching service window: $Title"

    # -NoExit keeps the window open so you can see logs after the process ends.
    $args = @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", "& { `$Host.UI.RawUI.WindowTitle = '$Title'; & '$ScriptPath' }"
    )

    Start-Process -FilePath "powershell.exe" -ArgumentList $args
    Write-Ok "$Title window opened."
}

# =============================================================================
#  BANNER
# =============================================================================
Write-Host ""
Write-Host "##############################################################" -ForegroundColor Magenta
Write-Host "#                                                            #" -ForegroundColor Magenta
Write-Host "#               SolarGenix  -  Dev Startup                  #" -ForegroundColor Magenta
Write-Host "#                                                            #" -ForegroundColor Magenta
Write-Host "##############################################################" -ForegroundColor Magenta
Write-Host ""

# =============================================================================
#  SERVICE SCRIPT PATHS  (update these if you move folders)
# =============================================================================
$AUTH_SCRIPT     = Join-Path $ROOT "authentication_api\run.ps1"
$PRED_SCRIPT     = Join-Path $ROOT "prediction_api\start_server.ps1"
$FRONTEND_SCRIPT = Join-Path $ROOT "solar_frontend\start_frontend.ps1"

Assert-Script $AUTH_SCRIPT     "authentication_api"
Assert-Script $PRED_SCRIPT     "prediction_api"
Assert-Script $FRONTEND_SCRIPT "solar_frontend"

# =============================================================================
#  LAUNCH ALL THREE SERVICES
# =============================================================================
Start-ServiceWindow -Title "SolarGenix | Auth API  (port 5000)" -ScriptPath $AUTH_SCRIPT
Start-Sleep -Milliseconds 800          # small stagger so windows don't collide

Start-ServiceWindow -Title "SolarGenix | Prediction API  (port 8000)" -ScriptPath $PRED_SCRIPT
Start-Sleep -Milliseconds 800

Start-ServiceWindow -Title "SolarGenix | Frontend  (Vite / port 5173)" -ScriptPath $FRONTEND_SCRIPT

# =============================================================================
#  SUMMARY
# =============================================================================
Write-Host ""
Write-Host "------------------------------------------------------------" -ForegroundColor Magenta
Write-Host "  All service windows launched." -ForegroundColor Green
Write-Host ""
Write-Host "  Auth API       ->  http://localhost:5000" -ForegroundColor Cyan
Write-Host "  Prediction API ->  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Frontend       ->  http://localhost:5173" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Magenta
Write-Host ""
