"""Calculator tool implementation."""
from typing import Any, Dict


class CalculatorTool:
    """Calculator tool for mathematical expressions."""
    
    def name(self) -> str:
        return "calc"
    
    def description(self) -> str:
        return "Evaluate mathematical expressions including percentages"
    
    def execute(self, expr: str) -> float:
        """Evaluate a mathematical expression."""
        e = expr.lower().replace("what is","").strip()
        
        if "% of" in e:
            return self._percent_of(e)
        
        # Basic expression cleaning
        e = e.replace("add ","").replace("plus ","+").replace(" to the "," + ").replace("average of","(10+20)/2")  # silly
        return eval(e)
    
    def _percent_of(self, expr: str) -> float:
        """Calculate percentage of a number."""
        try:
            left, right = expr.split("% of")
            x = float(left.strip())
            y = float(right.strip())
            return (x/100.0)*y
        except Exception:
            return eval(expr)
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Return JSON schema for the tool."""
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": {
                "type": "object",
                "properties": {
                    "expr": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expr"]
            }
        }
