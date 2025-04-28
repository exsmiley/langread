#!/usr/bin/env python3
"""
Script to create sample tags in the LangRead database
"""
from src.models.database import DatabaseService
import asyncio

async def create_sample_tags():
    db = DatabaseService()
    await db.connect()
    
    # English tags with their names
    en_tag_names = [
        'technology', 'politics', 'health', 'sports', 'business',
        'news', 'science', 'education', 'environment', 'culture'
    ]
    
    # Korean tags with their names and English translations
    ko_tag_data = [
        {'name': '기술', 'english': 'technology'},
        {'name': '정치', 'english': 'politics'},
        {'name': '건강', 'english': 'health'},
        {'name': '스포츠', 'english': 'sports'},
        {'name': '경제', 'english': 'business'},
        {'name': '뉴스', 'english': 'news'},
        {'name': '과학', 'english': 'science'},
        {'name': '교육', 'english': 'education'},
        {'name': '환경', 'english': 'environment'},
        {'name': '문화', 'english': 'culture'}
    ]
    
    # Create English tags
    for name in en_tag_names:
        try:
            tag = await db.create_tag(name=name, language='en', auto_approve=True)
            print(f"Created English tag: {name} with ID: {tag['_id']}")
        except Exception as e:
            print(f"Error creating English tag {name}: {e}")
    
    # Create Korean tags
    for tag_data in ko_tag_data:
        try:
            tag = await db.create_tag(
                name=tag_data['name'], 
                language='ko',
                english_name=tag_data['english'],
                auto_approve=True
            )
            print(f"Created Korean tag: {tag_data['name']} ({tag_data['english']}) with ID: {tag['_id']}")
        except Exception as e:
            print(f"Error creating Korean tag {tag_data['name']}: {e}")
    
    await db.disconnect()
    print('Sample tags created successfully')

if __name__ == "__main__":
    asyncio.run(create_sample_tags())
