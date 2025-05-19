@echo off
chcp 65001 >nul
title AI Image Batch Rename Tool

echo Checking Python environment...
python --version 2>nul | findstr /r "^Python 3" >nul
if errorlevel 1 (
    echo Error: Python 3 not found. Please install Python 3 or higher version!
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo Checking Ollama service...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo Starting Ollama service...
    start /B ollama serve
    timeout /t 5 /nobreak
)

echo Checking model...
ollama list | findstr "qwen2.5vl:3b" >nul
if errorlevel 1 (
    echo Downloading qwen2.5vl:3b model...
    ollama pull qwen2.5vl:3b
)

:main_menu
cls
echo ===================================
echo        AI Image Batch Rename
echo ===================================
echo.
echo  [1] Normal Batch Rename Mode
echo  [2] Eagle Library Mode
echo  [3] Exit
echo ===================================
set /p main_choice=Please select mode (1-3): 

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
echo        Select Rename Strategy
echo ===================================
echo.
echo  [1] Override Mode
echo      Replace original filename with new name
echo.
echo  [2] Prefix Mode
echo      Keep original filename with new name as prefix
echo.
echo  [3] Add Index
echo      Add sequential numbers (001-999)
echo.
echo  [4] Back to Main Menu
echo ===================================
set /p mode_choice=Please select rename strategy (1-4): 

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
echo        Normal Batch Rename Mode
echo ===================================
echo.
echo Please drag and drop the image folder here, then press Enter:
set /p folder=
if not exist "%folder%" (
    echo Error: Folder does not exist!
    pause
    goto normal_input
)
echo.
echo Processing images...
python src/main.py -i "%folder%" -m %rename_mode% %add_index%
pause
goto main_menu

:eagle_input
cls
echo ===================================
echo        Eagle Library Batch Rename Mode
echo ===================================
echo.
echo Please enter the path to your Eagle library root folder (e.g. E:\AIGC_Project\Library):
set /p eagle_root=
if not exist "%eagle_root%" (
    echo Error: Directory does not exist!
    pause
    goto eagle_input
)
echo.
echo Please paste Eagle folder links (one per line). After pasting all links, press Enter on an empty line to finish:
python src/eagle_rename.py --root "%eagle_root%" --mode %rename_mode% %add_index%
pause
goto main_menu

:end
echo Closing Ollama service...
taskkill /F /IM ollama.exe >nul 2>&1
exit 