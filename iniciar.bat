@echo off
title Bot MEGA ERP - Iniciador
chcp 65001 >nul

:: ============================================
:: VERIFICAR ADMINISTRADOR
:: ============================================
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %errorlevel% neq 0 (
    echo Este script requer privilegios de administrador.
    echo Reiniciando como administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ========================================
echo    Iniciando automacao MEGA ERP...
echo    (Certifique-se de que o MEGA esta
echo     aberto e no campo desejado)
echo ========================================
echo.

cd /d "%~dp0"
python auto.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] O script encontrou um problema.
) else (
    echo.
    echo Automacao concluida com sucesso!
)

echo.
pause
