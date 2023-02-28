@echo off
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
echo Please select the option
echo Start : 1 
echo Restart : 2
echo Stop : 3
echo Delete : 4
echo.
echo.

set /p option=
echo You have entered : %option%
echo.
echo.
if "%option%"=="1" (
    echo Starting the app and worker
    echo.
    echo.
    echo.
    call "env\Scripts\activate.bat"
    cd app
    concurrently "pm2 start celery --name worker --max-memory-restart \"200M\" -- --app proj worker --pool=gevent --concurrency=10 --loglevel=info" "pm2 start manage.py --name cyber_appliance --max-memory-restart \"100M\" --no-autorestart -- runserver 0.0.0.0:8000"
    cd ..
    call "env\Scripts\deactivate.bat"
    echo.
    echo.
    echo.
    echo Job Done!!!!
) else if "%option%"=="2" (
    echo Restarting the app and worker
    echo.
    echo.
    echo.
    concurrently "pm2 restart cyber_appliance" "pm2 restart worker"
    echo.
    echo.
    echo.
    echo Job Done!!!!

) else if "%option%"=="3" (
    echo Stopping the app and worker
    echo.
    echo.
    echo.
    concurrently "pm2 stop cyber_appliance" "pm2 stop worker"
    echo.
    echo.
    echo.
    echo Job Done!!!!
) else if "%option%"=="4" (
    echo Deleting the app and worker
    echo.
    echo.
    echo.
    concurrently "pm2 delete cyber_appliance" "pm2 delete worker"
    echo.
    echo.
    echo.
    echo Job Done!!!!
) else (
    echo Wrong Choice!!! Try Again!!
)