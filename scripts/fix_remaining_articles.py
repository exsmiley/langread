#!/usr/bin/env python3
"""
Fix remaining articles without images using more neutral prompts
"""

from path_helper import setup_path
# Add project root to Python path
setup_path()

import asyncio
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI


from src.models.database import DatabaseService

# Load environment variables
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is required")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Safe abstract image prompts for any topic
SAFE_PROMPTS = [
    "디지털 아트 일러스트레이션, 추상적인 비즈니스 성장 그래프, 미니멀한 디자인, 밝은 색상, 한국어 뉴스 기사 표지",
    "디지털 아트 일러스트레이션, 추상적인 연결된 노드와 네트워크, 미니멀한 디자인, 밝은 색상, 미래 기술 개념",
    "디지털 아트 일러스트레이션, 추상적인 아이디어 교환 시각화, 미니멀한 디자인, 밝은 색상, 커뮤니케이션 개념",
    "디지털 아트 일러스트레이션, 미래지향적 추상화, 미니멀한, 진취적인 이미지, 한국 디자인 영감",
    "디지털 아트 일러스트레이션, 미니멀한 데이터 흐름 시각화, 밝은 색상의 추상적 패턴, 정보 개념"
]

async def fix_remaining_articles():
    """Generate images for articles that still don't have them"""
    
    db = DatabaseService()
    await db.connect()
    print("Connected to database")
    
    try:
        # Find Korean articles without images
        articles = await db.articles_collection.find({
            'language': 'ko',
            '$or': [
                {'image_url': {'$exists': False}},
                {'image_url': None},
                {'image_url': ''}
            ]
        }).to_list(length=10)
        
        print(f"Found {len(articles)} articles without images")
        
        for i, article in enumerate(articles):
            article_id = article["_id"]
            title = article.get("title", "Untitled")
            
            print(f"\nProcessing article {i+1}/{len(articles)}: {title}")
            
            # Use a safe prompt that won't trigger content moderation
            prompt_index = i % len(SAFE_PROMPTS)
            prompt = SAFE_PROMPTS[prompt_index]
            
            try:
                # Generate image
                response = openai_client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    style="natural",
                    n=1
                )
                
                # Extract the image URL
                image_url = response.data[0].url
                print(f"Generated image: {image_url[:60]}...")
                
                # Update article with image URL
                result = await db.articles_collection.update_one(
                    {"_id": article_id},
                    {"$set": {
                        "image_url": image_url,
                        "image_generated": True
                    }}
                )
                
                if result.modified_count > 0:
                    print(f"Successfully updated article {article_id}")
                else:
                    print(f"Failed to update article {article_id}")
                
                # Pause between API calls
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Error processing article {article_id}: {e}")
        
        # Check final status
        remaining = await db.articles_collection.count_documents({
            'language': 'ko',
            '$or': [
                {'image_url': {'$exists': False}},
                {'image_url': None},
                {'image_url': ''}
            ]
        })
        
        if remaining == 0:
            print("\n🎉 All Korean articles now have images!")
        else:
            print(f"\nStill {remaining} articles without images")
            
    finally:
        await db.disconnect()
        print("\nDisconnected from database")

if __name__ == "__main__":
    asyncio.run(fix_remaining_articles())
