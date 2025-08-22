"""Legacy LLM module - imports from new structure."""
from src.agent.adapters.llm.openai_client import OpenAIClient
from src.agent.adapters.llm.fake_client import FakeClient

# Legacy function for backward compatibility
def call_llm(prompt: str):
    """Legacy call_llm function."""
    client = FakeClient()
    return client.call(prompt)
