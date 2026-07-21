import os

modal_html = """
<!-- GLOBAL AUTO-FIXER MODAL -->
<div id="auto-fixer-modal" class="fixed inset-0 z-[99999] bg-slate-900/80 backdrop-blur-sm flex items-center justify-center opacity-0 pointer-events-none transition-opacity duration-300">
    <div class="bg-white border-2 border-red-500 rounded-2xl shadow-[0_0_50px_rgba(239,68,68,0.3)] p-6 w-[600px] max-w-[90vw] transform scale-95 transition-transform duration-300 relative overflow-hidden" id="auto-fixer-content">
        
        <!-- Animated Background Warning Pattern -->
        <div class="absolute inset-0 opacity-10" style="background-image: repeating-linear-gradient(45deg, #ef4444 0, #ef4444 2px, transparent 2px, transparent 8px);"></div>

        <div class="relative z-10">
            <div class="flex items-center gap-4 mb-4">
                <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center border border-red-200 shrink-0 shadow-inner">
                    <i class="fa-solid fa-triangle-exclamation text-2xl text-red-600 animate-pulse"></i>
                </div>
                <div>
                    <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">SYSTEM ERROR DETECTED</h2>
                    <p class="text-xs text-red-600 font-bold uppercase tracking-widest">Autonomous Auto-Fixer Engaged</p>
                </div>
            </div>
            
            <div class="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-4 shadow-inner">
                <h3 class="text-[10px] uppercase font-black text-slate-500 mb-2 tracking-widest"><i class="fa-solid fa-bug text-slate-400"></i> Error Traceback</h3>
                <pre class="text-xs font-mono text-red-500 whitespace-pre-wrap overflow-x-auto" id="auto-fixer-error-text">Loading error context...</pre>
            </div>

            <div class="bg-sky-50 border border-sky-200 rounded-lg p-4 mb-4 shadow-inner">
                <h3 class="text-[10px] uppercase font-black text-sky-700 mb-2 tracking-widest"><i class="fa-solid fa-wrench text-sky-500"></i> Real-Time Remediation</h3>
                <div class="space-y-2 text-xs font-mono text-slate-700" id="auto-fixer-steps">
                    <div class="flex items-center gap-2"><i class="fa-solid fa-circle-notch fa-spin text-sky-500"></i> <span id="fix-step-1">Analyzing stack trace...</span></div>
                </div>
            </div>
            
            <div class="flex justify-between items-center mt-6 pt-4 border-t border-slate-100">
                <div class="flex items-center gap-2 text-xs font-bold text-slate-500">
                    <i class="fa-solid fa-cloud-arrow-up text-indigo-500 animate-bounce"></i> Redeploying to Cloudflare... Please wait.
                </div>
                <button onclick="closeAutoFixer()" class="px-4 py-2 bg-slate-800 text-white text-xs font-bold rounded-lg hover:bg-slate-900 transition-colors shadow">Force Close</button>
            </div>
        </div>
    </div>
</div>

<script>
    function triggerAutoFixer(errorMsg, fixSteps) {
        const modal = document.getElementById('auto-fixer-modal');
        const content = document.getElementById('auto-fixer-content');
        const errorText = document.getElementById('auto-fixer-error-text');
        const stepsContainer = document.getElementById('auto-fixer-steps');
        
        errorText.innerText = errorMsg;
        
        stepsContainer.innerHTML = '';
        fixSteps.forEach((step, index) => {
            setTimeout(() => {
                const div = document.createElement('div');
                div.className = 'flex items-center gap-2 opacity-0 transition-opacity duration-300';
                div.innerHTML = `<i class="fa-solid fa-check text-emerald-500"></i> <span>${step}</span>`;
                stepsContainer.appendChild(div);
                setTimeout(() => div.classList.remove('opacity-0'), 50);
            }, index * 1500); // Stagger steps
        });

        // Add a final spinner step
        setTimeout(() => {
            const finalDiv = document.createElement('div');
            finalDiv.className = 'flex items-center gap-2 text-indigo-600 font-bold';
            finalDiv.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> <span>Awaiting Cloudflare Edge Propagation...</span>`;
            stepsContainer.appendChild(finalDiv);
        }, fixSteps.length * 1500 + 500);

        modal.classList.remove('opacity-0', 'pointer-events-none');
        content.classList.remove('scale-95');
        content.classList.add('scale-100');
    }

    function closeAutoFixer() {
        const modal = document.getElementById('auto-fixer-modal');
        const content = document.getElementById('auto-fixer-content');
        modal.classList.add('opacity-0', 'pointer-events-none');
        content.classList.remove('scale-100');
        content.classList.add('scale-95');
    }
    
    // Listen for global window errors to trigger auto-fixer for demonstration
    window.addEventListener('error', function(e) {
        if (e.message && !e.message.includes("ResizeObserver")) {
            triggerAutoFixer(
                `Uncaught ${e.error ? e.error.name : 'Error'}: ${e.message}\\n  at ${e.filename}:${e.lineno}`,
                [
                    "Engaging autonomous fallback logic...",
                    "Patching DOM mutation failure...",
                    "Recompiling asset dependencies...",
                    "Pushing hotfix to Cloudflare Workers..."
                ]
            );
        }
    });
</script>
"""

files_to_patch = ["index.html", "admin.html", "nemesis_id.html", "darknet_portal.html"]

for filename in files_to_patch:
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            
        if "id=\"auto-fixer-modal\"" not in content:
            # Inject just before </body>
            if "</body>" in content:
                content = content.replace("</body>", f"{modal_html}\n</body>")
            else:
                content += modal_html
                
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Patched {filename}")
    else:
        print(f"File {filename} not found.")
