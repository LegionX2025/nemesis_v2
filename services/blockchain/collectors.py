import logging
import asyncio
import aiohttp
import os
import time
from datetime import datetime
from typing import List, Any

logger = logging.getLogger("NEMESIS_COLLECTOR")

class GBIOEdge:
    """Standardized representation of a blockchain transaction/transfer."""
    def __init__(self, tx_hash: str, src: str, dst: str, amt: float, ts: int):
        self.edge_id = tx_hash
        self.transaction_hash = tx_hash
        self.source_node_id = src
        self.target_node_id = dst
        self.amount_native = amt
        self.amount = amt
        self.timestamp = ts

async def _fetch_etherscan(session, address: str, chain: str) -> List[GBIOEdge]:
    """Real implementation for Etherscan/Blockscout API."""
    import os
    logger.info(f"Fetching trace for {address} on {chain} via Explorer APIs")
    
    chain = (chain or "").upper()
    api_url = "https://api.etherscan.io/api"
    api_key = os.getenv("ETHERSCAN_API_KEY", "")
    
    if chain in ["POLYGON", "MATIC"]:
        api_url = "https://api.polygonscan.com/api"
        api_key = os.getenv("POLYGONSCAN_API_KEY", "")
    elif chain in ["BSC", "BNB"]:
        api_url = "https://api.bscscan.com/api"
        api_key = os.getenv("BSCSCAN_API_KEY", "")
    elif chain in ["OPTIMISM", "OP"]:
        api_url = "https://api-optimistic.etherscan.io/api"
        api_key = os.getenv("OPTIMISMSCAN_API_KEY", "")
    elif chain in ["ARBITRUM", "ARB"]:
        api_url = "https://api.arbiscan.io/api"
        api_key = os.getenv("ARBITRUM_API_KEY", "")
    elif chain in ["AVALANCHE", "AVAX"]:
        api_url = "https://api.snowtrace.io/api"
        api_key = os.getenv("SNOWTRACE_API_KEY", "")
    elif chain == "BASE":
        api_url = "https://api.basescan.org/api"
        api_key = os.getenv("BASESCAN_API_KEY", "")
    elif chain == "CELO":
        api_url = "https://api.celoscan.io/api"
        api_key = os.getenv("CELOSCAN_API_KEY", "")
    elif chain == "LINEA":
        api_url = "https://api.lineascan.build/api"
        api_key = os.getenv("LINEASCAN_API_KEY", "")

    edges = []
    
    # Normal Transactions
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 50,
        "sort": "desc",
        "apikey": api_key
    }
    
    # Ankr Advanced API Fallback for supported EVM chains
    ankr_chains = {"ETHEREUM": "eth", "BSC": "bsc", "BNB": "bsc", "POLYGON": "polygon", "MATIC": "polygon", "AVALANCHE": "avalanche", "AVAX": "avalanche", "ARBITRUM": "arbitrum", "ARB": "arbitrum", "OPTIMISM": "optimism", "OP": "optimism", "BASE": "base"}
    if chain in ankr_chains:
        try:
            payload = {"jsonrpc": "2.0", "method": "ankr_getTransactionsByAddress", "params": {"blockchain": ankr_chains[chain], "address": address}, "id": 1}
            async with session.post("https://rpc.ankr.com/multichain/d0ebdc10f7a98d2c08105ddcef64d9353e5b92e1d59e545debed8af8bce60fbc", json=payload, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("result", {}).get("transactions"):
                        for tx in data["result"]["transactions"]:
                            val = float(int(tx.get("value", "0x0"), 16)) / 1e18 if str(tx.get("value", "")).startswith("0x") else float(tx.get("value", "0")) / 1e18
                            if val > 0:
                                ts = int(tx.get("timestamp", "0x0"), 16) if str(tx.get("timestamp", "")).startswith("0x") else int(tx.get("timestamp", "0"))
                                edges.append(GBIOEdge(tx.get("hash"), tx.get("from", "").lower(), tx.get("to", "").lower(), val, ts))
                        if len(edges) > 0:
                            return edges
        except Exception as e:
            logger.error(f"Error fetching Ankr txs: {e}")

    # Normal Transactions (Fallback to Etherscan)
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 50,
        "sort": "desc",
        "apikey": api_key
    }
    
    import asyncio
    async def _get_with_backoff(session, url, params, max_retries=3):
        for attempt in range(max_retries):
            try:
                async with session.get(url, params=params) as resp:
                    content_type = resp.headers.get('Content-Type', '')
                    if resp.status == 200:
                        if 'text/html' in content_type:
                            logger.warning(f"Received HTML instead of JSON from {url}. Retrying in {2**attempt}s...")
                            await asyncio.sleep(2**attempt)
                            continue
                        return await resp.json()
                    elif resp.status in [403, 429]:
                        logger.warning(f"Rate limited (status {resp.status}) on {url}. Retrying in {2**attempt}s...")
                        await asyncio.sleep(2**attempt)
                        continue
                    else:
                        break
            except Exception as e:
                logger.error(f"Etherscan fetch error on attempt {attempt}: {e}")
                await asyncio.sleep(2**attempt)
        return None

    try:
        data = await _get_with_backoff(session, api_url, params)
        if data and data.get("status") == "1":
            for tx in data.get("result", []):
                val = float(tx.get("value", 0)) / 1e18
                if val > 0:
                    edges.append(GBIOEdge(
                        tx.get("hash"),
                        tx.get("from", "").lower(),
                        tx.get("to", "").lower(),
                        val,
                        int(tx.get("timeStamp", 0))
                    ))
    except Exception as e:
        logger.error(f"Error fetching normal txs: {e}")
        
    # ERC20 Token Transfers
    params["action"] = "tokentx"
    try:
        data = await _get_with_backoff(session, api_url, params)
        if data and data.get("status") == "1":
            for tx in data.get("result", []):
                decimals = int(tx.get("tokenDecimal", 18))
                val = float(tx.get("value", 0)) / (10 ** decimals)
                if val > 0:
                        edge = GBIOEdge(
                            tx.get("hash"),
                            tx.get("from", "").lower(),
                            tx.get("to", "").lower(),
                            val,
                            int(tx.get("timeStamp", 0))
                        )
                        setattr(edge, "tokenSymbol", tx.get("tokenSymbol", ""))
                        setattr(edge, "tokenDecimal", decimals)
                        edges.append(edge)
    except Exception as e:
        logger.error(f"Error fetching token txs: {e}")
        
    return edges

async def _fetch_bitquery(session, address: str, chain: str) -> List[GBIOEdge]:
    logger.info(f"Fetching trace for {address} on {chain} via Bitquery V2")
    try:
        from services.bitquery_builder import bitquery_builder
    except ImportError:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from services.bitquery_builder import bitquery_builder
    
    chain = (chain or "").upper()
    edges = []
    
    chain_map = {
        "BSC": "bsc", "BNB": "bsc", "POLYGON": "matic", "MATIC": "matic",
        "ARBITRUM": "arbitrum", "ARB": "arbitrum", "OPTIMISM": "optimism", "OP": "optimism",
        "TRON": "tron", "TRX": "tron", "SOLANA": "solana", "SOL": "solana",
        "BITCOIN": "bitcoin", "BTC": "bitcoin", "AVALANCHE": "avalanche", "AVAX": "avalanche",
        "FANTOM": "fantom", "FTM": "fantom", "CELO": "celo",
        "CRONOS": "cronos", "CRO": "cronos", "BASE": "base",
        "LITECOIN": "litecoin", "LTC": "litecoin", "DOGECOIN": "dogecoin", "DOGE": "dogecoin",
        "DASH": "dash", "BITCOINCASH": "bitcoincash", "BCH": "bitcoincash",
    }
    network = chain_map.get(chain, chain.lower())
    
    query = ""
    evm_chains = ["eth", "bsc", "matic", "arbitrum", "optimism", "avalanche", "fantom", "celo", "cronos", "base", "ethereum"]
    if network in evm_chains:
        query = bitquery_builder.build_evm_transfers_query(network if network != "ethereum" else "eth", address, 100)
    elif network == "solana":
        query = bitquery_builder.build_solana_dex_trades_query(address, 100)
    elif network == "bitcoin":
        query = bitquery_builder.build_bitcoin_utxo_query(address)
    elif network == "tron":
        query = bitquery_builder.build_tron_transfers_query(address, 100)
    else:
        logger.warning(f"Unsupported bitquery chain: {network}")
        return []
        
    sem = asyncio.Semaphore(5)
    resp = await bitquery_builder.execute(query, sem)
    
    if resp and resp.get("data"):
        try:
            if network in evm_chains:
                transfers = resp["data"].get("EVM", {}).get("Transfers", [])
                for tx in transfers:
                    amt = float(tx.get("Transfer", {}).get("Amount", 0) or 0)
                    if amt > 0:
                        ts_str = tx.get("Block", {}).get("Time", "")
                        ts = int(datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()) if ts_str else int(time.time())
                        sender = tx.get("Transfer", {}).get("Sender", "")
                        receiver = tx.get("Transfer", {}).get("Receiver", "")
                        hash = tx.get("Transaction", {}).get("Hash", "")
                        sym = tx.get("Transfer", {}).get("Currency", {}).get("Symbol", "")
                        
                        edge = GBIOEdge(hash, sender.lower(), receiver.lower(), amt, ts)
                        setattr(edge, "tokenSymbol", sym)
                        edges.append(edge)
            elif network == "tron":
                transfers = resp["data"].get("Tron", {}).get("Transfers", [])
                for tx in transfers:
                    amt = float(tx.get("Transfer", {}).get("Amount", 0) or 0)
                    if amt > 0:
                        sender = tx.get("Transfer", {}).get("Sender", "")
                        receiver = tx.get("Transfer", {}).get("Receiver", "")
                        hash = tx.get("Transaction", {}).get("Hash", "")
                        sym = tx.get("Transfer", {}).get("Currency", {}).get("Symbol", "")
                        
                        edge = GBIOEdge(hash, sender, receiver, amt, int(time.time()))
                        setattr(edge, "tokenSymbol", sym)
                        edges.append(edge)
            elif network == "bitcoin":
                outputs = resp["data"].get("Bitcoin", {}).get("Outputs", [])
                for out in outputs:
                    amt = float(out.get("Output", {}).get("Value", 0) or 0)
                    if amt > 0:
                        hash = out.get("Transaction", {}).get("Hash", "")
                        edge = GBIOEdge(hash, "", address, amt, int(time.time()))
                        edges.append(edge)
            elif network == "solana":
                trades = resp["data"].get("Solana", {}).get("DEXTrades", [])
                for t in trades:
                    buy_amt = float(t.get("Trade", {}).get("Buy", {}).get("Amount", 0) or 0)
                    if buy_amt > 0:
                        hash = t.get("Transaction", {}).get("Signature", "")
                        ts_str = t.get("Block", {}).get("Time", "")
                        ts = int(datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()) if ts_str else int(time.time())
                        edge = GBIOEdge(hash, "", address, buy_amt, ts)
                        edges.append(edge)
        except Exception as e:
            logger.error(f"Bitquery parser error: {e}")
            
    return edges
async def run_collectors(session: aiohttp.ClientSession, address: str, chain: str = "eth"):
    """
    Replaces the broken bitquery_collectors.py logic.
    """
    try:
        edges = []
        # Run explorer collectors
        edges.extend(await _fetch_etherscan(session, address, chain))
        # Run Bitquery collector
        edges.extend(await _fetch_bitquery(session, address, chain))
        return edges
    except Exception as e:
        logger.error(f"Collector error for {address}: {e}")
        return []
