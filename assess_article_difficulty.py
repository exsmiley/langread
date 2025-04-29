#!/usr/bin/env python3
"""
LangRead Article Difficulty Assessment Service

This script:
1. Finds articles with unknown difficulty levels
2. Analyzes content complexity using LLM-based assessment
3. Assigns appropriate difficulty levels (beginner/intermediate/advanced)
4. Updates articles in the database with the assessed difficulty
"""

import os
import sys
import json
import asyncio
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logger.add("difficulty_assessment.log", rotation="10 MB")

# Validate environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ko": "Korean",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "zh": "Chinese"
}

# Language-specific difficulty criteria
DIFFICULTY_CRITERIA = {
    "en": {
        "beginner": "Simple vocabulary, short sentences, present tense, basic grammar, common topics",
        "intermediate": "Varied vocabulary, compound sentences, more tenses, idioms, wider range of topics",
        "advanced": "Rich vocabulary, complex sentences, all tenses, cultural references, specialized topics"
    },
    "ko": {
        "beginner": "Basic particles (은/는/이/가), simple verb endings, common vocabulary, short sentences",
        "intermediate": "Various verb endings, some honorifics, compound sentences, idioms, topic-specific vocabulary",
        "advanced": "Full honorific system, complex grammar patterns, abstract concepts, cultural nuances, specialized vocabulary"
    },
    # Add more languages as needed
}

# Default criteria for languages not specifically defined
DEFAULT_CRITERIA = {
    "beginner": "Simple vocabulary, short sentences, basic grammar structures, common topics",
    "intermediate": "Varied vocabulary, compound sentences, more complex grammar, idioms, wider range of topics",
    "advanced": "Rich vocabulary, complex sentence structures, cultural references, specialized topics, abstract concepts"
}

class DifficultyAssessor:
    """Handles assessment of article difficulty based on content analysis."""
    
    def __init__(self):
        """Initialize the difficulty assessor."""
        self.db = None
        self.stats = {
            "total_processed": 0,
            "beginner": 0,
            "intermediate": 0,
            "advanced": 0,
            "errors": 0
        }
    
    async def connect_to_db(self):
        """Connect to the database."""
        self.db = DatabaseService()
        await self.db.connect()
        logger.info("Connected to database")
    
    async def disconnect_from_db(self):
        """Disconnect from the database."""
        if self.db:
            await self.db.disconnect()
            logger.info("Disconnected from database")
    
    def extract_article_content(self, article: Dict[str, Any]) -> str:
        """Extract the textual content from an article."""
        try:
            content_sections = article.get("content", [])
            text_content = []
            
            for section in content_sections:
                if section.get("type") == "text":
                    text_content.append(section.get("content", ""))
            
            # If no text content found, use sample or title/description
            if not text_content:
                if "content_sample" in article:
                    return article["content_sample"]
                else:
                    return f"{article.get('title', '')} {article.get('description', '')}"
            
            return "\n".join(text_content)
        except Exception as e:
            logger.error(f"Error extracting content from article {article.get('_id')}: {e}")
            return article.get("title", "") + " " + article.get("description", "")
    
    async def assess_difficulty(self, article: Dict[str, Any]) -> str:
        """
        Assess the difficulty level of an article using OpenAI.
        Returns: "beginner", "intermediate", or "advanced"
        """
        article_id = str(article.get("_id", "unknown"))
        language = article.get("language", "en")
        
        try:
            # Extract content for analysis
            content = self.extract_article_content(article)
            if not content:
                logger.warning(f"No content found for article {article_id}")
                return "intermediate"  # Default if no content
            
            # Truncate content if too long (keep within token limits)
            if len(content) > 3000:
                content = content[:3000] + "..."
            
            # Get language-specific criteria or default
            criteria = DIFFICULTY_CRITERIA.get(language, DEFAULT_CRITERIA)
            language_name = SUPPORTED_LANGUAGES.get(language, language)
            
            # Prepare prompt for difficulty assessment
            prompt = f"""
            Assess the difficulty level of this {language_name} text for language learners.
            
            Text: "{content}"
            
            Analyze the vocabulary, grammar complexity, sentence structure, and topic.
            
            Difficulty criteria:
            - Beginner: {criteria['beginner']}
            - Intermediate: {criteria['intermediate']}
            - Advanced: {criteria['advanced']}
            
            Respond with EXACTLY ONE of these words: "beginner", "intermediate", or "advanced"
            """
            
            # Call OpenAI API for assessment
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a language education expert who assesses text difficulty."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip().lower()
            
            # Normalize response to ensure it's one of our valid difficulty levels
            if "beginner" in result:
                return "beginner"
            elif "advanced" in result:
                return "advanced"
            else:
                return "intermediate"  # Default to intermediate if ambiguous
                
        except Exception as e:
            logger.error(f"Error assessing difficulty for article {article_id}: {e}")
            return "intermediate"  # Default to intermediate on error
    
    async def update_article_difficulty(self, article_id: str, difficulty: str) -> bool:
        """Update an article's difficulty level in the database."""
        try:
            # Update the article
            result = await self.db.articles_collection.update_one(
                {"_id": article_id},
                {"$set": {"difficulty": difficulty, "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating article {article_id}: {e}")
            return False
    
    async def process_articles(self, language: Optional[str] = None, limit: int = 0):
        """Process articles with unknown difficulty and assign proper levels."""
        try:
            # Build query to find articles with unknown difficulty
            query = {"difficulty": {"$exists": False}}
            if language:
                query["language"] = language
            
            # Find articles that need difficulty assessment
            cursor = self.db.articles_collection.find(query)
            if limit > 0:
                articles = await cursor.to_list(length=limit)
            else:
                articles = await cursor.to_list(length=1000)  # Process up to 1000 articles at once
            
            total_articles = len(articles)
            logger.info(f"Found {total_articles} articles with unknown difficulty")
            
            if total_articles == 0:
                logger.info("No articles to process")
                return
            
            # Process each article
            for i, article in enumerate(articles):
                article_id = article["_id"]
                language = article.get("language", "unknown")
                title = article.get("title", "Untitled")
                
                logger.info(f"Processing article {i+1}/{total_articles}: {title} ({language})")
                
                # Assess difficulty
                difficulty = await self.assess_difficulty(article)
                logger.info(f"Assessed difficulty: {difficulty}")
                
                # Update article in database
                success = await self.update_article_difficulty(article_id, difficulty)
                if success:
                    logger.info(f"Updated article {article_id} with difficulty: {difficulty}")
                    self.stats["total_processed"] += 1
                    self.stats[difficulty] += 1
                else:
                    logger.error(f"Failed to update article {article_id}")
                    self.stats["errors"] += 1
                
                # Brief pause to avoid rate limits
                await asyncio.sleep(0.5)
            
            # Print summary
            logger.info(f"Processing complete. Summary:")
            logger.info(f"Total processed: {self.stats['total_processed']}")
            logger.info(f"Beginner: {self.stats['beginner']}")
            logger.info(f"Intermediate: {self.stats['intermediate']}")
            logger.info(f"Advanced: {self.stats['advanced']}")
            logger.info(f"Errors: {self.stats['errors']}")
            
        except Exception as e:
            logger.error(f"Error processing articles: {e}")

async def main():
    """Main function to run the difficulty assessment."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Assess difficulty of articles")
    parser.add_argument("--language", "-l", help="Filter by language code (e.g., 'ko', 'en')")
    parser.add_argument("--limit", "-n", type=int, default=0, help="Limit number of articles to process (0 for all)")
    args = parser.parse_args()
    
    # Initialize assessor
    assessor = DifficultyAssessor()
    
    try:
        # Connect to database
        await assessor.connect_to_db()
        
        # Process articles
        await assessor.process_articles(language=args.language, limit=args.limit)
        
        logger.info("Difficulty assessment complete")
        
    except Exception as e:
        logger.error(f"Error in difficulty assessment: {e}")
    finally:
        # Clean up
        await assessor.disconnect_from_db()

if __name__ == "__main__":
    asyncio.run(main())
