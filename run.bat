@echo off
cd /d "%~dp0"
chcp 65001 >nul 2>&1

echo ============================================
echo   Vocabulary Agent
echo ============================================
echo.

REM 支持拖拽文件（%1）或手动输入
if not "%~1"=="" (
    set "input_file=%~1"
    goto have_input
)

:input_loop
set "input_file="
set /p input_file="Input docx path (or drag file here): "
set input_file=%input_file:"=%

if "%input_file%"=="" (
    echo Path cannot be empty.
    echo.
    goto input_loop
)

if not exist "%input_file%" (
    echo [ERROR] File not found: %input_file%
    echo.
    goto input_loop
)

:have_input
if not exist "%input_file%" (
    echo [ERROR] File not found: %input_file%
    pause
    exit /b 1
)

REM 输出路径（%2 或手动输入）
if not "%~2"=="" (
    set "output_file=%~2"
    goto have_output
)

set "output_file="
set /p output_file="Output xlsx path (Enter = vocabulary_output.xlsx): "
set output_file=%output_file:"=%
if "%output_file%"=="" set output_file=vocabulary_output.xlsx

:have_output
echo.
echo Input:  %input_file%
echo Output: %output_file%
echo.
echo Running, please wait...
echo.

set PYTHONIOENCODING=utf-8
conda run --no-capture-output -n word2excel python main.py "%input_file%" "%output_file%"

echo.
if %ERRORLEVEL% EQU 0 (
    echo [OK] Done!
) else (
    echo [FAIL] Check errors above.
)

echo.
pause
