import sys

filepath = 'darknet_portal.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\\`', '`').replace('\\${', '${')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed backticks in darknet_portal.html')
