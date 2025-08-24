"""Enhanced telemetry implementation with comprehensive logging."""
import time
from typing import Any, Dict, Optional
from ...core.contracts import Telemetry
from ...core.logging_config import get_logger


class EnhancedTelemetry:
    """Enhanced telemetry implementation with structured logging."""
    
    def __init__(self, enabled: bool = True, request_id: str = None):
        self.enabled = enabled
        self.logger = get_logger()
        self.request_id = request_id
        self._spans = {}  # Track active spans for timing
    
    def set_request_id(self, request_id: str):
        """Set the current request ID for context."""
        self.request_id = request_id
    
    def log_event(self, event: str, data: Dict[str, Any]) -> None:
        """Log a telemetry event."""
        if not self.enabled:
            return
        
        # Add request context
        event_data = {
            **data,
            "request_id": self.request_id,
            "event_type": event
        }
        
        # Route to appropriate logging method based on event type
        if event == "question_received":
            self._log_question_received(event_data)
        elif event == "tool_executed":
            self._log_tool_executed(event_data)
        elif event == "tool_error":
            self._log_tool_error(event_data)
        elif event == "error":
            self._log_error(event_data)
        elif event.startswith("validation_"):
            self._log_validation(event_data)
        elif event.startswith("registry_"):
            self._log_registry(event_data)
        else:
            # Generic event logging
            self.logger.log_debug(self.request_id, "telemetry", f"Event: {event}", event_data)
    
    def start_span(self, span_name: str, context: Dict[str, Any] = None) -> str:
        """Start a timing span."""
        span_id = f"{span_name}_{int(time.time() * 1000000)}"  # microsecond precision
        self._spans[span_id] = {
            "name": span_name,
            "start_time": time.time(),
            "context": context or {}
        }
        
        self.logger.log_debug(
            self.request_id, 
            "telemetry", 
            f"Span started: {span_name}",
            {"span_id": span_id, "context": context}
        )
        
        return span_id
    
    def end_span(self, span_id: str, result: Any = None, error: str = None) -> float:
        """End a timing span and return the duration."""
        if span_id not in self._spans:
            self.logger.log_error(
                self.request_id, 
                "telemetry_error", 
                f"Attempted to end unknown span: {span_id}"
            )
            return 0.0
        
        span = self._spans.pop(span_id)
        duration = time.time() - span["start_time"]
        
        # Log span completion
        span_data = {
            "span_id": span_id,
            "span_name": span["name"],
            "duration_ms": round(duration * 1000, 2),
            "success": error is None,
            "error": error,
            "context": span["context"]
        }
        
        if span["name"] == "tool_execution":
            # Special handling for tool execution spans
            self.logger.log_tool_execution(
                self.request_id,
                span["context"].get("tool_name", "unknown"),
                span["context"].get("args", {}),
                result,
                duration,
                success=error is None,
                error=error
            )
        else:
            self.logger.log_debug(
                self.request_id,
                "telemetry",
                f"Span completed: {span['name']}",
                span_data
            )
        
        return duration
    
    def _log_question_received(self, data: Dict[str, Any]):
        """Log question received event."""
        self.logger.log_debug(
            self.request_id,
            "orchestrator",
            "Question received",
            {
                "question": data.get("question", ""),
                "question_length": len(data.get("question", ""))
            }
        )
    
    def _log_tool_executed(self, data: Dict[str, Any]):
        """Log tool execution event."""
        # This is handled by the span system, but we can add additional context
        self.logger.log_debug(
            self.request_id,
            "tool_executor",
            f"Tool executed: {data.get('tool', 'unknown')}",
            {
                "tool": data.get("tool"),
                "args": data.get("args", {}),
                "result_preview": data.get("result", "")[:100]
            }
        )
    
    def _log_tool_error(self, data: Dict[str, Any]):
        """Log tool error event."""
        self.logger.log_error(
            self.request_id,
            "tool_execution_error",
            data.get("error", "Unknown tool error"),
            context={
                "tool": data.get("tool"),
                "args": data.get("args", {})
            }
        )
    
    def _log_error(self, data: Dict[str, Any]):
        """Log general error event."""
        self.logger.log_error(
            self.request_id,
            "general_error",
            data.get("error", "Unknown error"),
            context=data
        )
    
    def _log_validation(self, data: Dict[str, Any]):
        """Log validation event."""
        validation_type = data.get("event_type", "").replace("validation_", "")
        self.logger.log_validation(
            self.request_id,
            validation_type,
            data.get("data"),
            data.get("success", True),
            data.get("error")
        )
    
    def _log_registry(self, data: Dict[str, Any]):
        """Log registry event."""
        operation = data.get("event_type", "").replace("registry_", "")
        self.logger.log_registry_operation(
            operation,
            data.get("tool_name"),
            data
        )
    
    def log_llm_call(self, prompt: str, response: Any, duration: float):
        """Log LLM call with timing."""
        self.logger.log_llm_call(self.request_id, prompt, response, duration)
    
    def get_active_spans(self) -> Dict[str, Dict[str, Any]]:
        """Get information about currently active spans."""
        return {
            span_id: {
                "name": span["name"],
                "duration_so_far": time.time() - span["start_time"],
                "context": span["context"]
            }
            for span_id, span in self._spans.items()
        }
