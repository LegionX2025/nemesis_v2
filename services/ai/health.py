from pydantic import BaseModel, Field
from typing import Dict

class HealthStatus(BaseModel):
    provider: str
    model: str
    status: str = "healthy"
    latency_ms: int = 0
    quota_remaining: int = 100
    rpm_limit: int = 1000
    supports: Dict[str, bool] = Field(default_factory=dict)
