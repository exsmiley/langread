#!/usr/bin/env python3
"""
Debug the articles API to identify and fix the error
"""

from path_helper import setup_path
# Add project root to Python path
setup_path()

import asyncio
import os
import sys
import json
import traceback
from pprint import pprint
from dotenv import load_dotenv


from src.models.database import DatabaseService
from src.api.routers.article_utils import fetch_articles_with_filters

# Load environment variables
load_dotenv()

async def debug_articles_api():
    """Debug the articles API and fix the issue"""
    
    # Initialize database connection
    db = DatabaseService()
    await db.connect()
    print("Connected to database")
    
    try:
        # Try to replicate the article request
        print("\nAttempting to fetch articles with basic filters...")
        try:
            # Basic test with minimal filters
            articles = await fetch_articles_with_filters(
                db=db,
                language="ko",
                difficulty="intermediate",
                limit=5
            )
            print(f"Successfully fetched {len(articles)} articles")
            
            # Print brief summary of each article
            for i, article in enumerate(articles[:3], 1):
                print(f"\nArticle {i}:")
                print(f"  Title: {article.get('title', 'Untitled')}")
                print(f"  Topics: {article.get('topics', [])}")
                print(f"  Tag IDs: {article.get('tag_ids', [])}")
                
        except Exception as e:
            print(f"Error fetching articles: {str(e)}")
            traceback.print_exc()
            
            # If error is related to tag_ids, try to check and fix tag_ids
            print("\nChecking article tag_ids format...")
            articles = await db.articles_collection.find({"language": "ko"}).limit(5).to_list(length=5)
            
            for article in articles:
                tag_ids = article.get("tag_ids", [])
                print(f"Article '{article.get('title', 'Untitled')}' has tag_ids: {tag_ids} (type: {type(tag_ids)})")
                
                # Check each tag_id
                if tag_ids and isinstance(tag_ids, list):
                    for i, tag_id in enumerate(tag_ids):
                        print(f"  Tag ID #{i+1}: {tag_id} (type: {type(tag_id)})")
            
            # Try to fix common tag_id issues by ensuring they're ObjectIds
            print("\nFixing any string tag_ids in the first 50 articles...")
            from bson import ObjectId
            
            # Check and fix articles
            fixed_count = 0
            cursor = db.articles_collection.find({"language": "ko"})
            articles_to_check = await cursor.limit(50).to_list(length=50)
            
            for article in articles_to_check:
                tag_ids = article.get("tag_ids", [])
                if not tag_ids or not isinstance(tag_ids, list):
                    continue
                
                # Check if any tag_id is a string
                need_fix = False
                fixed_tag_ids = []
                
                for tag_id in tag_ids:
                    if isinstance(tag_id, str):
                        need_fix = True
                        try:
                            # Convert string to ObjectId
                            fixed_tag_ids.append(ObjectId(tag_id))
                        except:
                            # Skip invalid tag_id
                            continue
                    else:
                        fixed_tag_ids.append(tag_id)
                
                # Update article if needed
                if need_fix:
                    result = await db.articles_collection.update_one(
                        {"_id": article["_id"]},
                        {"$set": {"tag_ids": fixed_tag_ids}}
                    )
                    if result.modified_count > 0:
                        fixed_count += 1
            
            print(f"Fixed tag_ids in {fixed_count} articles")
            
            # Try one more time with the fix
            if fixed_count > 0:
                print("\nRetrying article fetch after fixes...")
                articles = await fetch_articles_with_filters(
                    db=db,
                    language="ko",
                    difficulty="intermediate",
                    limit=5
                )
                print(f"Successfully fetched {len(articles)} articles after fixes")
            
    finally:
        # Disconnect from database
        await db.disconnect()
        print("\nDisconnected from database")

if __name__ == "__main__":
    asyncio.run(debug_articles_api())
