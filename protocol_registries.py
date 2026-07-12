from typing import Dict, Any, List
from gbio_ontology import EntityClass

class ProtocolRegistry:
    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}

    def register(self, address: str, name: str, chain: str, entity_class: EntityClass, category: str, tags: List[str], risk_score: float, confidence: float):
        self.entities[address.lower()] = {
            "name": name,
            "chain": chain,
            "entity_class": entity_class,
            "category": category,
            "tags": tags,
            "risk_score": risk_score,
            "confidence": confidence
        }

    def lookup(self, address: str) -> Dict[str, Any]:
        return self.entities.get(address.lower())

# Global Registries
EXCHANGE_REGISTRY = ProtocolRegistry()
BRIDGE_REGISTRY = ProtocolRegistry()
DEX_REGISTRY = ProtocolRegistry()
MIXER_REGISTRY = ProtocolRegistry()
VALIDATOR_REGISTRY = ProtocolRegistry()
CUSTODIAN_REGISTRY = ProtocolRegistry()
STABLECOIN_REGISTRY = ProtocolRegistry()
NFT_MARKETPLACE_REGISTRY = ProtocolRegistry()
DAO_REGISTRY = ProtocolRegistry()
LENDING_REGISTRY = ProtocolRegistry()
MEV_REGISTRY = ProtocolRegistry()
SANCTIONS_REGISTRY = ProtocolRegistry()

# Exchange
EXCHANGE_REGISTRY.register("0x28C6c06298d514Db089934071355E22Af164fC50", "Binance 14", "Ethereum", EntityClass.EXCHANGE_HOT, "CUSTODIAL_EXCHANGE", ["kyc-strict", "fiat-offramp", "binance"], 10.0, 99.0)
EXCHANGE_REGISTRY.register("0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE", "Binance 8", "Ethereum", EntityClass.EXCHANGE_HOT, "CUSTODIAL_EXCHANGE", ["kyc-strict", "binance"], 10.0, 99.0)
EXCHANGE_REGISTRY.register("0x00000000219ab540356cBB839Cbe05303d7705Fa", "Kraken", "Ethereum", EntityClass.EXCHANGE_HOT, "CUSTODIAL_EXCHANGE", ["kyc-strict"], 10.0, 99.0)

# Mixer
MIXER_REGISTRY.register("0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b", "Tornado Cash Router", "Ethereum", EntityClass.MIXER_ROUTER, "DECENTRALIZED_MIXER", ["anonymity", "tornado-cash", "ofac-sanctioned"], 100.0, 99.0)
MIXER_REGISTRY.register("0x47CE0C6eD5B0Ce3d3A51f161364B6da24665fB84", "Tornado Cash 100 ETH", "Ethereum", EntityClass.MIXER_POOL, "DECENTRALIZED_MIXER", ["anonymity", "ofac-sanctioned"], 100.0, 99.0)

# Bridge
BRIDGE_REGISTRY.register("0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1", "Optimism Gateway", "Ethereum", EntityClass.BRIDGE_ENDPOINT, "L2_BRIDGE", ["optimism", "rollup"], 20.0, 99.0)
BRIDGE_REGISTRY.register("0x3ee18B2214AFF97000D974cf647E7C347E8fa585", "Wormhole Network", "Ethereum", EntityClass.BRIDGE_ENDPOINT, "CROSS_CHAIN", ["wormhole", "high-volume"], 30.0, 99.0)

# DEX
DEX_REGISTRY.register("0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45", "Uniswap V3 Router 2", "Ethereum", EntityClass.DEX_ROUTER, "DEX_ROUTER", ["uniswap"], 5.0, 99.0)
DEX_REGISTRY.register("0x1111111254fb6c44bac0bed2854e76f90643097d", "1inch v4 Router", "Ethereum", EntityClass.DEX_ROUTER, "DEX_AGGREGATOR", ["1inch"], 5.0, 99.0)

# Stablecoin
STABLECOIN_REGISTRY.register("0xdAC17F958D2ee523a2206206994597C13D831ec7", "Tether (USDT)", "Ethereum", EntityClass.SMART_CONTRACT, "FIAT_BACKED", ["tether", "blacklist-capable"], 5.0, 99.0)
STABLECOIN_REGISTRY.register("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "USD Coin (USDC)", "Ethereum", EntityClass.SMART_CONTRACT, "FIAT_BACKED", ["circle", "blacklist-capable"], 5.0, 99.0)

# Lending
LENDING_REGISTRY.register("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9", "Aave V2 Lending Pool", "Ethereum", EntityClass.LENDING_POOL, "LENDING_POOL", ["aave"], 15.0, 99.0)

# Sanctions
SANCTIONS_REGISTRY.register("0x8576acc5c05d6ce88f4e49bf65bdf0c62f91353c", "Lazarus Group Wallet", "Ethereum", EntityClass.SANCTIONED_ENTITY, "OFAC_SDN", ["north-korea", "lazarus", "hack"], 100.0, 100.0)

def identify_entity(address: str) -> Dict[str, Any]:
    """Checks all registries for an address and returns the entity data if found."""
    registries = [
        EXCHANGE_REGISTRY, BRIDGE_REGISTRY, DEX_REGISTRY, MIXER_REGISTRY, 
        VALIDATOR_REGISTRY, CUSTODIAN_REGISTRY, STABLECOIN_REGISTRY, 
        NFT_MARKETPLACE_REGISTRY, DAO_REGISTRY, LENDING_REGISTRY, 
        MEV_REGISTRY, SANCTIONS_REGISTRY
    ]
    for registry in registries:
        result = registry.lookup(address)
        if result:
            return result
    return None
