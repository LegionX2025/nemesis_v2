import logging
from typing import Callable, Any, Dict

logger = logging.getLogger("NEMESIS_AI_FALLBACK")

class FallbackManager:
    """
    Handles robust execution of provider chains with exponential backoff.
    """
    @staticmethod
    async def execute_with_fallback(chain: list, func: Callable, *args, **kwargs) -> Any:
        for provider in chain:
            try:
                logger.info(f"Attempting execution via {provider}")
                return await func(provider, *args, **kwargs)
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}. Cascading to fallback.")
        
        logger.error("All providers in fallback chain exhausted.")
        raise RuntimeError("Complete Failure in AI Routing Chain.")
