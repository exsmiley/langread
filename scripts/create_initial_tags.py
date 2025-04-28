#!/usr/bin/env python3
"""
Script to create initial tags for the LangRead application.
This will create language learning related tags with proper translations.
"""
import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.database import DatabaseService

# Language learning specific tags with translations
LANGUAGE_LEARNING_TAGS = [
    {
        "name": "grammar",
        "translations": {
            "en": "grammar",
            "ko": "문법"
        }
    },
    {
        "name": "vocabulary",
        "translations": {
            "en": "vocabulary",
            "ko": "어휘"
        }
    },
    {
        "name": "reading",
        "translations": {
            "en": "reading",
            "ko": "읽기"
        }
    },
    {
        "name": "writing",
        "translations": {
            "en": "writing",
            "ko": "쓰기"
        }
    },
    {
        "name": "speaking",
        "translations": {
            "en": "speaking",
            "ko": "말하기"
        }
    },
    {
        "name": "listening",
        "translations": {
            "en": "listening",
            "ko": "듣기"
        }
    },
    {
        "name": "culture",
        "translations": {
            "en": "culture",
            "ko": "문화"
        }
    },
    {
        "name": "news",
        "translations": {
            "en": "news",
            "ko": "뉴스"
        }
    },
    {
        "name": "entertainment",
        "translations": {
            "en": "entertainment",
            "ko": "엔터테인먼트"
        }
    },
    {
        "name": "travel",
        "translations": {
            "en": "travel",
            "ko": "여행"
        }
    },
    {
        "name": "food",
        "translations": {
            "en": "food",
            "ko": "음식"
        }
    },
    {
        "name": "sports",
        "translations": {
            "en": "sports",
            "ko": "스포츠"
        }
    },
    {
        "name": "music",
        "translations": {
            "en": "music",
            "ko": "음악"
        }
    },
    {
        "name": "movies",
        "translations": {
            "en": "movies",
            "ko": "영화"
        }
    },
    {
        "name": "technology",
        "translations": {
            "en": "technology",
            "ko": "기술"
        }
    },
    {
        "name": "beginner",
        "translations": {
            "en": "beginner",
            "ko": "초급"
        }
    },
    {
        "name": "intermediate",
        "translations": {
            "en": "intermediate",
            "ko": "중급"
        }
    },
    {
        "name": "advanced",
        "translations": {
            "en": "advanced",
            "ko": "고급"
        }
    }
]

async def create_tags():
    """Create initial tags in the database"""
    db = DatabaseService()
    await db.connect()
    print("Connected to database")
    
    try:
        # Clear existing tags (optional)
        # Comment this line if you want to keep existing tags
        await db.tags_collection.delete_many({})
        print("Cleared existing tags")
        
        # Create new tags
        for tag_data in LANGUAGE_LEARNING_TAGS:
            name = tag_data["name"]
            translations = tag_data["translations"]
            
            # Create tag with English as default language
            tag = await db.create_tag(
                name=name,
                language="en",
                translations=translations,
                auto_approve=True
            )
            print(f"Created tag: {name} with ID: {tag['_id']}")
        
        print("\nAll tags created successfully!")
        print(f"Total tags created: {len(LANGUAGE_LEARNING_TAGS)}")
    finally:
        await db.disconnect()
        print("Disconnected from database")

if __name__ == "__main__":
    asyncio.run(create_tags())
