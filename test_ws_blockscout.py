import asyncio
import websockets
import json

async def test():
    async with websockets.connect("ws://localhost:8000/api/ws/trace") as ws:
        await ws.send(json.dumps({
            "type": "START_TRACE",
            "seeds": ["0x159a861A3F0838AdB1e6895886c7a0be7158BE89"],
            "target_amount": 10,
            "network": "ALL",
            "max_depth": 1
        }))
        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                print(f"Received: {data['type']}")
                if data["type"] == "TRACE_COMPLETE":
                    break
                elif data["type"] == "NEW_NODE":
                    print(f"Node: {data['node']}")
                elif data["type"] == "NEW_EDGE":
                    print(f"Edge: {data['edge']}")
            except websockets.exceptions.ConnectionClosed:
                break

asyncio.run(test())
