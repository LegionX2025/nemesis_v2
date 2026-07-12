import re

with open("tracer.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update edge creation to include ticker
edge_creation = """
                if (!nodes.get(edgeData.to)) {
                    nodes.add({ 
                        id: edgeData.to, 
                        label: edgeData.receiver_entity || (edgeData.to.substring(0,8) + '...'), 
                        image: getSafeIconUrl(edgeData.receiver_entity, isMixer, isCex, edgeData.chain),
                        custom_chain: edgeData.chain
                    });
                }
                
                edges.add({
                    id: edgeData.tx,
                    from: edgeData.from,
                    to: edgeData.to,
                    title: edgeData.amount + ' ' + (edgeData.ticker || 'NATIVE'),
                    label: edgeData.amount + ' ' + (edgeData.ticker || 'NATIVE') + '\\nOUTFLOW\\n↓ $' + usdAmount.toFixed(2),
                    custom_ticker: edgeData.ticker,
                    color: { color: isMixer ? '#ef4444' : '#64748b' }
                });
"""
content = re.sub(r'if \(!nodes\.get\(edgeData\.to\)\) \{.*?edges\.add\(\{.*?\}\);', edge_creation, content, flags=re.DOTALL)

# 2. Add ImageCache and Edge Drawing to afterDrawing
drawing_addition = """
            const imageCache = {};
            function getCachedImage(url) {
                if (!url) return null;
                if (!imageCache[url]) {
                    let img = new Image();
                    img.src = url;
                    imageCache[url] = img;
                }
                return imageCache[url];
            }
            
            network.on("afterDrawing", function (ctx) {
                let nodePositions = network.getPositions(nodes.getIds());
                
                // Draw Edges Tokens
                edges.get().forEach(e => {
                    let fromPos = nodePositions[e.from];
                    let toPos = nodePositions[e.to];
                    if (fromPos && toPos) {
                        let midX = (fromPos.x + toPos.x) / 2;
                        let midY = (fromPos.y + toPos.y) / 2;
                        
                        let ticker = e.custom_ticker || 'USDT';
                        let url = "https://cryptologos.cc/logos/tether-usdt-logo.png?v=035";
                        if (ticker.toUpperCase().includes("BTC")) url = "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=035";
                        if (ticker.toUpperCase().includes("ETH")) url = "https://cryptologos.cc/logos/ethereum-eth-logo.png?v=035";
                        if (ticker.toUpperCase().includes("SOL")) url = "https://cryptologos.cc/logos/solana-sol-logo.png?v=035";
                        if (ticker.toUpperCase().includes("BNB")) url = "https://cryptologos.cc/logos/bnb-bnb-logo.png?v=035";
                        
                        let img = getCachedImage(url);
                        if (img && img.complete) {
                            ctx.drawImage(img, midX - 10, midY - 25, 20, 20);
                        }
                    }
                });
                
                // Draw Node details (Amount, Badge, Classification)
"""
content = content.replace('network.on("afterDrawing", function (ctx) {\n                let nodePositions = network.getPositions(nodes.getIds());\n                \n                // Draw Node details (Amount, Badge, Classification)', drawing_addition)

# 3. Add Chain Icon to Nodes
node_addition = """
                    // Status Badge (bottom right of node)
                    ctx.beginPath();
                    ctx.arc(pos.x + 18, pos.y + 18, 8, 0, 2*Math.PI);
                    ctx.fillStyle = isCex ? "#10b981" : (isSuspect ? "#64748b" : "#3b82f6");
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    
                    ctx.font = '900 8px "Font Awesome 6 Free"';
                    ctx.fillStyle = "#ffffff";
                    let icon = isCex ? '\\uf00c' : (isSuspect ? '\\uf128' : '\\uf3ed');
                    ctx.fillText(icon, pos.x + 18, pos.y + 18);
                    
                    // Mini Chain Icon (top right)
                    let chainUrl = null;
                    let chain = n.custom_chain || "ETHEREUM";
                    if (chain === "ETHEREUM") chainUrl = "https://cryptologos.cc/logos/ethereum-eth-logo.png?v=035";
                    else if (chain === "BSC") chainUrl = "https://cryptologos.cc/logos/bnb-bnb-logo.png?v=035";
                    else if (chain === "POLYGON") chainUrl = "https://cryptologos.cc/logos/polygon-matic-logo.png?v=035";
                    else if (chain === "SOLANA") chainUrl = "https://cryptologos.cc/logos/solana-sol-logo.png?v=035";
                    else if (chain === "BITCOIN") chainUrl = "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=035";
                    
                    let cImg = getCachedImage(chainUrl);
                    if (cImg && cImg.complete) {
                        ctx.beginPath();
                        ctx.arc(pos.x + 18, pos.y - 18, 8, 0, 2*Math.PI);
                        ctx.fillStyle = "#ffffff";
                        ctx.fill();
                        ctx.drawImage(cImg, pos.x + 11, pos.y - 25, 14, 14);
                    }
"""
content = re.sub(r'// Status Badge.*?ctx\.fillText\(icon, pos\.x \+ 18, pos\.y \+ 18\);', node_addition, content, flags=re.DOTALL)

with open("tracer.html", "w", encoding="utf-8") as f:
    f.write(content)

print("tracer.html UI patched.")
