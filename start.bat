@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: 🎨 Цвета (ANSI-коды, работают в Windows Terminal / PowerShell)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "NC=[0m"

:: 📁 Пути
set "PROJECT_DIR=%CD%"
set "SCRIPTS_DIR=%PROJECT_DIR%\scripts"
set "VENV_DIR=%PROJECT_DIR%\venv"
set "SITE_DIR=%PROJECT_DIR%\site"
set "LOG_DIR=%PROJECT_DIR%\logs"
set "VPS=86.110.194.68"
set "SSH_KEY=%USERPROFILE%\.ssh\kb_vps"

mkdir "%LOG_DIR%" 2>nul

:: 📊 Прогресс-бар (упрощённый для CMD)
set /a TOTAL_STEPS=10
set /a CURRENT_STEP=0

:progress
set /a CURRENT_STEP+=1
set /a PCT=CURRENT_STEP*100/TOTAL_STEPS
set "BAR="
for /l %%i in (1,1,20) do (
    if %%i leq !PCT! / 5 (set "BAR=!BAR!#") else (set "BAR=!BAR!-")
)
<nul set /p "=🔄 [!BAR!] !PCT!%% | %~1 "
goto :eof

:log_ok
echo.
echo %GREEN%✅ %~1%NC%
goto :eof

:log_warn
echo.
echo %YELLOW%⚠️  %~1%NC%
goto :eof

:log_err
echo.
echo %RED%❌ %~1%NC%
exit /b 1
goto :eof

:: 🧹 Очистка при выходе
:cleanup
echo.
echo %YELLOW%🛑 Остановка...%NC%
if exist "%PROJECT_DIR%\stop.bat" (
    call "%PROJECT_DIR%\stop.bat"
)
exit /b

:: Перехват сигналов (Ctrl+C, закрытие окна)
trap cleanup 2>nul || (
    :: Fallback для CMD: просто вызываем stop.bat при выходе
)

:: 🚀 ГЛАВНЫЙ ЗАПУСК
echo %CYAN%╔════════════════════════╗%NC%
echo %CYAN%║  🚀 Запуск KB          ║%NC%
echo %CYAN%╚════════════════════════╝%NC%
echo.

:: 0. Очистка портов
call :progress "Очистка..."
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill //PID %%a //F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :25000 ^| findstr LISTENING') do taskkill //PID %%a //F >nul 2>&1
timeout /t 1 /nobreak >nul
call :log_ok "Порты очищены"

:: 1. Туннели
call :progress "Туннель..."
taskkill /f /im ssh.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: Запуск туннелей в фоне
start /min "Tunnel-API" ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no -R 0.0.0.0:8000:localhost:8000 -N -o ServerAliveInterval=30 root@%VPS%
start /min "Tunnel-WH" ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no -R 0.0.0.0:25000:localhost:25000 -N -o ServerAliveInterval=30 root@%VPS%

:: Ждём подключения (до 15 сек)
for /l %%i in (1,1,15) do (
    ssh -i "%SSH_KEY%" root@%VPS% "netstat -ano 2>nul | findstr :8000" >nul 2>&1 && ^
    ssh -i "%SSH_KEY%" root@%VPS% "netstat -ano 2>nul | findstr :25000" >nul 2>&1 && goto :tunnels_ready
    timeout /t 1 /nobreak >nul
)
:tunnels_ready
ssh -i "%SSH_KEY%" root@%VPS% "netstat -ano 2>nul | findstr :8000" >nul 2>&1 && call :log_ok "API-туннель" || call :log_warn "API-туннель"
ssh -i "%SSH_KEY%" root@%VPS% "netstat -ano 2>nul | findstr :25000" >nul 2>&1 && call :log_ok "Webhook-туннель" || call :log_warn "Webhook-туннель"

:: 2. Qdrant
call :progress "Qdrant..."
docker ps --format "{{.Names}}" 2>nul | findstr "qdrant" >nul 2>&1
if !errorlevel! equ 0 (
    call :log_ok "Qdrant запущен"
) else (
    docker run -d --name qdrant -p 6333:6333 --restart unless-stopped qdrant/qdrant >nul 2>&1
    timeout /t 2 /nobreak >nul
    call :log_ok "Qdrant запущен"
)

:: 3. Ollama
call :progress "Ollama..."
curl.exe -sf http://localhost:11434/api/tags >nul 2>&1 && call :log_ok "Ollama готов" || call :log_warn "Ollama не отвечает"

:: 4. Python venv + зависимости
call :progress "Python..."
if not exist "%VENV_DIR%\Scripts\python.exe" (
    call :log_warn "⚠️  venv не найден — создаю..."
    rmdir /s /q "%VENV_DIR%" 2>nul
    python -m venv "%VENV_DIR%"
)

set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "PIP=%VENV_DIR%\Scripts\pip.exe"
if not exist "%PIP%" set "PIP=%VENV_DIR%\Scripts\pip3.exe"

if not exist "%PYTHON%" (
    call :log_err "❌ Python в venv не найден!"
    exit /b 1
)

:: Обновление pip и установка зависимостей (тихо)
"%PIP%" install -q --upgrade pip setuptools wheel >nul 2>&1
echo.
"%PIP%" install -q -r "%PROJECT_DIR%\requirements.txt" 2>&1 | findstr /v "Requirement already satisfied" && call :log_ok "Зависимости установлены" || call :log_warn "⚠️  pip install завершён с предупреждениями"

:: 5. Синхронизация
call :progress "Синхронизация..."
cd /d "%PROJECT_DIR%"
"%PYTHON%" "%SCRIPTS_DIR%\sync.py" >> "%LOG_DIR%\start.log" 2>&1
if !errorlevel! equ 0 (call :log_ok "Данные синхронизированы") else (call :log_warn "sync.py упал — см. %LOG_DIR%\start.log")

:: 6. Индексация
call :progress "Индексация..."
cd /d "%PROJECT_DIR%"
"%PYTHON%" "%SCRIPTS_DIR%\ingest.py" >> "%LOG_DIR%\start.log" 2>&1
if !errorlevel! equ 0 (call :log_ok "База проиндексирована") else (call :log_warn "ingest.py упал — см. %LOG_DIR%\start.log")

:: 7. Сборка фронтенда
call :progress "Сборка..."
cd /d "%SITE_DIR%"
call npm run build --silent 2>&1 | findstr /v "Requirement" && call :log_ok "Build завершён" || call :log_warn "npm build упал"

:: 8. Деплой (scp вместо rsync)
call :progress "Деплой..."
cd /d "%SITE_DIR%"
if exist "docs\.vitepress\dist\" (
    scp -q -r "docs\.vitepress\dist\*" root@%VPS%:/var/www/swinki.ru/dist/ 2>&1 | findstr /v "Uploading" && call :log_ok "Фронтенд задеплоен" || call :log_warn "scp не удался"
)

:: 9. Запуск API (Waitress для Windows — Gunicorn не работает на Win)
call :progress "Запуск API..."
echo.

:: 🔥 Waitress — официальный WSGI-сервер для Windows
set "WAITRESS_CMD=cd /d "%SCRIPTS_DIR%" && call "%VENV_DIR%\Scripts\activate.bat" && "%VENV_DIR%\Scripts\waitress-serve.exe" --listen=*:8000 --threads=4 --channel-timeout=300 api:app"

start "🔙 API (Waitress)" cmd /k "%WAITRESS_CMD%"
timeout /t 2 /nobreak >nul

:: Проверка
curl.exe -sf http://localhost:8000/health >nul 2>&1 && call :log_ok "API запущен (Waitress)" || call :log_warn "API не отвечает"

:: 10. Запуск Webhook
call :progress "Запуск Webhook..."
if exist "%SCRIPTS_DIR%\webhook-listener.py" (
    set "WEBHOOK_CMD=cd /d "%PROJECT_DIR%" && call "%VENV_DIR%\Scripts\activate.bat" && python "%SCRIPTS_DIR%\webhook-listener.py""
    start "📡 Webhook" cmd /k "%WEBHOOK_CMD%"
    call :log_ok "Webhook запущен"
) else (
    call :log_warn "webhook-listener.py не найден"
)

:: === 🎉 ФИНАЛ ===
echo.
echo %GREEN%╔════════════════════════╗%NC%
echo %GREEN%║  🎉 Готово!            ║%NC%
echo %GREEN%╚════════════════════════╝%NC%
echo 🌐 %CYAN%https://swinki.ru%NC%
echo 🤖 %CYAN%http://localhost:8000%NC%
echo 🎣 %CYAN%http://localhost:25000%NC%
echo %YELLOW%💡 Закройте окна терминалов или запустите stop.bat для остановки%NC%

:: 🔥 Оставляем окно открытым
pause >nul