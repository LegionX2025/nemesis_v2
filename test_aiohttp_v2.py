import asyncio
import aiohttp

async def main():
    async with aiohttp.ClientSession() as s:
        async with s.get('https://api.etherscan.io/v2/api?chainid=1&module=account&action=txlist&address=0x030c0c65DBb914e423992F35b4Fe956F5E90b045&startblock=0&endblock=99999999&page=1&offset=50&sort=desc&apikey=5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY') as r:
            print(r.status)
            print(await r.text())

asyncio.run(main())
