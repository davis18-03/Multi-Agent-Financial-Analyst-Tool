#!/usr/bin/env python3
"""
Health check script for Multi-Agent Financial Analyst Tool

This script can be used to verify that the application is running correctly.
"""

import os
import sys
import requests
import time
from datetime import datetime


def check_health(base_url=None, max_retries=5, delay=2):
    """
    Check if the application is healthy.
    
    Args:
        base_url (str): Base URL to check (defaults to localhost with PORT env var)
        max_retries (int): Maximum number of retries
        delay (int): Delay between retries in seconds
    
    Returns:
        bool: True if healthy, False otherwise
    """
    if base_url is None:
        port = os.environ.get("PORT", "8000")
        base_url = f"http://localhost:{port}"
    
    health_url = f"{base_url}/health"
    
    print(f"Checking health at: {health_url}")
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed!")
                print(f"   Status: {data.get('status')}")
                print(f"   Version: {data.get('version')}")
                print(f"   Uptime: {data.get('uptime', 0):.2f}s")
                print(f"   Timestamp: {data.get('timestamp')}")
                return True
            else:
                print(f"❌ Health check failed with status code: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed (attempt {attempt + 1})")
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout (attempt {attempt + 1})")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        if attempt < max_retries - 1:
            print(f"   Retrying in {delay} seconds...")
            time.sleep(delay)
    
    print(f"❌ Health check failed after {max_retries} attempts")
    return False


def test_query_endpoint(base_url=None):
    """Test the query endpoint with a simple request."""
    if base_url is None:
        port = os.environ.get("PORT", "8000")
        base_url = f"http://localhost:{port}"
    
    query_url = f"{base_url}/query"
    
    test_data = {
        "user_id": "health_check_user",
        "query": "What is the current market trend?"
    }
    
    try:
        print(f"\nTesting query endpoint: {query_url}")
        response = requests.post(query_url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query endpoint test passed!")
            print(f"   Processing time: {data.get('processing_time', 0):.2f}s")
            print(f"   Success: {data.get('success')}")
            return True
        else:
            print(f"❌ Query endpoint test failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query endpoint test failed: {e}")
        return False


def main():
    """Main function."""
    print("🔍 Multi-Agent Financial Analyst - Health Check")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Get base URL from command line or environment
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = None
    
    # Run health check
    health_ok = check_health(base_url)
    
    if health_ok:
        # Test query endpoint
        query_ok = test_query_endpoint(base_url)
        
        if query_ok:
            print("\n🎉 All checks passed! Application is healthy.")
            sys.exit(0)
        else:
            print("\n⚠️  Health check passed but query endpoint failed.")
            sys.exit(1)
    else:
        print("\n❌ Health check failed. Application may not be running.")
        sys.exit(1)


if __name__ == "__main__":
    main()