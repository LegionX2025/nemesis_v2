import sys
with open('tracer.html', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        if '<nav' in line or 'href=' in line:
            print(f"{i+1}: {line.strip()}")
