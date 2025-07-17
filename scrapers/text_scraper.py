"""
Text scraper for extracting clean text content from webpages.
"""
import logging
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
from .base import BaseScraper

logger = logging.getLogger(__name__)

class TextScraper(BaseScraper):
    """Scraper for extracting text content from webpages."""
    
    def scrape(self, url):
        """
        Extract all text content from a given URL.
        
        Args:
            url (str): The URL to scrape
            
        Returns:
            dict: Dictionary containing success status, text content, and metadata
        """
        start_time = time.time()
        
        try:
            # Validate URL
            url, error = self.validate_url(url)
            if error:
                return self._create_empty_response(error, start_time)
            
            # Get page response
            response = self.get_page_response(url)
            
            # Check content length
            if len(response.content) > self.config.MAX_CONTENT_LENGTH:
                error_msg = f'Content too large: {len(response.content)} bytes (max: {self.config.MAX_CONTENT_LENGTH})'
                logger.warning(f"Content length exceeds limit for {url}")
                return self._create_empty_response(error_msg, start_time)
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text and metadata
            text_data = self._extract_text_content(soup)
            
            processing_time = time.time() - start_time
            logger.info(f"Successfully scraped {text_data['word_count']} words in {processing_time:.2f}s")
            
            return {
                'success': True,
                'text': text_data['text'],
                'title': text_data['title'],
                'meta_description': text_data['meta_description'],
                'headings': text_data['headings'],
                'word_count': text_data['word_count'],
                'character_count': text_data['character_count'],
                'processing_time': round(processing_time, 2),
                'timestamp': datetime.utcnow().isoformat(),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error scraping text from {url}: {str(e)}")
            return self.handle_request_errors(url, e, start_time)
    
    def _extract_text_content(self, soup):
        """
        Extract and clean text content from HTML.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            dict: Extracted text data
        """
        # Remove unwanted elements
        self._remove_unwanted_elements(soup)
        
        # Extract main text
        text = soup.get_text()
        cleaned_text = self._clean_text(text)
        
        # Extract metadata
        title = self._extract_title(soup)
        meta_description = self._extract_meta_description(soup)
        headings = self._extract_headings(soup)
        
        return {
            'text': cleaned_text,
            'title': title,
            'meta_description': meta_description,
            'headings': headings,
            'word_count': len(cleaned_text.split()),
            'character_count': len(cleaned_text)
        }
    
    def _remove_unwanted_elements(self, soup):
        """
        Remove script, style, and navigation elements.
        
        Args:
            soup (BeautifulSoup): Parsed HTML to modify
        """
        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()
        
        # Remove navigation and structural elements
        for element in soup(["nav", "header", "footer", "aside"]):
            element.decompose()
        
        # Remove common unwanted classes and IDs
        unwanted_selectors = [
            '[class*="nav"]',
            '[class*="menu"]',
            '[class*="sidebar"]',
            '[class*="footer"]',
            '[class*="header"]',
            '[id*="nav"]',
            '[id*="menu"]',
            '[id*="sidebar"]',
            '[id*="footer"]',
            '[id*="header"]'
        ]
        
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()
    
    def _clean_text(self, text):
        """
        Clean and normalize text content.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace and normalize line breaks
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    def _extract_title(self, soup):
        """
        Extract page title.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            str: Page title
        """
        title = soup.find('title')
        if title:
            return title.get_text(strip=True)
        
        # Try alternative title sources
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            return og_title.get('content', '')
        
        # Try h1 as fallback
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        return ""
    
    def _extract_meta_description(self, soup):
        """
        Extract meta description.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            str: Meta description
        """
        # Try standard meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc:
            return og_desc.get('content', '')
        
        return ""
    
    def _extract_headings(self, soup):
        """
        Extract heading structure.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            dict: Headings organized by level
        """
        return {
            'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
            'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
            'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
            'h4': [h.get_text(strip=True) for h in soup.find_all('h4')],
            'h5': [h.get_text(strip=True) for h in soup.find_all('h5')],
            'h6': [h.get_text(strip=True) for h in soup.find_all('h6')]
        }
    
    def _create_empty_response(self, error_msg, start_time):
        """
        Create an empty response for text scraping errors.
        
        Args:
            error_msg (str): Error message
            start_time (float): Start time
            
        Returns:
            dict: Empty response with error
        """
        return {
            'success': False,
            'text': '',
            'title': '',
            'meta_description': '',
            'headings': {},
            'word_count': 0,
            'character_count': 0,
            'processing_time': round(time.time() - start_time, 2),
            'timestamp': datetime.utcnow().isoformat(),
            'error': error_msg
        }
    
    def get_summary(self, url, max_sentences=3):
        """
        Get a summary of the page content.
        
        Args:
            url (str): URL to scrape
            max_sentences (int): Maximum number of sentences in summary
            
        Returns:
            dict: Scraping results with summary
        """
        result = self.scrape(url)
        
        if result['success'] and result['text']:
            # Simple sentence extraction
            sentences = re.split(r'[.!?]+', result['text'])
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Take first few sentences as summary
            summary = '. '.join(sentences[:max_sentences])
            if summary and not summary.endswith('.'):
                summary += '.'
            
            result['summary'] = summary
            result['total_sentences'] = len(sentences)
        
        return result
    
    def get_main_content(self, url):
        """
        Extract only the main content, excluding headers, footers, etc.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            dict: Scraping results with main content focus
        """
        result = self.scrape(url)
        
        if result['success']:
            # Additional processing could be added here
            # to further filter main content
            pass
        
        return result