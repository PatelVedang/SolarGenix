@echo off
set "VENV_DIR=%~dp0venv"

if not exist "%VENV_DIR%" (
    echo Virtual environment not found. Creating one...
    python -m venv "%VENV_DIR%"
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment. Please ensure Python is installed and in your PATH.
        pause
        exit /b %ERRORLEVEL%
    )
    
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
    
    echo Installing dependencies from requirements.txt...
    python -m pip install --upgrade pip
    pip install -r "%~dp0solar_project\requirements.txt"
    if %ERRORLEVEL% neq 0 (
        echo Failed to install dependencies.
        pause
        exit /b %ERRORLEVEL%
    )
) else (
    echo Virtual environment found. Activating...
    call "%VENV_DIR%\Scripts\activate.bat"
)

echo Starting Django server on port 8000...
cd "%~dp0solar_project"
python manage.py runserver 8000
