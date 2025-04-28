"""
Tag generation utilities for articles.
Uses LLM to extract relevant tags from article content.
"""
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
import json
from dotenv import load_dotenv
from openai import OpenAI
from loguru import logger

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TagGenerator:
    """
    Generates tags for articles using an LLM.
    """
    
    def __init__(self, model: str = "gpt-4.1-nano", temperature: float = 0.1):
        """
        Initialize the tag generator.
        
        Args:
            model: LLM model to use
            temperature: Sampling temperature
        """
        self.model = model
        self.temperature = temperature
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it as OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Predefined category tags per language
        # Maps ISO language codes to lists of common category tags
        self.category_tags = {
            # English
            "en": [
                "news", "politics", "technology", "science", "health", "business", 
                "entertainment", "sports", "education", "environment", "culture",
                "art", "food", "travel", "religion", "history", "literature",
                "fashion", "music", "film", "television", "automotive", "finance",
                "lifestyle", "social_issues", "economy", "international", "crime"
            ],
            # Korean
            "ko": [
                "뉴스", "정치", "기술", "과학", "건강", "경제", "비즈니스",
                "엔터테인먼트", "스포츠", "교육", "환경", "문화", "예술", "음식",
                "여행", "종교", "역사", "문학", "패션", "음악", "영화", "텔레비전",
                "자동차", "금융", "라이프스타일", "사회문제", "범죄", "국제"
            ],
            # Spanish
            "es": [
                "noticias", "política", "tecnología", "ciencia", "salud", "negocios",
                "entretenimiento", "deportes", "educación", "medio ambiente", "cultura",
                "arte", "comida", "viajes", "religión", "historia", "literatura"
            ],
            # French
            "fr": [
                "actualités", "politique", "technologie", "science", "santé", "affaires",
                "divertissement", "sports", "éducation", "environnement", "culture",
                "art", "cuisine", "voyages", "religion", "histoire", "littérature"
            ],
            # Japanese
            "ja": [
                "ニュース", "政治", "テクノロジー", "科学", "健康", "ビジネス",
                "エンターテイメント", "スポーツ", "教育", "環境", "文化",
                "アート", "食品", "旅行", "宗教", "歴史", "文学"
            ],
            # Chinese
            "zh": [
                "新闻", "政治", "技术", "科学", "健康", "商业",
                "娱乐", "体育", "教育", "环境", "文化",
                "艺术", "食品", "旅游", "宗教", "历史", "文学"
            ],
            # German
            "de": [
                "nachrichten", "politik", "technologie", "wissenschaft", "gesundheit", "geschäft",
                "unterhaltung", "sport", "bildung", "umwelt", "kultur",
                "kunst", "essen", "reisen", "religion", "geschichte", "literatur"
            ]
        }
    

        
    async def translate_tags_to_english(self, tags: List[str], source_language: str) -> List[str]:
        """
        Translate non-English tags to English for canonical storage
        
        Args:
            tags: List of tags in source language
            source_language: Source language code
            
        Returns:
            List of tags translated to English
        """
        if not tags:
            return []
            
        # Skip translation if source is already English
        if source_language == "en":
            return tags
            
        try:
            # Create a prompt for the LLM to translate tags
            prompt = f"""
            Please translate the following tags from {source_language} to English.
            Return the translations with the exact same meaning, but in English.
            Keep proper nouns and entity names as they are (e.g., names of people, places, products).
            Only translate common nouns, concepts and categories.
            
            Original tags: {', '.join(tags)}
            
            Format your response as a valid JSON array of strings containing ONLY the translated tags in the same order.
            Example: ["politics", "economics", "sports"]
            """
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a language translation assistant focused on accurately translating tags while preserving their meaning. Follow the instructions exactly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Extract translated tags from response
            content = completion.choices[0].message.content
            result = json.loads(content.strip())
            
            # Handle various output formats
            if isinstance(result, list):
                # Direct array output
                translated_tags = result
            elif "translations" in result:
                # Using a key like {"translations": [...]}
                translated_tags = result["translations"]
            elif "tags" in result:
                # Using a key like {"tags": [...]}
                translated_tags = result["tags"]
            else:
                # If none of the expected formats, try to get the first list value
                translated_tags = list(result.values())[0] if isinstance(list(result.values())[0], list) else []
            
            # Ensure we have the same number of translations as original tags
            if len(translated_tags) != len(tags):
                logger.warning(f"Translation count mismatch: {len(tags)} original vs {len(translated_tags)} translated")
                # Pad with original tags if needed
                if len(translated_tags) < len(tags):
                    translated_tags.extend(tags[len(translated_tags):])
                else:
                    translated_tags = translated_tags[:len(tags)]
            
            # Clean the translated tags
            return [self.clean_tag(tag) for tag in translated_tags]
            
        except Exception as e:
            logger.error(f"Error translating tags: {str(e)}")
            # Return original tags if translation fails
            return tags
        
    async def generate_tags(self, title: str, content: str, language: str, max_tags: int = 8, existing_tags: List[dict] = None) -> List[dict]:
        """
        Generate tags for an article using LLM. If existing_tags is provided, the LLM will prioritize using those tags.
        
        Args:
            title: Article title
            content: Article content
            language: Article language code (e.g., 'en', 'ko', 'fr', etc.)
            max_tags: Maximum number of tags to generate
            existing_tags: Optional list of existing tag objects to prioritize using
            
        Returns:
            List of tag objects with name, original_language, and translations
        """
        # Detect language if not provided or unknown
        if not language or language not in self.category_tags:
            # Default to English categories but ask the LLM to detect the language
            categories = self.category_tags["en"]
            detect_language = True
        else:
            # Use the specified language's categories
            categories = self.category_tags.get(language, self.category_tags["en"])
            detect_language = False
        
        # Format existing tags for the prompt if provided
        existing_tag_prompt = ""
        if existing_tags and len(existing_tags) > 0:
            # Get translations in the article language if available
            localized_tags = []
            for tag in existing_tags:
                # Use the localized version if available for this language
                if language != "en" and "translations" in tag and language in tag["translations"]:
                    localized_tags.append(tag["translations"][language])
                else:
                    localized_tags.append(tag["name"])
            
            # Create the existing tags section of the prompt
            existing_tag_prompt = f"""
8. PRIORITIZE using tags from this existing list if they apply to the article: {', '.join(localized_tags)}
9. You may still add new tags if the existing ones don't fully capture the article's content.
"""
        
        # Create a prompt for the LLM
        prompt = f"""
As a tag analyzer, extract the most relevant tags from this article, with the following requirements:
1. {"First, detect the language of this article and include it as a tag." if detect_language else f"The article is in {language} language."}
2. Select up to {max_tags} tags that best represent the article's content.
3. Tags should be in the same language as the article.
4. Return ONLY common nouns or short phrases, no adjectives alone or full sentences.
5. Include at least one category tag from this list: {', '.join(categories)}
6. For additional custom tags, extract specific entities, topics, or themes from the article.
7. Tags should be relevant, accurate, and helpful for search and categorization.{existing_tag_prompt}

Article Title: {title}
Article Content: {content[:2000]}  # Limit content length

Format your response as a valid JSON array of strings. 
Example: ["politics", "climate_change", "united_nations", "paris_agreement"]
"""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a tag extraction specialist that identifies relevant categories and topics from text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Extract tags from the response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            if "tags" in result:
                tags = result["tags"]
            else:
                # If the model didn't use the 'tags' key, assume the entire object is the tags array
                tags = list(result.values())[0] if isinstance(list(result.values())[0], list) else []
            
            # Extract language tag if detected by the LLM
            language_detected = False
            for tag in tags:
                # Check if tag is a possible language code or name
                if tag.lower() in ['en', 'english', 'ko', 'korean', 'fr', 'french', 'es', 'spanish', 'de', 'german',
                                   'ja', 'japanese', 'zh', 'chinese', 'ru', 'russian', 'pt', 'portuguese',
                                   'ar', 'arabic', 'hi', 'hindi', 'bn', 'bengali', 'it', 'italian'] or \
                   tag.lower() in list(self.category_tags.keys()):
                    language_detected = True
                    break
            
            # Ensure we have at least language as a tag
            if not language_detected:
                if language:
                    tags.append(language)
                else:
                    tags.append("en")
            
            # Clean tags
            cleaned_tags = [self.clean_tag(tag) for tag in tags]
            
            # If the language is not English, translate tags to English
            if language != "en" and language:
                translated_tags = await self.translate_tags_to_english(cleaned_tags, language)
                # Create tag objects with original and English versions
                tag_objects = [
                    {
                        "tag_id": None,  # Will be set when saved to database
                        "name": english_tag,  # English canonical name
                        "original_language": language,
                        "translations": {language: original_tag}  # Original language version
                    } for original_tag, english_tag in zip(cleaned_tags, translated_tags)
                ]
                return tag_objects
            else:
                # For English, just create simple tag objects
                tag_objects = [
                    {
                        "tag_id": None,  # Will be set when saved to database
                        "name": tag,  # Already in English
                        "original_language": "en",
                        "translations": {}
                    } for tag in cleaned_tags
                ]
                
            # Remove any duplicates and limit to max_tags
            # Use name as the key for deduplication
            unique_tags = {}
            for tag_obj in tag_objects:
                if tag_obj["name"] not in unique_tags:
                    unique_tags[tag_obj["name"]] = tag_obj
                    
            return list(unique_tags.values())[:max_tags]
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            # Return language as fallback in the standard tag object format
            return [{
                "tag_id": None,
                "name": language or "en",
                "original_language": language or "en",
                "translations": {}
            }]
    
    def clean_tag(self, tag: str) -> str:
        """
        Clean and normalize a tag.
        
        Args:
            tag: Raw tag
            
        Returns:
            Cleaned tag
        """
        # Remove special characters and replace spaces with underscores
        cleaned = tag.strip().lower()
        cleaned = ''.join(c for c in cleaned if c.isalnum() or c.isspace() or c in "-_")
        cleaned = cleaned.replace(" ", "_")
        
        # Limit length
        if len(cleaned) > 50:
            cleaned = cleaned[:50]
            
        return cleaned

# Create a singleton instance
tag_generator = TagGenerator()
