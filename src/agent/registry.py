"""Tool registry implementation - Backward compatibility layer."""
from .core.tool_registry import registry, Tool, ToolRegistry, initialize_tools

# Initialize tools on import
initialize_tools()

# Export for backward compatibility
__all__ = ["registry", "Tool", "ToolRegistry", "initialize_tools"]
