import re

with open('C:\\Users\\LEGIONX\\Downloads\\nemesis\\tracer_scripts\\tracer.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the mockData arrays and simulateDataStream logic correctly.
match = re.search(r'function simulateDataStream\(\) \{', content)
if match:
    start_idx = match.start()
    end_match = re.search(r'function changeLayout', content[start_idx:])
    if end_match:
        end_idx = start_idx + end_match.start()
        
        ws_logic = '''
        // WS connection
        const ws = new WebSocket(window.WS_URL + '/api/ws/trace');
        let isPaused = false;
        let pendingMessages = [];

        window.pauseTrace = function() { isPaused = true; document.getElementById('status').innerHTML = '<span class="text-amber-600 font-bold">Trace Paused</span>'; };
        window.resumeTrace = function() { 
            isPaused = false; 
            document.getElementById('status').innerHTML = '<span class="text-blue-600">Trace Running...</span>'; 
            while(pendingMessages.length > 0) {
                processWSMessage(pendingMessages.shift());
            }
        };

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (isPaused) {
                pendingMessages.push(data);
            } else {
                processWSMessage(data);
            }
        };

        ws.onopen = function() {
            console.log('WS Connected');
        };

        function processWSMessage(data) {
            if (data.type === 'INIT') {
                document.getElementById('status').innerHTML = '<span class="text-blue-600">Trace Running...</span>';
                nodes.clear(); edges.clear(); allNodesMap.clear(); allEdgesMap.clear();
                document.getElementById('tx-log-body').innerHTML = '';
                
                data.seeds.forEach(seed => {
                    nodes.add({ id: seed, label: '<b>START</b>\\n<span style="color:#3b82f6; font-size:8px;">' + seed.substring(0,6) + '...' + '</span>', image: getSafeIconUrl(seed, false, false) });
                    allNodesMap.set(seed, {id: seed});
                });
                network.fit({animation: true});
            } else if (data.type === 'LEDGER') {
                const edgeData = data.data;
                const txHash = edgeData.tx || edgeData.hash || 'UNKNOWN_TX';
                const amount = edgeData.amount || edgeData.usd_value || 0;
                const ticker = edgeData.ticker || edgeData.asset || 'N/A';
                
                // Add From Node if missing
                if(!allNodesMap.has(edgeData.from)) {
                    nodes.add({ id: edgeData.from, label: '<b>' + (edgeData.from.substring(0,6)) + '</b>\\n<span style="color:#94a3b8; font-size:8px;">' + edgeData.from.substring(0,8) + '...' + '</span>', image: getSafeIconUrl(edgeData.from, false, false) });
                    allNodesMap.set(edgeData.from, edgeData.from);
                }
                // Add To Node if missing
                if(!allNodesMap.has(edgeData.to)) {
                    let toLabel = edgeData.receiver_entity || 'UNKNOWN';
                    let isCex = toLabel.toUpperCase().includes("EXCHANGE") || toLabel.toUpperCase().includes("BINANCE");
                    nodes.add({ id: edgeData.to, label: '<b>' + toLabel + '</b>\\n<span style="color:#94a3b8; font-size:8px;">' + edgeData.to.substring(0,8) + '...' + '</span>', image: getSafeIconUrl(toLabel, false, isCex) });
                    allNodesMap.set(edgeData.to, edgeData.to);
                }

                if(!allEdgesMap.has(txHash)) {
                    edges.add({ id: txHash, from: edgeData.from, to: edgeData.to, label: '<b><span style="color:#ef4444;">↓ OUTFLOW</span></b>\\n<span style="color:#ef4444;">$' + amount.toLocaleString() + '</span>\\n<span style="font-family:monospace; color:#94a3b8;">' + txHash.substring(0,6) + '...' + '</span>' });
                    allEdgesMap.set(txHash, edgeData);
                    
                    let logHtml = `
                    <tr class="hover:bg-blue-50 transition-colors cursor-pointer">
                        <td class="p-2 pl-4 border-b border-slate-100">${new Date().toISOString().replace('T', ' ').substring(0,19)}</td>
                        <td class="p-2 border-b border-slate-100"><span class="bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded text-slate-600 font-bold">${ticker}</span></td>
                        <td class="p-2 border-b border-slate-100 text-blue-600 hover:underline">${txHash}</td>
                        <td class="p-2 border-b border-slate-100">${edgeData.from}</td>
                        <td class="p-2 border-b border-slate-100">${edgeData.to}</td>
                        <td class="p-2 border-b border-slate-100 font-bold text-slate-800">${edgeData.receiver_entity || 'UNKNOWN'}</td>
                        <td class="p-2 border-b border-slate-100 text-right pr-4 font-black text-emerald-600">$${amount.toLocaleString()}</td>
                        <td class="p-2 border-b border-slate-100">${edgeData.edge_type || 'Transfer'}</td>
                        <td class="p-2 border-b border-slate-100 text-slate-500">${edgeData.threat_level || 'Routing'}</td>
                        <td class="p-2 border-b border-slate-100 text-[9px]">${edgeData.from}</td>
                        <td class="p-2 border-b border-slate-100 font-bold text-emerald-600">99%</td>
                        <td class="p-2 border-b border-slate-100 text-slate-500 text-[10px]">On-Chain</td>
                        <td class="p-2 border-b border-slate-100 text-slate-500 text-[10px]">Trace match</td>
                    </tr>`;
                    document.getElementById('tx-log-body').insertAdjacentHTML('afterbegin', logHtml);
                    
                    let total = parseFloat(document.getElementById('total-traced-widget').innerText.replace(/[^0-9.-]+/g,"")) || 0;
                    document.getElementById('total-traced-widget').innerText = "$" + (total + amount).toLocaleString(undefined, {minimumFractionDigits: 2});
                }
            } else if (data.type === 'COMPLETE') {
                document.getElementById('status').innerHTML = '<span class="text-emerald-600 font-bold">Trace Complete</span>';
            }
        }

        window.submitTrace = function() {
            const seeds = document.getElementById('seed-input').value.split('\\n').map(s=>s.trim()).filter(s=>s);
            const targetAmount = document.getElementById('target-amount').value || "1000";
            const network = document.getElementById('chain-select').value || "AUTO";
            const maxDepth = document.getElementById('max-depth').value || "5";
            
            if (seeds.length === 0) return alert('Enter at least one seed');
            
            document.getElementById('trace-id-val').innerText = 'NMS-' + Math.floor(Math.random()*90000 + 10000);
            
            ws.send(JSON.stringify({
                type: 'START_TRACE',
                seeds: seeds,
                target_amount: targetAmount,
                network: network,
                max_depth: parseInt(maxDepth)
            }));
        }

        // --- ADDED MISSING FUNCTIONS ---
        window.handleAutoDetect = function() {
            const val = document.getElementById('landing-seed-input').value;
            const badge = document.getElementById('auto-detect-badge');
            if (val && val.length > 5) {
                if (badge) badge.classList.remove('hidden');
            } else {
                if (badge) badge.classList.add('hidden');
            }
        }

        window.handleCurrencyDetect = function() {
            // Optional stub
        }

        window.initiateLandingTrace = function() {
            const seed = document.getElementById('landing-seed-input').value;
            if(!seed) return alert('Enter a seed address');
            document.getElementById('seed-input').value = seed;
            openContentPage('tracing_engine');
            setTimeout(() => {
                submitTrace();
            }, 500);
        }
        '''
        
        content = content[:start_idx] + ws_logic + "\n        " + content[end_idx:]

        content = content.replace("simulateDataStream();", "")
        content = content.replace('<a href="#" target="_blank"><i class="fa-solid fa-id-card text-fuchsia-500"></i> Nemesis ID</a>', '<a href="/nemesis_id" target="_blank"><i class="fa-solid fa-id-card text-fuchsia-500"></i> Nemesis ID</a>')
        content = content.replace('<a href="#" class="hover:text-fuchsia-600 cursor-pointer transition flex items-center gap-2"><i class="fa-solid fa-id-card text-fuchsia-500"></i> Nemesis ID</a>', '<a href="/nemesis_id" class="hover:text-fuchsia-600 cursor-pointer transition flex items-center gap-2"><i class="fa-solid fa-id-card text-fuchsia-500"></i> Nemesis ID</a>')
        
        with open('C:\\Users\\LEGIONX\\Downloads\\nemesis\\tracer_scripts\\tracer.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Patched successfully")
else:
    print("Could not find simulateDataStream function")
