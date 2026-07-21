import sys

def overhaul_tracer(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Generic light to dark replacements
    replacements = {
        'bg-white/90': 'bg-slate-900/90',
        'bg-white/95': 'bg-slate-900/95',
        'bg-white': 'bg-slate-800',
        'border-slate-200': 'border-slate-700',
        'border-slate-300': 'border-slate-600',
        'text-slate-700': 'text-slate-300',
        'text-slate-800': 'text-slate-200',
        'text-slate-600': 'text-slate-400',
        'shadow-sm': 'shadow-[0_4px_15px_rgba(0,0,0,0.5)]',
        'bg-slate-50': 'bg-slate-700',
        'hover:bg-slate-50': 'hover:bg-slate-700',
        'shadow-lg': 'shadow-[0_10px_30px_rgba(0,0,0,0.6)]',
        'bg-slate-100': 'bg-slate-900',
    }

    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

overhaul_tracer('tracer.html')
print('tracer.html updated')
