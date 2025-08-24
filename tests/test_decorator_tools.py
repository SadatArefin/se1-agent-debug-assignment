"""Tests for the new decorator-based tool system."""
import pytest
from src.agent.core.decorators import tool, get_tool_instance
from src.agent.core.tool_registry import ToolRegistry


def test_tool_decorator_basic():
    """Test basic tool decorator functionality."""
    
    @tool(name="test_tool", description="A test tool")
    def test_function(param: str) -> str:
        """Test function."""
        return f"Hello {param}!"
    
    # Get the tool instance
    tool_instance = get_tool_instance(test_function)
    
    assert tool_instance is not None
    assert tool_instance.name() == "test_tool"
    assert tool_instance.description() == "A test tool"
    
    # Test execution
    result = tool_instance.execute(param="World")
    assert result == "Hello World!"


def test_tool_decorator_auto_name():
    """Test tool decorator with automatic name inference."""
    
    @tool(description="Auto-named tool")
    def my_auto_tool(x: int, y: int = 5) -> int:
        """Adds two numbers."""
        return x + y
    
    tool_instance = get_tool_instance(my_auto_tool)
    
    assert tool_instance.name() == "my_auto_tool"
    assert tool_instance.description() == "Auto-named tool"
    
    # Test with default parameter
    result = tool_instance.execute(x=10)
    assert result == 15


def test_tool_decorator_auto_description():
    """Test tool decorator with automatic description from docstring."""
    
    @tool(name="docstring_tool")
    def docstring_function(message: str) -> str:
        """This description comes from the docstring."""
        return f"Message: {message}"
    
    tool_instance = get_tool_instance(docstring_function)
    
    assert tool_instance.name() == "docstring_tool"
    assert tool_instance.description() == "This description comes from the docstring."


def test_tool_json_schema_generation():
    """Test automatic JSON schema generation."""
    
    @tool(name="schema_test", description="Test schema generation")
    def schema_function(text: str, count: int = 3, enabled: bool = True) -> str:
        """
        Test function with various parameter types.
        
        Args:
            text: The input text
            count: Number of repetitions
            enabled: Whether the function is enabled
        """
        if enabled:
            return text * count
        return ""
    
    tool_instance = get_tool_instance(schema_function)
    schema = tool_instance.to_json_schema()
    
    assert schema["name"] == "schema_test"
    assert schema["description"] == "Test schema generation"
    
    props = schema["parameters"]["properties"]
    assert props["text"]["type"] == "string"
    assert props["count"]["type"] == "integer"
    assert props["enabled"]["type"] == "boolean"
    
    # Check required parameters (those without defaults)
    assert "text" in schema["parameters"]["required"]
    assert "count" not in schema["parameters"]["required"]
    assert "enabled" not in schema["parameters"]["required"]


def test_tool_parameter_validation():
    """Test parameter validation during execution."""
    
    @tool(name="validation_test")
    def validation_function(required_param: str, optional_param: int = 42) -> str:
        """Test parameter validation."""
        return f"{required_param}: {optional_param}"
    
    tool_instance = get_tool_instance(validation_function)
    
    # Valid execution
    result = tool_instance.execute(required_param="test")
    assert result == "test: 42"
    
    # Valid execution with optional parameter
    result = tool_instance.execute(required_param="test", optional_param=100)
    assert result == "test: 100"
    
    # Invalid execution - missing required parameter
    with pytest.raises(ValueError, match="Invalid arguments"):
        tool_instance.execute(optional_param=100)


def test_tool_registry_integration():
    """Test that tools are automatically registered."""
    # Create a local registry for testing
    test_registry = ToolRegistry()
    
    # This should NOT auto-register since we specify auto_register=False
    @tool(name="manual_tool", auto_register=False)
    def manual_tool() -> str:
        return "manually registered"
    
    # Check it's not in any registry
    assert not test_registry.has_tool("manual_tool")
    
    # Manually register it
    tool_instance = get_tool_instance(manual_tool)
    test_registry.register(tool_instance)
    
    # Now it should be available
    assert test_registry.has_tool("manual_tool")
    retrieved_tool = test_registry.get_tool("manual_tool")
    assert retrieved_tool.execute() == "manually registered"


def test_complex_tool_example():
    """Test a more complex tool with multiple parameter types."""
    
    @tool(name="complex_tool", description="A complex tool with various parameters")
    def complex_tool(
        text: str,
        multiplier: int = 2,
        uppercase: bool = False,
        separator: str = " "
    ) -> str:
        """
        Complex tool that manipulates text.
        
        Args:
            text: The input text to process
            multiplier: How many times to repeat the text
            uppercase: Whether to convert to uppercase
            separator: String to join repeated text
        """
        result = separator.join([text] * multiplier)
        if uppercase:
            result = result.upper()
        return result
    
    tool_instance = get_tool_instance(complex_tool)
    
    # Test basic functionality
    result = tool_instance.execute(text="hello")
    assert result == "hello hello"
    
    # Test with all parameters
    result = tool_instance.execute(
        text="hello",
        multiplier=3,
        uppercase=True,
        separator="-"
    )
    assert result == "HELLO-HELLO-HELLO"


def test_tool_error_handling():
    """Test error handling in tool execution."""
    
    @tool(name="error_tool")
    def error_tool(should_error: bool = False) -> str:
        """Tool that can raise errors."""
        if should_error:
            raise ValueError("Intentional error")
        return "success"
    
    tool_instance = get_tool_instance(error_tool)
    
    # Normal execution
    result = tool_instance.execute(should_error=False)
    assert result == "success"
    
    # Error execution - should propagate the error
    with pytest.raises(ValueError, match="Intentional error"):
        tool_instance.execute(should_error=True)


if __name__ == "__main__":
    # Run the tests manually
    import sys
    import traceback
    
    test_functions = [
        test_tool_decorator_basic,
        test_tool_decorator_auto_name,
        test_tool_decorator_auto_description,
        test_tool_json_schema_generation,
        test_tool_parameter_validation,
        test_tool_registry_integration,
        test_complex_tool_example,
        test_tool_error_handling,
    ]
    
    print("🧪 Testing decorator-based tool system...")
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            print(f"  Running {test_func.__name__}...", end=" ")
            test_func()
            print("✅ PASS")
            passed += 1
        except Exception as e:
            print(f"❌ FAIL: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The decorator system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
