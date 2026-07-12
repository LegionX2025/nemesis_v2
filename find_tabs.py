import re

with open('nemesis_id.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'id="tab-' in l or 'class="tab-content' in l:
        print(f"Line {i+1}: {l.strip()[:100]}")
