@echo off
echo [INFO] Checking for mod updates...

:: Run the Python validator using PowerShell from configs\
powershell -Command "py '.\configs\Mod Version validator.py'"

echo [INFO] Starting Arma Reforger Server...
ArmaReforgerServer.exe -config ".\configs\config.json"
