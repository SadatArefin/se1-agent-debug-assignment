"""Tests for LLM clients."""
import pytest
from agent.adapters.llm.fake_client import FakeClient


class TestFakeClient:
    
    def test_fake_client_basic(self):
        client = FakeClient()
        result = client.call("Hello")
        assert result is not None
    
    def test_fake_client_weather_detection(self):
        client = FakeClient()
        results = []
        for _ in range(10):
            result = client.call("What's the weather in Paris?")
            results.append(result)
        
        has_weather_response = any(
            (isinstance(r, dict) and r.get("tool") == "weather") or
            (isinstance(r, str) and ("weather" in r.lower() or "paris" in r.lower()))
            for r in results
        )
        assert has_weather_response
    
    def test_fake_client_calc_detection(self):
        client = FakeClient()
        results = []
        for _ in range(10):
            result = client.call("What is 1 + 1?")
            results.append(result)
        
        has_calc_response = any(
            (isinstance(r, dict) and r.get("tool") == "calc") or
            (isinstance(r, str) and ("calc" in r.lower() or "+" in r))
            for r in results
        )
        assert has_calc_response
    
    def test_fake_client_kb_detection(self):
        client = FakeClient()
        results = []
        for _ in range(10):
            result = client.call("Who is Ada Lovelace?")
            results.append(result)
        
        has_kb_response = any(
            (isinstance(r, dict) and r.get("tool") == "kb") or
            (isinstance(r, str) and "ada lovelace" in r.lower())
            for r in results
        )
        assert has_kb_response
