import asyncio
from bitquery_collectors import run_all_collectors

async def main():
    addr = '0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772'
    print("Testing ETHEREUM...")
    eth_edges = await run_all_collectors(addr, "ETHEREUM")
    print(f"Found {len(eth_edges)} ETH edges")
    
    print("\nTesting BSC...")
    bsc_edges = await run_all_collectors(addr, "BSC")
    print(f"Found {len(bsc_edges)} BSC edges")

if __name__ == "__main__":
    asyncio.run(main())
