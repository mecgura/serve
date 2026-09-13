@echo off
echo ========================================
echo   MecGuraServe WhatsApp - Starting...
echo ========================================
echo.
echo URLs:
echo   WhatsApp:    http://127.0.0.1:8000/dashboard/whatsapp/
echo   Superadmin:  http://127.0.0.1:8000/superadmin/
echo.

cd /d "D:\open code\mecguraserve"

REM Wait for server to start then open browser
start "" cmd /c "timeout /t 8 /nobreak >nul && start http://127.0.0.1:8000/dashboard/whatsapp/"

REM Start server
"C:\Users\DeLL\AppData\Local\Programs\Python\Python314\python.exe" manage.py runserver 0.0.0.0:8000

pause
