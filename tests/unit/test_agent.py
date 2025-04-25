"""
Unit tests for the agent-based content fetcher.
"""
import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.scrapers.agent import ContentAgent, ArticleContent, SearchResult

@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response."""
    class MockResponse:
        class Choice:
            class Message:
                def __init__(self, content):
                    self.content = content
            
            def __init__(self, content):
                self.message = self.Message(content)
        
        def __init__(self, content):
            self.choices = [self.Choice(content)]
    
    return MockResponse("Hello!")

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test that the ContentAgent initializes properly."""
    # Skip if no API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("No OpenAI API key available for testing")
    
    # Initialize with a less expensive model for testing
    agent = ContentAgent(openai_api_key=api_key, model_name="gpt-3.5-turbo")
    
    # Check that components are initialized
    assert agent.api_key == api_key
    assert agent.llm is not None
    assert agent.tools is not None
    assert agent.agent is not None

@pytest.mark.asyncio
async def test_search_web_tool():
    """Test the search_web tool function."""
    # Skip if no API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("No OpenAI API key available for testing")
    
    agent = ContentAgent(openai_api_key=api_key, model_name="gpt-3.5-turbo")
    
    # Get the search_web function from the tools
    search_web_func = None
    for tool in agent.tools:
        if tool.name == "search_web":
            search_web_func = tool.func
            break
    
    assert search_web_func is not None
    
    # Test the function (it should return mock data in our implementation)
    results = search_web_func("test query", "en")
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert isinstance(results[0], SearchResult)
    assert hasattr(results[0], "title")
    assert hasattr(results[0], "url")
    assert hasattr(results[0], "snippet")

@pytest.mark.asyncio
async def test_extract_content_tool():
    """Test the extract_content tool function."""
    # Skip if no API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("No OpenAI API key available for testing")
    
    agent = ContentAgent(openai_api_key=api_key, model_name="gpt-3.5-turbo")
    
    # Get the extract_content function from the tools
    extract_content_func = None
    for tool in agent.tools:
        if tool.name == "extract_content":
            extract_content_func = tool.func
            break
    
    assert extract_content_func is not None
    
    # Test the function with a real URL
    # Using BBC News as it's stable and likely to be accessible
    result = extract_content_func("https://www.bbc.com/news")
    
    assert isinstance(result, ArticleContent)
    assert hasattr(result, "title")
    assert hasattr(result, "url")
    assert hasattr(result, "content")
    assert len(result.content) > 0

@pytest.mark.asyncio
@patch("src.scrapers.agent.ChatOpenAI")
async def test_get_content(mock_chat_openai, mock_openai_response):
    """Test the get_content method with mocked LLM."""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.ainvoke.return_value = {"output": "Mocked content from LLM"}
    mock_chat_openai.return_value = mock_instance
    
    # Create agent with mock
    agent = ContentAgent(openai_api_key="mock_key")
    
    # Call the method
    results = await agent.get_content(
        query="Korean food", 
        language="ko", 
        topic_type="news",
        max_sources=1
    )
    
    # Verify results
    assert isinstance(results, list)
    assert len(results) > 0
    assert isinstance(results[0], ArticleContent)
    assert "Korean food" in results[0].title

@pytest.mark.asyncio
async def test_real_get_content_simple():
    """
    Test the get_content method with a real API call.
    This is an integration test that makes a real API call,
    but with minimal content for cost reasons.
    """
    # Skip if no API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("No OpenAI API key available for testing")
    
    # Initialize with a less expensive model for testing
    agent = ContentAgent(openai_api_key=api_key, model_name="gpt-3.5-turbo")
    
    # Test with a simple, minimal query to reduce token usage
    results = await agent.get_content(
        query="hello",  # Very simple query 
        language="en",   # English for simplicity
        topic_type="general",
        max_sources=1   # Just one source
    )
    
    # Basic validation of results
    assert isinstance(results, list)
    assert len(results) > 0
    assert isinstance(results[0], ArticleContent)
