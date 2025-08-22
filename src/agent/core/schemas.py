"""Pydantic v2 models for messages, tool calls, and answers."""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in the conversation."""
    role: str = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The content of the message")
    timestamp: Optional[str] = Field(None, description="Timestamp of the message")


class ToolCall(BaseModel):
    """A tool call request."""
    tool: str = Field(..., description="The name of the tool to call")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool")
    id: Optional[str] = Field(None, description="Unique identifier for the tool call")


class ToolResult(BaseModel):
    """Result of a tool execution."""
    tool_call_id: Optional[str] = Field(None, description="ID of the tool call this result belongs to")
    result: Any = Field(..., description="The result of the tool execution")
    error: Optional[str] = Field(None, description="Error message if tool execution failed")


class Answer(BaseModel):
    """Final answer from the agent."""
    content: str = Field(..., description="The answer content")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tool calls made")
    tool_results: List[ToolResult] = Field(default_factory=list, description="Results from tool calls")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
