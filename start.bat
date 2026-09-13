@echo off
echo ========================================
echo   MecGuraServe - Quick Start
echo ========================================
echo.

echo [1] Installing requirements...
py -m pip install -r requirements.txt

echo.
echo [2] Running migrations...
py manage.py migrate

echo.
echo [3] Running setup script...
py setup.py

echo.
echo ========================================
echo   Starting Server...
echo ========================================
echo.
echo   Superadmin: http://localhost:8000/superadmin/login/
echo   Grand Resort: http://localhost:8000/dashboard/admin/?tenant=grand-resort
echo.
echo   Login: admin / admin123
echo.
py manage.py runserver

pause
