#!/bin/bash
# Render Build Script - Pre-download Piper models to persistent storage

set -e

echo "🇳🇬 Wazobia Agent - Render Build Script"
echo "========================================"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create persistent data directory for Piper models
export PIPER_HOME=${PIPER_HOME:-/var/data/piper}
mkdir -p $PIPER_HOME

echo "📥 Pre-downloading Piper models to $PIPER_HOME..."
echo "   (This runs once during build and caches models for fast startup)"

# Download Piper model
# The model will be cached in PIPER_HOME so subsequent deployments reuse it
python3 << 'EOF'
import os
import sys
from piper.download import ensure_voice_exists

# Set Piper home to persistent storage
os.environ['PIPER_HOME'] = '/var/data/piper'

# Pre-download the English model that we use
# This ensures it's cached and won't timeout on first request
try:
    print("⏳ Downloading piper-tts models... (this may take 2-3 minutes)")
    ensure_voice_exists('en_US-lessac-medium', download_dir='/var/data/piper')
    print("✅ Models downloaded successfully!")
except Exception as e:
    print(f"⚠️  Warning: Could not pre-download models: {e}")
    print("   Models will download on first request (slower startup)")
    sys.exit(0)
EOF

echo ""
echo "✅ Build complete!"
echo "   Piper models are cached in /var/data/piper"
echo "   Voice API will be fast on first request ⚡"
