import os
import json
import logging
import asyncio

logger = logging.getLogger("NEMESIS_BITQUERY_MEMPOOL")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("websockets library not found. Mempool tracker disabled.")

class BitqueryMempoolTracker:
    """
    Subscribes to Bitquery V2 WebSockets to track live mempool (pending) transactions.
    Used for Front-Running / MEV detection in NEMESIS TRACER.
    """
    def __init__(self):
        self.endpoint = "wss://streaming.bitquery.io/graphql"
        self.token = os.getenv("BITQUERY_APIV2_TOKEN", "")
        self.ws = None
        self.active_targets = set()
        self.task = None

    async def connect(self):
        if not WEBSOCKETS_AVAILABLE or not self.token:
            return False
            
        try:
            # GraphQL over WebSocket Protocol requires subprotocols
            self.ws = await websockets.connect(
                self.endpoint, 
                subprotocols=["graphql-ws"],
                extra_headers={"Authorization": f"Bearer {self.token}"}
            )
            
            # Send connection_init
            await self.ws.send(json.dumps({"type": "connection_init"}))
            response = json.loads(await self.ws.recv())
            if response.get("type") == "connection_ack":
                logger.info("Bitquery Mempool WebSocket connected.")
                self.task = asyncio.create_task(self._listen_loop())
                return True
            else:
                logger.error(f"WebSocket init failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False

    async def disconnect(self):
        if self.task:
            self.task.cancel()
        if self.ws:
            await self.ws.close()
            self.ws = None
            logger.info("Bitquery Mempool WebSocket closed.")

    async def start_tracking(self, target_address: str):
        """Starts a mempool subscription for a specific target."""
        if not self.ws or not self.token:
            return
            
        if target_address in self.active_targets:
            return
            
        self.active_targets.add(target_address)
        
        # Subscribe to Pending Transactions (Mempool)
        query = f"""
        subscription {{
          EVM(network: eth) {{
            Transactions(
              where: {{
                Transaction: {{
                  From: {{is: "{target_address}"}}
                }}
              }}
            ) {{
              Transaction {{
                Hash
                To
                Value
                Type
              }}
            }}
          }}
        }}
        """
        
        payload = {
            "type": "start",
            "id": f"mempool_{target_address}",
            "payload": {"query": query}
        }
        
        await self.ws.send(json.dumps(payload))
        logger.info(f"Subscribed to Mempool for target: {target_address}")

    async def _listen_loop(self):
        try:
            while True:
                msg = await self.ws.recv()
                data = json.loads(msg)
                
                if data.get("type") == "data":
                    payload = data.get("payload", {})
                    # In a full integration, this payload would be forwarded to the Cloudflare Worker Webhook
                    # For now, we log the detected MEV/Mempool event
                    logger.warning(f"🚨 MEMPOOL ALERT: {json.dumps(payload)}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Mempool connection closed remotely.")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Mempool listen loop: {e}")

# Singleton
bitquery_mempool = BitqueryMempoolTracker()
