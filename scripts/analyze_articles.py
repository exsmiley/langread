#!/usr/bin/env python3
"""
Script to analyze article and tag data in the database.
"""

from path_helper import setup_path
# Add project root to Python path
setup_path()

import asyncio
import os
import sys
from typing import Dict, List, Set
from bson import ObjectId
from dotenv import load_dotenv


from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

async def analyze_data():
    """Analyze article and tag data in the database."""
    
    print("-" * 50)
    print("Lingogi Database Analysis")
    print("-" * 50)
    
    # Initialize database connection
    db = DatabaseService()
    await db.connect()
    print("Connected to database")
    
    try:
        # Count articles by language
        languages = ["ko", "en", "es", "fr", "de", "ja", "zh"]
        print("\nArticle counts by language:")
        for lang in languages:
            count = await db.articles_collection.count_documents({"language": lang})
            if count > 0:
                print(f"  {lang}: {count} articles")
        
        # Count total articles
        total_articles = await db.articles_collection.count_documents({})
        print(f"\nTotal articles: {total_articles}")
        
        # Get details about Korean articles
        korean_articles = await db.articles_collection.find({"language": "ko"}).to_list(length=100)
        print(f"\nDetails about Korean articles (showing up to 100):")
        print(f"  Found {len(korean_articles)} Korean articles")
        
        # Analyze difficulty levels
        difficulty_counts = {}
        for article in korean_articles:
            difficulty = article.get("difficulty", "unknown")
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        print("\nKorean articles by difficulty:")
        for difficulty, count in difficulty_counts.items():
            print(f"  {difficulty}: {count} articles")
        
        # Analyze tag usage
        print("\nAnalyzing tag usage in Korean articles:")
        tag_usage = {}
        articles_with_tags = 0
        articles_without_tags = 0
        
        for article in korean_articles:
            tag_ids = article.get("tag_ids", [])
            if tag_ids:
                articles_with_tags += 1
                for tag_id in tag_ids:
                    if isinstance(tag_id, ObjectId):
                        tag_id = str(tag_id)
                    tag_usage[tag_id] = tag_usage.get(tag_id, 0) + 1
            else:
                articles_without_tags += 1
        
        print(f"  Articles with tags: {articles_with_tags}")
        print(f"  Articles without tags: {articles_without_tags}")
        
        # Get the most common tags
        if tag_usage:
            # Get tag names for the most common tags
            most_common_tags = sorted(tag_usage.items(), key=lambda x: x[1], reverse=True)[:10]
            print("\nMost common tags in Korean articles:")
            for tag_id, count in most_common_tags:
                tag = await db.get_tag(tag_id)
                if tag:
                    tag_name = tag.get("name", "Unknown")
                    print(f"  {tag_name}: {count} articles")
        
        # Check default tag selection in ArticleListPage
        print("\nChecking for default tag selection in frontend code...")
        with open(os.path.join("src", "frontend", "src", "pages", "ArticleListPage.tsx"), "r") as f:
            content = f.read()
            if "defaultSelectedTags" in content or "setSelectedTags" in content:
                print("  Found potential default tag selection in ArticleListPage.tsx")
            else:
                print("  No obvious default tag selection found in ArticleListPage.tsx")
        
    finally:
        # Disconnect from database
        await db.disconnect()
        print("\nDisconnected from database")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(analyze_data())
