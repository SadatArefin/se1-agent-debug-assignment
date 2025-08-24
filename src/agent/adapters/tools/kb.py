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
            import os
            # Handle both relative and absolute paths
            kb_path = config.kb_path
            if not os.path.isabs(kb_path):
                # If relative path, make it relative to the project root
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.join(current_dir, '..', '..', '..', '..')
                kb_path = os.path.join(project_root, kb_path)
            
            with open(kb_path, "r") as f:
                data = json.load(f)
            
            # Make search case-insensitive
            query_lower = q.lower().strip()
            
            for item in data.get("entries", []):
                name = item.get("name", "").lower()
                if query_lower in name or name in query_lower:
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
