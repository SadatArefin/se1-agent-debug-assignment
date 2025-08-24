"""Tool decorators for easy tool creation and registration."""
import inspect
from typing import Any, Dict, List, Optional, Callable, get_type_hints
from functools import wraps
from ..registry import registry


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    auto_register: bool = True
):
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        tool_description = description or (func.__doc__ or "").strip()
        
        tool_class = create_tool_from_function(func, tool_name, tool_description)
        
        tool_instance = tool_class()
        
        if auto_register:
            registry.register(tool_instance)
        
        func._tool_instance = tool_instance
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper._tool_instance = tool_instance
        return wrapper
    
    return decorator


def create_tool_from_function(func: Callable, name: str, description: str):
    """Create a tool class from a function."""
    
    class GeneratedTool:
        def __init__(self):
            self._name = name
            self._description = description
            self._func = func
            self._signature = inspect.signature(func)
            self._type_hints = get_type_hints(func)
        
        def name(self) -> str:
            return self._name
        
        def description(self) -> str:
            return self._description
        
        def execute(self, **kwargs) -> Any:
            try:
                bound_args = self._signature.bind(**kwargs)
                bound_args.apply_defaults()
                return self._func(**bound_args.arguments)
            except TypeError as e:
                raise ValueError(f"Invalid arguments for tool '{self._name}': {e}")
        
        def to_json_schema(self) -> Dict[str, Any]:
            schema = {
                "name": self._name,
                "description": self._description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            for param_name, param in self._signature.parameters.items():
                param_type = self._type_hints.get(param_name, str)
                param_schema = _python_type_to_json_schema(param_type)
                
                param_schema["description"] = _extract_param_description(
                    self._func.__doc__, param_name
                ) or f"Parameter {param_name}"
                
                schema["parameters"]["properties"][param_name] = param_schema
                
                if param.default == inspect.Parameter.empty:
                    schema["parameters"]["required"].append(param_name)
            
            return schema
    
    return GeneratedTool


def _python_type_to_json_schema(python_type) -> Dict[str, Any]:
    type_mapping = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        list: {"type": "array"},
        dict: {"type": "object"},
    }
    
    if hasattr(python_type, '__origin__'):
        if python_type.__origin__ is list:
            return {"type": "array"}
        elif python_type.__origin__ is dict:
            return {"type": "object"}
        elif python_type.__origin__ is type(None) or str(python_type).startswith('typing.Union'):
            args = getattr(python_type, '__args__', ())
            if args:
                non_none_type = next((arg for arg in args if arg is not type(None)), str)
                return _python_type_to_json_schema(non_none_type)
    
    return type_mapping.get(python_type, {"type": "string"})


def _extract_param_description(docstring: Optional[str], param_name: str) -> Optional[str]:
    if not docstring:
        return None
    
    lines = docstring.split('\n')
    for i, line in enumerate(lines):
        if f"{param_name}:" in line:
            parts = line.split(f"{param_name}:", 1)
            if len(parts) > 1:
                return parts[1].strip()
    
    return None


def auto_discover_tools(module_path: str = "src.agent.adapters.tools"):
    import importlib
    import pkgutil
    
    try:
        tools_module = importlib.import_module(module_path)
        
        # Walk through all submodules
        for importer, modname, ispkg in pkgutil.walk_packages(
            tools_module.__path__, 
            tools_module.__name__ + "."
        ):
            try:
                importlib.import_module(modname)
            except ImportError:
                # Skip modules that can't be imported
                continue
                
    except ImportError:
        # If the tools module doesn't exist, that's okay
        pass


# Convenience function to get tool instance from decorated function
def get_tool_instance(func: Callable):
    """Get the tool instance from a decorated function."""
    return getattr(func, '_tool_instance', None)
