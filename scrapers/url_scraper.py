"""
URL scraper for extracting hyperlinks from webpages.
"""
import logging
import time
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import BaseScraper

logger = logging.getLogger(__name__)

class URLScraper(BaseScraper):
    """Scraper for extracting URLs from webpages."""
    
    def scrape(self, url):
        """
        Extract all hyperlinks from a given URL and return them as full URLs.
        
        Args:
            url (str): The URL to scrape
            
        Returns:
            dict: Dictionary containing success status, URLs list, and metadata
        """
        start_time = time.time()
        
        try:
            # Validate URL
            url, error = self.validate_url(url)
            if error:
                return self._create_empty_response(error, start_time)
            
            # Get page response
            response = self.get_page_response(url)
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract links
            links = self._extract_links(soup, url)
            
            processing_time = time.time() - start_time
            logger.info(f"Successfully scraped {len(links)} URLs in {processing_time:.2f}s")
            
            return {
                'success': True,
                'urls': links,
                'count': len(links),
                'processing_time': round(processing_time, 2),
                'timestamp': datetime.utcnow().isoformat(),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error scraping URLs from {url}: {str(e)}")
            return self.handle_request_errors(url, e, start_time)
    
    def _extract_links(self, soup, base_url):
        """
        Extract all anchor tags and convert to link objects.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            base_url (str): Base URL for resolving relative links
            
        Returns:
            list: List of link objects
        """
        links = []
        
        for i, anchor in enumerate(soup.find_all('a', href=True)):
            href = anchor['href']
            full_url = urljoin(base_url, href)
            link_text = anchor.get_text(strip=True)
            
            # Determine if link is relative
            is_relative = not href.startswith(('http://', 'https://', 'mailto:', 'tel:', 'ftp://'))
            
            # Get additional link attributes
            link_title = anchor.get('title', '')
            link_class = ' '.join(anchor.get('class', []))
            
            link_obj = {
                'id': i + 1,
                'url': full_url,
                'original_href': href,
                'text': link_text,
                'title': link_title,
                'class': link_class,
                'is_relative': is_relative,
                'is_external': self._is_external_link(full_url, base_url),
                'link_type': self._get_link_type(href)
            }
            
            links.append(link_obj)
        
        return links
    
    def _is_external_link(self, link_url, base_url):
        """
        Check if a link is external (different domain).
        
        Args:
            link_url (str): The link URL
            base_url (str): The base URL
            
        Returns:
            bool: True if external link
        """
        try:
            from urllib.parse import urlparse
            link_domain = urlparse(link_url).netloc
            base_domain = urlparse(base_url).netloc
            return link_domain != base_domain and link_domain != ''
        except:
            return False
    
    def _get_link_type(self, href):
        """
        Determine the type of link.
        
        Args:
            href (str): The href attribute
            
        Returns:
            str: Link type (web, email, phone, file, etc.)
        """
        if href.startswith('mailto:'):
            return 'email'
        elif href.startswith('tel:'):
            return 'phone'
        elif href.startswith('ftp:'):
            return 'ftp'
        elif href.startswith('#'):
            return 'anchor'
        elif href.startswith('javascript:'):
            return 'javascript'
        elif any(href.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']):
            return 'file'
        else:
            return 'web'
    
    def _create_empty_response(self, error_msg, start_time):
        """
        Create an empty response for URL scraping errors.
        
        Args:
            error_msg (str): Error message
            start_time (float): Start time
            
        Returns:
            dict: Empty response with error
        """
        return {
            'success': False,
            'urls': [],
            'count': 0,
            'processing_time': round(time.time() - start_time, 2),
            'timestamp': datetime.utcnow().isoformat(),
            'error': error_msg
        }
    
    def get_links_by_type(self, url, link_type='web'):
        """
        Get links filtered by type.
        
        Args:
            url (str): URL to scrape
            link_type (str): Type of links to return
            
        Returns:
            dict: Filtered scraping results
        """
        result = self.scrape(url)
        
        if result['success']:
            filtered_urls = [
                link for link in result['urls'] 
                if link['link_type'] == link_type
            ]
            
            result['urls'] = filtered_urls
            result['count'] = len(filtered_urls)
        
        return result
    
    def get_external_links(self, url):
        """
        Get only external links from a webpage.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            dict: Scraping results with only external links
        """
        result = self.scrape(url)
        
        if result['success']:
            external_urls = [
                link for link in result['urls'] 
                if link['is_external']
            ]
            
            result['urls'] = external_urls
            result['count'] = len(external_urls)
        
        return result