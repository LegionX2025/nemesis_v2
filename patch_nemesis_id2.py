import re

with open('nemesis_id.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_js = """
        function populateFromCache(address, data) {
            const { init, osint, ai, graph } = data;
            
            // Set Header basics
            document.getElementById('hdr-wallet').innerHTML = `${address} <i class="fa-regular fa-copy text-sm text-slate-500 hover:text-blue-500 transition"></i>`;
            document.getElementById('hdr-nemesis-id').innerText = `NEMESIS ID: NMS-${address.substring(2,8).toUpperCase()}`;
            document.getElementById('hdr-entity-resolve').innerText = init ? init.basic_label : 'Unknown Entity';
            
            let compositeData = {
                wallet_address: address,
                chain_detected: init ? init.chain : 'Unknown',
                risk_profile: { taxonomy: {}, risk_factors: [] },
                financial_metrics: {},
                raw_analysis: { asset_lifecycle: [], etherscan_metadata: {} },
                swarm_intelligence: { data: {} },
                graph: { nodes: [], edges: [] }
            };

            // 1. OSINT
            if(osint) {
                compositeData.risk_profile.classification = osint.is_alert ? 'HIGH RISK (CEX)' : 'STANDARD';
                compositeData.risk_profile.risk_score = osint.is_alert ? 95 : 30;
                compositeData.risk_profile.taxonomy.primary_classification = osint.label;
                updateHeaderRisk(compositeData);
                updateProfileGrid(compositeData);
                if (document.getElementById('tab-intelligence')) {
                    document.getElementById('tab-intelligence').innerHTML = `
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm font-mono text-sm">
                        <h3 class="text-indigo-800 font-black mb-4">RAW OSINT FUSION DATA</h3>
                        <pre class="bg-slate-900 text-emerald-400 p-4 rounded text-xs overflow-x-auto">${JSON.stringify(osint.osint, null, 2)}</pre>
                    </div>`;
                }
            }

            // 2. AI (Swarm Intelligence)
            if(ai) {
                if(ai.profile) {
                    compositeData.swarm_intelligence.data.operational_summary = ai.profile.summary || 'No summary available.';
                    compositeData.financial_metrics.total_inbound_usd = ai.profile.total_in_usd || 0;
                    compositeData.financial_metrics.total_outbound_usd = ai.profile.total_out_usd || 0;
                    compositeData.financial_metrics.current_balance_usd = ai.profile.balance_usd || 0;
                    compositeData.raw_analysis.etherscan_metadata.firstActivity = ai.profile.first_activity || 'Unknown';
                    compositeData.raw_analysis.etherscan_metadata.latestActivity = ai.profile.last_activity || 'Unknown';
                    updateProfileSummary(compositeData);
                }
                
                // Counterparties
                if(ai.counterparties && document.getElementById('tab-counterparties')) {
                    const cp = ai.counterparties;
                    let inRows = (cp.top_inbound || []).map(x => `<tr class="border-b"><td class="py-2 text-blue-600">${x.address}</td><td class="py-2 text-emerald-600">$${x.amount_usd}</td><td class="py-2">${x.entity}</td></tr>`).join('');
                    let outRows = (cp.top_outbound || []).map(x => `<tr class="border-b"><td class="py-2 text-blue-600">${x.address}</td><td class="py-2 text-red-600">$${x.amount_usd}</td><td class="py-2">${x.entity}</td></tr>`).join('');
                    document.getElementById('tab-counterparties').innerHTML = `
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                                <h3 class="font-black text-slate-800 mb-4 uppercase">Top Inbound</h3>
                                <table class="w-full text-sm font-mono text-left"><thead><tr class="text-slate-500 border-b"><th>Address</th><th>Amount (USD)</th><th>Entity</th></tr></thead><tbody>${inRows}</tbody></table>
                            </div>
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                                <h3 class="font-black text-slate-800 mb-4 uppercase">Top Outbound</h3>
                                <table class="w-full text-sm font-mono text-left"><thead><tr class="text-slate-500 border-b"><th>Address</th><th>Amount (USD)</th><th>Entity</th></tr></thead><tbody>${outRows}</tbody></table>
                            </div>
                        </div>
                    `;
                }
                
                // AML
                if(ai.aml && document.getElementById('tab-aml')) {
                    document.getElementById('tab-aml').innerHTML = `
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h3 class="font-black text-slate-800 mb-4 uppercase">AML Risk Profile</h3>
                        <div class="grid grid-cols-2 gap-4 font-mono text-sm">
                            <div class="bg-slate-50 p-4 rounded"><span class="text-slate-500">Risk Score:</span> <span class="font-bold text-red-600">${ai.aml.risk_score}/100</span></div>
                            <div class="bg-slate-50 p-4 rounded"><span class="text-slate-500">Category:</span> <span class="font-bold text-slate-800">${ai.aml.risk_category}</span></div>
                            <div class="bg-slate-50 p-4 rounded"><span class="text-slate-500">Exposure Rate:</span> <span class="font-bold text-orange-600">${ai.aml.exposure_rate}</span></div>
                            <div class="bg-slate-50 p-4 rounded"><span class="text-slate-500">Last Receivers:</span> <span class="font-bold text-slate-800">${ai.aml.last_receivers}</span></div>
                        </div>
                    </div>`;
                }

                // Georisk
                if(ai.georisk && document.getElementById('tab-georisk')) {
                    document.getElementById('tab-georisk').innerHTML = `
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm font-mono text-sm">
                        <h3 class="font-black text-slate-800 mb-4 uppercase">Geographic Footprint</h3>
                        <pre class="bg-slate-100 p-4 rounded">${JSON.stringify(ai.georisk.associated_ips, null, 2)}</pre>
                    </div>`;
                }

                // AI Report
                if(ai.report && document.getElementById('tab-report')) {
                    document.getElementById('tab-report').innerHTML = `
                    <div class="bg-white p-8 rounded-xl shadow-lg border border-slate-200 prose max-w-none">
                        <div class="flex justify-between items-center border-b pb-4 mb-6">
                            <h2 class="text-2xl font-black text-slate-800 uppercase tracking-widest m-0">FORENSIC REPORT</h2>
                            <button onclick="window.open('/api/export/package?address=${address}&chain=${compositeData.chain_detected}', '_blank')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-xs font-bold font-mono uppercase tracking-widest transition shadow-md"><i class="fa-solid fa-file-export mr-2"></i> Export Legal Package</button>
                        </div>
                        <h3 class="text-slate-800 font-bold mt-4">Methodology</h3>
                        <p class="text-slate-600 text-sm">${ai.report.methodology}</p>
                        <h3 class="text-slate-800 font-bold mt-4">Findings</h3>
                        <p class="text-slate-600 text-sm">${ai.report.findings}</p>
                        <h3 class="text-slate-800 font-bold mt-4">Timeline</h3>
                        <p class="text-slate-600 text-sm">${ai.report.timeline}</p>
                        <h3 class="text-slate-800 font-bold mt-4">Recommendations</h3>
                        <p class="text-slate-600 text-sm">${ai.report.recommendations}</p>
                    </div>`;
                    
                    // Unhide the report tab if it was hidden
                    document.getElementById('tab-report').classList.remove('hidden');
                }
            }

            // 3. Graph
            if(graph) {
                const realTxs = graph.real_transactions || [];
                const graphNodes = [{ id: address, label: 'Target', color: '#3b82f6', value: 30 }];
                const graphEdges = [];
                const addedNodes = new Set([address.toLowerCase()]);
                
                let totalIn = 0; let totalOut = 0;
                const formattedTxs = realTxs.map(txObj => {
                    const tx = txObj.tx;
                    const fromAddr = tx.from || 'Unknown';
                    const toAddr = tx.to || 'Unknown';
                    const valUsd = (parseFloat(tx.value) || 0) * 3100 / 1e18; // approx ETH price for demo
                    
                    if (toAddr.toLowerCase() === address.toLowerCase()) totalIn += valUsd;
                    if (fromAddr.toLowerCase() === address.toLowerCase()) totalOut += valUsd;
                    
                    if (!addedNodes.has(fromAddr.toLowerCase())) {
                        if (tx.from_cex) {
                            graphNodes.push({ id: fromAddr, label: 'CEX: ' + tx.from_cex, color: '#ef4444', value: 20, font: {color: 'white'} });
                        } else {
                            graphNodes.push({ id: fromAddr, label: 'Source', color: '#94a3b8', value: 10 });
                        }
                        addedNodes.add(fromAddr.toLowerCase());
                    }
                    if (!addedNodes.has(toAddr.toLowerCase())) {
                        if (tx.to_cex) {
                            graphNodes.push({ id: toAddr, label: 'CEX: ' + tx.to_cex, color: '#ef4444', value: 25, font: {color: 'white'}, shape: 'star' });
                        } else {
                            graphNodes.push({ id: toAddr, label: 'Destination', color: '#94a3b8', value: 10 });
                        }
                        addedNodes.add(toAddr.toLowerCase());
                    }
                    graphEdges.push({ from: fromAddr, to: toAddr, value: valUsd || 1 });
                    
                    return { hash: tx.hash, from: fromAddr, to: toAddr, value_usd: valUsd, timestamp: tx.timeStamp ? new Date(tx.timeStamp * 1000).toLocaleString() : 'Recent' };
                });
                
                compositeData.graph.nodes = graphNodes;
                compositeData.graph.edges = graphEdges;
                compositeData.raw_analysis.asset_lifecycle = formattedTxs;
                
                if (!compositeData.financial_metrics.current_balance_usd) {
                    compositeData.financial_metrics.total_inbound_usd = totalIn;
                    compositeData.financial_metrics.total_outbound_usd = totalOut;
                    compositeData.financial_metrics.current_balance_usd = totalIn - totalOut;
                }
                updateGraphPane(compositeData);
            }
            
            window.CURRENT_DATA = compositeData;
            
            // Also need to render TX table if we have lifecycle data
            if (compositeData.raw_analysis && compositeData.raw_analysis.asset_lifecycle) {
                if (typeof renderTxTable === 'function') {
                    renderTxTable(compositeData.raw_analysis.asset_lifecycle);
                }
            }
        }
"""

# We need to replace the old function populateFromCache(address, data) { ... }
start_token = "function populateFromCache(address, data) {"
end_token = "async function executeNemesisSearch() {"

start_idx = html.find(start_token)
end_idx = html.find(end_token)

if start_idx != -1 and end_idx != -1:
    new_html = html[:start_idx] + new_js + html[end_idx:]
    with open('nemesis_id.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("nemesis_id.html updated successfully with AI/OSINT UI mappings.")
else:
    print("Could not find the target functions to replace in nemesis_id.html.")
