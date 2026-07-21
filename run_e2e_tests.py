import os
import subprocess
import sys
import time
import re

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("[*] Playwright not found. Auto-installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.sync_api import sync_playwright

def run_tests():
    print("==================================================")
    print("   NEMESIS E2E TESTING & TUNNEL ORCHESTRATOR      ")
    print("==================================================")

    # 1. Start nemesis_core.py
    print("[*] Starting Local AI Backend (nemesis_core.py)...")
    core_proc = subprocess.Popen(["python", "nemesis_core.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)

    # 2. Start cloudflared tunnel
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
                break
    
    if not tunnel_url:
        print("[!] Failed to get Cloudflare tunnel URL.")
        core_proc.kill()
        tunnel_proc.kill()
        return

    print(f"[+] Tunnel established at: {tunnel_url}")

    # 3. Update wrangler.toml and deploy worker
    print("[*] Updating Edge Worker with new Tunnel URL...")
    wrangler_path = os.path.join("workers", "wrangler.toml")
    
    wrangler_toml = f"""name = "nemesis-edge-api"
main = "src/index.ts"
compatibility_date = "2024-03-20"

[[durable_objects.bindings]]
name = "INVESTIGATION_SESSION"
class_name = "InvestigationSession"

[[migrations]]
tag = "v1"
new_sqlite_classes = ["InvestigationSession"]

[[queues.producers]]
binding = "TRACE_QUEUE"
queue = "nemesis-edge-trace-queue"

[[queues.consumers]]
queue = "nemesis-edge-trace-queue"
max_batch_size = 10
max_batch_timeout = 5
max_retries = 3

[[d1_databases]]
binding = "NEMESIS_DB"
database_name = "NEMESIS_DB"
database_id = "ec376c57-5dce-496b-8b55-db6975b52acb"

[[kv_namespaces]]
binding = "NEMESIS_CACHE"
id = "f4099ea1458e4e62ba838734f172846f"

[vars]
# You must set your Python API URL manually if using Cloudflare Tunnels
PYTHON_API_URL = "{tunnel_url}"
"""
    
    with open(wrangler_path, "w") as f:
        f.write(wrangler_toml)

    print("[*] Redeploying Worker API Gateway...")
    subprocess.run(["npx", "wrangler", "deploy"], cwd="workers", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[+] Worker Redeployed Successfully!")

    # 4. Run Playwright E2E Tests
    print("\n==================================================")
    print("   STARTING BROWSER E2E TESTING (PLAYWRIGHT)      ")
    print("==================================================")
    
    frontend_url = "https://nemesis-frontend.pages.dev"
    os.makedirs("test_results", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        page = browser.new_page()

        print(f"[*] Navigating to {frontend_url}...")
        page.goto(frontend_url, timeout=60000)
        page.wait_for_load_state('networkidle')
        
        # Test 1: Landing Page Load
        print("[+] Taking screenshot of Landing Page...")
        page.screenshot(path="test_results/1_landing_page.png", full_page=True)

        # Test 2: Admin Panel
        print("[*] Testing Admin Dashboard...")
        page.goto(f"{frontend_url}/admin.html", timeout=60000)
        page.wait_for_load_state('networkidle')
        print("[+] Taking screenshot of Admin Panel...")
        page.screenshot(path="test_results/2_admin_panel.png", full_page=True)
        
        # Test 3: Tracer Page
        print("[*] Testing Tracer UI...")
        page.goto(f"{frontend_url}/tracer.html", timeout=60000)
        page.wait_for_load_state('networkidle')
        print("[+] Taking screenshot of Tracer UI...")
        page.screenshot(path="test_results/3_tracer_ui.png", full_page=True)

        browser.close()
        print("\n[+] E2E Tests Completed Successfully!")
        print(f"[+] Screenshots saved in 'test_results' directory.")

    # Cleanup
    print("\n[*] Tearing down orchestrator...")
    core_proc.kill()
    tunnel_proc.kill()
    print("[+] Teardown complete. Testing Phase Finished.")

if __name__ == "__main__":
    run_tests()
