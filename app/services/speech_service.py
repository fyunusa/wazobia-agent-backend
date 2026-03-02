"""
Speech Service
==============
Orchestrates Speech-to-Text, LLM processing, and Text-to-Speech
for seamless voice conversation.

Author: Autonomous Implementation
Date: March 2026
"""

from typing import Optional, Dict, Any, AsyncIterator, List
from datetime import datetime
import asyncio
from .speech_to_text import SpeechToTextService
from .text_to_speech import TextToSpeechService


class SpeechService:
    """
    High-level speech service orchestrating full voice pipeline.
    Handles STT → LLM → TTS with streaming and optimization.
    """
    
    def __init__(
        self,
        stt_service: Optional[SpeechToTextService] = None,
        tts_service: Optional[TextToSpeechService] = None,
        agent = None
    ):
        """
        Initialize Speech Service.
        
        Args:
            stt_service: Speech-to-text service instance
            tts_service: Text-to-speech service instance
            agent: Wazobia Agent for LLM processing
        """
        self.stt = stt_service or SpeechToTextService()
        self.tts = tts_service or TextToSpeechService()
        self.agent = agent
        
        # Conversation state
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_language: str = 'en'
    
    async def process_speech(
        self,
        audio_data: bytes,
        language_hint: Optional[str] = None,
        mime_type: str = "audio/wav",
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process speech input to text output (STT only).
        
        Args:
            audio_data: Raw audio bytes
            language_hint: Optional language hint
            mime_type: Audio format
            conversation_history: Optional conversation context
        
        Returns:
            Dict with transcribed text and metadata
        """
        # Step 1: Speech-to-Text
        stt_result = await self.stt.transcribe(
            audio_data=audio_data,
            language=language_hint,
            mime_type=mime_type
        )
        
        if not stt_result['success']:
            return {
                "success": False,
                "error": "Transcription failed",
                "details": stt_result.get('error'),
                "timestamp": datetime.now().isoformat()
            }
        
        # Update current language
        self.current_language = stt_result['language']
        
        # Store in history
        self.conversation_history.append({
            "role": "user",
            "content": stt_result['text'],
            "language": stt_result['language'],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "text": stt_result['text'],
            "language": stt_result['language'],
            "confidence": stt_result['confidence'],
            "timestamp": datetime.now().isoformat()
        }
    
    async def text_to_speech(
        self,
        text: str,
        language: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Convert text to speech.
        
        Args:
            text: Text to synthesize
            language: Target language (defaults to detected language)
            stream: Whether to stream audio chunks
        
        Returns:
            Dict with audio and metadata (or async generator if stream=True)
        """
        target_language = language or self.current_language
        
        if stream:
            return await self.tts.stream_synthesize(
                text=text,
                language=target_language
            )
        else:
            return await self.tts.synthesize(
                text=text,
                language=target_language
            )
    
    async def speech_to_speech(
        self,
        audio_data: bytes,
        language_hint: Optional[str] = None,
        mime_type: str = "audio/wav",
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        stream_response: bool = True
    ) -> Dict[str, Any]:
        """
        Complete voice conversation: STT → LLM → TTS.
        Optimized for speed and seamlessness.
        
        Args:
            audio_data: Input audio bytes
            language_hint: Optional language hint
            mime_type: Audio format
            conversation_history: Previous conversation messages
            stream_response: Whether to stream TTS audio
        
        Returns:
            Dict with:
                - input_text: Transcribed user input
                - response_text: LLM response
                - audio: Synthesized speech (bytes or async iterator)
                - language: Detected/used language
                - processing_times: Performance metrics
        """
        timings = {}
        start_time = datetime.now()
        
        # Step 1: STT (Speech to Text)
        stt_start = datetime.now()
        stt_result = await self.stt.transcribe(
            audio_data=audio_data,
            language=language_hint,
            mime_type=mime_type
        )
        timings['stt_ms'] = (datetime.now() - stt_start).total_seconds() * 1000
        
        if not stt_result['success']:
            return {
                "success": False,
                "error": "Transcription failed",
                "details": stt_result.get('error'),
                "timestamp": datetime.now().isoformat()
            }
        
        user_text = stt_result['text']
        detected_language = stt_result['language']
        self.current_language = detected_language
        
        # Step 2: LLM Processing (using WazobiaAgent)
        llm_start = datetime.now()
        try:
            if self.agent:
                # Use the wazobia agent for intelligent response
                llm_response = self.agent.respond(
                    message=user_text,
                    language=detected_language,
                    conversation_history=conversation_history or self.conversation_history
                )
                response_text = llm_response.get('response', 'I did not understand that.')
            else:
                # Fallback: echo the input
                response_text = f"You said: {user_text}"
        
        except Exception as e:
            response_text = "I encountered an error processing your request."
            print(f"LLM Error: {e}")
        
        timings['llm_ms'] = (datetime.now() - llm_start).total_seconds() * 1000
        
        # Step 3: TTS (Text to Speech) - with optional streaming
        tts_start = datetime.now()
        
        if stream_response:
            # Return async generator for streaming
            audio_generator = await self.tts.stream_synthesize(
                text=response_text,
                language=detected_language
            )
            timings['tts_ms'] = (datetime.now() - tts_start).total_seconds() * 1000
            
            return {
                "success": True,
                "input_text": user_text,
                "response_text": response_text,
                "audio_stream": audio_generator,
                "language": detected_language,
                "processing_times": timings,
                "total_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Return complete audio
            tts_result = await self.tts.synthesize(
                text=response_text,
                language=detected_language
            )
            timings['tts_ms'] = (datetime.now() - tts_start).total_seconds() * 1000
            
            return {
                "success": True,
                "input_text": user_text,
                "response_text": response_text,
                "audio": tts_result.get('audio'),
                "language": detected_language,
                "processing_times": timings,
                "total_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "timestamp": datetime.now().isoformat()
            }
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.current_language = 'en'
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get current conversation history."""
        return self.conversation_history.copy()


def get_speech_service(
    stt_service: Optional[SpeechToTextService] = None,
    tts_service: Optional[TextToSpeechService] = None,
    agent = None
) -> SpeechService:
    """
    Factory function to get Speech service instance.
    
    Args:
        stt_service: Optional STT service instance
        tts_service: Optional TTS service instance
        agent: Optional Wazobia Agent instance
    
    Returns:
        SpeechService instance
    """
    return SpeechService(
        stt_service=stt_service,
        tts_service=tts_service,
        agent=agent
    )
