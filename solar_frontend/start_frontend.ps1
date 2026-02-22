# =============================================================================
#  SolarGenix - Frontend  (Vite / React / TypeScript - port 5173)
#  Run from Start-Dev.ps1 or standalone: .\solar_frontend\start_frontend.ps1
# =============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- Helpers ------------------------------------------------------------------
function Write-Step  { param([string]$m) Write-Host "`n[-->] $m" -ForegroundColor Cyan    }
function Write-Ok    { param([string]$m) Write-Host "[ OK] $m"  -ForegroundColor Green   }
function Write-Info  { param([string]$m) Write-Host "[   ] $m"  -ForegroundColor White   }
function Write-Fatal { param([string]$m) Write-Host "[ERR] $m"  -ForegroundColor Red; exit 1 }

# -- Resolve paths ------------------------------------------------------------
# The Vite project lives at: solar_frontend/SolarGenix/solar_frontend/solar_frontend/
$SERVICE_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VITE_ROOT    = Join-Path $SERVICE_ROOT "SolarGenix\solar_frontend\solar_frontend"
$NODE_MODULES = Join-Path $VITE_ROOT "node_modules"
$PACKAGE_JSON = Join-Path $VITE_ROOT "package.json"

# -- Banner -------------------------------------------------------------------
Write-Host ""
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host "  SolarGenix - Frontend  (Vite / port 5173)      " -ForegroundColor Magenta
Write-Host "=================================================="  -ForegroundColor Magenta

# -- Guard: ensure Vite project root exists ----------------------------------
if (-not (Test-Path $VITE_ROOT))    { Write-Fatal "Frontend project directory not found at: $VITE_ROOT" }
if (-not (Test-Path $PACKAGE_JSON)) { Write-Fatal "package.json not found at: $PACKAGE_JSON" }

# -- Node.js check -----------------------------------------------------------
Write-Step "Checking Node.js installation..."
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) { Write-Fatal "Node.js is not installed or not in PATH." }
Write-Ok "Node.js $nodeVersion detected."

# -- npm install --------------------------------------------------------------
Write-Step "Checking node_modules..."

if (-not (Test-Path $NODE_MODULES)) {
    Write-Info "node_modules not found - running npm install..."
    Set-Location $VITE_ROOT
    npm install
    if ($LASTEXITCODE -ne 0) { Write-Fatal "npm install failed." }
    Write-Ok "npm install completed."
} else {
    Write-Ok "node_modules already exists - skipping npm install."
}

# -- Start Vite dev server ----------------------------------------------------
Write-Step "Starting Vite development server..."
Set-Location $VITE_ROOT
Write-Host ""
npm run dev
