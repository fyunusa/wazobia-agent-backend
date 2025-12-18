"""
Wazobia Agent Package
====================
Multilingual AI agent for Nigerian languages.
"""

__version__ = "1.0.0"
__author__ = "Umar Farouk Yunusa"

from .agent import WazobiaAgent, get_wazobia_agent
from .language_detector import LanguageDetector, get_language_detector
from .prompt_loader import PromptLoader, get_prompt_loader
from .config import get_settings

# Initialize Groq client if API key is available
def _init_groq_client():
    """Initialize Groq client for LLM calls."""
    settings = get_settings()
    if settings.llm_provider == "groq" and settings.groq_api_key:
        try:
            from groq import Groq
            return Groq(api_key=settings.groq_api_key)
        except ImportError:
            print("Warning: groq package not installed. Run: pip install groq")
            return None
    return None

__all__ = [
    "WazobiaAgent",
    "get_wazobia_agent",
    "LanguageDetector",
    "get_language_detector",
    "PromptLoader",
    "get_prompt_loader",
    "get_settings",
    "_init_groq_client"
]
