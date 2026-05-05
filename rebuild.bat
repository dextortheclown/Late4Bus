@echo off
rd /s /q build
rd /s /q dist
del /f /q "%APPDATA%\Late4Bus\config.json"
pyinstaller Late4Bus.spec
pause