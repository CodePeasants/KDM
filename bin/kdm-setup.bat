@echo off
setlocal enabledelayedexpansion

REM Create virtual environment, install requirements and setup environment, if not already done.

set ROOT_PATH=%~dp0
set VENV_PATH=%ROOT_PATH%\..\venv
set REQUIREMENTS_FILE=%ROOT_PATH%\..\requirements.txt
set KDM_PTH_FILE=%VENV_PATH%\Lib\site-packages\kdm.pth
set KDM_ROOT=%ROOT_PATH%\..

if not exist %VENV_PATH% (
    echo "No virtual environment found, creating..."
    python -m venv %VENV_PATH%
    call %VENV_PATH%\Scripts\activate
    call %VENV_PATH%\Scripts\pip install -r %REQUIREMENTS_FILE%
)

if not exist %KDM_PTH_FILE% (
    echo "No kdm.pth envrionment file found, creating..."
    echo %KDM_ROOT% > %KDM_PTH_FILE%
)
