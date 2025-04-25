"""
Database services for LangRead application.
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


# Create a singleton instance
db_service = DatabaseService()
