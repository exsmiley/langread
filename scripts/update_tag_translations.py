#!/usr/bin/env python3
"""
Script to update all tags with translations in all supported languages.
This ensures consistent tag display across different language settings.
"""

from path_helper import setup_path
# Add project root to Python path
setup_path()

import os
import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
from pymongo import MongoClient
from bson import ObjectId
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger


# Load environment variables
load_dotenv()

# Configure logging
logger.add("update_tags.log", rotation="10 MB")

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "langread")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Supported languages with their full names
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ko": "Korean",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "zh": "Chinese"
}

# Common tag translations - predefine some common translations to reduce API calls
COMMON_TAGS = {
    "technology": {
        "en": "technology", 
        "ko": "기술", 
        "es": "tecnología", 
        "fr": "technologie", 
        "de": "Technologie", 
        "ja": "テクノロジー", 
        "zh": "技术"
    },
    "news": {
        "en": "news", 
        "ko": "뉴스", 
        "es": "noticias", 
        "fr": "actualités", 
        "de": "Nachrichten", 
        "ja": "ニュース", 
        "zh": "新闻"
    },
    "politics": {
        "en": "politics", 
        "ko": "정치", 
        "es": "política", 
        "fr": "politique", 
        "de": "Politik", 
        "ja": "政治", 
        "zh": "政治"
    },
    "sports": {
        "en": "sports", 
        "ko": "스포츠", 
        "es": "deportes", 
        "fr": "sports", 
        "de": "Sport", 
        "ja": "スポーツ", 
        "zh": "体育"
    },
    "business": {
        "en": "business", 
        "ko": "비즈니스", 
        "es": "negocios", 
        "fr": "affaires", 
        "de": "Geschäft", 
        "ja": "ビジネス", 
        "zh": "商业"
    },
    "entertainment": {
        "en": "entertainment", 
        "ko": "엔터테인먼트", 
        "es": "entretenimiento", 
        "fr": "divertissement", 
        "de": "Unterhaltung", 
        "ja": "エンターテイメント", 
        "zh": "娱乐"
    },
    "health": {
        "en": "health", 
        "ko": "건강", 
        "es": "salud", 
        "fr": "santé", 
        "de": "Gesundheit", 
        "ja": "健康", 
        "zh": "健康"
    },
    "science": {
        "en": "science", 
        "ko": "과학", 
        "es": "ciencia", 
        "fr": "science", 
        "de": "Wissenschaft", 
        "ja": "科学", 
        "zh": "科学"
    },
    "education": {
        "en": "education", 
        "ko": "교육", 
        "es": "educación", 
        "fr": "éducation", 
        "de": "Bildung", 
        "ja": "教育", 
        "zh": "教育"
    },
    "travel": {
        "en": "travel", 
        "ko": "여행", 
        "es": "viajes", 
        "fr": "voyages", 
        "de": "Reisen", 
        "ja": "旅行", 
        "zh": "旅游"
    }
}

def translate_tag_via_openai(tag_name: str, target_languages: List[str]) -> Dict[str, str]:
    """
    Translate a tag name to multiple target languages using OpenAI API.
    
    Args:
        tag_name: The tag name to translate (in English)
        target_languages: List of language codes to translate to
        
    Returns:
        Dictionary with language codes as keys and translations as values
    """
    if not target_languages:
        return {}
        
    try:
        # Check if it's a common tag with predefined translations
        if tag_name.lower() in COMMON_TAGS:
            translations = COMMON_TAGS[tag_name.lower()]
            # Only include requested target languages
            return {lang: translations.get(lang, tag_name) for lang in target_languages if lang in translations}
            
        # Create language names string for prompt
        language_names = ", ".join([f"{code} ({SUPPORTED_LANGUAGES[code]})" for code in target_languages])
        
        # Create a prompt for the LLM to translate tags
        prompt = f"""
        Translate the tag "{tag_name}" to the following languages: {language_names}.
        The tag should be translated as a single word or short phrase that would be used for categorizing content.
        Return ONLY a valid JSON object with language codes as keys and translations as values.
        Example: {{"ko": "기술", "es": "tecnología"}}
        """
        
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a precise translation assistant that returns only the requested translation in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # Extract translated tags from response
        content = completion.choices[0].message.content
        translations = json.loads(content)
        
        # Ensure all requested languages are included
        result = {}
        for lang in target_languages:
            if lang in translations and translations[lang]:
                result[lang] = translations[lang]
        
        return result
        
    except Exception as e:
        logger.error(f"Error translating tag '{tag_name}': {str(e)}")
        return {}

def update_tag_translations():
    """Main function to update tag translations for all tags in the database."""
    logger.info("Starting tag translation update process")
    
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    tags_collection = db.tags
    
    # Get all tags
    all_tags = list(tags_collection.find())
    total_tags = len(all_tags)
    logger.info(f"Found {total_tags} tags to process")
    
    # Process tags in batches to avoid rate limits
    batch_size = 10
    tags_updated = 0
    languages_added = 0
    
    for i in range(0, total_tags, batch_size):
        batch = all_tags[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(total_tags + batch_size - 1)//batch_size}")
        
        for tag in batch:
            tag_id = tag["_id"]
            tag_name = tag.get("name", "")
            current_translations = tag.get("translations", {})
            
            # Skip tags without a name
            if not tag_name:
                logger.warning(f"Skipping tag without name: {tag_id}")
                continue
                
            # Determine which languages need translations
            missing_languages = [lang for lang in SUPPORTED_LANGUAGES.keys() 
                                if lang not in current_translations or not current_translations[lang]]
            
            if not missing_languages:
                logger.debug(f"Tag '{tag_name}' already has all translations")
                continue
                
            logger.info(f"Updating tag '{tag_name}' with translations for: {', '.join(missing_languages)}")
            
            # Get translations for missing languages
            new_translations = translate_tag_via_openai(tag_name, missing_languages)
            
            if new_translations:
                # Update translations in the database
                update_data = {}
                for lang, translation in new_translations.items():
                    update_data[f"translations.{lang}"] = translation
                    
                if update_data:
                    result = tags_collection.update_one(
                        {"_id": tag_id},
                        {"$set": update_data}
                    )
                    
                    if result.modified_count > 0:
                        tags_updated += 1
                        languages_added += len(update_data)
                        logger.success(f"Updated tag '{tag_name}' with {len(update_data)} new translations")
            else:
                logger.warning(f"No translations generated for tag '{tag_name}'")
    
    logger.success(f"Tag translation update completed. Updated {tags_updated} tags with {languages_added} new translations.")
    
    # Print out some examples of fully translated tags
    top_tags = list(tags_collection.find().sort("article_count", -1).limit(10))
    logger.info("Examples of fully translated tags:")
    for tag in top_tags:
        logger.info(f"Tag: {tag.get('name')} | Translations: {tag.get('translations', {})}")

if __name__ == "__main__":
    # Run the tag translation update
    update_tag_translations()
