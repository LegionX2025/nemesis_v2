import re
path = 'tracer.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace body theme
html = html.replace('bg-slate-950', 'bg-slate-50')
html = html.replace('text-slate-200', 'text-slate-800')

# Replace control panel and side panels theme
html = html.replace('bg-slate-900/80', 'bg-white/90 border-b border-slate-200')
html = html.replace('bg-slate-900', 'bg-white')
html = html.replace('bg-slate-800', 'bg-slate-100')
html = html.replace('border-slate-800', 'border-slate-200')
html = html.replace('border-slate-700', 'border-slate-200')
html = html.replace('text-slate-400', 'text-slate-500')
html = html.replace('text-slate-300', 'text-slate-600')
html = html.replace('bg-indigo-900/50', 'bg-indigo-100')
html = html.replace('text-indigo-400', 'text-indigo-600')
html = html.replace('bg-blue-900/50', 'bg-blue-100')
html = html.replace('text-blue-400', 'text-blue-600')
html = html.replace('bg-emerald-900/50', 'bg-emerald-100')
html = html.replace('text-emerald-400', 'text-emerald-600')
html = html.replace('bg-red-900/50', 'bg-red-100')
html = html.replace('text-red-400', 'text-red-600')

# Ensure script injection
if 'nemesis-ui.js' not in html:
    html = html.replace('</body>', '    <script src="/nemesis-ui.js"></script>\n</body>')
if 'nemesis-ui.css' not in html:
    html = html.replace('</head>', '    <link rel="stylesheet" href="/nemesis-ui.css">\n</head>')

# Remove legacy landing page CSS from tracer to clean it up
html = re.sub(r'/\* Landing Page Styles \*/.*?/\* Control Panel \*/', '/* Control Panel */', html, flags=re.DOTALL)
html = re.sub(r'<div id="landing-page".*?<!-- App Container -->', '<!-- App Container -->', html, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Applied Light Theme replacements and cleaned tracer.html')
