# Environment Variables Configuration

This document explains how to configure environment variables for the Flask Web Scraper API.

## Quick Start

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file** with your configuration:
   ```bash
   nano .env
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

## Environment Variables

### API Keys Configuration

- **`API_KEYS`**: Comma-separated list of valid API keys
  - Example: `API_KEYS=key1,key2,key3`
  - These keys will be automatically loaded and validated

- **`DEFAULT_API_KEY`**: Default API key for development
  - Default: `dev-key-12345`
  - Used when no other API keys are configured

- **`REQUIRE_API_KEY`**: Whether API key authentication is required
  - Default: `true`
  - Set to `false` to disable authentication (not recommended for production)

### Server Configuration

- **`PORT`**: Port number for the Flask application
  - Default: `5000`
  - Example: `PORT=8080`

- **`HOST`**: Host interface to bind to
  - Default: `0.0.0.0`
  - Use `127.0.0.1` for localhost only

- **`DEBUG`**: Enable Flask debug mode
  - Default: `false`
  - Set to `true` for development

- **`FLASK_ENV`**: Flask environment
  - Default: `production`
  - Options: `development`, `production`

### Request Settings

- **`REQUEST_TIMEOUT`**: HTTP request timeout in seconds
  - Default: `10`
  - Example: `REQUEST_TIMEOUT=30`

- **`MAX_RETRIES`**: Maximum number of retry attempts
  - Default: `3`
  - Example: `MAX_RETRIES=5`

- **`RATE_LIMIT_DELAY`**: Delay between requests in seconds
  - Default: `1.0`
  - Example: `RATE_LIMIT_DELAY=0.5`

### Content Settings

- **`MAX_CONTENT_LENGTH`**: Maximum content length in bytes
  - Default: `1000000` (1MB)
  - Example: `MAX_CONTENT_LENGTH=5000000`

### Logging Configuration

- **`LOG_LEVEL`**: Logging level
  - Default: `INFO`
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`

- **`LOG_FILE`**: Log file path
  - Default: `scraper_api.log`
  - Example: `LOG_FILE=/app/logs/scraper.log`

### Security

- **`SECRET_KEY`**: Flask secret key for session management
  - Required for production
  - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

### Additional Settings

- **`API_KEYS_FILE`**: Path to file containing API keys
  - Default: `api_keys.txt`
  - Format: One key per line, optionally with name: `key|name`

- **`ALLOWED_ORIGINS`**: CORS allowed origins
  - Default: `*`
  - Example: `ALLOWED_ORIGINS=https://yourdomain.com,https://anotherdomain.com`

## Docker Compose Configuration

The `docker-compose.yml` file is configured to:

1. **Load .env file**: Uses `env_file: - .env` to load all environment variables
2. **Override specific variables**: Can override variables in the `environment` section
3. **Create custom network**: Uses `scraper-net` network for isolation
4. **Expose port 5000**: Maps container port 5000 to host port 5000

### Example docker-compose.yml:

```yaml
version: '3.8'

services:
  scraper-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    env_file:
      - .env  # Loads environment variables from .env file
    environment:
      # Override specific variables here
      - HOST=0.0.0.0
      - PORT=5000
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - scraper-net
    restart: unless-stopped

networks:
  scraper-net:
    driver: bridge
```

## Testing Environment Variables

### Test API Keys:

```bash
# Test with valid API key
curl -X POST "http://localhost:5000/api/scrape/urls" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{"url": "https://example.com"}'

# Test with invalid API key (should fail)
curl -X POST "http://localhost:5000/api/scrape/urls" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid-key" \
  -d '{"url": "https://example.com"}'
```

### Test Environment Loading:

```bash
# Check if environment variables are loaded
docker-compose exec scraper-api env | grep API_KEYS

# Check application logs
docker-compose logs scraper-api
```

## Troubleshooting

### Environment Variables Not Loading

1. **Check .env file exists**: Ensure `.env` file is in the same directory as `docker-compose.yml`
2. **Check .env format**: No spaces around `=`, no quotes unless needed
3. **Rebuild container**: Run `docker-compose up --build` to rebuild with new environment
4. **Check Docker logs**: `docker-compose logs scraper-api` for error messages

### API Key Authentication Issues

1. **Verify API_KEYS variable**: Check if your API keys are properly set in `.env`
2. **Check request headers**: Ensure `X-API-Key` header is being sent
3. **Check logs**: Look for authentication attempts in application logs
4. **Test default key**: Try using the default key `dev-key-12345`

### Common Issues

1. **Port already in use**: Change `PORT` in `.env` or stop conflicting services
2. **Permission denied**: Ensure Docker has proper permissions
3. **File not found**: Check file paths in environment variables
4. **Invalid format**: Ensure .env file follows `KEY=value` format

## Production Considerations

1. **Generate secure API keys**: Use strong, random API keys
2. **Set strong secret key**: Generate a secure `SECRET_KEY`
3. **Enable HTTPS**: Configure SSL/TLS certificates
4. **Limit origins**: Set specific domains in `ALLOWED_ORIGINS`
5. **Monitor logs**: Set up proper logging and monitoring
6. **Regular updates**: Keep dependencies and keys updated

## Example Production .env

```bash
# Production Environment Variables
API_KEYS=sk-prod-abc123...,sk-prod-def456...,sk-prod-ghi789...
DEFAULT_API_KEY=sk-prod-abc123...
REQUIRE_API_KEY=true
PORT=5000
HOST=0.0.0.0
DEBUG=false
FLASK_ENV=production
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RATE_LIMIT_DELAY=0.5
MAX_CONTENT_LENGTH=5000000
LOG_LEVEL=INFO
LOG_FILE=/app/logs/scraper.log
SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com
```