@echo off
setlocal enabledelayedexpansion

set ROOT_PATH=%~dp0
set SCRIPT_NAME=%~nx0
set "module_name=!SCRIPT_NAME:-=_!"
set "module_name=!module_name:.bat=.py!"

REM Set up any missing requirements first (create venv, install requirements, setup env...)
call %ROOT_PATH%kdm-setup.bat

set cmd_path=%ROOT_PATH%..\kdm\cli\%module_name%

%ROOT_PATH%..\venv\Scripts\python %cmd_path% %*