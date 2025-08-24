"""Main orchestrator for the agent loop, budgets, and policies."""
import time
from typing import Any, Dict, Optional
from .contracts import LLMClient, Registry, Telemetry
from .guardrails import sanitize_input, extract_tool_call_from_text, validate_output
from .schemas import Answer, ToolCall, ToolResult
from .logging_config import get_logger


class Orchestrator:
    """Main orchestrator for handling agent requests."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        registry: Registry,
        telemetry: Optional[Telemetry] = None,
        max_iterations: int = 3
    ):
        self.llm_client = llm_client
        self.registry = registry
        self.telemetry = telemetry
        self.max_iterations = max_iterations
        self.logger = get_logger()
    
    def answer(self, question: str) -> str:
        """Main entry point for answering questions."""
        # Generate request ID and start logging
        request_id = self.logger.get_request_id()
        context = self.logger.log_request_start(request_id, question)
        
        # Set request context in telemetry if available
        if self.telemetry and hasattr(self.telemetry, 'set_request_id'):
            self.telemetry.set_request_id(request_id)
        
        try:
            # Sanitize input
            clean_question = sanitize_input(question)
            self.logger.log_validation(request_id, "input_sanitization", question, True)
            
            # Log the request
            if self.telemetry:
                self.telemetry.log_event("question_received", {"question": clean_question})
            
            # Log available tools for debugging
            available_tools = self.registry.list_tools()
            if self.telemetry:
                self.telemetry.log_event("available_tools", {"tools": available_tools})
            
            self.logger.log_debug(request_id, "orchestrator", "Available tools", {"tools": available_tools})
            
            # Get plan from LLM with timing
            llm_start_time = time.time()
            plan = self.llm_client.call(clean_question)
            llm_duration = time.time() - llm_start_time
            
            # Log LLM call
            if self.telemetry and hasattr(self.telemetry, 'log_llm_call'):
                self.telemetry.log_llm_call(clean_question, plan, llm_duration)
            
            self.logger.log_debug(request_id, "llm", "LLM response received", {
                "response_type": type(plan).__name__,
                "response_preview": str(plan)[:200],
                "latency_ms": round(llm_duration * 1000, 2)
            })
            
            # Process the plan
            result = self._process_plan(plan, request_id)
            
            # Validate and return output
            validated_result = validate_output(result)
            self.logger.log_validation(request_id, "output_validation", result, True)
            
            # Log successful completion
            self.logger.log_request_end(context, validated_result, success=True)
            
            return validated_result
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            
            # Log error with full context
            self.logger.log_error(request_id, "orchestrator_error", str(e), 
                                context={"question": question}, exception=e)
            
            if self.telemetry:
                self.telemetry.log_event("error", {"error": str(e)})
            
            # Log failed completion
            self.logger.log_request_end(context, error_msg, success=False)
            
            return error_msg
    
    def _process_plan(self, plan: Any, request_id: str) -> Any:
        """Process the plan from the LLM."""
        self.logger.log_debug(request_id, "orchestrator", "Processing plan", {
            "plan_type": type(plan).__name__,
            "plan_preview": str(plan)[:200]
        })
        
        # If plan is already a dict with tool info, use it directly
        if isinstance(plan, dict) and "tool" in plan:
            tool_call = ToolCall(tool=plan["tool"], args=plan.get("args", {}))
            return self._execute_tool_call(tool_call, request_id)
        
        # Try to extract tool call from text
        if isinstance(plan, str):
            tool_data = extract_tool_call_from_text(plan)
            if tool_data:
                self.logger.log_debug(request_id, "orchestrator", "Extracted tool call from text", tool_data)
                tool_call = ToolCall(tool=tool_data["tool"], args=tool_data.get("args", {}))
                return self._execute_tool_call(tool_call, request_id)
        
        # If no tool call found, return the plan as-is
        self.logger.log_debug(request_id, "orchestrator", "No tool call found, returning plan as-is", {
            "plan": str(plan)[:200]
        })
        return plan
    
    def _execute_tool_call(self, tool_call: ToolCall, request_id: str) -> Any:
        """Execute a tool call."""
        # Start timing span for tool execution
        span_id = None
        if self.telemetry and hasattr(self.telemetry, 'start_span'):
            span_id = self.telemetry.start_span("tool_execution", {
                "tool_name": tool_call.tool,
                "args": tool_call.args
            })
        
        start_time = time.time()
        
        try:
            # Check if tool exists
            if not self.registry.has_tool(tool_call.tool):
                available_tools = self.registry.list_tools()
                error_msg = f"Tool '{tool_call.tool}' not found. Available tools: {', '.join(available_tools)}"
                
                self.logger.log_error(request_id, "tool_not_found", error_msg, context={
                    "requested_tool": tool_call.tool,
                    "available_tools": available_tools
                })
                
                if span_id and self.telemetry:
                    self.telemetry.end_span(span_id, error=error_msg)
                
                return error_msg
            
            # Execute the tool
            tool = self.registry.get_tool(tool_call.tool)
            
            self.logger.log_debug(request_id, "tool_executor", f"Executing tool: {tool_call.tool}", {
                "tool_name": tool_call.tool,
                "args": tool_call.args
            })
            
            result = tool.execute(**tool_call.args)
            execution_time = time.time() - start_time
            
            # Log successful execution
            self.logger.log_tool_execution(
                request_id, tool_call.tool, tool_call.args, result, execution_time, success=True
            )
            
            if self.telemetry:
                self.telemetry.log_event("tool_executed", {
                    "tool": tool_call.tool,
                    "args": tool_call.args,
                    "result": str(result)[:100]  # Truncate for logging
                })
            
            if span_id and self.telemetry:
                self.telemetry.end_span(span_id, result=result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tool execution error: {str(e)}"
            
            # Log execution error
            self.logger.log_tool_execution(
                request_id, tool_call.tool, tool_call.args, None, execution_time, 
                success=False, error=str(e)
            )
            
            if self.telemetry:
                self.telemetry.log_event("tool_error", {
                    "tool": tool_call.tool,
                    "error": error_msg
                })
            
            if span_id and self.telemetry:
                self.telemetry.end_span(span_id, error=error_msg)
            
            return error_msg
