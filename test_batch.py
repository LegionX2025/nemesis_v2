import requests
import time
import sys

addresses = [
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

print("Testing traces on backend...")

for addr in addresses:
    print(f"Testing {addr}...")
    try:
        resp = requests.post("http://127.0.0.1:8000/api/trace/start", json={
            "seed_address": addr,
            "chain": "AUTO",
            "max_depth": 3,
            "max_hops": 5,
            "target_amount_usd": 0
        }, timeout=10)
        print(f"[{resp.status_code}] {resp.text}")
    except Exception as e:
        print(f"Failed: {e}")
    time.sleep(1)

print("Tests completed.")
