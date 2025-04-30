#!/usr/bin/env python3
"""
Update article images to use permanent local images

This script:
1. Uses a curated set of high-quality topic-specific images 
2. Assigns appropriate images to articles based on tags and content
3. Updates the database with permanent local paths
"""

from path_helper import setup_path
# Add project root to Python path
setup_path()

import asyncio
import os
import sys
import re
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
import json


from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logger.add("update_images.log", rotation="10 MB")

# A curated list of topic-based images for Korean articles
IMAGE_DIRECTORY = "/images"

# High-quality topic-based stock images - these are already in the public directory
TOPIC_IMAGES = {
    # Technology category
    "technology": [
        "/images/topics/technology_01.jpg",
        "/images/topics/technology_02.jpg",
        "/images/topics/technology_03.jpg"
    ],
    "ai": [
        "/images/topics/ai_01.jpg",
        "/images/topics/ai_02.jpg",
        "/images/topics/ai_03.jpg"
    ],
    "blockchain": [
        "/images/topics/blockchain_01.jpg",
        "/images/topics/blockchain_02.jpg"
    ],
    
    # Business category
    "business": [
        "/images/topics/business_01.jpg",
        "/images/topics/business_02.jpg",
        "/images/topics/business_03.jpg",
        "/images/topics/business_04.jpg"
    ],
    "startup": [
        "/images/topics/startup_01.jpg",
        "/images/topics/startup_02.jpg",
        "/images/topics/startup_03.jpg"
    ],
    "finance": [
        "/images/topics/finance_01.jpg",
        "/images/topics/finance_02.jpg",
        "/images/topics/finance_03.jpg"
    ],
    
    # Science & Tech
    "science": [
        "/images/topics/science_01.jpg",
        "/images/topics/science_02.jpg"
    ],
    "innovation": [
        "/images/topics/innovation_01.jpg",
        "/images/topics/innovation_02.jpg"
    ],
    
    # Korean culture & society
    "korean_culture": [
        "/images/topics/korean_culture_01.jpg",
        "/images/topics/korean_culture_02.jpg",
        "/images/topics/korean_culture_03.jpg",
        "/images/topics/korean_culture_04.jpg"
    ],
    "society": [
        "/images/topics/society_01.jpg",
        "/images/topics/society_02.jpg",
        "/images/topics/society_03.jpg"
    ],
    
    # Default categories for articles that don't match specific topics
    "default_ko": [
        "/images/defaults/seoul_01.jpg",
        "/images/defaults/seoul_02.jpg",
        "/images/defaults/korean_landscape_01.jpg",
        "/images/defaults/korean_cityscape_01.jpg",
        "/images/defaults/korean_abstract_01.jpg",
        "/images/defaults/korean_tech_01.jpg",
        "/images/defaults/korean_business_01.jpg"
    ]
}

# Tag mapping to image categories
TAG_TO_CATEGORY = {
    # Technology
    "technology": "technology",
    "tech": "technology",
    "ai": "ai",
    "artificial intelligence": "ai",
    "머신러닝": "ai",
    "인공지능": "ai",
    "blockchain": "blockchain",
    "블록체인": "blockchain",
    "crypto": "blockchain",
    "innovation": "innovation",
    "혁신": "innovation",
    
    # Business
    "business": "business",
    "비즈니스": "business",
    "startup": "startup",
    "스타트업": "startup",
    "entrepreneur": "startup",
    "finance": "finance",
    "financial": "finance",
    "investment": "finance",
    "investing": "finance",
    "economy": "finance",
    "금융": "finance",
    "경제": "finance",
    
    # Science
    "science": "science",
    "scientific": "science",
    "research": "science",
    "과학": "science",
    "연구": "science",
    
    # Korean culture & society
    "korean": "korean_culture",
    "korea": "korean_culture",
    "seoul": "korean_culture",
    "한국": "korean_culture",
    "서울": "korean_culture",
    "society": "society",
    "social": "society",
    "culture": "korean_culture",
    "cultural": "korean_culture",
    "사회": "society",
    "문화": "korean_culture"
}

class ArticleImageUpdater:
    """Update article images with permanent local images"""
    
    def __init__(self):
        """Initialize the image updater."""
        self.db = None
        self.stats = {
            "processed": 0,
            "updated": 0,
            "errors": 0
        }
        
        # Create the image directory structure if it doesn't exist
        self.create_image_directories()
    
    def create_image_directories(self):
        """Create the necessary image directories in the frontend public folder."""
        try:
            frontend_dir = os.path.join(os.path.dirname(__file__), "src", "frontend", "public")
            
            # Create main image directories
            image_dir = os.path.join(frontend_dir, "images")
            os.makedirs(image_dir, exist_ok=True)
            
            # Create topic subdirectories
            topics_dir = os.path.join(image_dir, "topics")
            os.makedirs(topics_dir, exist_ok=True)
            
            # Create defaults subdirectory
            defaults_dir = os.path.join(image_dir, "defaults")
            os.makedirs(defaults_dir, exist_ok=True)
            
            logger.info(f"Created image directories at {image_dir}")
            
            # Write a placeholder file explaining the directory structure
            readme_path = os.path.join(image_dir, "README.md")
            with open(readme_path, "w") as f:
                f.write("# Article Images\n\n")
                f.write("This directory contains images for articles in Lingogi.\n\n")
                f.write("## Structure\n\n")
                f.write("- `/topics/` - Topic-specific images (technology, business, etc.)\n")
                f.write("- `/defaults/` - Default images for articles without specific topics\n")
        
        except Exception as e:
            logger.error(f"Error creating image directories: {e}")
    
    async def connect_to_db(self):
        """Connect to the database."""
        self.db = DatabaseService()
        await self.db.connect()
        logger.info("Connected to database")
    
    async def disconnect_from_db(self):
        """Disconnect from the database."""
        if self.db:
            await self.db.disconnect()
            logger.info("Disconnected from database")
    
    def select_image_for_article(self, article: Dict[str, Any]) -> str:
        """Select an appropriate image for an article based on its tags and content."""
        # Get article tags
        tags = []
        
        # Check for tag_ids and fetch the corresponding tags
        if "tag_ids" in article and isinstance(article["tag_ids"], list):
            tags.extend(article["tag_ids"])
        
        # Check for topics directly on the article
        if "topics" in article and isinstance(article["topics"], list):
            tags.extend(article["topics"])
        
        # Map tags to categories
        categories = set()
        for tag in tags:
            tag_lower = tag.lower() if isinstance(tag, str) else ""
            for key, category in TAG_TO_CATEGORY.items():
                if key in tag_lower:
                    categories.add(category)
                    break
        
        # If we found matching categories, select a random image from one of them
        if categories:
            # Choose a random category from the matched ones
            category = random.choice(list(categories))
            
            # Get the images for this category
            images = TOPIC_IMAGES.get(category, [])
            
            # If no images for this category, fallback to default
            if not images:
                images = TOPIC_IMAGES["default_ko"]
        else:
            # Use default images
            images = TOPIC_IMAGES["default_ko"]
        
        # Select a random image from the category
        image = random.choice(images)
        return image
    
    async def update_article_image(self, article_id: str, image_path: str) -> bool:
        """Update article with a permanent local image path."""
        try:
            # Update the article in the database
            result = await self.db.articles_collection.update_one(
                {"_id": article_id},
                {"$set": {
                    "image_url": image_path,
                    "image_permanent": True,
                    "image_updated_at": datetime.now()
                }}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating article {article_id}: {e}")
            return False
    
    async def process_articles(self, language: str = "ko", limit: int = 0):
        """Process articles and update them with permanent local images."""
        try:
            # Find all articles for the specified language
            query = {"language": language}
            
            cursor = self.db.articles_collection.find(query)
            if limit > 0:
                articles = await cursor.limit(limit).to_list(length=limit)
            else:
                articles = await cursor.to_list(length=None)
            
            total = len(articles)
            logger.info(f"Found {total} articles to update with permanent images")
            
            # Check if we have the image directories populated
            if not os.path.exists(os.path.join(os.path.dirname(__file__), "src", "frontend", "public", "images", "defaults")):
                logger.warning("Image directories not populated. Creating empty structure.")
                self.create_image_directories()
                
                # Generate default placeholder image configuration
                placeholders = {
                    "default_ko": ["/images/defaults/placeholder_ko.jpg"],
                    "default_en": ["/images/defaults/placeholder_en.jpg"]
                }
                
                # Write placeholder configuration
                placeholder_path = os.path.join(os.path.dirname(__file__), "src", "frontend", "public", "images", "placeholders.json")
                with open(placeholder_path, "w") as f:
                    json.dump(placeholders, f, indent=2)
                
                # Use more generic default paths
                logger.info("Using generic article cover images since specific topic images are not available")
                language_defaults = {
                    "ko": "/images/korean_article_cover.jpg",
                    "en": "/images/english_article_cover.jpg"
                }
                default_image = language_defaults.get(language, "/images/article_cover.jpg")
            
            # Process each article
            for i, article in enumerate(articles):
                article_id = article["_id"]
                title = article.get("title", "Untitled")
                
                logger.info(f"Processing article {i+1}/{total}: {title}")
                
                # Select an appropriate image path for this article
                # If the directories are not properly populated, use the default image
                if not os.path.exists(os.path.join(os.path.dirname(__file__), "src", "frontend", "public", "images", "defaults")):
                    image_path = default_image
                else:
                    image_path = self.select_image_for_article(article)
                
                # Update the article with the image path
                success = await self.update_article_image(article_id, image_path)
                
                if success:
                    logger.info(f"Updated article {article_id} with image: {image_path}")
                    self.stats["updated"] += 1
                else:
                    logger.error(f"Failed to update article {article_id}")
                    self.stats["errors"] += 1
                
                self.stats["processed"] += 1
                
                # Wait a short time between updates to avoid database strain
                await asyncio.sleep(0.05)
            
            # Print summary
            logger.info(f"Image update summary:")
            logger.info(f"Total processed: {self.stats['processed']}")
            logger.info(f"Articles updated: {self.stats['updated']}")
            logger.info(f"Errors: {self.stats['errors']}")
            
        except Exception as e:
            logger.error(f"Error processing articles: {e}")
    
    async def write_dummy_image_metadata(self):
        """Create dummy image metadata for reference."""
        try:
            # Create a metadata file for the image directory
            metadata_path = os.path.join(os.path.dirname(__file__), "src", "frontend", "public", "images", "image_metadata.json")
            
            # Create a simplified version of the topic images
            metadata = {
                "categories": {k: len(v) for k, v in TOPIC_IMAGES.items()},
                "tag_mapping": TAG_TO_CATEGORY
            }
            
            # Write the metadata
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
                
            logger.info(f"Created image metadata at {metadata_path}")
        except Exception as e:
            logger.error(f"Error writing image metadata: {e}")

async def main():
    """Main function to run the image updater."""
    import argparse
    parser = argparse.ArgumentParser(description="Update article images with permanent local images")
    parser.add_argument("--language", "-l", default="ko", help="Language code (e.g., 'ko', 'en')")
    parser.add_argument("--limit", "-n", type=int, default=0, help="Limit of articles to process (0 = all)")
    args = parser.parse_args()
    
    updater = ArticleImageUpdater()
    
    try:
        await updater.connect_to_db()
        
        # Create metadata for image directories
        await updater.write_dummy_image_metadata()
        
        # Process and update articles
        await updater.process_articles(language=args.language, limit=args.limit)
        
        logger.info("Image update complete")
        
    except Exception as e:
        logger.error(f"Error in image update: {e}")
    finally:
        await updater.disconnect_from_db()

if __name__ == "__main__":
    asyncio.run(main())
