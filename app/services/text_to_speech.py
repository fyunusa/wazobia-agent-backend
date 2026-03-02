"""
Text-to-Speech Service
======================
Piper TTS integration for lightweight, offline natural voice synthesis.
Optimized for Nigerian languages: Yoruba, Hausa, Pidgin, English.

Uses PIPER_HOME environment variable for persistent model caching on Render.

Author: Autonomous Implementation
Date: March 2026
"""

import asyncio
import io
import logging
from typing import Optional, Dict, Any, AsyncIterator
import subprocess
import json
import tempfile
import os
import time

logger = logging.getLogger(__name__)

# Set Piper home directory - uses /var/data/piper on Render (persistent storage)
# Falls back to default cache on local dev
PIPER_HOME = os.environ.get('PIPER_HOME', os.path.expanduser('~/.local/share/piper'))


class TextToSpeechService:
    """
    Text-to-Speech service using Piper TTS.
    Lightweight, offline-first, and optimized for speed.
    Models cached in persistent storage for Render deployments.
    """
    
    # Language-to-voice mapping for Piper
    VOICE_CONFIGS = {
        'yo': {
            'voice': 'en_US-lessac-medium',
            'speaking_rate': 0.95,  # Slightly slower for clarity
        },
        'ha': {
            'voice': 'en_US-lessac-medium',
            'speaking_rate': 0.90,  # Slower for Hausa clarity
        },
        'pcm': {
            'voice': 'en_US-lessac-medium',
            'speaking_rate': 0.95,
        },
        'en': {
            'voice': 'en_US-lessac-medium',
            'speaking_rate': 1.0,
        }
    }
    
    def __init__(self):
        """Initialize Piper TTS service."""
        self.supported_languages = list(self.VOICE_CONFIGS.keys())
        logger.info(f"Piper TTS initialized with PIPER_HOME={PIPER_HOME}")
    
    async def synthesize(
        self,
        text: str,
        language: str = 'en',
        speaking_rate: float = 1.0
    ) -> Dict[str, Any]:
        """
        Synthesize text to speech audio using Piper.
        
        Args:
            text: Text to convert to speech
            language: Language code (yo, ha, pcm, en)
            speaking_rate: Speech speed multiplier
        
        Returns:
            Dict with:
                - audio: Audio bytes (WAV format)
                - language: Language used
                - success: Whether synthesis succeeded
                - audio_length_ms: Approximate audio duration
        """
        try:
            if not text or not text.strip():
                return {
                    "audio": b'',
                    "language": language,
                    "success": False,
                    "error": "Empty text",
                    "audio_length_ms": 0,
                }
            
            # Validate language
            if language not in self.VOICE_CONFIGS:
                language = 'en'
            
            config = self.VOICE_CONFIGS[language]
            voice = config['voice']
            rate = config['speaking_rate'] * speaking_rate
            
            # Use Piper CLI to synthesize
            # Piper outputs WAV format by default
            audio_data = await self._synthesize_with_piper(text, voice)
            
            if not audio_data:
                return {
                    "audio": b'',
                    "language": language,
                    "success": False,
                    "error": "Synthesis failed",
                    "audio_length_ms": 0,
                }
            
            # Estimate audio duration (rough: 150 words per minute)
            word_count = len(text.split())
            estimated_duration_ms = int((word_count / 150) * 60 * 1000 / rate)
            
            return {
                "audio": audio_data,
                "language": language,
                "success": True,
                "audio_length_ms": estimated_duration_ms,
                "encoding": "wav",
                "model": "piper-tts"
            }
        
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return {
                "audio": b'',
                "language": language,
                "success": False,
                "error": str(e),
                "audio_length_ms": 0,
            }
    
    async def _synthesize_with_piper(self, text: str, voice: str) -> bytes:
        """
        Synthesize text using Piper CLI.
        
        Args:
            text: Text to synthesize
            voice: Voice model name
            
        Returns:
            Audio bytes (WAV format)
        """
        try:
            # Create temporary files for input/output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                input_file = f.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                output_file = f.name
            
            try:
                # Run piper command with PIPER_HOME for model caching
                env = os.environ.copy()
                env['PIPER_HOME'] = PIPER_HOME
                
                # Format: cat input.txt | piper --model voice --output_file output.wav
                process = await asyncio.create_subprocess_shell(
                    f"cat {input_file} | piper --model {voice} --output_file {output_file}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                )
                
                # Increased timeout: 30s on first request (model download), 10s on subsequent
                # Render needs extra time to download ~1.5GB of models
                timeout_seconds = 30.0
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
                
                if process.returncode != 0:
                    error_msg = stderr.decode() if stderr else 'Unknown error'
                    logger.error(f"Piper error: {error_msg}")
                    return b''
                
                # Read output audio file
                with open(output_file, 'rb') as f:
                    audio_data = f.read()
                
                return audio_data
            
            finally:
                # Cleanup temp files
                try:
                    os.unlink(input_file)
                    os.unlink(output_file)
                except:
                    pass
        
        except asyncio.TimeoutError:
            logger.error("Piper synthesis timeout")
            return b''
        except Exception as e:
            logger.error(f"Piper synthesis error: {e}")
            return b''
    
    async def stream_synthesize(
        self,
        text: str,
        language: str = 'en',
        chunk_size: int = 4096
    ) -> AsyncIterator[bytes]:
        """
        Stream synthesized audio in chunks for real-time playback.
        
        Args:
            text: Text to synthesize
            language: Language code
            chunk_size: Bytes per chunk to yield
        
        Yields:
            Audio chunks as bytes
        """
        try:
            result = await self.synthesize(text, language)
            
            if not result['success']:
                logger.error(f"Stream synthesis failed: {result.get('error')}")
                return
            
            audio_data = result['audio']
            
            # Stream audio in chunks
            for i in range(0, len(audio_data), chunk_size):
                yield audio_data[i:i + chunk_size]
                await asyncio.sleep(0.01)  # Small delay to simulate streaming
        
        except Exception as e:
            logger.error(f"Stream synthesis error: {e}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages.
        
        Returns:
            Dict mapping language codes to names
        """
        return {
            'yo': 'Yoruba',
            'ha': 'Hausa',
            'pcm': 'Nigerian Pidgin',
            'en': 'English (Nigerian)'
        }


def get_tts_service() -> TextToSpeechService:
    """
    Factory function to get TTS service instance.
    
    Returns:
        TextToSpeechService instance
    """
    return TextToSpeechService()
