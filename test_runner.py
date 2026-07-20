import asyncio
import aiohttp
import time
import json

ADDRESSES = [
    "bc1qpa8n0a5ckt7wkdw3cn8eklsz3z0kn89knme5a9",
    "ra58paZqDhh2e6LtA4VPQEgAztUz3Z3urq",
    "bc1qcrdrmxx49pfzrmltx6my4cp62n6t4e58jeu0y7",
    "0x159a861a3f0838adb1e6895886c7a0be7158be89",
    "0x2042404183ecd9610da5b251bb5f6e93eb9d3e08",
    "0x60E760222474A10f378cD53A5Bcd2CBd5a70eD1F",
    "0x0ed649357AbdAaA0222fE452B50D61D3E4a263a8",
    "0x6f00b583914fb35d314b36d2d914c145210be24e",
    "0x53556d7f1553Fa43D446D5363426447c40EDeAb3",
    "TNcykrU6R99SrR5BnxaqtDZe1V7o2sf664",
    "0x13d2d1f8e62f1f57eab648076583d7ce9f2af867",
    "0x7CA30EEE61DD4E2356B2aE59718C23C3C470D3bB",
    "0xf006878B4232C3281C545ae205Eda784DA6EAEAA",
    "GCMPTBICKA5R4HN2DMRSNPMFWGYN5YO73R4B3DUD3SG7OZGCI4LRA3BP",
    "r9xM4fYBKM9EJcvECEgzcmwMjG5QQeJP8z",
    "0x041a583db93c1bfc883583d08fbc2bb001edd25a"
]

async def test_endpoint(session, url):
    try:
        async with session.get(url, timeout=60) as resp:
            text = await resp.text()
            if resp.status == 200:
                try:
                    data = json.loads(text)
                    if data.get("status") == "success":
                        return True, "SUCCESS"
                    else:
                        return False, f"API ERROR: {data.get('message', 'Unknown Error')}"
                except:
                    return False, "JSON PARSE ERROR"
            else:
                return False, f"HTTP {resp.status}"
    except Exception as e:
        return False, f"EXCEPTION: {str(e)}"

async def test_address(session, idx, addr):
    print(f"[{idx}/16] Testing {addr}...")
    start_time = time.time()
    
    graph_url = f"http://127.0.0.1:8000/api/node/graph?address={addr}"
    osint_url = f"http://127.0.0.1:8000/api/node/osint?address={addr}"
    
    g_res, g_msg = await test_endpoint(session, graph_url)
    o_res, o_msg = await test_endpoint(session, osint_url)
    
    duration = time.time() - start_time
    
    status = "✅ PASS" if g_res and o_res else "❌ FAIL"
    print(f"{status} | {addr} | Time: {duration:.2f}s | Graph: {g_msg} | OSINT: {o_msg}")

async def main():
    async with aiohttp.ClientSession() as session:
        for idx, addr in enumerate(ADDRESSES, 1):
            await test_address(session, idx, addr)
            await asyncio.sleep(2) # Prevent rate limiting

if __name__ == "__main__":
    asyncio.run(main())
