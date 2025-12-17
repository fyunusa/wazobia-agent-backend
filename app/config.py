"""
Configuration Management
========================
Configuration settings for the Wazobia Agent.

Author: Firdausi Yakubu
Date: December 15, 2025
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    Environment variables should be prefixed with WAZOBIA_
    Example: WAZOBIA_API_KEY=your_key
    """
    
    # Application settings
    app_name: str = "Wazobia Multilingual Agent"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", "8000"))  # Support Render's PORT env var
    api_workers: int = 1
    cors_origins: list = ["*"]
    
    # LLM settings
    llm_provider: str = "anthropic"  # anthropic, groq, openai, azure, local
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    azure_api_key: Optional[str] = None
    
    # Model configuration
    default_model: str = "claude-3-5-sonnet-20241022"  # Claude 3.5 Sonnet
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # Knowledge base settings
    knowledge_base_path: Optional[str] = None
    use_embeddings: bool = False
    embedding_model: str = "text-embedding-3-small"
    
    # Agent settings
    max_conversation_history: int = 10
    context_window_size: int = 4000
    retrieval_top_k: int = 5
    
    # Language settings
    default_language: str = "en"
    supported_languages: list = ["ha", "pcm", "yo", "en"]
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    
    class Config:
        env_prefix = "WAZOBIA_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings instance
    """
    return Settings()


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """
    Get the data directory path.
    
    Returns:
        Path to data directory
    """
    return get_project_root() / "data"


def get_knowledge_base_path() -> Path:
    """
    Get the knowledge base path from settings or default.
    
    Returns:
        Path to knowledge base
    """
    settings = get_settings()
    
    if settings.knowledge_base_path:
        return Path(settings.knowledge_base_path)
    
    return get_data_dir()


# Language configuration
LANGUAGE_CONFIG = {
    "ha": {
        "name": "Hausa",
        "native_name": "Hausa",
        "code": "ha",
        "direction": "ltr",
        "greeting": "Sannu",
        "enabled": True
    },
    "pcm": {
        "name": "Nigerian Pidgin",
        "native_name": "Naija Pidgin",
        "code": "pcm",
        "direction": "ltr",
        "greeting": "How far",
        "enabled": True
    },
    "yo": {
        "name": "Yoruba",
        "native_name": "Yorùbá",
        "code": "yo",
        "direction": "ltr",
        "greeting": "Báwo ni",
        "enabled": True
    },
    "en": {
        "name": "English",
        "native_name": "English",
        "code": "en",
        "direction": "ltr",
        "greeting": "Hello",
        "enabled": True
    }
}


# Model configuration presets
MODEL_PRESETS = {
    "fast": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000
    },
    "balanced": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000
    },
    "creative": {
        "model": "gpt-4",
        "temperature": 0.9,
        "max_tokens": 2500
    },
    "precise": {
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 1500
    }
}


# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "wazobia_agent.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    },
    "loggers": {
        "wazobia": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        }
    }
}
