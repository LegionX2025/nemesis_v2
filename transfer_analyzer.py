"""
Transfer Analyzer Module
Normalizes raw blockchain transactions into the GBIO Transfer Ontology (300+ types).
"""
import logging
from enum import Enum
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TransferType(Enum):
    # Core Transfer Types
    STANDARD_TRANSFER = "STANDARD_TRANSFER"
    MINT = "MINT"
    BURN = "BURN"
    
    # DEX Operations
    DEX_SWAP = "DEX_SWAP"
    DEX_ADD_LIQUIDITY = "DEX_ADD_LIQUIDITY"
    DEX_REMOVE_LIQUIDITY = "DEX_REMOVE_LIQUIDITY"
    
    # Cross-Chain Operations
    BRIDGE_DEPOSIT = "BRIDGE_DEPOSIT"
    BRIDGE_WITHDRAWAL = "BRIDGE_WITHDRAWAL"
    CROSS_CHAIN_MESSAGE = "CROSS_CHAIN_MESSAGE"
    
    # Mixing/Privacy
    MIXER_DEPOSIT = "MIXER_DEPOSIT"
    MIXER_WITHDRAWAL = "MIXER_WITHDRAWAL"
    
    # Lending/Borrowing
    LENDING_DEPOSIT = "LENDING_DEPOSIT"
    LENDING_BORROW = "LENDING_BORROW"
    LENDING_REPAY = "LENDING_REPAY"
    LENDING_LIQUIDATION = "LENDING_LIQUIDATION"
    FLASH_LOAN = "FLASH_LOAN"
    
    # Staking
    STAKING_DEPOSIT = "STAKING_DEPOSIT"
    STAKING_WITHDRAWAL = "STAKING_WITHDRAWAL"
    STAKING_REWARD = "STAKING_REWARD"
    LIQUID_STAKING_MINT = "LIQUID_STAKING_MINT"
    
    # CEX Operations
    CEX_DEPOSIT = "CEX_DEPOSIT"
    CEX_WITHDRAWAL = "CEX_WITHDRAWAL"
    
    # NFTs
    NFT_MINT = "NFT_MINT"
    NFT_TRANSFER = "NFT_TRANSFER"
    NFT_SALE = "NFT_SALE"
    
    UNKNOWN = "UNKNOWN"

class TransferAnalyzer:
    """
    Analyzes raw transactions and classifies them into the normalized GBIO Transfer Ontology.
    """
    
    @staticmethod
    def classify_transfer(tx_data: Dict[str, Any], sender_label: str, receiver_label: str) -> TransferType:
        """
        Classify a transaction based on heuristics and labels.
        In a full implementation, this will rely on decoded ABI data from the Universal Decoder.
        """
        # 1. Null address checks (Mint/Burn)
        from_addr = tx_data.get("from", "").lower()
        to_addr = tx_data.get("to", "").lower()
        
        if from_addr in ["0x0000000000000000000000000000000000000000", "0x0", ""]:
            return TransferType.MINT
        if to_addr in ["0x0000000000000000000000000000000000000000", "0x000000000000000000000000000000000000dead", "0x0"]:
            return TransferType.BURN
            
        # 2. Heuristics based on Labels
        sender_lbl_upper = sender_label.upper()
        recv_lbl_upper = receiver_label.upper()
        
        # Mixers
        if "MIXER" in recv_lbl_upper or "TORNADO" in recv_lbl_upper:
            return TransferType.MIXER_DEPOSIT
        if "MIXER" in sender_lbl_upper or "TORNADO" in sender_lbl_upper:
            return TransferType.MIXER_WITHDRAWAL
            
        # CEX
        if "BINANCE" in recv_lbl_upper or "KRAKEN" in recv_lbl_upper or "EXCHANGE" in recv_lbl_upper:
            return TransferType.CEX_DEPOSIT
        if "BINANCE" in sender_lbl_upper or "KRAKEN" in sender_lbl_upper or "EXCHANGE" in sender_lbl_upper:
            return TransferType.CEX_WITHDRAWAL
            
        # Bridges
        if "BRIDGE" in recv_lbl_upper:
            return TransferType.BRIDGE_DEPOSIT
        if "BRIDGE" in sender_lbl_upper:
            return TransferType.BRIDGE_WITHDRAWAL
            
        # DEX
        if "UNISWAP" in recv_lbl_upper or "SUSHISWAP" in recv_lbl_upper or "PANCAKESWAP" in recv_lbl_upper or "ROUTER" in recv_lbl_upper:
            return TransferType.DEX_SWAP
            
        # Fallback
        return TransferType.STANDARD_TRANSFER
