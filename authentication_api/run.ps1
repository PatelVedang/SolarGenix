Write-Host "::::::::::::::::::::::::::::::::::::::::::::::::::" -ForegroundColor Cyan
Write-Host ":         SolarGenix Authentication API          :" -ForegroundColor Cyan
Write-Host "::::::::::::::::::::::::::::::::::::::::::::::::::" -ForegroundColor Cyan

# Get script root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

$envPath = Join-Path $scriptPath "app\env"

if (-not (Test-Path $envPath)) {
    Write-Host "[!] Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv app\env
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[X] Failed to create virtual environment." -ForegroundColor Red
        return
    }
    Write-Host "[V] Virtual environment created successfully." -ForegroundColor Green
    
    Write-Host "[*] Installing dependencies from app\requirements.txt..." -ForegroundColor Blue
    & "$envPath\Scripts\Activate.ps1"
    python -m pip install --upgrade pip
    pip install -r app\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[X] Failed to install dependencies." -ForegroundColor Red
        return
    }
    Write-Host "[V] Dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "[V] Virtual environment found." -ForegroundColor Green
    & "$envPath\Scripts\Activate.ps1"
}

# Run server
Set-Location (Join-Path $scriptPath "app")
Write-Host "[*] Running server on port 5000..." -ForegroundColor Yellow
python manage.py runserver 5000
