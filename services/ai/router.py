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
        # Initializing Gemini Multi-Key Rotation Providers
        self.providers = {
            "gemini-3.1-pro-extended": GoogleGeminiProvider({"model": "gemini-3.1-pro"}),
            "gemini-3.1-flash": GoogleGeminiProvider({"model": "gemini-3.1-flash"}),
            "gemini-3.0-pro": GoogleGeminiProvider({"model": "gemini-3.0-pro"}),
            "gemini-3.0-flash": GoogleGeminiProvider({"model": "gemini-3.0-flash"}),
            "gpt-5.5-mini": OpenAIProvider({"model": "gpt-5.5-mini"}),
            "claude-3-sonnet": AnthropicProvider({"model": "claude-3-sonnet"}),
            "nemesis-vllm": LocalVLLMProvider({"model": "nemesis-vllm"}),
        }

    async def parallel_route(self, prompt: str, models: List[str] = None, use_cache: bool = True, **kwargs) -> AIFabricResponse:
        """
        Executes the prompt across multiple Gemini models in parallel.
        Returns the fastest successful response.
        """
        if use_cache:
            cached_res = self.cache.get(prompt, **kwargs)
            if cached_res:
                cached_res.cached = True
                return cached_res

        if not models:
            # Default parallel aggressive burst
            models = ["gemini-3.1-flash", "gemini-3.0-flash"]
            
        logger.info(f"[ROUTER] Engaging Parallel AI Burst for models: {models}")
        
        tasks = []
        for model_id in models:
            provider = self.providers.get(model_id)
            if provider:
                tasks.append(asyncio.create_task(provider.generate_content(prompt, **kwargs)))
                
        if not tasks:
            raise ValueError(f"None of the specified models were found in the AIFabric.")
            
        # Wait for the first one to finish successfully
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        
        for p in pending:
            p.cancel() # Cancel the slower models!
            
        for task in done:
            try:
                res = task.result()
                if use_cache:
                    self.cache.set(prompt, res, **kwargs)
                return res
            except Exception as e:
                logger.error(f"[ROUTER] Parallel execution error: {e}")
                
        raise Exception("All parallel AI providers failed.")

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
