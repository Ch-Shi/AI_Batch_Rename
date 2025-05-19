@echo off
rem ��鲢������ȷ�Ĵ���ҳ
chcp 65001 >nul
if errorlevel 1 (
    echo �����޷����� UTF-8 ���룬��ȷ��ϵͳ֧�� UTF-8��
    pause
    exit /b 1
)

title ͼ��������������������

echo ���ڼ�� Python ����...
python --version 2>nul | findstr /r "^Python 3" >nul
if errorlevel 1 (
    echo ����δ��⵽ Python 3���밲װ Python 3 ����߰汾��
    pause
    exit /b 1
)

echo ���ڼ��������...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ���ڰ�װ������...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ������������װʧ�ܣ�
        pause
        exit /b 1
    )
)

echo ���ڼ�� Ollama ����...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo �������� Ollama ����...
    start /B ollama serve
    timeout /t 5 /nobreak
)

echo ���ڼ��ģ��...
ollama list | findstr "qwen2.5vl:3b" >nul
if errorlevel 1 (
    echo �������� qwen2.5vl:3b ģ��...
    ollama pull qwen2.5vl:3b
)

:main_menu
cls
echo ===================================
echo        ͼ����������������
echo ===================================
echo.
echo  [1] ��ͨ��������ģʽ
echo  [2] Eagle ר��ģʽ
echo  [3] �˳�
echo ===================================
set /p main_choice=��ѡ����ģʽ (1-3): 

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
echo        ѡ��������ʽ
echo ===================================
echo.
echo  [1] ����ģʽ��Override��
echo      ���������滻ԭ�ļ���
echo.
echo  [2] ǰ׺ģʽ��Prefix��
echo      ��������Ϊǰ׺����ԭ�ļ���
echo.
echo  [3] �����ţ�Add Index��
echo      �����ţ�001-999��
echo.
echo  [4] �������˵�
echo ===================================
set /p mode_choice=��ѡ��������ʽ (1-4): 

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
echo        ��ͨ��������ģʽ
echo ===================================
echo.
echo ������ͼƬ�ļ���·����Ȼ��س���
set /p folder=
if not exist "%folder%" (
    echo �����ļ��в����ڣ�
    pause
    goto normal_input
)
echo.
echo ���ڴ���ͼƬ...
python src/main.py -i "%folder%" -m %rename_mode% %add_index%
if errorlevel 1 (
    echo ���󣺴���ʧ�ܣ�������־�ļ���
    pause
)
pause
goto main_menu

:eagle_input
cls
echo ===================================
echo        Eagle ר����������ģʽ
echo ===================================
echo.
echo ������ Eagle ���Ͽ��Ŀ¼·������ E:\AIGC_Project\����ͼ��\Eagle���Ͽ⣩��
set /p eagle_root=
if not exist "%eagle_root%" (
    echo ����Ŀ¼�����ڣ�
    pause
    goto eagle_input
)
echo.
echo ��ճ�� Eagle Ŀ¼���ӣ��ÿո�ָ�������ӣ���Ȼ��س���
python src/eagle_rename.py --root "%eagle_root%" --mode %rename_mode% %add_index%
if errorlevel 1 (
    echo ����Eagle ����������ʧ�ܣ�������־��
    pause
)
pause
goto main_menu

:end
echo ���ڹر� Ollama ����...
taskkill /F /IM ollama.exe >nul 2>&1
pause
exit 