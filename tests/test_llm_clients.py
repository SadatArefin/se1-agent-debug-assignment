"""Tests for LLM clients."""
import pytest
from src.agent.adapters.llm.fake_client import FakeClient
from src.agent.adapters.llm.openai_client import OpenAIClient


class TestFakeClient:
    """Tests for the fake LLM client."""
    
    def test_fake_client_basic(self):
        """Test basic fake client functionality."""
        client = FakeClient()
        result = client.call("Hello")
        assert result is not None
    
    def test_fake_client_weather_detection(self):
        """Test that fake client can detect weather requests."""
        client = FakeClient()
        # Run multiple times since it's probabilistic
        results = []
        for _ in range(10):
            result = client.call("What's the weather in Paris?")
            results.append(result)
        
        # At least one should be a proper tool call or weather-related
        has_weather_response = any(
            (isinstance(r, dict) and r.get("tool") == "weather") or
            (isinstance(r, str) and ("weather" in r.lower() or "paris" in r.lower()))
            for r in results
        )
        assert has_weather_response
    
    def test_fake_client_calc_detection(self):
        """Test that fake client can detect calculation requests."""
        client = FakeClient()
        # Run multiple times since it's probabilistic
        results = []
        for _ in range(10):
            result = client.call("What is 1 + 1?")
            results.append(result)
        
        # At least one should be a proper tool call or calc-related
        has_calc_response = any(
            (isinstance(r, dict) and r.get("tool") == "calc") or
            (isinstance(r, str) and ("calc" in r.lower() or "+" in r))
            for r in results
        )
        assert has_calc_response
    
    def test_fake_client_kb_detection(self):
        """Test that fake client can detect knowledge base requests."""
        client = FakeClient()
        # Run multiple times since it's probabilistic
        results = []
        for _ in range(10):
            result = client.call("Who is Ada Lovelace?")
            results.append(result)
        
        # At least one should be KB-related or direct answer
        has_kb_response = any(
            (isinstance(r, dict) and r.get("tool") == "kb") or
            (isinstance(r, str) and "ada lovelace" in r.lower())
            for r in results
        )
        assert has_kb_response


class TestOpenAIClient:
    """Tests for the OpenAI client."""
    
    def test_openai_client_initialization(self):
        """Test OpenAI client initialization."""
        client = OpenAIClient("test-api-key")
        assert client.api_key == "test-api-key"
    
    def test_openai_client_not_implemented(self):
        """Test that OpenAI client raises NotImplementedError."""
        client = OpenAIClient("test-api-key")
        with pytest.raises(NotImplementedError):
            client.call("test prompt")
