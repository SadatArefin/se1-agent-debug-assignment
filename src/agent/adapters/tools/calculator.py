"""Calculator tool implementation."""
import re
from typing import Any, Dict


class CalculatorTool:
    
    def name(self) -> str:
        return "calc"
    
    def description(self) -> str:
        return "Evaluate mathematical expressions including percentages"
    
    def execute(self, expr: str) -> float:
        e = expr.lower().replace("what is","").strip()
        
        if "% of" in e:
            return self._percent_of(e)
        
        try:
            e = e.replace("what is", "").replace("calculate", "").strip()
            
            if "add" in e and "to" in e:
                parts = e.split("add")
                if len(parts) == 2:
                    after_add = parts[1].strip()
                    if "to" in after_add:
                        add_parts = after_add.split("to")
                        if len(add_parts) == 2:
                            num_to_add = add_parts[0].strip()
                            target = add_parts[1].strip()
                            
                            import re
                            add_match = re.search(r'(\d+(?:\.\d+)?)', num_to_add)
                            target_match = re.search(r'(\d+(?:\.\d+)?)', target)
                            
                            if add_match and target_match:
                                return float(target_match.group(1)) + float(add_match.group(1))
            
            e = e.replace("plus ", "+").replace("minus ", "-").replace("times ", "*").replace("divided by", "/")
            
            if re.match(r'^[\d\s+\-*/().%]+$', e):
                return eval(e)
            else:
                raise ValueError(f"Cannot evaluate complex expression: {expr}")
                
        except Exception as ex:
            raise ValueError(f"Invalid mathematical expression: {expr}. Error: {str(ex)}")
    
    def _percent_of(self, expr: str) -> float:
        try:
            left, right = expr.split("% of")
            x = float(left.strip())
            y = float(right.strip())
            return (x/100.0)*y
        except Exception:
            return eval(expr)
    
    def to_json_schema(self) -> Dict[str, Any]:
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
