"""Weather tool implementation."""
from typing import Any, Dict, Union


class WeatherTool:
    """Weather tool for getting temperature information."""
    
    def __init__(self):
        self._temps = {
            "paris": "18",
            "london": 17.0,
            "dhaka": 31,
            "amsterdam": "19.5"
        }
    
    def name(self) -> str:
        return "weather"
    
    def description(self) -> str:
        return "Get temperature information for cities"
    
    def execute(self, city: str) -> Union[str, float, int]:
        """Get temperature for a city."""
        c = (city or "").strip().lower()
        return self._temps.get(c, "20")
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Return JSON schema for the tool."""
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city to get weather for"
                    }
                },
                "required": ["city"]
            }
        }
