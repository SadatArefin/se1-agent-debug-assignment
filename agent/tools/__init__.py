"""Legacy tools compatibility layer."""
from src.agent.adapters.tools import calculator, weather, kb

# Legacy functions for backward compatibility
def evaluate(expr: str) -> float:
    """Legacy evaluate function."""
    return calculator.execute(expr)

def temp(city: str):
    """Legacy temp function."""
    return weather.execute(city)

def kb_lookup(q: str) -> str:
    """Legacy kb_lookup function."""
    return kb.execute(q)
