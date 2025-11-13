@echo off
setlocal EnableExtensions

:: Ativa o ambiente silenciosamente
call "%USERPROFILE%\anaconda3\condabin\conda.bat" activate meli_case >nul 2>&1

:: Executa o script Python
python "%~dp0run_etls.py"

pause