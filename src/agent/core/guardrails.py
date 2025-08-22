"""Input/output checks and JSON repair functionality."""
import json
import re
from typing import Any, Dict, Optional, Union


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    # Basic sanitization
    text = text.strip()
    if len(text) > 10000:  # Reasonable limit
        text = text[:10000]
    
    return text


def validate_tool_call(data: Any) -> bool:
    """Validate if data looks like a valid tool call."""
    if not isinstance(data, dict):
        return False
    
    required_fields = ["tool"]
    return all(field in data for field in required_fields)


def repair_json(text: str) -> Optional[Dict[str, Any]]:
    """Attempt to repair malformed JSON."""
    if not text:
        return None
    
    # Try parsing as-is first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Common repairs
    repairs = [
        # Missing closing brace
        lambda s: s + "}",
        # Missing closing quote
        lambda s: s + '"',
        # Missing closing bracket
        lambda s: s + "]",
        # Remove trailing comma
        lambda s: re.sub(r',\s*}', '}', s),
        lambda s: re.sub(r',\s*]', ']', s),
    ]
    
    for repair in repairs:
        try:
            repaired = repair(text.strip())
            return json.loads(repaired)
        except (json.JSONDecodeError, Exception):
            continue
    
    return None


def extract_tool_call_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract tool call from various text formats."""
    # Try JSON first
    result = repair_json(text)
    if result and validate_tool_call(result):
        return result
    
    # Try to parse "TOOL:name EXPR=value" format
    pattern = r'TOOL:(\w+)\s+(\w+)="([^"]*)"'
    match = re.search(pattern, text)
    if match:
        tool_name, arg_name, arg_value = match.groups()
        return {
            "tool": tool_name,
            "args": {arg_name.lower(): arg_value}
        }
    
    return None


def validate_output(output: Any) -> str:
    """Validate and format output."""
    if output is None:
        return "No result"
    
    if isinstance(output, (int, float)):
        return str(output)
    
    if isinstance(output, str):
        return output
    
    # Try to serialize complex objects
    try:
        return json.dumps(output, indent=2)
    except (TypeError, ValueError):
        return str(output)
