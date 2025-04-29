#!/usr/bin/env python3
"""
Check database connection and article status
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

async def check_database():
    """Check database connection and article status"""
    
    # Initialize database connection
    db = DatabaseService()
    await db.connect()
    print("Connected to database")
    
    try:
        # Count articles
        total_articles = await db.articles_collection.count_documents({})
        print(f"Total articles in database: {total_articles}")
        
        # Count by language
        ko_articles = await db.articles_collection.count_documents({"language": "ko"})
        print(f"Korean articles: {ko_articles}")
        
        # Check latest articles
        latest_articles = await db.articles_collection.find({}).sort("_id", -1).limit(3).to_list(length=3)
        
        print("\nLatest articles:")
        for article in latest_articles:
            print(f"  ID: {article.get('_id')}")
            print(f"  Title: {article.get('title', 'Untitled')}")
            print(f"  Topics: {article.get('topics', [])}")
            print(f"  Tag IDs: {article.get('tag_ids', [])}")
            print()
            
        # Check if any articles have invalid tag_ids
        invalid_tags = await db.articles_collection.count_documents({"tag_ids": {"$exists": True, "$ne": []}})
        print(f"Articles with tag_ids: {invalid_tags}")
        
        # Check if any tags might be invalid ObjectIds
        sample_article = await db.articles_collection.find_one({"tag_ids": {"$exists": True, "$ne": []}})
        if sample_article and "tag_ids" in sample_article:
            tag_ids = sample_article["tag_ids"]
            print(f"\nSample article tag_ids format: {type(tag_ids[0])}")
            
            # Check if the tags exist in the tags collection
            for tag_id in tag_ids[:3]:  # Check first 3 tags
                tag = await db.tags_collection.find_one({"_id": tag_id})
                print(f"Tag ID {tag_id}: {'Found' if tag else 'Not found'}")
        
    finally:
        # Disconnect from database
        await db.disconnect()
        print("\nDisconnected from database")

if __name__ == "__main__":
    asyncio.run(check_database())
