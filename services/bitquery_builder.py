import os
import aiohttp
import logging
import asyncio
from typing import Dict, Any, List

logger = logging.getLogger("NEMESIS_BITQUERY_BUILDER")

class BitqueryBuilder:
    """
    Massive universal GraphQL builder for Bitquery V2 APIs.
    Supports NEMESIS TRACER (Fund flow) and NEMESIS ID (Entity Profiling).
    """
    def __init__(self):
        self.endpoint = "https://streaming.bitquery.io/graphql"
        self.token = os.getenv("BITQUERY_APIV2_TOKEN", "")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    # ==========================================
    # 1. TRACER QUERIES (Fund Flow & DEX)
    # ==========================================

    def build_evm_transfers_query(self, network: str, address: str, limit: int = 1000) -> str:
        """Tracks inbound/outbound token and native transfers on EVM chains."""
        return f"""
        {{
          EVM(network: {network}) {{
            Transfers(
              where: {{Transfer: {{Receiver: {{is: "{address}"}} }} }}
              limit: {{count: {limit}}}
              orderBy: {{descending: Block_Time}}
            ) {{
              Block {{ Time }}
              Transfer {{
                Amount
                Currency {{ Symbol SmartContract }}
                Sender
                Receiver
              }}
              Transaction {{ Hash }}
            }}
          }}
        }}
        """

    def build_solana_dex_trades_query(self, address: str, limit: int = 500) -> str:
        """Extracts Raydium/Orca/Jupiter trades on Solana."""
        return f"""
        {{
          Solana {{
            DEXTrades(
              where: {{Trade: {{Account: {{Address: {{is: "{address}"}}}}}}}}
              limit: {{count: {limit}}}
              orderBy: {{descending: Block_Time}}
            ) {{
              Block {{ Time }}
              Trade {{
                Dex {{ ProtocolName }}
                Buy {{ Amount Currency {{ Symbol MintAddress }} }}
                Sell {{ Amount Currency {{ Symbol MintAddress }} }}
              }}
              Transaction {{ Signature }}
            }}
          }}
        }}
        """

    def build_bitcoin_utxo_query(self, address: str) -> str:
        """Tracks Bitcoin UTXO unspent outputs."""
        return f"""
        {{
          Bitcoin {{
            Outputs(
              where: {{Output: {{Address: {{is: "{address}"}}}}}}
            ) {{
              Output {{ Value }}
              Transaction {{ Hash }}
            }}
          }}
        }}
        """

    def build_tron_transfers_query(self, address: str, limit: int = 500) -> str:
        """Tracks Tron TRC-20 and TRX transfers."""
        return f"""
        {{
          Tron {{
            Transfers(
              where: {{Transfer: {{Receiver: {{is: "{address}"}}}}}}
              limit: {{count: {limit}}}
            ) {{
              Transfer {{ Amount Currency {{ Symbol }} Sender Receiver }}
              Transaction {{ Hash }}
            }}
          }}
        }}
        """

    # ==========================================
    # 2. NEMESIS ID QUERIES (Profiling)
    # ==========================================

    def build_polymarket_history_query(self, address: str) -> str:
        """Tracks betting history on Polymarket (Polygon)."""
        # Polymarket CTF Exchange on Polygon
        return f"""
        {{
          EVM(network: matic) {{
            DEXTrades(
              where: {{Trade: {{Dex: {{ProtocolName: {{is: "polymarket"}}}}, Buyer: {{is: "{address}"}}}}}}
              limit: {{count: 100}}
            ) {{
              Trade {{ Buy {{ Amount Currency {{ Symbol }} }} }}
              Transaction {{ Hash }}
            }}
          }}
        }}
        """

    def build_nft_portfolio_query(self, network: str, address: str) -> str:
        """Tracks ERC-721/1155 NFT holdings."""
        return f"""
        {{
          EVM(network: {network}) {{
            Transfers(
              where: {{Transfer: {{Receiver: {{is: "{address}"}}}}, Currency: {{Fungible: false}}}}
            ) {{
              Transfer {{ Currency {{ Name SmartContract }} Id }}
            }}
          }}
        }}
        """

    # ==========================================
    # 3. EXECUTION ENGINE
    # ==========================================

    async def execute(self, query: str, semaphore: asyncio.Semaphore, max_retries: int = 3) -> Dict[str, Any]:
        """Executes the GraphQL query against Bitquery V2 with rate limit protection."""
        if not self.token:
            return {"error": "Missing BITQUERY_APIV2_TOKEN"}
            
        for attempt in range(max_retries):
            async with semaphore:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(self.endpoint, headers=self.headers, json={"query": query}, timeout=30) as response:
                            if response.status == 200:
                                return await response.json()
                            elif response.status in [403, 429]:
                                text = await response.text()
                                logger.warning(f"Bitquery Rate Limited [{response.status}]: {text}. Retrying in {2**attempt}s...")
                                # Sleep OUTSIDE the semaphore to prevent holding it while waiting for rate limit
                            else:
                                text = await response.text()
                                logger.error(f"Bitquery API Error [{response.status}]: {text}")
                                return {"error": f"HTTP {response.status}", "details": text}
                except Exception as e:
                    logger.error(f"Bitquery execution failed on attempt {attempt}: {str(e)}")
            
            # Wait outside the semaphore before retrying
            await asyncio.sleep(2**attempt)
            
        return {"error": "Max retries exceeded"}

# Singleton instance
bitquery_builder = BitqueryBuilder()
