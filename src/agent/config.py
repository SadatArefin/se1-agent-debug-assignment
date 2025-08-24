"""Configuration management using pydantic-settings."""
from typing import Optional
try:
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict
except ImportError:
    from pydantic import BaseSettings
    ConfigDict = None


class Config(BaseSettings):
    
    llm_provider: str = "fake"
    
    kb_path: str = "data/kb.json"
    
    enable_telemetry: bool = False
    
    if ConfigDict:
        model_config = ConfigDict(
            env_file=".env",
            env_file_encoding="utf-8"
        )
    else:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"


config = Config()
