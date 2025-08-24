"""Legacy LLM module - imports from new structure."""
from src.agent.adapters.llm.fake_client import FakeClient

def call_llm(prompt: str):
    client = FakeClient()
    return client.call(prompt)
