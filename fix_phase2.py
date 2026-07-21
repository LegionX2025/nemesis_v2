import sys

def overhaul_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Generic light to dark replacements
    replacements = {
        'bg-white/90': 'bg-slate-900/90',
        'bg-white/95': 'bg-slate-900/95',
        'bg-white/50': 'bg-slate-800/50',
        'bg-white': 'bg-slate-800',
        'bg-slate-50': 'bg-slate-800/80',
        'bg-slate-100': 'bg-slate-900',
        'bg-gray-50': 'bg-slate-800/80',
        'bg-gray-100': 'bg-slate-900',
        
        'border-slate-200': 'border-slate-700',
        'border-slate-300': 'border-slate-600',
        'border-gray-200': 'border-slate-700',
        'border-gray-300': 'border-slate-600',
        
        'text-slate-700': 'text-slate-300',
        'text-slate-800': 'text-slate-200',
        'text-slate-600': 'text-slate-400',
        'text-slate-900': 'text-white',
        'text-gray-700': 'text-slate-300',
        'text-gray-800': 'text-slate-200',
        'text-gray-600': 'text-slate-400',
        'text-gray-900': 'text-white',
        
        'shadow-sm': 'shadow-[0_4px_15px_rgba(0,0,0,0.5)]',
        'shadow-md': 'shadow-[0_8px_25px_rgba(0,0,0,0.6)]',
        'shadow-lg': 'shadow-[0_10px_30px_rgba(0,0,0,0.7)]',
        'shadow-xl': 'shadow-[0_15px_40px_rgba(0,0,0,0.8)]',
        
        'hover:bg-slate-50': 'hover:bg-slate-700',
        'hover:bg-gray-50': 'hover:bg-slate-700',
        
        # Inject our fonts and global theme
        "font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #0f172a;": "font-family: 'Outfit', 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc;",
        "font-family: 'Inter', sans-serif; background-color: #f1f5f9; color: #0f172a;": "font-family: 'Outfit', 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc;",
        
        # Gradient overrides
        "from-blue-600 to-indigo-700": "from-cyan-500 to-blue-600",
        "from-indigo-600 to-blue-800": "from-indigo-500 to-purple-600",
        "bg-blue-600": "bg-cyan-600",
        "bg-indigo-600": "bg-indigo-500",
        "text-blue-600": "text-cyan-400",
        "text-indigo-600": "text-indigo-400",
        "hover:bg-blue-700": "hover:bg-cyan-500",
        "hover:bg-indigo-700": "hover:bg-indigo-400",
        
        # Form inputs
        "bg-white border-slate-300 text-slate-900": "bg-slate-900 border-slate-700 text-white",
        
        # Specific structural fixes if needed for glass premium
        'class="bg-slate-800 rounded-xl': 'class="glass-premium-card rounded-xl',
        'class="bg-slate-800 shadow': 'class="glass-premium-card shadow',
    }

    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

files = [
    'nemesis_id.html',
    'darknet_portal.html',
    'recovery_framework.html',
    'report_template.html'
]

for f in files:
    try:
        overhaul_file(f)
        print(f'{f} updated')
    except Exception as e:
        print(f'Error updating {f}: {e}')
