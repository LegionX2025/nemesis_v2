"""
Universal Decoder & Protocol Fingerprinting Engine
Automatically resolves ABIs, decodes calldata and logs, and fingerprints smart contracts.
"""
import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ABICache:
    """In-memory cache for ABIs to prevent rate-limiting"""
    _cache: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def get(cls, address: str, chain: str) -> Optional[Dict[str, Any]]:
        return cls._cache.get(f"{chain}_{address}")
        
    @classmethod
    def set(cls, address: str, chain: str, abi: Dict[str, Any]):
        cls._cache[f"{chain}_{address}"] = abi

class ProtocolFingerprint:
    """
    Fingerprints unknown smart contracts based on behavior, known selectors, and bytecode layout.
    """
    
    KNOWN_ROUTERS = {
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": "Uniswap V2 Router",
        "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45": "Uniswap V3 Router",
        "0x1111111254fb6c44bac0bed2854e76f90643097d": "1inch v4 Router",
        "0xdef1c0ded9bec7f1a1670819833240f027b25eff": "0x Exchange Proxy"
    }
    
    KNOWN_BRIDGES = {
        "0x401F6c983eA34274ec46f84D70b31C151321188b": "Polygon PoS Bridge",
        "0x99c9fc46f92e8a1c0dec1b1747d010903e884be1": "Optimism Gateway"
    }

    @staticmethod
    def identify_protocol(address: str, chain: str) -> str:
        addr_lower = address.lower()
        if addr_lower in ProtocolFingerprint.KNOWN_ROUTERS:
            return ProtocolFingerprint.KNOWN_ROUTERS[addr_lower]
        if addr_lower in ProtocolFingerprint.KNOWN_BRIDGES:
            return ProtocolFingerprint.KNOWN_BRIDGES[addr_lower]
            
        # Fallback for unknown protocols (will be enhanced by AI/OSINT later)
        return "Unknown Smart Contract"

class UniversalDecoder:
    """
    Core engine for decoding arbitrary transaction payloads across multiple chains.
    """
    
    @staticmethod
    async def fetch_abi(session: Any, address: str, chain: str) -> Optional[Dict[str, Any]]:
        # This function would normally use Etherscan/Basescan API keys from Config
        cached = ABICache.get(address, chain)
        if cached:
            return cached
            
        # Example API endpoint logic (mocked for safety in this iteration)
        # We simulate a delay to represent network fetch
        await asyncio.sleep(0.1)
        
        # In production, we'd do:
        # url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={Config.ETHERSCAN_API_KEY}"
        # async with session.get(url) as r: ...
        
        return None
        
    @staticmethod
    def decode_calldata(calldata: str, abi: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Decodes the 0x hex calldata into function name and parameters.
        """
        if not calldata or calldata == "0x":
            return {"type": "native_transfer"}
            
        # For standard ERC20 transfers, the selector is 0xa9059cbb
        if calldata.startswith("0xa9059cbb"):
            return {"type": "erc20_transfer", "raw": calldata}
            
        # For standard ERC20 approvals, the selector is 0x095ea7b3
        if calldata.startswith("0x095ea7b3"):
            return {"type": "erc20_approve", "raw": calldata}
            
        return {"type": "complex_contract_call", "selector": calldata[:10], "raw": calldata}
        
    @staticmethod
    async def process_transaction(session: Any, tx_data: Dict[str, Any], chain: str) -> Dict[str, Any]:
        """
        Takes a raw transaction dictionary, fingerprints the protocol, and decodes the calldata.
        """
        to_addr = tx_data.get("to", "")
        calldata = tx_data.get("input", "0x")
        
        if not to_addr:
            return {"protocol": "Contract Creation", "decoded": {"type": "contract_creation"}}
            
        protocol = ProtocolFingerprint.identify_protocol(to_addr, chain)
        abi = await UniversalDecoder.fetch_abi(session, to_addr, chain)
        
        decoded = UniversalDecoder.decode_calldata(calldata, abi)
        
        return {
            "protocol": protocol,
            "decoded": decoded,
            "has_abi": bool(abi)
        }
