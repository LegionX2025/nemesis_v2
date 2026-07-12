import re

with open('tracer.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_idx = html.find('<div id="landing-page"')
print("Start idx:", start_idx)
print("Snippet:", html[start_idx:start_idx+200])

# Just regex it up to the next outer div that looks like app container
# Looking at tracer.html from earlier view, we saw:
# <div id="network-container" or something similar?
# Let's print the lines after landing-page
lines = html.split('\n')
for i, l in enumerate(lines):
    if 'landing-page' in l:
        for j in range(i, min(i+400, len(lines))):
            if '<div' in lines[j] and 'landing' not in lines[j] and 'tsparticles' not in lines[j] and 'z-' not in lines[j]:
                if lines[j].strip().startswith('<div id="') or 'class="flex' in lines[j]:
                    print(f"Line {j}: {lines[j].strip()[:100]}")
