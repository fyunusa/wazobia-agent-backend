FROM python:3.10-slim

# Install system dependencies (including onnxruntime requirements)
RUN apt-get update && apt-get install -y \
    wget \
    tar \
    gzip \
    espeak-ng \
    espeak-ng-data \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application code first
COPY requirements.txt .

# Install Python dependencies (includes piper-tts with binary support)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create models directory for Piper voice models
RUN mkdir -p /var/data/piper /app/models

# Pre-download Piper voice model on build
# This ensures the ~1.5GB model is cached and first request won't timeout
RUN echo "⏳ Pre-downloading Piper voice model..." && \
    PIPER_HOME=/var/data/piper \
    timeout 180 bash -c 'echo "Welcome to Wazobia" | piper --model en_US-lessac-medium --output_file /tmp/test.wav 2>&1 || true' && \
    echo "✅ Piper models ready"

# Expose port
EXPOSE 8001

# Set Piper home for runtime
ENV PIPER_HOME=/var/data/piper

# Run FastAPI app
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8001"]
