import os

with open('tracer.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The error is a literal newline inside split("")
# like: n.title.split("
# ")[0]
bad_str = 'n.title.split("\\n")[0]' # In python, this is n.title.split(" + literal newline + ")[0]
# Actually, the string in the file literally spans two lines:
# let amountText = n.custom_amount || (n.title && n.title.includes("$") ? n.title.split("
# ")[0] : "$0.00");

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'let amountText = n.custom_amount' in line:
        if 'n.title.split("' in line and '")[0]' not in line:
            # It's split across lines
            lines[i] = '                    let amountText = n.custom_amount || (n.title && n.title.includes("$") ? n.title.split("\\n")[0] : "$0.00");'
            lines[i+1] = lines[i+1].replace('")[0] : "$0.00");', '')

with open('tracer.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
