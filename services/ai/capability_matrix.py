import logging
from typing import Dict, List

logger = logging.getLogger("NEMESIS_AI_MATRIX")

class CapabilityMatrix:
    """
    Defines the routing rules for specific AI capabilities.
    Maps a task category to an ordered list of model IDs (primary -> secondary -> fallback).
    """
    def __init__(self):
        # Ordered by priority based on capability and cost/latency tradeoffs
        self.matrix: Dict[str, List[str]] = {
            "reasoning": [
                "gemini-3.1-pro", 
                "gemini-2.5-pro", 
                "gpt-5.5-turbo", 
                "claude-3-opus", 
                "claude-3-sonnet", 
                "deepseek-reasoner",
                "nemesis-vllm"
            ],
            "fast": [
                "gemini-3.1-flash", 
                "gemini-2.5-flash", 
                "gpt-5.5-mini", 
                "claude-3-haiku",
                "deepseek-chat",
                "nemesis-vllm"
            ],
            "vision": [
                "gemini-vision", 
                "gpt-4o-vision", 
                "claude-3-sonnet"
            ],
            "embeddings": [
                "gemini-embeddings", 
                "openai-embeddings-v3", 
                "local-bge-m3"
            ],
            "code": [
                "deepseek-coder",
                "claude-3-sonnet",
                "gemini-3.1-pro",
                "gpt-5.5-turbo"
            ],
            "blockchain": [
                "gemini-2.5-pro",
                "deepseek-coder",
                "gpt-5.5-turbo"
            ],
            "report": [
                "claude-3-opus",
                "gemini-3.1-pro",
                "gpt-5.5-turbo"
            ]
        }
        
    def get_fallback_chain(self, capability: str) -> List[str]:
        """Returns the fallback chain for a given capability, defaulting to 'fast'."""
        if capability in self.matrix:
            return self.matrix[capability]
        
        logger.warning(f"Capability '{capability}' not found in matrix. Falling back to 'fast'.")
        return self.matrix["fast"]

    def override_chain(self, capability: str, chain: List[str]):
        """Dynamically update the routing priority at runtime."""
        self.matrix[capability] = chain
        logger.info(f"Updated routing chain for '{capability}'")
