"""Tests for state machine orchestrator functionality."""
import pytest
from unittest.mock import Mock, MagicMock
from agent.core.orchestrator import Orchestrator, AgentState
from agent.core.policies import PolicyManager
from agent.registry import ToolRegistry
from agent.adapters.tools.calculator import CalculatorTool


class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self, responses=None):
        self.responses = responses or []
        self.call_count = 0
    
    def call(self, prompt: str):
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        return "Default response"


class TestOrchestrator:
    """Test orchestrator state machine functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()
        self.telemetry = Mock()
        self.policy_manager = PolicyManager()
        
        # Register a calculator tool for testing
        calc_tool = CalculatorTool()
        self.registry.register(calc_tool)
    
    def test_simple_question_no_tool(self):
        """Test simple question that doesn't require tools."""
        llm_client = MockLLMClient(["This is a simple answer"])
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, self.policy_manager)
        
        result = orchestrator.answer("What is the capital of France?")
        
        assert isinstance(result, str)
        assert "simple answer" in result
    
    def test_tool_call_execution(self):
        """Test execution of a tool call."""
        # LLM returns a tool call, then we don't need another LLM call
        llm_client = MockLLMClient([{"tool": "calc", "args": {"expr": "2 + 2"}}])
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, self.policy_manager)
        
        result = orchestrator.answer("What is 2 + 2?")
        
        assert isinstance(result, str)
        # The result should contain the calculation result
        assert "4" in result or "4.0" in result
    
    def test_malformed_json_tool_call(self):
        """Test handling of malformed JSON tool calls."""
        # Return malformed JSON that should be parsed by guardrails
        llm_client = MockLLMClient(['{"tool": "calc", "args": {"expr": "1 + 1"'])
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, self.policy_manager)
        
        result = orchestrator.answer("Calculate 1 + 1")
        
        assert isinstance(result, str)
        # Should handle the malformed JSON gracefully
    
    def test_invalid_tool_name(self):
        """Test handling of invalid tool names."""
        llm_client = MockLLMClient([{"tool": "nonexistent_tool", "args": {}}])
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, self.policy_manager)
        
        result = orchestrator.answer("Use a nonexistent tool")
        
        assert isinstance(result, str)
        # Should contain an error message
        assert "error" in result.lower() or "Error" in result
    
    def test_state_transitions(self):
        """Test state machine transitions."""
        llm_client = MockLLMClient([{"tool": "calc", "args": {"expr": "5 * 5"}}])
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, self.policy_manager)
        
        # Initial state should be CALL_LLM
        assert orchestrator.current_state == AgentState.CALL_LLM
        
        result = orchestrator.answer("Calculate 5 * 5")
        
        # After execution, should be in DONE state
        assert orchestrator.current_state == AgentState.DONE
        assert isinstance(result, str)
    
    def test_step_limit_enforcement(self):
        """Test that step limits are enforced."""
        # Create a policy with very low step limit
        from agent.core.policies import ExecutionPolicy
        policy_manager = PolicyManager(execution_policy=ExecutionPolicy(max_steps=1))
        
        llm_client = MockLLMClient([{"tool": "calc", "args": {"expr": "1 + 1"}}])
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, policy_manager)
        
        result = orchestrator.answer("Calculate something")
        
        # Should complete but might be limited by steps
        assert isinstance(result, str)
    
    def test_telemetry_logging(self):
        """Test that telemetry events are logged."""
        llm_client = MockLLMClient([{"tool": "calc", "args": {"expr": "3 + 3"}}])
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, self.policy_manager)
        
        result = orchestrator.answer("Calculate 3 + 3")
        
        # Verify telemetry was called
        self.telemetry.log_event.assert_called()
        
        # Check for specific events
        call_args_list = [call[0] for call in self.telemetry.log_event.call_args_list]
        events = [args[0] for args in call_args_list]
        assert "question_received" in events
    
    def test_conversation_history_tracking(self):
        """Test that conversation history is tracked."""
        llm_client = MockLLMClient(["Just a simple response"])
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, self.policy_manager)
        
        orchestrator.answer("Test question")
        
        # Should have user message in history
        assert len(orchestrator.conversation_history) > 0
        assert orchestrator.conversation_history[0].role == "user"
        assert orchestrator.conversation_history[0].content == "Test question"
    
    def test_input_sanitization(self):
        """Test that input is properly sanitized."""
        llm_client = MockLLMClient(["Clean response"])
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, self.policy_manager)
        
        # Input with extra whitespace and length
        dirty_input = "   What is   2 + 2?   "
        result = orchestrator.answer(dirty_input)
        
        # Should handle the input gracefully
        assert isinstance(result, str)
        
        # Check that sanitized input was used
        assert orchestrator.conversation_history[0].content == "What is 2 + 2?"
    
    def test_error_handling(self):
        """Test error handling in orchestrator."""
        # Mock LLM that raises an exception
        llm_client = Mock()
        llm_client.call.side_effect = Exception("LLM Error")
        
        orchestrator = Orchestrator(llm_client, self.registry, self.telemetry, self.policy_manager)
        
        result = orchestrator.answer("Test question")
        
        assert isinstance(result, str)
        assert "Error" in result
