import re

with open("tracer.html", "r", encoding="utf-8") as f:
    content = f.read()

# 3. Add Chain Icon to Nodes (using exact replace)
old_node = """
                    // Status Badge (bottom right of node)
                    ctx.beginPath();
                    ctx.arc(pos.x + 18, pos.y + 18, 8, 0, 2*Math.PI);
                    ctx.fillStyle = isCex ? "#10b981" : (isSuspect ? "#64748b" : "#3b82f6");
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
"""
new_node = """
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
content = content.replace(old_node, new_node)

with open("tracer.html", "w", encoding="utf-8") as f:
    f.write(content)

print("tracer.html UI patched again.")
