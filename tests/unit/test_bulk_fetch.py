"""
Unit tests for the bulk fetching process.
"""
import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from src.scrapers.agent import ContentAgent, ArticleContent, SearchResult, GroupedArticleContent, ContentSection
from src.scrapers.cache import ArticleCache

# Sample mock data
MOCK_SEARCH_RESULTS = [
    SearchResult(
        title="Test Article 1",
        url="https://example.com/article1",
        snippet="This is a test article about technology."
    ),
    SearchResult(
        title="Test Article 2",
        url="https://example.com/article2",
        snippet="This is another test article about technology."
    )
]

# Create content sections for articles
MOCK_CONTENT_SECTIONS = [
    ContentSection(
        type="text",
        content="This is the content of the test article.",
        order=1
    ),
    ContentSection(
        type="text",
        content="This is a second paragraph of the test article.",
        order=2
    )
]

MOCK_ARTICLE_CONTENT = ArticleContent(
    title="Test Article",
    url="https://example.com/article1",
    content=MOCK_CONTENT_SECTIONS,
    source="Example News",
    language="en",
    topics=["technology", "news"],
    date_published=datetime.now()
)

MOCK_GROUPED_ARTICLE = GroupedArticleContent(
    title="Grouped Test Article",
    language="en",
    content=MOCK_CONTENT_SECTIONS,
    topics=["technology", "news"],
    date_created=datetime.now(),
    difficulty_level="intermediate",
    source_articles=[MOCK_ARTICLE_CONTENT.url],
    key_vocabulary=[{"word": "test", "definition": "a sample definition"}]
)

@pytest.fixture
def mock_agent():
    """Create a mock ContentAgent."""
    agent = MagicMock(spec=ContentAgent)
    agent.find_articles = AsyncMock(return_value=[MOCK_ARTICLE_CONTENT])
    agent.group_and_rewrite_articles = AsyncMock(return_value=[MOCK_GROUPED_ARTICLE])
    agent.llm = AsyncMock()
    agent.llm.apredict = AsyncMock(return_value='[{"main_topic": "Technology", "article_ids": [0]}]')
    return agent

@pytest.fixture
def mock_cache():
    """Create a mock ArticleCache."""
    cache = MagicMock(spec=ArticleCache)
    cache.get = MagicMock(return_value=[])
    cache.set = MagicMock()
    cache.get_all_queries = MagicMock(return_value=[])
    cache.get_stats = MagicMock(return_value={"total_queries": 0, "total_articles": 0})
    return cache

@pytest.mark.asyncio
async def test_fetch_rss_articles(mock_agent):
    """Test the fetch_rss_articles function."""
    # Import the function directly from the module where it's defined
    from src.api.main import fetch_rss_articles

    # A simple log function for testing
    log_messages = []
    def log_fn(message):
        log_messages.append(message)
    
    # Test the function
    articles = await fetch_rss_articles(language="en", agent=mock_agent, log_fn=log_fn)
    
    # Verify results
    assert len(articles) > 0
    # Verify the agent was called correctly
    mock_agent.find_articles.assert_called()
    # Check log messages
    assert any("Found" in msg for msg in log_messages)

@pytest.mark.asyncio
async def test_group_articles_by_similarity(mock_agent):
    """Test the group_articles_by_similarity function."""
    # Import the function directly from the module
    from src.api.main import group_articles_by_similarity
    
    # A simple log function for testing
    log_messages = []
    def log_fn(message):
        log_messages.append(message)
    
    # Sample articles for testing
    articles = [MOCK_ARTICLE_CONTENT, MOCK_ARTICLE_CONTENT]
    
    # Test the function
    groups = await group_articles_by_similarity(articles, mock_agent, log_fn)
    
    # Verify results
    assert len(groups) > 0
    assert "main_topic" in groups[0]
    assert "articles" in groups[0]
    assert len(groups[0]["articles"]) > 0
    # Check that the LLM was called
    mock_agent.llm.apredict.assert_called_once()

@pytest.mark.asyncio
async def test_process_bulk_fetch(mock_agent, mock_cache):
    """Test the process_bulk_fetch function."""
    # Import the function directly from the module
    from src.api.main import process_bulk_fetch
    
    # Setup test operation
    operation_id = "test-operation-1"
    mock_operations = {
        operation_id: {
            "id": operation_id,
            "status": "running",
            "logs": [],
            "language": "en",
            "completed": False,
            "started_at": datetime.now().isoformat(),
            "articles_processed": 0,
            "articles_cached": 0
        }
    }
    
    # Patch the bulk_fetch_operations dictionary
    with patch("src.api.main.bulk_fetch_operations", mock_operations):
        # Run the process function
        await process_bulk_fetch(operation_id, "en", mock_agent, mock_cache)
        
        # Verify the operation was updated correctly
        operation = mock_operations[operation_id]
        assert operation["completed"] is True
        assert operation["status"] == "completed"
        assert "completed_at" in operation
        assert len(operation["logs"]) > 0
        
        # Verify agent and cache methods were called
        mock_agent.find_articles.assert_called()
        mock_agent.group_and_rewrite_articles.assert_called()
        mock_cache.set.assert_called()

@pytest.mark.asyncio
async def test_bulk_fetch_endpoint():
    """Test the bulk_fetch endpoint function."""
    # Import FastAPI test client
    from fastapi.testclient import TestClient
    from src.api.main import app
    
    # Create test client
    client = TestClient(app)
    
    # Test the endpoint
    response = client.post("/bulk-fetch", json={"language": "en"})
    
    # Verify response
    assert response.status_code == 200
    assert "id" in response.json()
    assert "message" in response.json()
    assert "Bulk fetch operation started" in response.json()["message"]

@pytest.mark.asyncio
async def test_bulk_fetch_status_endpoint():
    """Test the bulk_fetch_status endpoint function."""
    # Import FastAPI test client
    from fastapi.testclient import TestClient
    from src.api.main import app, bulk_fetch_operations
    
    # Create a test operation
    operation_id = "test-status-1"
    bulk_fetch_operations[operation_id] = {
        "id": operation_id,
        "status": "completed",
        "logs": ["Test log message"],
        "language": "en",
        "completed": True,
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "articles_processed": 5,
        "articles_cached": 3
    }
    
    # Create test client
    client = TestClient(app)
    
    # Test the endpoint
    response = client.get(f"/bulk-fetch-status/{operation_id}")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == operation_id
    assert data["status"] == "completed"
    assert len(data["logs"]) > 0
    assert data["completed"] is True
    
    # Test with invalid ID
    invalid_response = client.get("/bulk-fetch-status/nonexistent-id")
    assert invalid_response.status_code == 404
