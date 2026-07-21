import subprocess
import time
import re

print("[*] Starting Cloudflare Quick Tunnel...")
tunnel_proc = subprocess.Popen(
    [r"..\cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

tunnel_url = None
print("[*] Waiting for Tunnel URL...")
start_time = time.time()
while time.time() - start_time < 30:
    line = tunnel_proc.stdout.readline()
    if "https://" in line and "trycloudflare.com" in line:
        match = re.search(r'(https://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
        if match:
            tunnel_url = match.group(1)
            print(f"TUNNEL_URL={tunnel_url}")
            
            # Auto-patch wrangler.toml
            import os
            wrangler_path = os.path.join(os.path.dirname(__file__), "workers", "wrangler.toml")
            if os.path.exists(wrangler_path):
                print(f"[*] Patching wrangler.toml with new Tunnel URL...")
                with open(wrangler_path, "r") as f:
                    config = f.read()
                
                config = re.sub(
                    r'PYTHON_API_URL\s*=\s*".*?"',
                    f'PYTHON_API_URL = "{tunnel_url}"',
                    config
                )
                
                with open(wrangler_path, "w") as f:
                    f.write(config)
                
                print("[*] Deploying updated Cloudflare Worker...")
                subprocess.Popen(
                    ["npx", "wrangler", "deploy"],
                    cwd=os.path.dirname(wrangler_path),
                    shell=True
                )
            
            break

# Keep the tunnel alive
try:
    tunnel_proc.wait()
except KeyboardInterrupt:
    print("[*] Stopping tunnel...")
    tunnel_proc.terminate()

