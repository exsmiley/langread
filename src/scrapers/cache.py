"""
Caching system for article content to avoid repeated fetching.
"""
import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("article_cache")

class ArticleCache:
    """
    Simple file-based cache for articles.
    Stores articles by query and language.
    """
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize the cache
        
        Args:
            cache_dir: Directory to store cache files (default: /tmp/langread_cache)
        """
        if cache_dir is None:
            # Default to project cache directory
            project_root = Path(__file__).parent.parent.parent
            cache_dir = os.path.join(project_root, "cache")
            
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Created cache directory: {self.cache_dir}")
            
        # Stats for the cache
        self.stats = {
            "hits": 0,
            "misses": 0,
            "items": 0
        }
        
        # Initialize or load cache metadata
        self.metadata_file = os.path.join(self.cache_dir, "metadata.json")
        self.metadata = self._load_metadata()
        
        logger.info(f"ArticleCache initialized with {len(self.metadata['queries'])} cached queries")
    
    def _load_metadata(self) -> Dict:
        """Load or initialize cache metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse metadata file. Creating new one.")
        
        # Initialize new metadata
        return {
            "queries": {},
            "last_cleanup": datetime.now().isoformat(),
            "total_articles": 0
        }
    
    def _save_metadata(self):
        """Save cache metadata to disk"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def _get_cache_key(self, query: str, language: str) -> str:
        """Generate a cache key from query and language"""
        # Normalize query: lowercase, remove extra spaces
        query = query.lower().strip()
        # Create simple filename-safe key
        key = f"{language}_{query.replace(' ', '_')}"
        return key
    
    def _get_cache_file(self, cache_key: str) -> str:
        """Get the cache file path for a given key"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, query: str, language: str) -> Optional[List[Dict]]:
        """
        Get cached articles for a query and language
        
        Args:
            query: Search query
            language: Language code (e.g., 'en', 'ko')
            
        Returns:
            List of articles if found in cache, None otherwise
        """
        cache_key = self._get_cache_key(query, language)
        cache_file = self._get_cache_file(cache_key)
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Check if cache is expired (default: 24 hours)
                cache_time = datetime.fromisoformat(data.get("timestamp", "2000-01-01T00:00:00"))
                current_time = datetime.now()
                
                if current_time - cache_time > timedelta(hours=24):
                    logger.info(f"Cache expired for query: {query}, language: {language}")
                    self.stats["misses"] += 1
                    return None
                    
                logger.info(f"Cache hit for query: {query}, language: {language}")
                self.stats["hits"] += 1
                return data.get("articles", [])
            except Exception as e:
                logger.warning(f"Error reading from cache: {str(e)}")
        
        logger.info(f"Cache miss for query: {query}, language: {language}")
        self.stats["misses"] += 1
        return None
    
    def _make_serializable(self, obj):
        """
        Convert objects to JSON-serializable dictionaries
        
        Args:
            obj: Object to make serializable (could be ArticleContent, ContentSection, etc.)
            
        Returns:
            JSON-serializable version of the object
        """
        if hasattr(obj, "dict") and callable(obj.dict):
            # Handle Pydantic models
            return self._make_serializable(obj.dict())
        elif isinstance(obj, datetime):
            # Handle datetime objects
            return obj.isoformat()
        elif hasattr(obj, "__dict__"):
            # Handle regular objects
            return {k: self._make_serializable(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, list):
            # Handle lists of objects
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            # Handle dictionaries
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (str, int, float, bool, type(None))):
            # Handle primitive types
            return obj
        else:
            # If we can't serialize it, convert to string
            return str(obj)
    
    def set(self, query: str, language: str, articles: List, logs: List[str] = None):
        """
        Cache articles for a query and language
        
        Args:
            query: Search query
            language: Language code
            articles: List of articles to cache (can be ArticleContent objects or dictionaries)
            logs: Optional list of processing logs
        """
        cache_key = self._get_cache_key(query, language)
        cache_file = self._get_cache_file(cache_key)
        
        # Convert articles to serializable dictionaries
        serializable_articles = self._make_serializable(articles)
        
        data = {
            "query": query,
            "language": language,
            "articles": serializable_articles,
            "timestamp": datetime.now().isoformat(),
            "logs": logs or []
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Update metadata
        self.metadata["queries"][cache_key] = {
            "query": query,
            "language": language,
            "timestamp": data["timestamp"],
            "article_count": len(articles)
        }
        
        self.metadata["total_articles"] = self.metadata.get("total_articles", 0) + len(articles)
        self._save_metadata()
        
        self.stats["items"] += 1
        logger.info(f"Cached {len(articles)} articles for query: {query}, language: {language}")
    
    def get_all_queries(self) -> List[Dict]:
        """
        Get metadata for all cached queries
        
        Returns:
            List of query metadata objects
        """
        return list(self.metadata["queries"].values())
    
    def clear(self):
        """Clear all cached data"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, filename))
        
        self.metadata = self._load_metadata()
        self._save_metadata()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            **self.stats,
            "total_queries": len(self.metadata["queries"]),
            "total_articles": self.metadata.get("total_articles", 0),
            "cache_size_bytes": sum(os.path.getsize(os.path.join(self.cache_dir, f)) 
                                   for f in os.listdir(self.cache_dir) if f.endswith('.json'))
        }
