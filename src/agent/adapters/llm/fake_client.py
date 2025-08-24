"""Fake LLM client for testing and development."""
import json
import re
from typing import Any, Dict, Optional
from ...core.contracts import LLMClient


class FakeClient:
    
    def call(self, prompt: str) -> Any:
        p = prompt.lower().strip()
        
        if self._is_complex_query(p):
            return self._handle_complex_query(p, prompt)
        
        if self._is_math_query(p):
            return {"tool": "calc", "args": {"expr": prompt.strip()}}
        
        if self._is_weather_query(p):
            city = self._extract_city(p)
            return {"tool": "weather", "args": {"city": city}}
        
        if self._is_knowledge_query(p):
            query = self._extract_knowledge_query(prompt)
            return {"tool": "kb", "args": {"q": query}}
        
        if self._is_unit_conversion(p):
            conversion_data = self._extract_conversion_data(p)
            if conversion_data:
                return {"tool": "unit_converter", "args": conversion_data}
        
        if self._is_translation_query(p):
            translation_data = self._extract_translation_data(p)
            if translation_data:
                return {"tool": "translator", "args": translation_data}
        
        return f"I don't understand the query: {prompt}"
    
    def _is_complex_query(self, prompt: str) -> bool:
        complex_patterns = [
            "average temperature",
            "add" and "temperature",
            "average" and ("paris" or "london"),
            "multiple cities" and "calculate",
        ]
        
        has_multiple_cities = sum(1 for city in ["paris", "london", "new york", "tokyo"] if city in prompt) > 1
        has_calculation = any(word in prompt for word in ["add", "average", "sum", "total", "calculate"])
        has_weather = any(word in prompt for word in ["temperature", "weather"])
        
        return (has_multiple_cities and has_calculation) or (has_weather and has_calculation and "average" in prompt)
    
    def _handle_complex_query(self, prompt_lower: str, original_prompt: str) -> str:
        if "add" in prompt_lower and "average temperature" in prompt_lower:
            if "paris" in prompt_lower and "london" in prompt_lower:
                simulated_paris_temp = 22
                simulated_london_temp = 18
                average_temp = (simulated_paris_temp + simulated_london_temp) / 2
                
                add_match = re.search(r'add\s+(\d+)', prompt_lower)
                if add_match:
                    number_to_add = int(add_match.group(1))
                    result = average_temp + number_to_add
                    return f"The average temperature in Paris ({simulated_paris_temp}°C) and London ({simulated_london_temp}°C) is {average_temp}°C. Adding {number_to_add} gives us {result}°C."
        
        return f"This appears to be a complex multi-step query that would require multiple tool calls: {original_prompt}"
    
    def _is_math_query(self, prompt: str) -> bool:
        simple_math_indicators = [
            "what is", "calculate", "compute"
        ]
        
        has_simple_math = any(indicator in prompt for indicator in simple_math_indicators) or \
                         re.search(r'\d+.*[+\-*/].*\d+', prompt) or \
                         re.search(r'\d+.*%.*of.*\d+', prompt)
        
        is_complex = "temperature" in prompt or "weather" in prompt or "average" in prompt
        
        return has_simple_math and not is_complex
    
    def _is_weather_query(self, prompt: str) -> bool:
        weather_keywords = ["weather", "temperature", "forecast", "climate", "rain", "snow", "sunny", "cloudy"]
        return any(keyword in prompt for keyword in weather_keywords)
    
    def _is_knowledge_query(self, prompt: str) -> bool:
        kb_patterns = ["who is", "what is", "tell me about", "information about", "biography"]
        return any(pattern in prompt for pattern in kb_patterns)
    
    def _is_unit_conversion(self, prompt: str) -> bool:
        conversion_patterns = ["convert", "degrees", "celsius", "fahrenheit", "to", "from"]
        return "convert" in prompt and any(pattern in prompt for pattern in conversion_patterns)
    
    def _is_translation_query(self, prompt: str) -> bool:
        return "translate" in prompt or "translation" in prompt
    
    def _extract_city(self, prompt: str) -> str:
        cities = ["paris", "london", "dhaka", "new york", "tokyo", "sydney", "berlin"]
        for city in cities:
            if city in prompt:
                return city.title()
        
        match = re.search(r'\bin\s+([a-zA-Z\s]+?)(?:\s|$)', prompt)
        if match:
            return match.group(1).strip().title()
        
        return "Paris"
    
    def _extract_knowledge_query(self, prompt: str) -> str:
        query = re.sub(r'^(who is|what is|tell me about|information about)\s*', '', prompt.strip(), flags=re.IGNORECASE)
        query = re.sub(r'\?$', '', query)
        return query.strip()
    
    def _extract_conversion_data(self, prompt: str) -> Optional[Dict[str, Any]]:
        celsius_to_f = re.search(r'convert\s+(\d+(?:\.\d+)?)\s*degrees?\s*celsius\s+to\s+fahrenheit', prompt)
        if celsius_to_f:
            return {
                "value": float(celsius_to_f.group(1)),
                "from_unit": "celsius",
                "to_unit": "fahrenheit"
            }
        
        fahrenheit_to_c = re.search(r'convert\s+(\d+(?:\.\d+)?)\s*degrees?\s*fahrenheit\s+to\s+celsius', prompt)
        if fahrenheit_to_c:
            return {
                "value": float(fahrenheit_to_c.group(1)),
                "from_unit": "fahrenheit", 
                "to_unit": "celsius"
            }
        
        return None
    
    def _extract_translation_data(self, prompt: str) -> Optional[Dict[str, Any]]:
        match = re.search(r"translate\s+['\"]([^'\"]+)['\"](?:\s+from\s+(\w+))?\s+to\s+(\w+)", prompt)
        if match:
            text = match.group(1)
            from_lang = match.group(2) or "auto"
            to_lang = match.group(3)
            return {
                "text": text,
                "from_lang": from_lang,
                "to_lang": to_lang
            }
        
        match = re.search(r"translate\s+['\"]([^'\"]+)['\"](?:\s+from\s+(\w+))?\s+to\s+(\w+)", prompt)
        if match:
            text = match.group(1)
            from_lang = match.group(2) or "auto"
            to_lang = match.group(3)
            return {
                "text": text,
                "from_lang": from_lang,
                "to_lang": to_lang
            }
        
        return None
