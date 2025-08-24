"""Translator tool implementation."""
from typing import Any, Dict


class TranslatorTool:
    
    def __init__(self):
        self.translations = {
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
            
            "bonjour": "hello",
            "merci": "thank you",
            "au revoir": "goodbye",
            "monde": "world",
            "s'il vous plaît": "please",
            "excusez-moi": "excuse me",
            "oui": "yes",
            "non": "no",
            
            "hallo": "hello",
            "danke": "thank you",
            "auf wiedersehen": "goodbye",
            "welt": "world",
            "bitte": "please",
            "entschuldigung": "excuse me",
            "ja": "yes",
            "nein": "no",
        }
        
        self.reverse_translations = {}
        for source, target in self.translations.items():
            if target not in self.reverse_translations:
                self.reverse_translations[target] = {}
            if source in ["hola", "gracias", "adiós", "mundo", "buenos días", "buenas noches", "por favor", "disculpe", "sí", "no"]:
                lang = "spanish"
            elif source in ["bonjour", "merci", "au revoir", "monde", "s'il vous plaît", "excusez-moi", "oui", "non"]:
                lang = "french"
            elif source in ["hallo", "danke", "auf wiedersehen", "welt", "bitte", "entschuldigung", "ja", "nein"]:
                lang = "german"
            else:
                lang = "unknown"
            
            self.reverse_translations[target][lang] = source
    
    def name(self) -> str:
        return "translator"
    
    def description(self) -> str:
        return "Translate text between different languages"
    
    def execute(self, text: str, from_lang: str = "auto", to_lang: str = "english") -> str:
        clean_text = text.strip().lower()
        
        if from_lang == to_lang:
            return text.strip()
        
        if from_lang == "english" and to_lang != "english":
            if clean_text in self.reverse_translations:
                if to_lang in self.reverse_translations[clean_text]:
                    return self.reverse_translations[clean_text][to_lang]
        
        if to_lang == "english":
            if clean_text in self.translations:
                return self.translations[clean_text]
        
        return f"Translated from {from_lang} to {to_lang}: {text.strip()}"
    
    def to_json_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate"
                    },
                    "from_lang": {
                        "type": "string",
                        "description": "Source language",
                        "default": "auto"
                    },
                    "to_lang": {
                        "type": "string",
                        "description": "Target language",
                        "default": "english"
                    }
                },
                "required": ["text"]
            }
        }
