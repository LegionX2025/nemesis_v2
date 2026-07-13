import os
import random
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

logger = logging.getLogger("NEMESIS_ROTATOR")

class OmniRotator:
    """
    Dynamic API Auto-Indexer and Fallback Rotator.
    Indexes .env on startup, maps providers to chains, and rotates keys.
    """
    def __init__(self):
        load_dotenv()
        self.llm_keys: Dict[str, List[str]] = {
            "gemini": [],
            "deepseek": [],
            "chatgpt": [],
            "bagoodex": [],
            "llama": []
        }
        self.rpc_endpoints: Dict[str, List[str]] = {
            "ethereum": [],
            "bsc": [],
            "polygon": [],
            "arbitrum": [],
            "optimism": [],
            "base": [],
            "solana": [],
            "avalanche": [],
            "linea": [],
            "celo": [],
            "zksync": [],
            "starknet": []
        }
        self.explorers: Dict[str, List[str]] = {}
        self._auto_index()

    def _auto_index(self):
        # 1. Index LLM Keys
        gemini_keys = os.getenv("VITE_GEMINI_API_KEYS", "")
        if gemini_keys:
            self.llm_keys["gemini"] = [k.strip() for k in gemini_keys.split(",")]
        
        # Additional single LLMs
        for provider in ["deepseek", "chatgpt", "bagoodex", "llama"]:
            key = os.getenv(f"VITE_AIML_API_KEY_{provider.upper()}")
            if key:
                self.llm_keys[provider].append(key)
                
        # 2. Index Multi-chain RPCs (Infura, Ankr, Tatum, PublicNode)
        infura_key = os.getenv("VITE_INFURA_API_KEY")
        ankr_rpc = os.getenv("VITE_ANKR_MULTICHAIN_RPC")
        
        chains = ["ethereum", "bsc", "polygon", "arbitrum", "optimism", "base", "avalanche", "linea", "celo", "zksync", "starknet"]
        for chain in chains:
            # Infura specifically listed in env
            infura_chain_url = os.getenv(f"VITE_INFURA_{chain.upper()}_MAINNET")
            if infura_chain_url:
                self.rpc_endpoints[chain].append(infura_chain_url)
            elif infura_key:
                # Construct default infura if key exists
                pass # skipping explicit construct to avoid bad endpoints

            if ankr_rpc:
                self.rpc_endpoints[chain].append(ankr_rpc)
                
        # 3. Explorers
        for chain in chains:
            explorer_key = os.getenv(f"VITE_{chain.upper()[:4]}SCAN_API_KEY") or os.getenv(f"VITE_{chain.upper()}SCAN_API_KEY")
            if explorer_key:
                if chain not in self.explorers: self.explorers[chain] = []
                self.explorers[chain].append(explorer_key)

        logger.info(f"[OmniRotator] Indexed {sum(len(v) for v in self.llm_keys.values())} LLM keys and {sum(len(v) for v in self.rpc_endpoints.values())} RPC endpoints.")

    def get_llm_key(self, provider: str = "gemini") -> Optional[str]:
        keys = self.llm_keys.get(provider.lower(), [])
        if keys:
            # Return random for rotation
            return random.choice(keys)
        # Fallback logic
        for fb_provider in ["gemini", "deepseek", "chatgpt"]:
            if self.llm_keys.get(fb_provider):
                return random.choice(self.llm_keys[fb_provider])
        return None

    def get_rpc(self, chain: str) -> Optional[str]:
        endpoints = self.rpc_endpoints.get(chain.lower(), [])
        if endpoints:
            return random.choice(endpoints)
        return None

    def get_explorer_key(self, chain: str) -> Optional[str]:
        keys = self.explorers.get(chain.lower(), [])
        if keys:
            return random.choice(keys)
        return os.getenv("VITE_ETHERSCAN_API_KEY") # Shared fallback

# Global instance
rotator = OmniRotator()
