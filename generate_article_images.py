#!/usr/bin/env python3
"""
Article Image Generator for LangRead

This script:
1. Finds articles without images
2. Generates content summaries for each article
3. Creates image prompts based on article content and tags
4. Generates images using OpenAI DALL-E
5. Updates the articles with image URLs in the database
"""

import asyncio
import os
import sys
import time
import re
import hashlib
import urllib.parse
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from loguru import logger

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logger.add("article_images.log", rotation="10 MB")

# Check for OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Default query parameters
DEFAULT_IMAGE_SIZE = "1024x1024"
DEFAULT_IMAGE_QUALITY = "standard"
DEFAULT_IMAGE_STYLE = "natural"

# Supported languages with relevant prompt templates
LANGUAGE_TEMPLATES = {
    "ko": {
        "prefix": "디지털 아트 일러스트레이션, 미니멀리스트, 현대적인 디자인, 밝은 색감, 주제:",  # Digital art illustration, minimalist, modern design, bright colors, topic:
        "style": "韓国のポップアート風",  # Korean pop art style
        "suffix": "뉴스 기사 표지 이미지"  # News article cover image
    },
    "en": {
        "prefix": "Digital art illustration, minimalist, modern design, bright colors, topic:",
        "style": "Contemporary editorial style",
        "suffix": "News article cover image"
    },
    "es": {
        "prefix": "Ilustración de arte digital, minimalista, diseño moderno, colores brillantes, tema:",
        "style": "Estilo editorial contemporáneo",
        "suffix": "Imagen de portada de artículo de noticias"
    },
    "fr": {
        "prefix": "Illustration d'art numérique, minimaliste, design moderne, couleurs vives, sujet:",
        "style": "Style éditorial contemporain",
        "suffix": "Image de couverture d'article de presse"
    },
    "de": {
        "prefix": "Digitale Kunstillustration, minimalistisch, modernes Design, leuchtende Farben, Thema:",
        "style": "Zeitgenössischer Redaktionsstil",
        "suffix": "Titelbild für Nachrichtenartikel"
    },
    "ja": {
        "prefix": "デジタルアートイラスト、ミニマリスト、モダンデザイン、明るい色、トピック:",
        "style": "現代的な編集スタイル",
        "suffix": "ニュース記事のカバー画像"
    },
    "zh": {
        "prefix": "数字艺术插图，极简主义，现代设计，明亮的颜色，主题：",
        "style": "当代编辑风格",
        "suffix": "新闻文章封面图片"
    }
}

# Default English template for unsupported languages
DEFAULT_TEMPLATE = LANGUAGE_TEMPLATES["en"]

# Tags mapped to visual concepts to enrich prompts
TAG_VISUAL_CONCEPTS = {
    # Technology
    "technology": "digital devices, circuit boards, futuristic interfaces",
    "ai": "neural networks visualization, glowing nodes, artificial intelligence",
    "blockchain": "connected blocks, digital chain links, cryptographic visuals",
    "tech": "modern gadgets, technology interfaces, digital innovation",
    
    # Business
    "business": "professional setting, modern office, business meeting",
    "economy": "financial charts, economy graphs, market visualization",
    "finance": "financial symbols, currency, banking concepts",
    "investment": "growing investments, stock market charts, financial growth",
    "startup": "launching rocket, innovative workspace, entrepreneur concept",
    
    # Politics
    "politics": "political symbols, government buildings, diplomatic imagery",
    "government": "official buildings, government symbols, political institutions",
    "policy": "policy documents, legislative process, regulatory concepts",
    
    # Education
    "education": "learning environment, books, educational tools",
    "학습": "studying materials, educational setting, learning tools",
    "research": "scientific research, laboratory setting, academic environment",
    
    # Health
    "health": "healthcare symbols, medical concepts, wellness imagery",
    "medical": "medical equipment, healthcare professionals, clinical setting",
    "healthcare": "healthcare facility, medical professionals, patient care",
    
    # Society
    "social": "community gathering, social interactions, people connecting",
    "culture": "cultural symbols, traditional elements, artistic expressions",
    "society": "social fabric, community scene, diverse people",
    
    # Media
    "media": "media channels, broadcasting, news symbols",
    "entertainment": "entertainment industry, performance stage, media content",
    "news": "news broadcast, journalism, media reporting",
    
    # Environment
    "environment": "natural landscapes, environmental elements, ecological scenes",
    "climate": "climate visuals, weather patterns, environmental change",
    "energy": "energy sources, power generation, sustainable technology"
}

class ArticleImageGenerator:
    """Handles generation of images for articles using DALL-E"""
    
    def __init__(self):
        """Initialize the image generator."""
        self.db = None
        self.stats = {
            "processed": 0,
            "generated": 0,
            "skipped": 0,
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
        """Extract textual content from an article for summarization."""
        try:
            # First try title and description
            content = f"{article.get('title', '')} {article.get('description', '')}"
            
            # Add text content from content sections if available
            if "content" in article and isinstance(article["content"], list):
                for section in article["content"]:
                    if isinstance(section, dict) and section.get("type") == "text":
                        content += " " + section.get("content", "")
            
            # Fallback to content_sample if available
            if not content.strip() and "content_sample" in article:
                content = article["content_sample"]
            
            # Trim to reasonable length for prompt
            if len(content) > 1500:
                content = content[:1500] + "..."
                
            return content
        except Exception as e:
            logger.error(f"Error extracting content from article {article.get('_id')}: {e}")
            return article.get("title", "") + " " + article.get("description", "")
    
    def get_article_tags(self, article: Dict[str, Any]) -> List[str]:
        """Get tag names for an article."""
        # If article has topics, use those
        if "topics" in article and isinstance(article["topics"], list):
            return article["topics"]
        
        # Return tag_ids as fallback
        if "tag_ids" in article and isinstance(article["tag_ids"], list):
            return article["tag_ids"]
        
        return []
    
    def create_safe_filename(self, text: str) -> str:
        """Create a safe, URL-friendly filename from text."""
        # Remove non-alphanumeric characters and replace spaces with underscores
        safe_text = re.sub(r'[^\w\s-]', '', text).strip().lower()
        safe_text = re.sub(r'[-\s]+', '_', safe_text)
        
        # Limit length and add hash for uniqueness
        max_length = 50
        if len(safe_text) > max_length:
            safe_text = safe_text[:max_length]
            
        # Add a hash for uniqueness
        hash_suffix = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"{safe_text}_{hash_suffix}"
    
    async def generate_content_summary(self, content: str, language: str, max_length: int = 100) -> str:
        """Generate a concise summary of article content for image prompt."""
        try:
            # Define language-specific instruction
            language_instructions = {
                "ko": "다음 텍스트의 주요 주제를 간결하게 요약해 주세요. 시각적 이미지로 표현할 수 있는 요소에 초점을 맞추세요.",
                "en": "Summarize the main topic of the following text concisely. Focus on elements that can be visually represented.",
                "es": "Resume el tema principal del siguiente texto de forma concisa. Enfócate en elementos que puedan ser representados visualmente.",
                "fr": "Résumez le sujet principal du texte suivant de manière concise. Concentrez-vous sur les éléments qui peuvent être représentés visuellement.",
                "de": "Fassen Sie das Hauptthema des folgenden Textes prägnant zusammen. Konzentrieren Sie sich auf Elemente, die visuell dargestellt werden können.",
                "ja": "以下のテキストの主題を簡潔に要約してください。視覚的に表現できる要素に焦点を当ててください。",
                "zh": "简明扼要地总结以下文本的主要主题。关注可以在视觉上表现的元素。"
            }
            
            instruction = language_instructions.get(language, language_instructions["en"])
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"{instruction} Keep the summary under {max_length} characters."},
                    {"role": "user", "content": content}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Ensure it's not too long
            if len(summary) > max_length:
                summary = summary[:max_length]
                
            logger.info(f"Generated summary: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fall back to using the first part of the content
            simple_summary = content.split('.')[0]
            if len(simple_summary) > max_length:
                simple_summary = simple_summary[:max_length] + "..."
            return simple_summary
    
    def create_image_prompt(self, summary: str, tags: List[str], language: str) -> str:
        """Create an image generation prompt from article summary and tags."""
        # Get language-specific template or fall back to default
        template = LANGUAGE_TEMPLATES.get(language, DEFAULT_TEMPLATE)
        
        # Extract visual concepts from tags
        visual_concepts = []
        for tag in tags:
            tag_lower = tag.lower()
            for key, concept in TAG_VISUAL_CONCEPTS.items():
                if key in tag_lower:
                    visual_concepts.append(concept)
                    break
        
        # Create visual concepts string
        visual_string = ""
        if visual_concepts:
            visual_string = f" {', '.join(visual_concepts[:3])}"
        
        # Combine template with summary and visual concepts
        prompt = f"{template['prefix']} {summary}{visual_string}, {template['style']}, {template['suffix']}"
        
        logger.info(f"Created prompt: {prompt}")
        return prompt
    
    async def generate_image_url(self, prompt: str, article_id: str) -> Optional[str]:
        """Generate an image using DALL-E based on the prompt."""
        try:
            # Create a safe filename from article ID
            safe_id = str(article_id).replace(" ", "_")
            
            response = openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=DEFAULT_IMAGE_SIZE,
                quality=DEFAULT_IMAGE_QUALITY,
                style=DEFAULT_IMAGE_STYLE,
                n=1
            )
            
            # Extract the image URL
            image_url = response.data[0].url
            logger.info(f"Generated image URL: {image_url}")
            
            return image_url
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
    
    async def update_article_image(self, article_id: str, image_url: str) -> bool:
        """Update an article with the generated image URL."""
        try:
            # Update the article
            result = await self.db.articles_collection.update_one(
                {"_id": article_id},
                {"$set": {
                    "image_url": image_url,
                    "image_generated": True,
                    "image_generated_at": datetime.now()
                }}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating article {article_id}: {e}")
            return False
    
    async def process_articles(self, language: Optional[str] = None, limit: int = 0):
        """Process articles without images and generate images for them."""
        try:
            # Build query to find articles without images
            query = {"$or": [
                {"image_url": {"$exists": False}},
                {"image_url": None},
                {"image_url": ""}
            ]}
            
            if language:
                query["language"] = language
            
            # Find articles that need images
            cursor = self.db.articles_collection.find(query)
            if limit > 0:
                articles = await cursor.limit(limit).to_list(length=limit)
            else:
                articles = await cursor.limit(20).to_list(length=20)  # Process up to 20 articles at once
            
            total_articles = len(articles)
            logger.info(f"Found {total_articles} articles without images")
            
            if total_articles == 0:
                logger.info("No articles to process")
                return
            
            # Process each article
            for i, article in enumerate(articles):
                article_id = article["_id"]
                language = article.get("language", "en")
                title = article.get("title", "Untitled")
                
                logger.info(f"Processing article {i+1}/{total_articles}: {title} ({language})")
                
                # Extract content for summarization
                content = self.extract_article_content(article)
                if not content:
                    logger.warning(f"No content found for article {article_id}")
                    self.stats["skipped"] += 1
                    continue
                
                # Get article tags
                tags = self.get_article_tags(article)
                
                try:
                    # Generate content summary
                    summary = await self.generate_content_summary(content, language)
                    
                    # Create image prompt
                    prompt = self.create_image_prompt(summary, tags, language)
                    
                    # Generate image
                    image_url = await self.generate_image_url(prompt, str(article_id))
                    
                    if image_url:
                        # Update article with image URL
                        success = await self.update_article_image(article_id, image_url)
                        
                        if success:
                            logger.info(f"Updated article {article_id} with image URL")
                            self.stats["generated"] += 1
                        else:
                            logger.error(f"Failed to update article {article_id}")
                            self.stats["errors"] += 1
                    else:
                        logger.warning(f"No image URL generated for article {article_id}")
                        self.stats["errors"] += 1
                    
                    self.stats["processed"] += 1
                    
                    # Pause between generation to avoid rate limits
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error processing article {article_id}: {e}")
                    self.stats["errors"] += 1
            
            # Print summary
            logger.info(f"Image generation summary:")
            logger.info(f"Total processed: {self.stats['processed']}")
            logger.info(f"Images generated: {self.stats['generated']}")
            logger.info(f"Articles skipped: {self.stats['skipped']}")
            logger.info(f"Errors: {self.stats['errors']}")
            
        except Exception as e:
            logger.error(f"Error processing articles: {e}")

async def main():
    """Main function to run the article image generator."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Generate images for articles")
    parser.add_argument("--language", "-l", help="Filter by language code (e.g., 'ko', 'en')")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Limit number of articles to process")
    args = parser.parse_args()
    
    # Initialize generator
    generator = ArticleImageGenerator()
    
    try:
        # Connect to database
        await generator.connect_to_db()
        
        # Process articles
        await generator.process_articles(language=args.language, limit=args.limit)
        
        logger.info("Article image generation complete")
        
    except Exception as e:
        logger.error(f"Error in article image generation: {e}")
    finally:
        # Clean up
        await generator.disconnect_from_db()

if __name__ == "__main__":
    asyncio.run(main())
