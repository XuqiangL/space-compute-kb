@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "??????" py main.py
exit

