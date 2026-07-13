import logging
from typing import List, Dict, Any

logger = logging.getLogger("NEMESIS_AI_MEMORY")

class ConversationalMemory:
    """
    Manages conversational context windows for multi-turn AI workflows.
    Ensures that context sizes do not exceed provider token limits.
    """
    def __init__(self, max_history_tokens: int = 4000):
        self.history: List[Dict[str, Any]] = []
        self.max_tokens = max_history_tokens
        
    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        self._prune_history()
        
    def _prune_history(self):
        # A simple sliding window stub. 
        # Production would use a real tokenizer (e.g. tiktoken).
        while len(self.history) > 10: 
            self.history.pop(0)
            
    def get_context(self) -> List[Dict[str, Any]]:
        return self.history
        
    def clear(self):
        self.history.clear()
