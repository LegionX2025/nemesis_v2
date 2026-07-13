import logging
import json
from typing import Any

logger = logging.getLogger("NEMESIS_AI_VALIDATOR")

class ResponseValidator:
    """
    Validates output from the AI Fabric models.
    Can enforce JSON schemas, regex matching, or structural constraints.
    """
    @staticmethod
    def validate_json(content: str) -> dict:
        """Attempt to extract and parse JSON from the raw text."""
        # Clean markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to validate JSON: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
