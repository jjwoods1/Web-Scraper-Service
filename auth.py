"""
API Key authentication and management system.
"""
import os
import hashlib
import secrets
import logging
from functools import wraps
from flask import request, jsonify
from datetime import datetime

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages API key authentication and validation."""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from environment variables or file."""
        api_keys = {}
        
        # Load from environment variable (comma-separated)
        env_keys = os.getenv('API_KEYS', '')
        if env_keys:
            for key in env_keys.split(','):
                key = key.strip()
                if key:
                    api_keys[key] = {
                        'name': 'env_key',
                        'created_at': datetime.utcnow().isoformat(),
                        'active': True
                    }
        
        # Load from file if exists
        try:
            keys_file = os.getenv('API_KEYS_FILE', 'api_keys.txt')
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('|')
                            key = parts[0].strip()
                            name = parts[1].strip() if len(parts) > 1 else 'file_key'
                            api_keys[key] = {
                                'name': name,
                                'created_at': datetime.utcnow().isoformat(),
                                'active': True
                            }
        except Exception as e:
            logger.error(f"Error loading API keys from file: {e}")
        
        # If no keys found, create a default one (for development)
        if not api_keys:
            default_key = os.getenv('DEFAULT_API_KEY', 'dev-key-12345')
            api_keys[default_key] = {
                'name': 'default_development_key',
                'created_at': datetime.utcnow().isoformat(),
                'active': True
            }
            logger.warning(f"No API keys configured, using default key: {default_key}")
        
        logger.info(f"Loaded {len(api_keys)} API keys")
        return api_keys
    
    def validate_api_key(self, api_key):
        """
        Validate an API key.
        
        Args:
            api_key (str): The API key to validate
            
        Returns:
            dict: Validation result with key info or None if invalid
        """
        if not api_key:
            return None
        
        key_info = self.api_keys.get(api_key)
        if key_info and key_info.get('active', True):
            return key_info
        
        return None
    
    def generate_api_key(self, name="generated_key"):
        """
        Generate a new API key.
        
        Args:
            name (str): Name/description for the key
            
        Returns:
            str: The generated API key
        """
        # Generate a secure random key
        key = f"sk-{secrets.token_urlsafe(32)}"
        
        self.api_keys[key] = {
            'name': name,
            'created_at': datetime.utcnow().isoformat(),
            'active': True
        }
        
        logger.info(f"Generated new API key: {name}")
        return key
    
    def revoke_api_key(self, api_key):
        """
        Revoke an API key.
        
        Args:
            api_key (str): The API key to revoke
            
        Returns:
            bool: True if revoked successfully
        """
        if api_key in self.api_keys:
            self.api_keys[api_key]['active'] = False
            logger.info(f"Revoked API key: {self.api_keys[api_key]['name']}")
            return True
        
        return False
    
    def list_api_keys(self):
        """
        List all API keys (without showing the actual keys).
        
        Returns:
            list: List of API key information
        """
        return [
            {
                'key_id': key[:8] + '...' + key[-4:],
                'name': info['name'],
                'created_at': info['created_at'],
                'active': info['active']
            }
            for key, info in self.api_keys.items()
        ]

# Global API key manager instance
api_key_manager = APIKeyManager()

def require_api_key(f):
    """
    Decorator to require API key authentication for endpoints.
    
    Usage:
        @app.route('/api/endpoint')
        @require_api_key
        def endpoint():
            return jsonify({'message': 'success'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        
        # Also check Authorization header (Bearer token format)
        if not api_key:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Validate API key
        key_info = api_key_manager.validate_api_key(api_key)
        if not key_info:
            logger.warning(f"Invalid API key attempt from {request.remote_addr}")
            return jsonify({
                'success': False,
                'error': 'Invalid or missing API key',
                'message': 'Please provide a valid API key in the X-API-Key header or Authorization header',
                'timestamp': datetime.utcnow().isoformat()
            }), 401
        
        # Log successful authentication
        logger.info(f"API key authenticated: {key_info['name']} from {request.remote_addr}")
        
        # Store key info in request context for use in endpoint
        request.api_key_info = key_info
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_api_key(f):
    """
    Decorator for optional API key authentication.
    If API key is provided, it must be valid.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                api_key = auth_header[7:]
        
        # If API key is provided, validate it
        if api_key:
            key_info = api_key_manager.validate_api_key(api_key)
            if not key_info:
                logger.warning(f"Invalid API key attempt from {request.remote_addr}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid API key',
                    'message': 'The provided API key is invalid',
                    'timestamp': datetime.utcnow().isoformat()
                }), 401
            
            request.api_key_info = key_info
            logger.info(f"API key authenticated: {key_info['name']} from {request.remote_addr}")
        else:
            request.api_key_info = None
        
        return f(*args, **kwargs)
    
    return decorated_function