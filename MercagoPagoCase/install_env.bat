@echo off
setlocal EnableExtensions

echo === Initializing Conda ===
call "%USERPROFILE%\anaconda3\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize Conda.
    pause
    exit /b
)

REM ===== Check if the environment already exists =====
call conda env list | findstr /C:"meli_case" >nul
if %errorlevel%==0 (
    echo.
    echo Environment 'meli_case' already exists. Skipping creation...
) else (
    echo.
    echo === Creating environment meli_case ===
    conda env create -f meli_case.yaml
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create environment.
        pause
        exit /b
    )
    echo.
    echo ✔ Environment successfully created!
)

echo.
echo === Activating environment meli_case ===
call conda activate meli_case
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate environment.
    pause
    exit /b
)

echo.
echo ✔ Environment 'meli_case' activated successfully!
echo.

pause



