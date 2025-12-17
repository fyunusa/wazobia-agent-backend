"""
Language Agent Services
======================
Specialized agents for each Nigerian language.
"""

from .base_agent import BaseLanguageAgent
from .yoruba_agent import YorubaAgent
from .hausa_agent import HausaAgent
from .pidgin_agent import PidginAgent
from .english_agent import EnglishAgent

__all__ = [
    'BaseLanguageAgent',
    'YorubaAgent',
    'HausaAgent',
    'PidginAgent',
    'EnglishAgent'
]
