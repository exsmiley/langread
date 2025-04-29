#!/usr/bin/env python3
"""
Download and save article images locally

This script:
1. Finds articles with temporary image URLs 
2. Downloads the images before they expire
3. Saves them to a local directory in the frontend public folder
4. Updates the database with permanent local paths
"""

import asyncio
import os
import sys
import re
import hashlib
import time
import urllib.request
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logger.add("download_images.log", rotation="10 MB")

# Set up the image storage directory in the frontend public folder
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "src", "frontend", "public", "article_images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Base URL for serving images
IMAGE_BASE_URL = "/article_images"

class ImageDownloader:
    """Download and save article images locally"""
    
    def __init__(self):
        """Initialize the image downloader."""
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
    
    async def download_image(self, article_id: str, image_url: str) -> Optional[str]:
        """Download an image and save it locally."""
        try:
            # Create a filename based on article ID and URL
            filename = self.create_safe_filename(article_id, image_url)
            filepath = os.path.join(IMAGES_DIR, filename)
            
            # Create a relative path for the database
            relative_path = f"{IMAGE_BASE_URL}/{filename}"
            
            # Check if file already exists
            if os.path.exists(filepath):
                logger.info(f"Image already exists at {filepath}")
                return relative_path
            
            # Download the image
            try:
                # Using requests for better timeout handling
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()  # Raise exception for bad status codes
                
                # Save the image to local file
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                logger.info(f"Saved image to {filepath}")
                return relative_path
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error downloading image: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return None
    
    async def update_article_image(self, article_id: str, image_path: str) -> bool:
        """Update article with a local image path."""
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
    
    async def process_all_articles(self, language: str = "ko", limit: int = 0):
        """Process all articles with external image URLs."""
        try:
            # Build query for articles with external URLs
            query = {
                "language": language,
                "image_url": {"$regex": "^https://"}
            }
            
            # Find articles with external image URLs
            cursor = self.db.articles_collection.find(query)
            if limit > 0:
                articles = await cursor.limit(limit).to_list(length=limit)
            else:
                articles = await cursor.to_list(length=None)
            
            total = len(articles)
            logger.info(f"Found {total} articles with external image URLs")
            
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
                    # Download and save the image
                    local_path = await self.download_image(article_id, image_url)
                    
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
                        logger.error(f"Failed to download image for article {article_id}")
                        self.stats["errors"] += 1
                    
                    self.stats["processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing article {article_id}: {e}")
                    self.stats["errors"] += 1
                
                # Wait a short time between downloads
                time.sleep(0.5)
            
            # Print summary
            logger.info(f"Image download summary:")
            logger.info(f"Total processed: {self.stats['processed']}")
            logger.info(f"Images saved: {self.stats['saved']}")
            logger.info(f"Errors: {self.stats['errors']}")
            
        except Exception as e:
            logger.error(f"Error processing articles: {e}")
    
    async def count_article_image_status(self, language: str = "ko"):
        """Count articles with different image status."""
        try:
            # Count total articles
            total = await self.db.articles_collection.count_documents({"language": language})
            
            # Count articles with permanent local images
            with_local = await self.db.articles_collection.count_documents({
                "language": language,
                "image_url": {"$regex": "^/article_images/"}
            })
            
            # Count articles with external URLs
            with_external = await self.db.articles_collection.count_documents({
                "language": language,
                "image_url": {"$regex": "^https://"}
            })
            
            # Count articles without images
            without_images = await self.db.articles_collection.count_documents({
                "language": language,
                "$or": [
                    {"image_url": {"$exists": False}},
                    {"image_url": None},
                    {"image_url": ""}
                ]
            })
            
            # Print summary
            print(f"\nArticle Image Status for {language} articles:")
            print(f"-------------------------------------------")
            print(f"Total articles: {total}")
            print(f"Articles with local images: {with_local} ({with_local/total*100:.1f}%)")
            print(f"Articles with external image URLs: {with_external} ({with_external/total*100:.1f}%)")
            print(f"Articles without images: {without_images} ({without_images/total*100:.1f}%)")
            
        except Exception as e:
            logger.error(f"Error counting article image status: {e}")

async def main():
    """Main function to run the image downloader."""
    import argparse
    parser = argparse.ArgumentParser(description="Download article images locally")
    parser.add_argument("--language", "-l", default="ko", help="Language code (e.g., 'ko', 'en')")
    parser.add_argument("--limit", "-n", type=int, default=0, help="Limit of articles to process (0 = all)")
    parser.add_argument("--status", action="store_true", help="Show article image status")
    args = parser.parse_args()
    
    downloader = ImageDownloader()
    
    try:
        await downloader.connect_to_db()
        
        if args.status:
            await downloader.count_article_image_status(language=args.language)
        else:
            await downloader.process_all_articles(language=args.language, limit=args.limit)
        
        logger.info("Image processing complete")
        
    except Exception as e:
        logger.error(f"Error in image processing: {e}")
    finally:
        await downloader.disconnect_from_db()

if __name__ == "__main__":
    asyncio.run(main())
