import logging
from typing import Dict, Any

logger = logging.getLogger("NEMESIS_AI_TELEMETRY")

class TelemetryEngine:
    """
    Logs API telemetry to the Enterprise Operations Center for analysis.
    """
    def __init__(self):
        self.metrics = []

    def record(self, provider: str, model: str, latency: int, tokens: int, success: bool):
        record = {
            "provider": provider,
            "model": model,
            "latency_ms": latency,
            "tokens": tokens,
            "success": success
        }
        self.metrics.append(record)
        logger.debug(f"Telemetry recorded: {record}")
        
    def get_metrics(self) -> list:
        return self.metrics
