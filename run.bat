@echo off
cd /d "%~dp0"
chcp 65001 >nul 2>&1

if "%~1"=="" (
    echo [用法] run.bat ^<input.docx^> [output.xlsx]
    echo [示例] run.bat vocabulary.docx
    pause
    exit /b 1
)

echo ============================================
echo   Word-to-Excel 词汇处理工具
echo ============================================
echo.
echo 正在运行，请稍候...
echo.

set PYTHONIOENCODING=utf-8
conda run --no-capture-output -n word2excel python main.py %*

echo.
echo ============================================
if %ERRORLEVEL% EQU 0 (
    echo Done!
) else (
    echo Failed! Check errors above.
)
echo ============================================
pause
