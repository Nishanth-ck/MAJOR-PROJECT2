@echo off
echo ========================================
echo   File Protector - Setup Wizard
echo ========================================
echo.

REM Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo Python found!
echo.

REM Check Node.js
echo [2/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js 14 or higher from https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo Node.js found!
echo.

REM Install Backend Dependencies
echo [3/4] Installing backend dependencies...
cd backend
if exist requirements.txt (
    pip install -r requirements.txt
    echo Backend dependencies installed!
) else (
    echo WARNING: requirements.txt not found in backend folder
)
cd ..
echo.

REM Install Frontend Dependencies
echo [4/4] Installing frontend dependencies...
cd frontend
if exist package.json (
    call npm install
    echo Frontend dependencies installed!
) else (
    echo WARNING: package.json not found in frontend folder
)
cd ..
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Update MongoDB connection in backend/api.py
echo 2. Update MongoDB connection in backend/file_protector2.py
echo 3. Run: backend\python api.py
echo 4. Run: frontend\npm start
echo 5. Open: http://localhost:3000
echo.
echo For detailed instructions, see USER_GUIDE.md
echo.
pause

