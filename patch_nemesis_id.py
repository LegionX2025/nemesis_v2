import re

file_path = "nemesis_id.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add fetch logic and dynamic rendering to the script section
script_injection = """
        // ==========================================
        // DYNAMIC DATA FETCHING & RENDERING
        // ==========================================
        async function fetchLiveNemesisData(address) {
            triggerLoader("Intercepting Blockchain Streams...");
            try {
                const res = await fetch(`/api/pipeline/prompt`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: "Analyze address " + address })
                });
                const data = await response.json();
                if (data.status === 'success' && data.pipeline_results.length > 0) {
                    const result = data.pipeline_results[0];
                    renderNemesisId(result, address);
                } else {
                    triggerAutoFixer("Data stream empty or failed.", ["Restarting pipeline..."]);
                }
            } catch(e) {
                console.error(e);
                triggerAutoFixer(e.message, ["Check backend connection."]);
            }
        }

        function renderNemesisId(intel, address) {
            // Update Header
            document.getElementById('header-address').innerHTML = `${address} <i class="fa-solid fa-copy text-xs text-slate-400"></i>`;
            
            // Build Profile Tab
            const profileHtml = `
                <div class="data-card p-6 border-l-4 border-indigo-500">
                    <h2 class="text-xl font-black uppercase tracking-widest text-slate-800 mb-4">Entity Profile</h2>
                    <div class="grid grid-cols-2 gap-4 text-sm font-mono text-slate-600">
                        <div><strong>Address:</strong> ${intel.address || address}</div>
                        <div><strong>Risk Score:</strong> ${intel.risk_score || 0}/100</div>
                        <div><strong>Label:</strong> ${intel.label || "Unknown"}</div>
                        <div><strong>Chain:</strong> ${intel.chain || "ETH"}</div>
                    </div>
                </div>
            `;
            document.getElementById('tab-profile').innerHTML = profileHtml;
            
            // Build Graph Data
            if(intel.nodes && intel.edges) {
                const nodes = new vis.DataSet(intel.nodes);
                const edges = new vis.DataSet(intel.edges);
                networkGraph.setData({nodes, edges});
            }
        }
        
        // Auto-run on load if target is in URL
        document.addEventListener('DOMContentLoaded', () => {
            const urlParams = new URLSearchParams(window.location.search);
            const target = urlParams.get('target');
            if(target) fetchLiveNemesisData(target);
        });
"""

# Inject script before the closing </script> of the main block (around line 1040)
content = content.replace("initQuantumBackground();\n        }", "initQuantumBackground();\n        }\n" + script_injection)

# Add an id to the header address so we can replace it easily
content = content.replace('<h1 class="text-xl font-mono font-bold text-slate-900 tracking-tight flex items-center gap-2 hover:text-blue-600 cursor-pointer transition" onclick="copyToClipboard(\'0x742d35Cc6634C0532925a3b844Bc454e4438f44e\')">', '<h1 id="header-address" class="text-xl font-mono font-bold text-slate-900 tracking-tight flex items-center gap-2 hover:text-blue-600 cursor-pointer transition" onclick="copyToClipboard(this.innerText)">')

# Empty out the static mock data in the tabs but leave the containers
def empty_tab(content, tab_id):
    pattern = re.compile(rf'(<div class="tab-content.*?id="{tab_id}">)(.*?)(</div><!-- End {tab_id} -->|</div>\s*<!--.*?-->|</div>\s*<div class="tab-content)', re.DOTALL)
    # This might be tricky with regex due to nested divs. It's safer to just inject a clear function in JS.
    return content

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched nemesis_id.html with dynamic fetch logic.")
