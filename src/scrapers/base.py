"""
Base scraper class that provides common functionality for all scrapers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, source_name: str, base_url: str):
        """
        Initialize the scraper
        
        Args:
            source_name: Name of the news source
            base_url: Base URL of the news source
        """
        self.source_name = source_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_soup(self, url: str) -> BeautifulSoup:
        """
        Get a BeautifulSoup object from a URL
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise
    
    @abstractmethod
    async def get_articles_list(self, date: Optional[datetime] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get a list of articles from the source
        
        Args:
            date: Optional date to fetch articles for (defaults to today)
            limit: Maximum number of articles to fetch
            
        Returns:
            List of article metadata dictionaries
        """
        pass
    
    @abstractmethod
    async def get_article_content(self, article_url: str) -> Dict[str, Any]:
        """
        Get the full content of an article
        
        Args:
            article_url: URL of the article to fetch
            
        Returns:
            Dictionary with article content
        """
        pass
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing line breaks
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Replace multiple spaces with a single space
        text = ' '.join(text.split())
        
        return text.strip()
