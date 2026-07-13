import os
import aiohttp
import logging
from datetime import datetime

# Adjust import based on environment
try:
    from services.gbio_ontology import GBIOEdge
except ImportError:
    from gbio_ontology import GBIOEdge

logger = logging.getLogger("NEMESIS_BITQUERY")

async def fetch_bitquery(session, address: str, chain: str):
    logger.info(f"Fetching Bitquery data for {address} on {chain}")
    url = "https://graphql.bitquery.io"
    api_key = os.getenv("BITQUERY_API_TOKEN", "")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    # Map chain
    network = "ethereum"
    if chain.upper() in ["BSC", "BNB"]: network = "bsc"
    elif chain.upper() in ["POLYGON", "MATIC"]: network = "matic"
    elif chain.upper() in ["ARBITRUM", "ARB"]: network = "arbitrum"
    elif chain.upper() in ["OPTIMISM", "OP"]: network = "optimism"
    
    query = """
    query ($network: EthereumNetwork!, $address: String!) {
      ethereum(network: $network) {
        transfers(sender: {is: $address}, options: {limit: 50, desc: "block.timestamp.time"}) {
          transaction { hash }
          sender { address }
          receiver { address }
          amount
          currency { symbol decimals }
          block { timestamp { time } }
        }
      }
    }
    """
    
    edges = []
    if not api_key:
        logger.warning("No BITQUERY_API_TOKEN found.")
        return edges

    try:
        async with session.post(url, json={"query": query, "variables": {"network": network, "address": address}}, headers=headers) as resp:
            data = await resp.json()
            if "data" in data and "ethereum" in data["data"] and data["data"]["ethereum"]:
                transfers = data["data"]["ethereum"].get("transfers", [])
                for tx in transfers:
                    amt = float(tx.get("amount", 0))
                    if amt > 0:
                        try:
                            # Try to parse ISO or standard format
                            ts_str = tx["block"]["timestamp"]["time"]
                            if "T" in ts_str:
                                ts = int(datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp())
                            else:
                                ts = int(datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").timestamp())
                        except Exception:
                            ts = int(datetime.now().timestamp())

                        edge = GBIOEdge(
                            tx["transaction"]["hash"],
                            tx["sender"]["address"].lower(),
                            tx["receiver"]["address"].lower(),
                            amt,
                            ts
                        )
                        setattr(edge, "tokenSymbol", tx["currency"]["symbol"])
                        setattr(edge, "tokenDecimal", tx["currency"]["decimals"] or 18)
                        edges.append(edge)
    except Exception as e:
        logger.error(f"Bitquery error: {e}")
        
    return edges
