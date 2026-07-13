from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class HealthStatus(BaseModel):
    provider: str
    model: str
    status: str = "healthy"
    latency_ms: int = 0
    quota_remaining: int = 100
    rpm_limit: int = 1000
    supports: Dict[str, bool] = Field(default_factory=dict)

class AIFabricResponse(BaseModel):
    content: str
    model: str
    provider: str
    latency_ms: int
    cost_estimate: float = 0.0
    cached: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseProvider(ABC):
    """
    Abstract base class for all AI Fabric Providers.
    Ensures modularity and strict contract adherence.
    """
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.health = HealthStatus(
            provider="unknown",
            model="unknown"
        )
        
    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> AIFabricResponse:
        """Generate content from the model."""
        pass
        
    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Any, **kwargs) -> AIFabricResponse:
        """Generate structured JSON output according to a schema."""
        pass
        
    @abstractmethod
    async def check_health(self) -> HealthStatus:
        """Ping the service to check health, latency, and quota."""
        pass
