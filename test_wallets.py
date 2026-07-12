import asyncio
import aiohttp
import json
import time
import sys

WALLETS = [
    # BTC
    "bc1qpa8n0a5ckt7wkdw3cn8eklsz3z0kn89knme5a9",
    "bc1qcrdrmxx49pfzrmltx6my4cp62n6t4e58jeu0y7",
    # XRP
    "ra58paZqDhh2e6LtA4VPQEgAztUz3Z3urq",
    "r9xM4fYBKM9EJcvECEgzcmwMjG5QQeJP8z",
    # EVM / ETH
    "0x159a861a3f0838adb1e6895886c7a0be7158be89",
    "0x2042404183ecd9610da5b251bb5f6e93eb9d3e08",
    "0x60E760222474A10f378cD53A5Bcd2CBd5a70eD1F",
    "0x0ed649357AbdAaA0222fE452B50D61D3E4a263a8",
    "0x6f00b583914fb35d314b36d2d914c145210be24e",
    "0x53556d7f1553Fa43D446D5363426447c40EDeAb3",
    "0x13d2d1f8e62f1f57eab648076583d7ce9f2af867",
    "0x7CA30EEE61DD4E2356B2aE59718C23C3C470D3bB",
    "0xf006878B4232C3281C545ae205Eda784DA6EAEAA",
    "0x041a583db93c1bfc883583d08fbc2bb001edd25a",
    # SOL
    "uThZSCB2R8UQXHuPKPQLrRC5n7VTdSqUrJDQuoJsNum",
    "6vMuna31vRDs9u9RAEF8UeCSs9CNu6j4LkXpe4Ko1gBQ",
    "G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t",
    "J7RBLx4gr5QisTidhJEzMj4awHz2ajwWKVREwN2J2TKR",
    # TRX
    "TNcykrU6R99SrR5BnxaqtDZe1V7o2sf664",
    # XLM
    "GCMPTBICKA5R4HN2DMRSNPMFWGYN5YO73R4B3DUD3SG7OZGCI4LRA3BP"
]

async def test_wallet(session, address):
    url = f"http://localhost:8000/api/node_intelligence?address={address}"
    print(f"[*] Testing {address[:12]}...")
    start_time = time.time()
    try:
        async with session.get(url, timeout=300) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                print(f"[SUCCESS] {address[:12]} | Time: {time.time()-start_time:.2f}s | Status: {data.get('status')}")
                return True
            else:
                text = await response.text()
                print(f"[FAILED]  {address[:12]} | HTTP {status} | Response: {text[:100]}")
                return False
    except Exception as e:
        print(f"[ERROR]   {address[:12]} | {str(e)}")
        return False

async def main():
    print("="*60)
    print(" NEMESIS WALLET BATCH TESTER ")
    print("="*60)
    
    # First, test the connection
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/", timeout=5) as r:
                if r.status != 200:
                    print("Backend root '/' returned non-200. Is it running?")
    except Exception as e:
        print(f"Could not connect to backend (localhost:8000): {e}")
        print("Please ensure the ghost process is killed and nemesis_core.py is running.")
        sys.exit(1)
        
    print("\nStarting batch tests...\n")
    successes = 0
    async with aiohttp.ClientSession() as session:
        for wallet in WALLETS:
            success = await test_wallet(session, wallet)
            if success: successes += 1
            await asyncio.sleep(2) # Prevent extreme rate-limiting on OSINT scrapers
            
    print("="*60)
    print(f" TEST COMPLETE: {successes}/{len(WALLETS)} Successful")
    print("="*60)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
