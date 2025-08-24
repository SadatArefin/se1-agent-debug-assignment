"""New decorator-based tool implementations."""

import re
from ..core.decorators import tool


@tool(name="calc", description="Evaluate mathematical expressions including percentages")
def calculator(expr: str) -> float:
    """
    Evaluate a mathematical expression.
    
    Args:
        expr: Mathematical expression to evaluate
    
    Returns:
        float: Result of the calculation
    """
    original_expr = expr
    e = expr.lower().strip()
    
    # Remove common question words and phrases
    e = e.replace("what is", "").replace("calculate", "").replace("?", "").strip()
    
    # Handle percentage calculations first
    if "% of" in e:
        try:
            left, right = e.split("% of")
            x = float(left.strip())
            y = float(right.strip())
            return (x/100.0)*y
        except Exception:
            pass  # Fall through to other methods
    
    # Handle simple mathematical expressions
    try:
        # Handle "add X to Y" patterns
        if "add" in e and "to" in e:
            parts = e.split("add")
            if len(parts) == 2:
                after_add = parts[1].strip()
                if "to" in after_add:
                    add_parts = after_add.split("to")
                    if len(add_parts) == 2:
                        num_to_add = add_parts[0].strip()
                        target = add_parts[1].strip()
                        
                        # Extract numbers
                        try:
                            add_match = re.search(r'(\d+(?:\.\d+)?)', num_to_add)
                            target_match = re.search(r'(\d+(?:\.\d+)?)', target)
                            
                            if add_match and target_match:
                                return float(target_match.group(1)) + float(add_match.group(1))
                        except:
                            pass
        
        # Clean up text operators
        e = e.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
        e = e.replace("add", "+").replace("subtract", "-").replace("multiply", "*").replace("divide", "/")
        
        # Check if it's now a valid mathematical expression (numbers and operators only)
        if re.match(r'^[\d\s+\-*/().%]+$', e):
            result = eval(e)
            return float(result)
        else:
            # If still contains letters, try to extract just the mathematical part
            math_match = re.search(r'([\d\s+\-*/().%]+)', e)
            if math_match:
                math_expr = math_match.group(1).strip()
                if math_expr:
                    result = eval(math_expr)
                    return float(result)
            
            raise ValueError(f"Cannot parse mathematical expression from: {original_expr}")
            
    except Exception as ex:
        raise ValueError(f"Invalid mathematical expression: {original_expr}. Error: {str(ex)}")


@tool(name="weather", description="Get temperature information for cities")
def weather(city: str) -> str:
    """
    Get temperature for a city.
    
    Args:
        city: Name of the city to get weather for
    
    Returns:
        str: Temperature information
    """
    temps = {
        "paris": "18",
        "london": 17.0,
        "dhaka": 31,
        "amsterdam": "19.5"
    }
    
    c = (city or "").strip().lower()
    return temps.get(c, "20")


@tool(name="kb", description="Look up information from the knowledge base")
def knowledge_base(q: str) -> str:
    """
    Look up information in the knowledge base.
    
    Args:
        q: Query to search for in the knowledge base
    
    Returns:
        str: Information from the knowledge base
    """
    import json
    import os
    from ...config import config
    
    try:
        # Handle both relative and absolute paths
        kb_path = config.kb_path
        if not os.path.isabs(kb_path):
            # If relative path, make it relative to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, '..', '..', '..')
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


@tool(name="unit_converter", description="Convert between different units of measurement")
def unit_converter(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert between units.
    
    Args:
        value: Value to convert
        from_unit: Unit to convert from
        to_unit: Unit to convert to
    
    Returns:
        float: Converted value
    """
    # Simple temperature conversions for now
    if from_unit.lower() == "celsius" and to_unit.lower() == "fahrenheit":
        return (value * 9/5) + 32
    elif from_unit.lower() == "fahrenheit" and to_unit.lower() == "celsius":
        return (value - 32) * 5/9
    else:
        raise ValueError(f"Conversion from {from_unit} to {to_unit} not supported")


@tool(name="translator", description="Translate text between different languages")
def translator(text: str, from_lang: str = "auto", to_lang: str = "english") -> str:
    """
    Translate text between languages.
    
    Args:
        text: Text to translate
        from_lang: Source language (default: auto)
        to_lang: Target language (default: english)
    
    Returns:
        str: Translated text
    """
    # Simple translation mappings
    translations = {
        # Spanish to English
        "hola": "hello",
        "gracias": "thank you",
        "adiós": "goodbye",
        "mundo": "world",
        "buenos días": "good morning",
        "buenas noches": "good night",
        "por favor": "please",
        "disculpe": "excuse me",
        "sí": "yes",
        "no": "no",
        
        # French to English
        "bonjour": "hello",
        "merci": "thank you",
        "au revoir": "goodbye",
        "monde": "world",
        "s'il vous plaît": "please",
        "excusez-moi": "excuse me",
        "oui": "yes",
        "non": "no",
        
        # German to English
        "hallo": "hello",
        "danke": "thank you",
        "auf wiedersehen": "goodbye",
        "welt": "world",
        "bitte": "please",
        "entschuldigung": "excuse me",
        "ja": "yes",
        "nein": "no",
    }
    
    # Create reverse mappings
    reverse_translations = {}
    for source, target in translations.items():
        if target not in reverse_translations:
            reverse_translations[target] = {}
        # Determine source language based on common patterns
        if source in ["hola", "gracias", "adiós", "mundo", "buenos días", "buenas noches", "por favor", "disculpe", "sí", "no"]:
            lang = "spanish"
        elif source in ["bonjour", "merci", "au revoir", "monde", "s'il vous plaît", "excusez-moi", "oui", "non"]:
            lang = "french"
        elif source in ["hallo", "danke", "auf wiedersehen", "welt", "bitte", "entschuldigung", "ja", "nein"]:
            lang = "german"
        else:
            lang = "unknown"
        
        reverse_translations[target][lang] = source
    
    # Clean input
    clean_text = text.strip().lower()
    
    # If same language, return as-is
    if from_lang == to_lang:
        return text.strip()
    
    # Handle English to other languages
    if from_lang == "english" and to_lang != "english":
        if clean_text in reverse_translations:
            if to_lang in reverse_translations[clean_text]:
                return reverse_translations[clean_text][to_lang]
    
    # Handle other languages to English
    if to_lang == "english":
        if clean_text in translations:
            return translations[clean_text]
    
    # Fallback for unknown phrases
    return f"Translated from {from_lang} to {to_lang}: {text.strip()}"


# Example of how easy it is to add a new tool with the decorator
@tool(name="random_quote", description="Get a random inspirational quote")
def random_quote(category: str = "general") -> str:
    """
    Get a random quote from the specified category.
    
    Args:
        category: Category of quote (general, tech, motivation)
    
    Returns:
        str: A random quote
    """
    quotes = {
        "general": [
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Life is what happens to you while you're busy making other plans. - John Lennon",
        ],
        "tech": [
            "Any sufficiently advanced technology is indistinguishable from magic. - Arthur C. Clarke",
            "The computer was born to solve problems that did not exist before. - Bill Gates",
        ],
        "motivation": [
            "The only impossible journey is the one you never begin. - Tony Robbins",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        ]
    }
    
    import random
    category_quotes = quotes.get(category.lower(), quotes["general"])
    return random.choice(category_quotes)
