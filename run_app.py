#!/usr/bin/env python3
"""
Application Runner for Multi-Agent Financial Analyst Tool

This script provides convenient commands to start the backend and frontend
components of the Multi-Agent Financial Analyst Tool.

Usage:
    python run_app.py backend    # Start FastAPI backend
    python run_app.py frontend   # Start Streamlit frontend
    python run_app.py both       # Start both (requires two terminals)
    python run_app.py check      # Check system requirements
"""

import sys
import subprocess
import os
import time
import requests
from pathlib import Path


def check_requirements():
    """Check if all required packages are installed."""
    print("🔍 Checking system requirements...")
    
    required_packages = [
        'streamlit', 'fastapi', 'uvicorn', 'requests', 'pandas', 
        'numpy', 'yfinance', 'matplotlib', 'seaborn', 'loguru'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required packages are installed!")
    return True


def check_backend_health(url="http://localhost:8000", timeout=5):
    """Check if the backend is healthy."""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False


def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting FastAPI backend server...")
    
    # Check if backend is already running
    if check_backend_health():
        print("⚠️  Backend is already running on http://localhost:8000")
        return
    
    try:
        # Change to backend directory
        backend_dir = Path(__file__).parent / "backend"
        os.chdir(backend_dir)
        
        # Start the server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "api:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ]
        
        print("Starting backend with command:", " ".join(cmd))
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")


def start_frontend():
    """Start the Streamlit frontend."""
    print("🚀 Starting Streamlit frontend...")
    
    try:
        # Check if backend is running
        if not check_backend_health():
            print("⚠️  Backend is not running. Please start it first:")
            print("   python run_app.py backend")
            return
        
        # Start Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", 
            "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ]
        
        print("Starting frontend with command:", " ".join(cmd))
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")


def start_both():
    """Start both backend and frontend (requires two terminals)."""
    print("🚀 Starting both backend and frontend...")
    print("\n📋 Instructions:")
    print("1. Open two terminal windows")
    print("2. In terminal 1, run: python run_app.py backend")
    print("3. In terminal 2, run: python run_app.py frontend")
    print("4. Access the app at: http://localhost:8501")
    print("\n⏳ Waiting for backend to start...")
    
    # Wait for backend to start
    for i in range(30):
        if check_backend_health():
            print("✅ Backend is ready!")
            print("🚀 Now starting frontend...")
            time.sleep(2)
            start_frontend()
            return
        time.sleep(1)
        print(".", end="", flush=True)
    
    print("\n❌ Backend failed to start within 30 seconds")


def show_status():
    """Show the current status of backend and frontend."""
    print("📊 System Status:")
    
    # Check backend
    if check_backend_health():
        print("✅ Backend: Running on http://localhost:8000")
    else:
        print("❌ Backend: Not running")
    
    # Check frontend (basic check)
    try:
        response = requests.get("http://localhost:8501", timeout=2)
        if response.status_code == 200:
            print("✅ Frontend: Running on http://localhost:8501")
        else:
            print("❌ Frontend: Not responding")
    except:
        print("❌ Frontend: Not running")


def show_help():
    """Show help information."""
    print("""
🤖 Multi-Agent Financial Analyst Tool

Usage:
    python run_app.py <command>

Commands:
    backend     Start FastAPI backend server
    frontend    Start Streamlit frontend
    both        Show instructions to start both
    check       Check system requirements
    status      Show current system status
    help        Show this help message

Examples:
    python run_app.py backend    # Start backend only
    python run_app.py frontend   # Start frontend only
    python run_app.py check      # Check requirements

URLs:
    Frontend: http://localhost:8501
    Backend:  http://localhost:8000
    API Docs: http://localhost:8000/docs
""")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    if command == "backend":
        start_backend()
    elif command == "frontend":
        start_frontend()
    elif command == "both":
        start_both()
    elif command == "check":
        check_requirements()
    elif command == "status":
        show_status()
    elif command in ["help", "-h", "--help"]:
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python run_app.py help' for usage information")


if __name__ == "__main__":
    main()
