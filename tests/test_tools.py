"""Tests for tool implementations."""
import pytest
from src.agent.adapters.tools.calculator import CalculatorTool
from src.agent.adapters.tools.weather import WeatherTool
from src.agent.adapters.tools.kb import KnowledgeBaseTool
from src.agent.adapters.tools.unit_converter import UnitConverterTool


class TestCalculatorTool:
    """Tests for the calculator tool."""
    
    def test_calculator_basic(self):
        """Test basic calculator operations."""
        calc = CalculatorTool()
        assert calc.name() == "calc"
        assert calc.execute("1 + 1") == 2
        assert calc.execute("10 * 5") == 50
    
    def test_calculator_percentage(self):
        """Test percentage calculations."""
        calc = CalculatorTool()
        result = calc.execute("10% of 100")
        assert result == 10.0
    
    def test_calculator_json_schema(self):
        """Test calculator JSON schema."""
        calc = CalculatorTool()
        schema = calc.to_json_schema()
        assert schema["name"] == "calc"
        assert "parameters" in schema


class TestWeatherTool:
    """Tests for the weather tool."""
    
    def test_weather_basic(self):
        """Test basic weather functionality."""
        weather = WeatherTool()
        assert weather.name() == "weather"
        temp = weather.execute("paris")
        assert temp == "18"
    
    def test_weather_unknown_city(self):
        """Test weather for unknown city."""
        weather = WeatherTool()
        temp = weather.execute("unknown_city")
        assert temp == "20"  # Default temperature
    
    def test_weather_json_schema(self):
        """Test weather JSON schema."""
        weather = WeatherTool()
        schema = weather.to_json_schema()
        assert schema["name"] == "weather"
        assert "parameters" in schema


class TestKnowledgeBaseTool:
    """Tests for the knowledge base tool."""
    
    def test_kb_basic(self):
        """Test basic KB functionality."""
        kb = KnowledgeBaseTool()
        assert kb.name() == "kb"
        # Note: This might fail if kb.json doesn't exist, but that's okay for structure testing
    
    def test_kb_json_schema(self):
        """Test KB JSON schema."""
        kb = KnowledgeBaseTool()
        schema = kb.to_json_schema()
        assert schema["name"] == "kb"
        assert "parameters" in schema


class TestUnitConverterTool:
    """Tests for the unit converter tool."""
    
    def test_unit_converter_basic(self):
        """Test basic unit conversion."""
        converter = UnitConverterTool()
        assert converter.name() == "unit_converter"
        
        # Test Celsius to Fahrenheit
        result = converter.execute(0, "celsius", "fahrenheit")
        assert result == 32.0
        
        # Test Fahrenheit to Celsius
        result = converter.execute(32, "fahrenheit", "celsius")
        assert result == 0.0
    
    def test_unit_converter_unsupported(self):
        """Test unsupported unit conversion."""
        converter = UnitConverterTool()
        with pytest.raises(ValueError):
            converter.execute(100, "unsupported", "also_unsupported")
    
    def test_unit_converter_json_schema(self):
        """Test unit converter JSON schema."""
        converter = UnitConverterTool()
        schema = converter.to_json_schema()
        assert schema["name"] == "unit_converter"
        assert "parameters" in schema
