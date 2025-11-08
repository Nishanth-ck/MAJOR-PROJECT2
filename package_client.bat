@echo off
echo ========================================
echo Packaging Desktop Client for Distribution
echo ========================================
echo.

REM Create dist folder if it doesn't exist
if not exist "dist" mkdir dist

REM Create platform-specific packages
echo Creating Windows package...
if exist "dist\file-protector-client-windows.zip" del "dist\file-protector-client-windows.zip"
powershell -Command "Compress-Archive -Path desktop_client\* -DestinationPath dist\file-protector-client-windows.zip -Force"
echo ✓ Windows package created: dist\file-protector-client-windows.zip

echo.
echo Creating macOS/Linux package...
if exist "dist\file-protector-client-macos.zip" del "dist\file-protector-client-macos.zip"
powershell -Command "Compress-Archive -Path desktop_client\* -DestinationPath dist\file-protector-client-macos.zip -Force"
if exist "dist\file-protector-client-linux.zip" del "dist\file-protector-client-linux.zip"
copy "dist\file-protector-client-macos.zip" "dist\file-protector-client-linux.zip" >nul
echo ✓ macOS/Linux packages created

echo.
echo ========================================
echo Packaging Complete!
echo ========================================
echo.
echo Packages created in 'dist' folder:
echo   - file-protector-client-windows.zip
echo   - file-protector-client-macos.zip
echo   - file-protector-client-linux.zip
echo.
echo Next steps:
echo   1. Upload these ZIP files to GitHub Releases
echo   2. Or host them in your public folder and update Download.js
echo   3. Update Download.js with the correct download URLs
echo.
pause

