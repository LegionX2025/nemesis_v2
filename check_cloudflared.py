import os
import subprocess

def run(cmd):
    print(">>>", cmd)
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(res.stdout)
        if res.stderr:
            print("STDERR:", res.stderr)
    except Exception as e:
        print("ERROR:", e)

run("cloudflared.exe --version")
run("where cloudflared")
