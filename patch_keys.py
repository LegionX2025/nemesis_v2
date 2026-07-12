import os
import re

filepath = 'nemesis_core.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make it support VITE_ prefixes for all api keys used in Config
content = re.sub(
    r'os\.getenv\("([^"]+)", ""\)',
    r'os.getenv("\1", os.getenv("VITE_\1", ""))',
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched API keys in nemesis_core.py')
