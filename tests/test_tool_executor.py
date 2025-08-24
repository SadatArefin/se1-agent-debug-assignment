"""Tests for tool executor functionality."""
import pytest
from unittest.mock import Mock, MagicMock
from agent.core.tool_executor import ToolExecutor
from agent.core.schemas import ToolCall, ToolResult
from agent.registry import ToolRegistry


class MockTool:
    """Mock tool for testing."""
    
    def __init__(self, name: str, result: str = "test result"):
        self._name = name
        self._result = result
    
    def name(self) -> str:
        return self._name
    
    def description(self) -> str:
        return f"Mock tool {self._name}"
    
    def execute(self, **kwargs):
        if "error" in kwargs:
            raise Exception("Tool execution error")
        return self._result
    
    def to_json_schema(self):
        return {"name": self._name, "description": self.description()}


class TestToolExecutor:
    """Test tool executor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()
        self.telemetry = Mock()
        self.executor = ToolExecutor(self.registry, self.telemetry)
        
        # Register a mock tool
        self.mock_tool = MockTool("test_tool")
        self.registry.register(self.mock_tool)
    
    def test_execute_successful_tool_call(self):
        """Test successful tool execution."""
        tool_call = ToolCall(tool="test_tool", args={"param": "value"}, id="test_id")
        
        result = self.executor.execute(tool_call)
        
        assert isinstance(result, ToolResult)
        assert result.tool_call_id == "test_id"
        assert result.result == "test result"
        assert result.error is None
        
        # Verify telemetry calls
        self.telemetry.start_span.assert_called_once()
        self.telemetry.end_span.assert_called_once()
    
    def test_execute_tool_error(self):
        """Test tool execution with error."""
        tool_call = ToolCall(tool="test_tool", args={"error": True}, id="test_id")
        
        result = self.executor.execute(tool_call)
        
        assert isinstance(result, ToolResult)
        assert result.tool_call_id == "test_id"
        assert result.result is None
        assert "Tool execution error" in result.error
        
        # Verify telemetry calls
        self.telemetry.start_span.assert_called_once()
        self.telemetry.end_span.assert_called_once()
    
    def test_execute_invalid_tool_name(self):
        """Test execution with invalid tool name."""
        tool_call = ToolCall(tool="invalid-tool", args={}, id="test_id")
        
        result = self.executor.execute(tool_call)
        
        assert isinstance(result, ToolResult)
        assert result.error is not None
        assert "Invalid tool name" in result.error
    
    def test_execute_nonexistent_tool(self):
        """Test execution with nonexistent tool."""
        tool_call = ToolCall(tool="nonexistent", args={}, id="test_id")
        
        result = self.executor.execute(tool_call)
        
        assert isinstance(result, ToolResult)
        assert result.error is not None
        assert "Tool execution error" in result.error
    
    def test_validate_tool_call_valid(self):
        """Test validation of valid tool call."""
        tool_call = ToolCall(tool="test_tool", args={"param": "value"})
        
        is_valid = self.executor.validate_tool_call(tool_call)
        
        assert is_valid is True
    
    def test_validate_tool_call_invalid_name(self):
        """Test validation of tool call with invalid name."""
        tool_call = ToolCall(tool="invalid-name", args={})
        
        is_valid = self.executor.validate_tool_call(tool_call)
        
        assert is_valid is False
    
    def test_validate_tool_call_nonexistent_tool(self):
        """Test validation of tool call with nonexistent tool."""
        tool_call = ToolCall(tool="nonexistent", args={})
        
        is_valid = self.executor.validate_tool_call(tool_call)
        
        assert is_valid is False
    
    def test_execute_without_telemetry(self):
        """Test execution without telemetry."""
        executor = ToolExecutor(self.registry, telemetry=None)
        tool_call = ToolCall(tool="test_tool", args={"param": "value"})
        
        result = executor.execute(tool_call)
        
        assert isinstance(result, ToolResult)
        assert result.result == "test result"
