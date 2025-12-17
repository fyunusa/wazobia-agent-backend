#!/usr/bin/env python3
"""
Run the Wazobia Agent API server
"""

import sys
import uvicorn
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.api import app
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print("=" * 60)
    print("🇳🇬 Wazobia Multilingual AI Agent")
    print("=" * 60)
    print(f"Starting server on {settings.api_host}:{settings.api_port}")
    print(f"Environment: {settings.environment}")
    print(f"Supported languages: Hausa, Nigerian Pidgin, Yoruba, English")
    print("=" * 60)
    print(f"\n📚 API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"📊 Health Check: http://{settings.api_host}:{settings.api_port}/health\n")
    
    uvicorn.run(
        "app.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
