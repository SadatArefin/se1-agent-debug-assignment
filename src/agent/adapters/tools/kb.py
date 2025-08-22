"""Knowledge base tool implementation."""
import json
from typing import Any, Dict
from ...config import config


class KnowledgeBaseTool:
    """Knowledge base lookup tool."""
    
    def name(self) -> str:
        return "kb"
    
    def description(self) -> str:
        return "Look up information from the knowledge base"
    
    def execute(self, q: str) -> str:
        """Look up information in the knowledge base."""
        try:
            with open(config.kb_path, "r") as f:
                data = json.load(f)
            for item in data.get("entries", []):
                if q in item.get("name", ""):
                    return item.get("summary", "")
            return "No entry found."
        except Exception as e:
            return f"KB error: {e}"
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Return JSON schema for the tool."""
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Query to search for in the knowledge base"
                    }
                },
                "required": ["q"]
            }
        }
