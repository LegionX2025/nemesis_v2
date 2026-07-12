import re

with open("nemesis_id.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the text-center mb-8 div inside initial-search-modal
old_modal_header = """            <div class="text-center mb-8">
                <img src="logo_nemesis.jpeg" alt="Nemesis Logo" class="w-24 h-24 mx-auto border border-slate-300 rounded-2xl mb-4 shadow-xl bg-white object-contain">
                <h1 class="text-5xl font-black font-cyber text-slate-900 tracking-widest drop-shadow-md">NEMESIS ID</h1>
                <p class="text-slate-500 font-mono text-sm tracking-widest lowercase italic my-2">by</p>
                <h2 class="text-2xl font-black font-serif text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-800 tracking-widest uppercase relative inline-block">
                    LIONSGATE NETWORK
                </h2>
                <p class="text-blue-600 font-mono text-[10px] tracking-widest uppercase mt-4">Entity Resolution & Intelligence Subsystem</p>
            </div>"""

new_modal_header = """            <div class="text-center mb-8">
                <p class="text-slate-500 font-mono text-sm tracking-widest lowercase italic my-2">by</p>
                <h2 class="text-2xl font-black font-serif text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-800 tracking-widest uppercase relative inline-block">
                    LIONSGATE NETWORK
                </h2>
                <p class="text-blue-600 font-mono text-[10px] tracking-widest uppercase mt-4">Entity Resolution & Intelligence Subsystem</p>
            </div>"""

content = content.replace(old_modal_header, new_modal_header)

with open("nemesis_id.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Landing page patched")
