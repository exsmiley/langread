#!/usr/bin/env python
"""

Script to trigger the article rewriting process for a specific article.
This will help debug if the rewriting functionality is working correctly.
"""
import sys
import os
import asyncio
import time
from datetime import datetime, timedelta
from pprint import pprint
from typing import Dict, List, Any, Optional

# Add project root to path to import modules
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from src.models.database import DatabaseService
from src.scrapers.agent import ContentAgent, ArticleContent, ContentSection
from src.api.main import extract_topics_from_article

async def trigger_rewrite():
    # Start timing the overall process
    overall_start_time = time.time()
    # Connect to database
    db = DatabaseService()
    await db.connect()
    print("Connected to MongoDB database")
    
    # Create content agent that handles rewriting
    agent = ContentAgent()
    
    # Set a reasonable limit to avoid overwhelming terminal
    limit = 1
    
    # Query for a raw article to rewrite
    raw_articles_cursor = db.articles_collection.find(
        {"content_type": "raw", "rewritten": {"$ne": True}},
        {"_id": 1, "title": 1, "language": 1, "url": 1, "bulk_fetch_id": 1, 
         "source": 1, "sections": 1, "topics": 1}
    ).limit(limit)
    
    raw_articles = await raw_articles_cursor.to_list(length=limit)
    
    if not raw_articles:
        print("No raw articles found in the database that haven't been rewritten")
        return
    
    print(f"Found {len(raw_articles)} raw articles to rewrite")
    
    for idx, article_doc in enumerate(raw_articles):
        print(f"\n--- Raw Article {idx+1} ---")
        print(f"Title: {article_doc.get('title', 'Unknown title')}")
        print(f"Language: {article_doc.get('language', 'Unknown language')}")
        print(f"ID: {article_doc.get('_id', 'Unknown ID')}")
        
        try:
            # Convert DB document to ArticleContent object
            # Extract text from sections for the text attribute
            article_text = ""
            for section in article_doc.get("sections", []):
                if section.get('content'):
                    article_text += section.get('content') + "\n\n"

            article = ArticleContent(
                title=article_doc.get("title", "Untitled"),
                url=article_doc.get("url", ""),
                source=article_doc.get("source", ""),
                language=article_doc.get("language", "ko"),
                topics=article_doc.get("topics", []),
                content=article_doc.get("sections", []),
                text=article_text.strip()  # Use the proper text attribute now
            )
            
            # Try to rewrite the article at different difficulty levels
            difficulties = ["beginner", "intermediate", "advanced"]
            for difficulty in difficulties:
                print(f"\nAttempting to rewrite at {difficulty} level...")
                # Start timing this difficulty level
                start_time = time.time()
                
                try:
                    # Rewrite article
                    rewritten_article = await agent.group_and_rewrite_articles(
                        articles=[article],
                        language=article.language,
                        target_difficulty=difficulty
                    )
                    
                    if not rewritten_article:
                        print(f"Failed to rewrite at {difficulty} level")
                        continue
                    
                    print(f"Successfully rewrote article at {difficulty} level")
                    
                    # Extract topics for tagging
                    topics = article.topics
                    
                    # Store in MongoDB with a test ID
                    operation_id = f"test-rewrite-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    rewritten_id = f"{operation_id}-{article.language}-{difficulty}-0"
                    
                    # Prepare the rewritten article for storage
                    rewritten_dict = {
                        "_id": rewritten_id,
                        "title": rewritten_article[0].title,
                        "language": article.language,
                        "difficulty": difficulty,
                        "date_created": datetime.now(),
                        "topics": topics,
                        "text": rewritten_article[0].text,
                        "summary": rewritten_article[0].summary if hasattr(rewritten_article[0], 'summary') else "",
                        "sections": [{
                            "title": section.title if hasattr(section, 'title') else "",
                            "content": section.content,
                            "words": section.words if hasattr(section, 'words') else []
                        } for section in rewritten_article[0].sections] if hasattr(rewritten_article[0], 'sections') else [],
                        "content_type": "rewritten",
                        "source_article": article.url,
                        "bulk_fetch_id": article_doc.get("bulk_fetch_id", operation_id)
                    }
                    
                    # Store in MongoDB
                    result = await db.articles_collection.insert_one(rewritten_dict)
                    print(f"Stored rewritten article in MongoDB with ID: {rewritten_id}")
                    
                    # Print a snippet of the rewritten text
                    text = rewritten_article[0].text
                    text_preview = text[:150] + "..." if text and len(text) > 150 else text
                    print(f"Text preview: {text_preview}")
                    
                    # Calculate and print elapsed time for this difficulty level
                    elapsed_time = time.time() - start_time
                    print(f"Rewriting at {difficulty} level completed in {elapsed_time:.2f} seconds")
                    
                except Exception as e:
                    print(f"Error rewriting article at {difficulty} level: {str(e)}")
                
        except Exception as e:
            print(f"Error processing article: {str(e)}")
    
    # Close database connection
    await db.disconnect()
    
    # Calculate and print total elapsed time
    total_elapsed_time = time.time() - overall_start_time
    minutes, seconds = divmod(total_elapsed_time, 60)
    print(f"\nTotal rewriting process completed in {int(minutes)} minutes and {seconds:.2f} seconds")
    print("\nDisconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(trigger_rewrite())
