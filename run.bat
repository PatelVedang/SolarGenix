@echo off
setlocal enabledelayedexpansion

echo ::::::::::::::::::::::::::::::::::::::::::::::::::
echo :         SolarGenix Authentication API          :
echo ::::::::::::::::::::::::::::::::::::::::::::::::::

cd /d "%~dp0"

IF NOT EXIST "app\env" (
    echo [!] Virtual environment not found. Creating one...
    python -m venv app\env
    IF !ERRORLEVEL! NEQ 0 (
        echo [X] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [V] Virtual environment created successfully.
    
    echo [*] Installing dependencies from app\requirements.txt...
    call app\env\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r app\requirements.txt
    IF !ERRORLEVEL! NEQ 0 (
        echo [X] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [V] Dependencies installed successfully.
) ELSE (
    echo [V] Virtual environment found.
    call app\env\Scripts\activate
)

echo [*] Navigating to app directory...
cd app

echo [*] Running server on port 5000...
python manage.py runserver 5000

pause
