# Multi-Agent Financial Analyst Tool - Docker Configuration
# This Dockerfile can run both backend and frontend for local testing
# For production deployment, use separate containers or Render/Streamlit Cloud

FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=development \
    LOG_LEVEL=INFO

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs charts vector_store .streamlit

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["python", "run_app.py", "backend"]

# Build instructions:
# docker build -t multi-agent-fin-analyst .
# 
# Run backend only:
# docker run -p 8000:8000 -e OPENROUTER_API_KEY=your-key multi-agent-fin-analyst
# 
# Run with custom command:
# docker run -p 8000:8000 -p 8501:8501 -e OPENROUTER_API_KEY=your-key multi-agent-fin-analyst python run_app.py both
