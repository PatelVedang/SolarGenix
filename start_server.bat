@echo off
echo Activating virtual environment...
call "%~dp0venv\Scripts\activate.bat"

echo Starting Django server on port 8000...
cd "%~dp0solar_project"
python manage.py runserver 8000
