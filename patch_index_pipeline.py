import os

prompt_ui_html = """
<!-- INTELLIGENCE PIPELINE PROMPT INPUT -->
<div class="max-w-4xl mx-auto mb-8 relative z-20">
    <div class="bg-white/95 backdrop-blur-xl border border-indigo-200 rounded-2xl shadow-2xl p-6 transition-all focus-within:shadow-[0_0_30px_rgba(99,102,241,0.2)] focus-within:border-indigo-400">
        <h3 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-4 flex items-center gap-2">
            <i class="fa-solid fa-sparkles text-indigo-500"></i> NEMESIS Intelligence Pipeline
        </h3>
        <textarea id="pipeline-prompt" rows="3" class="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none placeholder-slate-400 transition" placeholder="Enter target addresses, hashes, or unstructured text to extract intelligence and execute tracing..."></textarea>
        
        <div class="flex justify-between items-center mt-4">
            <div class="flex items-center gap-4 text-xs font-bold text-slate-500">
                <button class="flex items-center gap-2 hover:text-indigo-600 transition" onclick="document.getElementById('file-upload').click()">
                    <i class="fa-solid fa-file-import"></i> Import File
                </button>
                <input type="file" id="file-upload" class="hidden" accept=".txt,.csv,.json" />
                <span class="bg-indigo-50 text-indigo-600 px-2 py-1 rounded flex items-center gap-1">
                    <i class="fa-solid fa-brain"></i> Gemini Integration Active
                </span>
            </div>
            <button id="run-pipeline-btn" class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg text-xs font-bold uppercase tracking-widest shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2" onclick="executeIntelligencePipeline()">
                Execute Pipeline <i class="fa-solid fa-arrow-right"></i>
            </button>
        </div>
    </div>
</div>

<!-- FORENSIC REPORT CONTAINER -->
<div id="forensic-report-container" class="max-w-4xl mx-auto mb-8 hidden relative z-20">
    <div class="bg-white border-2 border-slate-800 rounded-xl p-8 shadow-2xl font-serif text-slate-800">
        <div class="text-center border-b-2 border-slate-300 pb-4 mb-6">
            <h1 class="text-3xl font-black uppercase tracking-widest text-slate-900">NEMESIS FORENSIC DOSSIER</h1>
            <p class="text-sm text-slate-500 font-mono mt-2" id="forensic-timestamp"></p>
        </div>
        <div class="prose max-w-none text-sm leading-relaxed" id="forensic-content">
            <!-- Content Injected via JS -->
        </div>
        <div class="mt-8 flex justify-end">
            <button class="bg-slate-800 text-white px-4 py-2 rounded text-xs font-bold font-sans uppercase hover:bg-slate-700 shadow" onclick="window.print()"><i class="fa-solid fa-print"></i> Export to PDF</button>
        </div>
    </div>
</div>

<script>
    async function executeIntelligencePipeline() {
        const promptText = document.getElementById('pipeline-prompt').value;
        const btn = document.getElementById('run-pipeline-btn');
        const reportContainer = document.getElementById('forensic-report-container');
        const reportContent = document.getElementById('forensic-content');
        
        if (!promptText.trim()) return;
        
        btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...`;
        btn.classList.add('opacity-75', 'cursor-not-allowed');
        
        try {
            const response = await fetch('/api/pipeline/prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: promptText })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                reportContainer.classList.remove('hidden');
                document.getElementById('forensic-timestamp').innerText = `Generated: ${new Date().toISOString()}`;
                
                let contentHTML = `<h3 class="text-lg font-bold">Summary Objectives & Goals</h3>
                                   <p>Target extracted addresses: <strong>${data.extracted_addresses.join(', ')}</strong></p>
                                   <h3 class="text-lg font-bold mt-4">Intelligence Analysis</h3>
                                   <div class="p-4 bg-slate-50 border border-slate-200 rounded font-mono text-xs whitespace-pre-wrap">${data.forensic_report}</div>`;
                
                reportContent.innerHTML = contentHTML;
                
                // If dashboard graph function exists, try to load the first address
                if (data.extracted_addresses.length > 0 && typeof startDissect === 'function') {
                    const targetInput = document.getElementById('target-address');
                    if (targetInput) {
                        targetInput.value = data.extracted_addresses[0];
                        startDissect();
                    }
                }
            } else {
                alert('Pipeline Error: ' + data.message);
            }
        } catch (error) {
            console.error(error);
            // Trigger auto fixer if available
            if (typeof triggerAutoFixer === 'function') {
                triggerAutoFixer("Pipeline API Failure: " + error.message, ["Restarting Pipeline API", "Engaging Gemini Fallback"]);
            }
        } finally {
            btn.innerHTML = `Execute Pipeline <i class="fa-solid fa-arrow-right"></i>`;
            btn.classList.remove('opacity-75', 'cursor-not-allowed');
        }
    }
</script>
"""

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

if "INTELLIGENCE PIPELINE PROMPT INPUT" not in content:
    # We will inject this at the start of the "COMMAND CENTER TAB" right after the h2 text
    target = '<div class="tab-content active space-y-4" id="command-center">'
    if target in content:
        content = content.replace(target, target + "\n" + prompt_ui_html)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Injected Intelligence Pipeline Prompt UI into index.html")
    else:
        print("Could not find COMMAND CENTER TAB in index.html to inject UI.")
else:
    print("UI already injected.")
