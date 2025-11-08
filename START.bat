@echo off
title File Protector
color 0A

echo ========================================
echo    File Protector - Starting Servers
echo ========================================
echo.

REM Check if backend and frontend folders exist
if not exist "backend" (
    echo ERROR: backend folder not found!
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERROR: frontend folder not found!
    pause
    exit /b 1
)

REM Start Backend Server
echo [1/2] Starting Backend Server...
start "File Protector - Backend" /D backend cmd /k "python api.py"
echo Backend starting...

REM Wait for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend Server
echo [2/2] Starting Frontend Server...
start "File Protector - Frontend" /D frontend cmd /k "npm start"
echo Frontend starting...

echo.
echo ========================================
echo    Servers Started!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Both terminal windows have been opened.
echo Close this window when done.
echo.
echo Press any key to open frontend in browser...
pause >nul
start http://localhost:3000

echo.
echo.
echo To stop the servers, close the terminal windows.
echo.
pause

