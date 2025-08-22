"""OpenAI client implementation."""
from typing import Any
from ...core.contracts import LLMClient


class OpenAIClient:
    """OpenAI LLM client implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # TODO: Initialize actual OpenAI client when needed
    
    def call(self, prompt: str) -> Any:
        """Call OpenAI API with the prompt."""
        # TODO: Implement actual OpenAI API call
        raise NotImplementedError("OpenAI client not yet implemented")
