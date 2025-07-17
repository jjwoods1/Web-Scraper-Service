import logging
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import configuration and scrapers
from config import Config
from scrapers.url_scraper import URLScraper
from scrapers.text_scraper import TextScraper
from auth import require_api_key, optional_api_key, api_key_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize scrapers
url_scraper = URLScraper(Config)
text_scraper = TextScraper(Config)

def validate_url_request(data):
    """Common URL validation for requests."""
    if not data or 'url' not in data:
        return None, 'Missing required field: url'
    
    url = data['url'].strip()
    
    if not url:
        return None, 'URL cannot be empty'
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url, None

# API Routes

@app.route('/api/scrape/urls', methods=['POST'])
@require_api_key
def api_scrape_urls():
    """
    API endpoint to scrape URLs from a given webpage.
    Requires API key authentication.
    """
    try:
        data = request.get_json()
        url, error = validate_url_request(data)
        
        if error:
            return jsonify({
                'success': False,
                'urls': [],
                'count': 0,
                'processing_time': 0,
                'timestamp': datetime.utcnow().isoformat(),
                'error': error
            }), 400
        
        # Rate limiting
        time.sleep(Config.RATE_LIMIT_DELAY)
        
        result = url_scraper.scrape(url)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({
            'success': False,
            'urls': [],
            'count': 0,
            'processing_time': 0,
            'timestamp': datetime.utcnow().isoformat(),
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/scrape/text', methods=['POST'])
@require_api_key
def api_scrape_text():
    """
    API endpoint to scrape text content from a given webpage.
    Requires API key authentication.
    """
    try:
        data = request.get_json()
        url, error = validate_url_request(data)
        
        if error:
            return jsonify({
                'success': False,
                'text': '',
                'title': '',
                'meta_description': '',
                'headings': {},
                'word_count': 0,
                'character_count': 0,
                'processing_time': 0,
                'timestamp': datetime.utcnow().isoformat(),
                'error': error
            }), 400
        
        # Rate limiting
        time.sleep(Config.RATE_LIMIT_DELAY)
        
        result = text_scraper.scrape(url)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({
            'success': False,
            'text': '',
            'title': '',
            'meta_description': '',
            'headings': {},
            'word_count': 0,
            'character_count': 0,
            'processing_time': 0,
            'timestamp': datetime.utcnow().isoformat(),
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
@optional_api_key
def health_check():
    """Health check endpoint (API key optional)."""
    return jsonify({
        'status': 'healthy',
        'service': 'unified-scraper-api',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'authenticated': hasattr(request, 'api_key_info') and request.api_key_info is not None
    }), 200

@app.route('/api/info', methods=['GET'])
@optional_api_key
def service_info():
    """Service information endpoint (API key optional)."""
    return jsonify({
        'service': 'Unified Web Scraper API',
        'version': '1.0.0',
        'description': 'Production-ready unified API for web scraping operations',
        'endpoints': {
            'POST /api/scrape/urls': 'Scrape URLs from a webpage',
            'POST /api/scrape/text': 'Scrape text content from a webpage',
            'GET /health': 'Health check',
            'GET /api/info': 'Service information'
        },
        'configuration': Config.to_dict(),
        'example_usage': {
            'url_scraping': {
                'url': '/api/scrape/urls',
                'method': 'POST',
                'payload': {'url': 'https://example.com'}
            },
            'text_scraping': {
                'url': '/api/scrape/text',
                'method': 'POST',
                'payload': {'url': 'https://example.com'}
            }
        }
    }), 200

@app.route('/', methods=['GET'])
@optional_api_key
def home():
    """Home endpoint with basic info."""
    return jsonify({
        'message': 'Unified Web Scraper API',
        'version': '1.0.0',
        'status': 'running',
        'authentication': {
            'required': Config.REQUIRE_API_KEY,
            'authenticated': hasattr(request, 'api_key_info') and request.api_key_info is not None
        },
        'endpoints': {
            'POST /api/scrape/urls': 'Scrape URLs from a webpage (requires API key)',
            'POST /api/scrape/text': 'Scrape text content from a webpage (requires API key)',
            'GET /health': 'Health check',
            'GET /api/info': 'Detailed service information',
            'GET /api/keys': 'API key management (requires API key)'
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'timestamp': datetime.utcnow().isoformat(),
        'available_endpoints': [
            'POST /api/scrape/urls (requires API key)',
            'POST /api/scrape/text (requires API key)',
            'GET /health',
            'GET /api/info',
            'GET /api/keys (requires API key)'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

# API Key Management Endpoints
@app.route('/api/keys', methods=['GET'])
@require_api_key
def list_api_keys():
    """List all API keys (without showing actual keys)."""
    keys = api_key_manager.list_api_keys()
    return jsonify({
        'success': True,
        'keys': keys,
        'count': len(keys),
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/keys/generate', methods=['POST'])
@require_api_key
def generate_api_key():
    """Generate a new API key."""
    data = request.get_json() or {}
    name = data.get('name', 'generated_key')
    
    new_key = api_key_manager.generate_api_key(name)
    
    return jsonify({
        'success': True,
        'message': 'API key generated successfully',
        'key': new_key,
        'name': name,
        'timestamp': datetime.utcnow().isoformat(),
        'warning': 'Store this key securely. It will not be shown again.'
    }), 201

@app.route('/api/keys/revoke', methods=['POST'])
@require_api_key
def revoke_api_key():
    """Revoke an API key."""
    data = request.get_json() or {}
    key_to_revoke = data.get('key')
    
    if not key_to_revoke:
        return jsonify({
            'success': False,
            'error': 'Missing required field: key',
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    success = api_key_manager.revoke_api_key(key_to_revoke)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'API key revoked successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'API key not found',
            'timestamp': datetime.utcnow().isoformat()
        }), 404

if __name__ == '__main__':
    logger.info(f"Starting Unified Scraper API on {Config.HOST}:{Config.PORT}")
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)