import asyncio
import websockets
import json

async def test():
    async with websockets.connect("ws://127.0.0.1:8000/api/ws/trace") as ws:
        await ws.send(json.dumps({"type": "START_TRACE", "seeds": ["0x932F2489f417531CceDE0c1C95bcE0d903fF0DCC"], "network": "ETHEREUM"}))
        try:
            while True:
                msg = await ws.recv()
                print("RECV:", msg[:200])
        except Exception as e:
            print("ERROR", e)

asyncio.run(test())
