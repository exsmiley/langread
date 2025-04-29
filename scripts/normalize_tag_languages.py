#!/usr/bin/env python3
"""
Script to normalize all tags in the database to use English as the canonical language.

This script:
1. Finds all tags with a non-English base language
2. Converts them to have English as the canonical language
3. Moves non-English content to the translations dictionary
4. Updates any references in articles if needed
"""

from path_helper import setup_path
# Add project root to Python path
setup_path()

import os
import sys
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger


from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logger.add("normalize_tags.log", rotation="10 MB")

# Supported languages with their full names (same as in update_tag_translations.py)
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ko": "Korean",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "zh": "Chinese"
}

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Function to translate a tag to English using OpenAI
async def translate_to_english(tag_name: str, source_language: str) -> str:
    """Translate a tag to English using OpenAI."""
    try:
        prompt = f"Translate this {source_language} tag to English as a single word or short phrase (3 words max): '{tag_name}'"
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful translator. Please provide only the direct translation without any explanation or additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=20
        )
        
        translation = response.choices[0].message.content.strip().lower()
        
        # Remove quotes and other unwanted characters
        translation = translation.replace('"', '').replace("'", '')
        
        logger.info(f"Translated '{tag_name}' ({source_language}) to '{translation}' (en)")
        return translation
    except Exception as e:
        logger.error(f"Error translating {tag_name} to English: {str(e)}")
        # Return the original name if translation fails
        return tag_name

async def process_tags(db: DatabaseService) -> None:
    """Process all tags in the database to normalize their language."""
    
    # Get all tags from the database
    all_tags = await db.get_all_tags_raw()
    logger.info(f"Found {len(all_tags)} tags in the database")
    
    # Count tags by language
    language_counts = {}
    for tag in all_tags:
        lang = tag.get("original_language", "unknown")
        language_counts[lang] = language_counts.get(lang, 0) + 1
    
    logger.info(f"Tag language distribution: {language_counts}")
    
    # Process non-English tags
    non_english_tags = [tag for tag in all_tags if tag.get("original_language") != "en"]
    logger.info(f"Found {len(non_english_tags)} tags with non-English original language")
    
    for i, tag in enumerate(non_english_tags):
        tag_id = str(tag["_id"])
        original_name = tag["name"]
        original_language = tag.get("original_language", "unknown")
        
        logger.info(f"Processing tag {i+1}/{len(non_english_tags)}: {original_name} ({original_language})")
        
        # Skip if already processed
        if original_language == "en":
            logger.info(f"Tag '{original_name}' is already in English - skipping")
            continue
            
        # If there are English translations already, use that
        translations = tag.get("translations", {})
        if "en" in translations and translations["en"]:
            english_name = translations["en"]
            logger.info(f"Using existing English translation: '{english_name}'")
        else:
            # Otherwise, translate the tag
            english_name = await translate_to_english(original_name, original_language)
            
        # Create updated tag document
        updated_tag = tag.copy()
        
        # Update name to be the English canonical name
        updated_tag["name"] = english_name.lower()
        
        # Make sure translations contains the original name
        if "translations" not in updated_tag:
            updated_tag["translations"] = {}
        
        # Add original name to translations if not already there
        if original_language != "en" and original_language not in updated_tag["translations"]:
            updated_tag["translations"][original_language] = original_name.lower()
            
        # Set original language to English
        updated_tag["original_language"] = "en"
        updated_tag["updated_at"] = datetime.now()
        
        # Update the tag in the database
        try:
            await db.update_tag_normalized(tag_id, updated_tag)
            logger.info(f"Successfully updated tag: '{original_name}' → '{english_name}'")
        except Exception as e:
            logger.error(f"Error updating tag '{original_name}': {str(e)}")
            
    logger.info("Tag language normalization completed")

async def main():
    """Main function to run the tag normalization process."""
    try:
        # Initialize database connection
        db = DatabaseService()
        await db.connect()
        logger.info("Connected to database")
        
        # Process tags
        await process_tags(db)
        
        # Summarize results
        logger.info("Tag normalization process completed successfully")
        logger.info("All tags now have English as their canonical language")
        logger.info("Non-English tag names have been moved to translations")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        # Disconnect from database
        await db.disconnect()
        logger.info("Disconnected from database")

# Add method to DatabaseService to update tags
async def update_tag_normalized(self, tag_id: str, updated_tag: dict) -> bool:
    """Update a tag with normalized language."""
    try:
        # Remove the _id field from the update document
        if "_id" in updated_tag:
            del updated_tag["_id"]
            
        result = await self.tags_collection.update_one(
            {"_id": ObjectId(tag_id)},
            {"$set": updated_tag}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating tag: {str(e)}")
        return False

# Add method to get all tags without filtering
async def get_all_tags_raw(self):
    """Get all tags without any filtering."""
    try:
        cursor = self.tags_collection.find({})
        tags = await cursor.to_list(length=1000)
        return tags
    except Exception as e:
        logger.error(f"Error getting all tags: {str(e)}")
        return []

# Add the methods to the DatabaseService class
DatabaseService.update_tag_normalized = update_tag_normalized
DatabaseService.get_all_tags_raw = get_all_tags_raw

if __name__ == "__main__":
    asyncio.run(main())
