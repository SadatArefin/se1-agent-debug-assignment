"""Core protocol definitions."""
from typing import Protocol, Any, Dict, List, Optional
from abc import ABC, abstractmethod


class LLMClient(Protocol):
    """Protocol for LLM clients."""
    
    def call(self, prompt: str) -> Any:
        """Call the LLM with a prompt."""
        ...


class Tool(Protocol):
    """Protocol for tools."""
    
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


class Telemetry(Protocol):
    """Protocol for telemetry."""
    
    def log_event(self, event: str, data: Dict[str, Any]) -> None:
        """Log an event."""
        ...


class Registry(Protocol):
    """Protocol for tool registry."""
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        ...
    
    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        ...
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        ...
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        ...
