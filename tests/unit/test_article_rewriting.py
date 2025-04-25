"""
Unit tests for the article rewriting functionality.
"""
import pytest
import pytest_asyncio
import os
import asyncio
from datetime import datetime
from typing import List

from src.scrapers.agent import ContentAgent, ArticleContent, ContentSection

# Skip tests if no OpenAI API key
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OpenAI API key not available"
)

@pytest_asyncio.fixture
async def content_agent():
    """Create a content agent for testing."""
    agent = ContentAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))
    return agent

@pytest_asyncio.fixture
def sample_articles() -> List[ArticleContent]:
    """Sample articles for testing."""
    return [
        ArticleContent(
            title="Korean Cuisine: A Guide to Popular Dishes",
            url="https://example.com/article1",
            source="Korean Food Blog",
            language="en",
            date_published=datetime.now(),
            content=[
                ContentSection(
                    type="heading",
                    content="Introduction to Korean Food",
                    order=0
                ),
                ContentSection(
                    type="text",
                    content="Korean cuisine is known for its bold flavors, featuring fermented foods, rice, vegetables, and meats.",
                    order=1
                ),
                ContentSection(
                    type="heading",
                    content="Popular Dishes",
                    order=2
                ),
                ContentSection(
                    type="text",
                    content="Kimchi, bibimbap, and bulgogi are among the most well-known Korean dishes worldwide.",
                    order=3
                )
            ],
            topics=["food", "korean", "cuisine"]
        ),
        ArticleContent(
            title="Health Benefits of Korean Food",
            url="https://example.com/article2",
            source="Health & Nutrition Magazine",
            language="en",
            date_published=datetime.now(),
            content=[
                ContentSection(
                    type="heading",
                    content="Korean Diet and Health",
                    order=0
                ),
                ContentSection(
                    type="text",
                    content="The traditional Korean diet is considered one of the healthiest in the world due to its high vegetable content and fermented foods.",
                    order=1
                ),
                ContentSection(
                    type="heading",
                    content="Kimchi Benefits",
                    order=2
                ),
                ContentSection(
                    type="text",
                    content="Kimchi contains probiotics that support gut health and boost immunity.",
                    order=3
                )
            ],
            topics=["food", "health", "korean"]
        )
    ]

@pytest.mark.asyncio
async def test_group_and_rewrite_articles(content_agent, sample_articles):
    """Test grouping and rewriting articles."""
    rewritten = await content_agent.group_and_rewrite_articles(
        articles=sample_articles,
        language="en",
        target_difficulty="intermediate"
    )
    
    # Verify we get a single article back
    assert len(rewritten) == 1
    
    article = rewritten[0]
    
    # Verify basic article properties
    assert article.title, "Article should have a title"
    assert article.language == "en"
    assert article.source == "AI-generated from multiple sources"
    
    # Verify content structure
    assert len(article.content) > 0, "Article should have content sections"
    
    # Check for expected topics
    common_topics = ["food", "korean"]
    for topic in common_topics:
        assert topic in article.topics, f"Expected topic '{topic}' missing from rewritten article"

@pytest.mark.asyncio
async def test_get_content_with_rewriting(content_agent):
    """Test the get_content method with rewriting enabled."""
    articles = await content_agent.get_content(
        query="Korean cuisine", 
        language="en",
        topic_type="educational",
        max_sources=2,
        group_and_rewrite=True
    )
    
    # Verify we get a result
    assert len(articles) > 0
    
    # Verify article has expected properties for a rewritten article
    article = articles[0]
    assert article.title, "Article should have a title"
    assert "Korean" in article.title or "cuisine" in article.title.lower(), "Title should be relevant to the query"
    assert article.source == "AI-generated from multiple sources"
    
    # Verify content has reasonable structure
    assert len(article.content) > 0, "Article should have content"
    
    # Verify educational nature
    for section in article.content:
        if section.type == "text" and len(section.content) > 100:
            # Check for educational tone in longer sections
            assert any(term in section.content.lower() for term in ["learn", "cuisine", "food", "korean", "dishes", "traditional"]), \
                "Content should have educational terms related to Korean cuisine"
