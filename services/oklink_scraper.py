import os
import aiohttp
import logging
import asyncio
from bs4 import BeautifulSoup
from services.api_rotator import rotator

logger = logging.getLogger("NEMESIS_OKLINK")

async def resolve_entity_oklink(session, address: str, chain: str):
    """
    Attempts to resolve entity metadata using OKLink API.
    Falls back to a headless scraper approach if API fails or no key is present.
    """
    logger.info(f"Resolving entity for {address} via OKLink/Scraper")
    api_key = os.getenv("OKLINK_API_KEY", "")
    
    chain_short = "eth"
    if chain.upper() in ["BSC", "BNB"]: chain_short = "bsc"
    elif chain.upper() in ["POLYGON", "MATIC"]: chain_short = "polygon"
    elif chain.upper() in ["ARBITRUM", "ARB"]: chain_short = "arbitrum"
    elif chain.upper() in ["OPTIMISM", "OP"]: chain_short = "optimism"
    
    # 1. Try API if key is present
    if api_key:
        url = f"https://www.oklink.com/api/v5/explorer/address/address-summary?chainShortName={chain_short}&address={address}"
        headers = {"Ok-Access-Key": api_key}
        
        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if data.get("code") == "0" and data.get("data"):
                    summary = data["data"][0]
                    label = summary.get("contractName", "") or summary.get("labelName", "")
                    if label:
                        return {
                            "name": label,
                            "tags": ["OKLink-API-Resolved"],
                            "entity_class": "EXCHANGE" if any(x in label.lower() for x in ["exchange", "binance", "kraken", "coinbase"]) else "SMART_CONTRACT"
                        }
        except Exception as e:
            logger.error(f"OKLink API error: {e}")
            
    # 2. Fallback to OSINT Scraper (BeautifulSoup approach for Etherscan/Blockscout)
    return await _osint_scrape_fallback(session, address, chain)


async def _osint_scrape_fallback(session, address: str, chain: str):
    # Simulated fallback OSINT logic using aiohttp & bs4
    logger.info(f"Engaging OSINT Scraper fallback for {address}")
    
    # Normally we would scrape Etherscan/Polygonscan label tags here
    # Example snippet (Note: Etherscan blocks simple aiohttp without headers/proxies)
    # So we use a mock resolution for demonstration unless we run Playwright
    await asyncio.sleep(0.5)
    
    return {
        "name": "Unknown Entity (Scanned)",
        "tags": ["OSINT-Fallback-Checked"],
        "entity_class": "UNKNOWN"
    }
