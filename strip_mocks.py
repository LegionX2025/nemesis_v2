import re

file_path = "nemesis_id.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Define the tabs we want to clear out
tabs_to_clear = [
    "tab-profile",
    "tab-counterparties",
    "tab-assets",
    "tab-chains",
    "tab-transactions",
    "tab-balances",
    "tab-graph",
    "tab-aml",
    "tab-georisk",
    "tab-intelligence",
    "tab-ai-insights",
    "tab-report"
]

for tab in tabs_to_clear:
    # Use non-greedy match to find everything between <div class="tab-content..." id="tab"> and the next </div><!-- End tab -->
    # Actually, in the HTML, they might not have "End tab". We can use a trick: split by the tab declaration.
    pattern = rf'(<div class="tab-content[^>]*id="{tab}"[^>]*>)(.*?)(</div>\s*<!-- End {tab} -->)'
    
    # Just in case there is no "End tab", we'll just inject empty divs from JS and leave the HTML alone.
    pass

# Actually, the safest way to remove mock data without breaking the HTML structure is to let the JS overwrite the innerHTML of those tabs on load.
# The user wants the hardcoded mock data removed, which implies the HTML file itself shouldn't have it.
# Let's try splitting the content at `<main` and `</main>` and replacing the inside with clean empty tab containers.

main_content = """
    <!-- Main Content (Adjusted with left padding for left-nav) -->
    <main class="flex-grow overflow-y-auto p-4 md:p-6 pl-20 lg:pl-24 relative z-10" id="main-content">
        <div id="tab-profile" class="tab-content active"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        <div id="tab-counterparties" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        <div id="tab-assets" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        <div id="tab-chains" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        <div id="tab-transactions" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        <div id="tab-balances" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        
        <!-- Vis.js Graph Container -->
        <div id="tab-graph" class="tab-content">
            <div class="glass-panel rounded-xl p-4 mb-6 shadow-sm border border-slate-200">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xs font-black uppercase tracking-widest text-slate-800"><i class="fa-solid fa-project-diagram text-cyan-600"></i> Entity Trace Graph</h2>
                </div>
                <div id="trace-network"></div>
            </div>
        </div>

        <div id="tab-aml" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        <div id="tab-georisk" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        <div id="tab-intelligence" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        <div id="tab-ai-insights" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
        <div id="tab-report" class="tab-content"><div class="flex justify-center p-10"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-blue-500"></i></div></div>
    </main>
"""

# Find the main tag
start_main = content.find('<main')
end_main = content.find('</main>') + 7

if start_main != -1 and end_main != -1:
    content = content[:start_main] + main_content + content[end_main:]
    
    # Also strip the hardcoded graph data in initTraceGraph
    graph_mock = """const nodes = new vis.DataSet([
                { id: 1, label: 'SUBJECT EOA\\n0x742...', color: { background: '#ef4444', border: '#b91c1c' }, font: { color: '#ffffff' }, size: 30, level: 2 },
                { id: 2, label: 'Tornado Cash\\nMixer', color: { background: '#64748b', border: '#475569' }, font: { color: '#ffffff' }, size: 25, level: 1 },
                { id: 3, label: 'Stargate Router\\nBridge/Contract', color: { background: '#8b5cf6', border: '#6d28d9' }, font: { color: '#ffffff' }, size: 25, level: 3 },
                { id: 4, label: 'Binance Hot 14\\nCEX/Custodial', color: { background: '#f59e0b', border: '#d97706' }, font: { color: '#ffffff' }, size: 35, level: 4 }
            ]);

            const edges = new vis.DataSet([
                { id: 'e1', from: 2, to: 1, label: '🟢 100 ETH', font: { color: '#1e293b', align: 'horizontal', background: 'rgba(255,255,255,0.8)' }, width: 3, color: { color: '#ef4444' } },
                { id: 'e3', from: 1, to: 3, label: '🟣 5.5M USDC', font: { color: '#1e293b', align: 'horizontal', background: 'rgba(255,255,255,0.8)' }, width: 3, color: { color: '#8b5cf6' } },
                { id: 'e4', from: 1, to: 4, label: '🟠 400 ETH', font: { color: '#1e293b', align: 'horizontal', background: 'rgba(255,255,255,0.8)' }, width: 4, color: { color: '#f59e0b' } }
            ]);"""
            
    graph_empty = """const nodes = new vis.DataSet([]);
            const edges = new vis.DataSet([]);"""
    
    content = content.replace(graph_mock, graph_empty)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully stripped mock data from nemesis_id.html")
else:
    print("Failed to find main tags")
