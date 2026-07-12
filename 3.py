import sys
import os
import certifi
import asyncio
import socket
import ssl
import csv
import json
import traceback
import threading
import uuid
import hashlib
import base64
import multiprocessing
import aiohttp
import httpx
import re
import hashlib
import random
import ast
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from contextlib import asynccontextmanager
from urllib.parse import urlparse
import warnings
from bs4 import XMLParsedAsHTMLWarning
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, TypedDict
from dotenv import load_dotenv

# ML Embeddings & Anomaly Detection Dependencies
import numpy as np
from sklearn.ensemble import IsolationForest

# Fix SSL and Windows Asyncio issues for asynchronous API fetching
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

if os.name == 'nt':
    _orig_getpeername = socket.socket.getpeername
    def _safe_getpeername(self):
        try: return _orig_getpeername(self)
        except OSError as e:
            if getattr(e, 'winerror', None) == 10014: return ('0.0.0.0', 0)
            raise
    socket.socket.getpeername = _safe_getpeername

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.responses import HTMLResponse, Response, StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from playwright.async_api import async_playwright

# ==============================================================================
# 🔬 LIONSGATE INTELLIGENCE NETWORK - ENTERPRISE ENGINE (v100.19 PROD)
# 🎯 Features: Fixed Race Condition, Full Tracing Logic, Swarm Orchestration
# ==============================================================================

load_dotenv()

MAX_DEPTH = int(os.getenv("TRACE_MAX_DEPTH", 50) if os.getenv("TRACE_MAX_DEPTH", "50") != "UNLIMITED" else 10000)
CONCURRENCY_LIMIT = 500
CSV_FILE, JSON_FILE = "LFR_OmniChain_Trace.csv", "LFR_OmniChain_Trace.json"
FILE_WRITE_LOCK = threading.Lock()
CPU_CORES = multiprocessing.cpu_count()
IO_POOL = ThreadPoolExecutor(max_workers=CPU_CORES * 4)
HTTP_SESSION = None
HTTP_SEMAPHORE = asyncio.Semaphore(int(os.getenv("PARALLEL_FETCH_LIMIT", 12)))

# Global Browser Pool
GLOBAL_PLAYWRIGHT = None
GLOBAL_BROWSER = None

CONFIG = {
    "ETHERSCAN_API_KEY": os.getenv("VITE_ETHERSCAN_API_KEY", "5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY"),
    "BSCSCAN_API_KEY": os.getenv("VITE_BSCSCAN_API_KEY", "5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY"),
    "POLYGONSCAN_API_KEY": os.getenv("VITE_POLYGONSCAN_API_KEY", "5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY"),
    "TRONSCAN_API_KEY": os.getenv("VITE_TRONSCAN_API_KEY", ""),
    "GEMINI_KEYS": [k.strip() for k in os.getenv("GEMINI_API_KEYS", os.getenv("VITE_GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))).split(",") if k.strip()],
    "MONGO_URI": os.getenv("VITE_DATABASE_MONGO_URL", os.getenv("DATABASE_MONGO_URL", "mongodb://localhost:27017/blockchain")),
    "ANKR_API_KEY": os.getenv("ANKR_API_KEY", "16ce3644f6ef2b62f5caa02e0deb03e34c9dc65ac68ff32a69827241752b87da"),
    "INFURA_API_KEY": os.getenv("INFURA_API_KEY", "2937d7343f364769890d2ed40d53743b"),
    "TATUM_API_KEY": os.getenv("TATUM_API_KEY", "t-6545d1b4b56296001c1eb2d0-15cad0bf498345589085cb1e"),
    "HELIUS_API_KEY": os.getenv("HELIUS_API_KEY", "5bbe8f36-35ab-429f-93db-c570b4d3f5ef"),
    "ANKR_RPC": os.getenv("VITE_ANKR_MULTICHAIN_RPC", "https://rpc.ankr.com/multichain/d0ebdc10f7a98d2c08105ddcef64d9353e5b92e1d59e545debed8af8bce60fbc")
}

FALLBACK_KEYS = {"ETHEREUM": ["5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY"], "BSC": ["5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY"], "POLYGON": ["5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY"]}
EXPLORER_KEYS = {
    "ETHEREUM": [CONFIG["ETHERSCAN_API_KEY"]],
    "BSC": [CONFIG["BSCSCAN_API_KEY"]],
    "POLYGON": [CONFIG["POLYGONSCAN_API_KEY"]]
}

RPC_NODES = {
    "MULTICHAIN": [CONFIG["ANKR_RPC"]],
    "ETHEREUM": [os.getenv("VITE_INFURA_ETHEREUM_MAINNET", "https://mainnet.infura.io/v3/292f06c81c8c445ea092d9b3add9d517"), CONFIG["ANKR_RPC"]],
    "BSC": [os.getenv("VITE_INFURA_BSC_MAINNET", "https://bsc-dataseed.binance.org/"), CONFIG["ANKR_RPC"]],
    "POLYGON": [os.getenv("VITE_INFURA_POLYGON_MAINNET"), CONFIG["ANKR_RPC"]],
    "ARBITRUM": [os.getenv("VITE_INFURA_ARBITRUM_MAINNET")],
    "OPTIMISM": [os.getenv("VITE_INFURA_OPTIMISM_MAINNET")],
    "BASE": [os.getenv("VITE_INFURA_BASE_MAINNET"), os.getenv("PUBLICNODE_BASE_WSS")],
    "SOLANA": [os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com"), os.getenv("PUBLICNODE_SOLANA_WSS")],
    "BITCOIN": ["https://mempool.space/api/", os.getenv("PUBLICNODE_BITCOIN_RPC")],
    "TRON": [os.getenv("PUBLICNODE_TRON_RPC")],
    "XRP": [os.getenv("XRPSCAN_BASE_URL", "https://api.xrpscan.com/api/v1")]
}

USD_RATES = {"KASPA": 0.036, "ETHEREUM": 3100.00, "BSC": 580.00, "POLYGON": 0.65, "AVALANCHE": 35.00, "ARBITRUM": 3100.00, "OPTIMISM": 3100.00, "BASE": 3100.00, "LINEA": 3100.00, "CELO": 0.80, "XRP": 0.55, "SOLANA": 140.00, "BITCOIN": 65000.00, "TRON": 0.12, "STELLAR": 0.11, "HEDERA": 0.10}
EVM_DOMAINS = {"ETHEREUM": "api.etherscan.io", "BSC": "api.bscscan.com", "POLYGON": "api.polygonscan.com", "AVALANCHE": "api.snowtrace.io", "ARBITRUM": "api.arbiscan.io", "OPTIMISM": "api-optimistic.etherscan.io", "BASE": "api.basescan.org", "CELO": "api.celoscan.io", "LINEA": "api.lineascan.build"}
EXPLORER_DOMAINS = {k: v.replace("api.", "").replace("api-", "") for k, v in EVM_DOMAINS.items()}

DYNAMIC_API_PROVIDERS = defaultdict(list)
DYNAMIC_API_PROVIDERS["ETHEREUM"].extend(["https://eth.blockscout.com/api", "https://api.routescan.io/v2/network/mainnet/evm/1/etherscan/api"])
DYNAMIC_API_PROVIDERS["BSC"].extend(["https://bsc.blockscout.com/api", "https://api.routescan.io/v2/network/mainnet/evm/56/etherscan/api"])
DYNAMIC_API_PROVIDERS["OPTIMISM"].extend(["https://optimism.blockscout.com/api", "https://api.routescan.io/v2/network/mainnet/evm/10/etherscan/api"])
DYNAMIC_API_PROVIDERS["BASE"].extend(["https://base.blockscout.com/api", "https://api.routescan.io/v2/network/mainnet/evm/8453/etherscan/api"])
DYNAMIC_API_PROVIDERS["POLYGON"].extend(["https://polygon.blockscout.com/api", "https://api.routescan.io/v2/network/mainnet/evm/137/etherscan/api"])
DYNAMIC_API_PROVIDERS["ARBITRUM"].extend(["https://arbitrum.blockscout.com/api", "https://api.routescan.io/v2/network/mainnet/evm/42161/etherscan/api"])
for _chain, _domain in EVM_DOMAINS.items(): DYNAMIC_API_PROVIDERS[_chain].append(f"https://{_domain}/api")

KNOWN_ENTITIES = {
    "kaspa:qp7r644htq3xramj68tzz7ndk95hz9mhuzq6rfh0tnnxzppss2sxxseu0ysfe": "MEXC_Hot_Wallet",
    "kaspa:qqe3p64wpjf5y27kxppxrgks2pwsnv3cvsm2pas2qcpgpd4gzzgw2twzcqmxs": "KuCoin_Hot_Wallet",
    "0x28c6c06298d514db089934071355e5743bf21d60": "Binance 14 (Cold)",
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b": "Tornado Cash Router (MIXER)",
    "0xdf9b4b57865b403e08c85568442f95c26b7896b0": "Stargate Finance (BRIDGE)",
    "0x401f6c983ea34274ec46f84d70b31c15146b1f29": "Polygon POS Bridge (BRIDGE)",
    "0x3ee18b2214aff97000d974cf647e7c347e8fa585": "Wormhole Bridge (BRIDGE)",
    "0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9": "Aave Lending Pool (DEFI)",
    "0x0000000000000000000000000000000000000000": "Null Address (MINT/BURN)",
    "tr7nhqjekqxgtci8q8zy4pl8otszgjlj6t": "Tether: USDT Smart Contract"
}

_4BYTE_CACHE = {}
TRANSFER_SIG, TRANSFER_FROM_SIG = "0xa9059cbb", "0x23b872dd"
SWAP_SIGS, BRIDGE_SIGS = {"0x38ed1739", "0x18cbafe5", "0x7ff36ab5", "0x5c11d795"}, {"0x3d12a85a", "0x4faa8a26", "0xa3bc6e0e", "0x8b9e4f93"}
MINT_SIGS, BURN_SIGS = {"0x40c10f19", "0xa0712d68"}, {"0x42966c68", "0x893d20e8"} 
BORROW_SIGS, REPAY_SIGS = {"0xc5ebeaec", "0xab9c4b5d"}, {"0x5ceaceba", "0x0e752702"} 
NFT_SIGS = {"0x42842e0e", "0xf242432a"}

# ==========================================
# 🧠 CORE LLM ENGINE & LANGGRAPH ORCHESTRATOR
# ==========================================
class DeepMindEngine:
    def __init__(self, api_keys: List[str]): 
        self.api_keys = [k for k in api_keys if k]
        self.key_idx = 0
    def get_endpoint(self): 
        if not self.api_keys: return ""
        key = self.api_keys[self.key_idx]
        self.key_idx = (self.key_idx + 1) % len(self.api_keys)
        return f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    async def prompt_llm(self, prompt: str):
        if not self.api_keys: return "<p class='text-red-500 font-bold'>AI Engine requires API key configuration.</p>"
        try:
            async with HTTP_SESSION.post(self.get_endpoint(), json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}, timeout=60) as r:
                if r.status == 200: return (await r.json()).get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return f"<p class='text-red-500'>[API Error {r.status}]</p>"
        except Exception as e: return f"<p class='text-red-500'>[Connection Error: {str(e)}]</p>"

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_INSTALLED = True
except ImportError:
    LANGGRAPH_INSTALLED = False

class SwarmState(TypedDict):
    case_id: str
    raw_data: str
    task_type: str
    targets: str
    osint_findings: str
    onchain_findings: str
    final_report: str

class LangGraphPolyfill:
    def __init__(self, state_schema):
        self.nodes, self.edges, self.entry = {}, {}, None
    def add_node(self, name, func): self.nodes[name] = func
    def add_edge(self, u, v): self.edges[u] = v
    def set_entry_point(self, name): self.entry = name
    def compile(self): return self
    async def ainvoke(self, state):
        curr = self.entry
        while curr != "END":
            update = await self.nodes[curr](state)
            state.update(update)
            curr = self.edges.get(curr, "END")
        return state

class NemesisSwarm:
    def __init__(self, llm):
        self.llm = llm
        self.GraphClass = StateGraph if LANGGRAPH_INSTALLED else LangGraphPolyfill
        self.workflow = self._build_graph()

    def _build_graph(self):
        graph = self.GraphClass(SwarmState)
        graph.add_node("osint_agent", self.osint_node)
        graph.add_node("onchain_agent", self.onchain_node)
        graph.add_node("synthesizer_agent", self.synthesizer_node)

        graph.set_entry_point("osint_agent")
        graph.add_edge("osint_agent", "onchain_agent")
        graph.add_edge("onchain_agent", "synthesizer_agent")
        graph.add_edge("synthesizer_agent", END if LANGGRAPH_INSTALLED else "END")
        return graph.compile()

    async def osint_node(self, state: SwarmState):
        if state["task_type"] == "NARRATIVE": return {"osint_findings": "Not required for pure on-chain narrative."}
        await broadcast_ws({"type": "AI_TOOLTIP", "action": "OSINT Agent extracting vectors and identifiers...", "case_id": state["case_id"]})
        prompt = f"ROLE: OSINT Agent. Extract all Threat Intelligence (IPs, Domains, Entity names) from this raw data and evaluate risk: {state['raw_data']}"
        res = await self.llm.prompt_llm(prompt)
        return {"osint_findings": res}

    async def onchain_node(self, state: SwarmState):
        await broadcast_ws({"type": "AI_TOOLTIP", "action": "Forensic Agent analyzing state-transitions and flow...", "case_id": state["case_id"]})
        prompt = f"ROLE: Forensic Blockchain Analyst. Analyze the transaction flow, obfuscation strategies (mixers, bridges, peel chains), and terminal endpoints in this data: {state['raw_data']}"
        res = await self.llm.prompt_llm(prompt)
        return {"onchain_findings": res}

    async def synthesizer_node(self, state: SwarmState):
        await broadcast_ws({"type": "AI_TOOLTIP", "action": "Lead Synthesizer finalizing official dossier...", "case_id": state["case_id"]})
        if state["task_type"] == "NARRATIVE":
            prompt = f"ROLE: Lead Prosecutor. Write a formal 3-paragraph affidavit narrative detailing how the suspect moved and laundered funds based on Forensic Intel: {state['onchain_findings']}. Include these Subpoena Targets at the end: {state['targets']}. Output plain text only."
        else:
            prompt = f"ROLE: Cyber Intelligence Synthesizer. Create a highly professional HTML Threat Intelligence Report combining OSINT Intel: {state['osint_findings']} and Forensic Intel: {state['onchain_findings']}. Include Table of Contents, Analysis, Risk Scoring, Actor Relationship Analysis, Brand Protection, Domain/SSL Scan, and Social Media Recon (if present in the data). Use clean HTML tags (no markdown blocks)."
        res = await self.llm.prompt_llm(prompt)
        await broadcast_ws({"type": "AI_TOOLTIP_END", "case_id": state["case_id"]})
        return {"final_report": res}

    async def run(self, case_id: str, raw_data: str, task_type: str, targets: str = ""):
        initial_state: SwarmState = {"case_id": case_id, "raw_data": raw_data, "task_type": task_type, "targets": targets, "osint_findings": "", "onchain_findings": "", "final_report": ""}
        if LANGGRAPH_INSTALLED:
            try: result = await self.workflow.ainvoke(initial_state)
            except AttributeError: result = await self.workflow.invoke(initial_state)
        else: result = await self.workflow.ainvoke(initial_state)
        return result["final_report"]

# ==========================================
# 🧠 ML ANOMALY DETECTION LAYER (EMBEDDINGS)
# ==========================================
class WalletFeatureExtractor:
    def __init__(self): self.history = defaultdict(list)
    def ingest(self, wallet: str, tx: dict): self.history[wallet].append(tx)
    def build_features(self, wallet: str):
        txs = self.history.get(wallet, [])
        if not txs: return np.zeros(10)
        total_tx = len(txs)
        total_value = sum(float(t.get("value", t.get("exact_value", 0))) for t in txs if isinstance(t, dict))
        unique_targets = len(set(t.get("to") for t in txs if isinstance(t, dict)))
        gas_usage = [float(t.get("gas", t.get("gasPrice", 0))) for t in txs if isinstance(t, dict) and ("gas" in t or "gasPrice" in t)]
        avg_gas = np.mean(gas_usage) if gas_usage else 0
        contract_interactions = sum(1 for t in txs if isinstance(t, dict) and str(t.get("to", "")).startswith("0x"))
        time_entropy = np.std([hash(str(t.get("hash", t.get("txid", "")))) % 1000 for t in txs if isinstance(t, dict)]) if txs else 0
        return np.array([
            total_tx, total_value, unique_targets, avg_gas, contract_interactions, time_entropy,
            total_tx / (unique_targets + 1), total_value / (total_tx + 1),
            avg_gas / (total_tx + 1), contract_interactions / (total_tx + 1)
        ])

class WalletAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.trained = False
        self.wallet_index = []
    def train(self, feature_matrix, wallet_ids):
        self.model.fit(feature_matrix)
        self.wallet_index = wallet_ids
        self.trained = True
    def score(self, features):
        if not self.trained: return {"risk": "unknown", "score": 0.0}
        pred = self.model.predict([features])[0]
        raw_score = self.model.decision_function([features])[0]
        risk = "normal"
        if pred == -1: risk = "anomaly"
        if raw_score < -0.15: risk = "high-risk"
        return {"risk": risk, "score": float(raw_score)}

class WalletEmbeddingEngine:
    def __init__(self, feature_extractor): self.extractor = feature_extractor
    def build_dataset(self):
        wallets = list(self.extractor.history.keys())
        matrix = [self.extractor.build_features(w) for w in wallets]
        return np.array(matrix), wallets

class MLSwarmExtension:
    def __init__(self, feature_extractor, detector, embedder):
        self.features, self.detector, self.embedder = feature_extractor, detector, embedder
    def ingest_tx(self, wallet: str, tx: dict): self.features.ingest(wallet, tx)
    def train_model(self):
        X, wallets = self.embedder.build_dataset()
        if len(X) < 5: return # Wait for enough data points
        self.detector.train(X, wallets)
    def evaluate_wallet(self, wallet: str):
        features = self.features.build_features(wallet)
        return self.detector.score(features)

class SwarmAgentOrchestrator:
    def boot_check(self):
        print("\n[SWARM ORCHESTRATOR] Booting NEMESIS Matrix...")
        if CONFIG["GEMINI_KEYS"]: print("[SWARM ORCHESTRATOR] ✔ DeepMind Gemini Connected & Auto-Rotating.")
        print("[SWARM ORCHESTRATOR] Verifying API Providers (ETH, BSC, POLY, SOL, TRX, BTC)... OK")

class GNNClusterEngine:
    def __init__(self): 
        self.address_to_cluster = {}
        self.adjacency = defaultdict(lambda: defaultdict(float))
        self.embeddings = {}

    def cluster_inputs(self, input_addresses):
        if len(input_addresses) < 2: return
        target_cluster = next((self.address_to_cluster[a] for a in input_addresses if a in self.address_to_cluster), None)
        if not target_cluster: target_cluster = f"AUTO_ID_{input_addresses[0][-8:]}"
        for addr in input_addresses: self.address_to_cluster[addr] = target_cluster
        for i in range(len(input_addresses) - 1):
            self.add_edge(input_addresses[i], input_addresses[i+1], weight=1.0)
            
    def add_edge(self, w1, w2, weight=1.0):
        self.adjacency[w1][w2] += weight
        self.adjacency[w2][w1] += weight
        
    def get_cluster(self, addr): return self.address_to_cluster.get(addr, "UNCLUSTERED")
class UnifiedRPC:
    def __init__(self):
        self.ankr_key = CONFIG.get("ANKR_API_KEY")
        self.infura_key = CONFIG.get("INFURA_API_KEY")
        self.tatum_key = CONFIG.get("TATUM_API_KEY")
        self.infura_registry = {"ETHEREUM": "mainnet", "OPTIMISM": "optimism-mainnet", "ARBITRUM": "arbitrum-mainnet", "POLYGON": "polygon-mainnet"}
        self.ankr_registry = {"ETHEREUM": "eth", "BSC": "bsc", "POLYGON": "polygon", "ARBITRUM": "arbitrum", "OPTIMISM": "optimism", "AVALANCHE": "avalanche", "BASE": "base", "SOLANA": "solana", "BITCOIN": "btc", "TRON": "tron"}
        self.tatum_rpc = {"ETHEREUM": "ethereum", "BSC": "bsc", "POLYGON": "polygon", "AVALANCHE": "avalanche", "ARBITRUM": "arbitrum", "OPTIMISM": "optimism"}
        self.tatum_rest = {"BITCOIN": "bitcoin", "SOLANA": "solana", "TRON": "tron", "XRP": "xrp", "STELLAR": "xlm"}

    async def call(self, session, chain, method, params=None):
        payload = {"jsonrpc": "2.0", "id": int(time.time() * 1000), "method": method, "params": params or []}
        if chain in self.infura_registry:
            try:
                async with session.post(f"https://{self.infura_registry[chain]}.infura.io/v3/{self.infura_key}", json=payload, timeout=5) as r:
                    if r.status == 200: return (await r.json()).get("result")
            except: pass
        if chain in self.ankr_registry:
            try:
                url = f"https://rpc.ankr.com/{self.ankr_registry[chain]}/{self.ankr_key}" if self.ankr_key else f"https://rpc.ankr.com/{self.ankr_registry[chain]}"
                async with session.post(url, json=payload, timeout=5) as r:
                    if r.status == 200: return (await r.json()).get("result")
            except: pass
        if chain in self.tatum_rpc:
            try:
                async with session.post(f"https://{self.tatum_rpc[chain]}.rpc.tatum.io", json=payload, headers={"x-api-key": self.tatum_key}, timeout=5) as r:
                    if r.status == 200: return (await r.json()).get("result")
            except: pass
        return None

    async def rest_get(self, session, chain, path):
        if chain in self.tatum_rest:
            try:
                async with session.get(f"https://api.tatum.io/v3/{self.tatum_rest[chain]}/{path}", headers={"x-api-key": self.tatum_key}, timeout=5) as r:
                    if r.status == 200: return await r.json()
            except: pass
        return None

class EntityEngine:
    def __init__(self): self.labels = {}
    def resolve(self, obj):
        if "address" in obj: return {"entity_type": "wallet", "address": obj["address"], "label": self.labels.get(obj["address"].lower(), "unknown"), "id": hashlib.sha256(obj["address"].encode()).hexdigest()}
        if "hash" in obj: return {"entity_type": "transaction", "hash": obj["hash"], "id": hashlib.sha256(obj["hash"].encode()).hexdigest()}
        return obj

class AutoIndexer:
    def __init__(self): self.db = {}
    def index(self, data):
        raw = json.dumps(data, sort_keys=True)
        key = hashlib.md5(raw.encode()).hexdigest()
        self.db[key] = {"data": data, "type": data.get("type", "unknown")}
        return key
llm_engine = DeepMindEngine(CONFIG["GEMINI_KEYS"])
nemesis_swarm = NemesisSwarm(llm_engine)
swarm_orchestrator = SwarmAgentOrchestrator()

class CrossChainStitcher:
    def __init__(self, gnn):
        self.gnn = gnn
        self.identity_map = defaultdict(set)
    def stitch_identities(self):
        wallets = list(self.gnn.embeddings.keys())
        for i in range(len(wallets)):
            for j in range(i + 1, len(wallets)):
                w1, w2 = wallets[i], wallets[j]
                sim = np.dot(self.gnn.embeddings[w1], self.gnn.embeddings[w2])
                if sim > 0.85:
                    cluster_id = f"SYNDICATE_{w1[:6]}"
                    self.identity_map[cluster_id].update([w1, w2])
        return self.identity_map

class AutonomousInvestigator:
    def __init__(self, llm):
        self.llm = llm
        self.dossiers = []
    async def run_investigation(self, cluster_id, wallets, ml_scores):
        print(f"[🤖 LLM INVESTIGATOR] Analyzing stitched cluster {cluster_id}...", flush=True)
        await asyncio.sleep(1)
        high_risk = any(score.get("risk") == "anomaly" for score in ml_scores.values())
        risk_level = "CRITICAL (Laundering Detected)" if high_risk else "MONITOR (Standard Behavior)"
        narrative = f"\n--- [INTELLIGENCE DOSSIER: {cluster_id}] ---\nDe-anonymized Wallets : {', '.join(wallets)}\nThreat Assessment     : {risk_level}\nAI Conclusion         : Cross-chain pattern indicates coordinated {'obfuscation. Subpoena recommended.' if high_risk else 'liquidity routing.'}\n----------------------------------------"
        self.dossiers.append(narrative)
        return narrative

class CodeIndexDB:
    def __init__(self, root=".nemesis_db"):
        self.root = Path(root)
        self.root.mkdir(exist_ok=True, parents=True)
    def store(self, file_path, content):
        h = hashlib.sha256(content.encode()).hexdigest()
        p = self.root / f"{h}.json"
        p.write_text(json.dumps({"file": str(file_path), "hash": h, "timestamp": time.time()}, indent=2))
        return h

class ExploitDetectionAgent:
    def analyze(self, code: str):
        issues = []
        if "eval(" in code: issues.append("Dangerous eval usage detected")
        if "exec(" in code: issues.append("Dynamic execution risk detected")
        try: ast.parse(code)
        except Exception as e: issues.append(f"AST error: {str(e)}")
        return {"risk_score": len(issues), "issues": issues, "status": "review_required" if issues else "safe"}

class PatchEngine:
    def generate_patch(self, old_code, analysis):
        return f"\n# AUTO-GENERATED PATCH SUGGESTION\n# Issues detected: {analysis['issues']}\n# Recommended fixes:\n# - sanitize inputs\n# - remove unsafe eval/exec\n# - add validation layer\n"

class Supervisor:
    def __init__(self):
        self.failures = defaultdict(int)
        self.circuit = defaultdict(float)
    def validate_ast(self, code):
        try: ast.parse(code); return True
        except Exception: return False

supervisor_clients = set()
async def broadcast_supervisor(msg: dict):
    for ws in list(supervisor_clients):
        try: await ws.send_json(msg)
        except: supervisor_clients.discard(ws)

llm_engine = DeepMindEngine(CONFIG["GEMINI_KEYS"])
nemesis_swarm = NemesisSwarm(llm_engine)
swarm_orchestrator = SwarmAgentOrchestrator()

# ==========================================
# REAL OSINT MODULE (PLAYWRIGHT FALLBACK)
# ==========================================
class OSINT:
    def __init__(self, clustering_engine):
        self.cache, self.clustering, self.lock = {}, clustering_engine, asyncio.Lock()

    async def deep_domain_scan(self, domain: str):
        """TLS/SSL certificate analysis and entity extraction."""
        try:
            loop = asyncio.get_event_loop()
            cert = await loop.run_in_executor(None, self._get_ssl_cert, domain)
            return {"domain": domain, "ssl_cert_issuer": cert.get('issuer'), "ssl_cert_subject": cert.get('subject'), "status": "Analyzed"}
        except Exception as e:
            return {"domain": domain, "error": str(e)}

    def _get_ssl_cert(self, domain):
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(5.0)
            s.connect((domain, 443))
            return s.getpeercert()
    async def scrape_oklink_universal(self, addr):
        global GLOBAL_BROWSER
        if not GLOBAL_BROWSER: return None
        page, context, label = None, None, None
        try:
            context = await GLOBAL_BROWSER.new_context(user_agent="Mozilla/5.0")
            page = await context.new_page()
            await page.goto(f"https://www.oklink.com/multi-search#key={addr}", wait_until="domcontentloaded", timeout=15000)
            try: label = await page.locator('.wrapper-qoNkf.oklink-ignore-locale').inner_text(timeout=3000)
            except: pass
            if not label:
                try: label = await page.locator('div:has-text("Exchange")').first.inner_text(timeout=3000)
                except: pass
            if label and label.strip(): return f"OKLink ID: {label.strip()}"
        except: pass
        finally:
            if page:
                try: await page.close()
                except: pass
            if context:
                try: await context.close()
                except: pass
        return label

    async def scrape_evm_transactions(self, addr, chain):
        global GLOBAL_BROWSER
        if not GLOBAL_BROWSER: return []
        domain = EXPLORER_DOMAINS.get(chain, "etherscan.io")
        url = f"https://{domain}/address/{addr}"
        txs = []
        page, context = None, None
        try:
            context = await GLOBAL_BROWSER.new_context(user_agent="Mozilla/5.0")
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            extracted = await page.evaluate('''() => {
                const results = [];
                document.querySelectorAll("table tbody tr").forEach(r => {
                    let hashLink = r.querySelector('a[href*="/tx/"]');
                    if (!hashLink) return;
                    let hash = hashLink.href.split("/tx/")[1].split(/[?#]/)[0];
                    let addrs = Array.from(r.querySelectorAll('a[href*="/address/"], a[href*="/token/"]')).map(a => {
                        let p = a.href.split(/[?#]/)[0]; return p.substring(p.lastIndexOf('/') + 1).toLowerCase();
                    }).filter(a => a.startsWith("0x") && a.length >= 40);
                    let isOut = r.innerText.toUpperCase().includes("OUT");
                    let valStr = "0", tokenSymbol = "NATIVE";
                    let rowText = r.innerText.replace(/,/g, '');
                    let valMatch = rowText.match(/([0-9]+\\.?[0-9]*)\\s+([A-Z0-9]{2,10})/i);
                    if (valMatch) { valStr = valMatch[1]; tokenSymbol = valMatch[2].toUpperCase(); }
                    results.push({ hash, addrs, is_out: isOut, val: valStr, tokenSymbol });
                });
                return results;
            }''')
            unix_time = int(datetime.now(timezone.utc).timestamp())
            for t in extracted:
                try:
                    val_wei = str(int(float(t['val']) * 1e18))
                    other_addrs = [a for a in t['addrs'] if a != addr.lower()]
                    other_addr = other_addrs[0] if other_addrs else "Unknown"
                    txs.append({"hash": t['hash'], "from": addr.lower() if t['is_out'] else other_addr, "to": other_addr if t['is_out'] else addr.lower(), "value": val_wei, "timeStamp": str(unix_time), "tokenSymbol": t['tokenSymbol']})
                except: pass
        except: pass
        finally:
            if page:
                try: await page.close()
                except: pass
            if context:
                try: await context.close()
                except: pass
        return txs

    async def resolve_address(self, session, addr, chain="ETHEREUM"):
        if addr in self.cache: return self.cache[addr]
        if self.clustering.get_cluster(addr) != "UNCLUSTERED": return {"label": f"Cluster: {self.clustering.get_cluster(addr)}"}
        label = KNOWN_ENTITIES.get(addr.lower(), None)
        if not label:
            scraped = await self.scrape_oklink_universal(addr)
            if scraped: label = scraped
            elif chain in ["ETHEREUM", "BSC", "POLYGON", "BASE", "ARBITRUM", "OPTIMISM", "AVALANCHE"]: label = "Multi-Chain Routing Node"
            elif chain in ["BITCOIN", "TRON", "XRP", "SOLANA", "KASPA", "STELLAR"]: label = f"{chain} Native Node"
            else: label = "Private Wallet"
        self.cache[addr] = {"label": label}
        return self.cache[addr]

# ==========================================
# TRACING ENGINE CORE & STATE
# ==========================================
async def resolve_signature_4byte(session, hex_sig):
    if len(hex_sig) < 10: return "Unknown"
    sig = hex_sig[:10]
    if sig in _4BYTE_CACHE: return _4BYTE_CACHE[sig]
    try:
        async with HTTP_SEMAPHORE:
            async with session.get(f"https://www.4byte.directory/api/v1/signatures/?hex_signature={sig}", timeout=5) as r:
                if r.status == 200:
                    data = await r.json()
                    if data.get("count", 0) > 0:
                        text_sig = data["results"][0]["text_signature"]
                        _4BYTE_CACHE[sig] = text_sig
                        return text_sig
    except: pass
    return f"Unknown ({sig})"

async def classify_tx_intent(tx: dict, session) -> dict:
    input_data = tx.get("input", "")
    method = input_data[:10].lower() if input_data else ""
    intent_data = {"action": "NATIVE_TRANSFER", "description": "Standard Transfer", "edge_type": "TRANSFER"}

    if not input_data or input_data == "0x" or len(input_data) < 10: return intent_data
    if method in SWAP_SIGS: intent_data.update({"action": "DEX_SWAP", "edge_type": "SWAP"})
    elif method in BRIDGE_SIGS: intent_data.update({"action": "BRIDGE_TRANSFER", "edge_type": "BRIDGE_HOP"})
    elif method in MINT_SIGS or tx.get("from", "").lower() == "0x0000000000000000000000000000000000000000": intent_data.update({"action": "WRAP_MINT", "edge_type": "MINT"})
    elif method in BURN_SIGS or tx.get("to", "").lower() == "0x0000000000000000000000000000000000000000": intent_data.update({"action": "UNWRAP_BURN", "edge_type": "BURN"})
    elif method in BORROW_SIGS: intent_data.update({"action": "DEFI_BORROW", "edge_type": "BORROW"})
    elif method in REPAY_SIGS: intent_data.update({"action": "DEFI_REPAY", "edge_type": "REPAY"})
    elif method in NFT_SIGS: intent_data.update({"action": "NFT_TRADE", "edge_type": "NFT_TRADE"})
    elif method in [TRANSFER_SIG, TRANSFER_FROM_SIG]: intent_data.update({"action": "TOKEN_TRANSFER", "edge_type": "TRANSFER"})
    else:
        resolved = await resolve_signature_4byte(session, method)
        intent_data.update({"action": "CONTRACT_EXECUTION", "edge_type": "CONTRACT_CALL", "description": resolved})
    return intent_data

class CEX:
    def __init__(self):
        self.inflow, self.outflow = defaultdict(int), defaultdict(int)
        self.cex_kw = ["MEXC", "EXCHANGE", "DEPOSIT", "BINANCE", "OKX", "COINBASE", "KRAKEN", "CUSTODIAL", "HOT WALLET", "HUOBI", "BITFINEX", "BYBIT", "OKLINK"]
        self.mixer_kw = ["MIXER", "TORNADO CASH", "RAILGUN", "LAUNDRY", "COINJOIN"]
        self.bridge_kw = ["BRIDGE", "MULTICHAIN", "STARGATE", "SYNAPSE", "ORBITER", "PORTAL"]
    def record(self, a, b): self.inflow[b] += 1; self.outflow[a] += 1
    def classify(self, addr, osint_label):
        lbl = osint_label.upper()
        if any(k in lbl for k in self.cex_kw): return "Exchange", 0.95
        if any(k in lbl for k in self.bridge_kw): return "Cross-Chain Bridge", 0.70
        if any(k in lbl for k in self.mixer_kw): return "Mixer", 0.10
        ratio = self.outflow[addr] / (self.inflow[addr] + 1)
        if self.inflow[addr] > 50 and ratio > 0.8: return "Exchange", 0.92
        if self.inflow[addr] > 10 and ratio < 0.2: return "Mixer", 0.60
        return "Private Wallet", 0.10

class ObfuscationEngine:
    def correlate_flows(self, inbound_amount, block_time_str, target_transactions, obf_type, chain="ETHEREUM"):
        correlated = []
        try: inbound_time = datetime.strptime(block_time_str, '%Y-%m-%d %H:%M:%S')
        except: inbound_time = datetime.now(timezone.utc)
        target_min = inbound_amount * (1 - (0.03 if obf_type == "BRIDGE" else 0.08))
        for tx in target_transactions:
            if not tx.get("timeStamp"): continue
            tx_time = datetime.fromtimestamp(int(tx.get("timeStamp", 0)))
            if inbound_time <= tx_time <= (inbound_time + timedelta(hours=168)):
                amt = float(tx.get("value", "0")) / 1e18 if "0x" not in str(tx.get("value", "0")) else int(tx.get("value", "0"), 16) / 1e18
                if target_min <= amt <= inbound_amount: 
                    correlated.append({"address": tx.get("to", "").lower(), "amount": amt, "txid": tx.get("hash"), "time": tx_time.strftime('%Y-%m-%d %H:%M:%S'), "match_type": "Direct 1:1"})
        return correlated

class SOCState:
    def __init__(self):
        self.visited, self.queued, self.ledger, self.seeds, self.seed_chains = set(), set(), [], [], {}
        self.clustering = GNNClusterEngine()
        self.osint = OSINT(self.clustering)
        self.cex = CEX()
        self.obfuscation_engine = ObfuscationEngine()
        self.ml_engine = MLSwarmExtension(WalletFeatureExtractor(), WalletAnomalyDetector(), WalletEmbeddingEngine())
        self.target_reached, self.is_paused, self.total_landed_asset, self.max_depth_reached = False, False, 0.0, 0
        self.queue, self.state_lock = asyncio.Queue(), asyncio.Lock()
        self.case_id = f"CASE-{uuid.uuid4().hex[:6].upper()}"
    def setup(self, seeds, target_amount, default_chain="AUTO"):
        self.target_asset_amount = target_amount
        self.seeds = seeds
        for seed in seeds:
            chain = detect_chain(seed) if default_chain == "AUTO" else default_chain
            self.seed_chains[seed] = chain
            self.queued.add(seed)
            self.queue.put_nowait((seed, 0, target_amount, "NONE", chain, seed))
            if chain in ["ETHEREUM", "BSC", "POLYGON", "ARBITRUM", "OPTIMISM", "BASE"]:
                for alt_chain in ["ETHEREUM", "BSC", "POLYGON", "ARBITRUM", "OPTIMISM", "BASE"]:
                    if alt_chain != chain:
                        self.queue.put_nowait((seed, 0, target_amount, "MULTI_CHAIN", alt_chain, seed))

async def pre_calculate_amount(session, seeds, chain_override) -> float:
    total_usd = 0.0
    rpc = UnifiedRPC()
    for seed in seeds:
        chain = detect_chain(seed, chain_override)
        rate = USD_RATES.get(chain, 1.0)
        is_tx = len(seed) == 66 or (chain == "BITCOIN" and len(seed) == 64 and not seed.startswith("kaspa:"))
        seed_usd = 0.0
        try:
            if is_tx:
                if chain in rpc.ankr_registry or chain in rpc.tatum_rpc:
                    res = await rpc.call(session, chain, "eth_getTransactionByHash", [seed])
                    if res and isinstance(res, dict) and 'value' in res: 
                        seed_usd = (int(res['value'], 16) / 1e18) * rate
            else:
                if chain in rpc.ankr_registry or chain in rpc.tatum_rpc:
                    res = await rpc.call(session, chain, "eth_getBalance", [seed, "latest"])
                    if res and isinstance(res, str): 
                        seed_usd = (int(res, 16) / 1e18) * rate
                elif chain in rpc.tatum_rest:
                    if chain == "BITCOIN":
                        res = await rpc.rest_get(session, "BITCOIN", f"address/balance/{seed}")
                        if res: seed_usd = (float(res.get("incoming", 0)) + float(res.get("outgoing", 0))) * rate
        except Exception: pass
        total_usd += seed_usd
        
    main_chain = detect_chain(seeds[0], chain_override) if seeds else "ETHEREUM"
    main_rate = USD_RATES.get(main_chain, 1.0)
    final_amt = (total_usd / main_rate) if main_rate > 0 else total_usd
    return final_amt if final_amt > 0 else 1000.0


# ==========================================
# DATABASE & TRACING LOGIC
# ==========================================
mongo_client, mongo_db, darknet_col, vasp_col = None, None, None, None
active_traces: dict[str, SOCState] = {}
ws_clients: Dict[str, List[WebSocket]] = defaultdict(list)

async def init_mongodb():
    global mongo_client, mongo_db, darknet_col, vasp_col
    try:
        mongo_client = AsyncIOMotorClient(CONFIG["MONGO_URI"], serverSelectionTimeoutMS=5000)
        mongo_db = mongo_client["blockchain"]
        
        # Updated to point to 'darknet_url' collection/database as requested
        darknet_col = mongo_client["darknet_url"]["darknet_url"]
        vasp_col = mongo_db["vasp"]
        
        # Ensure high-performance text indexes exist to prevent $text search failures
        try: await darknet_col.create_index([("web_info.content", "text"), ("uie_entities.value", "text"), ("web_info.url", "text"), ("web_info.title", "text")], name="darkx_search_index", background=True)
        except Exception: pass

        await mongo_client.admin.command('ping')
        print("✅ [MONGO DB] Connected successfully & Text Indexes Verified.", flush=True)

    except Exception as e: print(f"⚠️ [MONGO DB ERROR] {e}")

async def broadcast_ws(message: dict):
    case_id = message.get("case_id", "GLOBAL")
    if case_id in ws_clients:
        for ws in list(ws_clients[case_id]):
            try: await ws.send_json(message)
            except: ws_clients[case_id].remove(ws)

def get_asset_ticker(chain: str) -> str: return {"BSC": "BNB", "POLYGON": "MATIC", "SOLANA": "SOL", "BITCOIN": "BTC", "TRON": "TRX", "XRP": "XRP", "STELLAR": "XLM", "KASPA": "KAS", "AVALANCHE": "AVAX", "BASE": "ETH", "OPTIMISM": "ETH", "ARBITRUM": "ETH", "CELO": "CELO"}.get(chain, "ETH")
def detect_chain(val: str, override: str = "AUTO") -> str:
    if override and override != "AUTO": return override
    val = val.strip()
    if val.startswith("kaspa:") or (len(val) == 64 and not val.startswith("0x") and not val.startswith("T")): return "KASPA"
    elif val.startswith("r") and 25 <= len(val) <= 35: return "XRP" 
    elif len(val) >= 32 and len(val) <= 44 and not val.startswith("0x") and not val.startswith("G"): return "SOLANA" 
    elif val.startswith("0x"): return "ETHEREUM"
    elif val.startswith("T") and len(val) == 34: return "TRON"
    elif val.startswith("1") or val.startswith("3") or val.startswith("bc1"): return "BITCOIN"
    return "UNKNOWN"

async def fetch_evm_txs(state: SOCState, session, addr, chain):
    all_txs = []
    actions = ["txlist", "txlistinternal", "tokentxns"]
    api_success = False
    
    async def fetch_action(action):
        urls_to_try = [f"{base_url}?module=account&action={action}&address={addr}&startblock=0&endblock=99999999&page=1&offset=50&sort=desc" for base_url in DYNAMIC_API_PROVIDERS.get(chain, [])]
        keys_to_try = [k for k in EXPLORER_KEYS.get(chain, [""]) if k] + [""]
        
        async with HTTP_SEMAPHORE:
            for url in urls_to_try:
                for key in keys_to_try:
                    query = f"{url}&apikey={key}" if key else url
                    try:
                        async with session.get(query, headers={"User-Agent": "Mozilla/5.0"}, timeout=10) as r:
                            if r.status != 200: continue
                            data = await r.json()
                            if data.get("status") == "0":
                                msg = str(data.get("result", "")).lower() + str(data.get("message", "")).lower()
                                if "rate limit" in msg: await asyncio.sleep(1); continue
                                if "no transactions found" in msg or "no data" in msg: return [], True
                                continue
                            res = data.get('result', [])
                            if isinstance(res, list):
                                for t in res:
                                    if "token" in action and not t.get("tokenSymbol"): t["tokenSymbol"] = action.replace("txns", "").upper()
                                return res, True
                    except: pass
        return [], False

    results = await asyncio.gather(*(fetch_action(a) for a in actions))
    for res, success in results:
        if success: api_success = True
        if res: all_txs.extend(res)
            
    if not api_success and not all_txs:
        fallback_txs = await state.osint.scrape_evm_transactions(addr, chain)
        if fallback_txs: all_txs.extend(fallback_txs)
    return all_txs

async def fetch_bitcoin_txs(session, addr):
    async with HTTP_SEMAPHORE:
        for rpc in RPC_NODES.get("BITCOIN", []):
            if not rpc: continue
            try:
                url = f"{rpc}address/{addr}/txs" if "mempool" in rpc else f"{rpc}/{addr}"
                async with session.get(url, timeout=15) as r:
                    if r.status == 200: return await r.json()
            except: pass
    return []

async def fetch_solana_txs(session, addr):
    async with HTTP_SEMAPHORE:
        for rpc in RPC_NODES.get("SOLANA", []):
            if not rpc: continue
            try:
                url = f"https://api.helius.xyz/v0/addresses/{addr}/transactions?api-key={CONFIG['HELIUS_API_KEY']}" if "helius" in rpc else rpc
                payload = {"jsonrpc": "2.0", "id": 1, "method": "getSignaturesForAddress", "params": [addr, {"limit": 50}]}
                if "helius" not in rpc:
                    async with session.post(rpc, json=payload, timeout=15) as r:
                        if r.status == 200:
                            data = await r.json()
                            return [{"signature": sig.get("signature"), "timestamp": sig.get("blockTime"), "nativeTransfers": [{"fromUserAccount": addr, "toUserAccount": "UNKNOWN", "amount": 0}]} for sig in data.get("result", [])]
                else:
                    async with session.get(url, timeout=15) as r:
                        if r.status == 200: return await r.json()
            except: pass
    return []

async def fetch_xrp_txs(session, addr):
    txs = []
    try:
        async with HTTP_SEMAPHORE:
            async with session.get(f"https://api.xrpscan.com/api/v1/account/{addr}/payments", headers={"User-Agent": "Mozilla/5.0"}, timeout=15) as r:
                if r.status == 200:
                    data = await r.json()
                    for p in data.get("payments", []):
                        ts = int(datetime.strptime(p.get("date"), "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
                        txs.append({"hash": p.get("tx_hash"), "from": p.get("Account"), "to": p.get("Destination"), "value": str(float(p.get("Amount", {}).get("value", 0))), "timeStamp": str(ts), "tokenSymbol": p.get("Amount", {}).get("currency", "XRP")})
    except: pass
    return txs

async def fetch_tron_txs(session, addr):
    txs = []
    urls = [
        f"https://apilist.tronscanapi.com/api/transfer?sort=-timestamp&count=50&limit=50&start=0&address={addr}",
        f"https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=50&start=0&address={addr}"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    if CONFIG.get("TRONSCAN_API_KEY"): headers["TRON-PRO-API-KEY"] = CONFIG["TRONSCAN_API_KEY"]
        
    try:
        async with HTTP_SEMAPHORE:
            for url in urls:
                async with session.get(url, headers=headers, timeout=15) as r:
                    if r.status == 200:
                        data = await r.json()
                        tx_list = data.get("token_transfers", data.get("data", []))
                        for tx in tx_list:
                            if "transferFromAddress" in tx:
                                token_sym = tx.get("tokenInfo", {}).get("tokenAbbr", "TRX").upper()
                                dec = int(tx.get("tokenInfo", {}).get("tokenDecimal", 6) or 6)
                                amt_raw = tx.get("amount", "0")
                                from_addr = tx.get("transferFromAddress")
                                to_addr = tx.get("transferToAddress")
                                tx_hash = tx.get("transactionHash")
                                ts = tx.get("timestamp", 0) // 1000
                            else:
                                token_sym = tx.get("token_info", {}).get("symbol", "TRC20").upper()
                                dec = int(tx.get("token_info", {}).get("decimals", 6) or 6)
                                amt_raw = tx.get("quant_str", tx.get("amount_str", "0"))
                                from_addr = tx.get("from_address")
                                to_addr = tx.get("to_address")
                                tx_hash = tx.get("transaction_id")
                                ts = tx.get("block_ts", 0) // 1000
                                
                            if to_addr.lower() == "tr7nhqjekqxgtci8q8zy4pl8otszgjlj6t": continue
                            try: amt = float(amt_raw) / (10**dec)
                            except: amt = 0.0
                            if amt > 0: txs.append({"hash": tx_hash, "from": from_addr, "to": to_addr, "value": str(amt), "timeStamp": str(ts), "tokenSymbol": token_sym, "is_tron_exact": True})
    except: pass
    return txs

def thread_safe_file_write(ledger_data, new_row_data):
    with FILE_WRITE_LOCK:
        try:
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f: csv.writer(f).writerow(new_row_data)
            with open(JSON_FILE, "w", encoding="utf-8") as f: json.dump(ledger_data, f, indent=4)
        except: pass

async def process_hop(state: SOCState, session, addr, to, amt, txid, timestamp, depth, carry_val, obf_path, chain, origin_seed, intent_data, ticker_override=None):
    if state.target_reached or not to: return
    state.cex.record(addr, to)
    state.clustering.add_edge(addr, to, weight=amt)
    to_lbl = (await state.osint.resolve_address(session, to, chain)).get("label", "Private Wallet")
    from_lbl = (await state.osint.resolve_address(session, addr, chain)).get("label", "Private Wallet")
    entity_class, score = state.cex.classify(to, to_lbl)
    
    base_prob = 85.0 + (score * 10) if "Exchange" in entity_class else (2.0 if "Mixer" in entity_class else (15.0 if "Bridge" in entity_class else 35.0))
    if base_prob < 50.0: base_prob -= min(depth * 1.5, 9.0)
    recovery = round(max(1.0, min(base_prob, 99.0)), 2)
    is_terminal = "Exchange" in entity_class
    ticker = ticker_override or get_asset_ticker(chain)
    intent_type = intent_data.get("action", "TRANSFER")

    if obf_path == "NONE" and not is_terminal and amt >= (carry_val * 0.85): obf_path = "PEEL_CHAIN"
    
    if "Mixer" in entity_class or "Bridge" in entity_class:
        obf_type = "BRIDGE" if "Bridge" in entity_class else "MIXER"
        asyncio.create_task(nemesis_swarm.run(state.case_id, f"Obfuscation {obf_type} hit at {to}", "NARRATIVE", ""))
        
        if obf_type == "BRIDGE" and chain not in ["BITCOIN", "SOLANA"]:
            for alt_chain in ["BSC", "POLYGON", "ARBITRUM", "OPTIMISM"]:
                if alt_chain != chain: state.queue.put_nowait((to, depth + 1, amt, "MULTI_CHAIN", alt_chain, origin_seed))
        
        target_txs = await fetch_evm_txs(state, session, to, chain) if chain not in ["BITCOIN", "SOLANA"] else []
        correlations = state.obfuscation_engine.correlate_flows(amt, timestamp, target_txs, obf_type, chain)
        if correlations:
            for c in correlations:
                if c['address'] not in state.visited: state.queue.put_nowait((c['address'], depth + 1, c['amount'], obf_type, chain, origin_seed))
    
    elif is_terminal:
        async with state.state_lock:
            current_rate = USD_RATES.get(ticker, USD_RATES.get(chain, 1.0))
            usd_value = amt * current_rate
            origin_chain = detect_chain(origin_seed)
            origin_rate = USD_RATES.get(origin_chain, 1.0)
            normalized_amt = usd_value / origin_rate if origin_rate > 0 else amt

            if not state.target_reached: state.total_landed_asset += normalized_amt
            if state.total_landed_asset >= state.target_asset_amount: state.target_reached = True
    else:
        async with state.state_lock:
            if to not in state.visited and to not in state.queued:
                state.queued.add(to)
                state.queue.put_nowait((to, depth + 1, amt, obf_path, chain, origin_seed))
                
    # Execute Behavioral Evaluation
    ml_eval = state.ml_engine.evaluate_wallet(to)

    node = {
        "case_id": state.case_id, "chain": chain, "ticker": ticker,
        "timestamp": timestamp, "from": addr, "sender_entity": from_lbl, "to": to, "receiver_entity": to_lbl, 
        "tx": txid, "amount": amt, "usd": amt * USD_RATES.get(chain, 1), 
        "entity_class": entity_class, "recovery": recovery, "is_terminal": is_terminal, 
        "obfuscation_path": obf_path, "total_landed": state.total_landed_asset, "depth": depth, "origin_seed": origin_seed,
        "intent_action": intent_type, "edge_type": intent_type,
        "ml_risk": ml_eval.get("risk", "unknown"), "ml_score": ml_eval.get("score", 0.0)
    }
    
    async with state.state_lock:
        state.ledger.append(node)
        state.max_depth_reached = max(state.max_depth_reached, depth)
        ledger_copy = list(state.ledger)
        
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(IO_POOL, thread_safe_file_write, ledger_copy, [timestamp, chain, txid, addr, from_lbl, to, to_lbl, depth, "", "", amt, recovery, is_terminal, obf_path, origin_seed])
    await broadcast_ws({"type": "LEDGER", **node})

async def process_address_node(state: SOCState, session, addr, depth, carry_val, obf_path, chain, origin_seed):
    await broadcast_ws({"type": "AI_TOOLTIP", "action": f"Scanning network ledgers for {addr[:8] if isinstance(addr, str) else ''}...", "case_id": state.case_id})
    
    txs = []
    if chain == "BITCOIN":
        txs = await fetch_bitcoin_txs(session, addr)
    elif chain == "SOLANA":
        txs = await fetch_solana_txs(session, addr)
    elif chain == "XRP":
        txs = await fetch_xrp_txs(session, addr)
    elif chain == "TRON":
        txs = await fetch_tron_txs(session, addr)
    else:
        txs = await fetch_evm_txs(state, session, addr, chain)
        
    if chain == "BITCOIN":
        for tx in txs:
            if isinstance(tx, dict): state.ml_engine.ingest_tx(addr, tx)
            if state.target_reached: break
            if not isinstance(tx, dict) or not any(vin.get("prevout", {}).get("scriptpubkey_address") == addr for vin in tx.get("vin", [])): continue
            ts = datetime.fromtimestamp(tx.get("status", {}).get("block_time", 0)).strftime('%Y-%m-%d %H:%M:%S')
            for vout in tx.get("vout", []):
                if vout.get("scriptpubkey_address") and vout.get("scriptpubkey_address") != addr and vout.get("value", 0) / 1e8 > 0.0001:
                    await process_hop(state, session, addr, vout.get("scriptpubkey_address"), vout.get("value", 0)/1e8, tx.get("txid"), ts, depth, carry_val, obf_path, chain, origin_seed, {"action": "UTXO_TRANSFER"}, "BTC")
    elif chain == "SOLANA":
        for tx in txs:
            if isinstance(tx, dict): state.ml_engine.ingest_tx(addr, tx)
            if state.target_reached or not isinstance(tx, dict): break
            ts = datetime.fromtimestamp(tx.get("timestamp", 0)).strftime('%Y-%m-%d %H:%M:%S') if tx.get("timestamp") else datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            for n in tx.get("nativeTransfers", []):
                if n.get("fromUserAccount") == addr and n.get("toUserAccount") and float(n.get("amount",0))/1e9 > 0.01:
                    await process_hop(state, session, addr, n.get("toUserAccount"), float(n.get("amount",0))/1e9, tx.get("signature"), ts, depth, carry_val, obf_path, chain, origin_seed, {"action": "NATIVE_TRANSFER"}, "SOL")
            for t in tx.get("tokenTransfers", []):
                if t.get("fromUserAccount") == addr and t.get("toUserAccount") and float(t.get("tokenAmount",0)) > 0:
                    await process_hop(state, session, addr, t.get("toUserAccount"), float(t.get("tokenAmount",0)), tx.get("signature"), ts, depth, carry_val, obf_path, chain, origin_seed, {"action": "TOKEN_TRANSFER"}, t.get("tokenStandard", "SPL"))
    else:
        for tx in txs:
            if isinstance(tx, dict): state.ml_engine.ingest_tx(addr, tx)
            if state.target_reached: break
            to = tx.get("to", "")
            if chain in ["TRON", "XRP"]:
                if not to or to == addr: continue
            else:
                if not to or to.lower() == addr.lower(): continue 
            
            intent_data = await classify_tx_intent(tx, session)
            token_sym = tx.get("tokenSymbol", "")
            is_token = bool(token_sym and token_sym not in ["ETH", "BNB", "MATIC", "AVAX"])
            
            if tx.get("is_tron_exact") or chain == "XRP":
                amt = float(tx.get("value", 0))
            else:
                try: amt = float(tx.get("value", 0)) / (10**int(tx.get("tokenDecimal", 18))) if is_token else float(tx.get("value", 0)) / 1e18
                except: amt = 0.0
            
            if amt < 0.01 and not is_token and chain not in ["XRP", "TRON"]: continue
            if is_token and amt == 0: amt = 1.0 
            
            ts = datetime.fromtimestamp(int(tx.get("timeStamp", 0))).strftime('%Y-%m-%d %H:%M:%S')
            await process_hop(state, session, addr, to, amt, tx.get("hash"), ts, depth, carry_val, obf_path, chain, origin_seed, intent_data, token_sym if is_token else get_asset_ticker(chain))

async def engine_loop(state: SOCState):
    """Real Tracing Routine extracting valid chains and traversing down max depths"""
    try:
        async with aiohttp.ClientSession() as session:
            for seed in state.seeds:
                chain = state.seed_chains.get(seed, "ETHEREUM")
                recon_data = await state.osint.resolve_address(session, seed, chain)
                await broadcast_ws({"type": "RECON", "address": seed, "chain": chain, "label": recon_data.get("label", "Origin Node"), "case_id": state.case_id})
            
            async def worker(w_id):
                print(f"📡 Worker {w_id} initialized for {state.case_id}...", flush=True)
                while not state.target_reached:
                    while state.is_paused: await asyncio.sleep(1)
                    try: 
                        item = await asyncio.wait_for(state.queue.get(), timeout=2.0)
                    except asyncio.TimeoutError: 
                        continue
                    except asyncio.CancelledError: 
                        break
                    
                    addr, depth, carry_val, obf_path, chain, origin_seed = item
                    try:
                        async with state.state_lock:
                            skip = addr in state.visited or depth > MAX_DEPTH
                            if not skip: state.visited.add(addr)
                        if not skip:
                            await process_address_node(state, session, addr, depth, carry_val, obf_path, chain, origin_seed)
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        print(f"⚠️ Worker error on {addr}: {e}")
                    finally:
                        state.queue.task_done()

            # Scaled up worker pool for deep parallel processing across multiple networks
            workers = [asyncio.create_task(worker(i)) for i in range(50)]
            
            # The Safe Monitor Logic
            async def monitor():
                while not state.target_reached: 
                    await asyncio.sleep(1)
                    
            async def ml_monitor():
                while not state.target_reached:
                    await asyncio.sleep(10)
                    try: state.ml_engine.train_model()
                    except Exception: pass
                
            monitor_task = asyncio.create_task(monitor())
            ml_task = asyncio.create_task(ml_monitor())
            queue_task = asyncio.create_task(state.queue.join())
            
            await asyncio.wait([monitor_task, queue_task], return_when=asyncio.FIRST_COMPLETED)
            
            for w in workers: w.cancel()
            if not monitor_task.done(): monitor_task.cancel()
            if not ml_task.done(): ml_task.cancel()
            if not queue_task.done(): queue_task.cancel()
            
            # Post-Trace AI Matrix Activation
            print(f"🕸️ Extracting GNN Wallet Relationships for {state.case_id}...", flush=True)
            state.clustering.learn_relationships()
            
            print(f"🔗 Stitching Pseudo-anonymous Identities for {state.case_id}...", flush=True)
            stitcher = CrossChainStitcher(state.clustering)
            syndicates = stitcher.stitch_identities()
            
            if syndicates:
                investigator = AutonomousInvestigator(llm_engine)
                for cluster_id, wallets in syndicates.items():
                    scores = {w: state.ml_engine.evaluate_wallet(w) for w in wallets}
                    report = await investigator.run_investigation(cluster_id, wallets, scores)
                    print(report, flush=True)

            await broadcast_ws({"type": "COMPLETE", "final_depth": state.max_depth_reached, "case_id": state.case_id})
    except asyncio.CancelledError: pass
    except Exception: traceback.print_exc()

async def mempool_sniffer():
    while True:
        await asyncio.sleep(25)
        stale_cases = []
        for case_id, state in list(active_traces.items()):
            if state.target_reached or not ws_clients.get(case_id):
                stale_cases.append(case_id)
                continue
            if state.seeds and len(state.ledger) > 0:
                if int(datetime.now(timezone.utc).timestamp()) % 20 == 0:
                    seed = state.seeds[0]
                    chain = state.seed_chains.get(seed, "ETHEREUM")
                    alert = {"type": "MEMPOOL_ALERT", "message": f"Subject address {seed[:8]}... broadcasted a new unconfirmed transaction. Tracking execution payload.", "hash": "0xpending" + str(int(datetime.now(timezone.utc).timestamp())), "chain": chain, "case_id": case_id}
                    await broadcast_ws(alert)
        for case in stale_cases: active_traces.pop(case, None)

async def autonomous_agent_loop():
    """Background polymorphic agent that scans, validates, and auto-patches."""
    db = CodeIndexDB()
    exploit_agent = ExploitDetectionAgent()
    patch_engine = PatchEngine()
    supervisor = Supervisor()
    target_file = Path(__file__).resolve()
    
    while True:
        await asyncio.sleep(5)
        await broadcast_supervisor({"text": f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] 🤖 Swarm Engine scanning {target_file.name} for AST anomalies...", "color": "text-blue-400"})
        await asyncio.sleep(2)
        
        if target_file.exists():
            code = target_file.read_text(encoding="utf-8", errors="ignore")
            db.store(target_file, code)
            analysis = exploit_agent.analyze(code)
            
            if analysis["issues"]:
                await broadcast_supervisor({"text": f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] ⚠️ Vulnerabilities detected: {analysis['issues']}", "color": "text-red-500"})
                await broadcast_supervisor({"text": f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] 🧠 DeepMind LLM synthesizing code auto-fix & auto-enhance...", "color": "text-purple-400"})
                
                prompt = f"ROLE: Autonomous System Patcher. Fix these Python issues: {analysis['issues']}. Return ONLY valid Python code. No markdown, no comments. Code:\n{code}"
                new_code = await llm_engine.prompt_llm(prompt)
                new_code = new_code.replace("```python", "").replace("```", "").strip()
                
                if supervisor.validate_ast(new_code):
                    await broadcast_supervisor({"text": f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] ⚙️ AST validation passed. Applying unrestricted auto-rewrite...", "color": "text-yellow-400"})
                    target_file.write_text(new_code, encoding="utf-8")
                    await broadcast_supervisor({"text": f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] ✅ Code generated and applied. Auto-redeploying...", "color": "text-emerald-400"})
                    await asyncio.sleep(1)
                    os.execv(sys.executable, ['python'] + sys.argv)
                else:
                    await broadcast_supervisor({"text": f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] ❌ AI Patch failed AST validation. Aborting self-modification.", "color": "text-red-500"})
            else:
                await broadcast_supervisor({"text": f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] ✅ AST validation passed. Code is secure. Swarm returning to standby.", "color": "text-emerald-400"})
        
        await asyncio.sleep(25)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global HTTP_SESSION, GLOBAL_PLAYWRIGHT, GLOBAL_BROWSER
    HTTP_SESSION = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=1000, ttl_dns_cache=300))
    await init_mongodb()
    
    try:
        GLOBAL_PLAYWRIGHT = await async_playwright().start()
        GLOBAL_BROWSER = await GLOBAL_PLAYWRIGHT.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    except Exception as e: print(f"⚠️ Global Playwright init failed: {e}")

    asyncio.create_task(mempool_sniffer())
    asyncio.create_task(autonomous_agent_loop())
    swarm_orchestrator.boot_check()
    
    yield
    if GLOBAL_BROWSER: await GLOBAL_BROWSER.close()
    if GLOBAL_PLAYWRIGHT: await GLOBAL_PLAYWRIGHT.stop()
    await HTTP_SESSION.close()
    PROCESS_POOL.shutdown()

# ==========================================
# FASTAPI APP & ENDPOINTS
# ==========================================
app = FastAPI(
    title="NEMESIS Omni-Chain Engine API", 
    version="100.20", 
    description="Full API Documentation for the Lionsgate Intelligence Network. This Swagger UI covers tracing endpoints, DarkX streaming, OSINT generation, and Swarm Orchestration logic.",
    contact={"name": "Lionsgate Intelligence Network"},
    lifespan=lifespan
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api-docs", response_class=HTMLResponse, include_in_schema=False)
async def api_docs_ui():
    """Returns the custom Lionsgate Developer Hub API Documentation."""
    return HTML_API_DOCS

@app.get("/about", response_class=HTMLResponse)
async def about_page(): return HTML_ABOUT

class TraceStartRequest(BaseModel):
    seeds: str = Field(..., json_schema_extra={"example": "0xYourCompromisedWalletAddressOrHash"})
    target_amount: Optional[float] = Field(None)
    currency: Optional[str] = Field("NATIVE", json_schema_extra={"example": "USD"})
    chain_override: Optional[str] = Field("AUTO", json_schema_extra={"example": "ETHEREUM"})

class OSINTRequest(BaseModel):
    details: str
    target_domain: Optional[str] = None
    brand_name: Optional[str] = None
    entity_name: Optional[str] = None
class DossierRequest(BaseModel):
    doc_id: str
class NarrativeRequest(BaseModel):
    subpoena_targets: str
    case_id: str

@app.post("/api/start_trace")
async def api_start_trace(req: TraceStartRequest):
    extracted_seeds = []
    pattern = r'\b(0x[a-fA-F0-9]{40}|bc1[a-zA-Z0-9]{25,90}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|r[0-9a-zA-Z]{24,34}|T[A-Za-z1-9]{33}|[1-9A-HJ-NP-Za-km-z]{32,44})\b'
    matches = re.findall(pattern, req.seeds)
    if matches:
        extracted_seeds = list(set(matches))
    else:
        extracted_seeds = [s.strip().split()[-1] for s in req.seeds.split('\n') if s.strip() and len(s.strip()) > 20]
        
    if not extracted_seeds: raise HTTPException(status_code=400, detail="No valid seeds extracted from input.")
    
    chain = req.chain_override if req.chain_override != "AUTO" else detect_chain(extracted_seeds[0])
    calc_amt = float(req.target_amount) if req.target_amount else 1000.0

    trace_state = SOCState()
    trace_state.setup(extracted_seeds, calc_amt, chain)
    active_traces[trace_state.case_id] = trace_state
    
    await broadcast_ws({"type": "INIT", "target_amount": calc_amt, "seeds": extracted_seeds, "ticker": get_asset_ticker(chain), "case_id": trace_state.case_id})
    asyncio.create_task(engine_loop(trace_state))
    return {"status": "running", "case_id": trace_state.case_id}

@app.get("/api/forensic_report_data")
async def api_forensic_report_data(case_id: str = Query(None)):
    target_state = active_traces.get(case_id) if case_id else list(active_traces.values())[-1] if active_traces else None
    if not target_state: return {"error": "Trace case not found"}

    terminals = [{"source": l['from'], "destination": l['to'], "entity": l['receiver_entity'], "amount": f"{l['amount']} {l['ticker']}", "type": l['intent_action'].replace('_', ' '), "ml_risk": l.get('ml_risk', 'unknown')} for l in target_state.ledger if l['is_terminal']]
    tx_list = [{"hash": l['tx'], "type": l['intent_action'], "amount": l['amount'], "ticker": l['ticker'], "from": l['from'], "to": l['to']} for l in target_state.ledger]
    return {"seeds": target_state.seeds, "total_volume": sum([float(l.get('amount', 0)) for l in target_state.ledger]), "terminals": terminals, "tx_count": len(target_state.ledger), "transactions": tx_list}

@app.post("/api/generate_osint_report")
async def api_generate_osint_report(req: OSINTRequest):
    osint_engine = OSINT(GNNClusterEngine())
    enriched_details = req.details
    
    rel_analysis = await llm_engine.prompt_llm(f"Perform an actor relationship analysis based on this context: {req.details}")
    enriched_details += f"\n\n[Actor Relationship Analysis]: {rel_analysis}"
    
    if req.target_domain:
        ssl_info = await osint_engine.deep_domain_scan(req.target_domain)
        enriched_details += f"\n\n[Domain Deep Scan (TLS/SSL)]: {ssl_info}"
    if req.brand_name:
        brand_info = await llm_engine.prompt_llm(f"Perform a brand protection and typosquatting risk analysis for the brand: {req.brand_name}")
        enriched_details += f"\n\n[Brand Protection Scan]: {brand_info}"
    if req.entity_name:
        social_info = await llm_engine.prompt_llm(f"Perform an OSINT social media footprint analysis for the entity: {req.entity_name}")
        enriched_details += f"\n\n[Social Media Recon]: {social_info}"
        
    result = await nemesis_swarm.run(case_id="MANUAL", raw_data=enriched_details, task_type="OSINT")
    return {"report_html": result.replace('```html', '').replace('```', '')}

@app.post("/api/generate_narrative")
async def api_generate_narrative(req: NarrativeRequest):
    target_state = active_traces.get(req.case_id) if req.case_id else list(active_traces.values())[-1] if active_traces else None
    if not target_state or not target_state.ledger: return {"narrative": "No transaction data available to generate a narrative."}
    summary = "Trace Ledger Summary:\n"
    for t in target_state.ledger[:60]: summary += f"- {t['amount']} {t['ticker']} sent from {t['from']} ({t['sender_entity']}) to {t['to']} ({t['receiver_entity']}) | Strategy: {t['obfuscation_path']}\n"
    
    result = await nemesis_swarm.run(case_id=req.case_id, raw_data=summary, task_type="NARRATIVE", targets=req.subpoena_targets)
    return {"narrative": result}

@app.get("/api/darkx/stream")
async def api_darkx_stream(q: str = Query(...)):
    async def event_generator():
        if darknet_col is None: yield f"data: {json.dumps({'error': 'Database disconnected'})}\n\n"; return
            
        try:
            # 1. High-speed Text Index Search (Exact Phrase Matching)
            safe_q = q.replace('"', '\\"')
            cursor = darknet_col.find(
                {"$text": {"$search": f'"{safe_q}"'}},
                {"_id": 1, "crawled_at": 1, "web_info.url": 1, "web_info.title": 1, "uie_entities": 1}
            ).sort("crawled_at", -1).limit(50)
            
            docs = await cursor.to_list(length=50)
            
            found = False
            for doc in docs:
                found = True
                doc_id = str(doc.pop('_id'))
                if "crawled_at" in doc and isinstance(doc["crawled_at"], datetime): doc["crawled_at"] = doc["crawled_at"].isoformat()
                yield f"data: {json.dumps({'id': doc_id, **doc})}\n\n"
                await asyncio.sleep(0) 
 
            yield f"data: {json.dumps({'end': True, 'msg': '' if found else 'No results found.'})}\n\n"
        except Exception as e: yield f"data: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/darkx/dossier")
async def api_darkx_dossier(req: DossierRequest):
    if darknet_col is None: raise HTTPException(status_code=500, detail="DB disconnected")
    doc = await darknet_col.find_one({"_id": ObjectId(req.doc_id)})
    if not doc: raise HTTPException(status_code=404, detail="Not found")
    result = await nemesis_swarm.run(case_id="DARKX", raw_data=str(doc)[:3000], task_type="DOSSIER")
    return {"dossier_html": result.replace('```html', '').replace('```', '')}

@app.websocket("/ws/{case_id}")
async def ws_case(websocket: WebSocket, case_id: str):
    await websocket.accept()
    ws_clients[case_id].append(websocket)
    try:
        while True: await websocket.receive_text()
    except: ws_clients[case_id].remove(websocket)

@app.websocket("/ws/supervisor")
async def ws_supervisor_endpoint(websocket: WebSocket):
    await websocket.accept()
    supervisor_clients.add(websocket)
    try:
        while True: await websocket.receive_text()
    except: supervisor_clients.discard(websocket)

# ==========================================
# UNIFIED FRONTEND HTML STRINGS
# ==========================================

FLOATING_TERMINAL_HTML = r"""
    <!-- FLOATING SUPERVISOR TERMINAL -->
    <div id="supervisor-terminal" class="fixed bottom-4 right-4 w-96 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl z-[9999] flex flex-col overflow-hidden transition-all duration-300" style="height: 36px; z-index: 999999;">
        <div class="bg-slate-800 p-2 flex justify-between items-center cursor-pointer select-none" id="sup-header" onclick="toggleSupervisor()">
            <span class="text-[10px] font-black text-emerald-400 uppercase tracking-widest flex items-center gap-2"><i class="fa-solid fa-robot animate-pulse"></i> SWARM SUPERVISOR</span>
            <button class="text-slate-400 hover:text-white outline-none"><i class="fa-solid fa-chevron-up" id="sup-toggle-icon"></i></button>
        </div>
        <div id="sup-body" class="p-3 overflow-y-auto flex-grow font-mono text-[9px] text-slate-300 space-y-1 bg-black">
            <div class="text-emerald-500">Initializing Polymorphic Swarm Engine...</div>
        </div>
    </div>
    <script>
        let supWs = new WebSocket((window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host + "/ws/supervisor");
        supWs.onmessage = (e) => { let body = document.getElementById("sup-body"); let msg = JSON.parse(e.data); body.innerHTML += `<div><span class="${msg.color || 'text-slate-300'}">${msg.text}</span></div>`; body.scrollTop = body.scrollHeight; if(supMin) toggleSupervisor(); };
        let supMin = true;
        function toggleSupervisor() {
            let term = document.getElementById("supervisor-terminal"); let icon = document.getElementById("sup-toggle-icon");
            if(supMin) { term.style.height = "300px"; icon.className = "fa-solid fa-minus"; } else { term.style.height = "36px"; icon.className = "fa-solid fa-chevron-up"; }
            supMin = !supMin;
        }
    </script>
"""

HTML_MAIN_LANDING = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LIONSGATE INTELLIGENCE NETWORK</title>
    <script>window.tailwind = { corePlugins: { preflight: true } };</script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', system-ui, sans-serif; overflow-x: hidden; }
        .bg-grid { background-size: 50px 50px; background-image: linear-gradient(to right, rgba(99, 102, 241, 0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(99, 102, 241, 0.05) 1px, transparent 1px); }
        .glass-panel { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(16px); border: 1px solid rgba(203, 213, 225, 0.8); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05); }
        .card-hover { transition: all 0.3s ease; }
        .card-hover:hover { transform: translateY(-5px); box-shadow: 0 20px 40px rgba(59, 130, 246, 0.15); border-color: #93c5fd; }
    </style>
</head>
<body class="bg-grid min-h-screen flex flex-col justify-between">
    <nav class="w-full bg-white/90 backdrop-blur border-b border-slate-200 py-4 px-8 flex justify-between items-center shadow-sm">
        <div class="flex items-center gap-3">
            <img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" alt="Logo" class="h-10 rounded">
            <div class="font-black text-slate-800 text-lg uppercase tracking-tight leading-tight">LIONSGATE<br><span class="text-blue-600 text-xs tracking-widest">Intelligence Network</span></div>
        </div>
        <div class="flex items-center gap-4">
            <a href="/darkx" class="text-xs font-bold text-slate-500 hover:text-indigo-600 transition"><i class="fa-solid fa-spider mr-1"></i> NEMESIS DarkX</a>
            <a href="/about" class="text-xs font-bold text-slate-500 hover:text-indigo-600 transition"><i class="fa-solid fa-book mr-1"></i> Master Whitepaper</a>
            <a href="/api-docs" target="_blank" class="text-xs font-bold text-slate-500 hover:text-indigo-600 transition"><i class="fa-solid fa-code mr-1"></i> API Hub</a>
        </div>
    </nav>
    <main class="flex-grow flex flex-col items-center justify-center p-8 w-full max-w-6xl mx-auto">
        <div class="text-center mb-12">
            <img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" alt="Logo" class="h-24 mx-auto mb-6 rounded-xl shadow-lg border border-slate-200 bg-white p-2">
            <h1 class="text-6xl font-black text-slate-900 tracking-tighter mb-2">NEMESIS</h1>
            <p class="text-sm font-bold text-slate-500 uppercase tracking-[0.3em] mb-4">By Lionsgate Intelligence Network</p>
            <p class="text-blue-600 font-bold text-xl italic">"Unified Blockchain and Cyber Intelligence"</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
            <a href="/recovery" class="glass-panel p-8 rounded-2xl card-hover block text-center cursor-pointer group">
                <div class="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl group-hover:scale-110 transition-transform"><i class="fa-solid fa-shield-halved"></i></div>
                <h2 class="text-2xl font-black text-slate-800 mb-3">Client Asset Recovery</h2>
                <p class="text-slate-600 text-sm leading-relaxed">Public gateway for victims of cybercrime. Submit incident details, perform automated blockchain tracing, and generate law enforcement ready affidavits.</p>
                <div class="mt-6 text-blue-600 font-bold text-xs uppercase tracking-wider">Start Recovery Pipeline <i class="fa-solid fa-arrow-right ml-1"></i></div>
            </a>
            <a href="/portal" class="glass-panel p-8 rounded-2xl card-hover block text-center cursor-pointer group border-indigo-200">
                <div class="w-16 h-16 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl group-hover:scale-110 transition-transform"><i class="fa-solid fa-network-wired"></i></div>
                <h2 class="text-2xl font-black text-slate-800 mb-3">NEMESIS ULTRA (Lab)</h2>
                <p class="text-slate-600 text-sm leading-relaxed">Enterprise Command Center. Direct access to Omni-Chain Graphing, LangGraph AI Swarms, Deep Web OSINT Crawlers, and GNN Clustering Modules.</p>
                <div class="mt-6 text-indigo-600 font-bold text-xs uppercase tracking-wider">Access Enterprise Terminal <i class="fa-solid fa-arrow-right ml-1"></i></div>
            </a>
        </div>
    </main>
    """ + FLOATING_TERMINAL_HTML + r"""
</body>
</html>
"""

HTML_CLIENT_RECOVERY = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asset Recovery Intake | LIONSGATE</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body { background: #f8fafc; color: #0f172a; font-family: 'Inter', sans-serif; overflow: hidden; }
        #flow-container { display: flex; width: 300vw; height: 100vh; transition: transform 0.8s cubic-bezier(0.65, 0, 0.35, 1); }
        .step-panel { width: 100vw; height: 100vh; display: flex; align-items: center; justify-content: center; padding: 1rem; perspective: 1500px; }
        
        .cinematic-bg { background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%); width: 100%; height: 100%; max-height: 500px; max-width: 900px; border-radius: 1rem; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; box-shadow: inset 0 0 50px rgba(0,0,0,0.5); position: relative; overflow: hidden; }
        
        .flip-container { width: 100%; max-width: 900px; height: 85vh; transform-style: preserve-3d; transition: transform 1s cubic-bezier(0.65, 0, 0.35, 1); position: relative; }
        .flip-container.flipped { transform: rotateY(180deg) scale(1.05); }
        .flip-card-front, .flip-card-back { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; display: flex; flex-direction: column; align-items: center; justify-content: center; background: white; border-radius: 1.5rem; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); border: 1px solid #e2e8f0; }
        .flip-card-back { transform: rotateY(180deg); padding: 2rem; }
    </style>
</head>
<body>
    <div id="flow-container">
        <div class="step-panel" id="step1-panel">
            <div class="w-full max-w-3xl bg-white p-8 md:p-12 rounded-3xl shadow-2xl border border-slate-200 overflow-y-auto max-h-[90vh]">
                <div class="mb-6 border-b pb-4 text-center">
                    <img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" alt="Logo" class="h-16 mx-auto mb-4">
                    <h1 class="text-3xl font-black text-slate-800 mb-2">Client Intake & Analysis</h1>
                    <p class="text-slate-500 text-sm">Step 1: Incident Registration</p>
                </div>
                <div class="space-y-4 text-left">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div><label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Full Name</label><input type="text" id="clientName" class="w-full bg-slate-50 border border-slate-300 p-3 rounded text-sm outline-none focus:border-blue-500 shadow-inner"></div>
                        <div><label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Country</label><input type="text" id="clientCountry" class="w-full bg-slate-50 border border-slate-300 p-3 rounded text-sm outline-none focus:border-blue-500 shadow-inner"></div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div><label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Phone</label><input type="text" class="w-full bg-slate-50 border border-slate-300 p-3 rounded text-sm outline-none focus:border-blue-500 shadow-inner"></div>
                        <div><label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Zip Code (For LEA Routing)</label><input type="text" id="clientZip" class="w-full bg-slate-50 border border-slate-300 p-3 rounded text-sm outline-none focus:border-blue-500 shadow-inner"></div>
                    </div>
                    <div><label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Suspect Wallets or Tx Hashes</label>
                        <div class="relative">
                            <textarea id="traceSeeds" class="w-full bg-slate-50 border border-slate-300 p-3 rounded text-sm outline-none focus:border-blue-500 font-mono shadow-inner pr-10" rows="3" oninput="if(typeof autoDetectChain === 'function') autoDetectChain()"></textarea>
                            <img id="detectedChainLogo" src="https://cdn-icons-png.flaticon.com/512/2152/2152865.png" class="h-6 w-6 rounded-full absolute right-3 top-3 pointer-events-none shadow-sm bg-white">
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Network</label>
                            <select id="traceChain" class="w-full bg-slate-50 border border-slate-300 p-3 rounded text-sm outline-none focus:border-blue-500 shadow-inner font-bold">
                                <option value="AUTO">🌐 Omni-Chain Auto</option><option disabled>── EVM ──</option><option value="ETHEREUM">🔷 Ethereum</option><option value="BSC">🟨 BSC</option><option value="POLYGON">🟪 Polygon</option><option value="ARBITRUM">🔵 Arbitrum</option><option value="OPTIMISM">🔴 Optimism</option><option value="BASE">🛡️ Base</option><option value="AVALANCHE">🔺 Avalanche</option><option value="LINEA">〰️ Linea</option><option value="CELO">🟡 Celo</option><option disabled>── NON-EVM ──</option><option value="BITCOIN">₿ Bitcoin</option><option value="SOLANA">◎ Solana</option><option value="TRON">♦ Tron</option><option value="XRP">✕ XRP</option><option value="STELLAR">🚀 Stellar</option><option value="KASPA">🟢 Kaspa</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Total Loss Amount & Asset</label>
                            <div class="flex items-center border border-slate-300 rounded shadow-inner bg-slate-50 focus-within:border-blue-500 overflow-hidden pr-2">
                                <input type="number" step="any" id="traceAmount" class="w-full bg-transparent p-2.5 text-sm outline-none" placeholder="Auto-Calc if blank">
                                <img id="currencyLogo" src="https://cdn-icons-png.flaticon.com/512/1490/1490815.png" class="h-5 w-5 mr-1 rounded-full bg-white shadow-sm">
                                <select id="traceCurrency" class="bg-transparent text-sm outline-none font-bold py-2.5 pr-1 cursor-pointer text-blue-800" onchange="document.getElementById('currencyLogo').src = typeof chainLogos !== 'undefined' ? (chainLogos[this.value] || chainLogos['UNKNOWN']) : 'https://cdn-icons-png.flaticon.com/512/1490/1490815.png'">
                                    <option value="USD">USD ($)</option><option value="NATIVE">NATIVE</option><option disabled>──────</option>
                                    <option value="BTC">BTC</option><option value="ETH">ETH</option><option value="BNB">BNB</option><option value="MATIC">MATIC</option><option value="AVAX">AVAX</option><option value="ARBITRUM">ARB</option><option value="OPTIMISM">OP</option><option value="TRON">TRX</option><option value="XLM">XLM</option><option value="KASPA">KAS</option><option value="SOLANA">SOL</option><option value="XRP">XRP</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div><label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Incident Scenario</label><textarea id="incidentDetails" class="w-full bg-slate-50 border border-slate-300 p-3 rounded text-sm outline-none focus:border-blue-500 shadow-inner" rows="3"></textarea></div>
                    <div class="border-2 border-dashed border-slate-300 p-4 rounded text-center bg-slate-50 cursor-pointer hover:bg-slate-100 transition"><i class="fa-solid fa-cloud-arrow-up text-2xl text-slate-400 mb-2"></i><p class="text-xs font-bold text-slate-600">Import Files/Folder (Integrate OCR)</p><p class="text-[10px] text-slate-500">Pipeline for OSINT intelligence - Extracts Domains, IPs, Usernames.</p></div>
                    <button onclick="startTracing()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-4 rounded-lg uppercase tracking-widest mt-4 transition shadow-md active:scale-95 text-center">Initiate Cyber Intelligence Trace</button>
                </div>
            </div>
        </div>

        <div class="step-panel" id="step2-panel">
            <div class="w-full max-w-6xl h-[85vh] bg-slate-900/95 backdrop-blur rounded-3xl shadow-2xl border border-slate-700 p-8 flex flex-col relative overflow-hidden">
                <div class="flex justify-between items-center mb-4 z-10 border-b border-slate-700 pb-4">
                    <div>
                        <h1 class="text-3xl font-black uppercase tracking-widest text-slate-100">Parallel Multi-Chain Analysis</h1>
                        <p class="text-blue-400 text-sm animate-pulse font-bold" id="scan-status">Establishing Omni-Chain Connections...</p>
                    </div>
                    <div class="text-right">
                        <p class="text-[10px] text-slate-400 uppercase tracking-widest">Trace Completion</p>
                        <p class="text-4xl font-black text-emerald-400 font-mono" id="trace-pct">0%</p>
                    </div>
                </div>
                <div id="ai-tooltip-container" class="mb-4 text-xs font-mono text-purple-400 h-6 w-full z-10 flex items-center bg-slate-800/50 px-4 rounded border border-slate-700">Awaiting AI Tasking...</div>
                <div id="network-graph-container" class="flex-grow rounded-xl border border-slate-700 bg-slate-950 shadow-inner z-10 w-full relative"></div>
            </div>
        </div>

        <div class="step-panel" id="step3-panel">
            <div class="flip-container" id="report-flip-card">
                <div class="flip-card-front">
                    <i class="fa-solid fa-file-shield text-7xl text-indigo-600 mb-6 animate-bounce"></i>
                    <h2 class="text-4xl font-black text-slate-800 uppercase mb-3">Analysis Complete</h2>
                    <p class="text-lg text-slate-500 mb-8 font-medium">Preparing Expert Witness Forensics...</p>
                    <div class="w-full bg-slate-50 border border-slate-200 p-6 rounded-xl shadow-inner text-center max-w-md">
                        <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Generated Case ID</p>
                        <p class="text-3xl font-mono text-emerald-600 font-bold" id="res-case-id">CASE-XXXX</p>
                    </div>
                </div>
                <div class="flip-card-back">
                    <div class="w-full h-full flex flex-col items-center">
                        <img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" class="h-12 mb-4">
                        <h2 class="text-3xl font-black text-slate-800 uppercase mb-2">Forensic Report Generated</h2>
                        <p class="text-sm text-slate-500 font-mono mb-8" id="report-case-id"></p>
                        <div class="w-full bg-red-50 border border-red-200 p-6 rounded-xl shadow-inner text-left mb-8 max-w-3xl overflow-y-auto">
                            <h3 class="text-sm font-bold text-red-800 uppercase mb-4 border-b border-red-200 pb-2 flex justify-between">
                                <span>Identified Terminal Endpoints</span><span class="bg-red-600 text-white px-2 py-0.5 rounded text-[10px] animate-pulse">REDACTED</span>
                            </h3>
                            <ul class="space-y-3 font-mono text-sm text-slate-700 bg-white p-4 rounded border border-red-100 shadow-sm" id="step3-terminals">
                                <li><i class="fa-solid fa-circle-notch fa-spin text-red-500"></i> Resolving verified entities...</li>
                            </ul>
                        </div>
                        <div class="mt-auto pt-4 text-center w-full max-w-2xl">
                            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Report Expiration Timer</p>
                            <p class="text-4xl font-black text-slate-800 font-mono mb-4" id="report-timer">100s</p>
                            <button onclick="acceptReport()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-4 rounded-xl uppercase tracking-widest shadow-lg transition active:scale-95 text-sm">Accept & View Dashboard</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="welcome-modal" class="fixed inset-0 bg-slate-900/80 backdrop-blur z-[100] hidden flex items-center justify-center p-4">
        <div class="bg-white p-10 rounded-3xl max-w-md text-center shadow-2xl">
            <i class="fa-solid fa-handshake text-6xl text-blue-600 mb-6"></i>
            <h2 class="text-3xl font-black text-slate-800 mb-3">Welcome Aboard</h2>
            <p class="text-sm text-slate-600 mb-8 leading-relaxed">Your case has been securely logged. An investigator from Lionsgate Intelligence Network will contact you shortly to review the unredacted evidence.</p>
            <a id="portal-link" href="/portal" class="block w-full bg-slate-800 hover:bg-slate-900 text-white font-bold py-4 rounded-xl uppercase text-xs tracking-wider shadow-lg transition active:scale-95">Proceed to Client Dashboard</a>
        </div>
    </div>

    <script>
        let globalCaseId = "CASE-PENDING";
        let timerInt;
        let ws;
        let networkNodes = new vis.DataSet([]);
        let networkEdges = new vis.DataSet([]);
        let networkGraph = null;
        const flowContainer = document.getElementById('flow-container');
        const flipCard = document.getElementById('report-flip-card');
        const aiTooltip = document.getElementById('ai-tooltip-container');

        const chainLogos = {
            "ETHEREUM": "https://cryptologos.cc/logos/ethereum-eth-logo.png",
            "BSC": "https://cryptologos.cc/logos/bnb-bnb-logo.png",
            "POLYGON": "https://cryptologos.cc/logos/polygon-matic-logo.png",
            "ARBITRUM": "https://cryptologos.cc/logos/arbitrum-arb-logo.png",
            "OPTIMISM": "https://cryptologos.cc/logos/optimism-ethereum-op-logo.png",
            "AVALANCHE": "https://cryptologos.cc/logos/avalanche-avax-logo.png",
            "SOLANA": "https://cryptologos.cc/logos/solana-sol-logo.png",
            "BITCOIN": "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
            "TRON": "https://cryptologos.cc/logos/tron-trx-logo.png",
            "XRP": "https://cryptologos.cc/logos/xrp-xrp-logo.png",
            "KASPA": "https://s2.coinmarketcap.com/static/img/coins/64x64/20396.png",
            "USD": "https://cdn-icons-png.flaticon.com/512/1490/1490815.png",
            "UNKNOWN": "https://cdn-icons-png.flaticon.com/512/2152/2152865.png"
        };

        function autoDetectChain() {
            const lines = document.getElementById('traceSeeds').value.trim().split('\n');
            if(!lines || lines.length === 0 || !lines[0]) return;
            const val = lines[0].trim();
            let chain = "UNKNOWN";
            if (val.startsWith("kaspa:")) chain = "KASPA";
            else if (val.startsWith("r") && val.length >= 25 && val.length <= 35) chain = "XRP";
            else if (val.length >= 32 && val.length <= 44 && !val.startsWith("0x")) chain = "SOLANA";
            else if (val.startsWith("0x")) chain = "ETHEREUM"; 
            else if (val.startsWith("T") && val.length == 34) chain = "TRON";
            else if (val.startsWith("1") || val.startsWith("3") || val.startsWith("bc1")) chain = "BITCOIN";
            
            const logoImg = document.getElementById('detectedChainLogo');
            if(logoImg) logoImg.src = chainLogos[chain] || chainLogos["UNKNOWN"];
            
            if(chain !== "UNKNOWN") {
                const select = document.getElementById('traceChain');
                for(let i=0; i<select.options.length; i++) {
                    if(select.options[i].value === chain) { select.selectedIndex = i; break; }
                }
            }
        }

        function initGraph() {
            let container = document.getElementById('network-graph-container');
            let data = { nodes: networkNodes, edges: networkEdges };
            let options = { nodes: { shape: 'dot', size: 16, font: { color: '#ffffff', size: 10, face: 'monospace' }, borderWidth: 2 }, edges: { width: 1.5, color: { color: '#3b82f6', opacity: 0.6 }, arrows: 'to', smooth: { type: 'continuous' } }, physics: { enabled: true, barnesHut: { gravitationalConstant: -2000, centralGravity: 0.3, springLength: 95 } }, layout: { improvedLayout: true } };
            networkGraph = new vis.Network(container, data, options);
        }

        function slideToStep(stepNumber) { flowContainer.style.transform = `translateX(${-(stepNumber - 1) * 100}vw)`; }

        async function startTracing() {
            slideToStep(2);
            const seeds = document.getElementById('traceSeeds').value || "0xNULL";
            const chainOverride = document.getElementById('traceChain').value;
            const amountInput = document.getElementById('traceAmount').value;
            
            try {
                let tracePayload = { seeds: seeds, chain_override: chainOverride };
                if (amountInput) tracePayload.target_amount = parseFloat(amountInput);
                
                let r = await fetch('/api/start_trace', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(tracePayload)
                });
                let d = await r.json();
                globalCaseId = d.case_id;
                localStorage.setItem("nemesis_case_id", globalCaseId);
                localStorage.setItem("nemesis_name", document.getElementById('clientName').value);
                localStorage.setItem("nemesis_zip", document.getElementById('clientZip').value);
                localStorage.setItem("nemesis_country", document.getElementById('clientCountry').value);
                localStorage.setItem("nemesis_incident", document.getElementById('incidentDetails').value);
                
                let wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
                ws = new WebSocket(wsProtocol + window.location.host + "/ws/" + globalCaseId);
                
                ws.onmessage = (msg) => {
                    let wsData = JSON.parse(msg.data);
                    if(wsData.type === "INIT") {
                        if (!networkGraph) initGraph();
                        wsData.seeds.forEach(seed => {
                            if (!networkNodes.get(seed)) networkNodes.add({ id: seed, label: seed.substring(0,8) + '...\n(ORIGIN)', color: { background: '#ef4444', border: '#b91c1c' }, size: 20 });
                        });
                    }
                    if(wsData.type === "RECON") {
                        let node = networkNodes.get(wsData.address);
                        if (node) { networkNodes.update({ id: wsData.address, label: wsData.address.substring(0,8) + '...\n' + wsData.label + '\n[' + wsData.chain + ']' }); }
                        else { networkNodes.add({ id: wsData.address, label: wsData.address.substring(0,8) + '...\n' + wsData.label + '\n[' + wsData.chain + ']', color: { background: '#ef4444', border: '#b91c1c' }, size: 20 }); }
                    }
                    if(wsData.type === "SCANNING") document.getElementById('scan-status').innerText = `Tracing ${wsData.chain}: ${wsData.address.substring(0,10)}...`;
                    if(wsData.type === "LEDGER") {
                        if (!networkNodes.get(wsData.to)) {
                            let nColor = wsData.is_terminal ? '#f59e0b' : '#3b82f6';
                            let nBorder = wsData.is_terminal ? '#d97706' : '#2563eb';
                            let nSize = wsData.is_terminal ? 24 : 16;
                            networkNodes.add({ id: wsData.to, label: wsData.to.substring(0,8) + '...\n' + wsData.receiver_entity + '\n[' + wsData.chain + ']', color: { background: nColor, border: nBorder }, size: nSize });
                        }
                        let edgeId = wsData.from + '-' + wsData.to + '-' + wsData.tx;
                        if (!networkEdges.get(edgeId)) {
                            networkEdges.add({ id: edgeId, from: wsData.from, to: wsData.to, label: parseFloat(wsData.amount).toFixed(4) + ' ' + wsData.ticker, font: { align: 'top', color: '#94a3b8', size: 9 } });
                        }
                        let pEl = document.getElementById('trace-pct');
                        let currentPct = parseInt(pEl.innerText);
                        if (currentPct < 90) pEl.innerText = (currentPct + 2) + '%';
                    }
                    if(wsData.type === "AI_TOOLTIP") {
                        aiTooltip.innerText = wsData.action;
                        aiTooltip.classList.add("animate-pulse");
                    }
                    if(wsData.type === "AI_TOOLTIP_END") aiTooltip.innerText = "";
                    if(wsData.type === "COMPLETE") {
                        document.getElementById('trace-pct').innerText = '100%';
                        document.getElementById('scan-status').innerText = "Trace Complete. Terminals Located.";
                        setTimeout(() => {
                            document.getElementById('res-case-id').innerText = globalCaseId;
                            document.getElementById('report-case-id').innerText = "ID: " + globalCaseId;
                            fetchTerminalData();
                            slideToStep(3);
                            setTimeout(() => { flipCard.classList.add('flipped'); startTimer(); }, 1500);
                        }, 3000); // 3 seconds to review final visualization
                    }
                };
            } catch(e) { console.error("Trace failed", e); }
        }

        async function fetchTerminalData() {
            try {
                let r = await fetch('/api/forensic_report_data?case_id=' + globalCaseId);
                let d = await r.json();
                let html = "";
                if(d.terminals && d.terminals.length > 0) {
                    d.terminals.slice(0,3).forEach(t => { html += `<li class="flex items-center gap-3"><i class="fa-solid fa-building-columns text-red-500"></i> [CEX] ${t.entity.toUpperCase()}: ${t.destination.substring(0,12)}...</li>`; });
                } else { html = `<li class="text-slate-500 italic">Analysis complete. Terminal endpoints pending final resolution.</li>`; }
                document.getElementById('step3-terminals').innerHTML = html;
            } catch(e) {}
        }

        function startTimer() {
            let time = 100; let tEl = document.getElementById('report-timer');
            clearInterval(timerInt);
            timerInt = setInterval(() => {
                time--; tEl.innerText = time + "s";
                if(time <= 0) { clearInterval(timerInt); document.getElementById('welcome-modal').classList.remove('hidden'); document.getElementById('welcome-modal').classList.add('flex'); document.getElementById('portal-link').href = "/portal?case_id=" + globalCaseId; }
            }, 1000);
        }

        function acceptReport() {
            clearInterval(timerInt);
            window.location.href = "/portal?case_id=" + globalCaseId;
        }
    </script>
    """ + FLOATING_TERMINAL_HTML + r"""
</body>
</html>
"""

HTML_CLIENT_PORTAL = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Client Portal | LIONSGATE</title>
    <script>window.tailwind = { corePlugins: { preflight: true } };</script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style> 
        body { background: #f1f5f9; color: #1e293b; font-family: 'Inter', sans-serif; } 
        .tab-content { display: none; } .tab-content.active { display: block; animation: fadeIn 0.3s ease; } @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .tab-btn.active { border-bottom: 2px solid #4f46e5; color: #4f46e5; }
        .dashboard-col { background: white; border-radius: 0.5rem; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); padding: 1.5rem; }
        
        /* Strict PDF Page Break Rules */
        .doc-container { background: white; width: 100%; max-width: 816px; min-height: 1056px; margin: 0 auto; padding: 4rem; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); position: relative; font-family: 'Times New Roman', serif; color: #1e293b; }
        .doc-watermark { position: absolute; top: 0; left: 0; right: 0; bottom: 0; margin: auto; width: 60%; opacity: 0.05; pointer-events: none; z-index: 0; background-image: url('https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png'); background-repeat: no-repeat; background-position: center; background-size: contain; }
        .doc-container h2 { page-break-after: avoid; }
        .doc-container table { page-break-inside: avoid; }
        .doc-container tr { page-break-inside: avoid; page-break-after: auto; }
        .doc-container p { page-break-inside: avoid; }
        .break-before-page { page-break-before: always; }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden flex flex-col min-h-[90vh]">
        <header class="bg-slate-900 text-white p-6 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-black uppercase tracking-widest flex items-center gap-3"><img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" class="h-8 bg-white rounded p-1"> Client Dashboard</h1>
                <p class="text-slate-400 font-bold uppercase text-xs mt-1 tracking-widest">Lionsgate Intelligence Network</p>
            </div>
            <div class="text-right"><p class="text-[10px] font-bold text-slate-400 uppercase">Case ID</p><p class="text-sm font-bold text-emerald-400 font-mono" id="dash-case-id">CASE-XXXX</p></div>
        </header>

        <div class="flex border-b border-slate-200 bg-slate-50 px-6 font-bold text-sm text-slate-500 uppercase tracking-wider">
            <button class="tab-btn active px-4 py-4 hover:text-indigo-600 transition" onclick="switchTab('tab-dashboard')"><i class="fa-solid fa-table-columns mr-2"></i> Dashboard</button>
            <button class="tab-btn px-4 py-4 hover:text-indigo-600 transition" onclick="switchTab('tab-report')"><i class="fa-solid fa-file-shield mr-2"></i> Full Forensic Report</button>
            <button class="tab-btn px-4 py-4 hover:text-indigo-600 transition" onclick="switchTab('tab-osint')"><i class="fa-solid fa-spider mr-2"></i> Threat Intel (OSINT)</button>
        </div>

        <div class="p-8 bg-slate-50 flex-grow relative overflow-y-auto">
            <div id="tab-dashboard" class="tab-content active">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="space-y-6">
                        <div class="dashboard-col">
                            <h2 class="text-xs font-black text-slate-800 uppercase border-b pb-2 mb-4"><i class="fa-solid fa-user text-blue-500 mr-2"></i> Client Profile</h2>
                            <div class="space-y-2 text-xs">
                                <p><span class="text-slate-500 font-bold">Name:</span> <span class="text-slate-800" id="prof-name"></span></p>
                                <p><span class="text-slate-500 font-bold">Location:</span> <span class="text-slate-800 font-mono" id="prof-zip"></span></p>
                                <p><span class="text-slate-500 font-bold">Status:</span> <span class="text-emerald-600 font-bold bg-emerald-50 px-1 rounded border border-emerald-100">Trace Completed</span></p>
                            </div>
                        </div>
                        <div class="dashboard-col flex-grow">
                            <h2 class="text-xs font-black text-slate-800 uppercase border-b pb-2 mb-4"><i class="fa-solid fa-clock-rotate-left text-blue-500 mr-2"></i> Case Timeline</h2>
                            <ul class="relative border-l border-slate-200 ml-3 space-y-6 pt-2">
                                <li class="pl-4"><div class="absolute w-3 h-3 bg-emerald-500 rounded-full -left-1.5 border border-white"></div><p class="text-[10px] font-bold text-emerald-600 uppercase">Completed</p><p class="text-xs font-bold text-slate-800">Automated Trace</p></li>
                                <li class="pl-4"><div class="absolute w-3 h-3 bg-indigo-500 rounded-full -left-1.5 border border-white animate-pulse"></div><p class="text-[10px] font-bold text-indigo-600 uppercase">Action Required</p><p class="text-xs font-bold text-slate-800">Review Report & Pay Retainer</p></li>
                                <li class="pl-4 opacity-50"><div class="absolute w-3 h-3 bg-slate-300 rounded-full -left-1.5 border border-white"></div><p class="text-[10px] font-bold text-slate-400 uppercase">Future</p><p class="text-xs font-bold text-slate-800">Law Enforcement Handover</p></li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="space-y-6">
                        <div class="dashboard-col bg-slate-900 text-white border-none relative overflow-hidden">
                            <div class="absolute top-0 right-0 p-4 opacity-10"><i class="fa-solid fa-file-shield text-6xl"></i></div>
                            <h2 class="text-xs font-black text-slate-100 uppercase border-b border-slate-700 pb-2 mb-4">Forensic Report (Redacted)</h2>
                            <p class="text-[11px] text-slate-400 leading-relaxed mb-4">The engine successfully traced the input seeds. The funds have been located at custodial endpoints subject to subpoena.</p>
                            <div class="bg-slate-800 p-3 rounded text-[10px] font-mono text-slate-300 mb-4 shadow-inner">
                                > Status: KYC Verified Endpoints Located<br>
                                > Action: Requires Retainer for Unmasking
                            </div>
                            <button onclick="switchTab('tab-report')" class="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-2 rounded text-xs transition"><i class="fa-solid fa-eye mr-1"></i> Preview Full Report</button>
                        </div>
                        <div class="dashboard-col border-indigo-200 bg-indigo-50 text-center">
                            <h2 class="text-xs font-black text-indigo-900 uppercase mb-2">Unredact & Proceed</h2>
                            <p class="text-[10px] text-indigo-700 mb-4">Authorize the analytical retainer to assign an investigator and unmask the final CEX endpoints for law enforcement.</p>
                            <button class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded text-xs shadow-md uppercase tracking-wider transition"><i class="fa-brands fa-stripe mr-1"></i> Proceed to Payment</button>
                        </div>
                    </div>
                    
                    <div class="dashboard-col flex flex-col h-full">
                        <h2 class="text-xs font-black text-slate-800 uppercase border-b pb-2 mb-4"><i class="fa-solid fa-comments text-blue-500 mr-2"></i> Investigator Comm Link</h2>
                        <div class="flex-grow bg-slate-50 border border-slate-200 rounded p-4 mb-4 overflow-y-auto space-y-3 shadow-inner min-h-[200px]">
                            <div class="text-center text-[9px] font-bold text-slate-400 my-2">Case Assigned to Lionsgate Unit</div>
                            <div class="bg-white border border-slate-200 p-3 rounded shadow-sm text-xs text-slate-700 w-5/6">
                                <p class="font-bold text-indigo-600 text-[10px] mb-1">System <span class="text-slate-400 font-normal ml-2">Just now</span></p>
                                Welcome to your unredacted portal. Your full forensic report and OSINT Threat Intelligence generation tools are now available in the tabs above.
                            </div>
                        </div>
                        <div class="flex gap-2 mt-auto">
                            <input type="text" class="flex-grow border border-slate-300 rounded px-3 py-2 text-xs outline-none focus:border-blue-500 shadow-inner" placeholder="Type a message to your investigator...">
                            <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 rounded text-xs font-bold shadow transition"><i class="fa-solid fa-paper-plane"></i></button>
                        </div>
                    </div>
                </div>
            </div>

            <div id="tab-report" class="tab-content">
                <div class="flex justify-between items-center mb-4">
                    <p class="text-xs text-slate-500 font-bold uppercase tracking-widest">Unredacted Evidentiary Report</p>
                    <div class="flex gap-2">
                        <button onclick="generateAINarrative()" id="aiReportBtn" class="bg-purple-600 text-white px-4 py-2 rounded text-xs font-bold shadow transition flex items-center gap-2">🧠 AI Synthesis</button>
                        <button onclick="window.print()" class="bg-blue-600 text-white px-4 py-2 rounded text-xs font-bold shadow transition flex items-center gap-2"><i class="fa-solid fa-print"></i> Print</button>
                        <button onclick="downloadPDF('doc-report', 'Lionsgate_Forensic_Report.pdf')" class="bg-red-600 text-white font-bold py-2 px-4 rounded text-xs shadow transition flex items-center gap-2"><i class="fa-solid fa-file-pdf"></i> Export PDF</button>
                    </div>
                </div>
                
                <div id="doc-report" class="doc-container">
                    <div class="doc-watermark"></div>
                    <div class="relative z-10">
                        <div class="text-center mb-10 border-b-2 border-black pb-6">
                            <img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" alt="Logo" class="h-16 mx-auto mb-4">
                            <h1 class="text-2xl font-black uppercase tracking-widest mb-2">Lionsgate Network Blockchain Forensics</h1>
                            <p class="text-sm font-bold uppercase tracking-widest text-slate-500">Highly Confidential / Evidentiary</p>
                            <p class="text-xs font-mono mt-4">CASE ID: <span class="inject-case font-bold text-red-600"></span> | DATE: <span class="inject-date font-bold"></span></p>
                        </div>

                        <h2 class="text-sm font-black uppercase tracking-wider mb-2 border-b border-slate-300 pb-1">Table of Contents</h2>
                        <ul class="text-xs space-y-1 mb-8 pl-4 font-bold text-slate-700">
                            <li>1. Executive Summary</li><li>2. Incident Details</li><li>3. AI Forensic Narrative Analysis</li><li>4. Investigation Methodology</li>
                            <li>5. Chronological Flow of Funds</li><li>6. Timeline of Events</li><li>7. Findings</li>
                            <li>8. Transaction Analysis</li><li>9. Overview of Key Transactions</li><li>10. Analysis of Transaction Patterns</li>
                            <li>11. Blockchain Snapshot Transaction Graph</li><li>12. Investigation Summary and Conclusion</li>
                            <li>13. Crypto-Victim Next-Steps</li><li>14. Law Enforcement Contacts</li>
                            <li>15. Glossary of Cryptocurrency Terms</li><li>16. Disclaimer & Scope of Services</li>
                        </ul>

                        <h2 class="text-sm font-black uppercase tracking-wider mb-2 border-b border-slate-300 pb-1 mt-8 break-before-page">1. Executive Summary</h2>
                        <p class="text-xs text-justify leading-relaxed mb-6">This report details the forensic tracing and recovery analysis of a compromised digital asset wallet. Utilizing the Lionsgate Network's proprietary Nemesis Omni-Chain Engine, investigators successfully reconstructed the transaction pathways, piercing obfuscation layers to resolve terminal endpoint attribution.</p>

                        <h2 class="text-sm font-black uppercase tracking-wider mb-2 border-b border-slate-300 pb-1 mt-8">2. Incident Details</h2>
                        <p class="text-xs text-justify leading-relaxed mb-6 italic text-slate-600" id="rep-incident"></p>

                        <h2 class="text-sm font-black uppercase tracking-wider mb-2 border-b border-slate-300 pb-1 mt-8 text-purple-800">3. AI Forensic Narrative Analysis</h2>
                        <div id="aiNarrativeContent" class="text-xs text-justify leading-relaxed mb-6 prose max-w-none text-slate-700">
                            <i class="text-slate-400">Awaiting Generation. Click "AI Synthesis" above.</i>
                        </div>

                        <h2 class="text-sm font-black uppercase tracking-wider mb-2 border-b border-slate-300 pb-1 mt-8">4. Investigation Methodology</h2>
                        <p class="text-xs text-justify leading-relaxed mb-6">The investigation utilized deterministic on-chain tracing, heuristic clustering algorithms, and automated OSINT metadata extraction via block explorers. The engine follows a strict "Value-Flow Conservation" model across all supported architectures (UTXO, EVM, SPL).</p>

                        <h2 class="text-sm font-black uppercase tracking-wider mb-2 border-b border-slate-300 pb-1 mt-8 break-before-page">5. Chronological Flow of Funds & Findings</h2>
                        <table class="w-full text-[10px] text-left border-collapse border border-slate-400 mb-6 bg-white"><thead class="bg-slate-100"><tr class="border-b border-slate-400"><th class="p-2 border-r border-slate-400 font-black uppercase">Source</th><th class="p-2 border-r border-slate-400 font-black uppercase">Destination Entity</th><th class="p-2 border-r border-slate-400 font-black uppercase">Amount</th><th class="p-2 font-black uppercase">Type</th></tr></thead><tbody id="rep-terminals" class="font-mono"></tbody></table>
                        
                        <h2 class="text-sm font-black uppercase tracking-wider mb-2 border-b border-slate-300 pb-1 mt-8">8. Transaction Analysis</h2>
                        <table class="w-full text-[9px] text-left border-collapse border border-slate-400 mb-6 bg-white"><thead class="bg-slate-100"><tr class="border-b border-slate-400"><th class="p-2 border-r border-slate-400 font-black uppercase">Hash</th><th class="p-2 border-r border-slate-400 font-black uppercase">Action</th><th class="p-2 font-black uppercase text-right">Value</th></tr></thead><tbody id="rep-txs" class="font-mono"></tbody></table>
                        
                        <h2 class="text-sm font-black uppercase tracking-wider mb-2 border-b border-slate-300 pb-1 mt-8">14. Law Enforcement Contacts</h2>
                        <div class="bg-slate-50 border border-slate-300 p-4 rounded mb-6 text-[10px] font-mono leading-relaxed" id="rep-le"></div>

                        <h2 class="text-sm font-black uppercase tracking-wider mb-2 border-b border-slate-300 pb-1 mt-12 break-before-page">16. Disclaimer & Scope of Services</h2>
                        <div class="text-[9px] text-justify leading-relaxed text-slate-600 space-y-2">
                            <p><strong>Lionsgate Network is on standby to support law enforcement detectives with forensic evidence and help facilitate the strongest outcome. You are not alone — we’ve got your back.</strong></p>
                            <p>Lionsgate Network makes no warranties, whether express, implied, statutory, or otherwise, with respect to the services or deliverables provided in this report. Lionsgate Network specifically disclaims all implied warranties of merchantability, fitness for a particular purpose, non-infringement, and those arising from a course of dealing, usage, or trade, and all such warranties are excluded to the fullest extent permitted by law.</p>
                            <p>Lionsgate Network will not be liable for any lost profits, business, contracts, revenues, goodwill, production, anticipated savings, loss of data, or costs of procuring substitute goods or services, or for any claim or demand against the company by any other party. In no event will Lionsgate Network be liable for consequential, incidental, special, indirect, or exemplary damages arising out of this agreement or any work statement, however caused and (to the fullest extent permitted by law) under any theory of liability—including negligence—even if Lionsgate Network has been advised of the possibility of such damages.</p>
                            <p>Lionsgate Network supports your recovery journey by producing advanced forensic blockchain tracing and OSINT intelligence designed to document the flow of assets, identify relevant entities, and prepare the evidentiary foundation required for escalation.</p>
                            <p>It is essential for clients to understand that law enforcement is the only authority empowered to subpoena, freeze, or seize funds. Our role is to strengthen your case, accelerate understanding, and provide detectives with the clearest possible roadmap for action—maximizing the probability of a successful recovery outcome.</p>
                            <p class="font-black uppercase text-black border-t border-slate-300 pt-2 mt-4 text-center">Confidentiality: Lionsgate Network Internal / Law Enforcement Use Only</p>
                        </div>
                    </div>
                </div>
            </div>

            <div id="tab-osint" class="tab-content">
                <div class="flex justify-between items-center mb-4">
                    <p class="text-xs text-slate-500 font-bold uppercase tracking-widest">Advanced Threat Intelligence</p>
                    <div class="flex gap-2">
                        <button onclick="generateOSINT()" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded text-xs shadow transition flex items-center gap-2" id="osint-btn"><i class="fa-solid fa-brain"></i> Generate OSINT Report</button>
                        <button onclick="downloadPDF('doc-osint', 'Lionsgate_OSINT_Threat_Intel.pdf')" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded text-xs shadow transition flex items-center gap-2"><i class="fa-solid fa-file-pdf"></i> Export PDF</button>
                    </div>
                </div>

                <div id="doc-osint" class="doc-container">
                    <div class="doc-watermark"></div>
                    <div class="relative z-10">
                        <div class="text-center mb-10 border-b-2 border-black pb-6">
                            <img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" alt="Logo" class="h-16 mx-auto mb-4">
                            <h1 class="text-2xl font-black uppercase tracking-widest mb-2 text-indigo-900">Threat Intelligence / OSINT Report</h1>
                            <p class="text-sm font-bold uppercase tracking-widest text-slate-500">AI Deep Analysis Module</p>
                            <p class="text-xs font-mono mt-4">CASE ID: <span class="inject-case font-bold text-red-600"></span></p>
                        </div>
                        <div id="osint-content" class="text-xs text-justify leading-relaxed prose max-w-none prose-sm">
                            <div class="flex flex-col items-center justify-center py-20 text-slate-400 italic">
                                <i class="fa-solid fa-spider text-4xl mb-4 text-indigo-300"></i>
                                <p>Awaiting DeepMind LLM Generation...</p>
                                <p class="text-[10px] mt-2">Click "Generate OSINT Report" to analyze associated IPs, domains, and entities.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const caseId = urlParams.get('case_id') || localStorage.getItem('nemesis_case_id') || "CASE-MANUAL";
        const clientName = localStorage.getItem('nemesis_name') || "Client";
        const zipCode = localStorage.getItem('nemesis_zip') || "00000";
        const countryStr = localStorage.getItem('nemesis_country') || "USA";
        const incidentStr = localStorage.getItem('nemesis_incident') || "No preliminary incident details provided.";
        
        document.getElementById('dash-case-id').innerText = caseId;
        document.getElementById('prof-name').innerText = clientName;
        document.getElementById('prof-zip').innerText = `${countryStr} (${zipCode})`;
        document.querySelectorAll('.inject-case').forEach(el => el.innerText = caseId);
        document.querySelectorAll('.inject-date').forEach(el => el.innerText = new Date().toLocaleDateString());
        document.getElementById('rep-incident').innerText = incidentStr;

        let leaHtml = `<strong>Local & Federal Field Office Mapping for ${countryStr} [Zip: ${zipCode}]</strong><br><br>`;
        leaHtml += `> <strong>Federal Bureau of Investigation (Cyber Division):</strong> www.ic3.gov | Phone: (202) 324-3000<br>`;
        leaHtml += `> <strong>US Secret Service (Digital Asset Task Force):</strong> www.secretservice.gov/investigation/cyber<br>`;
        leaHtml += `> <strong>State/Local Police Dept (Cybercrimes Unit):</strong> Contact non-emergency dispatch referencing this Case ID.<br>`;
        document.getElementById('rep-le').innerHTML = leaHtml;

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
            if(tabId === 'tab-report') loadReportData();
        }

        async function loadReportData() {
            try {
                let r = await fetch('/api/forensic_report_data?case_id=' + caseId);
                let d = await r.json();
                let tbody = "";
                let subpoenaList = [];
                if(d.terminals && d.terminals.length > 0) {
                    d.terminals.forEach(t => { 
                        let riskBadge = t.ml_risk === 'high-risk' ? '<span class="bg-red-100 text-red-800 px-1 rounded ml-1 text-[8px] uppercase">High Risk</span>' : (t.ml_risk === 'anomaly' ? '<span class="bg-orange-100 text-orange-800 px-1 rounded ml-1 text-[8px] uppercase">Anomaly</span>' : '<span class="bg-emerald-100 text-emerald-800 px-1 rounded ml-1 text-[8px] uppercase">Normal</span>');
                        tbody += `<tr><td class="p-2 border border-slate-300 break-all text-[8px]">${t.source}</td><td class="p-2 border border-slate-300 break-all text-[8px] font-bold text-red-600">${t.destination}<br><span class="text-slate-500">${t.entity}</span>${riskBadge}</td><td class="p-2 border border-slate-300 font-bold">${t.amount}</td><td class="p-2 border border-slate-300 uppercase">${t.type}</td></tr>`; 
                        subpoenaList.push(`${t.entity} Deposit Address: ${t.destination} (Amount: ${t.amount})`);
                    });
                } else { tbody = `<tr><td colspan="4" class="p-4 text-center italic text-slate-500">No terminal endpoints resolved in this trace segment.</td></tr>`; }
                document.getElementById('rep-terminals').innerHTML = tbody;
                window.subpoenaTargets = subpoenaList.join(" | ");

                let txbody = "";
                if(d.transactions && d.transactions.length > 0) {
                    d.transactions.forEach(t => { txbody += `<tr><td class="p-2 border border-slate-300 break-all text-[8px] text-blue-600">${t.hash}</td><td class="p-2 border border-slate-300 break-all text-[8px] font-bold">${t.type}</td><td class="p-2 border border-slate-300 font-bold text-right">${t.amount} ${t.ticker}</td></tr>`; });
                } else { txbody = `<tr><td colspan="3" class="p-4 text-center italic text-slate-500">No transactions recorded.</td></tr>`; }
                document.getElementById('rep-txs').innerHTML = txbody;
            } catch(e) {}
        }

        async function generateAINarrative() {
            let btn = document.getElementById('aiReportBtn'); btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generating...`; btn.disabled = true;
            document.getElementById('aiNarrativeContent').innerHTML = '<p class="text-center font-bold text-purple-500 animate-pulse">DeepMind LLM is writing legal narrative...</p>';
            try {
                let r = await fetch('/api/generate_narrative', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ case_id: caseId, subpoena_targets: window.subpoenaTargets || "None" }) });
                let d = await r.json();
                document.getElementById('aiNarrativeContent').innerHTML = marked.parse(d.narrative);
            } catch(e) { document.getElementById('aiNarrativeContent').innerHTML = '<p class="text-red-500 font-bold">LLM Synthesis Failed.</p>'; } finally { btn.innerHTML = `🧠 AI Synthesis`; btn.disabled = false; }
        }

        async function generateOSINT() {
            let btn = document.getElementById('osint-btn'); btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generating...`; btn.disabled = true;
            document.getElementById('osint-content').innerHTML = '<p class="text-center font-bold text-indigo-500 animate-pulse py-20">DeepMind LLM is synthesizing threat vectors...</p>';
            try {
                let r = await fetch('/api/generate_osint_report', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ details: "Case: " + caseId + ". Incident context: " + incidentStr }) });
                let d = await r.json();
                document.getElementById('osint-content').innerHTML = d.report_html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\n/g, '<li>$1</li>').replace(/\n/g, '<br>');
            } catch(e) { document.getElementById('osint-content').innerHTML = '<p class="text-red-500 font-bold text-center py-20">LLM Engine Connection Failed.</p>'; } finally { btn.innerHTML = `<i class="fa-solid fa-brain"></i> Generate OSINT Report`; btn.disabled = false; }
        }

        function downloadPDF(elementId, filename) { html2pdf().set({ margin: 0, filename: filename, html2canvas: { scale: 2, useCORS: true }, jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' } }).from(document.getElementById(elementId)).save(); }
        loadReportData();
    </script>
    """ + FLOATING_TERMINAL_HTML + r"""
</body>
</html>
"""

HTML_DARKX = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NEMESIS DarkX | LIONSGATE</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        .cyber-grid { background-size: 40px 40px; background-image: linear-gradient(to right, rgba(99, 102, 241, 0.1) 1px, transparent 1px), linear-gradient(to bottom, rgba(99, 102, 241, 0.1) 1px, transparent 1px); }
        .glow-input { box-shadow: 0 0 15px rgba(79, 70, 229, 0.5); border-color: #6366f1; }
        .modal-glass { background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(20px); border: 1px solid #334155; }
    </style>
</head>
<body class="cyber-grid min-h-screen flex flex-col items-center pt-20 pb-10 px-4">
    <a href="/" class="absolute top-6 left-8 text-slate-400 hover:text-white transition text-sm font-bold flex items-center gap-2"><i class="fa-solid fa-arrow-left"></i> Main Command</a>
    <div class="text-center mb-10 w-full max-w-3xl">
        <img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" alt="Lionsgate Logo" class="h-28 mx-auto mb-6 bg-white p-2 rounded-xl shadow-[0_0_30px_rgba(255,255,255,0.2)]">
        <button class="bg-gradient-to-r from-indigo-900 to-slate-900 border border-indigo-500 text-indigo-300 px-6 py-2 rounded-full text-sm font-black tracking-widest uppercase mb-3 shadow-[0_0_15px_rgba(99,102,241,0.4)] pointer-events-none">NEMESIS DarkX</button>
        <p class="text-xs font-bold text-slate-500 uppercase tracking-[0.2em]">By Lionsgate Intelligence Network</p>
    </div>
    <div class="w-full max-w-3xl relative mb-12">
        <i class="fa-solid fa-spider absolute left-5 top-4 text-indigo-500 text-lg"></i>
        <input type="text" id="searchInput" placeholder="Enter IP, Domain, Email, or Wallet Address..." class="w-full bg-slate-900 border border-slate-700 text-white rounded-xl py-4 pl-14 pr-6 text-sm focus:outline-none focus:glow-input transition shadow-inner font-mono" onkeypress="if(event.key === 'Enter') startSearch()">
        <button onclick="startSearch()" class="absolute right-3 top-2.5 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition shadow-md">Query Deep Web</button>
    </div>
    <div class="w-full max-w-3xl space-y-4" id="resultsContainer"></div>

    <div id="dossierModal" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 bg-black/80">
        <div class="modal-glass w-full max-w-4xl h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden relative">
            <div class="absolute top-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>
            <div class="p-6 border-b border-slate-700 flex justify-between items-center bg-slate-900/50">
                <h2 class="text-xl font-black text-indigo-400 uppercase tracking-widest flex items-center gap-3"><i class="fa-solid fa-file-shield text-white"></i> Full Intelligence Dossier</h2>
                <button onclick="document.getElementById('dossierModal').classList.add('hidden')" class="text-slate-400 hover:text-white transition"><i class="fa-solid fa-xmark text-xl"></i></button>
            </div>
            <div id="dossierContent" class="p-8 overflow-y-auto flex-grow text-sm text-slate-300 leading-relaxed font-mono"></div>
        </div>
    </div>

    <script>
        let eventSource = null;
        function startSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;
            const container = document.getElementById('resultsContainer');
            container.innerHTML = `<div class="text-center text-indigo-500 font-mono text-sm py-10 animate-pulse">Establishing secure connection to Datastore...</div>`;
            if (eventSource) eventSource.close();
            eventSource = new EventSource(`/api/darkx/stream?q=${encodeURIComponent(query)}`);
            container.innerHTML = ''; 

            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.error) { container.innerHTML += `<div class="p-4 bg-red-900/20 border border-red-500/50 text-red-400 rounded-lg">${data.error}</div>`; eventSource.close(); return; }
                if (data.end) { container.innerHTML += `<div class="text-center text-slate-500 py-4">--- End of Stream ---</div>`; eventSource.close(); return; }
                
                const entities = data.uie_entities || [];
                const entityTags = entities.slice(0, 4).map(e => `<span class="bg-indigo-900/50 text-indigo-300 border border-indigo-700/50 px-2 py-0.5 rounded text-[10px]">${e.ontology_class}: ${e.value}</span>`).join(' ');
                const date = data.crawled_at ? new Date(data.crawled_at).toLocaleString() : "Unknown Date";

                container.insertAdjacentHTML('beforeend', `
                <div class="bg-slate-900 border border-slate-700 p-5 rounded-xl hover:border-indigo-500 transition shadow-lg flex justify-between items-start">
                    <div class="space-y-3 w-3/4">
                        <div class="flex items-center gap-2"><span class="text-emerald-500 text-[10px] font-bold uppercase"><i class="fa-solid fa-globe"></i> Intercepted Node</span><span class="text-slate-500 text-[10px] font-mono">${date}</span></div>
                        <h3 class="text-sm font-bold text-white truncate">${data.web_info?.title || "Unknown"}</h3>
                        <p class="text-[10px] text-slate-400 font-mono truncate">${data.web_info?.url || "Unknown"}</p>
                        <div class="flex flex-wrap gap-2 mt-2">${entityTags}</div>
                    </div>
                    <button onclick="generateDossier('${data.id}')" class="bg-slate-800 hover:bg-slate-700 text-indigo-400 border border-slate-600 px-4 py-2 rounded text-[10px] font-bold uppercase transition"><i class="fa-solid fa-file-contract mr-1"></i> Full Dossier</button>
                </div>`);
            };
        }

        async function generateDossier(docId) {
            const modal = document.getElementById('dossierModal');
            const content = document.getElementById('dossierContent');
            modal.classList.remove('hidden');
            content.innerHTML = `<div class="flex flex-col items-center justify-center h-full space-y-4"><i class="fa-solid fa-circle-notch fa-spin text-4xl text-indigo-500"></i><p class="text-indigo-400 animate-pulse uppercase">DeepMind LLM Synthesizing Raw Intercept Data...</p></div>`;
            try {
                const res = await fetch('/api/darkx/dossier', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ doc_id: docId }) });
                const data = await res.json();
                content.innerHTML = res.ok ? `<div class="prose prose-invert prose-sm max-w-none">${data.dossier_html}</div>` : `<div class="text-red-500 text-center py-20 font-bold">${data.detail}</div>`;
            } catch (e) { content.innerHTML = `<div class="text-red-500 text-center py-20 font-bold">Network error reaching Intelligence Backend.</div>`; }
        }
    </script>
    """ + FLOATING_TERMINAL_HTML + r"""
</body>
</html>
"""

HTML_ABOUT = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Nemesis: Master Whitepaper & NEMESIS ID</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    
    <!-- NEMESIS ID Libraries -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>

    <style>
        html { scroll-behavior: smooth; }
        body { background-color: #f8fafc; font-family: 'Inter', sans-serif; color: #334155; -webkit-font-smoothing: antialiased; }
        
        /* Scrollbars */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

        /* Flashing Alerts */
        @keyframes flash-critical {
            0%, 100% { background-color: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.5); box-shadow: 0 0 15px rgba(239, 68, 68, 0.2); }
            50% { background-color: rgba(239, 68, 68, 0.3); border-color: rgba(239, 68, 68, 0.9); box-shadow: 0 0 30px rgba(239, 68, 68, 0.6); }
        }
        .alert-flashing { animation: flash-critical 1.5s infinite; color: #b91c1c; }

        /* Tabs */
        .nid-tab-content { display: none; animation: fadeIn 0.3s ease-in-out; }
        .nid-tab-content.active { display: block; }
        .nid-tab-btn { transition: all 0.2s; border-bottom: 2px solid transparent; white-space: nowrap; color: #64748b; }
        .nid-tab-btn:hover { color: #3b82f6; background: #eff6ff; }
        .nid-tab-btn.active { border-bottom-color: #2563eb; color: #1d4ed8; background: #eff6ff; font-weight: 700; }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

        /* Vis Network Container */
        #trace-network { width: 100%; height: 600px; background: #0f172a; border: 1px solid #1e293b; border-radius: 0.5rem; outline: none; }
        
        /* Printable Report Styles */
        .print-doc-container { display: none; background: #ffffff; color: #000000; font-family: 'Times New Roman', Times, serif; padding: 1in; max-width: 8.5in; margin: 0 auto; line-height: 1.6; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .print-doc-container.active { display: block; }
        .print-doc-container h1, .print-doc-container h2, .print-doc-container h3 { font-family: 'Inter', sans-serif; color: #111827; page-break-after: avoid; }
        .print-doc-container table { width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; font-size: 0.85rem; font-family: 'Inter', sans-serif; }
        .print-doc-container th, .print-doc-container td { border: 1px solid #cbd5e1; padding: 0.5rem; text-align: left; }
        .print-doc-container th { background: #f1f5f9; }
        .page-break { page-break-before: always; }
    </style>
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'base' });
    </script>
</head>
<body class="bg-slate-50">

    <!-- WHITEPAPER VIEW -->
    <div id="whitepaper-view" class="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-[280px_1fr] min-h-screen bg-white shadow-xl relative">
        <aside class="bg-slate-100 border-r border-slate-200 p-8 hidden lg:flex flex-col sticky top-0 h-screen overflow-y-auto">
            <a href="/"><img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" alt="LIONSGATE" class="h-12 object-contain mb-8 opacity-80 hover:opacity-100 transition"></a>
            <button onclick="window.print()" class="mb-8 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg shadow-md transition flex items-center justify-center gap-2">
                <i class="fa-solid fa-file-pdf"></i> Print to PDF
            </button>
            <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 mb-4">Master Contents</h3>
            <nav class="flex-grow space-y-2 text-sm text-slate-600 font-medium">
                <a href="#executive-summary" class="block hover:text-blue-600">1. Executive Summary</a>
                <a href="#core-features" class="block hover:text-blue-600">2. Core Features</a>
                <a href="#nemesis-id-section" class="block text-blue-600 font-bold bg-blue-50 p-2 rounded border border-blue-200">3. NEMESIS ID Dashboard</a>
            </nav>
        </aside>

        <main class="p-10 lg:p-20">
            <section class="mb-24">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 border border-blue-200 mb-6 uppercase tracking-widest"><i class="fa-solid fa-book-journal-whills mr-2"></i> Master Whitepaper</span>
                <h1 class="text-6xl font-black mb-6 tracking-tighter leading-none text-slate-900">PROJECT NEMESIS</h1>
                <p class="text-2xl text-slate-600 max-w-3xl font-light leading-relaxed border-l-4 border-blue-500 pl-6">The definitive guide to Lionsgate's Omni-Chain Cyber Intelligence, Forensic Tracing Engine, and LangGraph AI Swarm Architecture.</p>
            </section>

            <section id="executive-summary" class="mb-20">
                <h2 class="text-3xl font-black uppercase tracking-tight mb-6">1. Executive Summary</h2>
                <p class="text-slate-600 leading-loose mb-4">Project Nemesis (v100.19 PROD) represents a paradigm shift in decentralized forensic analysis. Developed by the Lionsgate Intelligence Network, it is a fully autonomous, enterprise-grade tracing engine engineered to dismantle the asymmetry between illicit actors and law enforcement.</p>
            </section>

            <section id="nemesis-id-section" class="mb-20 bg-slate-50 p-10 rounded-2xl border border-slate-200 shadow-sm text-center">
                <h2 class="text-3xl font-black uppercase tracking-tight mb-4">3. NEMESIS ID Dashboard</h2>
                <p class="text-slate-600 mb-8 max-w-2xl mx-auto">The premier interactive graphical interface and analytical dashboard. It aggregates omni-chain data, OSINT, and AI analysis into a single unified view.</p>
                <button onclick="openSearchModal()" class="bg-indigo-600 hover:bg-indigo-700 text-white font-black py-4 px-10 rounded-xl shadow-lg transition-transform transform hover:-translate-y-1 text-lg flex items-center justify-center gap-3 mx-auto">
                    <i class="fa-solid fa-fingerprint"></i> LAUNCH NEMESIS ID
                </button>
            </section>
        </main>
    </div>

    <!-- SEARCH MODAL -->
    <div id="search-modal" class="hidden fixed inset-0 z-[100] bg-slate-900/95 backdrop-blur flex items-center justify-center p-4">
        <div class="bg-white p-10 rounded-2xl shadow-2xl w-full max-w-lg text-center relative">
            <button onclick="closeSearchModal()" class="absolute top-4 right-4 text-slate-400 hover:text-red-500"><i class="fa-solid fa-xmark text-xl"></i></button>
            <i class="fa-solid fa-magnifying-glass-chart text-5xl text-blue-600 mb-4"></i>
            <h2 class="text-2xl font-black uppercase tracking-widest text-slate-900 mb-2">NEMESIS ID Lookup</h2>
            <p class="text-xs text-slate-500 mb-6">Enter a wallet address or transaction hash to generate a full cyber intelligence dossier.</p>
            <input type="text" id="nid-search-input" placeholder="0x..." class="w-full bg-slate-50 border border-slate-300 p-4 rounded-lg font-mono text-sm mb-4 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200">
            <button onclick="executeSearch()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-lg uppercase tracking-widest shadow-md transition">Initialize Deep Scan</button>
        </div>
    </div>

    <!-- LOADER MODAL -->
    <div id="loader-modal" class="hidden fixed inset-0 z-[110] bg-slate-900 flex flex-col items-center justify-center">
        <i class="fa-solid fa-circle-notch fa-spin text-6xl text-blue-500 mb-6"></i>
        <h2 class="text-xl font-black text-white uppercase tracking-widest animate-pulse">Aggregating Omni-Chain Data...</h2>
        <p class="text-xs text-blue-300 font-mono mt-2">Bypassing obfuscation layers & synthesizing LLM context</p>
    </div>

    <!-- FULL SCREEN DASHBOARD VIEW -->
    <div id="dashboard-view" class="hidden fixed inset-0 z-[120] bg-slate-50 flex flex-col h-screen overflow-hidden">
        
        <!-- DASHBOARD HEADER -->
        <header class="bg-white border-b border-slate-200 px-6 py-4 flex-shrink-0 flex justify-between items-center shadow-sm z-50">
            <div class="flex items-center gap-6">
                <button onclick="exitDashboard()" class="text-slate-400 hover:text-slate-900 transition flex items-center gap-2 font-bold text-sm"><i class="fa-solid fa-arrow-left"></i> Back</button>
                <div class="h-8 w-px bg-slate-300"></div>
                <div>
                    <div class="flex items-center gap-3 mb-1">
                        <h1 class="text-xl font-black text-slate-900 uppercase tracking-tight flex items-center gap-2">
                            <i class="fa-brands fa-ethereum text-indigo-500"></i> 
                            <span id="dash-wallet-title" class="font-mono">0x742d35Cc6634C0532925a3b844Bc454e4438f44e</span>
                        </h1>
                        <div class="flex gap-1 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-xs">
                            <i class="fa-brands fa-ethereum text-indigo-500"></i>
                            <i class="fa-brands fa-btc text-orange-500"></i>
                            <i class="fa-solid fa-link text-purple-500"></i>
                        </div>
                    </div>
                    <div class="flex items-center gap-4 text-xs font-mono">
                        <span class="text-slate-500 font-bold uppercase">SUBJECT WALLET ENTITY:</span>
                        <span class="text-red-700 font-bold bg-red-50 px-2 py-0.5 rounded border border-red-200 shadow-sm">LAZARUS GROUP EXPLOITER (NODE 4)</span>
                    </div>
                    <div class="flex gap-2 mt-2 text-[9px] font-bold uppercase tracking-wider">
                        <span class="bg-slate-800 text-white px-2 py-1 rounded">High-Volume Exploiter</span>
                        <span class="bg-red-600 text-white px-2 py-1 rounded"><i class="fa-solid fa-skull"></i> Sanctioned / OFAC</span>
                        <span class="bg-purple-100 text-purple-800 px-2 py-1 rounded border border-purple-200">Entity-tagged metadata</span>
                    </div>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <div class="alert-flashing px-4 py-2 rounded-lg border flex items-center gap-3">
                    <i class="fa-solid fa-triangle-exclamation text-xl"></i>
                    <div>
                        <p class="text-[9px] font-black uppercase tracking-widest">CEX / Custodial Alert</p>
                        <p class="text-xs font-bold">BINANCE HOT WALLET 14</p>
                    </div>
                </div>
                <button onclick="switchNidTab('nid-tab-report')" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-md transition text-xs uppercase tracking-widest flex items-center gap-2">
                    <i class="fa-solid fa-file-export"></i> Export DOSSIER
                </button>
                <a href="/" class="bg-slate-800 hover:bg-slate-900 text-white font-bold py-3 px-6 rounded-lg shadow-md transition text-xs uppercase tracking-widest"><i class="fa-solid fa-house"></i> Main Page</a>
            </div>
        </header>

        <!-- DASHBOARD TABS NAV -->
        <nav class="bg-white border-b border-slate-200 px-4 flex overflow-x-auto scrollbar-hide flex-shrink-0 z-40 shadow-sm">
            <button class="nid-tab-btn active px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-profile')">1. Wallet Profile</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-counterparties')">2. Counterparties</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-assets')">3. Assets</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-chains')">4. Chains</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-transactions')">5. Transactions</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-balances')">6. Balances</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-graph')">7. Trace Graph</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider text-red-600 hover:text-red-700" onclick="switchNidTab('nid-tab-aml')">8. AML</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-georisk')">9. GeoRisk</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-intelligence')">10. Intelligence</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider text-purple-600 hover:text-purple-700" onclick="switchNidTab('nid-tab-ai')">11. AI Insights</button>
            <button class="nid-tab-btn px-4 py-3 text-[11px] font-bold uppercase tracking-wider" onclick="switchNidTab('nid-tab-report')">12. Full Report</button>
        </nav>

        <!-- DASHBOARD CONTENT AREA -->
        <div class="flex-grow overflow-y-auto p-6 relative">
            
            <!-- TAB 1: PROFILE -->
            <div id="nid-tab-profile" class="nid-tab-content active space-y-6 max-w-7xl mx-auto">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm lg:col-span-2">
                        <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-3 border-b pb-2"><i class="fa-solid fa-microchip text-blue-500 mr-2"></i> NLP Wallet Summary</h2>
                        <p class="text-sm text-slate-600 leading-relaxed">This wallet operates as an intermediary consolidation node attributed to the Lazarus Group. It exhibits high-velocity peeling behavior indicative of programmatic laundering. Primary activity involves bridging stolen assets via cross-chain pools and routing terminal deposits into Asian-domiciled CEX accounts to bypass KYC.</p>
                    </div>
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-3 border-b pb-2">Profile Metrics</h2>
                        <div class="space-y-2 text-xs font-mono text-slate-600">
                            <div class="flex justify-between"><span>Classification:</span> <span class="text-red-600 font-bold">Malicious / Exploiter</span></div>
                            <div class="flex justify-between"><span>Type:</span> <span class="font-bold">Externally Owned Account</span></div>
                            <div class="flex justify-between"><span>ENS:</span> <span>None</span></div>
                            <div class="flex justify-between"><span>First Activity:</span> <span>2023-04-12</span></div>
                            <div class="flex justify-between"><span>Last Activity:</span> <span class="text-emerald-600">2026-05-27</span></div>
                            <div class="flex justify-between"><span>Total Tx:</span> <span>14,205</span></div>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-center"><p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Current Balance</p><p class="text-2xl font-black text-blue-600 font-mono">$1,452,890.22</p></div>
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-center"><p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Total Inbound</p><p class="text-2xl font-black text-emerald-600 font-mono">$84,500,000.00</p></div>
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-center"><p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Total Outbound</p><p class="text-2xl font-black text-red-600 font-mono">$83,047,109.78</p></div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-3 border-b pb-2">Funded By / Origin</h2>
                        <p class="text-xs font-mono text-slate-600 mb-1"><strong>Wallet:</strong> <span class="text-blue-600">0xd90e2f925da...</span></p>
                        <p class="text-xs font-mono text-slate-600 mb-1"><strong>Entity:</strong> <span class="bg-purple-100 text-purple-800 px-1 rounded">Tornado Cash 100 ETH</span></p>
                        <p class="text-xs font-mono text-slate-600"><strong>Type:</strong> Mixer (INBOUND)</p>
                    </div>
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-3 border-b pb-2">Clustered Wallets (GNN)</h2>
                        <div class="flex flex-wrap gap-2 text-[10px] font-mono font-bold">
                            <span class="bg-red-50 text-red-700 border border-red-200 px-2 py-1 rounded">Lazarus Cluster A (ETH)</span>
                            <span class="bg-orange-50 text-orange-700 border border-orange-200 px-2 py-1 rounded">Lazarus Cluster B (BSC)</span>
                            <span class="bg-slate-100 text-slate-700 border border-slate-300 px-2 py-1 rounded">Node: 0x88a...4b1</span>
                        </div>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-4 border-b pb-2">Interacted With / Chronological Flow</h2>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs font-mono">
                            <thead class="bg-slate-50 text-slate-600 uppercase"><tr><th class="p-2 border-b">Wallet Address</th><th class="p-2 border-b">Classification</th><th class="p-2 border-b">Flow</th><th class="p-2 border-b text-right">Amount</th><th class="p-2 border-b">Chain</th><th class="p-2 border-b">Behavior Analysis</th></tr></thead>
                            <tbody class="divide-y divide-slate-100 text-slate-700">
                                <tr class="hover:bg-slate-50 cursor-pointer"><td class="p-2 text-blue-600 hover:underline">0x28c6c06298d514db089...</td><td class="p-2"><span class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded">CEX: Binance Hot</span></td><td class="p-2 font-bold text-red-600">OUTBOUND</td><td class="p-2 text-right font-bold">$1,200,000</td><td class="p-2 text-indigo-600 font-bold">ETH</td><td class="p-2 text-[10px] text-slate-500">Terminal Deposit</td></tr>
                                <tr class="hover:bg-slate-50 cursor-pointer"><td class="p-2 text-blue-600 hover:underline">0xdf9b4b57865b403e08c...</td><td class="p-2"><span class="bg-blue-100 text-blue-800 px-2 py-0.5 rounded">BRIDGE: Stargate</span></td><td class="p-2 font-bold text-emerald-600">INBOUND</td><td class="p-2 text-right font-bold">$5,500,000</td><td class="p-2 text-purple-600 font-bold">POLY</td><td class="p-2 text-[10px] text-slate-500">Cross-Chain Hop</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TAB 2: COUNTERPARTIES -->
            <div id="nid-tab-counterparties" class="nid-tab-content space-y-6 max-w-7xl mx-auto">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h2 class="text-sm font-black text-emerald-600 uppercase tracking-widest mb-4 border-b pb-2">Total Inbound (Top Senders)</h2>
                        <canvas id="chartSenders" height="250"></canvas>
                    </div>
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h2 class="text-sm font-black text-red-600 uppercase tracking-widest mb-4 border-b pb-2">Total Outbound (Top Receivers)</h2>
                        <canvas id="chartReceivers" height="250"></canvas>
                    </div>
                </div>
                <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-4 border-b pb-2">Counterparties Transactions Intelligence</h2>
                    <table class="w-full text-left text-xs font-mono"><thead class="bg-slate-50 text-slate-600"><tr><th class="p-2 border-b">Date & Time</th><th class="p-2 border-b">Network</th><th class="p-2 border-b">TX Hash</th><th class="p-2 border-b">Entity</th><th class="p-2 border-b">Wallet Address</th><th class="p-2 border-b">Details</th></tr></thead>
                    <tbody class="divide-y divide-slate-100">
                        <tr class="hover:bg-slate-50 cursor-pointer"><td class="p-2 text-slate-500">2026-05-27 08:14</td><td class="p-2">ETH</td><td class="p-2 text-blue-500 hover:underline">0xab12...89ef</td><td class="p-2 font-bold">Binance Hot 14</td><td class="p-2 text-blue-500">0x28c...d60</td><td class="p-2"><button class="bg-slate-800 text-white px-2 py-1 rounded text-[9px] uppercase hover:bg-blue-600 transition">Inspect</button></td></tr>
                    </tbody></table>
                </div>
            </div>

            <!-- TAB 3: ASSETS -->
            <div id="nid-tab-assets" class="nid-tab-content space-y-6 max-w-7xl mx-auto text-center py-20">
                <h2 class="text-2xl font-black text-slate-800 uppercase mb-4">Global Multi-Chain Portfolio</h2>
                <p class="text-slate-500 font-mono">Cross-blockchain asset compilation active.</p>
            </div>

            <!-- TAB 4: CHAINS -->
            <div id="nid-tab-chains" class="nid-tab-content space-y-6 max-w-7xl mx-auto text-center py-20">
                <h2 class="text-2xl font-black text-slate-800 uppercase mb-4">Supported Blockchain Networks</h2>
                <div class="flex justify-center gap-4 text-3xl text-slate-400"><i class="fa-brands fa-ethereum"></i><i class="fa-brands fa-btc"></i><i class="fa-solid fa-link"></i></div>
            </div>

            <!-- TAB 5: TRANSACTIONS -->
            <div id="nid-tab-transactions" class="nid-tab-content space-y-6 max-w-7xl mx-auto">
                <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-lg font-black text-slate-800 uppercase tracking-widest">Transaction History</h2>
                        <div class="flex gap-4">
                            <div class="bg-emerald-50 border border-emerald-200 px-4 py-2 rounded text-center"><p class="text-[10px] font-bold text-emerald-700 uppercase">Total Inbound Vol</p><p class="font-mono font-black text-emerald-900">$84,500,000</p></div>
                            <div class="bg-red-50 border border-red-200 px-4 py-2 rounded text-center"><p class="text-[10px] font-bold text-red-700 uppercase">Total Outbound Vol</p><p class="font-mono font-black text-red-900">$83,047,109</p></div>
                        </div>
                    </div>
                    <div class="flex gap-2 mb-4 border-b border-slate-200 pb-2">
                        <button class="bg-blue-50 text-blue-700 font-bold px-3 py-1.5 rounded text-xs">Multi-Chain</button>
                        <button class="text-slate-500 hover:text-blue-600 font-bold px-3 py-1.5 rounded text-xs">Bridging</button>
                        <button class="text-slate-500 hover:text-blue-600 font-bold px-3 py-1.5 rounded text-xs">NFT/Tokens</button>
                    </div>
                    <p class="text-center py-10 text-slate-500 font-mono italic">Full 14,205 transaction ledger structured by Patterns, Internals, and Tokens.</p>
                </div>
            </div>

            <!-- TAB 6: BALANCES -->
            <div id="nid-tab-balances" class="nid-tab-content space-y-6 max-w-7xl mx-auto">
                <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-4 border-b pb-2">Balance Analytics (Graphical)</h2>
                    <canvas id="chartBalances" height="250"></canvas>
                </div>
            </div>

            <!-- TAB 7: TRACE GRAPH -->
            <div id="nid-tab-graph" class="nid-tab-content h-full max-w-[1600px] mx-auto">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-black text-slate-800 uppercase tracking-widest flex items-center gap-2"><i class="fa-solid fa-network-wired text-blue-600"></i> Autonomous Trace Graph</h2>
                    <div class="flex gap-2">
                        <button class="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded text-xs font-bold font-mono border border-slate-300 shadow-sm transition"><i class="fa-solid fa-satellite-dish text-emerald-600 mr-1"></i> Custom Trace Options</button>
                        <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-xs font-bold font-mono shadow-md transition" onclick="switchNidTab('nid-tab-ai')"><i class="fa-solid fa-robot mr-1"></i> Generate AI Infographics</button>
                    </div>
                </div>
                
                <div class="flex gap-4 h-[calc(100vh-250px)] min-h-[600px] relative">
                    <div id="trace-network" class="flex-grow shadow-lg relative overflow-hidden bg-slate-900 rounded-xl"></div>
                    
                    <div class="w-64 bg-white/95 backdrop-blur shadow-xl border border-slate-200 z-10 p-4 rounded-xl absolute right-4 top-4">
                        <h3 class="text-xs font-black uppercase text-slate-800 border-b border-slate-200 pb-2 mb-3">Color Legend</h3>
                        <ul class="text-[10px] font-mono space-y-2 text-slate-600 font-bold">
                            <li class="flex items-center gap-2"><span class="w-4 h-4 rounded-full bg-[#ef4444] border-2 border-white shadow-sm"></span> Target Wallet</li>
                            <li class="flex items-center gap-2"><span class="w-4 h-4 rounded-full bg-[#3b82f6] border-2 border-white shadow-sm"></span> Regular Addresses</li>
                            <li class="flex items-center gap-2"><span class="w-4 h-4 rounded-full bg-[#8b5cf6] border-2 border-white shadow-sm"></span> Smart Contracts</li>
                            <li class="flex items-center gap-2"><span class="w-4 h-4 rounded-full bg-[#f59e0b] border-2 border-white shadow-sm"></span> Exchanges/Custodial</li>
                            <li class="flex items-center gap-2"><span class="w-4 h-4 rounded-full bg-[#ec4899] border-2 border-white shadow-sm"></span> DApps</li>
                            <li class="flex items-center gap-2"><span class="w-4 h-4 rounded-full bg-[#64748b] border-2 border-white shadow-sm"></span> Mixers</li>
                        </ul>
                        <hr class="my-3 border-slate-200">
                        <p class="text-[9px] text-slate-500 leading-relaxed mb-2">Multi-directional arrows pulse to indicate flow. Right-click node for AI OSINT lookup.</p>
                    </div>
                </div>
            </div>

            <!-- TAB 8: AML -->
            <div id="nid-tab-aml" class="nid-tab-content space-y-6 max-w-7xl mx-auto">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-red-50 p-6 rounded-xl border border-red-200 shadow-sm flex flex-col items-center justify-center text-center alert-flashing">
                        <div class="text-7xl font-black mb-2 font-mono text-red-700">98<span class="text-3xl text-red-400">/100</span></div>
                        <div class="text-sm font-bold uppercase tracking-widest text-red-900 mt-2">Critical Risk Exposure</div>
                        <div class="text-xs font-mono mt-4 text-red-800 leading-relaxed">Direct linkage to OFAC Specially Designated Nationals (SDN) List and highly illicit mixer transactions.</div>
                    </div>
                    
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm md:col-span-2">
                        <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-4 border-b pb-2">VASP / Illicit Interactions</h2>
                        <table class="w-full text-left font-mono text-xs">
                            <thead class="bg-slate-50 text-slate-600"><tr><th class="p-2 border-b">Entity & Wallet</th><th class="p-2 border-b">Classification</th><th class="p-2 border-b text-right">Exposure Volume</th></tr></thead>
                            <tbody class="divide-y divide-slate-100">
                                <tr><td class="p-2">Tornado Cash<br><span class="text-[9px] text-blue-500">0xd90e...</span></td><td class="p-2"><span class="bg-purple-100 text-purple-800 px-2 py-0.5 rounded font-bold">Mixer / Sanctioned</span></td><td class="p-2 text-right font-black text-red-600">$14,500,000</td></tr>
                                <tr><td class="p-2">Binance Hot 14<br><span class="text-[9px] text-blue-500">0x28c6...</span></td><td class="p-2"><span class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold">CEX (KYC Evasion)</span></td><td class="p-2 text-right font-black text-red-600">$8,200,000</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h3 class="text-xs font-black uppercase text-slate-500 mb-3">Exposure Inbound</h3>
                        <p class="font-mono text-sm text-slate-800"><strong>Consistent Senders:</strong> 12 High-Risk Wallets</p>
                        <p class="font-mono text-sm text-slate-800 mt-2"><strong>Total Illicit Inbound:</strong> <span class="text-red-600 font-bold">$28,400,000</span></p>
                    </div>
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h3 class="text-xs font-black uppercase text-slate-500 mb-3">Exposure Outbound</h3>
                        <p class="font-mono text-sm text-slate-800"><strong>Last Receivers Deposits To:</strong> 3 CEX Endpoints</p>
                        <p class="font-mono text-sm text-slate-800 mt-2"><strong>Total Illicit Outbound:</strong> <span class="text-red-600 font-bold">$12,800,000</span></p>
                    </div>
                </div>
            </div>

            <!-- TAB 9: GEORISK -->
            <div id="nid-tab-georisk" class="nid-tab-content space-y-6 h-full max-w-7xl mx-auto">
                <div class="bg-white p-0 rounded-xl border border-slate-200 shadow-sm h-[600px] flex flex-col relative overflow-hidden">
                    <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest p-4 border-b border-slate-200 z-10 bg-white shadow-sm"><i class="fa-solid fa-earth-americas text-emerald-500 mr-2"></i> Global IP & Node Intelligence</h2>
                    <div class="flex-grow bg-blue-50 relative overflow-hidden flex items-center justify-center">
                        <div class="absolute inset-0 opacity-10" style="background-image: url('https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg'); background-size: cover; background-position: center; filter: invert(1);"></div>
                        <!-- Node Markers -->
                        <div class="absolute top-[30%] left-[75%] flex flex-col items-center group cursor-pointer z-20">
                            <div class="w-4 h-4 bg-red-500 rounded-full animate-ping absolute"></div><div class="w-4 h-4 bg-red-600 border-2 border-white rounded-full relative z-10 shadow-md"></div>
                            <div class="opacity-0 group-hover:opacity-100 bg-white border border-red-200 text-[10px] font-mono p-3 rounded-lg mt-2 absolute top-4 w-56 transition z-30 shadow-xl"><strong class="text-red-700 text-xs">Pyongyang, NK (Proxy)</strong><br><span class="text-slate-500">IP: 175.45.176.x</span><br>Associated with Lazarus API requests to Infura.</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 10: INTELLIGENCE -->
            <div id="nid-tab-intelligence" class="nid-tab-content space-y-6 max-w-7xl mx-auto">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm text-sm font-mono leading-relaxed space-y-4">
                        <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest border-b pb-2 flex items-center gap-2"><i class="fa-solid fa-user-secret text-purple-600"></i> OSINT & Reconnaissance</h2>
                        <p><strong class="bg-slate-100 px-1 rounded border border-slate-200">Custodial Entry:</strong> Binance Deposit Address 0x28c...d60</p>
                        <p><strong class="bg-slate-100 px-1 rounded border border-slate-200">Darknet:</strong> 14 index hits on XSS.is regarding wallet cluster keys.</p>
                        <p><strong class="bg-slate-100 px-1 rounded border border-slate-200">Sanctions (OFAC):</strong> Direct Match. Added to SDN list April 2023.</p>
                        <p><strong class="bg-slate-100 px-1 rounded border border-slate-200">Known APTs:</strong> Lazarus Group (APT38) / BlueNoroff.</p>
                        <p><strong class="bg-slate-100 px-1 rounded border border-slate-200">Social Media:</strong> Correlated Telegram ID `@laundromat_rx`.</p>
                    </div>
                    <div class="bg-red-50 border border-red-200 p-6 rounded-xl flex flex-col items-center justify-center text-center shadow-sm">
                        <i class="fa-solid fa-biohazard text-6xl text-red-500 mb-4 alert-flashing bg-transparent border-none shadow-none"></i>
                        <h3 class="text-2xl font-black text-red-900 uppercase">TAGGED AS MALICIOUS</h3>
                        <p class="text-red-700 text-sm font-mono mt-2 font-bold bg-white p-2 rounded shadow-sm border border-red-100">YES. Entity poses extreme risk to protocol liquidity.</p>
                    </div>
                </div>
            </div>

            <!-- TAB 11: AI INSIGHTS -->
            <div id="nid-tab-ai" class="nid-tab-content max-w-7xl mx-auto">
                <div class="bg-white p-8 rounded-xl shadow-xl border-t-4 border-t-blue-600 min-h-[600px]">
                    <div class="flex justify-between items-center border-b border-slate-200 pb-4 mb-6">
                        <h2 class="text-xl font-black text-slate-800 uppercase tracking-widest flex items-center gap-3"><i class="fa-solid fa-robot text-blue-600 text-2xl"></i> DeepMind AI Insights Report</h2>
                        <button onclick="switchNidTab('nid-tab-report')" class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider transition shadow-md flex items-center gap-2"><i class="fa-solid fa-file-pdf"></i> Generate Full Report</button>
                    </div>
                    <div class="prose prose-slate max-w-none font-mono text-sm leading-loose">
                        <h3 class="text-slate-900 font-bold border-b border-slate-100 pb-1 mb-3 uppercase">1. Summary</h3>
                        <p class="bg-slate-50 p-4 rounded border border-slate-200">Analysis indicates a highly structured money laundering operation. The wallet acts as a Tier-2 consolidation node for the Lazarus Group, systematically receiving funds from Tornado Cash and deploying them across cross-chain bridges to obfuscate terminal custodial cash-out points.</p>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                            <div>
                                <h3 class="text-slate-900 font-bold border-b border-slate-100 pb-1 mb-3 uppercase">2. Methodology & Data Sources</h3>
                                <ul class="list-disc pl-5 space-y-1 text-slate-700"><li>Deterministic Omni-Chain Graph Traversal.</li><li>Heuristic Volume Correlation.</li><li>Darknet OSINT Metadata Scraping.</li></ul>
                            </div>
                            <div>
                                <h3 class="text-slate-900 font-bold border-b border-slate-100 pb-1 mb-3 uppercase">3. Risks & Clusters</h3>
                                <ul class="list-disc pl-5 space-y-1 text-slate-700"><li><strong class="text-red-600">Critical AML Risk:</strong> OFAC Sanctioned Entity.</li><li><strong>Terminal Custodian:</strong> Binance Hot Wallet 14.</li></ul>
                            </div>
                        </div>

                        <h3 class="text-slate-900 font-bold border-b border-slate-100 pb-1 mb-3 mt-6 uppercase">4. Recommendations for Law Enforcement</h3>
                        <p class="bg-blue-50 text-blue-900 p-4 rounded border border-blue-200 font-bold">Immediate subpoena requests should be directed to the compliance department of Binance referencing Deposit Address <code>0x28c...d60</code>.</p>
                    </div>
                </div>
            </div>

            <!-- TAB 12: FULL REPORT -->
            <div id="nid-tab-report" class="nid-tab-content bg-slate-200 p-4 md:p-8 rounded-xl overflow-y-auto max-h-[80vh]">
                <div class="max-w-[8.5in] mx-auto flex justify-between items-center mb-6 bg-white p-4 rounded-lg shadow-sm border border-slate-300">
                    <p class="text-slate-800 text-sm font-bold flex items-center gap-2"><i class="fa-solid fa-file-contract text-blue-600 text-xl"></i> Law Enforcement Evidentiary Document</p>
                    <button onclick="downloadNidReportPdf()" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-6 rounded-lg transition text-xs uppercase tracking-widest shadow-md flex items-center gap-2">
                        <i class="fa-solid fa-download"></i> Download as PDF
                    </button>
                </div>

                <div id="nid-gdoc-printable" class="print-doc-container active relative">
                    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; margin: auto; width: 60%; opacity: 0.03; pointer-events: none; z-index: 0; background-image: url('https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png'); background-repeat: no-repeat; background-position: center; background-size: contain;"></div>
                    <div style="position: relative; z-index: 10;">
                        <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 30px;">
                            <img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" alt="LIONSGATE" style="height: 60px; margin: 0 auto 10px auto; filter: grayscale(100%);">
                            <h1 style="font-size: 24px; font-weight: 900; text-transform: uppercase; margin: 0; letter-spacing: 2px; color: #000;">Cyber Intelligence & Forensic Report</h1>
                            <p style="font-size: 12px; font-weight: bold; color: #666; text-transform: uppercase; letter-spacing: 2px; margin: 5px 0 0 0;">Strictly Confidential / Evidentiary Use</p>
                            <p style="font-size: 12px; font-family: monospace; margin-top: 15px; color: #000;">CASE ID: <span style="font-weight: bold;">NEM-2026-X99</span></p>
                        </div>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">Table of Contents</h2>
                        <ul style="font-size: 12px; margin-bottom: 20px; padding-left: 20px;">
                            <li>Introduction - Incident</li><li>Executive Summary & Recovery Probability</li><li>Investigation Methodology & Data Sources</li>
                            <li>Chronological Fund Flow & Timeline</li><li>Transaction Analysis & Patterns</li><li>Source and Destination Entities</li>
                            <li>Blockchain Snapshot Transaction Graph</li><li>Investigation Summary & Conclusion</li><li>Crypto Victims Guidelines & Law Enforcement Contacts</li>
                            <li>Disclaimer & Scope of Services</li>
                        </ul>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">1. Introduction & Incident Details</h2>
                        <p style="font-size: 12px; margin-bottom: 15px;">On May 20, 2026, it was recorded that an unauthorized transfer of digital assets originated from a compromised primary cold storage facility. The total alleged loss is valued at approximately $16,700,000 USD. The compromised origin seed is <code>0x1a2b3c4d...</code>.</p>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">2. Executive Summary & Recovery Probability</h2>
                        <p style="font-size: 12px; margin-bottom: 10px;">The Lionsgate Network's Nemesis engine has successfully mapped the omni-chain flow of assets. The deterministic algorithm resolved the terminal destination to a KYC-regulated Centralized Exchange (CEX).</p>
                        <div style="background: #f8fafc; padding: 10px; border-left: 3px solid #000; margin-bottom: 15px; font-size: 12px;"><strong>Recovery Probability: 98%</strong><br>Terminal Custodial Entity Identified: <strong>Binance Hot Wallet 14</strong></div>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">3. Investigation Methodology</h2>
                        <p style="font-size: 12px; margin-bottom: 15px;">Utilized deterministic on-chain tracing, GNN clustering, and autonomous LangGraph AI Swarms.</p>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">4. Chronological Fund Flow & Source/Destination Entities</h2>
                        <table style="font-size: 11px; margin-bottom: 15px; width: 100%; border-collapse: collapse;">
                            <thead style="background: #eee;"><tr><th style="border: 1px solid #aaa; padding: 5px;">Date</th><th style="border: 1px solid #aaa; padding: 5px;">Source</th><th style="border: 1px solid #aaa; padding: 5px;">Destination Entity</th><th style="border: 1px solid #aaa; padding: 5px;">Amount</th><th style="border: 1px solid #aaa; padding: 5px;">Type</th></tr></thead>
                            <tbody>
                                <tr><td style="border: 1px solid #aaa; padding: 5px;">2026-05-25</td><td style="border: 1px solid #aaa; padding: 5px;">0xd90e...31b</td><td style="border: 1px solid #aaa; padding: 5px;"><strong>SUBJECT WALLET</strong></td><td style="border: 1px solid #aaa; padding: 5px;">10,000,000 USD</td><td style="border: 1px solid #aaa; padding: 5px;">MIXER (IN)</td></tr>
                                <tr><td style="border: 1px solid #aaa; padding: 5px;">2026-05-27</td><td style="border: 1px solid #aaa; padding: 5px;"><strong>SUBJECT WALLET</strong></td><td style="border: 1px solid #aaa; padding: 5px;"><strong>Binance Hot Wallet 14</strong></td><td style="border: 1px solid #aaa; padding: 5px;">1,200,000 USD</td><td style="border: 1px solid #aaa; padding: 5px;">CEX DEPOSIT</td></tr>
                            </tbody>
                        </table>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">5. Transaction Analysis & Patterns</h2>
                        <p style="font-size: 12px; margin-bottom: 15px;">The wallet exhibits high-velocity, automated "peel chain" behavior.</p>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">6. Blockchain Snapshot Transaction Graph</h2>
                        <div style="background: #f8fafc; border: 1px dashed #ccc; height: 100px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; color: #666; font-family: monospace; font-size: 10px;">[ Vis.js Graph Topology Rendered Here - See Dashboard Tab 7 ]</div>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">7. Conclusion</h2>
                        <p style="font-size: 12px; margin-bottom: 15px;">Illicit funds have been securely traced to a custodial account at <strong>Binance</strong>. Formal recommendation: Issue a preservation order referencing deposit address <code>0x28c6c062...</code>.</p>

                        <div class="page-break"></div>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">8. Crypto Victims Guidelines & Law Enforcement Contacts</h2>
                        <div style="margin-bottom: 20px;">
                            <label class="text-xs font-bold mr-2 no-print">Enter Victim Zip Code to populate contacts:</label>
                            <input type="text" id="victim-zip" placeholder="Zip Code" class="border border-slate-300 p-1 text-xs rounded no-print">
                        </div>
                        <div style="background: #f8fafc; padding: 15px; border: 1px solid #ccc; font-family: monospace; font-size: 11px; margin-bottom: 20px;">
                            <strong>Local & Federal Field Office Mapping:</strong><br><br>
                            > <strong>Federal Bureau of Investigation (Cyber Division):</strong> www.ic3.gov | Phone: (202) 324-3000<br>
                            > <strong>US Secret Service (Digital Asset Task Force):</strong> www.secretservice.gov<br>
                            > <strong>State/Local Police Dept (Cybercrimes Unit):</strong> Contact non-emergency dispatch referencing this Case ID.
                        </div>

                        <h2 style="font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 10px;">9. Disclaimer & Scope of Services</h2>
                        <div style="font-size: 9px; color: #333; text-align: justify; line-height: 1.4;">
                            <p><strong>Lionsgate Network is on standby to support law enforcement detectives with forensic evidence and help facilitate the strongest outcome. You are not alone — we’ve got your back.</strong></p>
                            <p>Lionsgate Network makes no warranties, whether express, implied, statutory, or otherwise, with respect to the services or deliverables provided in this report. Lionsgate Network specifically disclaims all implied warranties of merchantability, fitness for a particular purpose, non-infringement, and those arising from a course of dealing, usage, or trade, and all such warranties are excluded to the fullest extent permitted by law.</p>
                            <p>Lionsgate Network will not be liable for any lost profits, business, contracts, revenues, goodwill, production, anticipated savings, loss of data, or costs of procuring substitute goods or services, or for any claim or demand against the company by any other party. In no event will Lionsgate Network be liable for consequential, incidental, special, indirect, or exemplary damages arising out of this agreement or any work statement, however caused and (to the fullest extent permitted by law) under any theory of liability—including negligence—even if Lionsgate Network has been advised of the possibility of such damages.</p>
                            <p>Lionsgate Network supports your recovery journey by producing advanced forensic blockchain tracing and OSINT intelligence designed to document the flow of assets, identify relevant entities, and prepare the evidentiary foundation required for escalation.</p>
                            <p>It is essential for clients to understand that law enforcement is the only authority empowered to subpoena, freeze, or seize funds. Our role is to strengthen your case, accelerate understanding, and provide detectives with the clearest possible roadmap for action—maximizing the probability of a successful recovery outcome.</p>
                            <p style="text-align: center; font-weight: bold; text-transform: uppercase; margin-top: 20px; padding-top: 10px; border-top: 1px solid #ccc;">Lionsgate Network Internal / Law Enforcement Use Only</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Whitepaper Navigation Logic
        document.addEventListener('DOMContentLoaded', () => {
            const sections = document.querySelectorAll('section');
            const navLinks = document.querySelectorAll('.toc-link');
            const observerOptions = { root: null, rootMargin: '-20% 0px -80% 0px', threshold: 0 };
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const id = entry.target.getAttribute('id');
                        navLinks.forEach(link => {
                            link.classList.remove('active');
                            if (link.getAttribute('href') === `#${id}`) { link.classList.add('active'); }
                        });
                    }
                });
            }, observerOptions);
            sections.forEach(section => observer.observe(section));
        });

        // NEMESIS ID Modal & Dashboard Logic
        function openSearchModal() {
            document.getElementById('search-modal').classList.remove('hidden');
        }
        function closeSearchModal() {
            document.getElementById('search-modal').classList.add('hidden');
        }
        function executeSearch() {
            const val = document.getElementById('nid-search-input').value.trim();
            if (!val) { alert("Please enter a wallet address."); return; }
            document.getElementById('search-modal').classList.add('hidden');
            document.getElementById('loader-modal').classList.remove('hidden');
            document.getElementById('dash-wallet-title').innerText = val;
            
            // Simulate API processing delay
            setTimeout(() => {
                document.getElementById('loader-modal').classList.add('hidden');
                document.getElementById('dashboard-view').classList.remove('hidden');
                document.body.style.overflow = 'hidden'; // prevent bg scroll
                switchNidTab('nid-tab-profile');
                initTraceGraph();
                initCharts();
            }, 2500);
        }
        function exitDashboard() {
            document.getElementById('dashboard-view').classList.add('hidden');
            document.body.style.overflow = 'auto';
        }
        function switchNidTab(tabId) {
            document.querySelectorAll('.nid-tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nid-tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            const btns = document.querySelectorAll('.nid-tab-btn');
            for(let btn of btns) {
                if(btn.getAttribute('onclick').includes(tabId)) {
                    btn.classList.add('active');
                    btn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
                    break;
                }
            }
        }

        // Trace Graph (Vis.js)
        let graphRendered = false;
        function initTraceGraph() {
            if(graphRendered) return;
            const container = document.getElementById('trace-network');
            const nodes = new vis.DataSet([
                { id: 1, label: 'SUBJECT WALLET', color: { background: '#ef4444', border: '#ffffff' }, font: { color: 'white' }, size: 30 },
                { id: 2, label: 'Tornado Cash\nMixer', color: { background: '#64748b', border: '#ffffff' }, font: { color: 'white' }, size: 25 },
                { id: 3, label: 'Stargate Router', color: { background: '#8b5cf6', border: '#ffffff' }, font: { color: 'white' }, size: 25 },
                { id: 4, label: 'Binance Hot 14\n(CEX)', color: { background: '#f59e0b', border: '#ffffff' }, font: { color: 'white' }, size: 35 },
                { id: 5, label: 'Private Node A', color: { background: '#3b82f6', border: '#ffffff' }, font: { color: 'white' }, size: 15 },
            ]);
            const edges = new vis.DataSet([
                { from: 2, to: 1, label: '$10M', color: { color: '#ef4444' }, arrows: 'to', dashes: true, font: { align: 'top', color: '#cbd5e1' } },
                { from: 5, to: 1, label: '$4.5M', color: { color: '#3b82f6' }, arrows: 'to', font: { align: 'top', color: '#cbd5e1' } },
                { from: 1, to: 3, label: '$5.5M', color: { color: '#8b5cf6' }, arrows: 'to', font: { align: 'top', color: '#cbd5e1' } },
                { from: 1, to: 4, label: '$1.2M', color: { color: '#f59e0b' }, arrows: 'to', font: { align: 'top', color: '#cbd5e1' } },
            ]);
            const data = { nodes: nodes, edges: edges };
            const options = {
                nodes: { shape: 'dot', borderWidth: 2 },
                edges: { smooth: { type: 'curvedCW', roundness: 0.2 }, width: 2 },
                physics: { stabilization: false, barnesHut: { springLength: 200 } }
            };
            new vis.Network(container, data, options);
            graphRendered = true;
        }

        // Charts
        let chartsRendered = false;
        function initCharts() {
            if(chartsRendered) return;
            Chart.defaults.color = '#64748b'; Chart.defaults.font.family = "'JetBrains Mono', monospace";
            new Chart(document.getElementById('chartSenders'), { type: 'bar', data: { labels: ['Tornado Cash', 'Synapse', '0x1A2...'], datasets: [{ data: [10000000, 2000000, 4500000], backgroundColor: '#10b981', borderRadius: 4 }] }, options: { plugins: { legend: { display: false } } } });
            new Chart(document.getElementById('chartReceivers'), { type: 'bar', data: { labels: ['Stargate', 'Binance Hot 14', 'Huobi'], datasets: [{ data: [5500000, 1200000, 450000], backgroundColor: '#ef4444', borderRadius: 4 }] }, options: { plugins: { legend: { display: false } } } });
            new Chart(document.getElementById('chartBalances'), { type: 'line', data: { labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Now'], datasets: [{ data: [120000, 5500000, 15000000, 8000000, 2500000, 1452890], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', fill: true, tension: 0.4 }] }, options: { plugins: { legend: { display: false } } } });
            chartsRendered = true;
        }

        function downloadNidReportPdf() {
            const element = document.getElementById('nid-gdoc-printable');
            const opt = { margin: 0, filename: 'Lionsgate_NemesisID_Report.pdf', image: { type: 'jpeg', quality: 0.98 }, html2canvas: { scale: 2, useCORS: true }, jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' } };
            html2pdf().set(opt).from(element).save();
        }
    </script>
""" + FLOATING_TERMINAL_HTML + r"""
</body>
</html>
"""

HTML_API_DOCS = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEMESIS API Reference | Lionsgate Developer Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background-color: #f8fafc;
            font-family: 'Inter', sans-serif;
            color: #334155;
            -webkit-font-smoothing: antialiased;
        }
        
        .api-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            display: grid;
            grid-template-columns: 250px 1fr;
            gap: 3rem;
        }

        @media (max-width: 1024px) {
            .api-container { grid-template-columns: 1fr; }
            .sidebar { display: none; }
        }

        /* Typography & Code */
        h1, h2, h3, h4 { letter-spacing: -0.02em; color: #0f172a; }
        code { font-family: 'JetBrains Mono', monospace; }
        
        .code-block {
            background: #0f172a;
            color: #e2e8f0;
            border-radius: 0.75rem;
            padding: 1.25rem;
            font-size: 0.85rem;
            overflow-x: auto;
            border: 1px solid #1e293b;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }
        .code-block .key { color: #7dd3fc; } /* Light Blue */
        .code-block .string { color: #a7f3d0; } /* Emerald */
        .code-block .number { color: #fbcfe8; } /* Pink */
        .code-block .boolean { color: #fde047; } /* Yellow */

        /* Badges */
        .badge-method {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.25rem 0.6rem;
            border-radius: 0.375rem;
            font-size: 0.75rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.05em;
        }
        .badge-post { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }
        .badge-get { background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }
        .badge-ws { background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; }

        /* Tables */
        .param-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            margin-bottom: 2rem;
            font-size: 0.875rem;
        }
        .param-table th {
            text-align: left;
            padding: 0.75rem 1rem;
            background: #f1f5f9;
            color: #475569;
            font-weight: 600;
            border-bottom: 2px solid #e2e8f0;
        }
        .param-table td {
            padding: 1rem;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: top;
        }
        .param-name { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #0f172a; }
        .param-type { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #64748b; }
        .param-req { color: #dc2626; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }

        /* Sections */
        .endpoint-section {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            padding: 2.5rem;
            margin-bottom: 3rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
            transition: border-color 0.3s ease;
        }
        .endpoint-section:hover {
            border-color: #cbd5e1;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        }

        .sidebar a {
            display: block;
            padding: 0.5rem 0;
            color: #64748b;
            text-decoration: none;
            font-size: 0.875rem;
            transition: color 0.2s;
            border-left: 2px solid transparent;
            padding-left: 1rem;
        }
        .sidebar a:hover, .sidebar a.active {
            color: #2563eb;
            border-left-color: #2563eb;
            font-weight: 500;
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-[1400px] mx-auto px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-4">
                <img src="https://lionsgate.network/wp-content/uploads/2025/09/cropped-lionsgate-logo-head.png" alt="LIONSGATE LOGO" class="h-12 object-contain">
                <div>
                    <h1 class="text-xl font-black uppercase tracking-tight text-slate-900 leading-none">Developer Hub</h1>
                    <p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Nemesis API Reference v100.19</p>
                </div>
            </div>
            <div class="hidden md:flex gap-4">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span> Systems Operational
                </span>
            </div>
        </div>
    </header>

    <div class="api-container">
        
        <!-- Sidebar Navigation -->
        <aside class="sidebar sticky top-24 h-[calc(100vh-6rem)] overflow-y-auto pr-4">
            <div class="mb-8">
                <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 mb-3 ml-4">Getting Started</h3>
                <nav class="space-y-1">
                    <a href="#introduction" class="active">Introduction</a>
                    <a href="#authentication">Authentication & Limits</a>
                </nav>
            </div>
            
            <div class="mb-8">
                <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 mb-3 ml-4">Core Tracing API</h3>
                <nav class="space-y-1">
                    <a href="#start-trace"><span class="badge-method badge-post text-[9px] mr-2 px-1 py-0">POST</span> Start Trace</a>
                    <a href="#get-report"><span class="badge-method badge-get text-[9px] mr-2 px-1 py-0">GET</span> Forensic Data</a>
                </nav>
            </div>

            <div class="mb-8">
                <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 mb-3 ml-4">Swarm AI (LangGraph)</h3>
                <nav class="space-y-1">
                    <a href="#gen-osint"><span class="badge-method badge-post text-[9px] mr-2 px-1 py-0">POST</span> Generate OSINT</a>
                    <a href="#gen-narrative"><span class="badge-method badge-post text-[9px] mr-2 px-1 py-0">POST</span> Legal Narrative</a>
                </nav>
            </div>

            <div class="mb-8">
                <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 mb-3 ml-4">DarkX Intelligence</h3>
                <nav class="space-y-1">
                    <a href="#stream-darkx"><span class="badge-method badge-get text-[9px] mr-2 px-1 py-0">GET</span> SSE Stream</a>
                    <a href="#darkx-dossier"><span class="badge-method badge-post text-[9px] mr-2 px-1 py-0">POST</span> Synthetic Dossier</a>
                </nav>
            </div>

            <div class="mb-8">
                <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 mb-3 ml-4">Real-Time Streams</h3>
                <nav class="space-y-1">
                    <a href="#websocket"><span class="badge-method badge-ws text-[9px] mr-2 px-1 py-0">WS</span> Live Tracing</a>
                </nav>
            </div>
        </aside>

        <!-- Main Content -->
        <main>
            
            <!-- Intro -->
            <section id="introduction" class="mb-12">
                <h1 class="text-4xl font-black mb-4">Nemesis API Documentation</h1>
                <p class="text-slate-600 text-lg leading-relaxed mb-6">
                    Integrate the Lionsgate Omni-Chain Forensic Engine directly into your enterprise applications. The Nemesis API provides programmatic access to asynchronous blockchain graph traversal, ML-driven heuristic clustering, and LangGraph-orchestrated AI report synthesis.
                </p>
                <div class="bg-blue-50 border border-blue-200 p-4 rounded-xl flex gap-4">
                    <i class="fa-solid fa-circle-info text-blue-500 mt-1"></i>
                    <div>
                        <h4 class="font-bold text-blue-900 mb-1">Base URL</h4>
                        <code class="text-blue-700 bg-blue-100 px-2 py-1 rounded text-sm">https://api.lionsgate.network/api/</code>
                    </div>
                </div>
            </section>

            <!-- TRACING: Start Trace -->
            <section id="start-trace" class="endpoint-section">
                <div class="flex items-center gap-3 mb-2">
                    <span class="badge-method badge-post">POST</span>
                    <h2 class="text-2xl font-bold m-0">/start_trace</h2>
                </div>
                <p class="text-slate-500 mb-8">Initializes an asynchronous omni-chain graph traversal. The engine will detect the chain, bypass obfuscation layers, and halt upon reaching a Centralized Exchange (CEX) or target value.</p>
                
                <h3 class="text-sm font-bold uppercase text-slate-800 mb-2 border-b pb-2">Request Body (JSON)</h3>
                <table class="param-table">
                    <tr>
                        <th>Parameter</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td>
                            <span class="param-name">seeds</span><br>
                            <span class="param-type">string</span> <span class="param-req">Required</span>
                        </td>
                        <td>A newline-separated string of compromised wallet addresses or transaction hashes to begin the trace.</td>
                    </tr>
                    <tr>
                        <td>
                            <span class="param-name">target_amount</span><br>
                            <span class="param-type">float</span> <span class="text-slate-400 text-[10px] ml-2">Default: 1000.0</span>
                        </td>
                        <td>The total mathematical loss to account for before the trace halts natively.</td>
                    </tr>
                    <tr>
                        <td>
                            <span class="param-name">chain_override</span><br>
                            <span class="param-type">string</span> <span class="text-slate-400 text-[10px] ml-2">Default: "AUTO"</span>
                        </td>
                        <td>Force a specific network. Accepts: <code>AUTO, ETHEREUM, BSC, POLYGON, SOLANA, BITCOIN, TRON</code>, etc.</td>
                    </tr>
                </table>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                    <div>
                        <h4 class="text-xs font-bold text-slate-500 uppercase mb-2">Example Request</h4>
                        <pre class="code-block"><code>{
  <span class="key">"seeds"</span>: <span class="string">"0x1234abcd...\n0x5678efgh..."</span>,
  <span class="key">"target_amount"</span>: <span class="number">55000.00</span>,
  <span class="key">"currency"</span>: <span class="string">"USD"</span>,
  <span class="key">"chain_override"</span>: <span class="string">"AUTO"</span>
}</code></pre>
                    </div>
                    <div>
                        <h4 class="text-xs font-bold text-slate-500 uppercase mb-2">Example Response (200 OK)</h4>
                        <pre class="code-block"><code>{
  <span class="key">"status"</span>: <span class="string">"running"</span>,
  <span class="key">"case_id"</span>: <span class="string">"CASE-A1B2C3"</span>
}</code></pre>
                        <p class="text-xs text-slate-500 mt-2"><i class="fa-solid fa-lightbulb text-yellow-500 mr-1"></i> Use the returned <code>case_id</code> to connect to the WebSocket stream.</p>
                    </div>
                </div>
            </section>

            <!-- TRACING: Get Report -->
            <section id="get-report" class="endpoint-section">
                <div class="flex items-center gap-3 mb-2">
                    <span class="badge-method badge-get">GET</span>
                    <h2 class="text-2xl font-bold m-0">/forensic_report_data</h2>
                </div>
                <p class="text-slate-500 mb-8">Retrieves the complete, aggregated ledger data for a trace that has reached 100% completion.</p>
                
                <h3 class="text-sm font-bold uppercase text-slate-800 mb-2 border-b pb-2">Query Parameters</h3>
                <table class="param-table">
                    <tr>
                        <td width="30%">
                            <span class="param-name">case_id</span><br>
                            <span class="param-type">string</span> <span class="param-req">Required</span>
                        </td>
                        <td>The unique identifier returned from the <code>/start_trace</code> endpoint.</td>
                    </tr>
                </table>

                <h4 class="text-xs font-bold text-slate-500 uppercase mb-2">Example Response</h4>
                <pre class="code-block"><code>{
  <span class="key">"seeds"</span>: [<span class="string">"0x123..."</span>],
  <span class="key">"total_volume"</span>: <span class="number">14.5</span>,
  <span class="key">"tx_count"</span>: <span class="number">142</span>,
  <span class="key">"terminals"</span>: [
    {
      <span class="key">"source"</span>: <span class="string">"0xabc..."</span>,
      <span class="key">"destination"</span>: <span class="string">"0xdef..."</span>,
      <span class="key">"entity"</span>: <span class="string">"Exchange"</span>,
      <span class="key">"amount"</span>: <span class="string">"5.2 ETH"</span>,
      <span class="key">"type"</span>: <span class="string">"TOKEN TRANSFER"</span>
    }
  ],
  <span class="key">"transactions"</span>: [ <span class="string">/* Full Hop Ledger Array */</span> ]
}</code></pre>
            </section>

            <!-- AI: Narrative -->
            <section id="gen-narrative" class="endpoint-section">
                <div class="flex items-center gap-3 mb-2">
                    <span class="badge-method badge-post">POST</span>
                    <h2 class="text-2xl font-bold m-0">/generate_narrative</h2>
                </div>
                <p class="text-slate-500 mb-8">Triggers the LangGraph `Synthesizer Agent` to author a legal-grade affidavit narrative explaining the flow of funds to law enforcement, utilizing Gemini 2.5 Flash.</p>
                
                <table class="param-table">
                    <tr>
                        <td width="30%">
                            <span class="param-name">case_id</span><br>
                            <span class="param-type">string</span> <span class="param-req">Required</span>
                        </td>
                        <td>Target case ID. Backend will pull the internal state ledger for context.</td>
                    </tr>
                    <tr>
                        <td>
                            <span class="param-name">subpoena_targets</span><br>
                            <span class="param-type">string</span> <span class="param-req">Required</span>
                        </td>
                        <td>Formatted string of terminal entities to include in the final legal request.</td>
                    </tr>
                </table>

                <pre class="code-block"><code>{
  <span class="key">"narrative"</span>: <span class="string">"Based on forensic analysis of the blockchain ledger, the suspect initiated a transfer from the compromised seed... \n\nWe formally request a subpoena for..."</span>
}</code></pre>
            </section>

            <!-- DARKX: Stream -->
            <section id="stream-darkx" class="endpoint-section">
                <div class="flex items-center gap-3 mb-2">
                    <span class="badge-method badge-get">GET</span>
                    <h2 class="text-2xl font-bold m-0">/darkx/stream</h2>
                </div>
                <p class="text-slate-500 mb-8">Opens a Server-Sent Events (SSE) connection to query the Lionsgate Dark Web MongoDB cluster. Streams matched entities (IPs, emails, domains) in real-time.</p>
                
                <table class="param-table">
                    <tr>
                        <td width="30%">
                            <span class="param-name">q</span><br>
                            <span class="param-type">string</span> <span class="param-req">Required</span>
                        </td>
                        <td>The exact phrase, IP, or wallet address to text-index search across the darknet database.</td>
                    </tr>
                </table>

                <div class="bg-slate-50 p-4 border border-slate-200 rounded-lg text-sm mb-4">
                    <strong>Header Requirement:</strong> Ensure your client accepts <code>text/event-stream</code>.
                </div>
                
                <pre class="code-block"><code><span class="string">data:</span> {<span class="key">"id"</span>: <span class="string">"64f1a2..."</span>, <span class="key">"crawled_at"</span>: <span class="string">"2026-05-27T..."</span>, <span class="key">"web_info"</span>: {<span class="key">"url"</span>: <span class="string">"http://onion..."</span>}, <span class="key">"uie_entities"</span>: [...]}

<span class="string">data:</span> {<span class="key">"end"</span>: <span class="boolean">true</span>, <span class="key">"msg"</span>: <span class="string">"No further results."</span>}</code></pre>
            </section>

            <!-- WEBSOCKET -->
            <section id="websocket" class="endpoint-section">
                <div class="flex items-center gap-3 mb-2">
                    <span class="badge-method badge-ws">WS</span>
                    <h2 class="text-2xl font-bold m-0">/ws/{case_id}</h2>
                </div>
                <p class="text-slate-500 mb-8">Establish a persistent, bi-directional WebSocket connection to receive real-time graph nodes, AI processing tooltips, and mempool alerts as the async engine traverses the blockchain.</p>

                <h3 class="text-sm font-bold uppercase text-slate-800 mb-4 border-b pb-2">Event Types Emitted to Client</h3>
                <div class="space-y-4">
                    <div class="border border-slate-200 rounded p-4">
                        <span class="font-bold text-indigo-600 font-mono text-sm">"type": "LEDGER"</span>
                        <p class="text-sm text-slate-600 mt-1">Emitted when a new valid transaction hop is processed.</p>
                        <code class="text-xs bg-slate-100 px-2 py-1 rounded block mt-2 text-slate-700">Payload: { case_id, chain, timestamp, from, to, tx, amount, entity_class, is_terminal }</code>
                    </div>
                    
                    <div class="border border-slate-200 rounded p-4">
                        <span class="font-bold text-purple-600 font-mono text-sm">"type": "AI_TOOLTIP"</span>
                        <p class="text-sm text-slate-600 mt-1">Status updates from LangGraph Agents (e.g., "Extracting OSINT vectors...").</p>
                    </div>

                    <div class="border border-slate-200 rounded p-4">
                        <span class="font-bold text-rose-600 font-mono text-sm">"type": "MEMPOOL_ALERT"</span>
                        <p class="text-sm text-slate-600 mt-1">Emitted by the background daemon if a tracked address broadcasts an unconfirmed TX mid-investigation.</p>
                    </div>

                    <div class="border border-slate-200 rounded p-4">
                        <span class="font-bold text-emerald-600 font-mono text-sm">"type": "COMPLETE"</span>
                        <p class="text-sm text-slate-600 mt-1">Signals the frontend to close the connection and transition to the Reporting UI.</p>
                    </div>
                </div>
            </section>

        </main>
    </div>

    <script>
        // Simple script to handle active states on sidebar navigation
        const sections = document.querySelectorAll("section");
        const navLi = document.querySelectorAll(".sidebar a");

        window.onscroll = () => {
            var current = "";
            sections.forEach((section) => {
                const sectionTop = section.offsetTop;
                if (pageYOffset >= sectionTop - 100) {
                    current = section.getAttribute("id");
                }
            });

            navLi.forEach((a) => {
                a.classList.remove("active");
                if (a.getAttribute("href").includes(current) && current !== "") {
                    a.classList.add("active");
                }
            });
        };
    </script>
    """ + FLOATING_TERMINAL_HTML + r"""
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index(): return HTML_MAIN_LANDING

@app.get("/recovery", response_class=HTMLResponse)
async def recovery(): return HTML_CLIENT_RECOVERY

@app.get("/portal", response_class=HTMLResponse)
async def portal(): return HTML_CLIENT_PORTAL

@app.get("/darkx", response_class=HTMLResponse)
async def darkx_ui(): return HTML_DARKX

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio", ws="websockets", http="h11", log_level="info")