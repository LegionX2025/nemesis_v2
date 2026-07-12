import re
from typing import List, Dict, Any

# Known Mixer Contracts
MIXERS = {
    "ETHEREUM": [
        "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b", # Tornado Cash Router
        "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc", # Tornado Cash 100 ETH
        "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936", # Tornado Cash 10 ETH
        "0x910cbd523d972eb0a6f4cae4418a184084d8a59d", # Tornado Cash 1 ETH
        "0xfa0736cfdbb660a12e2e71fa08bbbb152a5c43d8", # Railgun
    ],
    "BSC": [
        "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc", # Tornado Cash BSC
    ],
    "POLYGON": [
        "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc",
    ]
}

# Known Bridges & Wrapped contracts
BRIDGES = {
    "ETHEREUM": {
        "0x99c9fc46f92e8a1c0dec1b1747d010903e884be1": "Optimism Bridge",
        "0x49048044d57e1c92a77f79988d21fa8faf74e97e": "Arbitrum Bridge",
        "0xa0c68c638235ee32657e8f720a23cec1bfc77c77": "Polygon PoS Bridge",
        "0xdf9b4b57865b403e08c85568442f95c26b7896b0": "Stargate Finance",
        "0x3ee18b2214aff97000d974cf647e7c347e8fa585": "Multichain Router",
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "Wrapped Ether (WETH)"
    },
    "BSC": {
        "0x4a364f8c717caad9a442737eb7b8a55cc6cf18d8": "Stargate Finance",
        "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c": "Wrapped BNB (WBNB)"
    },
    "POLYGON": {
        "0x45a01e4e04f14f7a4a6702c74187c5f6222033cd": "Stargate Finance",
        "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270": "Wrapped Matic (WMATIC)"
    }
}

# Known Centralized Exchange (CEX) Hot Wallets
KNOWN_CEX = {
    "ETHEREUM": {
        "0x28c6c06298d514db089934071355e5ba62210203": "Binance 14",
        "0xf977814e90da44bfa03b6295a0616a897441acec": "Binance 8",
        "0x5a52e96bacd65b1622b74b12c31e9c8cb080b080": "Binance 15",
        "0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67": "Binance 16",
        "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "Binance",
        "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "Binance: WETH",
        "0x71660c4005ba85c37ccec55d0c4493e66fe775d3": "Coinbase 1",
        "0x503828976d22510aad0201ac7ec88293211d23da": "Coinbase 2",
        "0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740": "Coinbase 3",
        "0x2b5634c42055806a59e9107ed44d43c426e58258": "Kraken",
        "0xe853c56864a2ebe4576a807d26fdc4a0ada51919": "Kraken 2",
        "0x04b096f2a246a48d88e0018f921a2c9fa2f592a8": "Kraken 3",
        "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b": "OKX",
        "0xc098b2a3aa256d2140208c3de6543aaef5cd3a94": "FTX Exchange",
        "0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2": "FTX Exchange",
        "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45": "Bitget",
        "0xcd697e64cbcc6ab04dfab34e3fb458bdc385dbcb": "KuCoin"
    },
    "BSC": {
        "0x8894e0a0c962cb723c1976a4421c95949be2d4e3": "Binance Hot Wallet",
        "0xf977814e90da44bfa03b6295a0616a897441acec": "Binance Hot Wallet",
        "0xdfd5293d8e347dfe59e90efd55b2956a1343963d": "Binance Hot Wallet"
    },
    "POLYGON": {
        "0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2": "FTX Exchange"
    }
}

class HeuristicEngine:
    @staticmethod
    def identify_entity_type(address: str, chain: str) -> str:
        """Checks if the address is a known Mixer, Bridge, or Wrapped Token."""
        addr_lower = address.lower()
        chain_upper = chain.upper()
        
        # Check Mixers
        if chain_upper in MIXERS and addr_lower in MIXERS[chain_upper]:
            return "MIXER"
            
        # Check Bridges
        if chain_upper in BRIDGES and addr_lower in BRIDGES[chain_upper]:
            return "BRIDGE"
            
        # Check Exchanges / Custodial
        if chain_upper in KNOWN_CEX and addr_lower in KNOWN_CEX[chain_upper]:
            return "EXCHANGE"
            
        return "UNKNOWN"

    @staticmethod
    def detect_peel_chain(txs: List[Dict[str, Any]], target_address: str) -> bool:
        """
        Heuristic algorithm to detect 'Peel Chain' behavior.
        A peel chain happens when a high value wallet sends a small fixed amount to one address
        and the large remainder to a change address, repeating this process rapidly.
        """
        target_lower = target_address.lower()
        
        # Filter OUTBOUND transactions from the target address
        outbound_txs = [tx for tx in txs if str(tx.get('from', '')).lower() == target_lower]
        
        # Need at least 3 outgoing transactions to form a pattern
        if len(outbound_txs) < 3:
            return False
            
        # Check for 2-output structure (in EVM, usually represented by rapid sequential transfers)
        # We look for a pattern where a large balance drops consistently while small amounts are siphoned.
        small_transfers = 0
        large_transfers = 0
        
        for tx in outbound_txs:
            try:
                amt = float(tx.get('value', '0')) / 1e18
                if 0.01 < amt <= 2.0:
                    small_transfers += 1
                elif amt > 5.0:
                    large_transfers += 1
            except:
                continue
                
        # If there are many small transfers and at least one or more large transfer (the change moving forward)
        # This is a strong indicator of an automated peeling script.
        if small_transfers >= 3 and large_transfers >= 1:
            return True
            
        return False

    @staticmethod
    def enrich_hop_metadata(address: str, chain: str, amount: float, txs: List[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Enriches a graph hop with deep heuristic flags.
        """
        entity_type = HeuristicEngine.identify_entity_type(address, chain)
        
        flags = []
        if entity_type == "MIXER":
            flags.append("OBFUSCATION_MIXER")
        elif entity_type == "BRIDGE":
            flags.append("CROSS_CHAIN_BRIDGE")
        elif entity_type == "EXCHANGE":
            flags.append("CUSTODIAL_TERMINAL")
            
        if txs and HeuristicEngine.detect_peel_chain(txs, address):
            flags.append("PEEL_CHAIN_PATTERN")
            
        return {
            "entity_type": entity_type,
            "heuristic_flags": flags
        }
