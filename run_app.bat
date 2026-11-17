@echo off
title Titan Gym & Fitness Management System
echo Launching Titan Gym Management Desktop Application...
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%.
    pause
)
