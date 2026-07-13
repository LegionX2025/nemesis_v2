import logging
from typing import Dict, Any, List

logger = logging.getLogger("NEMESIS_AI_REGISTRY")

class ModelRegistry:
    """
    Dynamic model registry for AI Fabric.
    Automatically detects and validates available models and capabilities.
    """
    def __init__(self):
        self.models = {}

    def register_model(self, model_id: str, provider_id: str, capabilities: Dict[str, bool], rpm_limit: int):
        self.models[model_id] = {
            "provider": provider_id,
            "capabilities": capabilities,
            "rpm_limit": rpm_limit,
            "status": "ready"
        }
        logger.debug(f"Registered model {model_id} via {provider_id}")

    def get_capable_models(self, capability: str) -> List[str]:
        return [
            m_id for m_id, data in self.models.items() 
            if data["capabilities"].get(capability, False) and data["status"] == "ready"
        ]

    def update_status(self, model_id: str, status: str):
        if model_id in self.models:
            self.models[model_id]["status"] = status
            
    def get_all(self):
        return self.models

registry = ModelRegistry()

# Hardcoded initial registry for demonstration; in production this is discovered.
registry.register_model("gemini-2.5-flash", "google", {"fast": True, "vision": True, "json": True}, 1500)
registry.register_model("gemini-2.5-pro", "google", {"reasoning": True, "vision": True, "json": True}, 500)
registry.register_model("gpt-5.5-mini", "openai", {"fast": True, "json": True}, 3000)
registry.register_model("gpt-5.5-turbo", "openai", {"reasoning": True, "json": True}, 500)
registry.register_model("claude-3-sonnet", "anthropic", {"reasoning": True}, 1000)
registry.register_model("claude-3-opus", "anthropic", {"report": True}, 100)
registry.register_model("deepseek-coder", "deepseek", {"blockchain": True, "fast": True}, 2000)
registry.register_model("nemesis-vllm", "local", {"default": True, "fallback": True}, 9999)
