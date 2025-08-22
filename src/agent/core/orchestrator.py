"""Main orchestrator for the agent loop, budgets, and policies."""
from typing import Any, Dict, Optional
from .contracts import LLMClient, Registry, Telemetry
from .guardrails import sanitize_input, extract_tool_call_from_text, validate_output
from .schemas import Answer, ToolCall, ToolResult


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
    
    def answer(self, question: str) -> str:
        """Main entry point for answering questions."""
        try:
            # Sanitize input
            clean_question = sanitize_input(question)
            
            # Log the request
            if self.telemetry:
                self.telemetry.log_event("question_received", {"question": clean_question})
            
            # Get plan from LLM
            plan = self.llm_client.call(clean_question)
            
            # Process the plan
            result = self._process_plan(plan)
            
            # Validate and return output
            return validate_output(result)
            
        except Exception as e:
            if self.telemetry:
                self.telemetry.log_event("error", {"error": str(e)})
            return f"Error: {str(e)}"
    
    def _process_plan(self, plan: Any) -> Any:
        """Process the plan from the LLM."""
        # If plan is already a dict with tool info, use it directly
        if isinstance(plan, dict) and "tool" in plan:
            tool_call = ToolCall(tool=plan["tool"], args=plan.get("args", {}))
            return self._execute_tool_call(tool_call)
        
        # Try to extract tool call from text
        if isinstance(plan, str):
            tool_data = extract_tool_call_from_text(plan)
            if tool_data:
                tool_call = ToolCall(tool=tool_data["tool"], args=tool_data.get("args", {}))
                return self._execute_tool_call(tool_call)
        
        # If no tool call found, return the plan as-is
        return plan
    
    def _execute_tool_call(self, tool_call: ToolCall) -> Any:
        """Execute a tool call."""
        try:
            tool = self.registry.get_tool(tool_call.tool)
            result = tool.execute(**tool_call.args)
            
            if self.telemetry:
                self.telemetry.log_event("tool_executed", {
                    "tool": tool_call.tool,
                    "args": tool_call.args,
                    "result": str(result)[:100]  # Truncate for logging
                })
            
            return result
            
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            if self.telemetry:
                self.telemetry.log_event("tool_error", {
                    "tool": tool_call.tool,
                    "error": error_msg
                })
            return error_msg
