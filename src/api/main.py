from typing import List, Dict, Optional, Union, Literal, Any
from fastapi import FastAPI, Query, BackgroundTasks, HTTPException, Depends, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from bson import ObjectId
from loguru import logger
from datetime import datetime
import json
import re
import nltk
import numpy as np
from nltk.tokenize import word_tokenize
import requests
from urllib.parse import urlparse
import feedparser
from newspaper import Article as NewspaperArticle, Config as NewspaperConfig
from bs4 import BeautifulSoup
import uvicorn
import os
import time
import uuid
import asyncio
import hashlib
import sys

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import tag generator
from src.utils.tag_generator import tag_generator

# Import tag routes
from src.api.tag_routes import router as tag_router, get_tag_stats
from pathlib import Path

# Import custom JSON encoder for MongoDB ObjectId
from src.api.utils.encoders import MongoJSONEncoder, jsonable_encoder_with_objectid

# Add the necessary directories to sys.path

# Add both the src directory and the project root to sys.path
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(src_dir)  # Add src directory
sys.path.append(os.path.dirname(src_dir))  # Add project root

# Now import the database service
from models.database import DatabaseService

# Import ContentAgent and ArticleCache
try:
    from src.scrapers.agent import ContentAgent, ArticleContent, GroupedArticleContent, ContentSection
    from src.scrapers.cache import ArticleCache
except ImportError:
    from scrapers.agent import ContentAgent, ArticleContent, GroupedArticleContent, ContentSection
    from scrapers.cache import ArticleCache

# Configure logging with loguru
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("langread.log", rotation="10 MB", level="INFO")

# Initialize the article cache
article_cache = ArticleCache()

# Initialize the FastAPI app
app = FastAPI(title="LangRead API", 
             description="API for LangRead language learning application",
             version="0.1.0")

# Add custom encoder for MongoDB ObjectId
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# Add custom JSON response class
class CustomJSONResponse(JSONResponse):
    def render(self, content):
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=MongoJSONEncoder,
        ).encode("utf-8")

app.json_response_class = CustomJSONResponse

# Initialize the database service
db_service = DatabaseService()

# Connect to MongoDB when the application starts
@app.on_event("startup")
async def startup():
    await db_service.connect()

# Disconnect from MongoDB when the application shuts down
@app.on_event("shutdown")
async def shutdown():
    await db_service.disconnect()

# Dependency to get the database service
async def get_database_service():
    return db_service

# Global ContentAgent instance (singleton)
content_agent = None

# Dependency for getting the content agent
async def get_content_agent():
    # Use a singleton pattern to avoid creating multiple instances
    global content_agent
    if content_agent is None:
        api_key = os.getenv("OPENAI_API_KEY")
        content_agent = ContentAgent(openai_api_key=api_key)
        logger.info("ContentAgent singleton initialized")
    return content_agent

# Dependency for getting the article cache
async def get_article_cache():
    return article_cache

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite development server
        "http://127.0.0.1:5173",
        "http://localhost:8080",  # Alternative frontend port
        "http://127.0.0.1:8080", 
        "http://127.0.0.1:63614",  # Preview ports
        "*"  # Allow any origin for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the LangRead API",
        "status": "online",
        "documentation": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Content Request Model
class ContentRequest(BaseModel):
    query: str
    language: str = "ko"  # Default to Korean as per initial requirements
    topic_type: str = "news"  # Default to news
    max_sources: int = 5  # Default to 5 sources
    group_and_rewrite: bool = False  # Whether to group and rewrite articles

# Rewrite Request Model
class RewriteRequest(BaseModel):
    article_ids: Optional[List[str]] = None  # IDs of articles to rewrite, if None use all recent for query
    query: Optional[str] = None  # If article_ids not provided, use this query to find articles
    language: str = "ko"  # Target language for the rewritten content
    target_difficulty: Literal["beginner", "intermediate", "advanced"] = "intermediate"  # Difficulty level
    max_sources: int = 5  # Maximum number of sources to use

# Simple Article List Model
class SimpleArticleRequest(BaseModel):
    language: str = "ko"  # Default to Korean
    difficulty: str = "intermediate"  # Default difficulty level
    query: str = ""  # Optional search query
    tag_ids: Optional[List[str]] = None  # Optional tag_ids to filter by
    max_sources: int = 10  # Default max sources
    group_and_rewrite: bool = True  # Whether to group articles

# Endpoint to get a quiz for an article
@app.get("/api/quizzes/{article_id}")
async def get_quiz_by_article_id(
    article_id: str,
    db: DatabaseService = Depends(get_database_service)
):
    """Get a quiz for a specific article"""
    try:
        # Find the article first to ensure it exists
        article = await db.articles_collection.find_one({"_id": article_id})
        
        if not article:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Article with ID {article_id} not found"}
            )
        
        # For now, return a mock quiz - in a real app, this would generate or retrieve a stored quiz
        mock_quiz = {
            "questions": [
                {
                    "id": "q1",
                    "question": "이 글의 주요 주제는 무엇인가요?",
                    "options": [
                        "경제 발전",
                        "기술 혁신",
                        "정치 변화",
                        "환경 문제"
                    ],
                    "correct_answer": "기술 혁신",
                    "evidence": "글의 전체적인 내용이 기술 혁신에 중점을 두고 있습니다."
                },
                {
                    "id": "q2",
                    "question": "기사에서 언급된 주요 단체나 기관은?",
                    "options": [
                        "삼성전자",
                        "현대자동차",
                        "한국과학기술원",
                        "네이버"
                    ],
                    "correct_answer": "한국과학기술원",
                    "evidence": "기사 내용 중 한국과학기술원의 연구 결과가 인용되었습니다."
                },
                {
                    "id": "q3",
                    "question": "이 기사는 어떤 관점에서 쓰여졌나요?",
                    "options": [
                        "비판적 관점",
                        "중립적 관점",
                        "긍정적 관점",
                        "역사적 관점"
                    ],
                    "correct_answer": "중립적 관점",
                    "evidence": "기사는 다양한 견해를 균형있게 다루고 있습니다."
                }
            ]
        }
        
        return mock_quiz
        
    except Exception as e:
        logger.error(f"Error getting quiz for article {article_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error retrieving quiz: {str(e)}"}
        )

# Endpoint to get a single article by ID
@app.get("/api/articles/{article_id}")
async def get_article_by_id(
    article_id: str,
    db: DatabaseService = Depends(get_database_service)
):
    """Get a single article by its ID"""
    try:
        # Find the article by ID
        article = await db.articles_collection.find_one({"_id": article_id})
        
        if not article:
            # If article not found, return 404
            return JSONResponse(
                status_code=404,
                content={"detail": f"Article with ID {article_id} not found"}
            )
        
        # Convert article to dict for serialization
        article_dict = dict(article)
        
        # Convert ObjectId fields to strings
        if "_id" in article_dict:
            article_dict["_id"] = str(article_dict["_id"])
            
        # Convert tag_ids to strings
        if "tag_ids" in article_dict and article_dict["tag_ids"]:
            article_dict["tag_ids"] = [str(tag_id) for tag_id in article_dict["tag_ids"]]
            
        return article_dict
        
    except Exception as e:
        logger.error(f"Error getting article {article_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error retrieving article: {str(e)}"}
        )

# Simple articles endpoint that returns articles directly from database
@app.post("/api/articles-simple")
async def get_articles_simple(
    request: SimpleArticleRequest,
    db: DatabaseService = Depends(get_database_service)
):
    """Get articles directly from the database with simple filtering"""
    try:
        # Build the query filter
        query_filter = {"language": request.language}
        
        # Add difficulty filter if specified
        if request.difficulty:
            query_filter["difficulty"] = request.difficulty
        
        # Add tag_ids filter if specified
        if request.tag_ids and len(request.tag_ids) > 0:
            # Convert string IDs to ObjectId
            object_ids = [ObjectId(tag_id) for tag_id in request.tag_ids if tag_id]
            if object_ids:
                query_filter["tag_ids"] = {"$in": object_ids}
                
        # Fetch articles from database
        cursor = db.articles_collection.find(query_filter).limit(50)
        articles = await cursor.to_list(length=50)
        
        # Convert ObjectId to strings for JSON serialization
        serialized_articles = []
        for article in articles:
            article_dict = dict(article)
            
            # Convert _id to string
            if "_id" in article_dict:
                article_dict["_id"] = str(article_dict["_id"])
                
            # Convert tag_ids to strings
            if "tag_ids" in article_dict and article_dict["tag_ids"]:
                article_dict["tag_ids"] = [str(tag_id) for tag_id in article_dict["tag_ids"]]
                
            serialized_articles.append(article_dict)
            
        # Return the serialized articles
        return {"articles": serialized_articles, "count": len(serialized_articles)}
        
    except Exception as e:
        logger.error(f"Error in get_articles_simple: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error retrieving articles: {str(e)}"}
        )

# Articles endpoint
@app.post("/articles")
async def get_articles(
    content_request: ContentRequest,
    background_tasks: BackgroundTasks,
    agent: ContentAgent = Depends(get_content_agent),
    cache: ArticleCache = Depends(get_article_cache),
    force_refresh: bool = False
):
    """
    Get articles based on query, language, and content type.
    This endpoint uses an LLM-powered agent to search for and extract content.
    If articles for the requested query and date exist in the cache, they will be returned.
    Otherwise, the agent will search for and extract new articles.
    
    All articles are grouped by topic and rewritten as a cohesive article for language learning.
    """
    query = content_request.query
    language = content_request.language
    logs = []
    
    try:
        # Check cache first unless force_refresh is True
        if not force_refresh:
            cached_articles = cache.get(query, language)
            if cached_articles:
                logger.info(f"Returning cached articles for query: {query}, language: {language}")
                logs.append(f"[CACHE HIT] Using cached articles for: {query}")
                
                return {
                    "query": query,
                    "language": language,
                    "topic_type": content_request.topic_type,
                    "grouped": True,
                    "articles": cached_articles,
                    "source": "cache",
                    "logs": logs,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Log the fetch operation
        logs.append(f"[FETCH] Searching for articles about: {query}")
        logs.append(f"[FETCH] Language: {language}")
        
        # Always group and rewrite articles
        start_time = datetime.now()
        articles = await agent.get_content(
            query=query,
            language=language,
            topic_type=content_request.topic_type,
            max_sources=content_request.max_sources,
            group_and_rewrite=True  # Always group and rewrite
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        logs.append(f"[FETCH] Found {len(articles)} articles in {processing_time:.2f} seconds")
        
        # Cache the articles for future requests
        cache.set(query, language, articles, logs)
        logs.append(f"[CACHE] Saved articles to cache")
        
        # Return the articles with logs
        return {
            "query": query,
            "language": language,
            "topic_type": content_request.topic_type,
            "grouped": True,
            "articles": articles,
            "source": "fresh",
            "logs": logs,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        error_msg = f"Error getting articles: {str(e)}"
        logs.append(f"[ERROR] {error_msg}")
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))

# Rewrite articles endpoint
@app.post("/rewrite-articles")
async def rewrite_articles(
    rewrite_request: RewriteRequest,
    agent: ContentAgent = Depends(get_content_agent)
):
    """
    Rewrite articles for language learning at a specific difficulty level.
    
    This endpoint groups multiple articles on the same topic and rewrites them into
    a single coherent article at the specified difficulty level with educational
    features like key vocabulary lists.
    """
    try:
        # TODO: If article_ids are provided, retrieve them from the database
        # For now, if no article_ids, just search for new articles
        if not rewrite_request.article_ids and not rewrite_request.query:
            raise HTTPException(
                status_code=400, 
                detail="Either article_ids or query must be provided"
            )
        
        articles = []
        
        # If article_ids not provided, search for articles with the query
        if not rewrite_request.article_ids and rewrite_request.query:
            raw_articles = await agent.get_content(
                query=rewrite_request.query,
                language=rewrite_request.language,
                max_sources=rewrite_request.max_sources,
                group_and_rewrite=False  # We'll do the rewriting in the next step
            )
            
            if not raw_articles:
                return {
                    "message": "No articles found for the given query",
                    "articles": []
                }
                
            articles = raw_articles
        else:
            # TODO: Fetch articles by IDs from database
            # For now, we'll return an error since DB isn't implemented yet
            raise HTTPException(
                status_code=501,
                detail="Fetching articles by ID is not yet implemented"
            )
        
        # Rewrite the articles
        rewritten_articles = await agent.group_and_rewrite_articles(
            articles=articles,
            language=rewrite_request.language,
            target_difficulty=rewrite_request.target_difficulty
        )
        
        # TODO: Store the rewritten article in the database
        
        return {
            "original_count": len(articles),
            "language": rewrite_request.language,
            "difficulty": rewrite_request.target_difficulty,
            "rewritten_articles": rewritten_articles,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error rewriting articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Translation endpoint
@app.post("/translate")
async def translate_text(
    text: str = Query(..., description="Text to translate"),
    source_lang: str = Query(..., description="Source language code"),
    target_lang: str = Query("en", description="Target language code"),
    agent: ContentAgent = Depends(get_content_agent)
):
    """
    Translate text from source language to target language using the LLM agent.
    """
    try:
        # TODO: Implement translation using the agent or a dedicated translation service
        # For now, return a mock response
        return {
            "original_text": text,
            "translated_text": f"[Translated {source_lang} to {target_lang}]: {text}",
            "source_language": source_lang,
            "target_language": target_lang
        }
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Vocabulary translation model
class VocabularyTranslationRequest(BaseModel):
    text: str = Field(..., description="Word or phrase to translate")
    context: str = Field("", description="Surrounding context where the word appears")
    source_lang: str = Field(..., description="Source language code (e.g., 'ko')")
    target_lang: str = Field("en", description="Target language code (e.g., 'en')")
    definition_lang: str = Field(None, description="Language for definitions and examples (defaults to target_lang if not provided)")


class VocabularyTranslationResponse(BaseModel):
    word: str = Field(..., description="The original word or phrase")
    translation: str = Field(..., description="The translated word or phrase")
    part_of_speech: str = Field(..., description="Part of speech (noun, verb, etc.)")
    definition: str = Field(..., description="Definition in the target language")
    examples: List[str] = Field(default_factory=list, description="Example sentences in the source language")


# Simple in-memory cache for vocabulary translations
# In a production environment, consider using Redis or another distributed cache
vocabulary_cache = {}


# Context-aware vocabulary translation endpoint
@app.post("/api/vocabulary/context-aware-translate", response_model=VocabularyTranslationResponse)
async def translate_vocabulary_context_aware(
    request: VocabularyTranslationRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseService = Depends(get_database_service)
):
    """
    Translate a word or phrase with context awareness for language learning.
    Returns detailed information including part of speech, definition, and example usage.
    """    
    # Create a cache key based on all relevant parameters
    cache_key = f"{request.text}:{request.context[:50]}:{request.source_lang}:{request.target_lang}"
    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
    
    # Check if we have this translation in our cache
    if cache_key in vocabulary_cache:
        logger.info(f"Vocabulary cache hit for: {request.text}")
        return vocabulary_cache[cache_key]
    
    # Check if we have it in the database (for persistent caching)
    try:
        # TODO: Implement database caching if needed
        pass
    except Exception as e:
        logger.warning(f"Database check for translation failed: {str(e)}")
    
    # Not in cache, need to generate a new translation
    try:
        # Get OPENAI_API_KEY from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        # Get language name from code for better prompt
        language_names = {
            "en": "English",
            "fr": "French",
            "es": "Spanish",
            "de": "German",
            "ja": "Japanese",
            "zh": "Chinese",
            "ko": "Korean"
        }
        source_lang_name = language_names.get(request.source_lang, request.source_lang)
        target_lang_name = language_names.get(request.target_lang, request.target_lang)
        
        # Determine the language for definitions and examples
        definition_lang = request.definition_lang if request.definition_lang else request.target_lang
        definition_lang_name = language_names.get(definition_lang, definition_lang)
        
        # Import the OpenAI client only when needed
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        # Prepare the prompt for OpenAI
        prompt = f"""
        You are a professional translator with expertise in {source_lang_name} to {target_lang_name} translation.
        
        I need you to translate the {source_lang_name} word or phrase: "{request.text}"
        {f'It appears in this context: "{request.context}"' if request.context else ''}
        
        Provide your response in the following JSON format only:
        {{"word": "{request.text}",
         "translation": "[translation in {target_lang_name}]",
         "part_of_speech": "[noun/verb/adjective/adverb/etc.]",
         "definition": "[brief definition in {definition_lang_name}]",
         "examples": ["[example sentence in {source_lang_name}]"]}}  
        
        Guidelines:
        1. Provide the base, non-conjugated form for verbs if applicable
        2. Provide a clear, concise definition IN {definition_lang_name}
        3. If the text is a phrase or sentence, translate it appropriately
        4. Create one or two SIMPLE example sentences that use the word/phrase naturally
        5. Example sentences should be short, clear and helpful for language learners - NOT excerpts from the provided context
        6. Use beginner to intermediate level vocabulary and grammar in your examples
        7. RESPOND ONLY WITH THE JSON, no additional text
        """

        # Make the request to OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Use an appropriate model 
            messages=[
                {"role": "system", "content": "You are a professional translator API that only responds with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent responses
            response_format={"type": "json_object"}
        )

        # Extract the response
        response_content = response.choices[0].message.content
        translation_data = json.loads(response_content)
        
        # Create the response
        translation_response = VocabularyTranslationResponse(
            word=translation_data["word"],
            translation=translation_data["translation"],
            part_of_speech=translation_data["part_of_speech"],
            definition=translation_data["definition"],
            examples=translation_data["examples"]
        )
        
        # Cache the result
        vocabulary_cache[cache_key] = translation_response
        
        # In the background, store this translation in the database for persistent caching
        # background_tasks.add_task(store_translation_in_db, request, translation_response, db)
        
        return translation_response
        
    except Exception as e:
        logger.error(f"Error translating vocabulary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

# Quiz generation endpoint
@app.post("/generate-quiz")
async def generate_quiz(
    article_id: str = Query(..., description="ID of the article to generate quiz for"),
    quiz_type: str = Query("multiple_choice", description="Type of quiz to generate (multiple_choice or short_answer)"),
    num_questions: int = Query(5, description="Number of questions to generate"),
    agent: ContentAgent = Depends(get_content_agent)
):
    """
    Generate a quiz for an article using the LLM agent.
    """
    try:
        # TODO: Retrieve the article from the database
        # TODO: Generate a quiz using the agent
        
        # For now, return a mock response
        return {
            "article_id": article_id,
            "quiz_type": quiz_type,
            "num_questions": num_questions,
            "questions": [
                {
                    "id": "q1",
                    "question": "Sample question 1?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "evidence": "This comes from paragraph 2 of the article."
                },
                {
                    "id": "q2",
                    "question": "Sample question 2?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option C",
                    "evidence": "This is explained in the third section."
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# User-facing read-only endpoint for cached articles
@app.post("/cached-articles")
async def get_cached_articles(
    content_request: ContentRequest,
    cache: ArticleCache = Depends(get_article_cache)
):
    """Get articles from cache only - for user interface"""
    try:
        query = content_request.query
        language = content_request.language
        
        # Look in cache only
        cached_articles = cache.get(query, language)
        
        if cached_articles:
            logger.info(f"Returning cached articles for query: {query}, language: {language}")
            
            return {
                "query": query,
                "language": language,
                "topic_type": content_request.topic_type,
                "grouped": True,
                "articles": cached_articles,
                "source": "cache",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # No cached articles found
            return {
                "query": query,
                "language": language,
                "articles": [],
                "source": "cache",
                "message": "No cached articles found. Please check the admin panel to add content.",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        error_msg = f"Error getting cached articles: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# MongoDB article endpoints
@app.get("/articles/{content_type}")
async def get_articles(
    content_type: str, 
    limit: int = 20, 
    language: Optional[str] = None,
    bulk_fetch_id: Optional[str] = None,
    source: Optional[str] = None,
    db: DatabaseService = Depends(get_database_service)
):
    """Get articles from MongoDB by content type (raw, group, rewritten) with optional filters"""
    try:
        # Validate content type
        valid_types = ["raw", "group", "rewritten"]
        if content_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid content type. Must be one of: {', '.join(valid_types)}")
        
        # Build query with filters
        query = {"content_type": content_type}
        
        # Add optional filters
        if language:
            query["language"] = language
        if bulk_fetch_id:
            query["bulk_fetch_id"] = bulk_fetch_id
        if source:
            query["source"] = source
        
        # Find articles with the specified content type and filters
        # Sort by most recent first
        articles = await db.articles_collection.find(query).sort("date_created", -1).limit(limit).to_list(limit)
        
        # Convert MongoDB documents to JSON-serializable format
        result = []
        for article in articles:
            # Convert ObjectId to string for JSON serialization
            if '_id' in article:
                article['_id'] = str(article['_id'])
                
            # Convert dates to ISO format strings
            for field in ['date_created', 'date_published']:
                if field in article and article[field]:
                    article[field] = article[field].isoformat()
                    
            result.append(article)
            
        return result
    except Exception as e:
        logger.error(f"Error retrieving articles from MongoDB: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving articles: {str(e)}")

# Cache management endpoints
@app.get("/cache/stats")
async def get_cache_stats(cache: ArticleCache = Depends(get_article_cache)):
    """Get cache statistics"""
    return cache.get_stats()

@app.get("/cache/queries")
async def get_cached_queries(cache: ArticleCache = Depends(get_article_cache)):
    """Get list of cached queries"""
    return cache.get_all_queries()

@app.post("/cache/clear")
async def clear_cache(cache: ArticleCache = Depends(get_article_cache)):
    """Clear the entire cache"""
    cache.clear()
    return {"message": "Cache cleared"}

# Clear the MongoDB articles collection
@app.post("/db/clear-articles")
async def clear_articles(db: DatabaseService = Depends(get_database_service)):
    """Clear all articles from MongoDB collection"""
    result = await db.articles_collection.delete_many({})  # Empty filter matches all documents
    count = result.deleted_count
    return {"message": f"Cleared {count} articles from the database"}

# In-memory storage for bulk fetch operations
bulk_fetch_operations = {}

class BulkFetchRequest(BaseModel):
    """Request model for bulk fetch operation"""
    language: str = "all"  # all, ko, or en, or any supported language code
    fetch_only: bool = False  # If True, only perform fetching step without aggregation/rewriting steps
    process_steps: List[str] = Field(default_factory=lambda: ["fetch", "aggregate", "rewrite"])  # Steps to execute

# Bulk fetch endpoint - fetches all RSS content
@app.post("/bulk-fetch")
async def bulk_fetch(request: BulkFetchRequest, 
              background_tasks: BackgroundTasks,
              agent: ContentAgent = Depends(get_content_agent),
              cache: ArticleCache = Depends(get_article_cache),
              db: DatabaseService = Depends(get_database_service)):
    """Start a bulk fetch operation to populate the cache"""
    # Generate a unique ID for this operation
    operation_id = f"bulk-fetch-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(bulk_fetch_operations) + 1}"
    
    # Initialize operation status
    bulk_fetch_operations[operation_id] = {
        "id": operation_id,
        "status": "running",
        "logs": [f"[{datetime.now().isoformat()}] Starting bulk fetch operation (ID: {operation_id})"],
        "language": request.language,
        "fetch_only": request.fetch_only,
        "process_steps": request.process_steps,
        "completed": False,
        "started_at": datetime.now().isoformat(),
        "articles_processed": 0,
        "articles_cached": 0,
        "articles_fetched": 0,
        "articles_skipped": 0
    }
    
    # Start the operation in the background
    background_tasks.add_task(
        process_bulk_fetch,
        operation_id=operation_id,
        language=request.language,
        agent=agent,
        cache=cache,
        db=db
    )
    
    # Return the operation ID
    return {"id": operation_id, "message": "Bulk fetch operation started"}

# Functions for each step of the bulk fetch process
async def fetch_step(operation_id: str, language: str, agent: ContentAgent, cache: ArticleCache, db: DatabaseService, log_message):
    """Step 1: Fetch articles from various sources and store them in MongoDB"""
    operation = bulk_fetch_operations[operation_id]
    
    # Determine which languages to process
    languages_to_process = ["ko", "en"] if language == "all" else [language]
    log_message(f"Processing languages: {', '.join(languages_to_process)}")
    
    all_articles = {}
    articles_added = 0
    articles_skipped = 0
    
    # Fetch articles for each language
    for lang in languages_to_process:
        log_message(f"Fetching RSS feeds for language: {lang}")
        
        # Get the latest articles from RSS feeds
        rss_articles = await fetch_rss_articles(lang, agent, log_message)
        log_message(f"Found {len(rss_articles)} articles from RSS feeds for {lang}")
        
        # Store raw articles in MongoDB with deduplication
        log_message(f"Processing {len(rss_articles)} raw articles for {lang}")
        raw_articles_count = 0
        deduplicated_count = 0
        
        for i, article in enumerate(rss_articles):
            try:
                # Initialize validation variables
                valid_article = True
                missing_attrs = []
                
                # Ensure the article has all required attributes before processing
                if not hasattr(article, 'url') or not article.url:
                    missing_attrs.append("URL")
                    valid_article = False
                    
                if not hasattr(article, 'title') or not article.title:
                    missing_attrs.append("title")
                    valid_article = False
                
                if not valid_article:
                    log_message(f"Skipping article with missing {', '.join(missing_attrs)}")
                    operation["articles_skipped"] = operation.get("articles_skipped", 0) + 1
                    continue
                    
                # Check if article has text content - needed for meaningful storage
                has_text = False
                if not hasattr(article, 'text') or not article.text:
                    # Try to get the text from the HTML if available
                    if hasattr(article, 'html') and article.html:
                        # Extract text from HTML if possible
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(article.html, 'html.parser')
                            article.text = soup.get_text(separator='\n', strip=True)
                            log_message(f"Extracted text from HTML for article: {article.title}")
                        except Exception as html_err:
                            log_message(f"Could not extract text from HTML: {str(html_err)}")
                
                # Check title
                if not hasattr(article, 'title') or not article.title:
                    missing_attrs.append("title")
                    valid_article = False
                
                # Check URL
                if not hasattr(article, 'url') or not article.url:
                    missing_attrs.append("URL")
                    valid_article = False
                
                # Check text - more comprehensive check
                has_text = False
                
                # Check for text attribute
                if hasattr(article, 'text') and article.text and len(article.text.strip()) > 100:
                    has_text = True
                
                # Check for sections/content with substantial text
                elif hasattr(article, 'content') and article.content and len(article.content) > 0:
                    # Verify that at least one section has content
                    for section in article.content:
                        if hasattr(section, 'content') and section.content and len(section.content.strip()) > 50:
                            has_text = True
                            break
                
                if not has_text:
                    missing_attrs.append("text content")
                    valid_article = False
                
                if not valid_article:
                    article_title = "Unknown"
                    if hasattr(article, 'title') and article.title:
                        article_title = article.title
                    elif hasattr(article, 'url') and article.url:
                        article_title = article.url
                        
                    log_message(f"Skipping article without {', '.join(missing_attrs)}: {article_title}")
                    operation["articles_skipped"] = operation.get("articles_skipped", 0) + 1
                    continue
                
                # Check if article already exists in MongoDB to avoid duplicates
                existing = None
                if hasattr(article, 'url') and article.url:
                    existing = await db.articles_collection.find_one({"url": article.url})
                    
                if existing:
                    log_message(f"Article already exists in database: {article.title}")
                    operation["articles_skipped"] = operation.get("articles_skipped", 0) + 1
                    deduplicated_count += 1
                    
                    # Check if this article has already been grouped (skip if it has)
                    already_grouped = existing.get("grouped", False)
                    if already_grouped:
                        log_message(f"Article has already been grouped: {article.title}")
                        continue
                    
                    # Although we're skipping storage, still add to all_articles for grouping
                    # Convert MongoDB document to ArticleContent object
                    if not operation.get("fetch_only", False) and "aggregate" in operation.get("process_steps", []):
                        try:
                            # Create ArticleContent from existing document
                            from_db = ArticleContent(
                                title=existing.get("title", "Untitled"),
                                url=existing.get("url", ""),
                                source=existing.get("source", ""),
                                language=existing.get("language", lang),
                                topics=existing.get("topics", []),
                                content=existing.get("sections", [])
                            )
                            # Add text attribute for grouping
                            from_db.__dict__['text'] = existing.get("text", "")
                            
                            # Store in memory for next steps
                            if lang not in all_articles:
                                all_articles[lang] = []
                            all_articles[lang].append(from_db)
                            log_message(f"Including existing article in grouping: {from_db.title}")
                        except Exception as e:
                            log_message(f"Error converting existing article: {str(e)}")
                    
                    continue
                    
                # Extract topics from article content
                topics = extract_topics_from_article(article, log_message)
                
                # Create a dictionary with article data
                article_dict = {
                    "_id": f"{operation_id}-{lang}-{i}",
                    "title": article.title,
                    "url": article.url,
                    "source": article.source if hasattr(article, 'source') else urlparse(article.url).netloc,
                    "language": lang,
                    "date_created": datetime.now(),
                    "date_published": article.date if hasattr(article, 'date') else None,
                    "author": article.author if hasattr(article, 'author') else "",
                    "text": article.text if hasattr(article, 'text') else "",
                    "summary": article.summary if hasattr(article, 'summary') else "",
                    "topics": topics,
                    "content_type": "raw",
                    "bulk_fetch_id": operation_id
                }
                
                # Add content sections if available
                if hasattr(article, 'content') and article.content:
                    article_dict["sections"] = []
                    for section in article.content:
                        if hasattr(section, 'content') and section.content:
                            article_dict["sections"].append({
                                "type": section.type if hasattr(section, 'type') else "text",
                                "content": section.content,
                                "order": section.order if hasattr(section, 'order') else 0
                            })
                
                # Add grouping tracking fields
                article_dict["grouped"] = False  # Initially not grouped
                article_dict["group_id"] = None  # Will be set when grouped
                
                # Save to MongoDB
                try:
                    await db.articles_collection.insert_one(article_dict)
                    log_message(f"Stored article in MongoDB: {article.title} - Text length: {len(article.text) if hasattr(article, 'text') and article.text else 'N/A'}, Sections: {len(article_dict.get('sections', []))}")
                    raw_articles_count += 1
                    operation["articles_fetched"] = operation.get("articles_fetched", 0) + 1
                except Exception as db_err:
                    log_message(f"Error saving article to MongoDB: {str(db_err)}")
                    operation["articles_skipped"] = operation.get("articles_skipped", 0) + 1
                
                # Store in memory for next steps
                if lang not in all_articles:
                    all_articles[lang] = []
                all_articles[lang].append(article)
                
            except Exception as e:
                log_message(f"Error processing article {article.title if hasattr(article, 'title') else 'unknown'}: {str(e)}")
        
        log_message(f"Successfully processed {raw_articles_count} raw articles for {lang} (skipped {deduplicated_count} duplicates)")
        operation["articles_cached"] += raw_articles_count
    
    # Update operation statistics
    operation["articles_fetched"] = articles_added
    operation["articles_skipped"] = articles_skipped
    
    # Return fetched articles for subsequent steps
    return all_articles

async def group_articles_by_similarity(articles, agent, log_fn):
    """Group articles by content similarity and identify a main topic for each group"""
    if not articles or len(articles) == 0:
        log_fn("No articles to group")
        return []
    
    # If there's only one article, put it in its own group
    if len(articles) == 1:
        article = articles[0]
        # Extract topics from the article
        topics = [topic for topic in article.topics if topic and len(topic) > 1]
        main_topic = topics[0] if topics else "General News"
        
        return [{
            "main_topic": main_topic,
            "articles": articles
        }]
    
    # For multiple articles, use the LLM to identify similarities and group them
    log_fn(f"Using LLM to group {len(articles)} articles by similarity")
    
    try:
        # Prepare article information for the LLM
        article_info = []
        for i, article in enumerate(articles):
            # Create a summary of the article for the LLM to analyze
            article_text = ""
            if hasattr(article, 'text') and article.text:
                # Use truncated text to avoid token limits
                article_text = article.text[:1000] + "..." if len(article.text) > 1000 else article.text
            
            # Create a compact representation of the article
            article_info.append({
                "id": i,  # Internal ID for reference
                "title": article.title,
                "text": article_text,
                "topics": article.topics if hasattr(article, 'topics') else [],
                "language": article.language
            })
        
        # Construct the prompt for the LLM
        prompt = f"""
        You will be presented with information about {len(articles)} news articles. 
        Your task is to group these articles by topic similarity and identify the main topic for each group.
        
        Here are the articles:
        {json.dumps(article_info, indent=2)}
        
        Please analyze these articles and group them by similarity of content and topic.
        Articles in the same group should be about the same event, topic, or closely related topics.
        
        Return your analysis as a JSON array, where each element is an object with these properties:
        - main_topic: A short string (2-5 words) describing the main topic of the group
        - article_ids: An array of article IDs that belong to this group
        
        Make sure the main_topic is specific and informative.
        Each article must be assigned to exactly one group.
        The response must be valid JSON with no extra text.
        """
        
        # Get response from LLM
        response = await agent.llm.apredict(prompt)
        log_fn(f"Received grouping analysis from LLM")
        
        # Parse the JSON response
        groups_data = json.loads(response)
        
        # Create the final groups with full article objects
        result_groups = []
        for group in groups_data:
            group_articles = [articles[article_id] for article_id in group["article_ids"] if article_id < len(articles)]
            if group_articles:  # Only add groups that actually have articles
                result_groups.append({
                    "main_topic": group["main_topic"],
                    "articles": group_articles
                })
        
        log_fn(f"Created {len(result_groups)} article groups")
        return result_groups
    
    except Exception as e:
        log_fn(f"Error grouping articles: {str(e)}")
        # Fallback: put all articles in one group
        return [{
            "main_topic": "Mixed News",
            "articles": articles
        }]

async def process_bulk_fetch(operation_id: str, language: str, agent: ContentAgent, cache: ArticleCache, db: DatabaseService):
    """Process a bulk fetch operation in the background with separated steps"""
    try:
        operation = bulk_fetch_operations[operation_id]
        log_message = lambda msg: operation["logs"].append(f"[{datetime.now().isoformat()}] {msg}")
        
        # Get the processing steps from the operation
        steps_to_run = operation.get("process_steps", ["fetch"])
        log_message(f"Executing bulk fetch steps: {', '.join(steps_to_run)}")
        
        # Step 1: Fetch - Always run this step
        log_message("Starting FETCH step to collect articles")
        fetched_articles = await fetch_step(operation_id, language, agent, cache, db, log_message)
        log_message(f"FETCH step completed with {sum(len(articles) for articles in fetched_articles.values())} articles")
        
        # If only fetch step is requested or if fetch_only flag is set, stop here
        if operation.get("fetch_only", False) or steps_to_run == ["fetch"]:
            log_message("Only fetch step was requested. Skipping preparation and rewriting.")
            operation["status"] = "completed"
            operation["completed"] = True
            operation["completed_at"] = datetime.now().isoformat()
            return
        
        # Step 2: Prepare articles for rewriting (renamed from aggregate)
        prepared_articles = {}
        if "aggregate" in steps_to_run:
            log_message("Starting PREPARE step to organize articles for rewriting")
            prepared_articles = await aggregate_step(operation_id, fetched_articles, agent, db, log_message)
            log_message(f"PREPARE step completed with {sum(len(articles) for articles in prepared_articles.values())} articles")
        
        # Step 3: Rewrite - Create rewritten versions at different difficulty levels with tags
        if "rewrite" in steps_to_run and prepared_articles:
            log_message("Starting REWRITE step to create difficulty-adjusted versions with tags")
            rewritten_count = await rewrite_step(operation_id, prepared_articles, agent, cache, db, log_message)
            log_message(f"REWRITE step completed with {rewritten_count} rewritten articles")
        
        # Mark operation as completed
        log_message(f"Bulk fetch operation completed successfully")
        operation["status"] = "completed"
        operation["completed"] = True
        operation["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"Error in bulk fetch operation {operation_id}: {str(e)}")
        if operation_id in bulk_fetch_operations:
            bulk_fetch_operations[operation_id]["status"] = "failed"
            bulk_fetch_operations[operation_id]["error"] = str(e)
            bulk_fetch_operations[operation_id]["logs"].append(f"[{datetime.now().isoformat()}] Error: {str(e)}")

async def aggregate_step(operation_id: str, fetched_articles, agent: ContentAgent, db: DatabaseService, log_message):
    """Step 2: Prepare articles for rewriting (no grouping now)"""
    operation = bulk_fetch_operations[operation_id]
    
    # We're eliminating the grouping step and simply passing articles by language
    article_by_language = {}
    
    for language, articles in fetched_articles.items():
        if not articles:
            log_message(f"No articles to process for language: {language}")
            continue
            
        log_message(f"Preparing {len(articles)} articles for {language}")
        article_by_language[language] = articles
    
    operation["articles_prepared"] = sum([len(articles) for articles in article_by_language.values()])
    log_message(f"Prepared {operation['articles_prepared']} articles for rewriting")
    return article_by_language

async def rewrite_step(operation_id: str, article_groups, agent: ContentAgent, cache: ArticleCache, db: DatabaseService, log_message):
    """Step 3: Rewrite individual articles at different difficulty levels and add tags"""
    # Note: article_groups is now a dictionary of language -> list of articles (not groups)
    operation = bulk_fetch_operations[operation_id]
    difficulties = ["beginner", "intermediate", "advanced"]
    rewritten_count = 0
    
    # Process articles by language
    for lang, articles in article_groups.items():
        if not articles:
            log_message(f"No articles to rewrite for language: {lang}")
            continue
            
        log_message(f"Rewriting {len(articles)} articles for {lang}")
        
        # Process each article individually
        for i, article in enumerate(articles):
            log_message(f"Processing article {i+1}/{len(articles)} for {lang}: {article.title}")
            
            # Generate tags for this article and store them in the database
            try:
                tag_data = await extract_tags_from_article(article, db, log_message)
                if not tag_data or not tag_data["tag_ids"]:
                    log_message(f"No tags generated for article, skipping: {article.title}")
                    continue
                    
                log_message(f"Generated {len(tag_data['tag_ids'])} tags for article: {article.title}")
                
                # Rewrite at each difficulty level
                for difficulty in difficulties:
                    try:
                        log_message(f"Rewriting article at {difficulty} level: {article.title}")
                        
                        # Generate rewritten version
                        rewritten_article = await agent.rewrite_article_content(article, difficulty)
                        if not rewritten_article:
                            log_message(f"Failed to rewrite article at {difficulty} level: {article.title}")
                            continue
                        
                        # Convert to dictionary for MongoDB storage
                        rewritten_dict = rewritten_article[0].dict() if hasattr(rewritten_article[0], 'dict') else rewritten_article[0].__dict__
                        
                        # Add metadata
                        rewritten_dict["_id"] = f"{article.url}-{difficulty}"
                        rewritten_dict["original_url"] = article.url
                        rewritten_dict["difficulty"] = difficulty
                        rewritten_dict["date_rewritten"] = datetime.now()
                        rewritten_dict["content_type"] = "rewritten_article"
                        rewritten_dict["bulk_fetch_id"] = operation_id
                        
                        # Add tags - only store tag IDs on the article itself
                        rewritten_dict["tag_ids"] = tag_data["tag_ids"]
                        
                        # Store the auto-generated tags separately for reference
                        rewritten_dict["auto_generated_tags"] = tag_data["auto_generated_tags"]
                        
                        # Store in database
                        await db.articles_collection.insert_one(rewritten_dict)
                        log_message(f"Stored rewritten article in MongoDB: {rewritten_article[0].title} ({difficulty})")
                        rewritten_count += 1
                        
                    except Exception as e:
                        log_message(f"Error rewriting article at {difficulty} level: {str(e)}")
                
                # Mark the original article as processed
                await db.articles_collection.update_one(
                    {"_id": article.url if isinstance(article.url, ObjectId) else ObjectId(article.url) if str(article).startswith("ObjectId") else article.url},
                    {"$set": {"rewritten": True}}
                )
            except Exception as e:
                log_message(f"Error processing article {article.title}: {str(e)}")
    
    operation["articles_rewritten"] = rewritten_count
    return rewritten_count


async def extract_tags_from_article(article, db, log_fn):
    """Extract tags from an article using the TagGenerator and store them in the database"""
    try:
        # Extract title and content
        title = article.title if hasattr(article, 'title') else ""
        language = article.language if hasattr(article, 'language') else "en"
        
        # Get content text from article
        content_text = ""
        if hasattr(article, 'text') and article.text:
            content_text = article.text
        elif hasattr(article, 'content') and article.content:
            content_text = ""
            for section in article.content:
                if hasattr(section, 'text') and section.text:
                    content_text += section.text + "\n\n"
                elif hasattr(section, 'content') and section.content:
                    content_text += section.content + "\n\n"
        
        # Fetch most popular tags for this language to provide as context
        # Get both tags in this language and tags with translations for this language
        existing_tags = []
        try:
            # Get most commonly used active tags (up to 20)
            active_tags = await db.get_tags(language=language, active_only=True)
            if active_tags:
                # Sort by article count (most used first)
                active_tags = sorted(active_tags, key=lambda x: x.get('article_count', 0), reverse=True)[:20]
                existing_tags.extend(active_tags)
                log_fn(f"Found {len(active_tags)} existing active tags for language: {language}")
        except Exception as e:
            log_fn(f"Error fetching existing tags: {str(e)}")
        
        # Generate tags using the TagGenerator with existing tags as context
        tag_objects = await tag_generator.generate_tags(
            title=title, 
            content=content_text, 
            language=language,
            existing_tags=existing_tags
        )
        log_fn(f"Generated {len(tag_objects)} tag objects for article: {title}")
        
        # Store the tags in the database and get their IDs
        tag_ids = []
        for tag_obj in tag_objects:
            # Check if tag with same English name already exists
            existing_tags = await db.get_tags(query=tag_obj["name"])
            existing_tag = next((t for t in existing_tags if t["name"].lower() == tag_obj["name"].lower()), None)
            
            if existing_tag:
                # Use existing tag ID
                tag_id = str(existing_tag["_id"])
                
                # Add any new translations
                if tag_obj["translations"] and "translations" in existing_tag:
                    updated_translations = existing_tag["translations"].copy()
                    updated_translations.update(tag_obj["translations"])
                    
                    # Update the tag with new translations if they were added
                    if updated_translations != existing_tag["translations"]:
                        await db.update_tag(tag_id, {"translations": updated_translations})
                        log_fn(f"Updated translations for existing tag: {tag_obj['name']}")
            else:
                # Create a new tag (standard categories will be auto-approved)
                new_tag = await db.create_tag(
                    name=tag_obj["name"],  # English canonical name
                    language=tag_obj["original_language"],
                    translations=tag_obj["translations"]
                )
                tag_id = str(new_tag["_id"])
                approval_status = "auto-approved" if new_tag.get("auto_approved") else "pending approval"
                log_fn(f"Created new tag: {tag_obj['name']} ({tag_id}) - {approval_status}")
            
            tag_ids.append(tag_id)
        
        # Record both the original tags and the tag IDs
        auto_generated_tags = [{
            "name": tag_obj["name"],
            "original_language": tag_obj["original_language"],
            "translations": tag_obj["translations"]
        } for tag_obj in tag_objects]
        
        return {
            "tag_ids": tag_ids,
            "auto_generated_tags": auto_generated_tags
        }
    except Exception as e:
        log_fn(f"Error extracting tags: {str(e)}")
        return {
            "tag_ids": [],
            "auto_generated_tags": []
        }

# Return the operation ID
    return {"id": operation_id, "message": "Bulk fetch operation started"}

@app.get("/bulk-fetch-status/{operation_id}")
async def get_bulk_fetch_status(operation_id: str):
    """Get the status of a bulk fetch operation"""
    if operation_id not in bulk_fetch_operations:
        raise HTTPException(status_code=404, detail=f"Bulk fetch operation {operation_id} not found")
    
    return bulk_fetch_operations[operation_id]

# Get information about cached content
@app.get("/bulk-fetch-info")
async def bulk_fetch_info(cache: ArticleCache = Depends(get_article_cache)):
    """Get information about what's in the cache"""
    # Get all cached queries
    cached_queries = cache.get_all_queries()
    
    return {
        "cached_queries": cached_queries,
        "cache_stats": cache.get_stats(),
        "timestamp": datetime.now().isoformat()
    }

# Include other routers here
app.include_router(tag_router)

# Add proxy routes for compatibility with frontend
@app.get("/api/tags")
async def get_tags_proxy(
    request: Request,
    language: Optional[str] = None,
    active_only: bool = Query(False, alias="active"),  # Match param name to frontend
    name_contains: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    db: DatabaseService = Depends(get_database_service)
):
    """Proxy endpoint to redirect /api/tags to /tags"""
    # Instead of directly forwarding, call the function with proper dependencies
    response = await tag_router.routes[0].endpoint(
        language=language,
        active_only=active_only,
        name_contains=name_contains,
        limit=limit,
        skip=skip,
        db=db
    )
    return response

# Frontend article request endpoint
@app.post("/api/articles")
async def get_articles_frontend(
    article_request: dict = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    agent: ContentAgent = Depends(get_content_agent),
    cache: ArticleCache = Depends(get_article_cache),
    db: DatabaseService = Depends(get_database_service)
):
    """Get articles based on frontend request parameters"""
    try:
        # Extract parameters from the request body
        language = article_request.get("language", "en")
        difficulty = article_request.get("difficulty", "intermediate")
        tag_ids = article_request.get("tag_ids", [])
        
        # First try to get articles from the database
        query = {"language": language}
        
        # Add tag filter if tags are provided
        if tag_ids and len(tag_ids) > 0:
            query["tag_ids"] = {"$in": tag_ids}
            
        # Get articles with the specified difficulty, not limited to rewritten content
        articles_query = {
            **query,
            "difficulty": difficulty
        }
        
        # Log the query to help with debugging
        logger.info(f"Fetching articles with query: {articles_query}")
        
        articles = await db.articles_collection.find(articles_query).limit(20).to_list(length=20)
        
        # Convert ObjectId to string for JSON serialization
        for article in articles:
            if '_id' in article and not isinstance(article['_id'], str):
                article['_id'] = str(article['_id'])
        
        if articles:
            return {
                "articles": articles,
                "count": len(articles),
                "language": language,
                "difficulty": difficulty,
                "source": "database"
            }
        else:
            # No articles found, log the issue
            logger.warning(f"No articles found for query: {articles_query}")
            return {
                "articles": [],
                "count": 0,
                "language": language,
                "difficulty": difficulty,
                "message": "No articles found. Try different filters or run a bulk fetch to populate content."
            }
    except Exception as e:
        logger.error(f"Error getting articles for frontend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tags/stats")
async def get_tags_stats_proxy(db: DatabaseService = Depends(get_database_service)):
    """Proxy endpoint to redirect /api/tags/stats to /tags/stats"""
    # Forward the request to the tags stats endpoint with the proper dependency
    response = await get_tag_stats(db=db)
    return response

if __name__ == "__main__":
    # Start the FastAPI server
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
