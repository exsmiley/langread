"""
Test script to demonstrate the complete end-to-end content fetching and rewriting workflow.
This script:
1. Fetches articles on a specified topic
2. Groups related articles 
3. Rewrites them with LLM into educational content for language learners
"""
import asyncio
import os
import json
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv

from src.scrapers.agent import ContentAgent, ArticleContent

# Load environment variables from .env file
load_dotenv()

async def test_workflow():
    """Run the complete content workflow."""
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key not found in environment variables.")
        return
    
    print("=" * 80)
    print("LangRead Content Workflow Test")
    print("=" * 80)
    
    # Initialize the content agent
    print("Initializing content agent...")
    agent = ContentAgent(openai_api_key=api_key)
    
    # Test parameters
    query = "최신 기술 트렌드"  # "Latest technology trends" in Korean
    language = "ko"  # Korean language
    topic_type = "news"
    max_sources = 3
    
    print(f"\nFetching articles about '{query}' in {language}...")
    print("-" * 80)
    
    # Step 1: Fetch articles
    original_articles = await agent.get_content(
        query=query,
        language=language,
        topic_type=topic_type,
        max_sources=max_sources,
        group_and_rewrite=False  # Get the original articles first
    )
    
    if not original_articles:
        print("No articles found. Please try a different query or check your internet connection.")
        return
    
    # Print original articles summary
    print(f"Found {len(original_articles)} articles:")
    for i, article in enumerate(original_articles):
        print(f"  {i+1}. {article.title} ({len(article.content)} sections)")
        print(f"     Source: {article.source}")
        print(f"     Topics: {', '.join(article.topics)}")
        print(f"     Content preview: {article.content[0].content[:100]}...")
        print()
    
    # Step 2: Group and rewrite articles
    print("\nGrouping and rewriting articles for language learners...")
    print("-" * 80)
    
    # For demonstration, we'll try different difficulty levels
    difficulty_levels = ["beginner", "intermediate", "advanced"]
    
    for difficulty in difficulty_levels:
        print(f"\nGenerating {difficulty} level content:")
        
        rewritten = await agent.group_and_rewrite_articles(
            articles=original_articles,
            language=language,
            target_difficulty=difficulty
        )
        
        if rewritten:
            article = rewritten[0]  # We get one synthesized article back
            
            # Print rewritten article summary
            print(f"Title: {article.title}")
            print(f"Difficulty: {difficulty}")
            print(f"Topics: {', '.join(article.topics)}")
            print("\nContent Preview:")
            
            # Print first few sections
            section_count = min(3, len(article.content))
            for i in range(section_count):
                section = article.content[i]
                if section.type == "heading":
                    print(f"\n## {section.content}")
                elif section.type == "text":
                    # Print just the first 150 chars of each section
                    preview = section.content[:150] + "..." if len(section.content) > 150 else section.content
                    print(preview)
            
            print("\n" + "-" * 40)
        else:
            print("Failed to rewrite articles.")
    
    # Save the last rewritten article to a file for inspection
    if rewritten:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert to dict for JSON serialization
        article_dict = {
            "title": article.title,
            "language": article.language,
            "source": article.source,
            "topics": article.topics,
            "content": [
                {
                    "type": section.type,
                    "content": section.content,
                    "order": section.order
                }
                for section in article.content
            ]
        }
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"rewritten_article_{timestamp}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(article_dict, f, ensure_ascii=False, indent=2)
        
        print(f"Saved rewritten article to {filename}")
    
    print("\nWorkflow test completed!")

if __name__ == "__main__":
    asyncio.run(test_workflow())
