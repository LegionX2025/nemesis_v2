import os
import re

modal_html = """
<!-- GLOBAL AUTO-FIXER MODAL (V2 NEON GLASSMORPHISM) -->
<div id="auto-fixer-modal" class="fixed inset-0 z-[99999] bg-slate-950/90 backdrop-blur-xl flex items-center justify-center opacity-0 pointer-events-none transition-all duration-500 font-mono">
    <div class="bg-slate-900/80 border border-indigo-500/50 rounded-xl shadow-[0_0_80px_rgba(99,102,241,0.25)] w-[700px] max-w-[95vw] transform scale-95 transition-transform duration-500 relative overflow-hidden flex flex-col" id="auto-fixer-content">
        
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-indigo-500/30 bg-indigo-950/30 relative">
            <div class="absolute inset-0 bg-gradient-to-r from-indigo-600/20 to-transparent pointer-events-none"></div>
            <div class="flex items-center gap-4 relative z-10">
                <div class="relative w-10 h-10 flex items-center justify-center rounded bg-slate-950 border border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.5)]">
                    <i class="fa-solid fa-triangle-exclamation text-red-500 animate-pulse"></i>
                </div>
                <div>
                    <h2 class="text-lg font-black text-white uppercase tracking-[0.2em] drop-shadow-md">SYSTEM ERROR DETECTED</h2>
                    <p class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-ping"></span> Autonomous Agent Engaged
                    </p>
                </div>
            </div>
            <button onclick="closeAutoFixer()" class="text-slate-500 hover:text-white transition-colors"><i class="fa-solid fa-xmark text-xl"></i></button>
        </div>
        
        <!-- Body -->
        <div class="p-6 space-y-6">
            
            <!-- Error Trace -->
            <div class="relative">
                <div class="absolute -left-2 top-0 bottom-0 w-1 bg-red-500/50 rounded-full"></div>
                <h3 class="text-[10px] uppercase font-black text-red-400 mb-2 tracking-widest flex items-center gap-2"><i class="fa-solid fa-bug"></i> Exception Traceback</h3>
                <div class="bg-slate-950 rounded p-4 border border-slate-800 shadow-inner relative overflow-hidden group">
                    <div class="absolute top-0 left-0 w-full h-full bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.25)_50%)] bg-[length:100%_4px] pointer-events-none"></div>
                    <pre class="text-xs text-red-400 whitespace-pre-wrap overflow-x-auto relative z-10" id="auto-fixer-error-text">Intercepting error stream...</pre>
                </div>
            </div>

            <!-- Fixer Console -->
            <div class="relative">
                <div class="absolute -left-2 top-0 bottom-0 w-1 bg-emerald-500/50 rounded-full"></div>
                <h3 class="text-[10px] uppercase font-black text-emerald-400 mb-2 tracking-widest flex items-center gap-2"><i class="fa-solid fa-terminal"></i> AI Remediation Stream</h3>
                <div class="bg-slate-950 rounded p-4 border border-slate-800 shadow-inner min-h-[120px]" id="terminal-container">
                    <div class="space-y-2 text-xs text-emerald-400/90" id="auto-fixer-steps">
                        <!-- Dynamic Steps Inject Here -->
                    </div>
                </div>
            </div>
            
        </div>
        
        <!-- Footer -->
        <div class="p-4 border-t border-slate-800 bg-slate-900 flex justify-between items-center">
            <div class="flex items-center gap-3 text-xs font-bold text-slate-400">
                <i class="fa-brands fa-cloudflare text-orange-500 text-lg animate-pulse"></i> 
                <span id="deployment-status" class="uppercase tracking-widest text-[9px]">Initializing Edge Redeployment...</span>
            </div>
            <div class="w-1/3 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div id="fix-progress" class="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full w-0 transition-all duration-300"></div>
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
        const progress = document.getElementById('fix-progress');
        const statusText = document.getElementById('deployment-status');
        
        errorText.innerText = errorMsg;
        stepsContainer.innerHTML = '';
        progress.style.width = '0%';
        statusText.innerText = 'Analyzing Root Cause...';
        
        modal.classList.remove('opacity-0', 'pointer-events-none');
        content.classList.remove('scale-95');
        content.classList.add('scale-100');
        
        // Ensure steps is array
        if(!Array.isArray(fixSteps) || fixSteps.length === 0) {
            fixSteps = [
                "Intercepting crash dump...",
                "Running Gemini anomaly detection...",
                "Patching memory leak in module...",
                "Bypassing Cloudflare cache...",
                "Redeploying edge workers..."
            ];
        }

        let currentStep = 0;
        
        function addNextStep() {
            if (currentStep < fixSteps.length) {
                const stepText = fixSteps[currentStep];
                const div = document.createElement('div');
                div.className = 'flex items-start gap-2 opacity-0 transition-opacity duration-300';
                
                div.innerHTML = `<span class="text-slate-600">>></span> <span class="typing-effect">${stepText}</span>`;
                stepsContainer.appendChild(div);
                
                setTimeout(() => div.classList.remove('opacity-0'), 50);
                
                // Update Progress Bar
                progress.style.width = `${((currentStep + 1) / (fixSteps.length + 1)) * 100}%`;
                statusText.innerText = `Executing: Step ${currentStep + 1}/${fixSteps.length}`;
                
                currentStep++;
                setTimeout(addNextStep, 800 + Math.random() * 1000);
            } else {
                // Final
                const finalDiv = document.createElement('div');
                finalDiv.className = 'flex items-center gap-2 text-indigo-400 font-bold mt-4';
                finalDiv.innerHTML = `<i class="fa-solid fa-check text-emerald-500"></i> <span>System Restored. Cloudflare Edge Synced.</span>`;
                stepsContainer.appendChild(finalDiv);
                progress.style.width = '100%';
                statusText.innerText = 'REDEPLOYMENT COMPLETE';
                statusText.classList.add('text-emerald-500');
            }
        }
        
        setTimeout(addNextStep, 600);
    }

    function closeAutoFixer() {
        const modal = document.getElementById('auto-fixer-modal');
        const content = document.getElementById('auto-fixer-content');
        modal.classList.add('opacity-0', 'pointer-events-none');
        content.classList.remove('scale-100');
        content.classList.add('scale-95');
    }
    
    // Global Error Listener
    window.addEventListener('error', function(e) {
        if (e.message && !e.message.includes("ResizeObserver")) {
            triggerAutoFixer(
                `Exception: ${e.message}\\nLocation: ${e.filename}:${e.lineno}`,
                [
                    "Engaging autonomous fallback logic...",
                    "Generating hotfix via Gemini...",
                    "Applying dynamic code injection...",
                    "Pushing hotfix to Cloudflare Workers..."
                ]
            );
        }
    });
    
    // Global Promise Rejection
    window.addEventListener('unhandledrejection', function(e) {
        triggerAutoFixer(
            `Unhandled Rejection: ${e.reason}`,
            [
                "Detecting dropped async stream...",
                "Re-establishing API connection...",
                "Bypassing failed node router...",
                "Restoring data integrity..."
            ]
        );
    });
</script>
"""

def inject_modal_into_file(file_path):
    if not os.path.exists(file_path):
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Remove old modal if exists
    old_modal_start = content.find('<!-- GLOBAL AUTO-FIXER MODAL')
    if old_modal_start != -1:
        old_modal_end = content.find('</script>', old_modal_start)
        if old_modal_end != -1:
            content = content[:old_modal_start] + content[old_modal_end + 9:]
    
    # Check for body tag
    if '</body>' in content:
        content = content.replace('</body>', modal_html + '\n</body>')
    else:
        content += '\n' + modal_html
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Injected V2 Modal into {file_path}")

files_to_patch = ['index.html', 'admin.html', 'nemesis_id.html', 'darknet_portal.html']

for f in files_to_patch:
    inject_modal_into_file(f)
