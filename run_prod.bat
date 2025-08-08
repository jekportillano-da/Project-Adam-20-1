@echo off
echo Starting Production Server (Port 8080)...
echo Authentication required for main routes
echo Access at: http://localhost:8080/
echo Login at: http://localhost:8080/login
echo.
python prod_server.py
pause
