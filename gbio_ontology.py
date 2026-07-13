from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime

class TransferAction(Enum):
    SENT_TO = "SENT_TO"
    SWAPPED_TO = "SWAPPED_TO"
    MINTED = "MINTED"
    BRIDGED_TO = "BRIDGED_TO"

class EntityClass(Enum):
    UNKNOWN = "UNKNOWN"
    EOA_WALLET = "EOA_WALLET"
    SMART_CONTRACT = "SMART_CONTRACT"
    CEX_DEPOSIT = "CEX_DEPOSIT"
    MIXER = "MIXER"

class BlockchainNetwork(Enum):
    UNKNOWN = "UNKNOWN"
    ETHEREUM = "ETHEREUM"
    BSC = "BSC"
    POLYGON = "POLYGON"
    AVALANCHE = "AVALANCHE"
    ARBITRUM = "ARBITRUM"
    OPTIMISM = "OPTIMISM"
    BASE = "BASE"
    LINEA = "LINEA"
    CELO = "CELO"
    BITCOIN = "BITCOIN"

class ThreatLevel(Enum):
    UNKNOWN = "UNKNOWN"
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"
    SANCTIONED = "SANCTIONED"

class EvidenceRecord:
    def __init__(self, source_provider: str, transaction_hash: str, raw_payload: Dict, confidence_score: float):
        self.source_provider = source_provider
        self.transaction_hash = transaction_hash
        self.raw_payload = raw_payload
        self.confidence_score = confidence_score

class RiskProfile:
    def __init__(self, threat_level: ThreatLevel = ThreatLevel.UNKNOWN):
        self.threat_level = threat_level

class BehavioralIndicator(Enum):
    PEEL_CHAIN = "PEEL_CHAIN"
    FAN_OUT = "FAN_OUT"

class AMLFlag(Enum):
    DARKNET = "DARKNET"
    SCAM = "SCAM"

class GBIONode:
    def __init__(self, identifier: str, network: BlockchainNetwork):
        self.identifier = identifier
        self.network = network
        self.entity_class = EntityClass.UNKNOWN
        self.risk_profile = RiskProfile(ThreatLevel.UNKNOWN)

class GBIOEdge:
    def __init__(self, action: TransferAction, source: GBIONode, target: GBIONode, asset: str, amount: float, usd_value: float, evidence: EvidenceRecord, timestamp: datetime):
        self.action = action
        self.source = source
        self.target = target
        self.asset = asset
        self.amount = amount
        self.usd_value = usd_value
        self.evidence = evidence
        self.timestamp = timestamp
        self.is_terminal_hop = False

class GBIOEngine:
    @classmethod
    def construct_edge(cls, action, source, target, asset, amount, usd_value, evidence, timestamp) -> GBIOEdge:
        edge = GBIOEdge(action, source, target, asset, amount, usd_value, evidence, timestamp)
        # Determine if terminal (e.g. CEX deposit or Mixer)
        # Simple heuristic stub: if it's a known CEX address (which we simulate via length or hardcode, we'll just say False for now)
        edge.is_terminal_hop = False
        return edge

class GBIONormalizer:
    pass
