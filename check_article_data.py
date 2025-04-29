#!/usr/bin/env python3
"""
Check article data to inspect tags and source information
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from pprint import pprint

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

async def check_article_data():
    """Check article data to inspect tags and source information"""
    
    # Initialize database connection
    db = DatabaseService()
    await db.connect()
    print("Connected to database")
    
    try:
        # Get sample of Korean articles
        articles = await db.articles_collection.find({'language': 'ko'}).limit(5).to_list(length=5)
        
        print(f"\nChecking {len(articles)} Korean articles for tag data:")
        print("-" * 50)
        
        for idx, article in enumerate(articles):
            print(f"\nArticle {idx+1}:")
            print(f"  ID: {article.get('_id')}")
            print(f"  Title: {article.get('title', 'Untitled')}")
            print(f"  Source: {article.get('source', 'Unknown')}")
            print(f"  Publication: {article.get('publication', 'N/A')}")
            print(f"  Publisher: {article.get('publisher', 'N/A')}")
            
            # Check for topic data
            topics = article.get("topics", [])
            print(f"  Topics: {topics}")
            
            # Check for tag IDs
            tag_ids = article.get("tag_ids", [])
            print(f"  Tag IDs: {tag_ids}")
            
            # If we have tag IDs, fetch the actual tags
            if tag_ids:
                tags = []
                for tag_id in tag_ids:
                    tag = await db.tags_collection.find_one({"_id": tag_id})
                    if tag:
                        tags.append({
                            "name": tag.get("name"),
                            "translations": tag.get("translations", {})
                        })
                print(f"  Tag details: {tags}")
    
    finally:
        # Disconnect from database
        await db.disconnect()
        print("\nDisconnected from database")

if __name__ == "__main__":
    asyncio.run(check_article_data())
