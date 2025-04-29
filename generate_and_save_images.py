#!/usr/bin/env python3
"""
Generate article images using GPT-4o and save them locally

This script:
1. Finds articles that need images
2. Generates a prompt based on article content and tags
3. Creates images using GPT-4o
4. Downloads the images to a local directory
5. Updates the database with local file paths
"""

import asyncio
import os
import sys
import time
import re
import hashlib
import urllib.request
import json
import base64
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from loguru import logger
import httpx

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logger.add("article_images_gpt4o.log", rotation="10 MB")

# Check for OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

# Set up the image storage directory
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "src", "frontend", "public", "article_images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Tag mapping for better prompts
TAG_VISUAL_CONCEPTS = {
    # Technology
    "technology": "디지털 기기, 첨단 기술",
    "ai": "인공지능, 머신러닝, 미래 기술",
    "blockchain": "블록체인, 암호화폐, 분산형 네트워크",
    "tech": "현대 기술, 디지털 혁신",
    
    # Business
    "business": "비즈니스 미팅, 현대적 사무실, 전문 환경",
    "economy": "경제 그래프, 금융 차트, 시장 동향",
    "finance": "금융 기호, 화폐, 은행 개념",
    "investment": "투자 성장, 주식 시장, 금융 성장",
    "startup": "스타트업, 혁신 작업공간, 창업가 개념",
    
    # Politics
    "politics": "정치 상징, 정부 건물, 외교적 이미지",
    "government": "공식 건물, 정부 상징, 정치 기관",
    "policy": "정책 문서, 입법 과정, 규제 개념",
    
    # Education
    "education": "학습 환경, 책, 교육 도구",
    "학습": "학습 자료, 교육 환경, 학습 도구",
    "research": "과학 연구, 실험실 환경, 학문적 환경",
    
    # Health
    "health": "의료 상징, 건강 개념, 웰빙 이미지",
    "medical": "의료 장비, 의료 전문가, 임상 환경",
    "healthcare": "의료 시설, 의료 전문가, 환자 케어",
    
    # Society
    "social": "커뮤니티 모임, 사회적 상호작용, 사람들의 연결",
    "culture": "문화 상징, 전통 요소, 예술적 표현",
    "society": "사회 구조, 커뮤니티 장면, 다양한 사람들",
    
    # Media
    "media": "미디어 채널, 방송, 뉴스 상징",
    "entertainment": "엔터테인먼트 산업, 공연 무대, 미디어 콘텐츠",
    "news": "뉴스 방송, 저널리즘, 미디어 보도",
    
    # Environment
    "environment": "자연 풍경, 환경 요소, 생태학적 장면",
    "climate": "기후 시각화, 날씨 패턴, 환경 변화",
    "energy": "에너지 원천, 발전, 지속 가능한 기술"
}

# Visual style templates for Korean articles
VISUAL_STYLES = [
    "한국 미니멀리즘 스타일, 간결한 디자인, 현대적인 색상",
    "케이팝 인플루언스 디자인, 밝은 네온 색상, 동적인 구성",
    "미니멀리스트 인포그래픽 스타일, 깔끔한 레이아웃, 글자와 이미지의 균형",
    "서울 도시 미학, 현대적 라인, 도시 컬러 팔레트",
    "한국 디지털 아트 스타일, 추상적 요소와 기하학적 형태",
    "미래지향적 한국 디자인, 곡선과 매끄러운 형태",
    "한국 전통 요소와 현대적 디자인의 융합",
    "아시아 팝 아트 영감, 대담한 윤곽선, 평면적 요소"
]

class GPT4oImageGenerator:
    """Generate article images using GPT-4o and save them locally"""
    
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
        """Create a safe filename from text."""
        # Remove non-alphanumeric characters and replace spaces with underscores
        safe_text = re.sub(r'[^\w\s-]', '', text).strip().lower()
        safe_text = re.sub(r'[-\s]+', '_', safe_text)
        
        # Limit length and add hash for uniqueness
        max_length = 40
        if len(safe_text) > max_length:
            safe_text = safe_text[:max_length]
            
        # Add a hash for uniqueness
        hash_suffix = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"{safe_text}_{hash_suffix}"
    
    async def generate_content_summary(self, content: str, language: str) -> str:
        """Generate a concise summary of article content for image prompt."""
        try:
            instruction = """
            다음 텍스트의 핵심 주제를 요약하세요. 시각적 이미지로 표현할 수 있는 
            요소에 집중하세요. 요약은 100자 이내로 작성해 주세요.
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": content}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fall back to using the first part of the content
            simple_summary = content.split('.')[0]
            if len(simple_summary) > 100:
                simple_summary = simple_summary[:100] + "..."
            return simple_summary
    
    def create_image_prompt(self, summary: str, tags: List[str]) -> str:
        """Create an image generation prompt from article summary and tags."""
        # Get visual concepts from tags
        visual_concepts = []
        for tag in tags:
            tag_lower = tag.lower()
            for key, concept in TAG_VISUAL_CONCEPTS.items():
                if key in tag_lower:
                    visual_concepts.append(concept)
                    break
        
        # Choose a random visual style
        import random
        visual_style = random.choice(VISUAL_STYLES)
        
        # Create visual concepts string
        visual_string = ""
        if visual_concepts:
            visual_string = f", {', '.join(visual_concepts[:2])}"
        
        # Combine with summary and visual style
        prompt = f"기사 주제: {summary}{visual_string}. {visual_style}. 뉴스 또는 잡지 표지 이미지로 적합한 디자인."
        
        logger.info(f"Created prompt: {prompt}")
        return prompt
    
    async def generate_image_with_gpt4o(self, prompt: str) -> Optional[str]:
        """Generate an image using GPT-4o."""
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 한국어 기사에 대한 이미지를 생성하는 디자이너야. 다음 설명에 맞게 이미지를 생성해줘."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract the image from the response
            content = response.choices[0].message.content
            
            # Check if the response has an image
            if not "![" in content and not "data:image" in content:
                logger.error(f"No image found in GPT-4o response: {content[:100]}...")
                return None
            
            # Try to extract the base64 image data
            data_uri_match = re.search(r'data:image\/[^;]+;base64,([^"\']+)', content)
            markdown_match = re.search(r'!\[.*?\]\((data:image\/[^)]+)\)', content)
            
            if data_uri_match:
                data_uri = data_uri_match.group(0)
                return data_uri
            elif markdown_match:
                data_uri = markdown_match.group(1)
                return data_uri
            else:
                logger.error(f"Could not extract image data from response: {content[:100]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error generating image with GPT-4o: {e}")
            return None
    
    def save_base64_image(self, data_uri: str, article_id: str) -> Optional[str]:
        """Save a base64 encoded image to a file."""
        try:
            # Extract the base64 data from the data URI
            header, encoded = data_uri.split(",", 1)
            data = base64.b64decode(encoded)
            
            # Create a filename based on article ID
            filename = f"article_{str(article_id).replace(' ', '_')}.png"
            filepath = os.path.join(IMAGES_DIR, filename)
            
            # Save the image
            with open(filepath, "wb") as f:
                f.write(data)
            
            # Return the relative path for the database
            relative_path = f"/article_images/{filename}"
            logger.info(f"Saved image to {filepath}")
            return relative_path
            
        except Exception as e:
            logger.error(f"Error saving base64 image: {e}")
            return None
    
    async def update_article_image(self, article_id: str, image_path: str) -> bool:
        """Update article with a local image path."""
        try:
            result = await self.db.articles_collection.update_one(
                {"_id": article_id},
                {"$set": {
                    "image_url": image_path,
                    "image_generated": True,
                    "image_generated_at": datetime.now()
                }}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating article {article_id}: {e}")
            return False
    
    async def process_articles(self, language: str = "ko", limit: int = 5):
        """Process articles and generate images for them."""
        try:
            # Build query for articles without proper images
            query = {
                "language": language,
                "$or": [
                    {"image_url": {"$exists": False}},
                    {"image_url": None},
                    {"image_url": ""},
                    {"image_url": {"$regex": "^https://oaidalleapiprodscus"}}  # DALL-E temporary URLs
                ]
            }
            
            # Find articles needing images
            cursor = self.db.articles_collection.find(query)
            if limit > 0:
                articles = await cursor.limit(limit).to_list(length=limit)
            else:
                articles = await cursor.limit(10).to_list(length=10)
            
            logger.info(f"Found {len(articles)} articles that need permanent images")
            
            if len(articles) == 0:
                logger.info("No articles to process")
                return
            
            # Process each article
            for i, article in enumerate(articles):
                article_id = article["_id"]
                title = article.get("title", "Untitled")
                
                logger.info(f"Processing article {i+1}/{len(articles)}: {title}")
                
                # Extract content for summarization
                content = self.extract_article_content(article)
                if not content:
                    logger.warning(f"No content found for article {article_id}")
                    self.stats["skipped"] += 1
                    continue
                
                try:
                    # Generate content summary
                    summary = await self.generate_content_summary(content, language)
                    
                    # Create image prompt
                    tags = self.get_article_tags(article)
                    prompt = self.create_image_prompt(summary, tags)
                    
                    # Generate image with GPT-4o
                    image_data = await self.generate_image_with_gpt4o(prompt)
                    
                    if image_data:
                        # Save image locally
                        image_path = self.save_base64_image(image_data, article_id)
                        
                        if image_path:
                            # Update article with local image path
                            success = await self.update_article_image(article_id, image_path)
                            
                            if success:
                                logger.info(f"Updated article {article_id} with local image path: {image_path}")
                                self.stats["generated"] += 1
                            else:
                                logger.error(f"Failed to update article {article_id}")
                                self.stats["errors"] += 1
                        else:
                            logger.error(f"Failed to save image for article {article_id}")
                            self.stats["errors"] += 1
                    else:
                        logger.warning(f"No image data generated for article {article_id}")
                        self.stats["errors"] += 1
                    
                    self.stats["processed"] += 1
                    
                    # Wait between requests to avoid rate limiting
                    await asyncio.sleep(2)
                    
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
    
    async def fix_existing_dalle_images(self, language: str = "ko", limit: int = 20):
        """Replace temporary DALL-E URLs with permanent local images."""
        try:
            # Query for articles with DALL-E URLs
            query = {
                "language": language,
                "image_url": {"$regex": "^https://oaidalleapiprodscus"}
            }
            
            cursor = self.db.articles_collection.find(query)
            if limit > 0:
                articles = await cursor.limit(limit).to_list(length=limit)
            else:
                articles = await cursor.limit(20).to_list(length=20)
            
            logger.info(f"Found {len(articles)} articles with temporary DALL-E image URLs")
            
            if len(articles) == 0:
                logger.info("No DALL-E URLs to fix")
                return
            
            saved_count = 0
            error_count = 0
            
            # Process each article
            for i, article in enumerate(articles):
                article_id = article["_id"]
                image_url = article.get("image_url", "")
                
                logger.info(f"Processing DALL-E URL {i+1}/{len(articles)}")
                
                try:
                    # Try to download the image while it's still valid
                    filename = f"article_{str(article_id).replace(' ', '_')}.png"
                    filepath = os.path.join(IMAGES_DIR, filename)
                    
                    try:
                        # Download the image
                        async with httpx.AsyncClient() as client:
                            response = await client.get(image_url, timeout=10.0)
                            if response.status_code == 200:
                                with open(filepath, "wb") as f:
                                    f.write(response.content)
                                    
                                # Update article with local path
                                relative_path = f"/article_images/{filename}"
                                success = await self.update_article_image(article_id, relative_path)
                                
                                if success:
                                    logger.info(f"Saved DALL-E image to {relative_path}")
                                    saved_count += 1
                                else:
                                    logger.error(f"Failed to update article with local path")
                                    error_count += 1
                            else:
                                logger.error(f"Failed to download image: {response.status_code}")
                                error_count += 1
                    except Exception as e:
                        logger.error(f"Error downloading DALL-E image: {e}")
                        error_count += 1
                        
                        # If we can't download it, generate a new image
                        await self.process_articles(language=language, limit=1)
                    
                    # Wait between requests
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing DALL-E URL for article {article_id}: {e}")
                    error_count += 1
            
            logger.info(f"DALL-E URL fix summary:")
            logger.info(f"Total processed: {len(articles)}")
            logger.info(f"Images saved: {saved_count}")
            logger.info(f"Errors: {error_count}")
            
        except Exception as e:
            logger.error(f"Error fixing DALL-E URLs: {e}")

async def main():
    """Main function to run the image generator."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate and save article images")
    parser.add_argument("--language", "-l", default="ko", help="Language code (e.g., 'ko', 'en')")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Limit of articles to process")
    parser.add_argument("--fix-dalle", action="store_true", help="Fix existing DALL-E URLs")
    args = parser.parse_args()
    
    generator = GPT4oImageGenerator()
    
    try:
        await generator.connect_to_db()
        
        if args.fix_dalle:
            await generator.fix_existing_dalle_images(language=args.language, limit=args.limit)
        else:
            await generator.process_articles(language=args.language, limit=args.limit)
        
        logger.info("Image generation complete")
        
    except Exception as e:
        logger.error(f"Error in image generation: {e}")
    finally:
        await generator.disconnect_from_db()

if __name__ == "__main__":
    asyncio.run(main())
