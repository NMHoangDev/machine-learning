@echo off
REM ============================================================
REM MIMIC-IV ML Pipeline - Complete Execution & Dashboard
REM ============================================================
REM This batch file:
REM 1. Runs the complete pipeline using py
REM 2. Automatically opens the dashboard in browser
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo MIMIC-IV ML Pipeline - Starting Execution
echo ============================================================
echo.
echo Timestamp: %date% %time%
echo.

REM Run the complete pipeline
echo Running complete pipeline...
echo.
py run_complete_pipeline.py

REM Check if pipeline completed successfully
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo ERROR: Pipeline execution failed!
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Pipeline execution completed successfully!
echo ============================================================
echo.
echo Opening dashboard in browser...
echo.

REM Wait a moment for dashboard to be generated
timeout /t 2 /nobreak

REM Open the dashboard in the default browser
if exist "analysis\dashboard.html" (
    start "" "analysis\dashboard.html"
    echo Dashboard opened in default browser
    echo.
    echo Location: analysis\dashboard.html
) else (
    echo.
    echo WARNING: Dashboard file not found at analysis\dashboard.html
    echo Please check the pipeline output for errors
)

echo.
echo ============================================================
echo Process complete!
echo ============================================================
echo.
pause
