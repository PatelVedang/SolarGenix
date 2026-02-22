# =============================================================================
#  SolarGenix - Prediction API  (Django - port 8000)
#  Run from Start-Dev.ps1 or standalone: .\prediction_api\start_server.ps1
# =============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- Helpers ------------------------------------------------------------------
function Write-Step  { param([string]$m) Write-Host "`n[-->] $m" -ForegroundColor Cyan   }
function Write-Ok    { param([string]$m) Write-Host "[ OK] $m"  -ForegroundColor Green  }
function Write-Info  { param([string]$m) Write-Host "[   ] $m"  -ForegroundColor White  }
function Write-Fatal { param([string]$m) Write-Host "[ERR] $m"  -ForegroundColor Red; exit 1 }

# -- Resolve paths ------------------------------------------------------------
$SERVICE_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VENV_DIR     = Join-Path $SERVICE_ROOT "venv"
$ACTIVATE     = Join-Path $VENV_DIR "Scripts\Activate.ps1"
$PROJECT_DIR  = Join-Path $SERVICE_ROOT "solar_project"
$REQUIREMENTS = Join-Path $PROJECT_DIR "requirements.txt"
$PORT         = 8000

# -- Banner -------------------------------------------------------------------
Write-Host ""
Write-Host "==================================================" -ForegroundColor Yellow
Write-Host "  SolarGenix - Prediction API  (port $PORT)      " -ForegroundColor Yellow
Write-Host "=================================================="  -ForegroundColor Yellow

# -- Guard: ensure project directory exists ---------------------------------
if (-not (Test-Path $PROJECT_DIR)) { Write-Fatal "solar_project/ directory not found at: $PROJECT_DIR" }

# -- Virtual environment -----------------------------------------------------
Write-Step "Checking virtual environment..."

if (-not (Test-Path $VENV_DIR)) {
    Write-Info "venv not found - creating at: $VENV_DIR"
    python -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) { Write-Fatal "Failed to create virtual environment." }
    Write-Ok "Virtual environment created."
} else {
    Write-Ok "Virtual environment already exists - skipping creation."
}

# -- Activate -----------------------------------------------------------------
Write-Step "Activating virtual environment..."
& $ACTIVATE
Write-Ok "venv activated."

# -- Dependencies -------------------------------------------------------------
Write-Step "Checking dependencies..."

if (-not (Test-Path $REQUIREMENTS)) { Write-Fatal "requirements.txt not found at: $REQUIREMENTS" }

$sitePackages   = Join-Path $VENV_DIR "Lib\site-packages"
$installedCount = (Get-ChildItem -Path $sitePackages -Directory -ErrorAction SilentlyContinue | Measure-Object).Count

if ($installedCount -le 2) {
    Write-Info "Installing dependencies from requirements.txt..."
    python -m pip install --upgrade pip --quiet
    pip install -r $REQUIREMENTS
    if ($LASTEXITCODE -ne 0) { Write-Fatal "pip install failed." }
    Write-Ok "Dependencies installed."
} else {
    Write-Ok "Dependencies already present ($installedCount packages) - skipping install."
}

# -- Start server -------------------------------------------------------------
Write-Step "Starting Prediction API on port $PORT..."
Set-Location $PROJECT_DIR
Write-Host ""
python manage.py runserver $PORT
