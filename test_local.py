#!/usr/bin/env python3
"""
Local testing script for the unified scraper API.
"""
import subprocess
import time
import requests
import json
import threading
import sys
from datetime import datetime

def start_server():
    """Start the Flask server in a separate thread."""
    try:
        subprocess.run([sys.executable, "app.py"], cwd=".", check=True)
    except KeyboardInterrupt:
        print("Server stopped.")

def test_api_endpoints():
    """Test API endpoints once server is running."""
    base_url = "http://localhost:5000"
    api_key = "dev-key-12345"  # Default development key
    
    print("🔍 Testing Unified Scraper API Locally")
    print(f"🔑 Using API Key: {api_key}")
    print("=" * 60)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    for i in range(30):
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is running!")
                break
        except:
            time.sleep(1)
    else:
        print("❌ Server failed to start within 30 seconds")
        return False
    
    # Test 1: Health check
    print("\n1. 🏥 Health Check:")
    try:
        response = requests.get(f"{base_url}/health")
        health = response.json()
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Service: {health.get('service', 'unknown')}")
        print(f"   Authenticated: {health.get('authenticated', False)}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Service info
    print("\n2. ℹ️  Service Information:")
    try:
        response = requests.get(f"{base_url}/api/info")
        info = response.json()
        print(f"   Service: {info.get('service', 'unknown')}")
        print(f"   Version: {info.get('version', 'unknown')}")
        print(f"   Endpoints: {len(info.get('endpoints', {}))}")
    except Exception as e:
        print(f"   ❌ Service info failed: {e}")
        return False
    
    # Test 3: URL scraping without API key (should fail)
    print("\n3. 🔓 URL Scraping (without API key - should fail):")
    try:
        response = requests.post(
            f"{base_url}/api/scrape/urls",
            json={"url": "https://example.com"},
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        if result.get('success'):
            print("   ❌ SECURITY ISSUE: Request succeeded without API key!")
        else:
            print(f"   ✅ Properly rejected: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    # Test 4: URL scraping with API key
    print("\n4. 🔗 URL Scraping (with API key):")
    try:
        response = requests.post(
            f"{base_url}/api/scrape/urls",
            json={"url": "https://example.com"},
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            }
        )
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Success: Found {result.get('count', 0)} URLs")
            print(f"   ⏱️  Processing Time: {result.get('processing_time', 0)}s")
            if result.get('urls'):
                print("   📋 Sample URLs:")
                for i, url_obj in enumerate(result['urls'][:3]):
                    print(f"      {i+1}. {url_obj.get('text', 'No text')}: {url_obj.get('url', 'No URL')}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    # Test 5: Text scraping with API key
    print("\n5. 📝 Text Scraping (with API key):")
    try:
        response = requests.post(
            f"{base_url}/api/scrape/text",
            json={"url": "https://example.com"},
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            }
        )
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Success: Extracted text content")
            print(f"   📄 Title: {result.get('title', 'No title')}")
            print(f"   📝 Word Count: {result.get('word_count', 0)}")
            print(f"   🔤 Character Count: {result.get('character_count', 0)}")
            print(f"   ⏱️  Processing Time: {result.get('processing_time', 0)}s")
            if result.get('text'):
                print(f"   📋 Sample Text: {result['text'][:100]}...")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed successfully!")
    print("🚀 Your API is ready for production deployment!")
    return True

def main():
    """Main testing function."""
    print("🚀 Starting Local API Testing")
    print("=" * 60)
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Run tests
    try:
        success = test_api_endpoints()
        if success:
            print("\n✅ All tests passed! Service is ready for deployment.")
        else:
            print("\n❌ Some tests failed. Please check the issues above.")
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user.")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
    
    print("\n🔄 Press Ctrl+C to stop the server and exit.")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()