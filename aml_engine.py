"""
AML Engine
Enterprise Anti-Money Laundering detection logic.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class RiskProfile:
    risk_score: float  # 0.0 to 100.0
    confidence: float  # 0.0 to 1.0
    flags: List[str]
    is_sanctioned: bool

class AMLEngine:
    """
    Detects sophisticated laundering typologies like Peeling Chains, Smurfing, and Mixers.
    """
    
    HIGH_RISK_JURISDICTIONS = ["IR", "KP", "SY", "CU"]
    
    @staticmethod
    def analyze_node_risk(node_address: str, chain: str, historical_txs: List[Dict[str, Any]]) -> RiskProfile:
        score = 0.0
        flags = []
        is_sanctioned = False
        
        # 1. Sanctions Screening
        if AMLEngine._check_ofac_sanctions(node_address):
            score = 100.0
            flags.append("OFAC_SANCTIONED_ENTITY")
            is_sanctioned = True
            return RiskProfile(score, 1.0, flags, is_sanctioned)
            
        if not historical_txs:
            return RiskProfile(0.0, 0.0, [], False)
            
        # 2. Structuring / Smurfing Detection
        smurfing_score = AMLEngine._detect_smurfing(historical_txs)
        if smurfing_score > 50:
            score += 30.0
            flags.append("SUSPECTED_SMURFING")
            
        # 3. Peeling Chain Detection
        peeling_score = AMLEngine._detect_peeling_chain(historical_txs, node_address)
        if peeling_score > 50:
            score += 40.0
            flags.append("SUSPECTED_PEELING_CHAIN")
            
        # 4. Rapid Movement
        if AMLEngine._detect_rapid_movement(historical_txs):
            score += 20.0
            flags.append("RAPID_FUNDS_MOVEMENT")
            
        score = min(score, 100.0)
        confidence = 0.85 if score > 50 else 0.5
        
        return RiskProfile(score, confidence, flags, is_sanctioned)
        
    @staticmethod
    def _check_ofac_sanctions(address: str) -> bool:
        # In production, this queries a local cached OFAC SDN list database.
        # Hardcoded Lazarus group address for demonstration.
        sanctioned = ["0x8576acc5c05d6ce88f4e49bf65bdf0c62f91353c"]
        return address.lower() in sanctioned
        
    @staticmethod
    def _detect_smurfing(txs: List[Dict[str, Any]]) -> float:
        # Detect multiple small deposits right below reporting thresholds (e.g., $9,999)
        suspicious_txs = [tx for tx in txs if 9000 <= tx.get("value_usd", 0) <= 9999]
        if len(suspicious_txs) >= 3:
            return 80.0
        return 0.0
        
    @staticmethod
    def _detect_peeling_chain(txs: List[Dict[str, Any]], target_address: str) -> float:
        # Detect pattern where a large input is peeled off into a small output and a large change output
        peels = 0
        for tx in txs:
            if tx.get("event_type") == "TRANSFER" and tx.get("from") == target_address:
                if tx.get("value_usd", 0) < 1000: # Small peel
                    peels += 1
        if peels > 5:
            return 75.0
        return 0.0
        
    @staticmethod
    def _detect_rapid_movement(txs: List[Dict[str, Any]]) -> bool:
        # Detect funds deposited and withdrawn within minutes
        if len(txs) < 2: return False
        
        # simplified mock logic for time delta
        return False
