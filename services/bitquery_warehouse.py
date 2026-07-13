import os
import aiohttp
import logging
import asyncio
import io
import zipfile
from typing import Dict, Any

logger = logging.getLogger("NEMESIS_BITQUERY_WAREHOUSE")

class BitqueryWarehouse:
    """
    Connects to Bitquery's Blockchain ClickHouse warehouse.
    Ideal for massive enterprise-level data extraction (e.g. exporting a full exchange's history as Parquet).
    """
    def __init__(self):
        self.clickhouse_url = os.getenv("BITQUERY_CLICKHOUSE_URL", "https://explorer-api.bitquery.io")
        self.clickhouse_user = os.getenv("BITQUERY_CLICKHOUSE_USER", "")
        self.clickhouse_pass = os.getenv("BITQUERY_CLICKHOUSE_PASS", "")
        # Fallback to standard V2 GraphQL if warehouse is unavailable
        self.fallback_token = os.getenv("BITQUERY_APIV2_TOKEN", "")

    async def extract_target_to_parquet(self, target_address: str, chain: str = "eth") -> bytes:
        """
        Simulates an extraction from the ClickHouse warehouse to a raw Parquet byte stream.
        In a full enterprise environment, this runs a massive distributed SQL query 
        and streams the Parquet resultset directly to memory.
        """
        if not self.clickhouse_user or not self.clickhouse_pass:
            logger.warning("ClickHouse credentials missing. Falling back to V2 JSON-to-Parquet conversion.")
            return await self._fallback_extract(target_address, chain)
            
        # Enterprise ClickHouse Logic (Pseudo-implementation)
        query = f"SELECT * FROM {chain}.transfers WHERE sender = '{target_address}' OR receiver = '{target_address}' FORMAT Parquet"
        
        try:
            auth = aiohttp.BasicAuth(self.clickhouse_user, self.clickhouse_pass)
            async with aiohttp.ClientSession() as session:
                async with session.post(self.clickhouse_url, auth=auth, data=query, timeout=300) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error(f"ClickHouse query failed: {response.status}")
                        return b""
        except Exception as e:
            logger.error(f"Warehouse extraction failed: {e}")
            return b""
            
    async def _fallback_extract(self, target_address: str, chain: str) -> bytes:
        """
        If the user does not have enterprise ClickHouse access, we fallback to pulling
        via the standard Bitquery V2 GraphQL API and mocking a Parquet-like CSV buffer for the zip.
        """
        import pandas as pd
        from services.bitquery_builder import bitquery_builder
        
        query = bitquery_builder.build_evm_transfers_query(chain, target_address, limit=5000)
        semaphore = asyncio.Semaphore(5)
        
        result = await bitquery_builder.execute(query, semaphore)
        
        # Flatten the data
        try:
            transfers = result.get("data", {}).get("EVM", {}).get("Transfers", [])
            flat_data = []
            for t in transfers:
                flat_data.append({
                    "BlockTime": t.get("Block", {}).get("Time"),
                    "Amount": t.get("Transfer", {}).get("Amount"),
                    "Currency": t.get("Transfer", {}).get("Currency", {}).get("Symbol"),
                    "Sender": t.get("Transfer", {}).get("Sender"),
                    "Receiver": t.get("Transfer", {}).get("Receiver"),
                    "TxHash": t.get("Transaction", {}).get("Hash")
                })
                
            df = pd.DataFrame(flat_data)
            parquet_buffer = io.BytesIO()
            # Try to save as parquet if pyarrow is installed, otherwise csv
            try:
                df.to_parquet(parquet_buffer, engine='pyarrow')
            except ImportError:
                df.to_csv(parquet_buffer, index=False)
                
            return parquet_buffer.getvalue()
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")
            return b"ERROR: Fallback extraction failed."

# Singleton
bitquery_warehouse = BitqueryWarehouse()
