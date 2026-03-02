"""
Speech-to-Text Service
======================
Groq Whisper API integration for fast audio transcription.
Supports Hausa, Yoruba, Pidgin, and English.

Author: Autonomous Implementation
Date: March 2026
"""

import io
from typing import Optional, Dict, Any
from groq import Groq


class SpeechToTextService:
    """
    Speech-to-Text service using Groq Whisper API.
    Optimized for speed with Nigerian languages support.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize STT service.
        
        Args:
            api_key: Groq API key (uses GROQ_API_KEY env var if not provided)
        """
        self.client = Groq(api_key=api_key)
        self.supported_languages = {
            'ha': 'Hausa',
            'yo': 'Yoruba',
            'pcm': 'Pidgin',
            'en': 'English'
        }
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        mime_type: str = "audio/wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using Groq Whisper.
        
        Args:
            audio_data: Raw audio bytes
            language: Optional language code (ha, yo, pcm, en)
            mime_type: Audio format (audio/wav, audio/mp3, audio/ogg, etc.)
        
        Returns:
            Dict with:
                - text: Transcribed text
                - language: Detected language code
                - confidence: Confidence score (0-1)
                - processing_time: Time taken in seconds
        """
        try:
            # Create file-like object from audio bytes
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{mime_type.split('/')[-1]}"
            
            # Call Groq Whisper API
            # Note: Groq's API expects file-like objects
            transcription = self.client.audio.transcriptions.create(
                file=(audio_file.name, audio_file, mime_type),
                model="whisper-large-v3",
                language=language,  # Optional: hint language for better accuracy
                response_format="json"
            )
            
            # Extract text
            text = transcription.text
            
            # Detect language if not provided
            detected_language = self._detect_language(text, language)
            
            # Groq Whisper doesn't return confidence, but we can estimate
            # Shorter responses and clear speech = higher confidence
            confidence = self._estimate_confidence(text, detected_language)
            
            return {
                "text": text,
                "language": detected_language,
                "confidence": confidence,
                "success": True,
                "model": "groq-whisper-large-v3"
            }
        
        except Exception as e:
            return {
                "text": None,
                "language": language,
                "confidence": 0.0,
                "success": False,
                "error": str(e),
                "model": "groq-whisper-large-v3"
            }
    
    def _detect_language(self, text: str, hint: Optional[str] = None) -> str:
        """
        Detect language from transcribed text.
        Groq Whisper auto-detects, but we verify and normalize.
        
        Args:
            text: Transcribed text
            hint: Language hint from Whisper
        
        Returns:
            Language code (ha, yo, pcm, en)
        """
        if hint and hint in self.supported_languages:
            return hint
        
        # Fallback: simple heuristics based on common words
        text_lower = text.lower()
        
        # Hausa keywords
        if any(word in text_lower for word in ['sannu', 'yaya', 'kuna', 'komai']):
            return 'ha'
        
        # Yoruba keywords
        if any(word in text_lower for word in ['bawo', 'ẹ', 'ni', 'dun']):
            return 'yo'
        
        # Pidgin keywords
        if any(word in text_lower for word in ['abeg', 'na', 'abi', 'broda', 'sista']):
            return 'pcm'
        
        # Default to English
        return 'en'
    
    def _estimate_confidence(self, text: str, language: str) -> float:
        """
        Estimate transcription confidence based on text characteristics.
        
        Args:
            text: Transcribed text
            language: Detected language
        
        Returns:
            Confidence score 0-1
        """
        if not text:
            return 0.0
        
        # Base confidence: text length (longer = usually clearer recording)
        base_confidence = min(len(text) / 50, 1.0)  # Max at 50 chars
        
        # Adjust for language-specific patterns
        if language == 'pcm' and len(text.split()) > 3:
            # Pidgin often flows naturally
            base_confidence = min(base_confidence + 0.1, 1.0)
        
        # Reduce confidence if text has unusual patterns
        if text.isupper():  # All caps might indicate transcription error
            base_confidence = max(base_confidence - 0.1, 0.3)
        
        return round(base_confidence, 2)


def get_stt_service(api_key: Optional[str] = None) -> SpeechToTextService:
    """
    Factory function to get STT service instance.
    
    Args:
        api_key: Optional Groq API key
    
    Returns:
        SpeechToTextService instance
    """
    return SpeechToTextService(api_key=api_key)
