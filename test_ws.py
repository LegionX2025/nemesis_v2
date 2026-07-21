import asyncio
import websockets
import json

async def test():
    uri = "ws://127.0.0.1:8000/api/ws/trace"
    try:
        # Test with standard Origin
        async with websockets.connect(uri, extra_headers={"Origin": "http://127.0.0.1:8000"}) as websocket:
            print("[+] Connection with standard Origin SUCCESS")
            await websocket.send(json.dumps({"type": "init"}))
            print("[+] Sent message")
            
        # Test with null Origin (file://)
        async with websockets.connect(uri, extra_headers={"Origin": "null"}) as websocket2:
            print("[+] Connection with null Origin SUCCESS")
            
    except Exception as e:
        print(f"[-] Connection failed: {e}")

asyncio.run(test())
