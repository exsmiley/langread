import pytest
import os
import sys
from datetime import datetime
import asyncio
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import pytest_asyncio
from unittest.mock import patch, MagicMock

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.database import DatabaseService
from src.api.auth.utils import get_password_hash

# Test user data
test_user = {
    "email": "testuser_db@lingogi.com",
    "password": "securepassword123",
    "name": "Test DB User",
    "native_language": "en",
    "learning_language": "ko"
}

@pytest_asyncio.fixture
async def mock_db_service():
    """
    Create a mock database service with in-memory collections
    """
    # Create a mock client that doesn't actually connect to a MongoDB instance
    mock_client = MagicMock(spec=AsyncIOMotorClient)
    
    # Create a mock database
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    # Create a mock users_collection with an in-memory dictionary to store users
    mock_users_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_users_collection
    
    # In-memory storage for users
    users_data = {}
    
    # Mock insert_one
    async def mock_insert_one(document):
        user_id = str(ObjectId())
        document["_id"] = user_id
        users_data[user_id] = document
        result = MagicMock()
        result.inserted_id = user_id
        return result
    
    # Mock find_one
    async def mock_find_one(filter_dict, *args, **kwargs):
        if "_id" in filter_dict:
            user_id = filter_dict["_id"]
            return users_data.get(user_id)
        elif "email" in filter_dict:
            email = filter_dict["email"]
            for user in users_data.values():
                if user.get("email") == email:
                    return user
        return None
    
    # Mock update_one
    async def mock_update_one(filter_dict, update_dict, *args, **kwargs):
        result = MagicMock()
        user_found = False
        
        if "_id" in filter_dict:
            user_id = filter_dict["_id"]
            if user_id in users_data:
                user_found = True
                
                # Handle $set operation
                if "$set" in update_dict:
                    for key, value in update_dict["$set"].items():
                        users_data[user_id][key] = value
                
                # Handle $push operation for arrays
                if "$push" in update_dict:
                    for key, value in update_dict["$push"].items():
                        if key not in users_data[user_id]:
                            users_data[user_id][key] = []
                        users_data[user_id][key].append(value)
                
                # Handle $pull operation for arrays
                if "$pull" in update_dict:
                    for key, condition in update_dict["$pull"].items():
                        if key in users_data[user_id] and isinstance(users_data[user_id][key], list):
                            # Get the field and value to match against
                            field, value = next(iter(condition.items()))
                            users_data[user_id][key] = [
                                item for item in users_data[user_id][key]
                                if item.get(field) != value
                            ]
                
                result.modified_count = 1
        
        if not user_found:
            result.modified_count = 0
        
        return result
    
    # Set mocks
    mock_users_collection.insert_one = mock_insert_one
    mock_users_collection.find_one = mock_find_one
    mock_users_collection.update_one = mock_update_one
    
    # Create database service instance with mocked components
    db_service = DatabaseService()
    db_service.client = mock_client
    db_service.db = mock_db
    db_service.users_collection = mock_users_collection
    
    return db_service, users_data

class TestUserDatabaseFunctions:
    """Tests for user-related database functions"""
    
    @pytest.mark.asyncio
    async def test_create_and_find_user(self, mock_db_service):
        """Test creating a user and finding them by email"""
        db_service, users_data = mock_db_service
        
        # Prepare user data with hashed password
        user_data = test_user.copy()
        hashed_password = get_password_hash(user_data["password"])
        user_data["hashed_password"] = hashed_password
        del user_data["password"]
        
        # Create user
        result = await db_service.users_collection.insert_one(user_data)
        assert result.inserted_id is not None
        user_id = result.inserted_id
        
        # Find user by email
        found_user = await db_service.users_collection.find_one({"email": test_user["email"]})
        assert found_user is not None
        assert found_user["email"] == test_user["email"]
        assert found_user["name"] == test_user["name"]
        assert found_user["hashed_password"] == hashed_password
        
        # Find user by ID
        found_user_by_id = await db_service.users_collection.find_one({"_id": user_id})
        assert found_user_by_id is not None
        assert found_user_by_id["_id"] == user_id
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self, mock_db_service):
        """Test updating user profile information"""
        db_service, users_data = mock_db_service
        
        # Create a user first
        user_data = test_user.copy()
        hashed_password = get_password_hash(user_data["password"])
        user_data["hashed_password"] = hashed_password
        del user_data["password"]
        
        result = await db_service.users_collection.insert_one(user_data)
        user_id = result.inserted_id
        
        # Update user's name
        new_name = "Updated Test User"
        update_result = await db_service.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"name": new_name}}
        )
        
        assert update_result.modified_count == 1
        
        # Verify the update
        updated_user = await db_service.users_collection.find_one({"_id": user_id})
        assert updated_user["name"] == new_name
        
        # Update multiple fields
        updates = {
            "learning_language": "ja",
            "bio": "Language enthusiast"
        }
        
        update_result = await db_service.users_collection.update_one(
            {"_id": user_id},
            {"$set": updates}
        )
        
        assert update_result.modified_count == 1
        
        # Verify multiple updates
        updated_user = await db_service.users_collection.find_one({"_id": user_id})
        assert updated_user["learning_language"] == "ja"
        assert updated_user["bio"] == "Language enthusiast"
    
    @pytest.mark.asyncio
    async def test_nonexistent_user(self, mock_db_service):
        """Test trying to find or update a non-existent user"""
        db_service, users_data = mock_db_service
        
        # Try to find a non-existent user
        non_existent = await db_service.users_collection.find_one({
            "email": "nonexistent@lingogi.com"
        })
        assert non_existent is None
        
        non_existent_id = str(ObjectId())
        non_existent_by_id = await db_service.users_collection.find_one({
            "_id": non_existent_id
        })
        assert non_existent_by_id is None
        
        # Try to update a non-existent user
        update_result = await db_service.users_collection.update_one(
            {"_id": non_existent_id},
            {"$set": {"name": "This should not update anyone"}}
        )
        assert update_result.modified_count == 0


@pytest.mark.asyncio
class TestUserVocabulary:
    """Tests for user vocabulary-related database functions"""
    
    async def test_save_and_retrieve_vocabulary(self, mock_db_service):
        """Test saving words to a user's vocabulary and retrieving them"""
        db_service, users_data = mock_db_service
        
        # Create a user first
        user_data = test_user.copy()
        user_data["studied_words"] = []
        hashed_password = get_password_hash(user_data["password"])
        user_data["hashed_password"] = hashed_password
        del user_data["password"]
        
        result = await db_service.users_collection.insert_one(user_data)
        user_id = result.inserted_id
        
        # Save a vocabulary word
        vocab_word = {
            "word": "안녕하세요",
            "translation": "Hello",
            "context": "안녕하세요, 저는 미국 사람이에요.",
            "timestamp": datetime.utcnow()
        }
        
        await db_service.users_collection.update_one(
            {"_id": user_id},
            {"$push": {"studied_words": vocab_word}}
        )
        
        # Verify the word was saved
        updated_user = await db_service.users_collection.find_one({"_id": user_id})
        assert len(updated_user["studied_words"]) == 1
        assert updated_user["studied_words"][0]["word"] == "안녕하세요"
        assert updated_user["studied_words"][0]["translation"] == "Hello"
        
        # Add more words
        more_words = [
            {
                "word": "감사합니다",
                "translation": "Thank you",
                "context": "감사합니다, 정말 좋아요.",
                "timestamp": datetime.utcnow()
            },
            {
                "word": "미안합니다",
                "translation": "I'm sorry",
                "context": "미안합니다, 제가 실수했어요.",
                "timestamp": datetime.utcnow()
            }
        ]
        
        for word in more_words:
            await db_service.users_collection.update_one(
                {"_id": user_id},
                {"$push": {"studied_words": word}}
            )
        
        # Verify all words were saved
        updated_user = await db_service.users_collection.find_one({"_id": user_id})
        assert len(updated_user["studied_words"]) == 3
        
        # Verify words can be removed
        await db_service.users_collection.update_one(
            {"_id": user_id},
            {"$pull": {"studied_words": {"word": "안녕하세요"}}}
        )
        
        updated_user = await db_service.users_collection.find_one({"_id": user_id})
        assert len(updated_user["studied_words"]) == 2
        assert all(word["word"] != "안녕하세요" for word in updated_user["studied_words"])


@pytest.mark.asyncio
class TestUserArticles:
    """Tests for user saved articles database functions"""
    
    async def test_save_and_retrieve_articles(self, mock_db_service):
        """Test saving articles to a user's library and retrieving them"""
        db_service, users_data = mock_db_service
        
        # Create a user first
        user_data = test_user.copy()
        user_data["saved_articles"] = []
        hashed_password = get_password_hash(user_data["password"])
        user_data["hashed_password"] = hashed_password
        del user_data["password"]
        
        result = await db_service.users_collection.insert_one(user_data)
        user_id = result.inserted_id
        
        # Save an article
        article = {
            "article_id": str(ObjectId()),
            "title": "한국의 역사",
            "saved_date": datetime.utcnow(),
            "language": "ko",
            "difficulty": "intermediate"
        }
        
        await db_service.users_collection.update_one(
            {"_id": user_id},
            {"$push": {"saved_articles": article}}
        )
        
        # Verify the article was saved
        updated_user = await db_service.users_collection.find_one({"_id": user_id})
        assert len(updated_user["saved_articles"]) == 1
        assert updated_user["saved_articles"][0]["title"] == "한국의 역사"
        
        # Add more articles
        more_articles = [
            {
                "article_id": str(ObjectId()),
                "title": "한국 음식 소개",
                "saved_date": datetime.utcnow(),
                "language": "ko",
                "difficulty": "beginner"
            },
            {
                "article_id": str(ObjectId()),
                "title": "서울의 대중교통",
                "saved_date": datetime.utcnow(),
                "language": "ko",
                "difficulty": "advanced"
            }
        ]
        
        for article in more_articles:
            await db_service.users_collection.update_one(
                {"_id": user_id},
                {"$push": {"saved_articles": article}}
            )
        
        # Verify all articles were saved
        updated_user = await db_service.users_collection.find_one({"_id": user_id})
        assert len(updated_user["saved_articles"]) == 3
        
        # Verify articles can be removed
        first_article_id = updated_user["saved_articles"][0]["article_id"]
        await db_service.users_collection.update_one(
            {"_id": user_id},
            {"$pull": {"saved_articles": {"article_id": first_article_id}}}
        )
        
        updated_user = await db_service.users_collection.find_one({"_id": user_id})
        assert len(updated_user["saved_articles"]) == 2
        assert all(article["article_id"] != first_article_id for article in updated_user["saved_articles"])
