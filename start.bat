@echo off
chcp 65001
title 图像智能重命名工具

echo 正在检查 Ollama 服务...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo 正在启动 Ollama 服务...
    start /B ollama serve
    timeout /t 5 /nobreak
)

echo 正在检查模型...
ollama list | findstr "qwen2.5vl:3b" >nul
if errorlevel 1 (
    echo 正在下载 qwen2.5vl:3b 模型...
    ollama pull qwen2.5vl:3b
)

:menu
cls
echo ===================================
echo        图像智能重命名工具
echo ===================================
echo.
echo  [1] 覆盖模式
echo.
echo      直接使用新名称替换原文件名
echo.
echo  [2] 前缀模式
echo.
echo      保留原文件名，添加新名称
echo.
echo  [3] 添加序号
echo.
echo      新名称后添加序号(001-999)
echo.
echo  [4] 退出
echo.
echo      关闭程序
echo.
echo ===================================

set /p choice=请选择操作 (1-4): 

if "%choice%"=="1" (
    set mode=override
    goto input
)
if "%choice%"=="2" (
    set mode=prefix
    goto input
)
if "%choice%"=="3" (
    set mode=override
    set add_index=--add_index
    goto input
)
if "%choice%"=="4" (
    goto end
)
goto menu

:input
cls
echo ===================================
echo        图像智能重命名工具
echo ===================================
echo.
echo 当前模式: %mode%
if defined add_index echo 已启用序号添加
echo.
echo 请将图片文件夹拖放到此处，然后按回车：
set /p folder=

if not exist "%folder%" (
    echo 错误：文件夹不存在！
    pause
    goto menu
)

echo.
echo 正在处理图片...
python src/main.py -i "%folder%" -m %mode% %add_index%
echo.
echo 处理完成！
pause
goto menu

:end
echo 正在关闭 Ollama 服务...
taskkill /F /IM ollama.exe >nul 2>&1
exit 