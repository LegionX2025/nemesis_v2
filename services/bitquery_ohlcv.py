import os
import aiohttp
import logging
import asyncio
from typing import Dict, Any, List

logger = logging.getLogger("NEMESIS_BITQUERY_OHLCV")

class BitqueryOHLCV:
    """
    Extracts real-time and historical OHLCV data from Bitquery V2.
    Ideal for rendering trading performance charts in NEMESIS ID.
    """
    def __init__(self):
        self.endpoint = "https://streaming.bitquery.io/graphql"
        self.token = os.getenv("BITQUERY_APIV2_TOKEN", "")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def _build_ohlcv_query(self, network: str, token_address: str, base_address: str, interval_minutes: int, limit: int = 100) -> str:
        """
        Builds the GraphQL V2 query for OHLCV data.
        """
        return f"""
        {{
          EVM(network: {network}) {{
            DEXTrades(
              where: {{
                Trade: {{
                  Buy: {{Currency: {{SmartContract: {{is: "{token_address}"}}}}}},
                  Sell: {{Currency: {{SmartContract: {{is: "{base_address}"}}}}}}
                }}
              }}
              orderBy: {{descendingByField: "Block_Time"}}
              limit: {{count: {limit}}}
            ) {{
              Block {{
                Time(interval: {{in: minutes, count: {interval_minutes}}})
              }}
              Trade {{
                open: Price(minimum: Block_Number)
                high: Price(maximum: Price)
                low: Price(minimum: Price)
                close: Price(maximum: Block_Number)
                volume: Amount(sum: Trade_Amount)
              }}
            }}
          }}
        }}
        """

    async def get_chart_data(self, network: str, token_address: str, base_address: str = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", interval: int = 60, limit: int = 100) -> Dict[str, Any]:
        """
        Fetches OHLCV chart data for a specific token pair.
        Defaults to WETH as the base currency on Ethereum.
        """
        if not self.token:
            return {"error": "Missing BITQUERY_APIV2_TOKEN"}
            
        query = self._build_ohlcv_query(network, token_address, base_address, interval, limit)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, headers=self.headers, json={"query": query}, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Restructure for lightweight frontend charting (e.g. TradingView Lightweight Charts)
                        chart_data = []
                        trades = data.get("data", {}).get("EVM", {}).get("DEXTrades", [])
                        for t in trades:
                            block_time = t.get("Block", {}).get("Time")
                            trade_data = t.get("Trade", {})
                            if block_time and trade_data:
                                chart_data.append({
                                    "time": block_time,
                                    "open": trade_data.get("open"),
                                    "high": trade_data.get("high"),
                                    "low": trade_data.get("low"),
                                    "close": trade_data.get("close"),
                                    "volume": trade_data.get("volume")
                                })
                        return {"status": "success", "data": chart_data}
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}: {await response.text()}"}
        except Exception as e:
            logger.error(f"Failed to fetch OHLCV: {e}")
            return {"status": "error", "message": str(e)}

# Singleton
bitquery_ohlcv = BitqueryOHLCV()
