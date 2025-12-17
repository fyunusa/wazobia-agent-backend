#!/bin/bash
# Quick start script for Wazobia Agent

set -e

echo "🇳🇬 Wazobia Agent - Quick Start Setup"
echo "======================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created - please edit it with your API keys"
else
    echo "✓ .env file already exists"
fi

# Check data directory
if [ -d "data" ] && [ "$(ls -A data)" ]; then
    DATA_FILES=$(ls data/*.json 2>/dev/null | wc -l)
    echo "✓ Found $DATA_FILES data files in data/ directory"
else
    echo "⚠️  Warning: data/ directory is empty or missing"
    echo "   The agent will work but won't have knowledge base content"
fi

echo ""
echo "======================================"
echo "✅ Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys (if using LLM)"
echo "2. Start the server: python run.py"
echo "3. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "Quick commands:"
echo "  python run.py              - Start the API server"
echo "  python examples.py         - Run usage examples"
echo "  pytest                     - Run tests"
echo ""
echo "For more information, see README.md"
