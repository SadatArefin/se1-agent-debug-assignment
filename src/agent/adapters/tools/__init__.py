"""Tool adapter implementations."""
from .calculator import CalculatorTool
from .weather import WeatherTool
from .kb import KnowledgeBaseTool
from .unit_converter import UnitConverterTool
from .translator import TranslatorTool

# Wire tool instances into Registry
from ...registry import registry

# Register all tools
calculator = CalculatorTool()
weather = WeatherTool()
kb = KnowledgeBaseTool()
unit_converter = UnitConverterTool()
translator = TranslatorTool()

registry.register(calculator)
registry.register(weather)
registry.register(kb)
registry.register(unit_converter)
registry.register(translator)

__all__ = ["calculator", "weather", "kb", "unit_converter", "translator"]
