#!/usr/bin/env python3
"""
Check the status of article images in the LangRead database
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

async def check_image_status():
    """Check how many articles have images and how many still need them"""
    
    # Initialize database connection
    db = DatabaseService()
    await db.connect()
    print("Connected to database")
    
    try:
        # Count articles with and without images
        articles_without_images = await db.articles_collection.count_documents({
            'language': 'ko',
            '$or': [
                {'image_url': {'$exists': False}},
                {'image_url': None},
                {'image_url': ''}
            ]
        })
        
        total_articles = await db.articles_collection.count_documents({'language': 'ko'})
        articles_with_images = total_articles - articles_without_images
        
        print(f"\nImage Status for Korean Articles:")
        print(f"--------------------------------")
        print(f"Total Korean articles: {total_articles}")
        print(f"Articles with images: {articles_with_images} ({articles_with_images/total_articles*100:.1f}%)")
        print(f"Articles without images: {articles_without_images} ({articles_without_images/total_articles*100:.1f}%)")
        
        if articles_without_images > 0:
            print(f"\nYou still need to generate images for {articles_without_images} articles.")
            print(f"Run: python generate_article_images.py --language ko --limit {articles_without_images}")
        else:
            print("\nAll Korean articles now have images! 🎉")
        
    finally:
        # Disconnect from database
        await db.disconnect()
        print("\nDisconnected from database")

if __name__ == "__main__":
    asyncio.run(check_image_status())
