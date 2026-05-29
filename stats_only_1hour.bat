@echo off
REM ============================================================
REM MIMIC-IV ML Pipeline - STATS ONLY (1 hour)
REM ============================================================
REM Runs Phases 7-9: Advanced Stats + Visualizations + Dashboard
REM Skips Phase 8 model comparison for speed
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo MIMIC-IV ML Pipeline - STATS ONLY (1 hour)
echo ============================================================
echo.
echo This will run Phases 7-9 (no model comparison)
echo.
echo Timestamp: %date% %time%
echo.

REM Phase 7.1: Descriptive Statistics
echo Step 1/5: Descriptive Statistics (20 min)...
py analysis/descriptive_statistics.py
if %errorlevel% neq 0 (
    echo ERROR: Descriptive statistics failed!
    pause
    exit /b 1
)

REM Phase 7.2: Bivariate Analysis
echo.
echo Step 2/5: Bivariate Analysis (25 min)...
py analysis/bivariate_analysis.py
if %errorlevel% neq 0 (
    echo ERROR: Bivariate analysis failed!
    pause
    exit /b 1
)

REM Phase 7.3: Multivariate Analysis
echo.
echo Step 3/5: Multivariate Analysis (15 min)...
py analysis/multivariate_analysis.py
if %errorlevel% neq 0 (
    echo ERROR: Multivariate analysis failed!
    pause
    exit /b 1
)

REM Phase 9: Visualizations
echo.
echo Step 4/5: Creating Visualizations (10 min)...
py analysis/visualization.py
if %errorlevel% neq 0 (
    echo ERROR: Visualization failed!
    pause
    exit /b 1
)

REM Phase 9: Dashboard
echo.
echo Step 5/5: Generating Dashboard (5 min)...
py analysis/generate_dashboard.py
if %errorlevel% neq 0 (
    echo ERROR: Dashboard generation failed!
    pause
    exit /b 1
)

echo.
echo Opening dashboard...
timeout /t 2 /nobreak

if exist "analysis\dashboard.html" (
    start "" "analysis\dashboard.html"
    echo.
    echo ============================================================
    echo SUCCESS! All stats completed and dashboard opened
    echo ============================================================
    echo.
) else (
    echo ERROR: Dashboard file not found!
)

pause
