import os
import time
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NEMESIS_AI_ROUTER")

class AIRouter:
    def __init__(self):
        self.primary_model = "gemini-2.5-flash"
        self.fallback_hierarchy = [
            {"provider": "google", "model": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
            {"provider": "openai", "model": "gpt-5.5-turbo", "name": "GPT-5.5"},
            {"provider": "deepseek", "model": "deepseek-coder", "name": "DeepSeek"},
            {"provider": "mistral", "model": "mistral-large", "name": "Mistral Large"},
            {"provider": "anthropic", "model": "claude-3-opus", "name": "Claude 3"},
            {"provider": "local", "model": "nemesis-vllm", "name": "NEMESIS LLM (Offline)"}
        ]
        self.active_provider = "google"
        self.active_model = self.primary_model
        
        # We simulate checking for local vLLM endpoint
        self.local_vllm_url = os.environ.get("VLLM_URL", "http://localhost:8080/v1")

    def route_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Attempts to route the request through the hierarchy.
        Returns the response and updates the active_model state.
        """
        logger.info(f"[ROUTER] Routing prompt (length: {len(prompt)})")
        
        # 1. Primary Attempt (Gemini 2.5 Flash)
        try:
            return self._call_google(prompt, model=self.primary_model)
        except Exception as e:
            logger.warning(f"[ROUTER] Primary {self.primary_model} failed: {str(e)}")
            
        # 2. Fallbacks
        for fallback in self.fallback_hierarchy:
            logger.info(f"[ROUTER] Attempting fallback: {fallback['name']}")
            try:
                if fallback["provider"] == "google":
                    res = self._call_google(prompt, model=fallback["model"])
                elif fallback["provider"] == "local":
                    res = self._call_local(prompt)
                else:
                    # For other providers, if no key exists, it will raise exception and skip
                    res = self._call_mock_provider(prompt, fallback)
                    
                self.active_provider = fallback["provider"]
                self.active_model = fallback["model"]
                return res
            except Exception as e:
                logger.error(f"[ROUTER] Fallback {fallback['name']} failed: {str(e)}")
                
        raise Exception("ALL AI PROVIDERS FAILED. COGNITIVE CORE OFFLINE.")
        
    def _call_google(self, prompt: str, model: str) -> Dict[str, Any]:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No GEMINI_API_KEY")
            
        genai.configure(api_key=api_key)
        m = genai.GenerativeModel(model)
        # We add timeout simulation
        response = m.generate_content(prompt)
        self.active_provider = "google"
        self.active_model = model
        return {"content": response.text, "model": model, "provider": "google", "offline": False}

    def _call_local(self, prompt: str) -> Dict[str, Any]:
        # Implementation to hit local vLLM API
        # E.g., via aiohttp or requests
        logger.info(f"[ROUTER] Hitting local vLLM at {self.local_vllm_url}")
        # Mocking local response for now
        time.sleep(1)
        self.active_provider = "local"
        self.active_model = "nemesis-vllm"
        return {
            "content": f"[OFFLINE INFERENCE] Processed locally via vLLM. Input: {prompt[:50]}...",
            "model": "nemesis-vllm",
            "provider": "local",
            "offline": True
        }

    def _call_mock_provider(self, prompt: str, config: Dict[str, str]) -> Dict[str, Any]:
        raise ValueError(f"API Key for {config['provider']} missing. Triggering next fallback.")

    def get_status(self) -> Dict[str, Any]:
        return {
            "active_model": self.active_model,
            "provider": self.active_provider,
            "is_offline": self.active_provider == "local",
            "hierarchy": [self.primary_model] + [f['model'] for f in self.fallback_hierarchy]
        }

router_instance = AIRouter()

if __name__ == "__main__":
    # Test Router
    print("Testing AI Router Fallback...")
    # Force failure by unsetting key temporarily
    old_key = os.environ.get("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = ""
    try:
        res = router_instance.route_request("Analyze this wallet: 0x123")
        print("Response:", res)
    except Exception as e:
        print("Final Error:", e)
    if old_key:
        os.environ["GEMINI_API_KEY"] = old_key
