@echo off
REM ============================================================
REM MIMIC-IV ML Pipeline - FAST DASHBOARD (15 minutes)
REM ============================================================
REM Uses existing Phase 1-6 results to create visualizations
REM and dashboard INSTANTLY
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo MIMIC-IV ML Pipeline - FAST DASHBOARD (15 min)
echo ============================================================
echo.
echo This will create visualizations and dashboard from
echo existing Phase 1-6 results
echo.
echo Timestamp: %date% %time%
echo.

REM Create visualizations
echo Step 1/3: Creating visualizations...
py analysis/visualization.py
if %errorlevel% neq 0 (
    echo ERROR: Visualization failed!
    pause
    exit /b 1
)

echo.
echo Step 2/3: Generating dashboard...
py analysis/generate_dashboard.py
if %errorlevel% neq 0 (
    echo ERROR: Dashboard generation failed!
    pause
    exit /b 1
)

echo.
echo Step 3/3: Opening dashboard...
timeout /t 2 /nobreak

if exist "analysis\dashboard.html" (
    start "" "analysis\dashboard.html"
    echo.
    echo ============================================================
    echo SUCCESS! Dashboard opened in browser
    echo ============================================================
    echo.
) else (
    echo ERROR: Dashboard file not found!
)

pause
