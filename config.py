"""
Configuration management for the unified scraper API.
"""
import os

class Config:
    """Configuration class for the scraper API."""
    
    # Request settings
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', 1.0))
    
    # Content limits
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 1000000))  # 1MB
    
    # Server settings
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', 'scraper_api.log')
    
    # API Key settings
    REQUIRE_API_KEY = os.getenv('REQUIRE_API_KEY', 'True').lower() == 'true'
    API_KEYS = os.getenv('API_KEYS', '')  # Comma-separated list of API keys
    API_KEYS_FILE = os.getenv('API_KEYS_FILE', 'api_keys.txt')
    DEFAULT_API_KEY = os.getenv('DEFAULT_API_KEY', 'dev-key-12345')
    
    @classmethod
    def to_dict(cls):
        """Convert configuration to dictionary."""
        return {
            'request_timeout': cls.REQUEST_TIMEOUT,
            'max_retries': cls.MAX_RETRIES,
            'rate_limit_delay': cls.RATE_LIMIT_DELAY,
            'max_content_length': cls.MAX_CONTENT_LENGTH,
            'port': cls.PORT,
            'host': cls.HOST,
            'debug': cls.DEBUG,
            'log_level': cls.LOG_LEVEL,
            'require_api_key': cls.REQUIRE_API_KEY,
            'api_keys_configured': bool(cls.API_KEYS or os.path.exists(cls.API_KEYS_FILE))
        }