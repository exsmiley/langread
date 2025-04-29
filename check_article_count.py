#!/usr/bin/env python3
"""
Script to check article counts by language and difficulty level.
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

async def check_articles():
    """Check article counts by language and difficulty level."""
    
    # Initialize database connection
    db = DatabaseService()
    await db.connect()
    print("Connected to database")
    
    try:
        # Languages to check
        languages = ["ko", "en", "es", "fr", "de", "ja", "zh"]
        difficulty_levels = ["beginner", "intermediate", "advanced", "unknown"]
        
        # Check total article counts
        print("\n=== TOTAL ARTICLE COUNTS ===")
        for lang in languages:
            count = await db.articles_collection.count_documents({"language": lang})
            if count > 0:
                print(f"{lang.upper()}: {count} articles")
        
        # Check article counts by difficulty for Korean
        print("\n=== KOREAN ARTICLES BY DIFFICULTY ===")
        for difficulty in difficulty_levels:
            if difficulty == "unknown":
                # Count articles with no difficulty field
                count = await db.articles_collection.count_documents({
                    "language": "ko",
                    "difficulty": {"$exists": False}
                })
            else:
                count = await db.articles_collection.count_documents({
                    "language": "ko",
                    "difficulty": difficulty
                })
            print(f"{difficulty.capitalize()}: {count} articles")
            
        # Check article counts by tag IDs for Korean
        print("\n=== KOREAN ARTICLES BY TAG AVAILABILITY ===")
        with_tags = await db.articles_collection.count_documents({
            "language": "ko",
            "tag_ids": {"$exists": True, "$ne": []}
        })
        without_tags = await db.articles_collection.count_documents({
            "language": "ko",
            "$or": [
                {"tag_ids": {"$exists": False}},
                {"tag_ids": []}
            ]
        })
        print(f"With tags: {with_tags} articles")
        print(f"Without tags: {without_tags} articles")
        
        # Test how many Korean articles would show up in the default filter scenario
        default_filter_count = await db.articles_collection.count_documents({
            "language": "ko",
            "difficulty": "intermediate"
        })
        print(f"\nKorean intermediate articles (default filter): {default_filter_count}")
        
        # Test how many articles would show up total (without default filtering)
        all_korean = await db.articles_collection.count_documents({
            "language": "ko"
        })
        print(f"All Korean articles (no filtering): {all_korean}")
        
    finally:
        # Disconnect from database
        await db.disconnect()
        print("\nDisconnected from database")

if __name__ == "__main__":
    asyncio.run(check_articles())
