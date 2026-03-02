"""
Language Agent Services
======================
Specialized agents for each Nigerian language and speech services.
"""

from .base_agent import BaseLanguageAgent
from .yoruba_agent import YorubaAgent
from .hausa_agent import HausaAgent
from .pidgin_agent import PidginAgent
from .english_agent import EnglishAgent
from .speech_to_text import SpeechToTextService, get_stt_service
from .text_to_speech import TextToSpeechService, get_tts_service
from .speech_service import SpeechService, get_speech_service

__all__ = [
    'BaseLanguageAgent',
    'YorubaAgent',
    'HausaAgent',
    'PidginAgent',
    'EnglishAgent',
    'SpeechToTextService',
    'TextToSpeechService',
    'SpeechService',
    'get_stt_service',
    'get_tts_service',
    'get_speech_service'
]
