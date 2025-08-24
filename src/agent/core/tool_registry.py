"""Enhanced tool registry with auto-discovery capabilities."""
import importlib
import pkgutil
from typing import Dict, Any, List, Protocol, Optional
import logging

logger = logging.getLogger(__name__)


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
    """Enhanced registry for managing available tools with auto-discovery."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._auto_discovery_enabled = True
        # Import logging after the class is defined to avoid circular imports
        try:
            from .logging_config import get_logger
            self._logger = get_logger()
        except ImportError:
            self._logger = None
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        tool_name = tool.name()
        
        # Check if tool is already registered to avoid duplicates
        if tool_name in self._tools:
            logger.debug(f"Tool {tool_name} already registered, skipping duplicate registration")
            return
            
        self._tools[tool_name] = tool
        logger.debug(f"Registered tool: {tool_name}")
        
        # Only log to our custom logger if it's available and console logging is enabled
        if self._logger and hasattr(self._logger, 'enable_console') and self._logger.enable_console:
            self._logger.log_registry_operation("register", tool_name, {
                "description": tool.description()
            })
    
    def unregister(self, name: str) -> bool:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]
            logger.debug(f"Unregistered tool: {name}")
            
            if self._logger:
                self._logger.log_registry_operation("unregister", name)
            return True
        return False
    
    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found. Available tools: {self.list_tools()}")
        return self._tools[name]
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def get_tools_count(self) -> int:
        """Get the number of registered tools."""
        return len(self._tools)
    
    def tools_to_json(self) -> List[Dict[str, Any]]:
        """Convert all tools to JSON schema format."""
        return [tool.to_json_schema() for tool in self._tools.values()]
    
    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        logger.debug("Cleared all tools from registry")
    
    def auto_discover_tools(self, *module_paths: str) -> int:
        """
        Automatically discover and register tools from specified modules.
        
        Args:
            *module_paths: Module paths to search for tools
            
        Returns:
            int: Number of new tools discovered
        """
        if not self._auto_discovery_enabled:
            logger.debug("Auto-discovery is disabled")
            return 0
        
        initial_count = self.get_tools_count()
        
        # Default module paths if none provided
        if not module_paths:
            module_paths = [
                "src.agent.tools",
                "src.agent.adapters.tools",
            ]
        
        for module_path in module_paths:
            self._discover_from_module(module_path)
        
        discovered_count = self.get_tools_count() - initial_count
        logger.info(f"Auto-discovered {discovered_count} tools from {len(module_paths)} modules")
        return discovered_count
    
    def _discover_from_module(self, module_path: str) -> None:
        """Discover tools from a specific module."""
        try:
            # Import the module to trigger any @tool decorators
            module = importlib.import_module(module_path)
            logger.debug(f"Successfully imported module: {module_path}")
            
            # If it's a package, walk through submodules
            if hasattr(module, '__path__'):
                for importer, modname, ispkg in pkgutil.walk_packages(
                    module.__path__, 
                    module.__name__ + "."
                ):
                    try:
                        importlib.import_module(modname)
                        logger.debug(f"Imported submodule: {modname}")
                    except ImportError as e:
                        logger.warning(f"Failed to import submodule {modname}: {e}")
                        continue
                        
        except ImportError as e:
            logger.warning(f"Failed to import module {module_path}: {e}")
    
    def enable_auto_discovery(self) -> None:
        """Enable auto-discovery of tools."""
        self._auto_discovery_enabled = True
    
    def disable_auto_discovery(self) -> None:
        """Disable auto-discovery of tools."""
        self._auto_discovery_enabled = False
    
    def get_tool_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a tool."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found")
        
        tool = self._tools[name]
        return {
            "name": tool.name(),
            "description": tool.description(),
            "schema": tool.to_json_schema()
        }
    
    def search_tools(self, query: str) -> List[str]:
        """Search for tools by name or description."""
        query_lower = query.lower()
        matching_tools = []
        
        for tool_name, tool in self._tools.items():
            if (query_lower in tool_name.lower() or 
                query_lower in tool.description().lower()):
                matching_tools.append(tool_name)
        
        return matching_tools


# Global registry instance
registry = ToolRegistry()


def initialize_tools() -> None:
    """Initialize and discover all available tools."""
    logger.info("Initializing tool registry...")
    
    # Auto-discover tools from both old and new locations
    discovered = registry.auto_discover_tools(
        "src.agent.tools",           # New decorator-based tools
        "src.agent.adapters.tools"   # Legacy class-based tools
    )
    
    logger.info(f"Tool registry initialized with {registry.get_tools_count()} tools")
    if discovered > 0:
        logger.info(f"Discovered {discovered} new tools")
    
    # Log all registered tools
    tools = registry.list_tools()
    if tools:
        logger.info(f"Available tools: {', '.join(tools)}")
    else:
        logger.warning("No tools registered!")


# Convenience functions
def get_tool(name: str) -> Tool:
    """Get a tool by name from the global registry."""
    return registry.get_tool(name)


def list_tools() -> List[str]:
    """List all available tools."""
    return registry.list_tools()


def register_tool(tool: Tool) -> None:
    """Register a tool with the global registry."""
    registry.register(tool)
