@echo off
cls
echo.
echo.
echo.
echo   ____      _                    _                _ _                      
echo  / ___^|   _^| ^|__   ___ _ __     / \   _ __  _ __ ^| (_) __ _ _ __   ___ ___ 
echo ^| ^|  ^| ^| ^| ^| '_ \ / _ \ '__^|   / _ \ ^| '_ \^| '_ \^| ^| ^|/ _\` ^| '_ \ / __/ _ \
echo ^| ^|__^| ^|_^| ^| ^|_) ^|  __/ ^|     / ___ \^| ^|_) ^| ^|_) ^| ^| ^| (_^| ^| ^| ^| ^| (_^|  __/
echo  \____\__, ^|_.__/ \___^|_^|    /_/   \_\ .__/^| .__/^|_^|_^|\__,_^|_^| ^|_^|\___\___^|
echo       ^|___/                          ^|_^|   ^|_^|                             
echo.
echo.
echo.
echo Running the test cases
echo.
echo.
echo.
rem Activate the virtual environment
call "env\Scripts\activate.bat"
cd app
python manage.py test
cd ..
rem De-activate the virtual environment
call "env\Scripts\deactivate.bat"
echo Job Done!!!!