"""
Integration tests for the end-to-end article fetching and storage workflow.
Tests the interaction between the ContentAgent and DatabaseService.
"""
import pytest
import asyncio
import os
from datetime import datetime

from src.scrapers.agent import ContentAgent
from src.models.database import DatabaseService

# Use a test database
TEST_DB_URI = os.getenv("TEST_MONGODB_URI", "mongodb://localhost:27017/langread_test")

import pytest_asyncio

@pytest_asyncio.fixture
async def db_service():
    """Create a database service for testing."""
    service = DatabaseService(TEST_DB_URI)
    connected = await service.connect()
    if not connected:
        pytest.skip("Could not connect to test database")
    
    # Clear test collections before each test
    if service.db is not None:
        await service.db.articles.delete_many({})
        await service.db.vocabulary.delete_many({})
    
    yield service
    
    # Clean up after tests
    if service.db is not None:
        await service.db.articles.delete_many({})
        await service.db.vocabulary.delete_many({})
    
    await service.disconnect()

@pytest.fixture
def content_agent():
    """Create a content agent for testing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("No OpenAI API key available for testing")
    
    # Use a less expensive model for testing
    return ContentAgent(openai_api_key=api_key, model_name="gpt-3.5-turbo")

@pytest.mark.asyncio
async def test_fetch_and_store_article(db_service, content_agent):
    """
    Test fetching an article with the agent and storing it in the database.
    
    This is an integration test that tests the full workflow:
    1. Fetch an article with the ContentAgent
    2. Store it in the database
    3. Retrieve it from the database
    """
    # Skip if API key not available
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("No OpenAI API key available for testing")
    
    # Fetch an article with the agent
    articles = await content_agent.get_content(
        query="simple greeting",  # Use a simple topic to minimize tokens
        language="en",            # English for simplicity
        topic_type="general",
        max_sources=1             # Just get one article
    )
    
    assert len(articles) > 0
    article = articles[0]
    
    # Prepare article for database storage
    article_data = {
        "title": article.title,
        "url": article.url,
        "source": article.source,
        "language": article.language,
        "date_published": article.date_published or datetime.utcnow(),
        "date_fetched": datetime.utcnow(),
        "content": [
            {
                "type": section.type,
                "content": section.content,
                "caption": section.caption,
                "order": section.order
            }
            for section in article.content
        ],
        "topics": article.topics
    }
    
    # Store article in database
    article_id = await db_service.save_article(article_data)
    assert article_id is not None
    
    # Retrieve article from database
    stored_article = await db_service.get_article(article_id)
    assert stored_article is not None
    assert stored_article["title"] == article.title
    assert stored_article["language"] == article.language
    
    # Check if content was stored correctly
    assert len(stored_article["content"]) == len(article.content)
    
    # Print success message with article title
    print(f"Successfully processed article: {article.title}")

@pytest.mark.asyncio
async def test_article_language_filtering(db_service, content_agent):
    """Test fetching articles in different languages and filtering them."""
    # Skip if API key not available
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("No OpenAI API key available for testing")
    
    # Fetch articles in English
    en_articles = await content_agent.get_content(
        query="hello",
        language="en",
        topic_type="general",
        max_sources=1
    )
    
    # Store the English article
    for article in en_articles:
        article_data = {
            "title": article.title,
            "url": article.url,
            "source": article.source,
            "language": "en",  # Explicitly set to ensure correct filtering
            "date_published": article.date_published or datetime.utcnow(),
            "date_fetched": datetime.utcnow(),
            "content": [
                {
                    "type": section.type,
                    "content": section.content,
                    "caption": section.caption,
                    "order": section.order
                }
                for section in article.content
            ],
            "topics": article.topics
        }
        await db_service.save_article(article_data)
    
    # Create a "fake" Spanish article for testing
    # (This avoids making too many API calls)
    es_article_data = {
        "title": "Hola Mundo",
        "url": "https://example.com/hola",
        "source": "Test Source",
        "language": "es",
        "date_published": datetime.utcnow(),
        "date_fetched": datetime.utcnow(),
        "content": [
            {
                "type": "text",
                "content": "Este es un artículo de prueba en español.",
                "order": 0
            }
        ],
        "topics": ["test", "spanish"]
    }
    await db_service.save_article(es_article_data)
    
    # Test filtering by language
    en_results = await db_service.get_articles(language="en")
    es_results = await db_service.get_articles(language="es")
    
    assert len(en_results) > 0
    assert len(es_results) == 1
    
    # Verify correct filtering
    for article in en_results:
        assert article["language"] == "en"
    
    assert es_results[0]["language"] == "es"
    assert es_results[0]["title"] == "Hola Mundo"
