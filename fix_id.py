import os

nemesis_id_path = 'C:/Users/LEGIONX/Downloads/nemesis/tracer_scripts/nemesis_id.html'
with open(nemesis_id_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Implement Multi-Cloud Backend Fallback
replacement = """
    // === MULTI-CLOUD BACKEND FAILOVER ===
    const BACKENDS = [
        "nemesisfinal.vercel.app", 
        "projectnemesis.onrender.com"
    ];
    let currentBackendIndex = 0;

    function getBackendHttpUrl(path) {
        return `https://${BACKENDS[currentBackendIndex]}/api/${path}`;
    }
    // =====================================
"""

if "// === MULTI-CLOUD BACKEND FAILOVER ===" not in content:
    content = content.replace("<script>", "<script>\n" + replacement)

content = content.replace("http://127.0.0.1:3001/api/", "https://nemesisfinal.vercel.app/api/")
content = content.replace("http://localhost:3001/api/", "https://nemesisfinal.vercel.app/api/")

with open(nemesis_id_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] Applied Multi-Cloud Backend Fallback to nemesis_id.html")
