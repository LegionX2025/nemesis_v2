import logging
from typing import Dict, Any

logger = logging.getLogger("NEMESIS_AI_CLASSIFIER")

class TaskClassifier:
    """
    Intelligently analyzes an incoming prompt/task and classifies it into a capability domain.
    Used by the AI Fabric Router to determine the optimal provider.
    """
    
    def __init__(self):
        self.rules = {
            "blockchain": ["address", "0x", "transaction", "tx", "wallet", "smart contract", "token", "defi"],
            "reasoning": ["analyze", "evaluate", "why", "how", "explain", "compare", "correlate"],
            "report": ["summarize", "report", "generate document", "briefing"],
            "vision": ["image", "screenshot", "ocr", "picture", "photo"],
            "code": ["script", "python", "javascript", "refactor", "debug", "implement"],
            "darknet": ["onion", "tor", "i2p", "market", "vendor", "pgp"]
        }

    def classify(self, prompt: str, explicit_type: str = None) -> str:
        """
        Classify the task type based on the prompt content.
        If explicit_type is provided, it overrides automatic classification unless it's 'default'.
        """
        if explicit_type and explicit_type != "default":
            logger.debug(f"Using explicit task type: {explicit_type}")
            return explicit_type
            
        prompt_lower = prompt.lower()
        
        scores = {k: 0 for k in self.rules.keys()}
        
        for category, keywords in self.rules.items():
            for kw in keywords:
                if kw in prompt_lower:
                    scores[category] += 1
                    
        # Find category with highest score
        best_category = max(scores, key=scores.get)
        
        if scores[best_category] > 0:
            logger.debug(f"Classified prompt as '{best_category}' (score: {scores[best_category]})")
            return best_category
            
        logger.debug("Could not classify prompt. Defaulting to 'fast'.")
        return "fast"
