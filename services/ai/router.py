import logging
from typing import Dict, Any, List, Optional
from .providers.base import AIFabricResponse, BaseProvider
from .providers.gemini import GoogleGeminiProvider
from .providers.adapters import (
    OpenAIProvider, AnthropicProvider, 
    DeepSeekProvider, MistralProvider, LocalVLLMProvider
)
from .classifier import TaskClassifier
from .capability_matrix import CapabilityMatrix
from .cache import AICache

logger = logging.getLogger("NEMESIS_AI_FABRIC")

class AIFabricRouter:
    def __init__(self):
        self.classifier = TaskClassifier()
        self.matrix = CapabilityMatrix()
        self.cache = AICache()
        self._initialize_providers()
        
    def _initialize_providers(self):
        # In a real environment, load credentials from config/Vault
        self.providers = {
            "gemini-3.1-pro": GoogleGeminiProvider({"model": "gemini-3.1-pro"}),
            "gemini-3.1-flash": GoogleGeminiProvider({"model": "gemini-3.1-flash"}),
            "gemini-2.5-pro": GoogleGeminiProvider({"model": "gemini-2.5-pro"}),
            "gemini-2.5-flash": GoogleGeminiProvider({"model": "gemini-2.5-flash"}),
            "gemini-vision": GoogleGeminiProvider({"model": "gemini-2.5-flash-vision"}),
            "gpt-5.5-mini": OpenAIProvider({"model": "gpt-5.5-mini"}),
            "gpt-5.5-turbo": OpenAIProvider({"model": "gpt-5.5-turbo"}),
            "claude-3-sonnet": AnthropicProvider({"model": "claude-3-sonnet"}),
            "claude-3-opus": AnthropicProvider({"model": "claude-3-opus"}),
            "deepseek-coder": DeepSeekProvider({"model": "deepseek-coder"}),
            "deepseek-reasoner": DeepSeekProvider({"model": "deepseek-reasoner"}),
            "nemesis-vllm": LocalVLLMProvider({"model": "nemesis-vllm"}),
        }

    async def route(self, prompt: str, explicit_type: str = None, use_cache: bool = True, **kwargs) -> AIFabricResponse:
        # Check cache
        if use_cache:
            cached_res = self.cache.get(prompt, **kwargs)
            if cached_res:
                cached_res.cached = True
                return cached_res

        # Classify Task
        task_type = self.classifier.classify(prompt, explicit_type)
        logger.info(f"[ROUTER] Assigned capability routing: {task_type}")
        
        # Determine Routing Chain
        fallback_chain = self.matrix.get_fallback_chain(task_type)
        
        for p_key in fallback_chain:
            provider = self.providers.get(p_key)
            if not provider:
                continue
                
            try:
                # Health & Quota Gate
                health = await provider.check_health()
                if health.status not in ["healthy", "ready"]:
                    logger.warning(f"Skipping {p_key} due to status: {health.status}")
                    continue
                    
                logger.info(f"Attempting inference via {p_key}")
                response = await provider.generate_content(prompt, **kwargs)
                
                # Cache success
                if use_cache:
                    self.cache.set(prompt, response, **kwargs)
                    
                return response
                
            except Exception as e:
                logger.error(f"Provider {p_key} failed: {e}")
                
        # Ultimate fallback (Air-gapped / Local Rescue)
        logger.warning("All primary/secondary providers failed. Engaging Local vLLM Rescue.")
        rescue_res = await self.providers["nemesis-vllm"].generate_content(prompt, **kwargs)
        if use_cache:
            self.cache.set(prompt, rescue_res, **kwargs)
        return rescue_res
        
    async def get_system_health(self) -> Dict[str, Any]:
        provider_health = []
        for p_key, provider in self.providers.items():
            h = await provider.check_health()
            provider_health.append(h.model_dump())
            
        return {
            "providers": provider_health,
            "cache_stats": self.cache.get_stats(),
            "active_routes": len(self.matrix.matrix)
        }
