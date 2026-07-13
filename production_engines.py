import logging

logger = logging.getLogger("PRODUCTION_ENGINES_SHIM")

# Compatibility Shim: Re-exporting engines from their new modular domains.
from services.blockchain.engines import UniversalDecoder, TransferAnalyzer, WalletClassifier
from services.graph.engines import GraphIntelligence, ClusterEngine
from services.intelligence.engines import (
    AttributionEngine, HeuristicEngine, BehaviorEngine, 
    TemporalEngine, MixerDetector, BridgeDetector
)
from services.risk.engines import RiskEngine, SanctionEngine

# Ensure all classes are exported to prevent ImportErrors
__all__ = [
    "UniversalDecoder", "TransferAnalyzer", "WalletClassifier",
    "GraphIntelligence", "ClusterEngine",
    "AttributionEngine", "HeuristicEngine", "BehaviorEngine",
    "TemporalEngine", "MixerDetector", "BridgeDetector",
    "RiskEngine", "SanctionEngine"
]
