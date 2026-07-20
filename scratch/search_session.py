import os

with open("nemesis_core.py", "r", encoding="utf-8") as f:
    lines = []
    for i, line in enumerate(f):
        if "ClientSession" in line:
            lines.append(f"Line {i}: {line.strip()}\n")

with open("scratch/out.txt", "w", encoding="utf-8") as fw:
    fw.writelines(lines)
