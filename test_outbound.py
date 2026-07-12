import asyncio
import aiohttp
from nemesis_core import fetch_chain_logs

async def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with aiohttp.ClientSession(headers=headers) as session:
        for addr in ["0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772", "0x030c0c65DBb914e423992F35b4Fe956F5E90b045"]:
            logs = await fetch_chain_logs(session, addr, "POLYGON")
            outbound = 0
            for ev in logs:
                tx = ev["tx"]
                f_addr = str(tx.get("from", "")).lower()
                if f_addr == addr.lower(): outbound += 1
            print(f"{addr} OUTBOUND: {outbound} / {len(logs)}")

asyncio.run(main())
