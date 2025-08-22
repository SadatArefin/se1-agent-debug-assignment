"""Tests for the core orchestrator."""
import pytest
from src.agent.core.orchestrator import Orchestrator
from src.agent.adapters.tools.calculator import CalculatorTool
from src.agent.adapters.tools.weather import WeatherTool
from src.agent.adapters.tools.kb import KnowledgeBaseTool


def test_orchestrator_initialization(fake_llm_client, tool_registry, telemetry):
    """Test orchestrator initialization."""
    orchestrator = Orchestrator(fake_llm_client, tool_registry, telemetry)
    assert orchestrator.llm_client == fake_llm_client
    assert orchestrator.registry == tool_registry
    assert orchestrator.telemetry == telemetry


def test_orchestrator_answer_basic(orchestrator):
    """Test basic answer functionality."""
    result = orchestrator.answer("Hello")
    assert isinstance(result, str)
    assert len(result) > 0


def test_orchestrator_with_tools(tool_registry, fake_llm_client, telemetry):
    """Test orchestrator with registered tools."""
    # Register tools
    tool_registry.register(CalculatorTool())
    tool_registry.register(WeatherTool())
    tool_registry.register(KnowledgeBaseTool())
    
    orchestrator = Orchestrator(fake_llm_client, tool_registry, telemetry)
    
    # Test with a question that might trigger tools
    result = orchestrator.answer("What is 1 + 1?")
    assert isinstance(result, str)


def test_orchestrator_error_handling(orchestrator):
    """Test orchestrator error handling."""
    # Test with empty input
    result = orchestrator.answer("")
    assert isinstance(result, str)
    
    # Test with very long input
    long_input = "x" * 20000
    result = orchestrator.answer(long_input)
    assert isinstance(result, str)
