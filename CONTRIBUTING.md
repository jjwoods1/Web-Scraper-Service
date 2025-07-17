# Contributing to Unified Web Scraper API

Thank you for your interest in contributing to the Unified Web Scraper API! This document provides guidelines and instructions for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information** including:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and logs

### Submitting Changes

1. **Fork the repository** and create a new branch
2. **Make your changes** following the coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if necessary
5. **Submit a pull request** with a clear description

## 🏗️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for testing containerized deployment)

### Setting up the Development Environment

1. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/unified-scraper-api.git
   cd unified-scraper-api
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If you create this file
   ```

4. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your development settings
   ```

## 📝 Coding Standards

### Code Style

- Follow **PEP 8** Python style guidelines
- Use **type hints** where appropriate
- Write **clear, descriptive variable and function names**
- Add **docstrings** to all functions and classes
- Keep **line length under 127 characters**

### Code Organization

- Keep **related functionality together** in modules
- Use **meaningful file and directory names**
- Follow the **existing project structure**
- Separate **configuration from business logic**

### Example Code Style

```python
def scrape_urls(self, url: str) -> Dict[str, Any]:
    """
    Extract all hyperlinks from a given URL.
    
    Args:
        url (str): The URL to scrape
        
    Returns:
        Dict[str, Any]: Dictionary containing scraped URLs and metadata
        
    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    start_time = time.time()
    
    try:
        response = self.get_page_response(url)
        # ... implementation
    except Exception as e:
        logger.error(f"Error scraping URLs from {url}: {str(e)}")
        raise
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_scrapers.py

# Run tests with verbose output
python -m pytest -v
```

### Writing Tests

- Write tests for **all new functionality**
- Use **descriptive test names**
- Include **both positive and negative test cases**
- Test **error conditions and edge cases**
- Use **fixtures** for common test data

### Test Structure

```python
import pytest
from unittest.mock import patch, MagicMock
from scrapers.url_scraper import URLScraper
from config import Config

class TestURLScraper:
    @pytest.fixture
    def scraper(self):
        return URLScraper(Config)
    
    def test_scrape_valid_url(self, scraper):
        """Test scraping a valid URL returns expected data structure."""
        # Test implementation
        pass
    
    def test_scrape_invalid_url(self, scraper):
        """Test scraping an invalid URL raises appropriate exception."""
        # Test implementation
        pass
```

## 🔄 Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
2. **Update documentation** if needed
3. **Add/update type hints**
4. **Follow the coding standards**
5. **Write descriptive commit messages**

### Pull Request Guidelines

1. **Use a clear, descriptive title**
2. **Provide a detailed description** of changes
3. **Reference related issues** using keywords (e.g., "Fixes #123")
4. **Include screenshots** for UI changes
5. **Ensure CI/CD pipeline passes**

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows the project's coding standards
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
```

## 📊 Performance Considerations

- **Optimize for readability first**, then performance
- **Use appropriate data structures** for the task
- **Avoid unnecessary network requests**
- **Implement proper caching** where beneficial
- **Consider memory usage** for large datasets

## 🔒 Security Guidelines

- **Never commit sensitive data** (API keys, passwords, etc.)
- **Validate all input data** thoroughly
- **Use secure coding practices**
- **Follow OWASP guidelines** for web applications
- **Report security vulnerabilities** privately

## 📚 Documentation

### Documentation Requirements

- **Update README.md** for new features
- **Add inline comments** for complex logic
- **Update API documentation** for endpoint changes
- **Include example usage** in docstrings
- **Update configuration documentation**

### Documentation Style

```python
class URLScraper:
    """
    A scraper for extracting URLs from web pages.
    
    This class provides functionality to scrape and extract all hyperlinks
    from a given webpage, with support for various link types and metadata
    extraction.
    
    Attributes:
        config: Configuration object containing scraper settings
        session: Requests session for HTTP connections
        
    Example:
        >>> scraper = URLScraper(config)
        >>> result = scraper.scrape('https://example.com')
        >>> print(result['count'])
        15
    """
```

## 🎯 Feature Requests

### Before Submitting a Feature Request

1. **Check if it already exists** in issues
2. **Consider the scope** and impact
3. **Think about implementation** complexity
4. **Ensure it fits the project goals**

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature.

## Use Case
Explain why this feature would be valuable.

## Proposed Implementation
Brief outline of how it could be implemented.

## Alternatives Considered
Other approaches that were considered.

## Additional Context
Any other relevant information.
```

## 🚀 Release Process

1. **Version bump** following semantic versioning
2. **Update CHANGELOG.md** with new features and fixes
3. **Create a release branch** for final testing
4. **Merge to main** and create a tagged release
5. **Deploy to production** following the deployment guide

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the README and inline documentation first

Thank you for contributing to the Unified Web Scraper API! 🎉