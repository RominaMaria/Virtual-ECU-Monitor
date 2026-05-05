@echo off
:: Move the command context to the project root
cd /d "%~dp0.."

echo [1/3] Stopping old ECU instances...
docker stop ecu_monitor_live >nul 2>&1
docker rm ecu_monitor_live >nul 2>&1

echo [2/3] Building and Starting ECU System...
:: Now it will find the Dockerfile correctly
docker build -t ecu-monitor-system .
docker run -d -p 8000:8000 --name ecu_monitor_live ecu-monitor-system

echo [3/3] Opening Dashboard...
timeout /t 3
:: Open the API to check the JSON
start http://localhost:8000/sensor-data
:: Open the Dashboard file
start frontend/index.html

echo.
echo ========================================
echo ECU Monitor System is now ACTIVE
echo ========================================
pause