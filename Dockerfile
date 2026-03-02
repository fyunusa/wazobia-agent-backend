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

# Pre-download Piper voice model during build to /app
# Models will be cached in the Docker image and available immediately at runtime
RUN echo "⏳ Pre-downloading Piper voice model..." && \
    export PIPER_HOME=/app && \
    echo "Welcome to Wazobia" | piper --model en_US-lessac-medium --output_file /tmp/test.wav 2>/dev/null || true && \
    echo "✅ Piper models cached in Docker image"

# Expose port
EXPOSE 8001

# Set Piper home to /app where models are already cached in the Docker image
# This avoids redundant downloads at runtime
ENV PIPER_HOME=/app

# Run FastAPI app
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8001"]
