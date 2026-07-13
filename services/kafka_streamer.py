import os
import json
import logging
import asyncio
import aiohttp

logger = logging.getLogger("NEMESIS_KAFKA_STREAMER")

try:
    from aiokafka import AIOKafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning("aiokafka not found. Kafka Streamer will be disabled.")

class BitqueryKafkaStreamer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.bitquery.io:9092")
        self.username = os.getenv("KAFKA_USERNAME", "bitquery")
        self.password = os.getenv("BITQUERY_APIV2_TOKEN", "")
        self.worker_url = os.getenv("VITE_WORKER_URL", "")
        
        # Default dynamic topics mapped to NEMESIS multi-chain architecture
        self.topics = [
            "ethereum.dex.trades", 
            "solana.transfers",
            "bsc.dex.trades",
            "tron.transfers",
            "polygon.dex.trades",
            "base.dex.trades",
            "arbitrum.dex.trades",
            "optimism.dex.trades",
            "bitcoin.transfers",
            "cardano.transfers",
            "ripple.transfers",
            "cosmos.transfers",
            "polymarket.bets",
            "nft.trades"
        ]
        
        self.consumer = None
        self.consume_task = None
        self.is_running = False

    async def start(self):
        if not KAFKA_AVAILABLE:
            logger.error("Cannot start Kafka Streamer: aiokafka not installed.")
            return False

        if not self.password:
            logger.error("No BITQUERY_APIV2_TOKEN found. Cannot connect to Kafka.")
            return False
            
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                security_protocol="SASL_SSL",
                sasl_mechanism="PLAIN",
                sasl_plain_username=self.username,
                sasl_plain_password=self.password,
                group_id="nemesis-tracer-group",
                auto_offset_reset="latest"
            )
            
            await self.consumer.start()
            self.is_running = True
            logger.info(f"Connected to Bitquery Kafka Streams. Subscribed to: {self.topics}")
            
            # Start background consuming task
            self.consume_task = asyncio.create_task(self._consume_loop())
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Kafka Streamer: {str(e)}")
            self.is_running = False
            return False

    async def stop(self):
        self.is_running = False
        if self.consume_task:
            self.consume_task.cancel()
        if self.consumer:
            await self.consumer.stop()
        logger.info("Bitquery Kafka Streamer stopped.")

    async def _consume_loop(self):
        try:
            async for msg in self.consumer:
                if not self.is_running:
                    break
                    
                # Process Kafka message
                payload = json.loads(msg.value.decode('utf-8'))
                
                # Format it for the NEMESIS frontend
                event = {
                    "type": "kafka_stream_event",
                    "topic": msg.topic,
                    "data": payload,
                    "timestamp": msg.timestamp
                }
                
                # Broadcast to the Worker Webhook so all active tracer dashboards get the live blip
                if self.worker_url:
                    webhook_endpoint = f"{self.worker_url.rstrip('/')}/internal/broadcast"
                    try:
                        async with aiohttp.ClientSession() as session:
                            await session.post(webhook_endpoint, json=event, timeout=5)
                    except Exception as e:
                        logger.debug(f"Failed to broadcast Kafka event: {str(e)}")
                        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Kafka consume loop: {str(e)}")
            self.is_running = False

# Singleton instance
kafka_streamer = BitqueryKafkaStreamer()
