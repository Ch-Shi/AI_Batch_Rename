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

:menu
cls
echo ===================================
echo        AI Image Batch Rename
echo ===================================
echo.
echo  [1] Override Mode
echo.
echo      Replace original filename with new name
echo.
echo  [2] Prefix Mode
echo.
echo      Keep original filename with new name as prefix
echo.
echo  [3] Add Index
echo.
echo      Add sequential numbers (001-999)
echo.
echo  [4] Exit
echo.
echo      Close program
echo.
echo ===================================

set /p choice=Please select operation (1-4): 

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
echo        AI Image Batch Rename
echo ===================================
echo.
echo Current mode: %mode%
if defined add_index echo Index mode enabled
echo.
echo Please drag and drop image folder here, then press Enter:
set /p folder=

if not exist "%folder%" (
    echo Error: Folder does not exist!
    pause
    goto menu
)

echo.
echo Processing images...
python src/main.py -i "%folder%" -m %mode% %add_index%
if errorlevel 1 (
    echo Error: Processing failed, please check log file!
    pause
    goto menu
)
echo.
echo Processing completed!
pause
goto menu

:end
echo Closing Ollama service...
taskkill /F /IM ollama.exe >nul 2>&1
exit 