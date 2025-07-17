"""
Base scraper functionality shared across all scrapers.
"""
import logging
import requests
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class BaseScraper:
    """Base class for all scrapers with common functionality."""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page_response(self, url):
        """
        Get HTTP response for a URL with proper error handling.
        
        Args:
            url (str): URL to fetch
            
        Returns:
            requests.Response: HTTP response object
            
        Raises:
            requests.exceptions.RequestException: For HTTP errors
        """
        logger.info(f"Fetching URL: {url}")
        response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response
    
    def create_error_response(self, error_msg, start_time=None):
        """
        Create a standardized error response.
        
        Args:
            error_msg (str): Error message
            start_time (float): Optional start time for processing calculation
            
        Returns:
            dict: Standardized error response
        """
        processing_time = time.time() - start_time if start_time else 0
        
        return {
            'success': False,
            'processing_time': round(processing_time, 2),
            'timestamp': datetime.utcnow().isoformat(),
            'error': error_msg
        }
    
    def handle_request_errors(self, url, error, start_time):
        """
        Handle common request errors with appropriate logging.
        
        Args:
            url (str): URL that failed
            error (Exception): The exception that occurred
            start_time (float): Start time for processing calculation
            
        Returns:
            dict: Error response
        """
        if isinstance(error, requests.exceptions.Timeout):
            error_msg = f"Request timeout after {self.config.REQUEST_TIMEOUT} seconds"
            logger.error(f"Timeout error for {url}: {error_msg}")
        elif isinstance(error, requests.exceptions.RequestException):
            error_msg = f"Request failed: {str(error)}"
            logger.error(f"Request error for {url}: {error_msg}")
        else:
            error_msg = f"Unexpected error: {str(error)}"
            logger.error(f"Unexpected error for {url}: {error_msg}")
        
        return self.create_error_response(error_msg, start_time)
    
    def validate_url(self, url):
        """
        Validate and normalize a URL.
        
        Args:
            url (str): URL to validate
            
        Returns:
            tuple: (normalized_url, error_message)
        """
        if not url:
            return None, 'URL cannot be empty'
        
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url, None