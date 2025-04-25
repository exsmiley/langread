from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ArticleContent(BaseModel):
    """Represents a section of article content (text or image)"""
    type: str = Field(..., description="Type of content: 'text', 'image', 'heading', etc.")
    content: str = Field(..., description="The actual content text or image URL")
    caption: Optional[str] = None
    order: int = Field(..., description="Order of the content in the article")


class Article(BaseModel):
    """Represents a full article with metadata and content"""
    id: Optional[str] = Field(None, description="Unique identifier for the article")
    title: str
    description: Optional[str] = None
    url: str = Field(..., description="Original source URL")
    source: str = Field(..., description="Name of the source website")
    language: str = Field("ko", description="Language code (default: Korean)")
    date_published: datetime
    date_fetched: datetime = Field(default_factory=datetime.utcnow)
    content: List[ArticleContent] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123456",
                "title": "샘플 뉴스 기사",
                "description": "이것은 샘플 뉴스 기사입니다.",
                "url": "https://example.com/news/123456",
                "source": "Sample News",
                "language": "ko",
                "date_published": "2025-04-23T00:00:00Z",
                "date_fetched": "2025-04-23T01:30:00Z",
                "content": [
                    {
                        "type": "heading",
                        "content": "뉴스 헤드라인",
                        "order": 0
                    },
                    {
                        "type": "text",
                        "content": "뉴스 기사 내용입니다. 한국어로 작성되어 있습니다.",
                        "order": 1
                    },
                    {
                        "type": "image",
                        "content": "https://example.com/images/news_image.jpg",
                        "caption": "뉴스 이미지 캡션",
                        "order": 2
                    }
                ],
                "topics": ["정치", "사회"]
            }
        }


class ArticleList(BaseModel):
    """Response model for list of articles"""
    date: str
    total: int
    articles: List[Article]
