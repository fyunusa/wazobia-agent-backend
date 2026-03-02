FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    tar \
    gzip \
    espeak-ng \
    espeak-ng-data \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download Piper binary release from GitHub
RUN echo "⏳ Downloading Piper binary..." && \
    wget -q https://github.com/rhasspy/piper/releases/download/2023.11.14-1/piper_linux_x86_64.tar.gz && \
    tar -xzf piper_linux_x86_64.tar.gz && \
    rm piper_linux_x86_64.tar.gz && \
    chmod +x piper && \
    echo "✅ Piper binary installed"

# Add Piper to PATH
ENV PATH="/app:$PATH"

# Create models directory for Piper voice models
RUN mkdir -p /app/models && mkdir -p /var/data/piper

# Copy application code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-download Piper voice model for faster first request
# Use echo to trigger model download without blocking
RUN echo "⏳ Pre-downloading voice model..." && \
    timeout 120 bash -c 'echo "test" | piper --model en_US-lessac-medium --output_file /tmp/test.wav' || true && \
    echo "✅ Voice model ready"

# Expose port
EXPOSE 8001

# Run FastAPI app
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8001"]
