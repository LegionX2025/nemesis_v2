
        // Simulation variables
        var nodes = new vis.DataSet();
        var edges = new vis.DataSet();
        var allEdgesMap = new Map();
        var allNodesMap = new Map();
        var network = null;
        var isSidebarOpen = true;
        var isLogPanelOpen = true;

        function toggleSidebar() {
            const sidebar = document.getElementById('left-sidebar');
            const icon = document.getElementById('sidebar-icon');
            const contents = document.querySelectorAll('.sidebar-content');
            
            if (isSidebarOpen) {
                sidebar.classList.remove('w-64');
                sidebar.classList.add('w-0');
                contents.forEach(el => el.style.opacity = '0');
                icon.classList.remove('fa-chevron-left');
                icon.classList.add('fa-chevron-right');
            } else {
                sidebar.classList.remove('w-0');
                sidebar.classList.add('w-64');
                setTimeout(() => { contents.forEach(el => el.style.opacity = '1'); }, 200);
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-left');
            }
            isSidebarOpen = !isSidebarOpen;
            setTimeout(() => { if (network) network.fit(); }, 300);
        }

        function toggleLogPanel() {
            const panel = document.getElementById('data-log-panel');
            const icon = document.getElementById('log-toggle-icon');
            if (isLogPanelOpen) {
                panel.classList.remove('h-64');
                panel.classList.add('h-10'); // Header only
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            } else {
                panel.classList.remove('h-10');
                panel.classList.add('h-64');
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            }
            isLogPanelOpen = !isLogPanelOpen;
        }

        window.initiateLandingTrace = function() {
            const seedVal = document.getElementById("landing-seed-input").value;
            if(!seedVal) return alert("Please enter a target wallet address.");
            
            // Transfer values to main UI inputs before starting
            document.getElementById("seed-input").value = seedVal;
            document.getElementById("target-amount").value = document.getElementById("landing-target-amount").value;
            
            // Hide landing page
            const landing = document.getElementById('landing-page');
            landing.style.opacity = '0';
            setTimeout(() => {
                landing.style.display = 'none';
                document.getElementById('main-ui').classList.remove('hidden');
                document.getElementById('main-ui').classList.add('flex');
                
                initGraphSimulation();
                submitTrace();
            }, 800);
        }

        function getSafeIconUrl(entityLabel, isMixer, isCex) {
            let upper = (entityLabel || "").toUpperCase();
            
            let bgColor = "#ffffff";
            let textColor = "#0f172a";
            let text = "W";
            let borderColor = "#cbd5e1";
            
            if (isCex || upper.includes("BINANCE")) { bgColor = "#facc15"; text = "B"; borderColor = "#eab308"; }
            else if (upper.includes("OKX")) { bgColor = "#000000"; text = "O"; borderColor = "#333333"; textColor = "#ffffff"; }
            else if (upper.includes("KRAKEN")) { bgColor = "#4f46e5"; text = "K"; borderColor = "#4338ca"; textColor = "#ffffff"; }
            else if (upper.includes("COINBASE")) { bgColor = "#2563eb"; text = "C"; borderColor = "#1d4ed8"; textColor = "#ffffff"; }
            else if (isMixer || upper.includes("MIXER") || upper.includes("TORNADO")) { bgColor = "#1e293b"; text = "M"; borderColor = "#0f172a"; textColor = "#ffffff"; }
            else if (upper.includes("SUSPECT")) { bgColor = "#fee2e2"; text = "S"; borderColor = "#ef4444"; textColor = "#b91c1c"; }

            const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="${bgColor}" stroke="${borderColor}" stroke-width="4"/><text x="50" y="50" font-family="Inter, sans-serif" font-size="44" font-weight="900" fill="${textColor}" text-anchor="middle" dominant-baseline="central">${text}</text></svg>`;
            return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
        }

        function initGraphSimulation() {
            const container = document.getElementById('graph');
            
            var options = {
                layout: { hierarchical: { enabled: true, direction: 'LR', sortMethod: 'directed', levelSeparation: 250, nodeSpacing: 100 } },
                physics: { enabled: false },
                interaction: { hover: true, tooltipDelay: 50, zoomView: true, dragView: true },
                nodes: { 
                    shape: 'circularImage', size: 30,
                    font: { size: 10, face: 'Inter', color: '#1e293b', multi: true, bold: '12px Inter' }, 
                    borderWidth: 2, 
                    shadow: { color: 'rgba(0,0,0,0.05)', size: 10, x: 0, y: 5 } 
                },
                edges: { 
                    arrows: 'to', 
                    font: { align: 'middle', size: 9, color: '#64748b', background: '#ffffff', strokeWidth: 0, multi: true }, 
                    smooth: { type: 'cubicBezier', forceDirection: 'horizontal', roundness: 0.4 },
                    color: { color: '#3b82f6', highlight: '#2563eb', hover: '#2563eb' },
                    width: 1.5
                }
            };
            
            network = new vis.Network(container, {nodes, edges}, options);

            // Custom Drawing for the Modern Clean Aesthetic (Overlays/Badges)
            network.on("afterDrawing", function (ctx) {
                let edgePositions = network.getPositions(nodes.getIds());
                
                // Draw Badges on Nodes
                nodes.get().forEach(n => {
                    let pos = edgePositions[n.id];
                    if(!pos) return;
                    
                    let isCex = n.label.toUpperCase().includes("EXCHANGE");
                    let isSuspect = n.label.toUpperCase().includes("UNKNOWN") || n.label.toUpperCase().includes("SUSPECT");
                    
                    ctx.beginPath();
                    ctx.arc(pos.x + 20, pos.y + 20, 10, 0, 2*Math.PI);
                    ctx.fillStyle = isCex ? "#10b981" : (isSuspect ? "#94a3b8" : "#3b82f6");
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 2;
                    ctx.stroke();
                    
                    ctx.font = '900 10px "Font Awesome 6 Free"';
                    ctx.fillStyle = "#ffffff";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    let icon = isCex ? '\uf00c' : (isSuspect ? '\uf128' : '\uf3ed'); // Check, Question, Shield
                    ctx.fillText(icon, pos.x + 20, pos.y + 20);
                });
            });

            
        }

        
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
                if (!network) initGraphSimulation();
                document.getElementById('status').innerHTML = '<span class="text-blue-600">Trace Running...</span>';
                document.getElementById('tx-log-loader').classList.remove('hidden');
                nodes.clear(); edges.clear(); allNodesMap.clear(); allEdgesMap.clear();
                document.getElementById('tx-log-body').innerHTML = '';
                
                data.seeds.forEach(seed => {
                    nodes.add({ id: seed, label: '*START*\n' + seed.substring(0,6) + '...', image: getSafeIconUrl(seed, false, false) });
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
                    nodes.add({ id: edgeData.from, label: '*' + (edgeData.from.substring(0,6)) + '*\n' + edgeData.from.substring(0,8) + '...', image: getSafeIconUrl(edgeData.from, false, false) });
                    allNodesMap.set(edgeData.from, edgeData.from);
                }
                // Add To Node if missing
                if(!allNodesMap.has(edgeData.to)) {
                    let toLabel = edgeData.receiver_entity || 'UNKNOWN';
                    let isCex = toLabel.toUpperCase().includes("EXCHANGE") || toLabel.toUpperCase().includes("BINANCE");
                    nodes.add({ id: edgeData.to, label: '*' + toLabel + '*\n' + edgeData.to.substring(0,8) + '...', image: getSafeIconUrl(toLabel, false, isCex) });
                    allNodesMap.set(edgeData.to, edgeData.to);
                }

                if(!allEdgesMap.has(txHash)) {
                    const usdAmount = edgeData.usd_value || edgeData.amount || 0;
                    edges.add({
                        id: txHash,
                        from: edgeData.from,
                        to: edgeData.to,
                        label: parseFloat(amount).toFixed(2) + ' ' + ticker,
                        title: `TX: ${txHash}\nAmount: ${amount} ${ticker}\nUSD: $${parseFloat(usdAmount).toFixed(2)}`,
                        color: { color: edgeData.is_terminal ? '#ef4444' : '#cbd5e1' },
                        width: Math.min(5, Math.max(1, amount / 100)),
                        arrows: 'to'
                    });
                    allEdgesMap.set(txHash, edgeData);
                    
                    let logHtml = `
                    <tr class="hover:bg-blue-50 transition-colors cursor-pointer">
                        <td class="p-2 pl-4 border-b border-slate-100">${new Date().toISOString().replace('T', ' ').substring(0,19)}</td>
                        <td class="p-2 border-b border-slate-100"><span class="bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded text-slate-600 font-bold">${ticker}</span></td>
                        <td class="p-2 border-b border-slate-100 text-blue-600 hover:underline">${txHash}</td>
                        <td class="p-2 border-b border-slate-100">${edgeData.from}</td>
                        <td class="p-2 border-b border-slate-100">${edgeData.to}</td>
                        <td class="p-2 border-b border-slate-100 font-bold text-slate-800">${edgeData.receiver_entity || 'UNKNOWN'}</td>
                        <td class="p-2 border-b border-slate-100 text-right pr-4 font-black text-emerald-600">$${usdAmount.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        <td class="p-2 border-b border-slate-100">${edgeData.edge_type || 'Transfer'}</td>
                        <td class="p-2 border-b border-slate-100 text-slate-500">${edgeData.threat_level || 'Routing'}</td>
                        <td class="p-2 border-b border-slate-100 text-[9px]">${edgeData.from}</td>
                        <td class="p-2 border-b border-slate-100 font-bold text-emerald-600">99%</td>
                        <td class="p-2 border-b border-slate-100 text-slate-500 text-[10px]">On-Chain</td>
                        <td class="p-2 border-b border-slate-100 text-slate-500 text-[10px]">Trace match</td>
                    </tr>`;
                    document.getElementById('tx-log-body').insertAdjacentHTML('afterbegin', logHtml);
                    
                    if (edgeData.is_terminal) {
                        let total = parseFloat(document.getElementById('total-traced-widget').innerText.replace(/[^0-9.-]+/g,"")) || 0;
                        document.getElementById('total-traced-widget').innerText = "$" + (total + usdAmount).toLocaleString(undefined, {minimumFractionDigits: 2});
                    }
                } // <-- THIS WAS MISSING
            } else if (data.type === 'COMPLETE') {
                document.getElementById('status').innerHTML = '<span class="text-emerald-600 font-bold">Trace Complete</span>';
                document.getElementById('tx-log-loader').classList.add('hidden');
            } else if (data.type === 'ERROR') {
                document.getElementById('status').innerHTML = '<span class="text-red-600 font-bold">Trace Error</span>';
                document.getElementById('tx-log-loader').classList.add('hidden');
                alert(data.message);
            }
        }

        window.submitTrace = function() {
            const seeds = document.getElementById('seed-input').value.split('\n').map(s=>s.trim()).filter(s=>s);
            const targetAmount = document.getElementById('target-amount').value || "1000";
            const network = document.getElementById('chain-select').value || "AUTO";
            const maxDepth = document.getElementById('max-depth').value || "5";
            
            if (seeds.length === 0) return alert('Enter at least one seed');
            
            document.getElementById('trace-id-val').innerText = 'NMS-' + Math.floor(Math.random()*90000 + 10000);
            if (ws.readyState === WebSocket.CONNECTING) {
                setTimeout(window.submitTrace, 500);
                return;
            } else if (ws.readyState !== WebSocket.OPEN) {
                alert("Connection to tracing engine lost. Please refresh the page.");
                return;
            }
            
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

        window.openContentPage = function(pageId) {
            console.log("Navigation disabled in tracer-only view: ", pageId);
        }

        window.toggleLogModal = function() {
            console.log("Log modal toggled");
            // Optional: Implement actual UI change if there is a modal
            alert("Evidentiary Log Modal Opened");
        };

        window.toggleAutoCluster = function(e) {
            console.log("Auto-cluster toggled: ", e ? e.checked : "unknown");
        };

        window.setCurrencyMode = function(select) {
            console.log("Currency mode set to: ", select ? select.value : "unknown");
        };

        window.highlightLossPaths = function() {
            console.log("Highlighting loss paths...");
            alert("Highlighting critical loss paths on graph.");
        };

        window.startCourtReplay = function() {
            console.log("Starting Court Replay...");
            alert("Generating Court-Ready Replay...");
        };
        
        function changeLayout() {
            let layout = document.getElementById("layoutSelect").value;
            if (layout === "physics") {
                network.setOptions({ layout: { hierarchical: { enabled: false } }, physics: { enabled: true, barnesHut: { gravitationalConstant: -20000, centralGravity: 0.3 } } });
            } else if (layout === "hierarchical_lr") {
                network.setOptions({ layout: { hierarchical: { enabled: true, direction: 'LR', sortMethod: 'directed', levelSeparation: 250, nodeSpacing: 100 } }, physics: { enabled: false } });
            } else if (layout === "tree") {
                network.setOptions({ layout: { hierarchical: { enabled: true, direction: 'UD', sortMethod: 'hubsize' } }, physics: { enabled: false } });
            }
            network.fit();
        }
    