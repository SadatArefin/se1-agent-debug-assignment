"""Compatibility layer - re-export from src.agent."""
from src.agent import Orchestrator, Config

# Legacy function for backward compatibility
def answer(q: str) -> str:
    """Legacy answer function for backward compatibility."""
    from src.agent.adapters.llm.fake_client import FakeClient
    from src.agent.registry import registry
    from src.agent.adapters.telemetry.otel import OTelTelemetry
    
    # Import tools to register them
    import src.agent.adapters.tools
    
    # Create orchestrator
    llm_client = FakeClient()
    telemetry = OTelTelemetry(enabled=False)
    orchestrator = Orchestrator(llm_client, registry, telemetry)
    
    return orchestrator.answer(q)

__all__ = ["answer", "Orchestrator", "Config"]
