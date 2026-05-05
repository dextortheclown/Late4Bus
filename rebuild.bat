@echo off
echo Cleaning previous build...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist installer_output rd /s /q installer_output

echo Building exe...
pyinstaller Late4Bus.spec
if errorlevel 1 (
    echo PyInstaller build failed.
    pause
    exit /b 1
)

echo Building installer...
if not exist installer_output mkdir installer_output
"G:\Inno Setup 6\ISCC.exe" installer.iss
if errorlevel 1 (
    echo Inno Setup build failed.
    pause
    exit /b 1
)

echo Done. Installer output in installer_output\
pause