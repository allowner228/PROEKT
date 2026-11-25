@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Запуск платформы EGE Math...
start /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"
.venv\Scripts\python.exe app.py
pause