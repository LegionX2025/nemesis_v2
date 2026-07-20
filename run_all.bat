@echo off
set PATH=%PATH%;C:\Windows\System32;C:\Windows\System32\Wbem
echo ========================================================
echo LIONSGATE NEMESIS - GHOST PROCESS TERMINATOR
echo ========================================================
echo.
echo Killing processes on port 8000 (Backend)...
for /f "tokens=5" %%a in ('C:\Windows\System32\netstat.exe -aon ^| C:\Windows\System32\find.exe ":8000" ^| C:\Windows\System32\find.exe "LISTENING"') do C:\Windows\System32\taskkill.exe /f /pid %%a

echo Killing processes on port 3001 (Frontend)...
for /f "tokens=5" %%a in ('C:\Windows\System32\netstat.exe -aon ^| C:\Windows\System32\find.exe ":3001" ^| C:\Windows\System32\find.exe "LISTENING"') do C:\Windows\System32\taskkill.exe /f /pid %%a

echo Killing processes on port 8088...
for /f "tokens=5" %%a in ('C:\Windows\System32\netstat.exe -aon ^| C:\Windows\System32\find.exe ":8088" ^| C:\Windows\System32\find.exe "LISTENING"') do C:\Windows\System32\taskkill.exe /f /pid %%a

echo.
echo Ports cleared.
echo.

echo Deploying Cloudflare Worker (API Proxy)...
cd /d "C:\Users\LEGIONX\downloads\nemesis\tracer_scripts\workers"
call npx wrangler deploy

echo Deploying Cloudflare Pages (Frontend)...
cd /d "C:\Users\LEGIONX\downloads\nemesis\tracer_scripts"
call npx wrangler pages deploy public --project-name nemesis-id-frontend

echo.
echo Starting Darknet Autonomous Service...
cd /d "C:\Users\LEGIONX\downloads\nemesis\tracer_scripts"
start /B python scripts\darknet.py

echo Starting Nemesis Core Engine...
python nemesis_core.py
