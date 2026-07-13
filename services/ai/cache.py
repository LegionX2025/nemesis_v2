import logging
import hashlib
import json
import time
from typing import Optional, Any, Dict

logger = logging.getLogger("NEMESIS_AI_CACHE")

class AICache:
    """
    In-memory caching mechanism for AI responses.
    Production implementations should replace this with Redis.
    """
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        self.hits = 0
        self.misses = 0

    def _generate_key(self, prompt: str, **kwargs) -> str:
        """Create a deterministic hash for a given prompt and parameters."""
        data = {"prompt": prompt, "kwargs": kwargs}
        # Sort keys to ensure consistent hashing
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def get(self, prompt: str, **kwargs) -> Optional[Any]:
        key = self._generate_key(prompt, **kwargs)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                self.hits += 1
                logger.debug(f"Cache HIT for key {key[:8]}")
                return entry["response"]
            else:
                # Expired
                del self._cache[key]
                
        self.misses += 1
        return None

    def set(self, prompt: str, response: Any, **kwargs):
        key = self._generate_key(prompt, **kwargs)
        self._cache[key] = {
            "timestamp": time.time(),
            "response": response
        }
        logger.debug(f"Cache SET for key {key[:8]}")
        
    def get_stats(self) -> Dict[str, int]:
        total = self.hits + self.misses
        hit_ratio = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": len(self._cache),
            "hit_ratio_percent": round(hit_ratio, 2)
        }
        
    def clear(self):
        self._cache.clear()
        self.hits = 0
        self.misses = 0
