#!/usr/bin/env python3
"""
Add meaningful tags to articles in the LangRead database.

This script:
1. Finds articles with only metadata tags (like "rss", "ko")
2. Assigns appropriate content-based tags to each article
3. Updates the database with the new tags
"""

import asyncio
import os
import sys
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

openai.api_key = OPENAI_API_KEY

# Common Korean article tags (based on typical news categories)
CORE_TAGS = {
    "business": {
        "en": "business",
        "ko": "비즈니스"
    },
    "technology": {
        "en": "technology",
        "ko": "기술"
    },
    "politics": {
        "en": "politics",
        "ko": "정치"
    },
    "economy": {
        "en": "economy",
        "ko": "경제"
    },
    "culture": {
        "en": "culture",
        "ko": "문화"
    },
    "entertainment": {
        "en": "entertainment",
        "ko": "연예"
    },
    "science": {
        "en": "science",
        "ko": "과학"
    },
    "health": {
        "en": "health",
        "ko": "건강"
    },
    "society": {
        "en": "society",
        "ko": "사회"
    },
    "sports": {
        "en": "sports",
        "ko": "스포츠"
    },
    "education": {
        "en": "education",
        "ko": "교육"
    },
    "startup": {
        "en": "startup",
        "ko": "스타트업"
    },
    "innovation": {
        "en": "innovation",
        "ko": "혁신"
    },
    "environment": {
        "en": "environment",
        "ko": "환경"
    }
}

class ArticleTagger:
    """Add meaningful tags to articles"""
    
    def __init__(self):
        """Initialize the tagger"""
        self.db = None
        self.tags_cache = {}  # Cache of existing tags
    
    async def connect_to_db(self):
        """Connect to the database"""
        self.db = DatabaseService()
        await self.db.connect()
        print("Connected to database")
    
    async def disconnect_from_db(self):
        """Disconnect from the database"""
        if self.db:
            await self.db.disconnect()
            print("Disconnected from database")
    
    async def load_tags(self):
        """Load existing tags from the database into the cache"""
        tags = await self.db.tags_collection.find({}).to_list(length=None)
        for tag in tags:
            self.tags_cache[tag["name"]] = tag
        print(f"Loaded {len(self.tags_cache)} tags from database")
    
    async def create_tag_if_not_exists(self, name: str, language: str = "en", translations: Dict[str, str] = None) -> str:
        """Create a tag if it doesn't exist, and return its ID"""
        # Normalize name to lowercase
        name = name.lower()
        
        # Check if tag already exists in cache
        if name in self.tags_cache:
            return self.tags_cache[name]["_id"]
        
        # Check if tag exists in database
        tag = await self.db.tags_collection.find_one({"name": name})
        if tag:
            # Add to cache
            self.tags_cache[name] = tag
            return tag["_id"]
        
        # Create new tag
        print(f"Creating new tag: {name}")
        tag = await self.db.create_tag(
            name=name,
            language=language,
            translations=translations
        )
        
        # Add to cache
        self.tags_cache[name] = tag
        return tag["_id"]
    
    async def extract_tags_from_article(self, article: Dict[str, Any]) -> List[str]:
        """Extract meaningful tags from article content using GPT"""
        # Combine title and content for analysis
        title = article.get("title", "")
        content = ""
        
        # Extract text from content sections if available
        if "content" in article and isinstance(article["content"], list):
            for section in article["content"]:
                if isinstance(section, dict) and section.get("type") == "text":
                    content += section.get("content", "") + " "
        
        # Use sample content if available
        if not content and "content_sample" in article:
            content = article["content_sample"]
        
        # Prepare text for analysis
        analysis_text = title + "\n" + content[:1000]  # Limit content length
        
        # Use fixed tags for simplicity and speed
        if article.get("language") == "ko":
            # For Korean articles, try to detect topics from title keywords
            title_lower = title.lower()
            
            # Initial tag set (start with empty)
            detected_tags = set()
            
            # Business and economy keywords
            business_keywords = ["기업", "회사", "비즈니스", "경제", "투자", "시장", "주식", "금융"]
            if any(keyword in title_lower for keyword in business_keywords):
                detected_tags.add("business")
                detected_tags.add("economy")
            
            # Technology keywords
            tech_keywords = ["기술", "테크", "디지털", "인공지능", "ai", "ml", "블록체인", "소프트웨어"]
            if any(keyword in title_lower for keyword in tech_keywords):
                detected_tags.add("technology")
            
            # Startup keywords
            startup_keywords = ["스타트업", "창업", "벤처", "혁신", "유니콘"]
            if any(keyword in title_lower for keyword in startup_keywords):
                detected_tags.add("startup")
                detected_tags.add("innovation")
            
            # Add default tags if none detected
            if not detected_tags:
                detected_tags.add("business")  # Default tag for Korean articles
            
            return list(detected_tags)
        
        # Default tags for non-Korean articles
        return ["news"]
    
    async def update_article_tags(self, article: Dict[str, Any]) -> bool:
        """Update article with meaningful tags"""
        article_id = article["_id"]
        
        # Extract tags from article content
        tags = await self.extract_tags_from_article(article)
        
        # Skip if no tags extracted
        if not tags:
            print(f"No tags extracted for article: {article.get('title')}")
            return False
        
        # Create tags in database and get their IDs
        tag_ids = []
        for tag in tags:
            # Get translations from core tags or create empty dict
            translations = CORE_TAGS.get(tag, {})
            if translations:
                tag_id = await self.create_tag_if_not_exists(
                    name=tag,
                    language="en",
                    translations=translations
                )
            else:
                tag_id = await self.create_tag_if_not_exists(name=tag)
            
            tag_ids.append(tag_id)
        
        # Update article with new tag IDs
        result = await self.db.articles_collection.update_one(
            {"_id": article_id},
            {"$set": {
                "tag_ids": tag_ids,
                "topics": tags  # Also update topics with meaningful tags
            }}
        )
        
        return result.modified_count > 0
    
    async def process_articles(self, language: str = "ko", limit: int = 0):
        """Process articles and add meaningful tags"""
        # Find articles with metadata-only topics or no topics
        query = {
            "language": language,
            "$or": [
                {"topics": {"$in": ["", "rss", "ko", "feeds"]}},
                {"topics": {"$size": 0}},
                {"topics": {"$exists": False}}
            ]
        }
        
        cursor = self.db.articles_collection.find(query)
        if limit > 0:
            articles = await cursor.limit(limit).to_list(length=limit)
        else:
            articles = await cursor.to_list(length=None)
        
        total = len(articles)
        print(f"Found {total} articles that need meaningful tags")
        
        if total == 0:
            print("No articles to process")
            return
        
        # Process each article
        updated_count = 0
        for i, article in enumerate(articles):
            title = article.get("title", "Untitled")
            print(f"Processing article {i+1}/{total}: {title}")
            
            # Update article tags
            success = await self.update_article_tags(article)
            
            if success:
                updated_count += 1
            
            # Wait briefly between updates to not overload the database
            await asyncio.sleep(0.1)
        
        print(f"\nUpdated {updated_count}/{total} articles with meaningful tags")
    
    async def check_tag_display(self, limit: int = 5):
        """Check how tags are displayed for a sample of articles"""
        articles = await self.db.articles_collection.find({"language": "ko"}).limit(limit).to_list(length=limit)
        
        print(f"\nChecking tag display for {len(articles)} articles:")
        print("-" * 50)
        
        for idx, article in enumerate(articles):
            print(f"\nArticle {idx+1}: {article.get('title')}")
            print(f"  Topics: {article.get('topics', [])}")
            
            # Get tag details
            tag_ids = article.get("tag_ids", [])
            tag_details = []
            
            for tag_id in tag_ids:
                tag = await self.db.tags_collection.find_one({"_id": tag_id})
                if tag:
                    tag_details.append({
                        "name": tag.get("name"),
                        "translations": tag.get("translations", {})
                    })
            
            print(f"  Tag IDs: {tag_ids}")
            print(f"  Tag details: {tag_details}")

async def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description="Add meaningful tags to articles")
    parser.add_argument("--language", "-l", default="ko", help="Language code (e.g., 'ko', 'en')")
    parser.add_argument("--limit", "-n", type=int, default=0, help="Limit of articles to process (0 = all)")
    parser.add_argument("--check", action="store_true", help="Check tag display without updating")
    args = parser.parse_args()
    
    tagger = ArticleTagger()
    
    try:
        await tagger.connect_to_db()
        await tagger.load_tags()
        
        if args.check:
            await tagger.check_tag_display(limit=args.limit or 5)
        else:
            await tagger.process_articles(language=args.language, limit=args.limit)
            # Check results after processing
            await tagger.check_tag_display(limit=5)
    finally:
        await tagger.disconnect_from_db()

if __name__ == "__main__":
    asyncio.run(main())
