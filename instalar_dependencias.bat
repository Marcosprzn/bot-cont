@echo off
title Bot MEGA ERP - Instalador de Dependencias
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
echo    Instalador de Dependencias - MEGA ERP
echo ========================================
echo.

:: ============================================
:: VERIFICAR WINDOWS ARCH (32 ou 64 bits)
:: ============================================
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" set ARCH=64
if "%PROCESSOR_ARCHITECTURE%"=="x86" set ARCH=86
if "%PROCESSOR_ARCHITECTURE%"=="ARM64" set ARCH=64
echo Arquitetura detectada: %ARCH% bits
echo.

:: ============================================
:: VERIFICAR SE PYTHON ESTA INSTALADO
:: ============================================
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python --version
    echo Python ja instalado.
    goto INSTALL_DEPS
)

echo Python nao encontrado. Instalando Python 3.11.8...
echo.

:: ============================================
:: BAIXAR PYTHON 3.11.8
:: ============================================
set "PYTHON_URL_64=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
set "PYTHON_URL_86=https://www.python.org/ftp/python/3.11.8/python-3.11.8.exe"
set "INSTALLER=%TEMP%\python-3.11.8-installer.exe"

if "%ARCH%"=="64" (
    echo Baixando Python 64-bit...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL_64%' -OutFile '%INSTALLER%' -UseBasicParsing"
) else (
    echo Baixando Python 32-bit...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL_86%' -OutFile '%INSTALLER%' -UseBasicParsing"
)

if not exist "%INSTALLER%" (
    echo.
    echo [ERRO] Falha ao baixar o instalador do Python.
    echo Verifique sua conexao com internet.
    pause
    exit /b 1
)

echo Instalando Python (aguarde, pode levar alguns minutos)...
echo.
start /wait "" "%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

:: Verificar se instalou
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha na instalacao do Python.
    echo Tente reiniciar o script ou instalar manualmente em: python.org
    pause
    exit /b 1
)

echo Python instalado com sucesso!
python --version

:: ============================================
:: INSTALAR DEPENDENCIAS
:: ============================================
:INSTALL_DEPS
echo.
echo Instalando dependencias (pywinauto, pyautogui, keyboard)...
python -m pip install --upgrade pip --quiet
python -m pip install pywinauto --quiet
python -m pip install pyautogui --quiet
python -m pip install keyboard --quiet

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Todas as dependencias instaladas!
echo  Agora execute o "iniciar.bat"
echo ========================================
echo.
pause
