"""Legacy agent module - imports from new structure."""
from src.agent.core.orchestrator import Orchestrator
from src.agent.adapters.llm.fake_client import FakeClient
from src.agent.registry import registry
from src.agent.adapters.telemetry.otel import OTelTelemetry

# Import tools to register them
import src.agent.adapters.tools

def answer(q: str):
    """Legacy answer function that uses the new orchestrator."""
    llm_client = FakeClient()
    telemetry = OTelTelemetry(enabled=False)
    orchestrator = Orchestrator(llm_client, registry, telemetry)
    
    return orchestrator.answer(q)
