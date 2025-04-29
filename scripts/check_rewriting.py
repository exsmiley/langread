#!/usr/bin/env python
"""
Script to check if article rewriting is working correctly.
This script will:
1. Connect to MongoDB
2. Query for raw articles
3. Find corresponding rewritten versions
4. Print results
"""
from path_helper import setup_path
# Add project root to Python path
setup_path()

import sys
import os
import asyncio
from datetime import datetime
from pprint import pprint
from typing import Dict, List, Any, Optional

# Add project root to path to import modules
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from src.models.database import DatabaseService

async def check_rewriting_status():
    # Connect to database
    db = DatabaseService()
    await db.connect()
    print("Connected to MongoDB database")
    
    # Set a reasonable limit to avoid overwhelming terminal
    limit = 3
    
    # Query for raw articles
    raw_articles_cursor = db.articles_collection.find(
        {"content_type": "raw"},
        {"_id": 1, "title": 1, "language": 1, "url": 1, "bulk_fetch_id": 1}
    ).limit(limit)
    
    raw_articles = await raw_articles_cursor.to_list(length=limit)
    
    if not raw_articles:
        print("No raw articles found in the database")
        return
    
    print(f"Found {len(raw_articles)} raw articles")
    
    for idx, raw_article in enumerate(raw_articles):
        print(f"\n--- Raw Article {idx+1} ---")
        print(f"Title: {raw_article.get('title', 'Unknown title')}")
        print(f"Language: {raw_article.get('language', 'Unknown language')}")
        print(f"ID: {raw_article.get('_id', 'Unknown ID')}")
        
        # Get bulk fetch ID to find rewritten versions
        bulk_fetch_id = raw_article.get('bulk_fetch_id')
        if not bulk_fetch_id:
            print("No bulk fetch ID found for this article, cannot search for rewritten versions")
            continue
        
        # Find rewritten versions
        difficulties = ["beginner", "intermediate", "advanced"]
        for difficulty in difficulties:
            rewritten_cursor = db.articles_collection.find(
                {
                    "bulk_fetch_id": bulk_fetch_id,
                    "content_type": "rewritten",
                    "difficulty": difficulty
                },
                {"_id": 1, "title": 1, "text": 1, "date_created": 1}
            ).limit(1)
            
            rewritten = await rewritten_cursor.to_list(length=1)
            
            if rewritten:
                article = rewritten[0]
                print(f"\n  Rewritten at {difficulty} level:")
                print(f"  Title: {article.get('title', 'Unknown title')}")
                print(f"  Created: {article.get('date_created', 'Unknown date')}")
                
                # Print a snippet of the text
                text = article.get('text', '')
                text_preview = text[:150] + "..." if text and len(text) > 150 else text
                print(f"  Text preview: {text_preview}")
            else:
                print(f"\n  No rewritten version found at {difficulty} level")
    
    # Close database connection
    await db.disconnect()
    print("\nDisconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(check_rewriting_status())
