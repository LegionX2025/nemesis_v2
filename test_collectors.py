import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
import bitquery_collectors
import aiohttp

async def main():
    target = "0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772"
    chain = "ETHEREUM"
    print("Testing bitquery_collectors...")
    edges = await bitquery_collectors.run_all_collectors(target, chain)
    print(f"Got {len(edges)} edges!")
    if edges:
        print(edges[0])

if __name__ == "__main__":
    asyncio.run(main())
