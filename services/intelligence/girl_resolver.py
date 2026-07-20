import asyncio

class GlobalIdentityResolutionLayer:
    """
    NEMESIS GIRL (Global Identity Resolution Layer)
    Responsible for normalizing blockchain entities, chains, tokens, and logos.
    """
    
    # Internal mappings for CryptoLogos CDN
    CHAIN_MAP = {
        "ETHEREUM": {"logo": "ethereum-eth-logo.png", "native": "ETH", "color": "#627EEA", "explorer": "https://etherscan.io"},
        "BSC": {"logo": "bnb-bnb-logo.png", "native": "BNB", "color": "#F3BA2F", "explorer": "https://bscscan.com"},
        "POLYGON": {"logo": "polygon-matic-logo.png", "native": "MATIC", "color": "#8247E5", "explorer": "https://polygonscan.com"},
        "AVALANCHE": {"logo": "avalanche-avax-logo.png", "native": "AVAX", "color": "#E84142", "explorer": "https://snowtrace.io"},
        "ARBITRUM": {"logo": "arbitrum-arb-logo.png", "native": "ETH", "color": "#2D374B", "explorer": "https://arbiscan.io"},
        "OPTIMISM": {"logo": "optimism-op-logo.png", "native": "ETH", "color": "#FF0420", "explorer": "https://optimistic.etherscan.io"},
        "BASE": {"logo": "base-logo.png", "native": "ETH", "color": "#0052FF", "explorer": "https://basescan.org"},
        "SOLANA": {"logo": "solana-sol-logo.png", "native": "SOL", "color": "#14F195", "explorer": "https://solscan.io"},
        "TRON": {"logo": "tron-trx-logo.png", "native": "TRX", "color": "#FF0013", "explorer": "https://tronscan.org"},
        "BITCOIN": {"logo": "bitcoin-btc-logo.png", "native": "BTC", "color": "#F7931A", "explorer": "https://www.blockchain.com/btc"}
    }
    
    TOKEN_MAP = {
        "USDT": "tether-usdt-logo.png",
        "USDC": "usd-coin-usdc-logo.png",
        "DAI": "multi-collateral-dai-dai-logo.png",
        "LINK": "chainlink-link-logo.png",
        "UNI": "uniswap-uni-logo.png",
        "AAVE": "aave-aave-logo.png",
        "WBTC": "wrapped-bitcoin-wbtc-logo.png",
        "SHIB": "shiba-inu-shib-logo.png"
    }

    ENTITY_MAP = {
        "binance": {"name": "Binance", "type": "Exchange", "icon": "🏦", "logo": "/assets/entities/binance.svg"},
        "coinbase": {"name": "Coinbase", "type": "Exchange", "icon": "🏦", "logo": "/assets/entities/coinbase.svg"},
        "kraken": {"name": "Kraken", "type": "Exchange", "icon": "🏦", "logo": "/assets/entities/kraken.svg"},
        "okx": {"name": "OKX", "type": "Exchange", "icon": "🏦", "logo": "/assets/entities/okx.svg"},
        "kucoin": {"name": "KuCoin", "type": "Exchange", "icon": "🏦", "logo": "/assets/entities/kucoin.svg"},
        "tornado cash": {"name": "Tornado Cash", "type": "Mixer", "icon": "🌪", "logo": "/assets/entities/tornado-cash.svg"},
        "stargate": {"name": "Stargate", "type": "Bridge", "icon": "🌉", "logo": "/assets/entities/stargate.svg"},
    }

    @classmethod
    def get_cryptologos_url(cls, logo_file: str) -> str:
        """Returns the fully qualified URL for a CryptoLogos image."""
        if not logo_file: return ""
        if logo_file == "base-logo.png": return "https://basescan.org/images/logo-ether.png" # Fallback
        return f"https://cryptologos.cc/logos/{logo_file}?v=035"

    @classmethod
    def resolve_token(cls, symbol: str) -> dict:
        symbol = str(symbol).upper()
        # If it's a native token
        for chain, data in cls.CHAIN_MAP.items():
            if data["native"] == symbol:
                return {
                    "symbol": symbol,
                    "logo": cls.get_cryptologos_url(data["logo"]),
                    "is_native": True
                }
        
        # Check standard tokens
        logo_file = cls.TOKEN_MAP.get(symbol)
        if logo_file:
            return {
                "symbol": symbol,
                "logo": cls.get_cryptologos_url(logo_file),
                "is_native": False
            }
            
        return {
            "symbol": symbol,
            "logo": "",
            "is_native": False
        }

    @classmethod
    def resolve_chain(cls, chain_name: str) -> dict:
        chain_name = str(chain_name).upper()
        data = cls.CHAIN_MAP.get(chain_name)
        if data:
            return {
                "chain": chain_name,
                "logo": cls.get_cryptologos_url(data["logo"]),
                "color": data["color"],
                "explorer": data["explorer"],
                "native": data["native"]
            }
        return {
            "chain": chain_name,
            "logo": "",
            "color": "#888888",
            "explorer": "",
            "native": "UNKNOWN"
        }

    @classmethod
    def resolve_entity(cls, label: str) -> dict:
        if not label or label == "Unknown Entity" or label == "EOA_WALLET":
            return {
                "name": "Unknown Wallet",
                "type": "Wallet",
                "icon": "👤",
                "logo": "",
                "classification": "Unverified EOA",
                "risk_score": 0,
                "tags": []
            }
            
        label_lower = label.lower()
        
        # Exact match
        for key, data in cls.ENTITY_MAP.items():
            if key in label_lower:
                return {
                    "name": data["name"],
                    "type": data["type"],
                    "icon": data["icon"],
                    "logo": data["logo"],
                    "classification": f"Known {data['type']}",
                    "risk_score": 10 if data["type"] == "Exchange" else 80 if data["type"] == "Mixer" else 50,
                    "tags": [data["type"], "Verified"]
                }
                
        # Heuristic Match
        is_exchange = "exchange" in label_lower or "hot wallet" in label_lower
        is_bridge = "bridge" in label_lower
        is_mixer = "mixer" in label_lower
        is_phish = "phish" in label_lower or "scam" in label_lower or "exploit" in label_lower
        
        name = label.title()
        type_ = "Wallet"
        icon = "👤"
        risk = 0
        tags = []
        
        if is_exchange:
            type_ = "Exchange"
            icon = "🏦"
            risk = 15
            tags.append("Exchange")
        elif is_bridge:
            type_ = "Bridge"
            icon = "🌉"
            tags.append("Bridge")
        elif is_mixer:
            type_ = "Mixer"
            icon = "🌪"
            risk = 90
            tags.append("Mixer")
        elif is_phish:
            type_ = "Malicious"
            icon = "💀"
            risk = 100
            tags.extend(["Scam", "High-Risk"])
            
        return {
            "name": name,
            "type": type_,
            "icon": icon,
            "logo": "",
            "classification": type_,
            "risk_score": risk,
            "tags": tags
        }

    @classmethod
    def globally_resolve_wallet(cls, address: str, chain: str, raw_label: str, confidence: float = 0.0) -> dict:
        """
        Takes raw pipeline output and structures it into the Global Identity Resolution Schema.
        """
        chain_info = cls.resolve_chain(chain)
        entity_info = cls.resolve_entity(raw_label)
        
        explorer_url = f"{chain_info['explorer']}/address/{address}" if chain_info['explorer'] else ""
        
        return {
            "id": f"{chain_info['chain'].lower()}:{address.lower()}",
            "address": address,
            "entity_name": entity_info["name"],
            "entity_logo": entity_info["logo"],
            "entity_icon": entity_info["icon"],
            "entity_type": entity_info["type"],
            "wallet_type": "Hot Wallet" if "hot" in raw_label.lower() else "EOA",
            "classification": entity_info["classification"],
            "chain": chain_info["chain"],
            "chain_logo": chain_info["logo"],
            "chain_color": chain_info["color"],
            "native_asset": chain_info["native"],
            "risk_score": entity_info["risk_score"],
            "confidence": confidence if confidence else 95.5 if entity_info["name"] != "Unknown Wallet" else 0.0,
            "verified": entity_info["name"] != "Unknown Wallet",
            "tags": entity_info["tags"],
            "explorer_urls": {
                "primary": explorer_url
            }
        }
