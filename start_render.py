#!/usr/bin/env python3
"""
Render.com startup script for Multi-Agent Financial Analyst Tool

This script ensures proper port binding for Render deployment.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Main startup function for Render deployment."""
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Get port from environment (Render sets this)
    port = os.environ.get("PORT")
    if not port:
        print("ERROR: PORT environment variable not set")
        sys.exit(1)
    
    print(f"Starting FastAPI server on port {port}")
    
    # Start the server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "api:app",
        "--host", "0.0.0.0",
        "--port", port,
        "--workers", "1"  # Single worker for free tier
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Server failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Server stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()