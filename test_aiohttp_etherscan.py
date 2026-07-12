import asyncio
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        url = "https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx&address=0x932F2489f417531CceDE0c1C95bcE0d903fF0DCC&startblock=0&endblock=99999999&page=1&offset=100&sort=desc&apikey=5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY"
        try:
            async with session.get(url, timeout=10) as r:
                print("STATUS:", r.status)
                data = await r.json()
                print("DATA:", data)
        except Exception as e:
            print("ERROR TYPE:", type(e))
            print("ERROR:", e)

asyncio.run(main())
