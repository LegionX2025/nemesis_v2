import os, re
path = 'nemesis_id.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inject nemesis-ui.css in head
if 'nemesis-ui.css' not in html:
    html = html.replace('</head>', '    <link rel="stylesheet" href="/nemesis-ui.css">\n</head>')

# 2. Inject nemesis-ui.js before </body>
if 'nemesis-ui.js' not in html:
    html = html.replace('</body>', '    <script src="/nemesis-ui.js"></script>\n</body>')

# 3. Replace body dark theme with light theme
html = html.replace('bg-slate-950', 'bg-slate-50')
html = html.replace('text-slate-200', 'text-slate-800')
html = html.replace('bg-slate-900', 'bg-white border border-slate-200')
html = html.replace('bg-slate-800', 'bg-slate-100')
html = html.replace('border-slate-800', 'border-slate-200')
html = html.replace('border-slate-700', 'border-slate-200')
html = html.replace('text-slate-400', 'text-slate-500')
html = html.replace('text-slate-300', 'text-slate-600')
html = html.replace('bg-indigo-900/50', 'bg-indigo-100')
html = html.replace('bg-red-900/50', 'bg-red-100')
html = html.replace('bg-green-900/50', 'bg-green-100')
html = html.replace('bg-emerald-900/50', 'bg-emerald-100')
html = html.replace('text-indigo-400', 'text-indigo-600')
html = html.replace('text-red-400', 'text-red-600')
html = html.replace('text-green-400', 'text-green-600')
html = html.replace('text-emerald-400', 'text-emerald-600')
html = html.replace('text-blue-400', 'text-blue-600')
html = html.replace('text-amber-400', 'text-amber-600')
html = html.replace('bg-blue-900/50', 'bg-blue-100')
html = html.replace('bg-amber-900/50', 'bg-amber-100')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Applied Light Theme replacements to nemesis_id.html')
