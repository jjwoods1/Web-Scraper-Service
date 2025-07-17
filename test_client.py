import requests
import json
import time

class ScraperAPIClient:
    def __init__(self, base_url="http://localhost:5000", api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def scrape_urls(self, url):
        """Scrape URLs from a webpage."""
        try:
            response = requests.post(
                f"{self.base_url}/api/scrape/urls",
                json={"url": url},
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": f"API call failed: {str(e)}"}
    
    def scrape_text(self, url):
        """Scrape text content from a webpage."""
        try:
            response = requests.post(
                f"{self.base_url}/api/scrape/text",
                json={"url": url},
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": f"API call failed: {str(e)}"}
    
    def health_check(self):
        """Check API health."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"status": "error", "error": f"Health check failed: {str(e)}"}
    
    def get_info(self):
        """Get service information."""
        try:
            response = requests.get(f"{self.base_url}/api/info")
            return response.json()
        except Exception as e:
            return {"service": "unknown", "error": f"Info request failed: {str(e)}"}

def test_api():
    """Test the unified scraper API."""
    # Use default API key for testing
    api_key = "dev-key-12345"  # Default development key
    client = ScraperAPIClient(api_key=api_key)
    test_url = "https://example.com"
    
    print("🔍 Testing Unified Scraper API")
    print(f"🔑 Using API Key: {api_key}")
    print("=" * 50)
    
    # Test health check
    print("\n1. Health Check:")
    health = client.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    print(f"   Service: {health.get('service', 'unknown')}")
    print(f"   Authenticated: {health.get('authenticated', False)}")
    
    # Test service info
    print("\n2. Service Information:")
    info = client.get_info()
    print(f"   Service: {info['service']}")
    print(f"   Version: {info['version']}")
    print(f"   Available Endpoints: {len(info['endpoints'])}")
    
    # Test URL scraping
    print(f"\n3. URL Scraping from {test_url}:")
    start_time = time.time()
    urls_result = client.scrape_urls(test_url)
    
    if urls_result['success']:
        print(f"   ✅ Success: Found {urls_result['count']} URLs")
        print(f"   ⏱️  Processing Time: {urls_result['processing_time']}s")
        print("   📋 Sample URLs:")
        for i, url_obj in enumerate(urls_result['urls'][:3]):
            print(f"      {i+1}. {url_obj['text']}: {url_obj['url']}")
    else:
        print(f"   ❌ Error: {urls_result['error']}")
    
    # Test text scraping
    print(f"\n4. Text Scraping from {test_url}:")
    text_result = client.scrape_text(test_url)
    
    if text_result['success']:
        print(f"   ✅ Success: Extracted text content")
        print(f"   📄 Title: {text_result['title']}")
        print(f"   📝 Word Count: {text_result['word_count']}")
        print(f"   🔤 Character Count: {text_result['character_count']}")
        print(f"   ⏱️  Processing Time: {text_result['processing_time']}s")
        print(f"   📋 Sample Text: {text_result['text'][:100]}...")
        
        # Show headings if available
        if text_result['headings']['h1']:
            print(f"   📑 H1 Headings: {text_result['headings']['h1']}")
    else:
        print(f"   ❌ Error: {text_result['error']}")
    
    print("\n" + "=" * 50)
    print("🎉 API Test Complete!")

def test_without_api_key():
    """Test API without API key to verify authentication."""
    print("\n🔓 Testing API without API key")
    print("=" * 50)
    
    client = ScraperAPIClient()  # No API key
    
    # Test health check (should work)
    print("\n1. Health Check (should work):")
    health = client.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    print(f"   Authenticated: {health.get('authenticated', False)}")
    
    # Test URL scraping (should fail)
    print("\n2. URL Scraping (should fail):")
    result = client.scrape_urls("https://example.com")
    if result.get('success'):
        print("   ❌ SECURITY ISSUE: Request succeeded without API key!")
    else:
        print(f"   ✅ Properly rejected: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_api()
    test_without_api_key()