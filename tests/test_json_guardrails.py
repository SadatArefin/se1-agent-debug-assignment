"""Tests for JSON guardrails and repair functionality."""
import pytest
from agent.core.guardrails import (
    sanitize_input,
    validate_tool_call,
    repair_json,
    extract_tool_call_from_text,
    validate_output
)


class TestInputSanitization:
    """Tests for input sanitization."""
    
    def test_sanitize_basic(self):
        """Test basic input sanitization."""
        result = sanitize_input("  hello world  ")
        assert result == "hello world"
    
    def test_sanitize_too_long(self):
        """Test input that's too long gets truncated."""
        long_input = "x" * 20000
        result = sanitize_input(long_input)
        assert len(result) == 10000
    
    def test_sanitize_invalid_type(self):
        """Test that non-string input raises error."""
        with pytest.raises(ValueError):
            sanitize_input(123)


class TestToolCallValidation:
    """Tests for tool call validation."""
    
    def test_validate_valid_tool_call(self):
        """Test validation of valid tool call."""
        valid_call = {"tool": "calc", "args": {"expr": "1+1"}}
        assert validate_tool_call(valid_call) is True
    
    def test_validate_invalid_tool_call(self):
        """Test validation of invalid tool calls."""
        assert validate_tool_call({}) is False
        assert validate_tool_call({"args": {}}) is False
        assert validate_tool_call("not a dict") is False


class TestJSONRepair:
    """Tests for JSON repair functionality."""
    
    def test_repair_valid_json(self):
        """Test that valid JSON passes through unchanged."""
        valid_json = '{"tool": "calc", "args": {"expr": "1+1"}}'
        result = repair_json(valid_json)
        assert result == {"tool": "calc", "args": {"expr": "1+1"}}
    
    def test_repair_missing_brace(self):
        """Test repair of JSON missing closing brace."""
        broken_json = '{"tool": "calc", "args": {"expr": "1+1"}'
        result = repair_json(broken_json)
        assert result is not None
        assert "tool" in result
    
    def test_repair_trailing_comma(self):
        """Test repair of JSON with trailing comma."""
        broken_json = '{"tool": "calc", "args": {"expr": "1+1",},}'
        result = repair_json(broken_json)
        assert result is not None
        assert "tool" in result
    
    def test_repair_completely_broken(self):
        """Test that completely broken JSON returns None."""
        broken_json = "this is not json at all"
        result = repair_json(broken_json)
        assert result is None


class TestToolCallExtraction:
    """Tests for tool call extraction from text."""
    
    def test_extract_from_json(self):
        """Test extraction from JSON text."""
        json_text = '{"tool": "calc", "args": {"expr": "1+1"}}'
        result = extract_tool_call_from_text(json_text)
        assert result["tool"] == "calc"
        assert result["args"]["expr"] == "1+1"
    
    def test_extract_from_special_format(self):
        """Test extraction from special TOOL:name format."""
        special_text = 'TOOL:calc EXPR="1+1"'
        result = extract_tool_call_from_text(special_text)
        assert result["tool"] == "calc"
        assert result["args"]["expr"] == "1+1"
    
    def test_extract_from_invalid(self):
        """Test extraction from invalid text."""
        invalid_text = "just some random text"
        result = extract_tool_call_from_text(invalid_text)
        assert result is None


class TestOutputValidation:
    """Tests for output validation."""
    
    def test_validate_string_output(self):
        """Test validation of string output."""
        result = validate_output("hello world")
        assert result == "hello world"
    
    def test_validate_number_output(self):
        """Test validation of number output."""
        assert validate_output(42) == "42"
        assert validate_output(3.14) == "3.14"
    
    def test_validate_none_output(self):
        """Test validation of None output."""
        result = validate_output(None)
        assert result == "No result"
    
    def test_validate_complex_output(self):
        """Test validation of complex object output."""
        complex_obj = {"key": "value", "number": 42}
        result = validate_output(complex_obj)
        assert "key" in result
        assert "value" in result
