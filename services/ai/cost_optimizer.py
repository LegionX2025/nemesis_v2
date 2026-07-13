import logging

logger = logging.getLogger("NEMESIS_AI_COST_OP")

class CostOptimizer:
    """
    Calculates estimated costs per provider and redirects to cheaper models
    if budget limits are approached.
    """
    def __init__(self):
        self.pricing = {
            "gemini-3.1-pro": {"input": 0.0025, "output": 0.0075},
            "gemini-3.1-flash": {"input": 0.00025, "output": 0.00075},
            "gpt-5.5-turbo": {"input": 0.0050, "output": 0.0150},
            "gpt-5.5-mini": {"input": 0.0005, "output": 0.0015},
            "claude-3-opus": {"input": 0.0150, "output": 0.0750},
            "nemesis-vllm": {"input": 0.0, "output": 0.0}
        }
        
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        rates = self.pricing.get(model, {"input": 0.001, "output": 0.002})
        return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])
