import re
import subprocess
import tempfile
import os

html = open("tracer.html", encoding="utf-8").read()
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
for i, script in enumerate(scripts):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(script)
        name = f.name
    res = subprocess.run(["node", "-c", name], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error in tracer script {i}: {res.stderr}")
    os.remove(name)

html = open("nemesis_id.html", encoding="utf-8").read()
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
for i, script in enumerate(scripts):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(script)
        name = f.name
    res = subprocess.run(["node", "-c", name], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error in nemesis_id script {i}: {res.stderr}")
    os.remove(name)
