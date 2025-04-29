#!/usr/bin/env python3
"""
Download and save DALL-E generated images locally

This script:
1. Finds articles with DALL-E image URLs (which expire after ~1 hour)
2. Downloads the images to a local directory
3. Updates the database with local file paths
"""

from path_helper import setup_path
# Add project root to Python path
setup_path()

import asyncio
import os
import sys
import re
import hashlib
import urllib.request
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
import httpx
from loguru import logger


from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logger.add("save_dalle_images.log", rotation="10 MB")

# Set up the image storage directory
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "src", "frontend", "public", "article_images")
os.makedirs(IMAGES_DIR, exist_ok=True)

class ImageSaver:
    """Download and save DALL-E generated images locally"""
    
    def __init__(self):
        """Initialize the image saver."""
        self.db = None
        self.stats = {
            "processed": 0,
            "saved": 0,
            "errors": 0
        }
    
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
    
    def create_safe_filename(self, article_id: str, image_url: str) -> str:
        """Create a safe, unique filename for an image."""
        # Create a hash from the URL for uniqueness
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:12]
        
        # Clean the article_id for use in a filename
        safe_id = re.sub(r'[^\w\-]', '_', str(article_id))
        
        # Return a filename with format: article_[id]_[hash].png
        return f"article_{safe_id}_{url_hash}.png"
    
    async def save_dalle_image(self, article_id: str, image_url: str) -> Optional[str]:
        """Download and save a DALL-E image to local storage."""
        try:
            # Create a filename based on article ID and URL
            filename = self.create_safe_filename(article_id, image_url)
            filepath = os.path.join(IMAGES_DIR, filename)
            
            # Create a relative path for the database
            relative_path = f"/article_images/{filename}"
            
            # Check if file already exists
            if os.path.exists(filepath):
                logger.info(f"Image already exists at {filepath}")
                return relative_path
            
            # Download the image
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=10.0)
                
                if response.status_code == 200:
                    # Save the image locally
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    
                    logger.info(f"Saved image to {filepath}")
                    return relative_path
                else:
                    logger.error(f"Failed to download image: HTTP {response.status_code}")
                    return None
                
        except Exception as e:
            logger.error(f"Error saving DALL-E image: {e}")
            return None
    
    async def update_article_image(self, article_id: str, image_path: str) -> bool:
        """Update article with a local image path."""
        try:
            # Update the article in the database
            result = await self.db.articles_collection.update_one(
                {"_id": article_id},
                {"$set": {
                    "image_url": image_path,
                    "image_url_permanent": True,
                    "image_updated_at": datetime.now()
                }}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating article {article_id}: {e}")
            return False
    
    async def process_articles(self, language: str = "ko", limit: int = 0):
        """Process articles with DALL-E image URLs."""
        try:
            # Query for articles with DALL-E URLs
            query = {
                "language": language,
                "image_url": {"$regex": "^https://oaidalleapiprodscus"}
            }
            
            # Find articles with DALL-E URLs
            cursor = self.db.articles_collection.find(query)
            if limit > 0:
                articles = await cursor.limit(limit).to_list(length=limit)
            else:
                articles = await cursor.limit(100).to_list(length=100)
            
            total = len(articles)
            logger.info(f"Found {total} articles with DALL-E image URLs")
            
            if total == 0:
                logger.info("No articles to process")
                return
            
            # Process each article
            for i, article in enumerate(articles):
                article_id = article["_id"]
                image_url = article.get("image_url", "")
                title = article.get("title", "Untitled")
                
                logger.info(f"Processing article {i+1}/{total}: {title}")
                
                try:
                    # Save the DALL-E image
                    local_path = await self.save_dalle_image(article_id, image_url)
                    
                    if local_path:
                        # Update the article with the local path
                        success = await self.update_article_image(article_id, local_path)
                        
                        if success:
                            logger.info(f"Updated article {article_id} with local path: {local_path}")
                            self.stats["saved"] += 1
                        else:
                            logger.error(f"Failed to update article {article_id}")
                            self.stats["errors"] += 1
                    else:
                        logger.error(f"Failed to save image for article {article_id}")
                        self.stats["errors"] += 1
                    
                    self.stats["processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing article {article_id}: {e}")
                    self.stats["errors"] += 1
                
                # Wait a short time between requests
                await asyncio.sleep(0.5)
            
            # Print summary
            logger.info(f"Image saving summary:")
            logger.info(f"Total processed: {self.stats['processed']}")
            logger.info(f"Images saved: {self.stats['saved']}")
            logger.info(f"Errors: {self.stats['errors']}")
            
        except Exception as e:
            logger.error(f"Error processing articles: {e}")
    
    async def fix_article_image_paths(self):
        """Fix image paths to include proper public URL base."""
        try:
            # Find articles with relative paths that need the base URL
            fixed_count = 0
            
            # Query for relative path images (starting with /)
            query = {
                "image_url": {"$regex": "^/article_images/"}
            }
            
            articles = await self.db.articles_collection.find(query).to_list(length=1000)
            
            logger.info(f"Found {len(articles)} articles with relative image paths")
            
            if len(articles) == 0:
                logger.info("No article paths to fix")
                return
            
            for article in articles:
                article_id = article["_id"]
                relative_path = article.get("image_url", "")
                
                # Create the full URL path
                full_path = relative_path
                
                # Update the article
                result = await self.db.articles_collection.update_one(
                    {"_id": article_id},
                    {"$set": {"image_url": full_path}}
                )
                
                if result.modified_count > 0:
                    fixed_count += 1
            
            logger.info(f"Fixed {fixed_count} article image paths")
            
        except Exception as e:
            logger.error(f"Error fixing article image paths: {e}")

async def main():
    """Main function to run the image saver."""
    import argparse
    parser = argparse.ArgumentParser(description="Save DALL-E images locally")
    parser.add_argument("--language", "-l", default="ko", help="Language code (e.g., 'ko', 'en')")
    parser.add_argument("--limit", "-n", type=int, default=0, help="Limit of articles to process (0 = all)")
    parser.add_argument("--fix-paths", action="store_true", help="Fix relative image paths")
    args = parser.parse_args()
    
    saver = ImageSaver()
    
    try:
        await saver.connect_to_db()
        
        if args.fix_paths:
            await saver.fix_article_image_paths()
        else:
            await saver.process_articles(language=args.language, limit=args.limit)
        
        logger.info("Image saving complete")
        
    except Exception as e:
        logger.error(f"Error in image saving: {e}")
    finally:
        await saver.disconnect_from_db()

if __name__ == "__main__":
    asyncio.run(main())
