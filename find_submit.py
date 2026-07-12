import sys
with open('tracer.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'function submitTrace()' in line:
            print(f"Line {i+1}: {line.strip()}")
            for j in range(max(0, i), min(len(lines), i+30)):
                print(f"{j+1}: {lines[j].strip()}")
            break
