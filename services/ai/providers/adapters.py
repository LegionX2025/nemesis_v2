from typing import Dict, Any
from .base import BaseProvider, AIFabricResponse, HealthStatus
import time

class MockProvider(BaseProvider):
    def __init__(self, config: Dict[str, Any], provider_name: str):
        super().__init__(config)
        self.provider_name = provider_name
        self.model_name = config.get("model", f"mock-{provider_name.lower()}")
        self.health = HealthStatus(
            provider=self.provider_name,
            model=self.model_name,
            supports={"vision": False, "stream": False, "json": True, "reasoning": False}
        )
        
    async def generate_content(self, prompt: str, **kwargs) -> AIFabricResponse:
        start = time.time()
        time.sleep(0.1) # simulate latency
        latency = int((time.time() - start) * 1000)
        
        return AIFabricResponse(
            content=f"[MOCK] {self.provider_name} response for model {self.model_name}.",
            model=self.model_name,
            provider=self.provider_name,
            latency_ms=latency
        )
        
    async def generate_structured(self, prompt: str, schema: Any, **kwargs) -> AIFabricResponse:
        return await self.generate_content(prompt, **kwargs)
        
    async def check_health(self) -> HealthStatus:
        return self.health

class OpenAIProvider(MockProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "OpenAI")

class AnthropicProvider(MockProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "Anthropic")

class DeepSeekProvider(MockProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "DeepSeek")

class MistralProvider(MockProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "Mistral")

class LocalVLLMProvider(MockProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "LocalVLLM")
        self.health.status = "ready"
