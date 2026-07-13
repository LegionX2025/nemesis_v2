import os
import aiohttp
import asyncio
import time
import json
import logging
from typing import Dict, Any, List
from .base import BaseProvider, AIFabricResponse, HealthStatus

logger = logging.getLogger("NEMESIS_GEMINI")

class GeminiKeyManager:
    def __init__(self):
        # Parse multiple keys from .env
        raw_keys = os.environ.get("GEMINI_API_KEYS", os.environ.get("GEMINI_API_KEY", ""))
        self.keys = [k.strip().replace('"', '').replace("'", "") for k in raw_keys.split(",") if k.strip()]
        self.current_index = 0
        self.lock = asyncio.Lock()
        
        if not self.keys:
            raise ValueError("GEMINI_API_KEYS is missing from .env")
            
        logger.info(f"[GEMINI MANAGER] Loaded {len(self.keys)} API Keys for rotation.")

    async def get_key(self) -> str:
        async with self.lock:
            key = self.keys[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.keys)
            return key
            
    async def report_rate_limit(self):
        logger.warning("[GEMINI MANAGER] Rate Limit (429) hit. Rotating key.")
        # Key is already rotated by get_key in round-robin, but we can add backoff logic here if needed.

# Global key manager shared across all Gemini Provider instances
global_key_manager = GeminiKeyManager()

class GoogleGeminiProvider(BaseProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = config.get("model", "gemini-3.0-flash")
        
        self.health = HealthStatus(
            provider="Google DeepMind",
            model=self.model_name,
            supports={"vision": True, "stream": True, "json": True, "reasoning": "pro" in self.model_name, "parallel": True}
        )
        
    async def generate_content(self, prompt: str, **kwargs) -> AIFabricResponse:
        start = time.time()
        max_retries = len(global_key_manager.keys)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        for attempt in range(max_retries):
            api_key = await global_key_manager.get_key()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers={"Content-Type": "application/json"}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        try:
                            content = data["candidates"][0]["content"]["parts"][0]["text"]
                        except (KeyError, IndexError):
                            content = ""
                            
                        latency = int((time.time() - start) * 1000)
                        return AIFabricResponse(
                            content=content,
                            model=self.model_name,
                            provider="Google DeepMind (REST)",
                            latency_ms=latency
                        )
                    elif resp.status == 429:
                        await global_key_manager.report_rate_limit()
                        continue # Try next key
                    else:
                        error_text = await resp.text()
                        logger.error(f"[GEMINI] API Error {resp.status}: {error_text}")
                        # If it's a 400 or 500, we still might want to fallback, but let's break for critical errors
                        if resp.status in [400, 403, 404]:
                            break
                        
        raise Exception(f"Gemini API exhausted all keys or failed. Model: {self.model_name}")

    async def generate_structured(self, prompt: str, schema: Any, **kwargs) -> AIFabricResponse:
        # In a real implementation, you would pass `response_schema` to the REST payload.
        # For now, we fallback to base generation.
        return await self.generate_content(prompt, **kwargs)
        
    async def check_health(self) -> HealthStatus:
        return self.health
