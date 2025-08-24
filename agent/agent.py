"""Legacy agent module - imports from new structure."""
from src.agent.core.orchestrator import Orchestrator
from src.agent.adapters.llm.fake_client import FakeClient
from src.agent.registry import registry
from src.agent.adapters.telemetry.enhanced_telemetry import EnhancedTelemetry
from src.agent.core.logging_config import initialize_logging
import os

# Import tools to register them
import src.agent.adapters.tools

# Global logger instance (initialized lazily)
_agent_logger = None

def _get_agent_logger():
    """Get or initialize the agent logger."""
    global _agent_logger
    if _agent_logger is None:
        # Environment variables are already set by main.py before import
        _agent_logger = initialize_logging()
    return _agent_logger

def answer(q: str):
    """Legacy answer function that uses the new orchestrator."""
    llm_client = FakeClient()
    
    # Use enhanced telemetry with logging
    enable_telemetry = os.getenv("ENABLE_TELEMETRY", "true").lower() == "true"
    telemetry = EnhancedTelemetry(enabled=enable_telemetry)
    
    orchestrator = Orchestrator(llm_client, registry, telemetry)
    
    result = orchestrator.answer(q)
    
    return result

def get_log_summary():
    """Get logging summary for debugging."""
    return _get_agent_logger().get_log_summary()
