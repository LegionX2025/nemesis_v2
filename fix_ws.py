import os

tracer_path = 'tracer.html'
with open(tracer_path, 'r', encoding='utf-8') as f:
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

    function getBackendWsUrl(path) {
        return `wss://${BACKENDS[currentBackendIndex]}/api/ws/${path}`;
    }
    // =====================================
"""

if "// === MULTI-CLOUD BACKEND FAILOVER ===" not in content:
    content = content.replace("<script>", "<script>\n" + replacement)

content = content.replace("ws://127.0.0.1:3001/api/ws/trace", "wss://nemesisfinal.vercel.app/api/ws/trace")
content = content.replace("http://127.0.0.1:3001/api/", "https://nemesisfinal.vercel.app/api/")

with open(tracer_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] Applied Multi-Cloud Backend Fallback to tracer.html")
