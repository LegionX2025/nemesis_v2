import re
import os

html = open('nemesis_id.html', encoding='utf-8').read()
scripts = re.findall(r'<script.*?>([\s\S]*?)</script>', html)
for i, s in enumerate(scripts):
    with open(f'nid_script_{i}.js', 'w', encoding='utf-8') as f:
        f.write(s)
