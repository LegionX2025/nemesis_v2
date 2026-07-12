import asyncio
import os
import aiohttp
from typing import List, Dict, Any
from gbio_ontology import GBIOEdge, TransferAction, EvidenceRecord
from datetime import datetime, timezone
from eth_utils import to_checksum_address
import json
from dotenv import load_dotenv

load_dotenv()

BITQUERY_URL = "https://streaming.bitquery.io/graphql"
BITQUERY_TOKEN = os.environ.get("BITQUERY_APIV2_TOKEN", "")

# Load API Keys
ANKR_API_KEY = os.environ.get("ANKR_API_KEY", "")
ETHERSCAN_KEY = os.environ.get("VITE_ETHERSCAN_API_KEY", "")

class BaseCollector:
    name = "BaseCollector"
    
    @classmethod
    async def fetch(cls, session: aiohttp.ClientSession, target_address: str, chain: str) -> List[GBIOEdge]:
        raise NotImplementedError

class AnkrCollector(BaseCollector):
    name = "AnkrCollector"
    
    @classmethod
    async def fetch(cls, session: aiohttp.ClientSession, target_address: str, chain: str) -> List[GBIOEdge]:
        if not ANKR_API_KEY:
            return []
        
        edges = []
        url = f"https://rpc.ankr.com/multichain/{ANKR_API_KEY}"
        
        chain_map = {
            "ETHEREUM": "eth",
            "BSC": "bsc",
            "POLYGON": "polygon",
            "ARBITRUM": "arbitrum",
            "OPTIMISM": "optimism",
            "BASE": "base"
        }
        
        ankr_chain = chain_map.get(chain.upper())
        if not ankr_chain:
            return []

        # 1. Fetch Native Transactions
        native_payload = {
            "jsonrpc": "2.0",
            "method": "ankr_getTransactionsByAddress",
            "params": {
                "address": target_address,
                "blockchain": [ankr_chain],
                "descOrder": True,
                "pageSize": 50
            },
            "id": 1
        }
        
        # 2. Fetch ERC20 Token Transfers
        token_payload = {
            "jsonrpc": "2.0",
            "method": "ankr_getTokenTransfers",
            "params": {
                "address": target_address,
                "blockchain": [ankr_chain],
                "descOrder": True,
                "pageSize": 50
            },
            "id": 2
        }

        native_data = None
        token_data = None
        
        try:
            async with session.post(url, json=native_payload, timeout=15) as res:
                if res.status == 200:
                    native_data = await res.json()
        except Exception as e:
            print(f"Ankr Native Request Error: {e}")

        try:
            async with session.post(url, json=token_payload, timeout=15) as res:
                if res.status == 200:
                    token_data = await res.json()
        except Exception as e:
            print(f"Ankr Token Request Error: {e}")

        try:
            if native_data and 'result' in native_data and 'transactions' in native_data['result']:
                for tx in native_data['result']['transactions']:
                    try:
                        # Ankr returns hex string for value
                        val_hex = tx.get("value", "0x0")
                        val_int = int(val_hex, 16)
                        amt = val_int / 1e18
                        if amt <= 0.0001: continue
                        
                        frm = tx.get("from", "").lower()
                        to = tx.get("to", "").lower()
                        ts = datetime.fromtimestamp(int(tx.get("timestamp", "0x0"), 16)).isoformat()
                        
                        edges.append(GBIOEdge(
                            edge_id=tx.get("hash", "") + "_NATIVE",
                            action=TransferAction.RECEIVED_FROM if to == target_address.lower() else TransferAction.SENT_TO,
                            source_node_id=frm,
                            target_node_id=to,
                            amount_native=amt,
                            timestamp=ts,
                            chain=chain,
                            asset_symbol="ETH" if chain.upper() == "ETHEREUM" else ("BNB" if chain.upper() == "BSC" else ("MATIC" if chain.upper() == "POLYGON" else "NATIVE")),
                            evidence=EvidenceRecord(source_provider="AnkrNative", retrieval_timestamp=datetime.now(timezone.utc), transaction_hash=tx.get("hash"), confidence_score=1.0)
                        ))
                    except Exception as e:
                        print(f"Ankr Native Tx Error: {e}")
                        
            if token_data and 'result' in token_data and 'transfers' in token_data['result']:
                for tx in token_data['result']['transfers']:
                    try:
                        amt = float(tx.get("value", 0))
                        if amt <= 0.0001: continue
                        
                        frm = tx.get("fromAddress", "").lower()
                        to = tx.get("toAddress", "").lower()
                        ts = datetime.fromtimestamp(tx.get("timestamp", 0)).isoformat()
                        
                        edges.append(GBIOEdge(
                            edge_id=tx.get("transactionHash", "") + "_" + tx.get("tokenSymbol", "TKN"),
                            action=TransferAction.RECEIVED_FROM if to == target_address.lower() else TransferAction.SENT_TO,
                            source_node_id=frm,
                            target_node_id=to,
                            amount_native=amt,
                            timestamp=ts,
                            chain=chain,
                            asset_symbol=tx.get("tokenSymbol", "TKN"),
                            evidence=EvidenceRecord(source_provider="AnkrToken", retrieval_timestamp=datetime.now(timezone.utc), transaction_hash=tx.get("transactionHash"), confidence_score=1.0)
                        ))
                    except Exception as e:
                        print(f"Ankr Token Tx Error: {e}")
                        
        except Exception as e:
            print(f"AnkrCollector Error: {e}")
            
        return edges

class EtherscanV2Collector(BaseCollector):
    name = "EtherscanV2Collector"

    @classmethod
    async def fetch(cls, session: aiohttp.ClientSession, target_address: str, chain: str) -> List[GBIOEdge]:
        if not ETHERSCAN_KEY or chain.upper() != "ETHEREUM":
            # Free tier only works on Ethereum Mainnet
            return []
            
        edges = []
        api_urls = [
            f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=txlist&address={target_address}&startblock=0&endblock=99999999&page=1&offset=50&sort=desc&apikey={ETHERSCAN_KEY}",
            f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx&address={target_address}&startblock=0&endblock=99999999&page=1&offset=50&sort=desc&apikey={ETHERSCAN_KEY}"
        ]
        
        for api_url in api_urls:
            try:
                async with session.get(api_url, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "1":
                            for tx in data.get("result", []):
                                try:
                                    decimals = int(tx.get("tokenDecimal", 18))
                                    amt = float(tx.get("value", 0)) / (10 ** decimals)
                                    if amt <= 0.0001: continue
                                    frm = str(tx.get("from", "")).lower()
                                    to = str(tx.get("to", "")).lower()
                                    
                                    try:
                                        ts = datetime.fromtimestamp(int(tx.get("timeStamp", 0))).isoformat()
                                    except:
                                        ts = datetime.now(timezone.utc).isoformat()
                                        
                                    edges.append(GBIOEdge(
                                        edge_id=tx.get("hash", "") + tx.get("tokenSymbol", "ETH"),
                                        action=TransferAction.RECEIVED_FROM if to == target_address.lower() else TransferAction.SENT_TO,
                                        source_node_id=frm,
                                        target_node_id=to,
                                        amount_native=amt,
                                        timestamp=ts,
                                        chain=chain,
                                        asset_symbol=tx.get("tokenSymbol", "ETH"),
                                        evidence=EvidenceRecord(source_provider="EtherscanV2", retrieval_timestamp=datetime.now(timezone.utc), transaction_hash=tx.get("hash"), confidence_score=1.0)
                                    ))
                                except Exception:
                                    pass
            except Exception as e:
                print(f"Etherscan V2 Fallback Error: {e}")
        return edges

class BitqueryCollectorWrapper(BaseCollector):
    name = "BitqueryCollector"

    @classmethod
    async def fetch(cls, session: aiohttp.ClientSession, target_address: str, chain: str) -> List[GBIOEdge]:
        if not BITQUERY_TOKEN:
            return []
        
        query = """
        query ($address: String!) {
          EVM(dataset: combined, network: eth) {
            Transfers(
              where: {any: [{Transfer: {Receiver: {is: $address}}}, {Transfer: {Sender: {is: $address}}}]}
              limit: {count: 50}
            ) {
              Transfer {
                Amount
                Currency { Symbol SmartContract }
                Sender
                Receiver
                Transaction { Hash Time }
              }
            }
          }
        }
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {BITQUERY_TOKEN}"
        }
        try:
            async with session.post(BITQUERY_URL, json={"query": query, "variables": {"address": target_address}}, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    edges = []
                    transfers = data.get("data", {}).get("EVM", {}).get("Transfers", [])
                    for t in transfers:
                        tr = t.get("Transfer", {})
                        sender = tr.get("Sender")
                        receiver = tr.get("Receiver")
                        if sender and receiver:
                            edge_type = TransferAction.RECEIVED_FROM if sender.lower() == target_address.lower() else TransferAction.SENT_TO
                            edge = GBIOEdge(
                                edge_id=f"{tr.get('Transaction', {}).get('Hash')}_{sender}_{receiver}",
                                action=edge_type,
                                source_node_id=sender,
                                target_node_id=receiver,
                                asset_symbol=tr.get("Currency", {}).get("Symbol", "ETH"),
                                asset_address=tr.get("Currency", {}).get("SmartContract", ""),
                                amount_native=float(tr.get("Amount") or 0.0),
                                timestamp=tr.get("Transaction", {}).get("Time", "1970-01-01T00:00:00Z"),
                                chain=chain,
                                evidence=EvidenceRecord(source_provider="Bitquery", retrieval_timestamp=datetime.now(timezone.utc), transaction_hash=tr.get("Transaction", {}).get("Hash"), confidence_score=1.0)
                            )
                            edges.append(edge)
                    return edges
        except Exception as e:
            print(f"Bitquery connection error: {e}")
        return []

async def run_all_collectors(session: aiohttp.ClientSession, target_address: str, chain: str) -> List[GBIOEdge]:
    """Runs all registered collectors in parallel using a shared session."""
    print(f"[{chain}] Activating Omni-Chain Multi-Provider Scraper for {target_address}")
    
    tasks = [
        AnkrCollector.fetch(session, target_address, chain),
        EtherscanV2Collector.fetch(session, target_address, chain),
        BitqueryCollectorWrapper.fetch(session, target_address, chain)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
        
    all_edges = []
    seen_txs = set()
    
    for result in results:
        if isinstance(result, list):
            for edge in result:
                # Deduplicate by tx hash + action
                uniq_id = f"{edge.edge_id}_{edge.action}"
                if uniq_id not in seen_txs:
                    seen_txs.add(uniq_id)
                    all_edges.append(edge)
        else:
            print(f"Collector Exception: {result}")
            
    print(f"[{chain}] Collected {len(all_edges)} unique transfers for {target_address}")
    return all_edges

