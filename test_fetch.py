import asyncio
import aiohttp
from nemesis_core import fetch_chain_logs

async def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with aiohttp.ClientSession(headers=headers) as session:
        logs = await fetch_chain_logs(session, "0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772", "ETHEREUM")
        print("0x3b5D ETHEREUM:", len(logs))
        logs = await fetch_chain_logs(session, "0x030c0c65DBb914e423992F35b4Fe956F5E90b045", "POLYGON")
        print("0x030c POLYGON:", len(logs))
        for ev in logs:
            if ev["event_type"] != "Transfer":
                print(ev)

asyncio.run(main())
