"""Tests for translator tool functionality."""
import pytest
from agent.adapters.tools.translator import TranslatorTool


class TestTranslatorTool:
    """Test translator tool functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool = TranslatorTool()
    
    def test_name(self):
        """Test tool name."""
        assert self.tool.name() == "translator"
    
    def test_description(self):
        """Test tool description."""
        description = self.tool.description()
        assert "translate" in description.lower()
        assert "language" in description.lower()
    
    def test_same_language_translation(self):
        """Test translation when source and target are the same."""
        result = self.tool.execute("Hello", from_lang="english", to_lang="english")
        assert result == "Hello"
    
    def test_spanish_to_english_known_phrase(self):
        """Test Spanish to English translation for known phrases."""
        result = self.tool.execute("hola", from_lang="spanish", to_lang="english")
        assert result == "hello"
        
        result = self.tool.execute("gracias", from_lang="spanish", to_lang="english")
        assert result == "thank you"
    
    def test_french_to_english_known_phrase(self):
        """Test French to English translation for known phrases."""
        result = self.tool.execute("bonjour", from_lang="french", to_lang="english")
        assert result == "hello"
        
        result = self.tool.execute("merci", from_lang="french", to_lang="english")
        assert result == "thank you"
    
    def test_german_to_english_known_phrase(self):
        """Test German to English translation for known phrases."""
        result = self.tool.execute("hallo", from_lang="german", to_lang="english")
        assert result == "hello"
        
        result = self.tool.execute("danke", from_lang="german", to_lang="english")
        assert result == "thank you"
    
    def test_english_to_spanish_reverse_lookup(self):
        """Test reverse lookup for English to Spanish."""
        result = self.tool.execute("hello", from_lang="english", to_lang="spanish")
        assert result == "hola"
    
    def test_unknown_phrase_fallback(self):
        """Test fallback for unknown phrases."""
        result = self.tool.execute("unknown phrase", from_lang="spanish", to_lang="english")
        assert "Translated from spanish to english" in result
        assert "unknown phrase" in result
    
    def test_case_insensitive_matching(self):
        """Test case insensitive phrase matching."""
        result = self.tool.execute("HOLA", from_lang="spanish", to_lang="english")
        assert result == "hello"
        
        result = self.tool.execute("Gracias", from_lang="spanish", to_lang="english")
        assert result == "thank you"
    
    def test_default_parameters(self):
        """Test default parameter values."""
        # Should use defaults: from_lang="auto", to_lang="english"
        result = self.tool.execute("test text")
        assert isinstance(result, str)
    
    def test_whitespace_handling(self):
        """Test whitespace handling in input."""
        result = self.tool.execute("  hola  ", from_lang="spanish", to_lang="english")
        assert result == "hello"
    
    def test_to_json_schema(self):
        """Test JSON schema generation."""
        schema = self.tool.to_json_schema()
        
        assert schema["name"] == "translator"
        assert "description" in schema
        assert "parameters" in schema
        
        params = schema["parameters"]
        assert params["type"] == "object"
        assert "text" in params["properties"]
        assert "from_lang" in params["properties"]
        assert "to_lang" in params["properties"]
        assert params["required"] == ["text"]
        
        # Check default values
        assert params["properties"]["from_lang"]["default"] == "auto"
        assert params["properties"]["to_lang"]["default"] == "english"
