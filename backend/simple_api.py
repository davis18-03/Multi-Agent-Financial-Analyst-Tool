"""
Simple API for initial deployment testing
This is a minimal FastAPI app to test deployment without heavy dependencies
"""

from fastapi import FastAPI
from datetime import datetime
from typing import Dict, Any
import os

app = FastAPI(
    title="Multi-Agent Financial Analyst - Simple API",
    description="Minimal API for deployment testing",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Multi-Agent Financial Analyst API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "uptime": "running"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working."""
    return {
        "message": "API is working correctly!",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": "3.10+"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
