import re

filepath = 'nemesis_id.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make buttons premium
content = re.sub(r'class="([^"]*)bg-slate-800 hover:bg-slate-700([^"]*)text-slate-300([^"]*)"', r'class="\1 btn-premium \2text-slate-200\3"', content)
content = re.sub(r'class="([^"]*)bg-slate-900 border border-slate-700 text-slate-300 hover:text-white([^"]*)"', r'class="\1 btn-premium \2"', content)
content = re.sub(r'class="([^"]*)bg-cyan-600 hover:bg-cyan-500 text-white([^"]*)"', r'class="\1 btn-premium \2"', content)
content = re.sub(r'class="([^"]*)bg-slate-800 hover:text-cyan-400([^"]*)"', r'class="\1 btn-premium hover:text-cyan-400\2"', content)

# Make cards premium
content = re.sub(r'class="([^"]*)bg-slate-800 border border-slate-700 rounded([^"]*)"', r'class="\1 glass-premium-card border-none rounded\2"', content)
content = re.sub(r'class="([^"]*)bg-slate-800/80 border border-slate-700 rounded([^"]*)"', r'class="\1 glass-premium-card border-none rounded\2"', content)
content = re.sub(r'class="([^"]*)bg-slate-900 border border-slate-700 rounded([^"]*)"', r'class="\1 glass-premium-card border-none rounded\2"', content)
content = re.sub(r'class="([^"]*)bg-slate-800 border-slate-700([^"]*)"', r'class="\1 glass-premium-card border-none\2"', content)
content = re.sub(r'class="([^"]*)bg-slate-900 border-slate-700([^"]*)"', r'class="\1 glass-premium-card border-none\2"', content)


# Table aesthetics
content = re.sub(r'class="([^"]*)divide-slate-700([^"]*)"', r'class="\1 divide-slate-800/50\2"', content)
content = re.sub(r'class="([^"]*)bg-slate-900 text-left([^"]*)"', r'class="\1 bg-slate-900/50 text-left backdrop-blur-sm\2"', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
