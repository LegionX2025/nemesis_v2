import os
import sys
import time
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
    print("   TESTING WALLETS VIA PLAYWRIGHT                 ")
    print("==================================================")
    
    os.makedirs("test_results_wallets", exist_ok=True)
    frontend_url = "http://localhost:8080/tracer.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

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
            terminal_text = page.evaluate("() => document.getElementById('terminal-list').innerText")
            print("    [Terminal Output Snippet]:")
            print("    " + "\n    ".join(terminal_text.strip().split("\n")[-5:]))

        browser.close()
        print("\n[+] Wallet Tests Completed!")

if __name__ == "__main__":
    run_tests()
