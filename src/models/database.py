"""
Database services for Lingogi application.
Provides functionality for storing and retrieving articles, vocabulary, and user data.
"""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import os
import motor.motor_asyncio
from pymongo import ReturnDocument
from bson import ObjectId
import json
from pydantic import BaseModel
import logging

# Configure logging
logger = logging.getLogger(__name__)

class PyObjectId(str):
    """Custom ObjectId class for Pydantic models to work with MongoDB ObjectId."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class DatabaseService:
    """Service for interacting with MongoDB database."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the database service.
        
        Args:
            connection_string: MongoDB connection string
                (if None, will try to get from environment)
        """
        self.connection_string = connection_string or os.getenv("MONGODB_URI", "mongodb://localhost:27017/langread")
        self.client = None
        self.db = None
        
        # Collections
        self.articles_collection = None
        self.vocabulary_collection = None
        self.users_collection = None
        self.flashcards_collection = None
        self.tags_collection = None
    
    async def connect(self):
        """Connect to the database."""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.connection_string)
            self.db = self.client.langread
            
            # Initialize collections
            self.articles_collection = self.db.articles
            self.vocabulary_collection = self.db.vocabulary
            self.users_collection = self.db.users
            self.flashcards_collection = self.db.flashcards
            self.tags_collection = self.db.tags
            
            # Create indexes
            await self.articles_collection.create_index([("date_fetched", 1)])
            await self.articles_collection.create_index([("language", 1)])
            await self.articles_collection.create_index([("topics", 1)])
            
            await self.vocabulary_collection.create_index([("word", 1), ("language", 1)], unique=True)
            await self.vocabulary_collection.create_index([("tags", 1)])
            
            await self.users_collection.create_index([("email", 1)], unique=True)
            
            await self.flashcards_collection.create_index([("user_id", 1), ("word", 1), ("language", 1)], unique=True)
            
            logger.info("Connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from the database."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    # Article methods
    async def save_article(self, article_data: Dict[str, Any]) -> str:
        """
        Save an article to the database.
        
        Args:
            article_data: Article data
            
        Returns:
            ID of the saved article
        """
        try:
            # Check if article already exists by URL
            existing_article = await self.articles_collection.find_one({"url": article_data["url"]})
            
            if existing_article:
                # Update existing article
                article_data["_id"] = existing_article["_id"]
                article_data["updated_at"] = datetime.utcnow()
                
                await self.articles_collection.replace_one(
                    {"_id": existing_article["_id"]},
                    article_data
                )
                logger.info(f"Updated article: {article_data['title']}")
                return str(existing_article["_id"])
            else:
                # Create new article
                article_data["created_at"] = datetime.utcnow()
                article_data["updated_at"] = article_data["created_at"]
                
                result = await self.articles_collection.insert_one(article_data)
                logger.info(f"Created article: {article_data['title']}")
                return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving article: {str(e)}")
            raise
    
    async def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an article by ID.
        
        Args:
            article_id: Article ID
            
        Returns:
            Article data or None if not found
        """
        try:
            article = await self.articles_collection.find_one({"_id": ObjectId(article_id)})
            if article:
                article["_id"] = str(article["_id"])
            return article
        except Exception as e:
            logger.error(f"Error getting article: {str(e)}")
            return None
    
    async def get_articles(self, 
                          language: Optional[str] = None, 
                          topic: Optional[str] = None,
                          date_from: Optional[datetime] = None,
                          date_to: Optional[datetime] = None,
                          limit: int = 10,
                          skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get articles with optional filtering.
        
        Args:
            language: Filter by language
            topic: Filter by topic
            date_from: Filter by date from
            date_to: Filter by date to
            limit: Maximum number of articles to return
            skip: Number of articles to skip (for pagination)
            
        Returns:
            List of article data
        """
        try:
            # Build query
            query = {}
            
            if language:
                query["language"] = language
            
            if topic:
                query["topics"] = topic
            
            if date_from or date_to:
                date_query = {}
                if date_from:
                    date_query["$gte"] = date_from
                if date_to:
                    date_query["$lte"] = date_to
                
                if date_query:
                    query["date_fetched"] = date_query
            
            # Execute query
            cursor = self.articles_collection.find(query)
            
            # Sort by date (newest first)
            cursor = cursor.sort("date_fetched", -1)
            
            # Apply pagination
            cursor = cursor.skip(skip).limit(limit)
            
            # Convert to list
            articles = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for article in articles:
                article["_id"] = str(article["_id"])
            
            return articles
        except Exception as e:
            logger.error(f"Error getting articles: {str(e)}")
            return []
    
    async def get_article_tags(self, article_id: str, language: str = None) -> List[dict]:
        """Get all tags for an article with optional language filtering for translations"""
        article = await self.articles_collection.find_one({"_id": article_id})
        if not article or "tag_ids" not in article:
            return []
            
        # Convert tag IDs to ObjectId
        tag_ids = [ObjectId(tag_id) for tag_id in article["tag_ids"]]
        if not tag_ids:
            return []
            
        # Get tags
        cursor = self.tags_collection.find({"_id": {"$in": tag_ids}})
        tags = await cursor.to_list(length=1000)
        
        # If language is specified, add the localized name to each tag
        if language and language != "en":
            for tag in tags:
                if "translations" in tag and language in tag["translations"]:
                    tag["localized_name"] = tag["translations"][language]
                else:
                    tag["localized_name"] = tag["name"]
        
        return tags
    
    # Vocabulary methods
    async def save_vocabulary(self, vocabulary_data: Dict[str, Any]) -> str:
        """
        Save a vocabulary item to the database.
        
        Args:
            vocabulary_data: Vocabulary data
            
        Returns:
            ID of the saved vocabulary item
        """
        try:
            # Check if vocabulary item already exists
            existing_vocab = await self.vocabulary_collection.find_one({
                "word": vocabulary_data["word"],
                "language": vocabulary_data["language"]
            })
            
            if existing_vocab:
                # Update existing vocabulary
                vocabulary_data["_id"] = existing_vocab["_id"]
                vocabulary_data["updated_at"] = datetime.utcnow()
                
                # Merge article references and tags
                if "article_references" in vocabulary_data:
                    if "article_references" in existing_vocab:
                        vocabulary_data["article_references"] = list(set(
                            existing_vocab["article_references"] + vocabulary_data["article_references"]
                        ))
                
                if "tags" in vocabulary_data:
                    if "tags" in existing_vocab:
                        vocabulary_data["tags"] = list(set(
                            existing_vocab["tags"] + vocabulary_data["tags"]
                        ))
                
                await self.vocabulary_collection.replace_one(
                    {"_id": existing_vocab["_id"]},
                    vocabulary_data
                )
                logger.info(f"Updated vocabulary: {vocabulary_data['word']}")
                return str(existing_vocab["_id"])
            else:
                # Create new vocabulary
                vocabulary_data["created_at"] = datetime.utcnow()
                vocabulary_data["updated_at"] = vocabulary_data["created_at"]
                
                result = await self.vocabulary_collection.insert_one(vocabulary_data)
                logger.info(f"Created vocabulary: {vocabulary_data['word']}")
                return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving vocabulary: {str(e)}")
            raise
    
    async def get_vocabulary(self, 
                           word: Optional[str] = None,
                           language: Optional[str] = None,
                           tags: Optional[List[str]] = None,
                           article_id: Optional[str] = None,
                           limit: int = 50,
                           skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get vocabulary items with optional filtering.
        
        Args:
            word: Filter by word (exact match)
            language: Filter by language
            tags: Filter by tags
            article_id: Filter by article reference
            limit: Maximum number of items to return
            skip: Number of items to skip (for pagination)
            
        Returns:
            List of vocabulary data
        """
        try:
            # Build query
            query = {}
            
            if word:
                query["word"] = word
            
            if language:
                query["language"] = language
            
            if tags:
                query["tags"] = {"$all": tags}
            
            if article_id:
                query["article_references"] = article_id
            
            # Execute query
            cursor = self.vocabulary_collection.find(query)
            
            # Sort by word
            cursor = cursor.sort("word", 1)
            
            # Apply pagination
            cursor = cursor.skip(skip).limit(limit)
            
            # Convert to list
            vocabulary_items = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for item in vocabulary_items:
                item["_id"] = str(item["_id"])
            
            return vocabulary_items
        except Exception as e:
            logger.error(f"Error getting vocabulary: {str(e)}")
            return []
    
    async def get_vocabulary_item(self, vocabulary_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a vocabulary item by ID.
        
        Args:
            vocabulary_id: Vocabulary ID
            
        Returns:
            Vocabulary data or None if not found
        """
        try:
            vocabulary = await self.vocabulary_collection.find_one({"_id": ObjectId(vocabulary_id)})
            if vocabulary:
                vocabulary["_id"] = str(vocabulary["_id"])
            return vocabulary
        except Exception as e:
            logger.error(f"Error getting vocabulary item: {str(e)}")
            return None
    
    # Flashcard methods
    async def save_flashcard(self, flashcard_data: Dict[str, Any]) -> str:
        """
        Save a flashcard to the database.
        
        Args:
            flashcard_data: Flashcard data
            
        Returns:
            ID of the saved flashcard
        """
        try:
            # Check if flashcard already exists
            existing_flashcard = None
            if "user_id" in flashcard_data and "word" in flashcard_data and "language" in flashcard_data:
                existing_flashcard = await self.flashcards_collection.find_one({
                    "user_id": flashcard_data["user_id"],
                    "word": flashcard_data["word"],
                    "language": flashcard_data["language"]
                })
            
            if existing_flashcard:
                # Update existing flashcard
                flashcard_data["_id"] = existing_flashcard["_id"]
                flashcard_data["updated_at"] = datetime.utcnow()
                
                await self.flashcards_collection.replace_one(
                    {"_id": existing_flashcard["_id"]},
                    flashcard_data
                )
                logger.info(f"Updated flashcard: {flashcard_data['word']}")
                return str(existing_flashcard["_id"])
            else:
                # Create new flashcard
                flashcard_data["created_at"] = datetime.utcnow()
                flashcard_data["updated_at"] = flashcard_data["created_at"]
                
                result = await self.flashcards_collection.insert_one(flashcard_data)
                logger.info(f"Created flashcard: {flashcard_data['word']}")
                return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving flashcard: {str(e)}")
            raise
    
    async def get_flashcards(self,
                           user_id: str,
                           language: Optional[str] = None,
                           tags: Optional[List[str]] = None,
                           limit: int = 50,
                           skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get flashcards for a user with optional filtering.
        
        Args:
            user_id: User ID
            language: Filter by language
            tags: Filter by tags
            limit: Maximum number of items to return
            skip: Number of items to skip (for pagination)
            
        Returns:
            List of flashcard data
        """
        try:
            # Build query
            query = {"user_id": user_id}
            
            if language:
                query["language"] = language
            
            if tags:
                query["tags"] = {"$all": tags}
            
            # Execute query
            cursor = self.flashcards_collection.find(query)
            
            # Sort by next review date
            cursor = cursor.sort("next_review", 1)
            
            # Apply pagination
            cursor = cursor.skip(skip).limit(limit)
            
            # Convert to list
            flashcards = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for flashcard in flashcards:
                flashcard["_id"] = str(flashcard["_id"])
            
            return flashcards
        except Exception as e:
            logger.error(f"Error getting flashcards: {str(e)}")
            return []


    async def create_tag(self, name: str, language: str, english_name: str = None, translations: dict = None, article_ids: List[str] = [], auto_approve: bool = False) -> dict:
        """
        Create a new tag with English as the canonical name and optional translations.
        
        IMPORTANT TAG DESIGN NOTE: In Lingogi, all tags are canonically stored in English, with translations
        stored as metadata. This allows for consistent cross-language article categorization while
        enabling localized display in the user interface.
        
        When a tag is displayed in the UI, it should be shown in the user's native language, not the
        target language they are learning. So an English user learning Korean should see tags in English.
        
        Args:
            name: The tag name in the source language
            language: The language code of the source language
            english_name: The English name for this tag (if name is not already in English)
            translations: Dictionary of translations keyed by language code
            article_ids: List of article IDs to associate with this tag
            auto_approve: Whether to automatically approve this tag
            
        Returns:
            The created tag document
        """
        # Use english_name if provided, otherwise use name (assuming it's already in English)
        canonical_name = english_name.lower() if english_name else name.lower()
        
        # Initialize translations dict if not provided
        if translations is None:
            translations = {}
            
        # If name is not in English and not already in translations, add it
        if language != "en" and language not in translations and english_name is not None:
            translations[language] = name.lower()
        
        # Check if this is a language tag that should be auto-approved
        # Language tags include language codes (en, ko, fr) and language names (english, korean, french)
        language_codes = ["en", "ko", "fr", "es", "de", "ja", "zh", "ru", "pt", "ar", "hi", "bn", "it"]
        language_names = ["english", "korean", "french", "spanish", "german", "japanese", "chinese", 
                         "russian", "portuguese", "arabic", "hindi", "bengali", "italian"]
        
        # Also automatically approve standard category tags
        auto_approved_categories = [
            # General categories
            "news", "politics", "technology", "science", "health", "business", "economy",
            "entertainment", "sports", "education", "environment", "culture", "art",
            "food", "travel", "religion", "history", "literature", "fashion", "music",
            "film", "television", "automotive", "finance", "lifestyle", "social_issues", "international", "crime",
            # Include translations of these categories
            "뉴스", "정치", "기술", "과학", "건강", "경제", "비즈니스", "엔터테인먼트", "스포츠",
            "noticias", "política", "tecnología", "ciencia", "salud", "negocios",
            "actualités", "politique", "technologie", "santé", "affaires"
        ]
        
        is_auto_approved = auto_approve or \
                         canonical_name.lower() in language_codes or \
                         canonical_name.lower() in language_names or \
                         canonical_name.lower() in auto_approved_categories
        
        tag = {
            "name": canonical_name,  # Store canonical English name
            "language_specific": language != "en",  # Flag if it's a language-specific concept
            "translations": translations,  # Store translations in different languages
            "original_language": language,  # Record the original language it was created in
            "article_count": len(article_ids),
            "active": is_auto_approved,  # Auto-approve language tags and standard categories
            "auto_approved": is_auto_approved,  # Mark that this was auto-approved
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = await self.tags_collection.insert_one(tag)
        tag["_id"] = result.inserted_id
        
        # Associate tag with articles
        for article_id in article_ids:
            await self.add_tag_to_article(str(tag["_id"]), article_id)
            
        return tag
    
    async def get_tag(self, tag_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a tag by ID.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            Tag data or None if not found
        """
        try:
            tag = await self.tags_collection.find_one({"_id": ObjectId(tag_id)})
            if tag:
                tag["_id"] = str(tag["_id"])
            return tag
        except Exception as e:
            logger.error(f"Error getting tag: {str(e)}")
            return None
    
    async def get_tags(self, language: str = None, active_only: bool = False, query: str = None) -> List[dict]:
        """Get all tags with optional filtering"""
        filter_query = {}
        
        if language:
            # For language filtering, check if it's either the original language
            # or if it has a translation in that language
            filter_query["$or"] = [
                {"original_language": language},
                {f"translations.{language}": {"$exists": True}}
            ]
            
        if active_only:
            filter_query["active"] = True
            
        if query:
            # Search in canonical name and translations
            regex_pattern = f".*{query}.*"
            name_condition = {"name": {"$regex": regex_pattern, "$options": "i"}}
            translation_conditions = []
            
            # If language is specified, only search translations for that language
            if language:
                translation_conditions.append({f"translations.{language}": {"$regex": regex_pattern, "$options": "i"}})
            else:
                # Otherwise, search all translations
                translation_conditions.append({"translations": {"$regex": regex_pattern, "$options": "i"}})
            
            filter_query["$or"] = [name_condition, *translation_conditions]
            
        cursor = self.tags_collection.find(filter_query)
        tags = await cursor.to_list(length=1000)
        return tags
    
    async def add_tag_to_article(self, tag_id: str, article_id: str) -> bool:
        """Add a tag to an article (stores only the tag ID, not the tag name)"""
        # Convert tag_id to ObjectId if it's a string
        tag_obj_id = ObjectId(tag_id) if isinstance(tag_id, str) else tag_id
        
        # Update article to add tag ID
        article_result = await self.articles_collection.update_one(
            {"_id": article_id},
            {"$addToSet": {"tag_ids": str(tag_obj_id)}}
        )
        
        # Update tag to increment article count
        tag_result = await self.tags_collection.update_one(
            {"_id": tag_obj_id},
            {"$inc": {"article_count": 1}, "$set": {"updated_at": datetime.now()}}
        )
        
        return article_result.modified_count > 0 and tag_result.modified_count > 0

    async def remove_tag_from_article(self, tag_id: str, article_id: str) -> bool:
        """Remove a tag from an article"""
        # Convert tag_id to ObjectId if it's a string
        tag_obj_id = ObjectId(tag_id) if isinstance(tag_id, str) else tag_id
        
        # Update article to remove tag ID
        article_result = await self.articles_collection.update_one(
            {"_id": article_id},
            {"$pull": {"tag_ids": str(tag_obj_id)}}
        )
        
        # Update tag to decrement article count
        tag_result = await self.tags_collection.update_one(
            {"_id": tag_obj_id},
            {"$inc": {"article_count": -1}, "$set": {"updated_at": datetime.now()}}
        )
        
        return article_result.modified_count > 0 and tag_result.modified_count > 0

    async def update_article_tags(self, article_id: str, tag_ids: List[str]) -> bool:
        """Update all tags for an article (storing only tag IDs)"""
        # First remove article from all existing tags
        article = await self.articles_collection.find_one({"_id": article_id})
        if article and "tag_ids" in article:
            for tag_id in article["tag_ids"]:
                await self.tags_collection.update_one(
                    {"_id": ObjectId(tag_id)},
                    {"$inc": {"article_count": -1}, "$set": {"updated_at": datetime.now()}}
                )
        
        # Ensure all tag_ids are strings
        string_tag_ids = [str(tag_id) for tag_id in tag_ids]
        
        # Update article with new tag IDs
        result = await self.articles_collection.update_one(
            {"_id": article_id},
            {"$set": {"tag_ids": string_tag_ids}}
        )
        
        # Update article count for all new tags
        for tag_id in tag_ids:
            await self.tags_collection.update_one(
                {"_id": ObjectId(tag_id) if isinstance(tag_id, str) else tag_id},
                {"$inc": {"article_count": 1}, "$set": {"updated_at": datetime.now()}}
            )
        
        return result.modified_count > 0

    async def activate_tag(self, tag_id: str, active: bool = True) -> bool:
        """Activate or deactivate a tag"""
        try:
            result = await self.tags_collection.update_one(
                {"_id": ObjectId(tag_id)},
                {"$set": {"active": active, "updated_at": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error activating tag: {str(e)}")
            return False

    async def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag and remove it from all articles"""
        try:
            # First find all articles that have this tag
            tag_obj_id = ObjectId(tag_id)
            query = {"tag_ids": str(tag_obj_id)}
            articles = await self.articles_collection.find(query).to_list(length=1000)
            
            # Remove tag from all articles
            for article in articles:
                await self.articles_collection.update_one(
                    {"_id": article["_id"]},
                    {"$pull": {"tag_ids": str(tag_obj_id)}}
                )
            
            # Delete the tag
            result = await self.tags_collection.delete_one({"_id": tag_obj_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting tag: {str(e)}")
            return False

    async def update_tag(self, tag_id: str, update_data: dict) -> bool:
        """Update a tag with new data"""
        try:
            # Don't allow direct updates to article_count
            if "article_count" in update_data:
                del update_data["article_count"]
                
            # Add updated timestamp
            update_data["updated_at"] = datetime.now()
            
            result = await self.tags_collection.update_one(
                {"_id": ObjectId(tag_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating tag: {str(e)}")
            return False

    async def get_tag_stats(self) -> Dict[str, Any]:
        """
        Get statistics about tags.
        
        Returns:
            Dictionary with tag statistics
        """
        try:
            # Get total count
            total_count = await self.tags_collection.count_documents({})
            
            # Get count by original language
            languages_cursor = self.tags_collection.aggregate([
                {"$group": {"_id": "$original_language", "count": {"$sum": 1}}}
            ])
            languages = await languages_cursor.to_list(length=100)
            
            # Get count by active status
            active_cursor = self.tags_collection.aggregate([
                {"$group": {"_id": "$active", "count": {"$sum": 1}}}
            ])
            active = await active_cursor.to_list(length=100)
            
            # Get most used tags
            popular_cursor = self.tags_collection.find().sort("article_count", -1).limit(10)
            popular_tags = await popular_cursor.to_list(length=10)
            
            # Format results
            stats = {
                "total": total_count,
                "by_language": {item["_id"]: item["count"] for item in languages},
                "by_active": {str(item["_id"]): item["count"] for item in active},
                "popular_tags": [{
                    "id": str(tag["_id"]),
                    "name": tag["name"],
                    "count": tag["article_count"]
                } for tag in popular_tags]
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting tag stats: {str(e)}")
            return {"total": 0, "by_language": {}, "by_active": {}, "popular_tags": []}

# Create a singleton instance
db_service = DatabaseService()
