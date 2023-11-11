@echo off
setlocal enabledelayedexpansion
set root_path=%~dp0
set script_name=%~nx0

set "module_name=!script_name:-=_!"
set "module_name=!module_name:.bat=.py!"

set cmd_path=%root_path%..\kdm\cli\%module_name%

call %root_path%..\venv\Scripts\activate
python %cmd_path%
deactivate