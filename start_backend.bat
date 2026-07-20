@echo off
set PYTHONPATH=C:\Users\LEGIONX\Downloads\nemesis\tracer_scripts;C:\Users\LEGIONX\Downloads\nemesis\tracer_scripts\backend
cd C:\Users\LEGIONX\Downloads\nemesis\tracer_scripts\backend
C:\Users\LEGIONX\AppData\Local\Programs\Python\Python313\python.exe -m uvicorn nemesis_core:app --host 127.0.0.1 --port 8000
