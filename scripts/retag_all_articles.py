#!/usr/bin/env python3
"""
Script to re-tag all existing articles in the LangRead database.
This will process each article through the tag generator and 
assign appropriate tags based on the article content.
"""

from path_helper import setup_path
# Add project root to Python path
setup_path()

import os
import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Any
import json
import openai
from openai import OpenAI
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from loguru import logger


# Import local modules
from utils.tag_generator import TagGenerator

# Create a simplified local tag generator that doesn't need async
class SimpleTagGenerator:
    """A simplified tag generator that doesn't rely on async operations"""
    
    def __init__(self):
        """Initialize with predefined tags that are common in articles"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
            
        self.openai_client = OpenAI(api_key=self.api_key)
        
        # Common tags in Korean news articles
        self.ko_tags = {
            "news": {"en": "news", "ko": "뉴스"},
            "business": {"en": "business", "ko": "비즈니스"},
            "technology": {"en": "technology", "ko": "기술"},
            "politics": {"en": "politics", "ko": "정치"},
            "economy": {"en": "economy", "ko": "경제"},
            "culture": {"en": "culture", "ko": "문화"},
            "entertainment": {"en": "entertainment", "ko": "엔터테인먼트"},
            "sports": {"en": "sports", "ko": "스포츠"},
            "science": {"en": "science", "ko": "과학"},
            "health": {"en": "health", "ko": "건강"},
            "education": {"en": "education", "ko": "교육"},
            "society": {"en": "society", "ko": "사회"},
            "lifestyle": {"en": "lifestyle", "ko": "라이프스타일"},
            "travel": {"en": "travel", "ko": "여행"}
        }
    
    async def generate_tags(self, title, content, language="ko", max_tags=5):
        """Generate tags for the given article using a synchronous OpenAI call"""
        try:
            # Create a prompt for the LLM
            prompt = f"""
            Analyze this article and extract {max_tags} relevant tags that categorize its content.
            Tags should be simple nouns or concepts, not phrases or sentences.
            
            Article Title: {title}
            Article Sample: {content[:1000]}  # Using first 1000 chars
            
            Return your response as a JSON array of strings.
            Example: ["business", "technology", "startup", "finance"]
            """
            
            # Make a synchronous call to OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You extract concise, relevant tags from article content. Return only a JSON array of tags."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Handle various response formats
            tags = []
            if isinstance(result, list):
                tags = result
            elif "tags" in result:
                tags = result["tags"]
            else:
                # Try to get the first list value
                tags = list(result.values())[0] if result and isinstance(list(result.values())[0], list) else []
                
            # Clean and normalize tags
            tags = [tag.lower().strip() for tag in tags]
            tags = [tag for tag in tags if tag]  # Remove empty tags
            
            # Create tag objects
            tag_objects = []
            for tag in tags[:max_tags]:  # Limit to max_tags
                # Check if tag is in predefined list
                if tag in self.ko_tags:
                    translations = self.ko_tags[tag]
                else:
                    # Simple translation
                    translations = {"en": tag, language: tag}
                
                tag_objects.append({
                    "name": tag,
                    "original_language": "en",
                    "translations": translations
                })
                
            return tag_objects
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            # Return a default tag as fallback
            return [{
                "name": "news",
                "original_language": "en",
                "translations": {"en": "news", "ko": "뉴스"}
            }]

# Create an instance of our simplified tag generator
tag_generator = SimpleTagGenerator()
from models.database import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logger.add("retag_articles.log", rotation="10 MB")

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "langread")

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def connect_db() -> DatabaseService:
    """Connect to the database and return a DatabaseService instance."""
    connection_string = MONGO_URI + DB_NAME if not MONGO_URI.endswith('/') else MONGO_URI + DB_NAME
    db_service = DatabaseService(connection_string=connection_string)
    await db_service.connect()
    return db_service

async def get_all_articles(db: DatabaseService) -> List[Dict[str, Any]]:
    """Get all articles from the database."""
    # Get articles without tags or with empty tag lists
    articles = await db.articles_collection.find({
        "$or": [
            {"tag_ids": {"$exists": False}},
            {"tag_ids": []},
            {"tag_ids": None}
        ]
    }).to_list(length=1000)
    
    logger.info(f"Found {len(articles)} articles without tags to process")
    return articles

async def process_article(db: DatabaseService, article: Dict[str, Any]) -> None:
    """Process a single article to generate and assign tags."""
    article_id = str(article["_id"])
    title = article.get("title", "")
    content = article.get("content", "")
    language = article.get("language", "en")
    
    # Check if this is a properly formatted article with content
    if not content or not title:
        # Try to find content in the 'text' field, which is also used in some articles
        content = article.get("text", "")
        if not content:
            logger.warning(f"Skipping article with no content: {article_id}")
            return
            
    # Use a sample of the content for tag generation (maximum 2000 chars)
    content_sample = content[:2000] if len(content) > 2000 else content
        
    logger.info(f"Processing article: {title[:50]}... (ID: {article_id}, Language: {language})")
    
    try:
        # Generate tags for the article
        generated_tags = await tag_generator.generate_tags(
            title=title,
            content=content_sample,
            language=language,
            max_tags=5
        )
        
        # Save tags and associate with article
        tag_ids = []
        for tag_data in generated_tags:
            # Ensure the tag has a name
            if not tag_data.get("name"):
                continue
                
            # Check if tag already exists
            existing_tag = await db.tags_collection.find_one({"name": tag_data["name"]})
            
            if existing_tag:
                tag_id = str(existing_tag["_id"])
                logger.debug(f"Using existing tag: {tag_data['name']} (ID: {tag_id})")
                
                # Update translations if needed
                if language != "en" and language not in existing_tag.get("translations", {}):
                    await db.tags_collection.update_one(
                        {"_id": existing_tag["_id"]},
                        {"$set": {f"translations.{language}": tag_data["translations"].get(language, tag_data["name"])}}
                    )
            else:
                # Create new tag
                tag_obj = {
                    "name": tag_data["name"],
                    "language_specific": False,
                    "translations": tag_data["translations"],
                    "original_language": tag_data.get("original_language", "en"),
                    "article_count": 0,  # Will be incremented when associated
                    "active": True,
                    "auto_approved": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await db.tags_collection.insert_one(tag_obj)
                tag_id = str(result.inserted_id)
                logger.debug(f"Created new tag: {tag_data['name']} (ID: {tag_id})")
            
            tag_ids.append(tag_id)
        
        # Update the article with the tag IDs
        if tag_ids:
            await db.articles_collection.update_one(
                {"_id": article["_id"]},
                {"$set": {"tag_ids": tag_ids}}
            )
            
            # Update article counts for each tag
            for tag_id in tag_ids:
                await db.tags_collection.update_one(
                    {"_id": ObjectId(tag_id)},
                    {"$inc": {"article_count": 1}}
                )
            
            logger.success(f"Assigned {len(tag_ids)} tags to article: {article_id}")
        else:
            logger.warning(f"No tags generated for article: {article_id}")
    except Exception as e:
        logger.error(f"Error processing article {article_id}: {str(e)}")

async def retag_all_articles() -> None:
    """Main function to retag all articles."""
    logger.info("Starting article retagging process")
    
    db = await connect_db()
    articles = await get_all_articles(db)
    
    logger.info(f"Processing {len(articles)} articles")
    
    # Process articles in batches to avoid overloading the system
    batch_size = 10
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        tasks = [process_article(db, article) for article in batch]
        await asyncio.gather(*tasks)
        
        logger.info(f"Processed batch {i//batch_size + 1}/{(len(articles) + batch_size - 1)//batch_size}")
    
    logger.success(f"Retagging completed for {len(articles)} articles")
    
    # Print summary of tags
    tags = await db.tags_collection.find({"article_count": {"$gt": 0}}).sort("article_count", -1).to_list(length=20)
    logger.info(f"Top {len(tags)} tags after retagging:")
    for tag in tags:
        logger.info(f"- {tag['name']}: {tag['article_count']} articles")

if __name__ == "__main__":
    # Run the retagging process
    asyncio.run(retag_all_articles())
