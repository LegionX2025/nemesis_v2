import asyncio
import aiohttp
from nemesis_core import fetch_chain_logs

async def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with aiohttp.ClientSession(headers=headers) as session:
        logs = await fetch_chain_logs(session, "0x030c0c65DBb914e423992F35b4Fe956F5E90b045", "POLYGON")
        for ev in logs[:2]:
            tx = ev["tx"]
            print(f"From: {tx.get('from')} To: {tx.get('to')} Value: {tx.get('value')} Token: {tx.get('tokenSymbol')}")

asyncio.run(main())
