"""Configuration management using pydantic-settings."""
from typing import Optional
try:
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings
    ConfigDict = None


class Config(BaseSettings):
    """Application configuration."""
    
    # LLM settings
    llm_provider: str = "fake"
    openai_api_key: Optional[str] = None
    
    # Tool settings
    kb_path: str = "data/kb.json"
    
    # Telemetry settings
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


# Global config instance
config = Config()
