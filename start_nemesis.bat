@echo off
echo ==================================================
echo   Starting NEMESIS Auto-Cloudflare Deployer...
echo ==================================================
cd /d "%~dp0"
python auto_cloudflare.py
pause
