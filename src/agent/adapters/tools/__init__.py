"""Tool adapter implementations."""
from .calculator import CalculatorTool
from .weather import WeatherTool
from .kb import KnowledgeBaseTool
from .unit_converter import UnitConverterTool

# Wire tool instances into Registry
from ...registry import registry

# Register all tools
calculator = CalculatorTool()
weather = WeatherTool()
kb = KnowledgeBaseTool()
unit_converter = UnitConverterTool()

registry.register(calculator)
registry.register(weather)
registry.register(kb)
registry.register(unit_converter)

__all__ = ["calculator", "weather", "kb", "unit_converter"]
