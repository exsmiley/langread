"""
Unit tests for the database module.
"""
import pytest
import asyncio
from datetime import datetime
import os
from bson import ObjectId

from src.models.database import DatabaseService

# Use a test database
TEST_DB_URI = os.getenv("TEST_MONGODB_URI", "mongodb://localhost:27017/langread_test")

import pytest_asyncio

@pytest_asyncio.fixture
async def db_service():
    """Create a database service for testing."""
    service = DatabaseService(TEST_DB_URI)
    await service.connect()
    
    # Clear test collections before each test
    if service.db is not None:
        await service.db.articles.delete_many({})
        await service.db.vocabulary.delete_many({})
        await service.db.flashcards.delete_many({})
    
    yield service
    
    # Clean up after tests
    if service.db is not None:
        await service.db.articles.delete_many({})
        await service.db.vocabulary.delete_many({})
        await service.db.flashcards.delete_many({})
    
    await service.disconnect()

@pytest.mark.asyncio
async def test_connect():
    """Test database connection."""
    service = DatabaseService(TEST_DB_URI)
    connected = await service.connect()
    assert connected is True
    await service.disconnect()

@pytest.mark.asyncio
async def test_save_and_get_article(db_service):
    """Test saving and retrieving an article."""
    # Create test article
    article_data = {
        "title": "Test Article",
        "description": "This is a test article",
        "url": "https://example.com/test-article",
        "source": "Test Source",
        "language": "ko",
        "date_published": datetime.utcnow(),
        "date_fetched": datetime.utcnow(),
        "content": [
            {
                "type": "heading",
                "content": "Test Heading",
                "order": 0
            },
            {
                "type": "text",
                "content": "This is test content.",
                "order": 1
            }
        ],
        "topics": ["test", "sample"]
    }
    
    # Save article
    article_id = await db_service.save_article(article_data)
    assert article_id is not None
    
    # Get article
    article = await db_service.get_article(article_id)
    assert article is not None
    assert article["title"] == "Test Article"
    assert article["language"] == "ko"
    assert len(article["topics"]) == 2
    assert "test" in article["topics"]

@pytest.mark.asyncio
async def test_update_article(db_service):
    """Test updating an existing article."""
    # Create test article
    article_data = {
        "title": "Original Title",
        "description": "Original description",
        "url": "https://example.com/test-article",
        "source": "Test Source",
        "language": "ko",
        "date_published": datetime.utcnow(),
        "date_fetched": datetime.utcnow(),
        "content": [],
        "topics": ["original"]
    }
    
    # Save article
    article_id = await db_service.save_article(article_data)
    
    # Update article
    updated_data = {
        "title": "Updated Title",
        "description": "Updated description",
        "url": "https://example.com/test-article",  # Same URL to update
        "source": "Test Source",
        "language": "ko",
        "date_published": datetime.utcnow(),
        "date_fetched": datetime.utcnow(),
        "content": [],
        "topics": ["updated"]
    }
    
    updated_id = await db_service.save_article(updated_data)
    assert updated_id == article_id  # Should be the same ID
    
    # Get updated article
    article = await db_service.get_article(article_id)
    assert article["title"] == "Updated Title"
    assert article["description"] == "Updated description"
    assert "updated" in article["topics"]

@pytest.mark.asyncio
async def test_get_articles_with_filters(db_service):
    """Test getting articles with filters."""
    # Create test articles
    article1 = {
        "title": "Korean Article",
        "url": "https://example.com/article1",
        "source": "Source 1",
        "language": "ko",
        "date_published": datetime.utcnow(),
        "date_fetched": datetime.utcnow(),
        "content": [],
        "topics": ["food", "culture"]
    }
    
    article2 = {
        "title": "Japanese Article",
        "url": "https://example.com/article2",
        "source": "Source 2",
        "language": "ja",
        "date_published": datetime.utcnow(),
        "date_fetched": datetime.utcnow(),
        "content": [],
        "topics": ["technology", "business"]
    }
    
    article3 = {
        "title": "Another Korean Article",
        "url": "https://example.com/article3",
        "source": "Source 3",
        "language": "ko",
        "date_published": datetime.utcnow(),
        "date_fetched": datetime.utcnow(),
        "content": [],
        "topics": ["news", "politics"]
    }
    
    # Save articles
    await db_service.save_article(article1)
    await db_service.save_article(article2)
    await db_service.save_article(article3)
    
    # Test language filter
    ko_articles = await db_service.get_articles(language="ko")
    assert len(ko_articles) == 2
    
    ja_articles = await db_service.get_articles(language="ja")
    assert len(ja_articles) == 1
    
    # Test topic filter
    food_articles = await db_service.get_articles(topic="food")
    assert len(food_articles) == 1
    assert food_articles[0]["title"] == "Korean Article"
    
    # Test limit
    limited_articles = await db_service.get_articles(limit=1)
    assert len(limited_articles) == 1

@pytest.mark.asyncio
async def test_save_and_get_vocabulary(db_service):
    """Test saving and retrieving vocabulary."""
    # Create test vocabulary
    vocab_data = {
        "word": "테스트",
        "language": "ko",
        "part_of_speech": "noun",
        "translations": {"en": "test"},
        "definitions": [
            {
                "definition": "A procedure to evaluate something",
                "examples": ["이것은 테스트입니다."]
            }
        ],
        "article_references": ["article123"],
        "tags": ["common", "beginner"]
    }
    
    # Save vocabulary
    vocab_id = await db_service.save_vocabulary(vocab_data)
    assert vocab_id is not None
    
    # Get vocabulary
    vocab_items = await db_service.get_vocabulary(word="테스트", language="ko")
    assert len(vocab_items) == 1
    assert vocab_items[0]["word"] == "테스트"
    assert vocab_items[0]["translations"]["en"] == "test"
    assert "beginner" in vocab_items[0]["tags"]

@pytest.mark.asyncio
async def test_update_vocabulary(db_service):
    """Test updating vocabulary with new references."""
    # Create initial vocabulary
    vocab_data = {
        "word": "단어",
        "language": "ko",
        "part_of_speech": "noun",
        "translations": {"en": "word"},
        "article_references": ["article1"],
        "tags": ["common"]
    }
    
    # Save vocabulary
    vocab_id = await db_service.save_vocabulary(vocab_data)
    
    # Update with new article reference
    updated_data = {
        "word": "단어",
        "language": "ko",
        "part_of_speech": "noun",
        "translations": {"en": "word"},
        "article_references": ["article2"],
        "tags": ["intermediate"]
    }
    
    updated_id = await db_service.save_vocabulary(updated_data)
    assert updated_id == vocab_id
    
    # Get updated vocabulary
    vocab_items = await db_service.get_vocabulary(word="단어")
    assert len(vocab_items) == 1
    assert len(vocab_items[0]["article_references"]) == 2
    assert "article1" in vocab_items[0]["article_references"]
    assert "article2" in vocab_items[0]["article_references"]
    assert len(vocab_items[0]["tags"]) == 2
    assert "common" in vocab_items[0]["tags"]
    assert "intermediate" in vocab_items[0]["tags"]

@pytest.mark.asyncio
async def test_save_and_get_flashcards(db_service):
    """Test saving and retrieving flashcards."""
    # Create test flashcard
    flashcard_data = {
        "user_id": "user123",
        "word": "안녕하세요",
        "language": "ko",
        "front": "안녕하세요",
        "back": "Hello",
        "example": "안녕하세요, 반갑습니다.",
        "tags": ["greeting", "beginner"],
        "next_review": datetime.utcnow(),
        "ease_factor": 2.5,
        "interval": 1,
        "times_reviewed": 0
    }
    
    # Save flashcard
    flashcard_id = await db_service.save_flashcard(flashcard_data)
    assert flashcard_id is not None
    
    # Get flashcards
    flashcards = await db_service.get_flashcards(user_id="user123")
    assert len(flashcards) == 1
    assert flashcards[0]["word"] == "안녕하세요"
    assert flashcards[0]["front"] == "안녕하세요"
    assert flashcards[0]["back"] == "Hello"
    
    # Test tag filter
    beginner_cards = await db_service.get_flashcards(
        user_id="user123", 
        tags=["beginner"]
    )
    assert len(beginner_cards) == 1
    
    advanced_cards = await db_service.get_flashcards(
        user_id="user123", 
        tags=["advanced"]
    )
    assert len(advanced_cards) == 0
