@echo off
cd /d C:\Users\alexr\options_signal_bot
call venv\Scripts\activate.bat
python main.py --force >> tasklog.txt 2>&1
