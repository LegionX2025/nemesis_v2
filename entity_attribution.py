"""
Entity Attribution Engine
Aggregates OSINT, Heuristics, and On-Chain Identity to form a unified entity profile.
"""
from typing import Dict, Any, List
import logging
from aml_engine import AMLEngine, RiskProfile
from gbio_ontology import GBIONormalizer

logger = logging.getLogger(__name__)

class AttributionEngine:
    @staticmethod
    def generate_entity_dossier(address: str, chain: str, historical_txs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a comprehensive dossier for an entity.
        """
        addr_lower = address.lower()
        
        # 1. AML Risk Profiling
        risk_profile = AMLEngine.analyze_node_risk(addr_lower, chain, historical_txs)
        
        # 2. Heuristics & GBIO
        # Usually we would call HeuristicsEngine and OSINT here.
        gbio_node = GBIONormalizer.normalize_entity(addr_lower, chain, "Wallet")
        if risk_profile.is_sanctioned:
            gbio_node.threat_level = gbio_node.threat_level.SANCTIONED
        elif risk_profile.risk_score > 75:
            gbio_node.threat_level = gbio_node.threat_level.CRITICAL
            
        return {
            "entity_id": f"{chain}_{addr_lower}",
            "address": addr_lower,
            "chain": chain,
            "gbio_class": gbio_node.entity_class.value,
            "threat_level": gbio_node.threat_level.name,
            "risk_score": risk_profile.risk_score,
            "aml_flags": risk_profile.flags,
            "is_sanctioned": risk_profile.is_sanctioned,
            "cluster_id": None # Populated by ML clustering later
        }
