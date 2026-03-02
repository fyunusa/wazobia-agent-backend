"""
Wazobia Agent API
================
FastAPI-based REST API for the Wazobia multilingual agent.

Author: Umar Farouk Yunusa
Date: December 15, 2025
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn
import asyncio

from .agent import get_wazobia_agent, WazobiaAgent
from .language_detector import get_language_detector
from .config import get_settings
from .services import (
    SpeechToTextService, 
    TextToSpeechService, 
    SpeechService,
    get_stt_service,
    get_tts_service,
    get_speech_service
)
from .routers import auth, conversations
from .database import get_db


# Initialize FastAPI app
app = FastAPI(
    title="Wazobia Multilingual Agent API",
    description="API for Nigerian language AI agent supporting Hausa, Pidgin, and Yoruba",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(conversations.router)

# Get settings
settings = get_settings()

# Initialize agent (lazy loading)
_agent: Optional[WazobiaAgent] = None

# Initialize speech services (lazy loading)
_stt_service: Optional[SpeechToTextService] = None
_tts_service: Optional[TextToSpeechService] = None
_speech_service: Optional[SpeechService] = None

# Rate limiting: Maximum 3 concurrent chat requests
chat_semaphore = asyncio.Semaphore(3)


def get_agent() -> WazobiaAgent:
    """Get or initialize the agent."""
    global _agent
    if _agent is None:
        _agent = get_wazobia_agent()
    return _agent


def get_stt() -> SpeechToTextService:
    """Get or initialize STT service."""
    global _stt_service
    if _stt_service is None:
        _stt_service = get_stt_service(api_key=settings.groq_api_key)
    return _stt_service


def get_tts() -> TextToSpeechService:
    """Get or initialize TTS service."""
    global _tts_service
    if _tts_service is None:
        _tts_service = get_tts_service()
    return _tts_service


def get_speech() -> SpeechService:
    """Get or initialize full Speech service."""
    global _speech_service
    if _speech_service is None:
        agent = get_agent()
        _speech_service = get_speech_service(
            stt_service=get_stt(),
            tts_service=get_tts(),
            agent=agent
        )
    return _speech_service


# ============================================================================
# Request/Response Models
# ============================================================================

class MessageRequest(BaseModel):
    """Request model for message processing."""
    message: str = Field(..., description="User message to process")
    language: Optional[str] = Field(None, description="Preferred language (ha, pcm, yo, en)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(None, description="Previous conversation messages")
    preferred_languages: Optional[List[str]] = Field(None, description="List of preferred languages for mixed-language support")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Sannu, yaya kuke?",
                "language": "ha",
                "context": {"user_id": "user123"},
                "preferred_languages": ["ha", "en"]
            }
        }


class MessageResponse(BaseModel):
    """Response model for message processing."""
    response: str = Field(..., description="Agent's response")
    language: str = Field(..., description="Language of response")
    detected_language: Optional[str] = Field(None, description="Detected input language")
    intent: str = Field(..., description="Detected intent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata including confidence scores")
    confidence_level: Optional[str] = Field(None, description="Confidence level: low, medium, or high")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Sannu! Lafiya lau. Yaya zan iya taimaka maka?",
                "language": "ha",
                "detected_language": "ha",
                "intent": "greeting",
                "confidence_level": "high",
                "metadata": {
                    "confidence_score": 0.95,
                    "validation": {
                        "is_valid": True,
                        "confidence_score": 0.95
                    }
                },
                "timestamp": "2025-12-15T10:30:00"
            }
        }


class TranslationRequest(BaseModel):
    """Request model for translation."""
    text: str = Field(..., description="Text to translate")
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, how are you?",
                "source_language": "en",
                "target_language": "ha"
            }
        }


class TranslationResponse(BaseModel):
    """Response model for translation."""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class LanguageDetectionRequest(BaseModel):
    """Request model for language detection."""
    text: str = Field(..., description="Text to detect language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Sannu, yaya kuke?"
            }
        }


class LanguageDetectionResponse(BaseModel):
    """Response model for language detection."""
    text: str
    detected_language: str
    language_name: str
    confidence: float
    all_scores: Dict[str, float]
    is_mixed: bool


class ContentGenerationRequest(BaseModel):
    """Request model for content generation."""
    topic: str = Field(..., description="Topic for content generation")
    content_type: str = Field(..., description="Type of content (story, article, poem, etc.)")
    language: str = Field(..., description="Target language")
    additional_context: Optional[str] = Field(None, description="Additional requirements")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Nigerian independence",
                "content_type": "article",
                "language": "pcm",
                "additional_context": "Focus on cultural impact"
            }
        }


class StatsResponse(BaseModel):
    """Response model for agent statistics."""
    total_conversations: int
    knowledge_base_size: Dict[str, int]
    languages_supported: List[str]
    uptime: str


# ============================================================================
# Speech Endpoints Models
# ============================================================================

class SpeechToTextResponse(BaseModel):
    """Response model for speech-to-text."""
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language code")
    confidence: float = Field(..., description="Confidence score 0-1")
    success: bool = Field(..., description="Whether transcription succeeded")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Sannu, yaya kuke?",
                "language": "ha",
                "confidence": 0.87,
                "success": True,
                "timestamp": "2026-03-02T10:30:00"
            }
        }


class TextToSpeechResponse(BaseModel):
    """Response model for text-to-speech."""
    success: bool = Field(..., description="Whether synthesis succeeded")
    language: str = Field(..., description="Language of speech")
    audio_length_ms: int = Field(..., description="Approximate audio duration")
    encoding: str = Field(..., description="Audio format (mp3)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "language": "ha",
                "audio_length_ms": 3500,
                "encoding": "mp3",
                "timestamp": "2026-03-02T10:30:00"
            }
        }


class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech."""
    text: str = Field(..., description="Text to convert to speech")
    language: str = Field("en", description="Language code (ha, yo, pcm, en)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Sannu, yaya kuke?",
                "language": "ha"
            }
        }


class SpeechToSpeechRequest(BaseModel):
    """Request model for speech-to-speech conversation."""
    language_hint: Optional[str] = Field(None, description="Language hint (ha, yo, pcm, en)")
    provide_text: bool = Field(True, description="Include transcribed text in response")
    stream: bool = Field(False, description="Stream audio response for real-time playback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "language_hint": "ha",
                "provide_text": True,
                "stream": False
            }
        }


class SpeechToSpeechResponse(BaseModel):
    """Response model for speech-to-speech."""
    success: bool = Field(..., description="Whether processing succeeded")
    input_text: Optional[str] = Field(None, description="Transcribed user input")
    response_text: Optional[str] = Field(None, description="Agent's text response")
    language: str = Field(..., description="Primary language used")
    processing_times: Dict[str, float] = Field(..., description="Breakdown of processing times in ms")
    total_time_ms: float = Field(..., description="Total processing time")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "input_text": "Sannu, yaya kuke?",
                "response_text": "Lafiya lau! Yaya zan iya taimaka maka?",
                "language": "ha",
                "processing_times": {
                    "stt_ms": 245,
                    "llm_ms": 890,
                    "tts_ms": 450
                },
                "total_time_ms": 1585,
                "timestamp": "2026-03-02T10:30:00Z"
            }
        }



@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Wazobia Multilingual Agent API",
        "version": "1.0.0",
        "description": "AI agent for Nigerian languages (Hausa, Pidgin, Yoruba) with speech capabilities",
        "endpoints": {
            "POST /chat": "Process chat messages",
            "POST /translate": "Translate text between languages",
            "POST /detect-language": "Detect language of text",
            "POST /generate-content": "Generate content in Nigerian languages",
            "POST /stt": "Speech-to-Text (audio input → text output)",
            "POST /tts": "Text-to-Speech (text input → audio output)",
            "POST /s2s": "Speech-to-Speech (voice chat with voice response)",
            "GET /stats": "Get agent statistics",
            "GET /health": "Health check",
            "GET /languages": "Get supported languages"
        },
        "speech_capabilities": {
            "stt": "Groq Whisper API - Fast, accurate transcription",
            "tts": "Google Cloud TTS - Natural-sounding voices",
            "s2s": "Full voice conversation pipeline"
        },
        "supported_languages": ["Hausa (ha)", "Nigerian Pidgin (pcm)", "Yoruba (yo)", "English (en)"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        agent = get_agent()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "agent_initialized": agent is not None,
            "knowledge_base_loaded": len(agent.knowledge_base) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/chat", response_model=MessageResponse)
async def chat(
    request: MessageRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Process a chat message and generate a response.
    
    The agent will:
    - Detect the language 
    - Understand the intent
    - Retrieve relevant knowledge
    - Generate an appropriate response
    
    Rate limited to 3 concurrent requests to avoid exceeding free API limits.
    """
    # Acquire semaphore to limit concurrent requests
    async with chat_semaphore:
        try:
            agent = get_agent()
            
            # Add preferred_languages to context if provided
            context = request.context or {}
            if request.preferred_languages:
                context['preferred_languages'] = request.preferred_languages
            
            # Process message
            result = await asyncio.to_thread(
                agent.process_message,
                message=request.message,
                context=context
            )
            
            # Save to database if user is authenticated
            if authorization and authorization.startswith("Bearer "):
                try:
                    token = authorization.replace("Bearer ", "")
                    db = get_db()
                    session = db.get_session(token)
                    
                    if session:
                        user_id = session['user_id']
                        print(f"💾 Saving message for user_id: {user_id}")
                        
                        # Get or create a conversation for this user
                        conversations_list = db.get_user_conversations(user_id)
                        
                        if conversations_list:
                            # Use the most recent conversation
                            conversation_id = conversations_list[0]['id']
                            print(f"📝 Using existing conversation: {conversation_id}")
                        else:
                            # Create a new conversation
                            conversation_id = db.create_conversation(user_id, "New Conversation")
                            print(f"🆕 Created new conversation: {conversation_id}")
                        
                        # Save user message
                        db.add_message(
                            conversation_id=conversation_id,
                            role='user',
                            content=request.message,
                            language=result.get('language')
                        )
                        
                        # Save agent response
                        db.add_message(
                            conversation_id=conversation_id,
                            role='assistant',
                            content=result['response'],
                            language=result.get('language')
                        )
                        print(f"✅ Successfully saved 2 messages to conversation {conversation_id}")
                    else:
                        print("⚠️ No session found for token")
                except Exception as e:
                    # Log but don't fail the request if DB save fails
                    print(f"❌ Failed to save conversation: {e}")
            else:
                print("ℹ️ No authorization header - skipping message save")
            
            return MessageResponse(
                response=result['response'],
                language=result['language'],
                detected_language=result.get('metadata', {}).get('input_language', result['language']),
                intent=result['intent'],
                confidence_level=result.get('metadata', {}).get('confidence_level', 'high'),
                metadata=result.get('metadata', {}),
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """
    Translate text between languages.
    
    Supports translation between:
    - English, Hausa, Nigerian Pidgin, Yoruba
    """
    try:
        agent = get_agent()
        
        # Directly call the translation handler with proper parameters
        result = agent._handle_translation(
            message=f"Translate: {request.text}",
            language=request.source_language,
            context={
                'source_language': request.source_language,
                'target_language': request.target_language,
                'text_to_translate': request.text
            }
        )
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=result['response'],
            source_language=request.source_language,
            target_language=request.target_language
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")


@app.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    """
    Detect the language of the given text.
    
    Returns:
    - Detected language code
    - Confidence score
    - Scores for all languages
    """
    try:
        detector = get_language_detector()
        
        detection = detector.detect_language(request.text)
        
        return LanguageDetectionResponse(
            text=request.text,
            detected_language=detection['language'],
            language_name=detector.get_language_name(detection['language']),
            confidence=detection['confidence'],
            all_scores=detection['scores'],
            is_mixed=detection['is_mixed']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection error: {str(e)}")


@app.post("/generate-content")
async def generate_content(request: ContentGenerationRequest):
    """
    Generate content in Nigerian languages.
    
    Supports various content types:
    - Articles
    - Stories
    - Poems
    - Dialogues
    """
    try:
        agent = get_agent()
        
        # Create content generation message
        message = f"Write a {request.content_type} about {request.topic}"
        if request.additional_context:
            message += f". {request.additional_context}"
        
        result = agent.process_message(
            message,
            context={'target_language': request.language}
        )
        
        return {
            "generated_content": result['response'],
            "topic": request.topic,
            "content_type": request.content_type,
            "language": request.language,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation error: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get agent statistics and information.
    """
    try:
        agent = get_agent()
        stats = agent.get_statistics()
        
        return StatsResponse(
            total_conversations=stats['total_conversations'],
            knowledge_base_size=stats['knowledge_base_size'],
            languages_supported=stats['languages_supported'],
            uptime="N/A"  # Can be enhanced with actual uptime tracking
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.post("/clear-history")
async def clear_history():
    """
    Clear conversation history.
    """
    try:
        agent = get_agent()
        agent.clear_history()
        
        return {
            "status": "success",
            "message": "Conversation history cleared",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")


# ============================================================================
# Speech Endpoints
# ============================================================================

@app.post("/stt", response_model=SpeechToTextResponse)
async def speech_to_text(
    file: UploadFile = File(..., description="Audio file (wav, mp3, ogg, etc.)"),
    language_hint: Optional[str] = None
):
    """
    Convert speech (audio) to text using Groq Whisper API.
    
    Supports:
    - Hausa (ha), Yoruba (yo), Nigerian Pidgin (pcm), English (en)
    - Audio formats: WAV, MP3, OGG, FLAC, WebM
    
    Returns transcribed text with confidence score.
    """
    try:
        # Read audio data
        audio_data = await file.read()
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="No audio data provided")
        
        # Get MIME type from filename
        mime_type = file.content_type or "audio/wav"
        
        # Process with STT service
        stt_service = get_stt()
        result = await stt_service.transcribe(
            audio_data=audio_data,
            language=language_hint,
            mime_type=mime_type
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Transcription failed'))
        
        return SpeechToTextResponse(
            text=result['text'],
            language=result['language'],
            confidence=result['confidence'],
            success=True
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-text error: {str(e)}")


@app.post("/tts")
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech using Piper TTS.
    
    Supports:
    - Hausa (ha), Yoruba (yo), Nigerian Pidgin (pcm), English (en)
    
    Returns WAV audio stream ready for playback.
    """
    try:
        text = request.text
        language = request.language
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > 5000:
            raise HTTPException(status_code=400, detail="Text exceeds maximum length (5000 characters)")
        
        # Get TTS service
        tts_service = get_tts()
        result = await tts_service.synthesize(
            text=text,
            language=language
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Synthesis failed'))
        
        # Return audio file as WAV
        return StreamingResponse(
            iter([result['audio']]),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=response.wav",
                "X-Audio-Length-Ms": str(result['audio_length_ms']),
                "X-Language": result['language']
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text-to-speech error: {str(e)}")


@app.post("/s2s")
async def speech_to_speech(
    file: UploadFile = File(..., description="Audio file (wav, mp3, ogg, etc.)"),
    request_data: Optional[SpeechToSpeechRequest] = None
):
    """
    Complete voice conversation: Speech-to-Text → LLM → Text-to-Speech.
    
    This is the main voice interface. Send audio, get voice response.
    
    Supports:
    - Hausa (ha), Yoruba (yo), Nigerian Pidgin (pcm), English (en)
    - Audio formats: WAV, MP3, OGG, FLAC, WebM
    
    Returns:
    - Transcribed input text
    - AI-generated response text
    - Synthesized speech audio (MP3)
    - Performance metrics
    """
    try:
        # Read audio data
        audio_data = await file.read()
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="No audio data provided")
        
        # Get MIME type
        mime_type = file.content_type or "audio/wav"
        
        # Parse request data if provided
        language_hint = None
        if request_data:
            language_hint = request_data.language_hint
        
        # Get Speech service
        speech_service = get_speech()
        result = await speech_service.speech_to_speech(
            audio_data=audio_data,
            language_hint=language_hint,
            mime_type=mime_type,
            stream_response=False  # For now, return complete audio
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Processing failed'))
        
        # Return audio response
        return StreamingResponse(
            iter([result['audio']]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=response.mp3",
                "X-Input-Text": result.get('input_text', ''),
                "X-Response-Text": result.get('response_text', ''),
                "X-Language": result['language'],
                "X-Total-Time-Ms": str(result['total_time_ms']),
                "X-STT-Ms": str(result['processing_times'].get('stt_ms', 0)),
                "X-LLM-Ms": str(result['processing_times'].get('llm_ms', 0)),
                "X-TTS-Ms": str(result['processing_times'].get('tts_ms', 0))
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-speech error: {str(e)}")


@app.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages.
    """
    return {
        "languages": [
            {
                "code": "ha",
                "name": "Hausa",
                "native_name": "Hausa",
                "example": "Sannu, yaya kuke?"
            },
            {
                "code": "pcm",
                "name": "Nigerian Pidgin",
                "native_name": "Naija Pidgin",
                "example": "How you dey?"
            },
            {
                "code": "yo",
                "name": "Yoruba",
                "native_name": "Yorùbá",
                "example": "Báwo ni?"
            },
            {
                "code": "en",
                "name": "English",
                "native_name": "English",
                "example": "How are you?"
            }
        ]
    }


# ============================================================================
# Main
# ============================================================================

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Start the API server.
    
    Args:
        host: Host address
        port: Port number
    """
    uvicorn.run(
        "app.api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()
