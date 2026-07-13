import logging
import time
from typing import Dict

logger = logging.getLogger("NEMESIS_AI_RATE_LIMIT")

class RateLimiter:
    """
    Client-side token bucket rate limiting to avoid HTTP 429s from Providers.
    """
    def __init__(self):
        self.buckets: Dict[str, Dict[str, float]] = {}
        
    def _init_bucket(self, provider: str, capacity: float):
        if provider not in self.buckets:
            self.buckets[provider] = {
                "tokens": capacity,
                "last_refill": time.time(),
                "capacity": capacity,
                "refill_rate": capacity / 60.0 # Refill per second
            }

    def consume(self, provider: str, amount: float = 1.0, capacity: float = 60.0) -> bool:
        self._init_bucket(provider, capacity)
        bucket = self.buckets[provider]
        
        now = time.time()
        elapsed = now - bucket["last_refill"]
        
        # Refill
        bucket["tokens"] = min(bucket["capacity"], bucket["tokens"] + (elapsed * bucket["refill_rate"]))
        bucket["last_refill"] = now
        
        if bucket["tokens"] >= amount:
            bucket["tokens"] -= amount
            return True
        return False
