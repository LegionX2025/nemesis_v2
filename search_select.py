import sys
with open('landing.html', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        if '<select' in line:
            print(f"{i+1}: {line.strip()}")
