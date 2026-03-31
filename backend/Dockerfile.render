# VISHWAS Backend - Render Free Tier Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for Render)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-render.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-render.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port (Render sets PORT automatically)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start command (Render provides PORT)
CMD ["uvicorn", "main-render:app", "--host", "0.0.0.0", "--port", "$PORT"]
