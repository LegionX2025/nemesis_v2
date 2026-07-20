import os

with open("nemesis_id.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "Real-Time Transaction" in line or "Real-Time" in line:
            print(f"Line {i}: {line.strip()}")
            for j in range(i+1, min(i+20, len(lines))):
                print(f"Line {j}: {lines[j].strip()}")
            break
