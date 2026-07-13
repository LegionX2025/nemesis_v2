import os
from typing import Dict, Any
from .base import BaseProvider, AIFabricResponse, HealthStatus
import time

class GoogleGeminiProvider(BaseProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", os.environ.get("GEMINI_API_KEY"))
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")
            
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.genai = genai
        self.model_name = config.get("model", "gemini-2.5-flash")
        
        self.health = HealthStatus(
            provider="Google",
            model=self.model_name,
            supports={"vision": True, "stream": True, "json": True, "reasoning": "pro" in self.model_name}
        )
        
    async def generate_content(self, prompt: str, **kwargs) -> AIFabricResponse:
        start = time.time()
        m = self.genai.GenerativeModel(self.model_name)
        response = m.generate_content(prompt)
        latency = int((time.time() - start) * 1000)
        
        return AIFabricResponse(
            content=response.text,
            model=self.model_name,
            provider="Google",
            latency_ms=latency
        )
        
    async def generate_structured(self, prompt: str, schema: Any, **kwargs) -> AIFabricResponse:
        # Simplistic stub for structured output
        return await self.generate_content(prompt, **kwargs)
        
    async def check_health(self) -> HealthStatus:
        return self.health
