"""Tests for input guards functionality."""
import pytest
from agent.core.input_guards import InputGuards
from agent.config import config


class TestInputGuards:
    """Test input validation and sanitization."""
    
    def test_trim_and_validate_basic(self):
        """Test basic trimming and validation."""
        text = "  Hello, world!  "
        result = InputGuards.trim_and_validate(text)
        assert result == "Hello, world!"
    
    def test_trim_and_validate_whitespace_normalization(self):
        """Test whitespace normalization."""
        text = "Hello    world\n\ntest"
        result = InputGuards.trim_and_validate(text)
        assert result == "Hello world test"
    
    def test_trim_and_validate_length_limit(self):
        """Test length limiting."""
        text = "a" * 1000
        result = InputGuards.trim_and_validate(text, max_length=100)
        assert len(result) == 100
    
    def test_trim_and_validate_min_length_error(self):
        """Test minimum length validation."""
        with pytest.raises(ValueError, match="Input too short"):
            InputGuards.trim_and_validate("", max_length=1000)
    
    def test_trim_and_validate_non_string_error(self):
        """Test non-string input error."""
        with pytest.raises(ValueError, match="Input must be a string"):
            InputGuards.trim_and_validate(123)
    
    def test_sanitize_harmful_patterns(self):
        """Test removal of harmful patterns."""
        text = "Hello <script>alert('xss')</script> world"
        result = InputGuards.trim_and_validate(text)
        assert "<script>" not in result
        assert "alert" not in result
    
    def test_validate_tool_name_valid(self):
        """Test valid tool name validation."""
        assert InputGuards.validate_tool_name("calculator")
        assert InputGuards.validate_tool_name("unit_converter")
        assert InputGuards.validate_tool_name("my_tool_123")
    
    def test_validate_tool_name_invalid(self):
        """Test invalid tool name validation."""
        assert not InputGuards.validate_tool_name("123invalid")
        assert not InputGuards.validate_tool_name("tool-name")
        assert not InputGuards.validate_tool_name("tool.name")
        assert not InputGuards.validate_tool_name("")
        assert not InputGuards.validate_tool_name(None)
    
    def test_validate_tool_args_valid(self):
        """Test valid tool arguments validation."""
        args = {"param1": "value1", "param2": 123}
        result = InputGuards.validate_tool_args(args)
        assert result == args
    
    def test_validate_tool_args_string_sanitization(self):
        """Test string argument sanitization."""
        args = {"param": "  value  with   spaces  "}
        result = InputGuards.validate_tool_args(args)
        assert result["param"] == "value with spaces"
    
    def test_validate_tool_args_invalid_key(self):
        """Test invalid argument key."""
        with pytest.raises(ValueError, match="Tool argument key must be string"):
            InputGuards.validate_tool_args({123: "value"})
    
    def test_validate_tool_args_non_dict(self):
        """Test non-dict arguments."""
        with pytest.raises(ValueError, match="Tool arguments must be a dictionary"):
            InputGuards.validate_tool_args("not a dict")
