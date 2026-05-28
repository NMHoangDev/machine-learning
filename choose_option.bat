@echo off
REM ============================================================
REM CHOOSE YOUR OPTION
REM ============================================================
REM Pick the execution option that works best for you!
REM ============================================================

:menu
cls
echo.
echo ============================================================
echo MIMIC-IV ML Pipeline - Choose Your Option
echo ============================================================
echo.
echo 1. FASTEST (15 min)    - Dashboard only
echo    └─ Creates visualizations from existing results
echo.
echo 2. STATS ONLY (1 hour) - Advanced statistical analysis
echo    └─ Phases 7-9 (skips model comparison)
echo.
echo 3. FULL (2.5 hours)    - Complete pipeline
echo    └─ All 9 phases (stats + models + visualizations)
echo.
echo ============================================================
echo.

set /p choice="Select option (1/2/3): "

if "%choice%"=="1" (
    call quick_dashboard_15min.bat
) else if "%choice%"=="2" (
    call stats_only_1hour.bat
) else if "%choice%"=="3" (
    call run_pipeline_and_open_dashboard.bat
) else (
    echo Invalid choice. Please select 1, 2, or 3
    timeout /t 2 /nobreak
    goto menu
)

