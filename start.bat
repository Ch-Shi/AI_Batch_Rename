@echo off
rem 检查并设置正确的代码页
chcp 65001 >nul
if errorlevel 1 (
    echo 错误：无法设置 UTF-8 编码，请确保系统支持 UTF-8！
    pause
    exit /b 1
)

title 图像智能批量重命名工具

echo 正在检查 Python 环境...
python --version 2>nul | findstr /r "^Python 3" >nul
if errorlevel 1 (
    echo 错误：未检测到 Python 3，请安装 Python 3 或更高版本！
    pause
    exit /b 1
)

echo 正在检查依赖包...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误：依赖包安装失败！
        pause
        exit /b 1
    )
)

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

:main_menu
cls
echo ===================================
echo        图像智能批量重命名
echo ===================================
echo.
echo  [1] 普通批量命名模式
echo  [2] Eagle 专用模式
echo  [3] 退出
echo ===================================
set /p main_choice=请选择主模式 (1-3): 

if "%main_choice%"=="1" (
    set mode_type=normal
    goto mode_menu
)
if "%main_choice%"=="2" (
    set mode_type=eagle
    goto mode_menu
)
if "%main_choice%"=="3" (
    goto end
)
goto main_menu

:mode_menu
cls
echo ===================================
echo        选择命名方式
echo ===================================
echo.
echo  [1] 覆盖模式（Override）
echo      用新名称替换原文件名
echo.
echo  [2] 前缀模式（Prefix）
echo      新名称作为前缀保留原文件名
echo.
echo  [3] 添加序号（Add Index）
echo      添加序号（001-999）
echo.
echo  [4] 返回主菜单
echo ===================================
set /p mode_choice=请选择命名方式 (1-4): 

if "%mode_choice%"=="1" (
    set rename_mode=override
    set add_index=
)
if "%mode_choice%"=="2" (
    set rename_mode=prefix
    set add_index=
)
if "%mode_choice%"=="3" (
    set rename_mode=override
    set add_index=--add_index
)
if "%mode_choice%"=="4" (
    goto main_menu
)
if not defined rename_mode goto mode_menu

if "%mode_type%"=="normal" (
    goto normal_input
) else (
    goto eagle_input
)

:normal_input
cls
echo ===================================
echo        普通批量命名模式
echo ===================================
echo.
echo 请拖入图片文件夹路径，然后回车：
set /p folder=
if not exist "%folder%" (
    echo 错误：文件夹不存在！
    pause
    goto normal_input
)
echo.
echo 正在处理图片...
python src/main.py -i "%folder%" -m %rename_mode% %add_index%
if errorlevel 1 (
    echo 错误：处理失败，请检查日志文件！
    pause
)
pause
goto main_menu

:eagle_input
cls
echo ===================================
echo        Eagle 专用批量命名模式
echo ===================================
echo.
echo 请输入 Eagle 资料库根目录路径（如 E:\AIGC_Project\订阅图库\Eagle资料库）：
set /p eagle_root=
if not exist "%eagle_root%" (
    echo 错误：目录不存在！
    pause
    goto eagle_input
)
echo.
echo 请粘贴 Eagle 目录链接（用空格分隔多个链接），然后回车：
python src/eagle_rename.py --root "%eagle_root%" --mode %rename_mode% %add_index%
if errorlevel 1 (
    echo 错误：Eagle 批量重命名失败，请检查日志！
    pause
)
pause
goto main_menu

:end
echo 正在关闭 Ollama 服务...
taskkill /F /IM ollama.exe >nul 2>&1
pause
exit 