@echo off
cd /d "%~dp0"
chcp 65001 >nul 2>&1

echo ============================================
echo   Vocabulary Agent - 词汇处理工具
echo ============================================
echo.

REM 输入文件
:input_loop
set "input_file="
set /p input_file="请输入 Word 文档路径（或直接拖拽文件到此处）: "

REM 去掉路径两端的引号
set input_file=%input_file:"=%

if "%input_file%"=="" (
    echo 路径不能为空，请重新输入。
    echo.
    goto input_loop
)

if not exist "%input_file%" (
    echo [错误] 文件不存在: %input_file%
    echo 请检查路径是否正确。
    echo.
    goto input_loop
)

REM 输出文件
set "output_file="
set /p output_file="请输入输出 Excel 路径（直接回车默认 vocabulary_output.xlsx）: "
set output_file=%output_file:"=%
if "%output_file%"=="" set output_file=vocabulary_output.xlsx

echo.
echo ============================================
echo   输入: %input_file%
echo   输出: %output_file%
echo ============================================
echo.
echo 正在运行，请稍候...
echo.

set PYTHONIOENCODING=utf-8
conda run --no-capture-output -n word2excel python main.py "%input_file%" "%output_file%"

echo.
echo ============================================
if %ERRORLEVEL% EQU 0 (
    echo [完成] 处理成功！
) else (
    echo [失败] 处理出错，请检查上方错误信息。
)
echo ============================================
echo.
pause
