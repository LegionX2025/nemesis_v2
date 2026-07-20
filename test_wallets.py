import os
import subprocess
import time
import re
import sys
from playwright.sync_api import sync_playwright

test_wallets = [
    "bc1qguj54d66l502pwvft3zjrgwtmvhhq88nsaj7t6",
    "0x2a91386cEdb02D0d1fc37a262B07d458A015F06F",
    "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "0xD6094943979AfB5d2748FBB84788Aa4D2b0bd857",
    "rJnLjofJ25FQc5wXgac4LCJFC364hptbJx",
    "rhwTCnnXrunzYGAe9GVEqcbUx7PUbTHWsm",
    "01beef7b5cb9814c9457048d3e444e629d555ef53a064dc4f69b804234eb4da4",
    "C46E163E55837748A2F623D55898B281B517654AFE06CCE6AC69BB8B0BF4553C",
    "0x353085f3c41a3c5475df2f5542dfd2d2757cd73ca2f6bf9c0b740ef0cdb07490",
    "0x33c5e72fcebed5d255eb396017982ad2cdceb2ef97275c58d04889ab2c52fac2",
    "0x69F8c4c19A3Fb24859fc9E0DacfD554c17958d75",
    "0x4Cbcff095bdb49885439c4B4F3c8dEC287F942d2"
]

def run_tests():
    print("==================================================")
    print("   NEMESIS WALLET TRACER E2E TESTING              ")
    print("==================================================")

    # 1. Start nemesis_core.py
    print("[*] Starting Local AI Backend (nemesis_core.py)...")
    core_proc = subprocess.Popen([sys.executable, "nemesis_core.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(3)

    # 2. Start frontend server
    print("[*] Starting Local Frontend Server...")
    frontend_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8080", "--directory", "public"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    # 3. Start cloudflared tunnel
    print("[*] Starting Cloudflare Quick Tunnel...")
    tunnel_proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://127.0.0.1:8000"],
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
        frontend_proc.kill()
        return

    print(f"[+] Tunnel established at: {tunnel_url}")

    # 4. Update wrangler.toml and deploy worker
    print("[*] Updating Edge Worker with new Tunnel URL...")
    wrangler_path = os.path.join("workers", "wrangler.toml")
    
    with open(wrangler_path, "r") as f:
        config = f.read()
    
    # Simple regex replace for PYTHON_API_URL
    config = re.sub(r'PYTHON_API_URL\s*=\s*".*?"', f'PYTHON_API_URL = "{tunnel_url}"', config)
    
    with open(wrangler_path, "w") as f:
        f.write(config)

    print("[*] Redeploying Worker API Gateway...")
    subprocess.run(["npx.cmd", "wrangler", "deploy"], cwd="workers", shell=True)
    print("[+] Worker Redeployed Successfully!")

    # 5. Run Playwright Tests for each Wallet
    print("\n==================================================")
    print("   TESTING WALLETS VIA PLAYWRIGHT                 ")
    print("==================================================")
    
    os.makedirs("test_results_wallets", exist_ok=True)
    frontend_url = "http://localhost:8080/tracer.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        print(f"[*] Navigating to {frontend_url}...")
        page.goto(frontend_url, timeout=60000)
        page.wait_for_load_state('load')

        # Wait for WebSocket to connect - checking console output
        page.wait_for_timeout(3000)
        
        for idx, wallet in enumerate(test_wallets):
            print(f"\n[*] Testing wallet {idx+1}/{len(test_wallets)}: {wallet}")
            
            # Reload page to reset state
            page.goto(frontend_url, timeout=60000)
            page.wait_for_load_state('load')
            page.wait_for_timeout(2000)
            
            # Fill the address in the landing modal
            page.fill('#landing-seed', wallet)
            
            # Click trace
            page.click('button:has-text("Initialize Trace Sequence")')
            
            # Wait for some trace output
            print(f"    Waiting 8 seconds for trace to process...")
            page.wait_for_timeout(8000)
            
            # Save screenshot
            screenshot_path = f"test_results_wallets/trace_{idx+1}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"    [+] Screenshot saved to {screenshot_path}")
            
            # Optional: Extract terminal output from the page to verify
            terminal_text = page.evaluate("() => document.getElementById('terminal-body').innerText")
            print("    [Terminal Output Snippet]:")
            print("    " + "\n    ".join(terminal_text.strip().split("\n")[-5:]))

        browser.close()
        print("\n[+] Wallet Tests Completed!")

    # Cleanup
    print("\n[*] Shutting down background processes...")
    core_proc.kill()
    tunnel_proc.kill()
    frontend_proc.kill()
    print("[+] Cleanup complete.")

if __name__ == "__main__":
    run_tests()
