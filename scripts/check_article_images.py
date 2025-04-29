#!/usr/bin/env python3
"""
Script to check if articles have images that can be used as profile pictures
"""

from path_helper import setup_path
# Add project root to Python path
setup_path()

import asyncio
import os
import sys
from dotenv import load_dotenv


from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

async def check_article_images():
    """Check if Korean articles have images that can be used as profile pictures"""
    
    # Initialize database connection
    db = DatabaseService()
    await db.connect()
    print("Connected to database")
    
    try:
        # Get sample of Korean articles
        articles = await db.articles_collection.find({'language': 'ko'}).limit(10).to_list(length=10)
        
        print(f"\nChecking {len(articles)} Korean articles for images:")
        print("-" * 50)
        
        articles_with_image_url = 0
        articles_with_image_section = 0
        
        for idx, article in enumerate(articles):
            title = article.get("title", "Untitled")
            has_image_url = "image_url" in article and article["image_url"]
            
            # Check for image sections in content
            image_sections = []
            if "content" in article and isinstance(article["content"], list):
                image_sections = [
                    section for section in article["content"] 
                    if isinstance(section, dict) and section.get("type") == "image" and section.get("content")
                ]
            
            if has_image_url:
                articles_with_image_url += 1
            
            if image_sections:
                articles_with_image_section += 1
            
            print(f"Article {idx+1}: {title[:40]}...")
            print(f"  Has image_url: {has_image_url}")
            if has_image_url:
                print(f"  Image URL: {article['image_url']}")
            
            print(f"  Has image section(s): {bool(image_sections)} ({len(image_sections)} sections)")
            for i, img_section in enumerate(image_sections):
                print(f"  Image section {i+1}: {img_section.get('content')[:60]}...")
            
            print()
        
        # Summary
        print("-" * 50)
        print(f"Summary for {len(articles)} articles:")
        print(f"  Articles with image_url: {articles_with_image_url} ({articles_with_image_url/len(articles)*100:.0f}%)")
        print(f"  Articles with image sections: {articles_with_image_section} ({articles_with_image_section/len(articles)*100:.0f}%)")
        print(f"  Articles with no images: {len(articles) - max(articles_with_image_url, articles_with_image_section)} ({(len(articles) - max(articles_with_image_url, articles_with_image_section))/len(articles)*100:.0f}%)")
        
    finally:
        # Disconnect from database
        await db.disconnect()
        print("\nDisconnected from database")

if __name__ == "__main__":
    asyncio.run(check_article_images())
