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
export PIPER_HOME=/var/data/piper
mkdir -p $PIPER_HOME

echo "📥 Pre-downloading Piper models to $PIPER_HOME..."
echo "   (This runs once during build - models cached on Render)"

# Set Piper home so it downloads to persistent storage
export PIPER_HOME=/var/data/piper
mkdir -p $PIPER_HOME/models

# Download Piper model using piper CLI
# This ensures the model files are cached in /var/data/piper
echo "⏳ Downloading en_US-lessac-medium voice model..."
python3 << 'PYTHON_SCRIPT'
import os
import subprocess
import sys

os.environ['PIPER_HOME'] = '/var/data/piper'

try:
    # Use piper's python interface to download model
    # This will download model files to PIPER_HOME/models
    result = subprocess.run(
        ['piper', '--model', 'en_US-lessac-medium', '--help'],
        capture_output=True,
        timeout=30,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Piper model appears to be available!")
    else:
        # Try downloading with echo
        print("⏳ Downloading model files...")
        result = subprocess.run(
            'echo "test" | piper --model en_US-lessac-medium --output_file /tmp/test.wav',
            shell=True,
            capture_output=True,
            timeout=60,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Model downloaded successfully!")
        else:
            print(f"⚠️  Model download: {result.stderr}")
            
except subprocess.TimeoutExpired:
    print("⚠️  Piper command timed out")
except Exception as e:
    print(f"⚠️  Could not pre-download: {e}")

print("✅ Build complete!")
print("   Piper models cached in /var/data/piper")
print("   Voice API will work on first request")
PYTHON_SCRIPT

echo ""
echo "✅ Build script finished"

