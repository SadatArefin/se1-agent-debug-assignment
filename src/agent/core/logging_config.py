"""Comprehensive logging configuration with structured logging."""
import os
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class AgentLogger:
    """Enhanced logger for the agent system with structured logging."""
    
    def __init__(self, log_dir: str = "logs", enable_console: bool = True, log_level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.enable_console = enable_console
        
        # Create log files for different types
        self.agent_log_file = self.log_dir / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
        self.performance_log_file = self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
        self.tool_log_file = self.log_dir / f"tools_{datetime.now().strftime('%Y%m%d')}.log"
        self.error_log_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure loggers
        self._setup_loggers(log_level)
        
        # Session tracking
        self.session_id = f"session_{int(time.time())}"
        self.request_counter = 0
        
    def _setup_loggers(self, log_level: str):
        """Setup different loggers for different purposes."""
        log_level = getattr(logging, log_level.upper())
        
        # Formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Agent logger (main operations)
        self.agent_logger = logging.getLogger('agent')
        self.agent_logger.setLevel(log_level)
        agent_handler = logging.FileHandler(self.agent_log_file)
        agent_handler.setFormatter(formatter)
        self.agent_logger.addHandler(agent_handler)
        
        # Performance logger
        self.performance_logger = logging.getLogger('performance')
        self.performance_logger.setLevel(logging.INFO)
        perf_handler = logging.FileHandler(self.performance_log_file)
        perf_handler.setFormatter(formatter)
        self.performance_logger.addHandler(perf_handler)
        
        # Tool logger
        self.tool_logger = logging.getLogger('tools')
        self.tool_logger.setLevel(log_level)
        tool_handler = logging.FileHandler(self.tool_log_file)
        tool_handler.setFormatter(formatter)
        self.tool_logger.addHandler(tool_handler)
        
        # Error logger
        self.error_logger = logging.getLogger('errors')
        self.error_logger.setLevel(logging.WARNING)
        error_handler = logging.FileHandler(self.error_log_file)
        error_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_handler)
        
        # Console handler only if explicitly enabled
        if self.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.agent_logger.addHandler(console_handler)
    
    def get_request_id(self) -> str:
        """Generate a unique request ID."""
        self.request_counter += 1
        return f"{self.session_id}_req_{self.request_counter:04d}"
    
    def log_request_start(self, request_id: str, query: str) -> Dict[str, Any]:
        """Log the start of a request and return context."""
        context = {
            "request_id": request_id,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "start_time": time.time(),
            "query": query,
            "query_length": len(query)
        }
        
        self.agent_logger.info(f"REQUEST_START: {json.dumps(context)}")
        return context
    
    def log_request_end(self, context: Dict[str, Any], response: str, success: bool = True):
        """Log the end of a request with performance metrics."""
        end_time = time.time()
        latency = end_time - context["start_time"]
        
        result_context = {
            **context,
            "end_time": end_time,
            "latency_seconds": round(latency, 4),
            "latency_ms": round(latency * 1000, 2),
            "response": response,
            "response_length": len(response),
            "success": success
        }
        
        self.agent_logger.info(f"REQUEST_END: {json.dumps(result_context)}")
        
        # Log performance metrics separately
        perf_data = {
            "request_id": context["request_id"],
            "latency_ms": result_context["latency_ms"],
            "query_length": context["query_length"],
            "response_length": result_context["response_length"],
            "success": success,
            "timestamp": context["timestamp"]
        }
        self.performance_logger.info(f"PERFORMANCE: {json.dumps(perf_data)}")
    
    def log_llm_call(self, request_id: str, prompt: str, response: Any, latency: float):
        """Log LLM interaction details."""
        llm_data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "prompt_length": len(prompt),
            "response": str(response),
            "response_length": len(str(response)),
            "latency_ms": round(latency * 1000, 2)
        }
        
        self.agent_logger.info(f"LLM_CALL: {json.dumps(llm_data)}")
    
    def log_tool_execution(self, request_id: str, tool_name: str, args: Dict[str, Any], 
                          result: Any, latency: float, success: bool = True, error: str = None):
        """Log tool execution with detailed information."""
        tool_data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "args": args,
            "result": str(result)[:500] if result else None,  # Truncate long results
            "latency_ms": round(latency * 1000, 2),
            "success": success,
            "error": error
        }
        
        self.tool_logger.info(f"TOOL_EXECUTION: {json.dumps(tool_data)}")
        
        if not success and error:
            self.error_logger.error(f"TOOL_ERROR: {json.dumps(tool_data)}")
    
    def log_validation(self, request_id: str, validation_type: str, data: Any, success: bool, error: str = None):
        """Log validation operations."""
        validation_data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "validation_type": validation_type,
            "data_type": type(data).__name__,
            "data_length": len(str(data)) if data else 0,
            "success": success,
            "error": error
        }
        
        self.agent_logger.info(f"VALIDATION: {json.dumps(validation_data)}")
        
        if not success and error:
            self.error_logger.warning(f"VALIDATION_ERROR: {json.dumps(validation_data)}")
    
    def log_registry_operation(self, operation: str, tool_name: str = None, details: Dict[str, Any] = None):
        """Log tool registry operations."""
        registry_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "tool_name": tool_name,
            "details": details or {}
        }
        
        self.agent_logger.info(f"REGISTRY: {json.dumps(registry_data)}")
    
    def log_error(self, request_id: str, error_type: str, error_message: str, 
                  context: Dict[str, Any] = None, exception: Exception = None):
        """Log errors with full context."""
        error_data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
            "exception_type": type(exception).__name__ if exception else None
        }
        
        self.error_logger.error(f"ERROR: {json.dumps(error_data)}")
    
    def log_debug(self, request_id: str, component: str, message: str, data: Dict[str, Any] = None):
        """Log debug information."""
        debug_data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "message": message,
            "data": data or {}
        }
        
        self.agent_logger.debug(f"DEBUG: {json.dumps(debug_data)}")
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get a summary of log statistics."""
        summary = {
            "session_id": self.session_id,
            "total_requests": self.request_counter,
            "log_files": {
                "agent_log": str(self.agent_log_file),
                "performance_log": str(self.performance_log_file),
                "tool_log": str(self.tool_log_file),
                "error_log": str(self.error_log_file)
            },
            "log_directory": str(self.log_dir)
        }
        return summary


# Global logger instance
_logger_instance: Optional[AgentLogger] = None


def get_logger() -> AgentLogger:
    """Get the global logger instance with environment-based configuration."""
    global _logger_instance
    if _logger_instance is None:
        # Check environment variables for configuration
        import os
        log_dir = os.getenv("LOG_DIR", "logs")
        enable_console = os.getenv("ENABLE_CONSOLE_LOGGING", "false").lower() == "true"
        log_level = os.getenv("LOG_LEVEL", "INFO")
        
        _logger_instance = AgentLogger(log_dir=log_dir, enable_console=enable_console, log_level=log_level)
    return _logger_instance


def initialize_logging(log_dir: str = "logs", enable_console: bool = True, log_level: str = "INFO") -> AgentLogger:
    """Initialize the global logger with specified configuration."""
    global _logger_instance
    _logger_instance = AgentLogger(log_dir=log_dir, enable_console=enable_console, log_level=log_level)
    return _logger_instance
