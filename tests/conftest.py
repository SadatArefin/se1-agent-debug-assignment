"""Test configuration and fixtures."""
import pytest
from agent.core.orchestrator import Orchestrator
from agent.adapters.llm.fake_client import FakeClient
from agent.registry import ToolRegistry
from agent.adapters.telemetry.otel import OTelTelemetry


@pytest.fixture
def fake_llm_client():
    """Provide a fake LLM client for testing."""
    return FakeClient()


@pytest.fixture
def tool_registry():
    """Provide a clean tool registry for testing."""
    return ToolRegistry()


@pytest.fixture
def telemetry():
    """Provide telemetry instance for testing."""
    return OTelTelemetry(enabled=False)


@pytest.fixture
def orchestrator(fake_llm_client, tool_registry, telemetry):
    """Provide an orchestrator instance for testing."""
    return Orchestrator(fake_llm_client, tool_registry, telemetry)
