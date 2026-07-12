import re

with open("tracer.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Handle NODE_UPDATE in WebSocket
ws_logic = """
            if (msg.type === "NODE_UPDATE") {
                let n = nodes.get(msg.node);
                if (n) {
                    nodes.update({
                        id: msg.node,
                        custom_entity: msg.label_str,
                        custom_role: msg.classification,
                        custom_is_cex: msg.is_cex,
                        custom_is_suspect: msg.is_suspect
                    });
                }
                return;
            }
            if (msg.type === "LEDGER_BATCH") {
"""
content = content.replace("if (msg.type === \"LEDGER_BATCH\") {", ws_logic)

# 2. Add custom drawing to afterDrawing
# I'll replace the existing ctx.fillText logic
new_drawing = """
                    // Outflow Amount (Dummy/Calculated)
                    let amountText = n.custom_amount || (n.title && n.title.includes("$") ? n.title.split("\\n")[0] : "$0.00");
                    ctx.font = 'bold 14px "Inter", sans-serif';
                    ctx.fillStyle = "#3b82f6"; // Blue
                    ctx.fillText(amountText, pos.x, pos.y + 65);
                    
                    // Entity Badge
                    let isCex = n.custom_is_cex !== undefined ? n.custom_is_cex : (n.label.toUpperCase().includes("EXCHANGE") || n.label.toUpperCase().includes("CUSTODIAL"));
                    let isSuspect = n.custom_is_suspect !== undefined ? n.custom_is_suspect : (n.label.toUpperCase().includes("UNKNOWN") || n.label.toUpperCase().includes("SUSPECT"));
                    let entityName = n.custom_entity ? n.custom_entity.substring(0,15) : (isCex ? "BINANCE" : (isSuspect ? "UNKNOWN" : "WALLET"));
                    
                    ctx.fillStyle = isCex ? "#dcfce7" : "#e0f2fe"; // light green or light blue
                    let bw = Math.max(60, ctx.measureText(entityName).width + 10);
                    let bh = 14;
                    ctx.beginPath();
                    ctx.roundRect(pos.x - bw/2, pos.y + 80, bw, bh, 4);
                    ctx.fill();
                    
                    ctx.font = 'bold 8px "Inter", sans-serif';
                    ctx.fillStyle = isCex ? "#166534" : "#0369a1";
                    ctx.fillText(entityName.toUpperCase(), pos.x, pos.y + 80 + bh/2);
                    
                    // Role
                    let role = n.custom_role || (isCex ? "EXCHANGE" : "UNKNOWN ENTITY");
                    ctx.font = 'bold 9px "Inter", sans-serif';
                    ctx.fillStyle = "#64748b";
                    ctx.fillText(role.toUpperCase(), pos.x, pos.y + 100);
                    
                    // Status Badge (bottom right of node)
                    ctx.beginPath();
                    ctx.arc(pos.x + 18, pos.y + 18, 8, 0, 2*Math.PI);
                    ctx.fillStyle = isCex ? "#10b981" : (isSuspect ? "#64748b" : "#3b82f6");
                    ctx.fill();
                    ctx.strokeStyle = "#ffffff";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
"""
# Replace everything from "let amountText = ..." to "ctx.stroke();"
import re
content = re.sub(r'// Outflow Amount.*?ctx\.stroke\(\);', new_drawing, content, flags=re.DOTALL)

with open("tracer.html", "w", encoding="utf-8") as f:
    f.write(content)

print("tracer.html patched for node update")
