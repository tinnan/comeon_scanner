@ECHO OFF
setlocal
rem Execution environment variable
set COMEON_ENV=prod
rem Python path to current directory, this batch file is supposed to be in project root directory.
set PYTHONPATH=%cd%

rem Execute scanner
python .\src\main.py
endlocal
