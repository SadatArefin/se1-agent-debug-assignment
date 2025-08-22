"""Tool registry implementation."""
from typing import Dict, Any, List, Protocol
import json


class Tool(Protocol):
    """Tool protocol definition."""
    
    def name(self) -> str:
        """Return the tool name."""
        ...
    
    def description(self) -> str:
        """Return the tool description."""
        ...
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given arguments."""
        ...
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Return JSON schema for the tool."""
        ...


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name()] = tool
    
    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found")
        return self._tools[name]
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def tools_to_json(self) -> List[Dict[str, Any]]:
        """Convert all tools to JSON schema format."""
        return [tool.to_json_schema() for tool in self._tools.values()]


# Global registry instance
registry = ToolRegistry()
