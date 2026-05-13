@echo off
cd /d "%~dp0"
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
conda run --no-capture-output -n word2excel python launcher.py %*
pause
