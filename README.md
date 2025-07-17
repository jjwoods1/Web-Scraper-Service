# 🕷️ Unified Web Scraper API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

A production-ready, secure, and scalable web scraping API service that combines URL extraction and text content scraping capabilities. Built with Flask and designed for enterprise deployment with comprehensive API key authentication.

## ✨ Features

- **🔗 URL Scraping**: Extract all hyperlinks from webpages with comprehensive metadata
- **📝 Text Scraping**: Extract clean, formatted text content from webpages
- **🔐 API Key Authentication**: Secure access with comprehensive key management
- **🏗️ Modular Architecture**: Clean, extensible codebase with separate scraper modules
- **🐳 Docker Support**: Fully containerized for easy deployment and scaling
- **⚡ Production Ready**: Comprehensive error handling, logging, and monitoring
- **🛡️ Rate Limiting**: Built-in protection against abuse and overload
- **📊 Health Monitoring**: Health check endpoints for monitoring and observability
- **🔧 Easy Configuration**: Environment-based configuration management
- **📈 Scalable**: Designed for high-performance production environments

## 🚀 Quick Start

#### Prerequisites
- Python 3.8+
- Docker (optional, for containerized deployment)

#### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/unified-scraper-api.git
   cd unified-scraper-api
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Generate API key**:
   ```bash
   python key_manager.py generate "my-app"
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Test the API**:
   ```bash
   # Test URL scraping
   curl -X POST http://localhost:5000/api/scrape/urls \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -d '{"url": "https://example.com"}'
   
   # Test text scraping
   curl -X POST http://localhost:5000/api/scrape/text \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -d '{"url": "https://example.com"}'
   ```

#### 🐳 Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build -d
   ```

2. **Or build and run manually**:
   ```bash
   docker build -t unified-scraper-api .
   docker run -p 5000:5000 -e API_KEYS="your-api-key-here" unified-scraper-api
   ```

## 📚 API Documentation

### Base URL: `http://localhost:5000`

### 🔐 Authentication

All scraping endpoints require API key authentication. Include your API key in the request header:

```bash
# Using X-API-Key header (recommended)
-H "X-API-Key: your-api-key-here"

# Or using Authorization header
-H "Authorization: Bearer your-api-key-here"
```

### POST /api/scrape/urls

Extract all URLs from a webpage.

**Request**:
```json
{
  "url": "https://example.com"
}
```

**Response**:
```json
{
  "success": true,
  "urls": [
    {
      "id": 1,
      "url": "https://example.com/page1",
      "original_href": "/page1",
      "text": "Page 1",
      "is_relative": true
    }
  ],
  "count": 1,
  "processing_time": 0.45,
  "timestamp": "2024-01-01T12:00:00.000Z",
  "error": null
}
```

### POST /api/scrape/text

Extract text content from a webpage.

**Request**:
```json
{
  "url": "https://example.com"
}
```

**Response**:
```json
{
  "success": true,
  "text": "Clean text content from the webpage...",
  "title": "Example Page Title",
  "meta_description": "Page description",
  "headings": {
    "h1": ["Main Heading"],
    "h2": ["Subheading 1", "Subheading 2"],
    "h3": ["Sub-subheading"]
  },
  "word_count": 1234,
  "character_count": 5678,
  "processing_time": 0.45,
  "timestamp": "2024-01-01T12:00:00.000Z",
  "error": null
}
```

### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "unified-scraper-api",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "version": "1.0.0"
}
```

### GET /api/info

Detailed service information.

**Response**:
```json
{
  "service": "Unified Web Scraper API",
  "version": "1.0.0",
  "description": "Production-ready unified API for web scraping operations",
  "endpoints": {
    "POST /api/scrape/urls": "Scrape URLs from a webpage",
    "POST /api/scrape/text": "Scrape text content from a webpage",
    "GET /health": "Health check",
    "GET /api/info": "Service information"
  },
  "configuration": {
    "request_timeout": 10,
    "max_retries": 3,
    "rate_limit_delay": 1.0,
    "max_content_length": 1000000
  }
}
```

## Configuration

Environment variables (can be set in `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `REQUEST_TIMEOUT` | 10 | HTTP request timeout in seconds |
| `MAX_RETRIES` | 3 | Maximum retry attempts for failed requests |
| `RATE_LIMIT_DELAY` | 1.0 | Delay between requests in seconds |
| `MAX_CONTENT_LENGTH` | 1000000 | Maximum content size in bytes (1MB) |
| `PORT` | 5000 | Server port |
| `HOST` | 0.0.0.0 | Server host |
| `DEBUG` | False | Enable debug mode |

## Production Deployment

### Environment Setup

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Modify configuration** as needed for production

### Docker Deployment (Recommended)

```bash
docker-compose up -d
```

### Manual Deployment with Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 30 app:app
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }
}
```

## Usage Examples

### PowerShell (Windows)

```powershell
# URL scraping
Invoke-RestMethod -Uri "http://localhost:5000/api/scrape/urls" -Method Post -ContentType "application/json" -Body '{"url": "https://example.com"}'

# Text scraping
Invoke-RestMethod -Uri "http://localhost:5000/api/scrape/text" -Method Post -ContentType "application/json" -Body '{"url": "https://example.com"}'
```

### Python Client

```python
import requests

# URL scraping
response = requests.post('http://localhost:5000/api/scrape/urls', 
                        json={'url': 'https://example.com'})
urls_data = response.json()

# Text scraping
response = requests.post('http://localhost:5000/api/scrape/text', 
                        json={'url': 'https://example.com'})
text_data = response.json()
```

### JavaScript/Node.js

```javascript
// URL scraping
const urlResponse = await fetch('http://localhost:5000/api/scrape/urls', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: 'https://example.com' })
});
const urlsData = await urlResponse.json();

// Text scraping
const textResponse = await fetch('http://localhost:5000/api/scrape/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: 'https://example.com' })
});
const textData = await textResponse.json();
```

## Adding New Features

The unified architecture makes it easy to add new scraping features:

1. **Add new scraping function** in `app.py`
2. **Create new API endpoint** following the pattern `/api/scrape/{feature}`
3. **Update the service info** in the `service_info()` function
4. **Add documentation** for the new endpoint

Example structure for a new feature:

```python
@app.route('/api/scrape/images', methods=['POST'])
def api_scrape_images():
    """Extract images from a webpage."""
    # Implementation here
    pass
```

## Monitoring and Logging

- **Logs**: Written to `scraper_api.log`
- **Health Check**: `GET /health`
- **Service Info**: `GET /api/info`
- **Performance Metrics**: Processing time included in all responses

## Error Handling

Comprehensive error handling for:
- Network timeouts and connection errors
- Invalid URLs and malformed requests
- Content size limits
- Parsing errors
- Rate limiting

## Security Features

- **CORS**: Enabled for cross-origin requests
- **Rate Limiting**: Built-in delays between requests
- **Content Limits**: Maximum content size protection
- **Input Validation**: URL validation and sanitization
- **Non-root User**: Docker container security
- **Realistic User Agent**: Avoids bot detection

## License

MIT License