"""Unit converter tool implementation."""
from typing import Any, Dict


class UnitConverterTool:
    """Unit conversion tool."""
    
    def name(self) -> str:
        return "unit_converter"
    
    def description(self) -> str:
        return "Convert between different units of measurement"
    
    def execute(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between units."""
        # Simple temperature conversions for now
        if from_unit.lower() == "celsius" and to_unit.lower() == "fahrenheit":
            return (value * 9/5) + 32
        elif from_unit.lower() == "fahrenheit" and to_unit.lower() == "celsius":
            return (value - 32) * 5/9
        else:
            raise ValueError(f"Conversion from {from_unit} to {to_unit} not supported")
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Return JSON schema for the tool."""
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "Value to convert"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "Unit to convert from"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "Unit to convert to"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        }
