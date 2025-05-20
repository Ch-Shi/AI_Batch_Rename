@echo off
chcp 65001 >nul
pip install -r requirements.txt
python src/main_entry.py
pause 